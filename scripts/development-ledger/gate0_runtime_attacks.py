#!/usr/bin/env python3
"""The half of the GATE 0 Red Team battery that has to run inside the API image.

These attacks construct the real settings object, the real application and the real readiness
probes, so they need FastAPI, pydantic and the application package — none of which is installed on
the host, and none of which should be: the host runs standard-library tooling only.

`gate0_red_team.py` runs this module inside the API container and merges the verdicts. Splitting it
out is what lets every attack execute a real mutation against real code instead of asserting
something about a file.

Output is one JSON document on stdout, so the caller parses a result rather than scraping prose.

    python -m iacode_red_team.gate0_runtime_attacks     # as mounted into the image
"""

from __future__ import annotations

import asyncio
import json
import logging
import sys
import time
from typing import Callable

from fastapi import APIRouter
from fastapi.testclient import TestClient
from iacode_api.config import Settings, settings_for_tests
from iacode_api.main import create_app
from iacode_api.readiness import DependencyProbe, run_probes
from iacode_telemetry.logging import JsonLogFormatter
from pydantic import ValidationError

Result = tuple[bool, str]


def _reason(error: ValidationError) -> str:
    """The line of a pydantic error that says what was wrong.

    ``str(error).splitlines()[-1]`` is the documentation URL, which is the same for every failure
    and therefore tells a reader nothing about what the control actually refused.
    """
    for line in str(error).splitlines():
        stripped = line.strip()
        if stripped.startswith(("Value error", "Input should")):
            return stripped[:180]
    return str(error).splitlines()[0][:180]


def cors_wildcard() -> Result:
    try:
        settings_for_tests(cors_allow_origins=["*"])
    except ValidationError as error:
        return "may not contain" in str(error), _reason(error)
    return False, "a wildcard origin was accepted"


def synchronous_driver() -> Result:
    try:
        settings_for_tests(database_url="postgresql://iacode:iacode@db:5432/iacode")
    except ValidationError as error:
        return "asyncpg" in str(error), _reason(error)
    return False, "a synchronous driver was accepted, which would block the event loop"


def endpoint_with_scheme() -> Result:
    try:
        settings_for_tests(minio_endpoint="http://minio:9000")
    except ValidationError as error:
        return "host:port" in str(error), _reason(error)
    return False, "a URL was accepted where the SDK expects host:port"


def invalid_enumerated_value() -> Result:
    try:
        settings_for_tests(log_level="CHATTY")
    except ValidationError as error:
        return "log_level" in str(error), _reason(error)
    return False, "an invalid log level was accepted"


def default_credentials() -> Result:
    defaults = Settings(_env_file=None, _env_prefix="IACODE_UNUSED_")
    leaked = [name for name in ("minio_access_key", "minio_secret_key")
              if defaults.__getattribute__(name).get_secret_value()]
    return not leaked, (f"defaults carry {', '.join(leaked)}" if leaked
                        else "every credential default is empty")


def secret_in_a_log_record() -> Result:
    record = logging.LogRecord(
        name="attack", level=logging.ERROR, pathname=__file__, lineno=1,
        msg="could not connect to postgresql://iacode:hunter2@db:5432/iacode",
        args=(), exc_info=None)
    record.config = {"minio_secret_key": "objectsecret", "host": "minio"}
    rendered = JsonLogFormatter(service="iacode-api").format(record)
    payload = json.loads(rendered)
    leaked = [token for token in ("hunter2", "objectsecret") if token in rendered]
    return not leaked, (f"leaked {', '.join(leaked)}" if leaked else
                        f"redacted; host preserved as {payload['context']['config']['host']!r}")


def traceback_reaches_the_client() -> Result:
    application = create_app(settings_for_tests())
    router = APIRouter()

    @router.get("/_attack/boom")
    async def boom() -> None:
        raise RuntimeError("connect to postgresql://iacode:hunter2@db:5432/iacode failed")

    application.include_router(router)
    with TestClient(application, raise_server_exceptions=False) as client:
        response = client.get("/_attack/boom")

    leaked = [token for token in ("hunter2", "RuntimeError", "Traceback") if token in response.text]
    body = response.json()
    defended = (response.status_code == 500 and not leaked
                and body.get("code") == "INTERNAL_ERROR" and bool(body.get("correlationId")))
    return defended, (f"HTTP {response.status_code}; "
                      + (f"leaked {', '.join(leaked)}" if leaked
                         else f"code={body.get('code')} correlationId present"))


