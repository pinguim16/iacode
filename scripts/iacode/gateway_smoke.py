#!/usr/bin/env python3
"""Prove the Model Gateway actually reaches a real provider.

Mocks prove the gateway's own logic. Only this proves the integration: that the configured provider
answers, that its catalog parses into our catalog, that a model generates, that it streams, that the
call was recorded and that the observability stack saw it.

It drives the **running stack over HTTP**, exactly as any other consumer would, rather than
importing the gateway in a process of its own. That is deliberate: what is being proved is the
deployed path — the API, the composed gateway, the provider policy inside the image, the database
and Prometheus — and a script that imported the library would prove the library.

    python scripts/iacode/gateway_smoke.py
    python scripts/iacode/gateway_smoke.py --report var/gateway-smoke.json

Three environment variables decide what it does, and it reads them from the host environment first
and from ``infra/compose/.env`` second, which is the same file the stack was started with:

    IACODE_DEVWORLD_BASE_URL     where the provider is
    IACODE_DEVWORLD_API_KEY      how to authenticate; never printed, never written to the report
    IACODE_GATEWAY_SMOKE_MODEL   'provider:model' this check is authorised to spend tokens on

**Without a credential it does not pass.** It exits `BLOCKED`, naming the variable that is missing,
because a live check that quietly reports success when it never called anything is worse than no
live check at all.

**The smoke model is never substituted.** If the configured model is not in the discovered catalog,
the check fails. Silently picking another one would spend money on a model nobody authorised, and
the bill is the first anyone would hear of it.

It is deliberately cheap: one catalog read repeated once for idempotence, one short generation and
one short stream, each capped to a handful of output tokens.
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from compose import (
    StackError,
    log,
    main_guard,
    psql,
    published_port,
    read_env_file,
)

#: Short, cheap, and impossible to satisfy by accident.
PROMPT = "Reply with exactly: IACODE_GATEWAY_OK"
EXPECTED = "IACODE_GATEWAY_OK"

#: Small enough that a mistake costs nothing. The answer is seventeen characters.
MAX_OUTPUT_TOKENS = 32

READ_TIMEOUT_SECONDS = 20
INFERENCE_TIMEOUT_SECONDS = 180

#: The exit code that means "not run, and not passed either".
BLOCKED_EXIT = 2


@dataclass
class Check:
    name: str
    ok: bool
    detail: str
    data: dict = field(default_factory=dict)


class BlockedError(RuntimeError):
    """The check could not run because something outside the repository is not configured."""


def setting(name: str) -> str:
    """One configuration value, from the host environment or the stack's own file."""
    import os

    value = (os.environ.get(name) or "").strip()
    if value:
        return value
    return (read_env_file().get(name) or "").strip()


def request_json(url: str, payload: dict | None = None, *, timeout: float,
                 accept_status: tuple[int, ...] = (200,)) -> tuple[int, dict]:
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    request = urllib.request.Request(
        url, data=data, method="POST" if data is not None else "GET",
        headers={"Accept": "application/json",
                 **({"Content-Type": "application/json"} if data is not None else {})})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        if error.code in accept_status:
            return error.code, json.loads(body)
        raise StackError(f"{url} responded {error.code}: {body[:400]}") from error
    except urllib.error.URLError as error:
        raise StackError(f"{url} is unreachable: {error.reason}") from error


def read_stream(url: str, payload: dict, *, timeout: float) -> list[tuple[str, dict]]:
    """Read a Server-Sent Event stream into (event name, payload) pairs."""
    request = urllib.request.Request(
        url, data=json.dumps(payload).encode("utf-8"), method="POST",
        headers={"Accept": "text/event-stream", "Content-Type": "application/json"})
    events: list[tuple[str, dict]] = []
    name: str | None = None
    data: list[str] = []
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            for raw in response:
                line = raw.decode("utf-8", errors="replace").rstrip("\r\n")
                if not line:
                    if data:
                        events.append((name or "message", json.loads("\n".join(data))))
                    name, data = None, []
                    continue
                if line.startswith("event:"):
                    name = line.split(":", 1)[1].strip()
                elif line.startswith("data:"):
                    data.append(line.split(":", 1)[1].lstrip())
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        raise StackError(f"{url} responded {error.code}: {body[:400]}") from error
    except urllib.error.URLError as error:
        raise StackError(f"{url} is unreachable: {error.reason}") from error
    if data:
        events.append((name or "message", json.loads("\n".join(data))))
    return events


