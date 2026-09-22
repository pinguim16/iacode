#!/usr/bin/env python3
"""Prove the running stack actually works, end to end.

Not a health check. Health says a process is alive; this exercises the paths a caller uses:

1. the API answers ``/health``, ``/ready`` and ``/version``;
2. readiness reports every mandatory dependency as ``UP``;
3. the web shell serves its page and its runtime configuration;
4. Prometheus has both of its IACode targets up;
5. Grafana reports itself healthy and has the provisioned datasource;
6. a real Temporal workflow executes in the worker and returns the worker's own observations.

The last one is the point. Everything above it proves a connection exists; only executing a
workflow proves the durable-execution path works, because the activity runs in a different process
and its result travels back through Temporal's history.

    python scripts/iacode/smoke.py
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from compose import StackError, log, main_guard, published_port, read_env_file, run_in

TIMEOUT_SECONDS = 15


@dataclass
class Check:
    name: str
    ok: bool
    detail: str


def http_json(url: str, accept_status: tuple[int, ...] = (200,)) -> tuple[int, dict]:
    request = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8")
        if error.code in accept_status:
            return error.code, json.loads(body)
        raise StackError(f"{url} responded {error.code}: {body[:300]}") from error
    except urllib.error.URLError as error:
        raise StackError(f"{url} is unreachable: {error.reason}") from error


def http_text(url: str) -> str:
    try:
        with urllib.request.urlopen(url, timeout=TIMEOUT_SECONDS) as response:
            return response.read().decode("utf-8", errors="replace")
    except urllib.error.URLError as error:
        raise StackError(f"{url} is unreachable: {error}") from error


def check_api(base: str) -> list[Check]:
    checks: list[Check] = []

    _status, health = http_json(f"{base}/health")
    checks.append(Check("api.health", health.get("status") == "UP",
                        f"status={health.get('status')} version={health.get('version')}"))

    status, ready = http_json(f"{base}/ready", accept_status=(200, 503))
    dependencies = {item["name"]: item["status"] for item in ready.get("dependencies", [])}
    down = sorted(name for name, state in dependencies.items() if state != "UP")
    checks.append(Check(
        "api.ready",
        status == 200 and ready.get("status") == "READY" and not down,
        f"HTTP {status} status={ready.get('status')} "
        + (f"down={', '.join(down)}" if down else "every dependency UP")))
    for name in ("postgres", "redis", "minio", "temporal"):
        checks.append(Check(f"dependency.{name}", dependencies.get(name) == "UP",
                            f"{dependencies.get(name, 'not reported')}"))

    _status, version = http_json(f"{base}/version")
    checks.append(Check("api.version", bool(version.get("version")),
                        f"{version.get('version')} commit={version.get('commit')} "
                        f"python={version.get('pythonVersion')}"))

    metrics = http_text(f"{base}/metrics")
    checks.append(Check("api.metrics", "iacode_http_requests_total" in metrics,
                        f"{len(metrics.splitlines())} exposition lines"))

    # An endpoint that reported the configuration would be the obvious way to leak a password.
    leaked = [token for token in ("PASSWORD", "SECRET_KEY", "postgresql+asyncpg://")
              if token in json.dumps(version) or token in json.dumps(health)]
    checks.append(Check("api.no_secret_exposed", not leaked,
                        "no configuration value is exposed" if not leaked
                        else f"exposed: {', '.join(leaked)}"))
    return checks


def check_web(base: str) -> list[Check]:
    page = http_text(f"{base}/")
    _status, config = http_json(f"{base}/config.json")
    return [
        Check("web.page", "<app-root></app-root>" in page, f"{len(page)} bytes served"),
        Check("web.config", "apiBaseUrl" in config,
              f"apiBaseUrl={config.get('apiBaseUrl') or '<same origin>'}"),
        # The page is public; a credential written into its runtime configuration would be too.
        Check("web.config_has_no_secret",
              set(config) == {"apiBaseUrl"},
              f"keys={sorted(config)}"),
    ]


#: Prometheus scrapes every fifteen seconds (`infra/prometheus/prometheus.yml`). On a stack that has
#: just started, the last scrape of a target can predate that target's readiness, and the target
#: reads "down" until the next one: the fresh installation of GATE-2-CP-0002's verification failed
#: on exactly that. The check waits up to three scrape intervals for both targets, asking only
#: Prometheus. G2-F-014, LSN-0049.
TARGET_WAIT_SECONDS = 45.0
TARGET_POLL_SECONDS = 3.0
REQUIRED_TARGETS = ("iacode-api", "iacode-worker")


def _active_targets(base: str) -> tuple[dict, list, dict]:
    _status, payload = http_json(f"{base}/api/v1/targets?state=active")
    targets = payload.get("data", {}).get("activeTargets", [])
    return payload, targets, {item.get("labels", {}).get("job"): item.get("health")
                              for item in targets}


def check_prometheus(base: str) -> list[Check]:
    started = time.monotonic()
    payload, targets, by_job = _active_targets(base)
    while any(by_job.get(job) != "up" for job in REQUIRED_TARGETS) and (
            time.monotonic() - started < TARGET_WAIT_SECONDS):
        time.sleep(TARGET_POLL_SECONDS)
        payload, targets, by_job = _active_targets(base)
    checks = [Check("prometheus.reachable", payload.get("status") == "success",
                    f"{len(targets)} active target(s)")]
    for job in REQUIRED_TARGETS:
        checks.append(Check(f"prometheus.target.{job}", by_job.get(job) == "up",
                            f"{by_job.get(job, 'absent')}"))
    return checks


def check_grafana(base: str) -> list[Check]:
    _status, health = http_json(f"{base}/api/health")
    return [Check("grafana.health", health.get("database") == "ok",
                  f"version={health.get('version')} database={health.get('database')}")]


def check_workflow() -> list[Check]:
    """Execute a real workflow through the worker.

    Run from a new container of the worker image, on the stack's network, so the check uses the
    same SDK and the same configuration the worker uses. Driving it from the host would need the
    SDK installed there and would test a different client.
    """
    result = run_in("worker", "python", "-m", "iacode_orchestrator.smoke_client",
                    timeout=180)
    if not result.ok:
        return [Check("temporal.workflow", False,
                      result.stdout.strip().splitlines()[-1] if result.stdout.strip()
                      else f"exit {result.exit_code}")]
    payload = None
    for line in result.stdout.splitlines():
        line = line.strip()
        if line.startswith("{") and "workflowId" in line:
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                continue
    if payload is None:
        return [Check("temporal.workflow", False,
                      "the workflow client produced no result document")]
    return [
        Check("temporal.workflow", payload.get("message") == "foundation-smoke",
              f"workflowId={payload.get('workflowId')} executedAt={payload.get('executedAt')}"),
        # The activity reports where it ran. A constant would pass a smoke check that proves
        # nothing; this value can only come from the worker process.
        Check("temporal.activity_ran_in_worker", bool(payload.get("workerIdentity")),
              f"workerIdentity={payload.get('workerIdentity')}"),
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--json", action="store_true", help="emit the result as JSON")
    arguments = parser.parse_args()

    values = read_env_file()
    api = f"http://127.0.0.1:{published_port('api', 8000)}"
    web = f"http://127.0.0.1:{published_port('web', 8080)}"
    prometheus = f"http://127.0.0.1:{published_port('prometheus', 9090)}"
    grafana = f"http://127.0.0.1:{published_port('grafana', 3000)}"
    log(f"api={api} web={web} prometheus={prometheus} grafana={grafana}")
    if not values:
        raise StackError("the compose environment file is empty")

    checks: list[Check] = []
    checks += check_api(api)
    checks += check_web(web)
    checks += check_prometheus(prometheus)
    checks += check_grafana(grafana)
    checks += check_workflow()

    failed = [check for check in checks if not check.ok]
    if arguments.json:
        print(json.dumps({
            "result": "PASS" if not failed else "FAIL",
            "total": len(checks),
            "passed": len(checks) - len(failed),
            "checks": [check.__dict__ for check in checks],
        }, indent=2))
    else:
        for check in checks:
            print(f"[{'PASS' if check.ok else 'FAIL'}] {check.name}: {check.detail}")
        print(f"SMOKE={'PASS' if not failed else 'FAIL'} "
              f"{len(checks) - len(failed)}/{len(checks)} checks")
    return 0 if not failed else 1


if __name__ == "__main__":
    main_guard(main)