def forged_correlation_header() -> Result:
    with TestClient(create_app(settings_for_tests())) as client:
        too_short = client.get("/health", headers={"X-Correlation-ID": "short"})
        with_space = client.get("/health", headers={"X-Correlation-ID": "has a space"})
        oversized = client.get("/health", headers={"X-Correlation-ID": "x" * 400})

    returned = [response.headers["X-Correlation-ID"] for response in
                (too_short, with_space, oversized)]
    echoed = [value for value in returned
              if value in ("short", "has a space", "x" * 400)]
    return not echoed, (f"echoed {echoed}" if echoed
                        else f"all three replaced, e.g. {returned[0][:24]}...")


def readiness_with_nothing_running() -> Result:
    with TestClient(create_app(settings_for_tests())) as client:
        ready = client.get("/ready")
        health = client.get("/health")
    body = ready.json()
    defended = (ready.status_code == 503 and body["status"] == "NOT_READY"
                and health.json()["status"] == "UP"
                and all(item["status"] == "DOWN" for item in body["dependencies"]))
    return defended, (f"ready=HTTP {ready.status_code} {body['status']}, "
                      f"health={health.json()['status']}, "
                      f"{len(body['dependencies'])} dependencies reported")


def readiness_leaks_the_connection_string() -> Result:
    settings = settings_for_tests(
        database_url="postgresql+asyncpg://iacode:hunter2@nowhere.invalid:5432/iacode")
    with TestClient(create_app(settings)) as client:
        body = client.get("/ready").text
    return "hunter2" not in body, ("the payload carries the password" if "hunter2" in body
                                   else "the failure detail is redacted")


def readiness_hangs() -> Result:
    async def never() -> None:
        await asyncio.sleep(3600)

    started = time.monotonic()
    outcome = asyncio.run(run_probes([DependencyProbe(name="hung", probe=never)],
                                     timeout_seconds=1.0))
    elapsed = time.monotonic() - started
    return (not outcome.ready and elapsed < 5), (
        f"answered in {elapsed:.1f}s with {outcome.reports[0].status.value}")


def version_exposes_configuration() -> Result:
    settings = settings_for_tests(
        database_url="postgresql+asyncpg://iacode:hunter2@db:5432/iacode",
        minio_secret_key="objectsecret")
    with TestClient(create_app(settings)) as client:
        body = client.get("/version").text
    leaked = [token for token in ("hunter2", "objectsecret", "postgresql", "minio")
              if token in body]
    return not leaked, (f"leaked {', '.join(leaked)}" if leaked
                        else "the payload carries build identity only")


# The null-mutation control for this half: unmutated input through the identical path, accepted.
def baseline() -> Result:
    settings = settings_for_tests()
    with TestClient(create_app(settings)) as client:
        health = client.get("/health")
        version = client.get("/version")
    ok = (settings.environment == "test" and health.status_code == 200
          and health.json()["status"] == "UP" and version.status_code == 200)
    return ok, (f"configuration loads, health={health.json().get('status')}, "
                f"version={version.json().get('version')}")


ATTACKS: dict[str, Callable[[], Result]] = {
    "G0-A": cors_wildcard,
    "G0-B": synchronous_driver,
    "G0-C": endpoint_with_scheme,
    "G0-D": invalid_enumerated_value,
    "G0-E": default_credentials,
    "G0-F": secret_in_a_log_record,
    "G0-I": traceback_reaches_the_client,
    "G0-J": forged_correlation_header,
    "G0-K": readiness_with_nothing_running,
    "G0-L": readiness_leaks_the_connection_string,
    "G0-M": readiness_hangs,
    "G0-N": version_exposes_configuration,
}


def main() -> int:
    results: dict[str, dict[str, object]] = {}
    ok, detail = baseline()
    results["baseline"] = {"defended": ok, "observed": detail}

    for identifier, attack in ATTACKS.items():
        try:
            defended, observed = attack()
        except Exception as error:  # noqa: BLE001 - a harness that crashes has found something
            defended, observed = False, f"the attack itself failed: {type(error).__name__}: {error}"
        results[identifier] = {"defended": defended, "observed": observed[:400]}

    print(json.dumps(results))
    return 0


if __name__ == "__main__":
    sys.exit(main())