def require_configuration(base: str) -> tuple[str, dict]:
    """The smoke model, and the provider the gateway says it is configured with.

    Raises :class:`BlockedError` rather than failing when something is simply not set up here: "not
    configured on this machine" and "broken" are different states, and reporting the first as the
    second sends somebody looking for a defect that does not exist.
    """
    smoke_model = setting("IACODE_GATEWAY_SMOKE_MODEL")
    if not smoke_model:
        raise BlockedError(
            "IACODE_GATEWAY_SMOKE_MODEL is not set. It names the 'provider:model' this check is "
            "authorised to spend tokens on, and there is no safe default: choosing one would mean "
            "spending on a model nobody authorised.")
    if ":" not in smoke_model:
        raise StackError(
            f"IACODE_GATEWAY_SMOKE_MODEL is {smoke_model!r}, which is not 'provider:model'. "
            f"A bare identifier is ambiguous because two providers may expose the same one.")

    _status, health = request_json(f"{base}/api/v1/gateway/health",
                                   timeout=READ_TIMEOUT_SECONDS)
    provider_id = smoke_model.split(":", 1)[0]
    providers = {item["provider"]: item for item in health.get("providers", [])}
    provider = providers.get(provider_id)
    if provider is None:
        raise StackError(
            f"the gateway knows no provider {provider_id!r}; the configured providers are "
            + (", ".join(sorted(providers)) or "none"))
    if not provider["addressConfigured"]:
        raise BlockedError(
            f"provider {provider_id!r} has no address. Set {provider['addressVariable']} in "
            f"infra/compose/.env and restart the stack.")
    if not provider["credentialConfigured"]:
        raise BlockedError(
            f"provider {provider_id!r} has no credential. Set {provider['credentialVariable']} in "
            f"infra/compose/.env and restart the stack. The value is never read by this script, "
            f"never printed and never written to the report.")
    if not provider["enabled"]:
        raise BlockedError(
            f"provider {provider_id!r} is disabled in .iacode/policies/providers.json.")
    return smoke_model, provider


def check_catalog(base: str, smoke_model: str) -> list[Check]:
    """One real synchronisation, repeated once, and the model this check is authorised to use."""
    checks: list[Check] = []
    provider_id, model_id = smoke_model.split(":", 1)

    status, first = request_json(f"{base}/api/v1/gateway/models/sync",
                                 {"provider": provider_id}, timeout=INFERENCE_TIMEOUT_SECONDS)
    outcome = next((item for item in first["outcomes"] if item["provider"] == provider_id), None)
    if outcome is None:
        raise StackError(f"the synchronisation reported nothing for {provider_id!r}")
    if outcome["errors"]:
        raise StackError(
            f"the catalog could not be synchronised: {'; '.join(outcome['errors'])[:400]}")
    discovered = outcome["added"] + outcome["updated"] + outcome["unchanged"]
    checks.append(Check("catalog.sync", status == 200 and discovered >= 1,
                        f"{discovered} model(s) from the provider's own API",
                        {"added": outcome["added"], "updated": outcome["updated"],
                         "deactivated": outcome["deactivated"],
                         "unchanged": outcome["unchanged"]}))

    _status, second = request_json(f"{base}/api/v1/gateway/models/sync",
                                   {"provider": provider_id},
                                   timeout=INFERENCE_TIMEOUT_SECONDS)
    repeated = next(item for item in second["outcomes"] if item["provider"] == provider_id)
    checks.append(Check(
        "catalog.idempotent",
        repeated["added"] == 0 and repeated["deactivated"] == 0,
        f"a second synchronisation added {repeated['added']} and deactivated "
        f"{repeated['deactivated']}",
        {"unchanged": repeated["unchanged"], "updated": repeated["updated"]}))

    _status, listing = request_json(
        f"{base}/api/v1/gateway/models?provider={provider_id}&active=true",
        timeout=READ_TIMEOUT_SECONDS)
    models = {item["model"]: item for item in listing["models"]}
    checks.append(Check("catalog.persisted", len(models) >= 1,
                        f"{len(models)} active model(s) in the catalog",
                        {"total": listing["total"]}))

    present = model_id in models
    checks.append(Check(
        "catalog.smoke_model_present", present,
        f"{smoke_model} is {'in' if present else 'NOT in'} the discovered catalog; it is never "
        f"substituted, because spending on a different model is how a surprise bill happens"))
    if not present:
        raise StackError(
            f"the configured smoke model {smoke_model!r} is not in the provider's catalog. "
            f"Correct IACODE_GATEWAY_SMOKE_MODEL; no other model is used in its place.")

    normalised = models[model_id]
    checks.append(Check(
        "catalog.normalised",
        bool(normalised.get("displayName")) and "capabilities" in normalised,
        "the provider's record was normalised into the catalog's shape",
        {"contextWindow": normalised.get("contextWindow"),
         "streaming": normalised["capabilities"].get("streaming", {}).get("state"),
         "provenance": normalised["capabilities"].get("streaming", {}).get("provenance")}))
    return checks


