#!/usr/bin/env python3
"""The dependency-failure scenario: liveness holds, readiness tells the truth, both recover.

`docs/GATE-0-CHECKLIST.md` row 13.7. This is the scenario that proves the distinction between
``/health`` and ``/ready`` is real rather than documented. With a mandatory dependency stopped:

* ``/health`` stays ``UP``  — the process is fine, and restarting it would help nobody;
* ``/ready`` returns 503   — the service cannot accept work, and it names which dependency failed;
* the failure detail carries no credential, because a driver error quotes the connection string.

Then the dependency comes back and readiness recovers on its own, without restarting the API.

The dependency is stopped, never deleted: no volume is touched and no data is at risk.

    python scripts/iacode/scenarios/dependency_failure.py
    python scripts/iacode/scenarios/dependency_failure.py --service redis
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from compose import StackError, compose, log, main_guard, published_port

# Which service maps to which dependency name in the readiness payload.
DEPENDENCIES = {
    "postgres": "postgres",
    "redis": "redis",
    "minio": "minio",
}

# Which dependencies readiness should report as DOWN when a service is stopped.
#
# This is the *declared blast radius*, and declaring it is the point. Stopping PostgreSQL takes
# Temporal down with it, because Temporal persists into the same server — a real consequence of the
# decision recorded in ADR-0014 to run one database container rather than two. Asserting the
# expected set rather than "only the stopped one" is what makes that consequence a checked fact
# instead of a surprise, and what makes the *narrow* cases meaningful: stopping Redis must not take
# anything else with it, and this check now fails if it ever does.
BLAST_RADIUS = {
    "postgres": {"postgres", "temporal"},
    "redis": {"redis"},
    "minio": {"minio"},
}

RECOVERY_TIMEOUT_SECONDS = 120.0


def probe(base: str, path: str) -> tuple[int, dict]:
    request = urllib.request.Request(f"{base}{path}", headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        return error.code, json.loads(error.read().decode("utf-8"))


def wait_until_ready(base: str, expected: str, timeout: float = RECOVERY_TIMEOUT_SECONDS) -> str:
    """Poll readiness until it reports ``expected``, or give up and return what it last said."""
    deadline = time.monotonic() + timeout
    status = "unknown"
    while time.monotonic() < deadline:
        try:
            _code, body = probe(base, "/ready")
            status = body.get("status", "unknown")
            if status == expected:
                return status
        except (urllib.error.URLError, OSError) as error:
            status = f"unreachable: {error}"
        time.sleep(3)
    return status


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--service", choices=sorted(DEPENDENCIES), default="postgres",
                        help="which mandatory dependency to stop")
    parser.add_argument("--json", action="store_true")
    arguments = parser.parse_args()

    service = arguments.service
    dependency = DEPENDENCIES[service]
    base = f"http://127.0.0.1:{published_port('api', 8000)}"
    steps: list[dict[str, object]] = []
    started = time.monotonic()

    def record(name: str, ok: bool, detail: str) -> None:
        steps.append({"step": name, "ok": ok, "detail": detail})
        log(f"[{'OK' if ok else 'FAILED'}] {name}: {detail}")

    code, body = probe(base, "/ready")
    if not (code == 200 and body.get("status") == "READY"):
        raise StackError(
            f"the stack is not ready before the scenario starts (HTTP {code}, "
            f"{body.get('status')!r}); there is nothing to prove about a failure it is already in")
    record("baseline_ready", True, "readiness is READY before the dependency is stopped")

    try:
        log(f"stopping {service}")
        compose("stop", service, check=True)

        code, health = probe(base, "/health")
        record("health_stays_up", code == 200 and health.get("status") == "UP",
               f"HTTP {code} status={health.get('status')!r}")

        code, ready = probe(base, "/ready")
        reported = {item["name"]: item for item in ready.get("dependencies", [])}
        failing = reported.get(dependency, {})
        record("readiness_refuses", code == 503 and ready.get("status") == "NOT_READY",
               f"HTTP {code} status={ready.get('status')!r}")
        record("failure_is_named", failing.get("status") == "DOWN",
               f"{dependency}={failing.get('status')!r} "
               f"detail={str(failing.get('detail'))[:110]!r}")
        record("failure_has_a_reason", bool(failing.get("detail")),
               "the payload says why the probe failed"
               if failing.get("detail") else "the dependency is DOWN with no reason given")

        # A driver error routinely quotes the connection string it failed on, password included.
        payload = json.dumps(ready)
        leaked = [token for token in ("PGPASSWORD", "@postgres:5432", "@minio:9000", "@redis:6379")
                  if token in payload]
        record("failure_leaks_no_credential", not leaked,
               "no connection string in the payload" if not leaked
               else f"leaked: {', '.join(leaked)}")

        observed_down = {name for name, item in reported.items()
                         if item.get("status") != "UP"}
        expected_down = BLAST_RADIUS[service]
        record("blast_radius_is_as_declared", observed_down == expected_down,
               f"down={sorted(observed_down)} expected={sorted(expected_down)}"
               + ("" if observed_down == expected_down
                  else f"; unexpected={sorted(observed_down - expected_down)}"
                       f" missing={sorted(expected_down - observed_down)}"))
    finally:
        log(f"starting {service} again")
        compose("start", service, capture=False)

    status = wait_until_ready(base, "READY")
    record("readiness_recovers", status == "READY",
           f"readiness returned to {status!r} without restarting the API")

    failed = [step for step in steps if not step["ok"]]
    elapsed = time.monotonic() - started
    if arguments.json:
        print(json.dumps({
            "scenario": "dependency_failure",
            "service": service,
            "result": "PASS" if not failed else "FAIL",
            "durationSeconds": round(elapsed, 1),
            "steps": steps,
        }, indent=2))
    log(f"DEPENDENCY_FAILURE={'PASS' if not failed else 'FAIL'} service={service} "
        f"{len(steps) - len(failed)}/{len(steps)} steps in {elapsed:.0f}s")
    return 0 if not failed else 1


if __name__ == "__main__":
    main_guard(main)
