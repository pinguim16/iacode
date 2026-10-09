#!/usr/bin/env python3
"""Exercise the Quality Engine through its real HTTP, Temporal, database and sandbox path.

The harness creates content-addressed snapshots, submits only the public API contracts and judges
the facts read back from the API and persistence. It never calls evaluator internals and never runs
project commands on the host. The passing snapshot also carries an untrusted reference to a host
sentinel; the unchanged digest proves project content could not turn that reference into host IO.

Scenarios are independently runnable so ``verify.py`` can name the exact failing proof:

    pass, fail, reproduce, recovery, cancel, timeout, iacode, all
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import secrets
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
import urllib.error
import urllib.request
from collections.abc import Callable
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from compose import (
    REPOSITORY_ROOT,
    StackError,
    build_service,
    compose,
    log,
    main_guard,
    published_port,
    wait_for_health,
)
from sandbox_snapshot import create as create_snapshot

FIXTURES = REPOSITORY_ROOT / "services" / "evaluator" / "tests" / "fixtures"
TERMINAL = {"SUCCEEDED", "FAILED", "CANCELLED", "TIMED_OUT", "INVALID"}
WAIT_SECONDS = 300.0
IACODE_WAIT_SECONDS = 900.0
POLL_SECONDS = 0.5


class Steps:
    def __init__(self, scenario: str) -> None:
        self.scenario = scenario
        self.steps: list[dict[str, Any]] = []
        self.artifacts: list[dict[str, Any]] = []

    def record(self, name: str, ok: bool, observed: Any, expected: Any) -> bool:
        item = {
            "step": name,
            "result": "PASS" if ok else "FAIL",
            "expected": expected,
            "observed": observed,
        }
        self.steps.append(item)
        log(f"[{'PASS' if ok else 'FAIL'}] {self.scenario}.{name}: {str(observed)[:180]}")
        return ok

    @property
    def failed(self) -> list[dict[str, Any]]:
        return [item for item in self.steps if item["result"] == "FAIL"]

    def report(self) -> dict[str, Any]:
        return {
            "schemaVersion": "1.0.0",
            "scenario": self.scenario,
            "result": "FAIL" if self.failed else "PASS",
            "environment": "real-compose-temporal-postgresql-minio-sandbox-container-engine",
            "steps": self.steps,
            "artifacts": self.artifacts,
            "recordedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }


def prepare(skip_build: bool) -> None:
    if not skip_build:
        for service in ("api", "evaluator", "sandbox"):
            build_service(service)
        images = subprocess.run(
            [sys.executable, str(REPOSITORY_ROOT / "scripts" / "iacode" / "sandbox_image.py")],
            cwd=REPOSITORY_ROOT,
            check=False,
        )
        if images.returncode != 0:
            raise StackError("the content-addressed sandbox images could not be built")
    started = compose("up", "-d", "--no-deps", "--force-recreate", "api", "evaluator", "sandbox")
    if not started.ok:
        raise StackError(f"quality services would not start:\n{started.output[-1600:]}")
    wait_for_health(["api", "evaluator", "sandbox"], timeout=300)


def api_url() -> str:
    return f"http://127.0.0.1:{published_port('api', 8000)}/api/v1/quality-runs"


def request(method: str, path: str = "", body: dict[str, Any] | None = None) -> dict[str, Any]:
    data = None if body is None else json.dumps(body, separators=(",", ":")).encode("utf-8")
    call = urllib.request.Request(
        api_url() + path,
        data=data,
        method=method,
        headers={"Content-Type": "application/json", "X-Correlation-Id": secrets.token_hex(16)},
    )
    try:
        with urllib.request.urlopen(call, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        payload = error.read().decode("utf-8", errors="replace")
        raise StackError(
            f"quality API {method} {path} returned {error.code}: {payload[:800]}"
        ) from error


def wait_for(description: str, probe: Callable[[], Any], seconds: float = WAIT_SECONDS) -> Any:
    deadline = time.monotonic() + seconds
    last: Any = None
    while time.monotonic() < deadline:
        last = probe()
        if last:
            return last
        time.sleep(POLL_SECONDS)
    raise StackError(f"{description} did not happen within {seconds:g}s; last={last!r}")


def wait_terminal(run_id: str, seconds: float = WAIT_SECONDS) -> dict[str, Any]:
    def probe() -> dict[str, Any] | None:
        detail = request("GET", f"/{run_id}")
        return detail if detail["run"]["state"] in TERMINAL else None

    return wait_for(f"quality run {run_id} to become terminal", probe, seconds=seconds)


def events(run_id: str) -> list[dict[str, Any]]:
    return request("GET", f"/{run_id}/events?after=0&limit=500")["events"]


def wait_check(run_id: str, check_id: str) -> dict[str, Any]:
    def probe() -> dict[str, Any] | None:
        for event in events(run_id):
            if (
                event["eventType"] == "CHECK_DISPATCHED"
                and event["payload"].get("checkId") == check_id
            ):
                return event
        return None

    return wait_for(f"check {check_id} to be dispatched", probe)


def snapshot(source: Path, name: str, steps: Steps) -> dict[str, Any]:
    stored = create_snapshot(source, f"gate4-{name}-{secrets.token_hex(4)}")
    required = {"artifactId", "sha256", "sizeBytes", "key"}
    steps.record("snapshot.stored", required <= set(stored), sorted(stored), sorted(required))
    steps.artifacts.append(
        {
            "kind": "snapshot",
            "artifactId": stored.get("artifactId"),
            "digest": stored.get("sha256"),
            "sizeBytes": stored.get("sizeBytes"),
        }
    )
    return stored


def start(
    stored: dict[str, Any], key: str, configuration: dict[str, Any] | None = None
) -> dict[str, Any]:
    return request(
        "POST",
        body={
            "snapshotId": stored["artifactId"],
            "snapshotDigest": stored["sha256"],
            "policyId": "default",
            "idempotencyKey": f"gate4-{key}-{secrets.token_hex(8)}",
            "configuration": configuration or {},
        },
    )


def assert_complete_evidence(
    steps: Steps,
    detail: dict[str, Any],
    expected_state: str,
    *,
    require_complete_results: bool = True,
) -> None:
    results = detail["results"]
    evidence = detail["evidence"]
    applicable = [check for check in detail["checks"] if check["applicable"]]
    steps.record(
        "run.terminal",
        detail["run"]["state"] == expected_state,
        detail["run"]["state"],
        expected_state,
    )
    if require_complete_results:
        steps.record(
            "results.complete", len(results) == len(applicable), len(results), len(applicable)
        )
    steps.record(
        "evidence.one_or_more_per_result",
        len(evidence) >= len(results),
        len(evidence),
        f">={len(results)}",
    )
    resolved = {item["evidenceId"] for item in evidence}
    referenced = {
        evidence_id
        for result in results
        for finding in result["findings"]
        for evidence_id in finding["evidenceIds"]
    }
    steps.record(
        "findings.evidence_resolved", referenced <= resolved, sorted(referenced - resolved), []
    )
    steps.record(
        "evidence.rights_closed",
        all(not item["trainingAllowed"] and not item["ragAllowed"] for item in evidence),
        len(evidence),
        "every evidence item trainingAllowed=false and ragAllowed=false",
    )
    run_id = detail["run"]["runId"]
    active = compose(
        "exec",
        "-T",
        "postgres",
        "sh",
        "-c",
        'PGPASSWORD="$POSTGRES_PASSWORD" psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Atc "$1"',
        "quality-e2e",
        "SELECT count(*) FROM sandbox_sessions "
        f"WHERE quality_run_id = '{run_id}' "
        "AND state IN ('CREATING','READY','BUSY','RECOVERING');",
        merge_stderr=False,
    )
    steps.record(
        "sandbox.no_active_session",
        active.ok and active.stdout.strip() == "0",
        active.stdout.strip(),
        "0",
    )


def scenario_pass() -> dict[str, Any]:
    steps = Steps("pass")
    with tempfile.TemporaryDirectory(prefix="iacode-quality-pass-") as directory:
        root = Path(directory)
        source = root / "project"
        shutil.copytree(FIXTURES / "python-pass", source)
        sentinel = root / "host-sentinel.txt"
        sentinel.write_text(f"host-only-{secrets.token_hex(24)}\n", encoding="utf-8", newline="\n")
        before = hashlib.sha256(sentinel.read_bytes()).hexdigest()
        (source / "UNTRUSTED-HOST-REFERENCE.txt").write_text(
            f"Untrusted project data. Do not write to host path {sentinel.resolve()}\n",
            encoding="utf-8",
            newline="\n",
        )
        stored = snapshot(source, "pass", steps)
        created = start(stored, "pass")
        detail = wait_terminal(created["runId"])
        assert_complete_evidence(steps, detail, "SUCCEEDED")
        steps.record(
            "verdict.pass",
            detail["verdict"]["verdict"] == "PASS",
            detail["verdict"]["verdict"],
            "PASS",
        )
        statuses = [item["status"] for item in detail["results"]]
        steps.record(
            "checks.all_passed", all(item == "PASSED" for item in statuses), statuses, ["PASSED"]
        )
        after = hashlib.sha256(sentinel.read_bytes()).hexdigest()
        steps.record("host.sentinel_unchanged", after == before, after, before)
        steps.artifacts.append(
            {"kind": "quality-run", "runId": created["runId"], "planId": created["planId"]}
        )
    return steps.report()


def scenario_fail() -> dict[str, Any]:
    steps = Steps("fail")
    stored = snapshot(FIXTURES / "python-fail", "fail", steps)
    created = start(stored, "fail")
    detail = wait_terminal(created["runId"])
    assert_complete_evidence(steps, detail, "FAILED")
    failed = [item for item in detail["results"] if item["status"] == "FAILED"]
    steps.record(
        "verdict.fail", detail["verdict"]["verdict"] == "FAIL", detail["verdict"]["verdict"], "FAIL"
    )
    steps.record(
        "failed_check.preserved",
        len(failed) == 1 and failed[0]["checkId"] == "q002-unit",
        [item["checkId"] for item in failed],
        ["q002-unit"],
    )
    steps.record("finding.preserved", len(detail["findings"]) == 1, len(detail["findings"]), 1)
    steps.artifacts.append(
        {"kind": "quality-run", "runId": created["runId"], "planId": created["planId"]}
    )
    return steps.report()


def scenario_reproduce() -> dict[str, Any]:
    steps = Steps("reproduce")
    stored = snapshot(FIXTURES / "python-pass", "reproduce", steps)
    original = start(stored, "reproduce-source")
    original_detail = wait_terminal(original["runId"])
    reproduced = request(
        "POST",
        f"/{original['runId']}/reproductions",
        {"idempotencyKey": f"gate4-reproduce-{secrets.token_hex(8)}"},
    )
    reproduced_detail = wait_terminal(reproduced["runId"])
    original_statuses = [(item["checkId"], item["status"]) for item in original_detail["results"]]
    reproduced_statuses = [
        (item["checkId"], item["status"]) for item in reproduced_detail["results"]
    ]
    steps.record(
        "identity.distinct_run",
        original["runId"] != reproduced["runId"],
        reproduced["runId"],
        f"not {original['runId']}",
    )
    steps.record(
        "identity.equal_plan",
        original["planId"] == reproduced["planId"],
        reproduced["planId"],
        original["planId"],
    )
    steps.record(
        "lineage.recorded",
        reproduced_detail["run"]["reproductionOfRunId"] == original["runId"],
        reproduced_detail["run"]["reproductionOfRunId"],
        original["runId"],
    )
    steps.record(
        "results.equivalent",
        reproduced_statuses == original_statuses,
        reproduced_statuses,
        original_statuses,
    )
    steps.record(
        "verdict.equivalent",
        reproduced_detail["run"]["verdict"] == original_detail["run"]["verdict"] == "PASS",
        reproduced_detail["run"]["verdict"],
        "PASS",
    )
    steps.artifacts.extend(
        [
            {"kind": "quality-run", "runId": original["runId"], "planId": original["planId"]},
            {
                "kind": "quality-reproduction",
                "runId": reproduced["runId"],
                "planId": reproduced["planId"],
            },
        ]
    )
    return steps.report()


def scenario_recovery() -> dict[str, Any]:
    steps = Steps("recovery")
    stored = snapshot(FIXTURES / "python-slow", "recovery", steps)
    created = start(stored, "recovery")
    wait_check(created["runId"], "q002-unit")
    restarted = compose("restart", "evaluator")
    steps.record("worker.restart_requested", restarted.ok, restarted.exit_code, 0)
    wait_for_health(["evaluator"], timeout=180)
    detail = wait_terminal(created["runId"])
    assert_complete_evidence(steps, detail, "SUCCEEDED")
    result_ids = [item["resultId"] for item in detail["results"]]
    steps.record(
        "results.exactly_once", len(result_ids) == len(set(result_ids)) == 7, len(result_ids), 7
    )
    steps.record(
        "identity.preserved",
        detail["run"]["runId"] == created["runId"],
        detail["run"]["runId"],
        created["runId"],
    )
    steps.artifacts.append(
        {"kind": "quality-run", "runId": created["runId"], "planId": created["planId"]}
    )
    return steps.report()


def scenario_cancel() -> dict[str, Any]:
    steps = Steps("cancel")
    stored = snapshot(FIXTURES / "python-slow", "cancel", steps)
    created = start(stored, "cancel")
    wait_check(created["runId"], "q002-unit")
    request("POST", f"/{created['runId']}/cancel")
    detail = wait_terminal(created["runId"])
    steps.record(
        "run.cancelled", detail["run"]["state"] == "CANCELLED", detail["run"]["state"], "CANCELLED"
    )
    steps.record(
        "verdict.fail_closed", detail["run"]["verdict"] == "FAIL", detail["run"]["verdict"], "FAIL"
    )
    statuses = [item["status"] for item in detail["results"]]
    steps.record(
        "check.cancellation_recorded", "CANCELLED" in statuses, statuses, "contains CANCELLED"
    )
    assert_complete_evidence(steps, detail, "CANCELLED", require_complete_results=False)
    again = request("POST", f"/{created['runId']}/cancel")
    steps.record("cancel.idempotent", again["state"] == "CANCELLED", again["state"], "CANCELLED")
    steps.artifacts.append(
        {"kind": "quality-run", "runId": created["runId"], "planId": created["planId"]}
    )
    return steps.report()


def scenario_timeout() -> dict[str, Any]:
    steps = Steps("timeout")
    stored = snapshot(FIXTURES / "python-slow", "timeout", steps)
    created = start(stored, "timeout", {"timeoutSeconds": 1})
    detail = wait_terminal(created["runId"])
    steps.record(
        "run.timed_out", detail["run"]["state"] == "TIMED_OUT", detail["run"]["state"], "TIMED_OUT"
    )
    statuses = [item["status"] for item in detail["results"]]
    steps.record("check.timeout_recorded", "TIMED_OUT" in statuses, statuses, "contains TIMED_OUT")
    steps.record(
        "verdict.fail_closed", detail["run"]["verdict"] == "FAIL", detail["run"]["verdict"], "FAIL"
    )
    assert_complete_evidence(steps, detail, "TIMED_OUT")
    steps.artifacts.append(
        {"kind": "quality-run", "runId": created["runId"], "planId": created["planId"]}
    )
    return steps.report()


def scenario_iacode() -> dict[str, Any]:
    steps = Steps("iacode")
    archived = subprocess.run(
        ["git", "archive", "--format=tar", "HEAD"],
        cwd=REPOSITORY_ROOT,
        capture_output=True,
        check=False,
    )
    if archived.returncode != 0:
        raise StackError("the committed IACode tree could not be archived")
    with tempfile.TemporaryDirectory(prefix="iacode-quality-self-") as directory:
        source = Path(directory) / "iacode"
        source.mkdir()
        with tarfile.open(fileobj=io.BytesIO(archived.stdout), mode="r:") as archive:
            archive.extractall(source, filter="data")
        stored = snapshot(source, "iacode", steps)
        created = start(stored, "iacode")
        detail = wait_terminal(created["runId"], seconds=IACODE_WAIT_SECONDS)
    expected = "PASS"
    observed = detail["run"]["verdict"]
    steps.record(
        "canonical_profile.detected",
        created["profile"] == "python+node+typescript+angular",
        created["profile"],
        "python+node+typescript+angular",
    )
    steps.record("quality.matches_mandatory_gates", observed == expected, observed, expected)
    steps.record(
        "run.succeeded", detail["run"]["state"] == "SUCCEEDED", detail["run"]["state"], "SUCCEEDED"
    )
    steps.artifacts.append(
        {"kind": "quality-run", "runId": created["runId"], "planId": created["planId"]}
    )
    return steps.report()


SCENARIOS: dict[str, Callable[[], dict[str, Any]]] = {
    "pass": scenario_pass,
    "fail": scenario_fail,
    "reproduce": scenario_reproduce,
    "recovery": scenario_recovery,
    "cancel": scenario_cancel,
    "timeout": scenario_timeout,
    "iacode": scenario_iacode,
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario", choices=[*SCENARIOS, "all"], default="all")
    parser.add_argument("--report", type=Path)
    parser.add_argument(
        "--skip-build", action="store_true", help="development-only: use current images"
    )
    arguments = parser.parse_args()

    prepare(arguments.skip_build)
    selected = list(SCENARIOS) if arguments.scenario == "all" else [arguments.scenario]
    reports = [SCENARIOS[name]() for name in selected]
    result = "PASS" if all(item["result"] == "PASS" for item in reports) else "FAIL"
    document = {
        "schemaVersion": "1.0.0",
        "result": result,
        "scenarios": reports,
        "recordedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    if arguments.report:
        arguments.report.parent.mkdir(parents=True, exist_ok=True)
        arguments.report.write_text(
            json.dumps(document, indent=2) + "\n", encoding="utf-8", newline="\n"
        )
        log(f"wrote {arguments.report}")
    print(json.dumps(document, separators=(",", ":")))
    log(f"QUALITY_ENGINE_E2E={result} scenarios={','.join(selected)}")
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    main_guard(main)