def check_inference(base: str, smoke_model: str) -> tuple[list[Check], str]:
    """One short generation. The answer is checked, not merely the status code."""
    status, answer = request_json(f"{base}/api/v1/gateway/infer", {
        "messages": [{"role": "user", "content": PROMPT}],
        "model": smoke_model,
        "maxOutputTokens": MAX_OUTPUT_TOKENS,
        "temperature": 0,
    }, timeout=INFERENCE_TIMEOUT_SECONDS)

    provider_id, model_id = smoke_model.split(":", 1)
    checks = [
        Check("inference.answered", status == 200 and EXPECTED in answer["content"],
              f"the model answered with {EXPECTED!r}" if EXPECTED in answer["content"]
              else f"the answer did not contain {EXPECTED!r}: {answer['content'][:120]!r}"),
        Check("inference.attributed",
              answer["provider"] == provider_id and answer["model"] == model_id,
              f"answered by {answer['provider']}:{answer['model']} over {answer['endpoint']}",
              {"route": answer["route"]["reason"], "endpoint": answer["endpoint"]}),
        Check("inference.latency", answer["latencyMs"] > 0,
              f"{answer['latencyMs']:.0f} ms"),
        Check("inference.usage", True,
              "usage as the provider reported it; absent fields stay absent",
              dict(answer["usage"])),
        Check("inference.cost_is_not_invented", answer["cost"] is None,
              "no pricing is configured, so the cost is absent rather than zero"),
    ]
    return checks, answer["requestId"]


def check_streaming(base: str, smoke_model: str) -> list[Check]:
    """One short stream. Start, at least one delta, an end, and nothing delivered twice."""
    events = read_stream(f"{base}/api/v1/gateway/stream", {
        "messages": [{"role": "user", "content": PROMPT}],
        "model": smoke_model,
        "maxOutputTokens": MAX_OUTPUT_TOKENS,
        "temperature": 0,
    }, timeout=INFERENCE_TIMEOUT_SECONDS)

    kinds = [name for name, _payload in events]
    deltas = [payload for name, payload in events if name == "text_delta"]
    text = "".join(payload.get("text", "") for payload in deltas)
    sequences = [payload.get("sequence") for _name, payload in events
                 if payload.get("sequence") is not None]
    failures = [payload for name, payload in events if name == "error"]

    return [
        Check("stream.started", kinds[:1] == ["start"],
              f"the first event was {kinds[0] if kinds else 'nothing'}"),
        Check("stream.delivered", len(deltas) >= 1,
              f"{len(deltas)} content event(s) carrying {len(text)} character(s)"),
        Check("stream.ended", kinds[-1:] == ["end"] and not failures,
              f"the last event was {kinds[-1] if kinds else 'nothing'}"),
        Check("stream.answered", EXPECTED in text,
              f"the streamed answer contained {EXPECTED!r}" if EXPECTED in text
              else f"the streamed answer did not contain {EXPECTED!r}: {text[:120]!r}"),
        Check("stream.not_duplicated",
              sequences == sorted(set(sequences)) and text.count(EXPECTED) == 1,
              "every sequence number is distinct and ascending, and the answer appears once",
              {"events": len(events)}),
    ]


def check_persistence(request_id: str, smoke_model: str) -> list[Check]:
    """The recorded call, read from the database the API wrote it to."""
    provider_id, model_id = smoke_model.split(":", 1)
    query = (
        "SELECT c.status, c.latency_ms, c.input_tokens, c.output_tokens, c.endpoint, "
        "c.route, c.retry_count, c.fallback_count, c.request_fingerprint, p.slug, m.slug "
        "FROM model_calls c LEFT JOIN providers p ON p.id = c.provider_id "
        "LEFT JOIN models m ON m.id = c.model_id "
        f"WHERE c.request_id = '{request_id}'")
    result = psql(query)
    if not result.ok:
        raise StackError(f"the recorded call could not be read: {result.output[:300]}")
    rows = [line for line in result.stdout.splitlines() if line.strip() and "|" in line]
    if not rows:
        raise StackError(f"no model_call was recorded for request {request_id}")
    fields = rows[0].split("|")

    columns = psql(
        "SELECT column_name FROM information_schema.columns "
        "WHERE table_schema = 'public' AND table_name = 'model_calls'")
    names = {line.strip() for line in columns.stdout.splitlines() if line.strip()}

    return [
        Check("persistence.recorded", fields[0] == "SUCCEEDED",
              f"the call is recorded as {fields[0]}",
              {"latencyMs": fields[1], "inputTokens": fields[2], "outputTokens": fields[3],
               "endpoint": fields[4], "route": fields[5] or None,
               "retries": fields[6], "fallbacks": fields[7]}),
        Check("persistence.attributed",
              fields[9] == provider_id and fields[10] == model_id,
              f"recorded against {fields[9]}:{fields[10]}"),
        Check("persistence.fingerprinted", len(fields[8]) == 64,
              "a request fingerprint was stored for correlation"),
        Check("persistence.no_prompt",
              not names & {"prompt", "messages", "completion", "response", "content"},
              "the table has no column that could hold a prompt or a completion",
              {"columns": len(names)}),
    ]


def check_observability(prometheus: str) -> list[Check]:
    """Prometheus scraped the instruments the call moved."""
    status, body = request_json(
        f"{prometheus}/api/v1/query?query=iacode_gateway_requests_total",
        timeout=READ_TIMEOUT_SECONDS)
    series = body.get("data", {}).get("result", []) if status == 200 else []
    total = sum(float(item["value"][1]) for item in series)
    return [
        Check("observability.scraped", bool(series) and total >= 1,
              f"{len(series)} gateway request series, {total:.0f} observation(s)",
              {"series": len(series)}),
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--report", type=Path, default=None,
                        help="write a machine-readable result document to this path")
    arguments = parser.parse_args()

    api = f"http://127.0.0.1:{published_port('api', 8000)}"
    prometheus = f"http://127.0.0.1:{published_port('prometheus', 9090)}"

    try:
        smoke_model, provider = require_configuration(api)
    except BlockedError as blocked:
        log("GATEWAY_SMOKE=BLOCKED")
        log(str(blocked))
        if arguments.report:
            arguments.report.parent.mkdir(parents=True, exist_ok=True)
            arguments.report.write_text(json.dumps({
                "result": "BLOCKED", "reason": str(blocked), "checks": [],
            }, indent=2) + "\n", encoding="utf-8", newline="\n")
        return BLOCKED_EXIT

    log(f"provider {provider['provider']} is configured; smoke model {smoke_model}")

    checks: list[Check] = []
    checks += check_catalog(api, smoke_model)
    inference, request_id = check_inference(api, smoke_model)
    checks += inference
    checks += check_streaming(api, smoke_model)
    checks += check_persistence(request_id, smoke_model)
    checks += check_observability(prometheus)

    failed = [check for check in checks if not check.ok]
    for check in checks:
        log(f"[{'PASS' if check.ok else 'FAIL'}] {check.name:34} {check.detail}")

    if arguments.report:
        arguments.report.parent.mkdir(parents=True, exist_ok=True)
        arguments.report.write_text(json.dumps({
            "result": "PASS" if not failed else "FAIL",
            "provider": provider["provider"],
            "adapter": provider["adapter"],
            "smokeModel": smoke_model,
            "prompt": PROMPT,
            "maxOutputTokens": MAX_OUTPUT_TOKENS,
            "requestId": request_id,
            "checks": [
                {"name": check.name, "result": "PASS" if check.ok else "FAIL",
                 "detail": check.detail, **({"data": check.data} if check.data else {})}
                for check in checks
            ],
        }, indent=2) + "\n", encoding="utf-8", newline="\n")
        log(f"wrote {arguments.report}")

    log(f"GATEWAY_SMOKE={'PASS' if not failed else 'FAIL'} "
        f"{len(checks) - len(failed)}/{len(checks)} checks")
    return 0 if not failed else 1


if __name__ == "__main__":
    main_guard(main)
