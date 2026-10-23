#!/usr/bin/env python3
"""Exercise the Quality Engine through its real HTTP, Temporal, database and sandbox path.

The harness creates content-addressed snapshots, submits only the public API contracts and judges
the facts read back from the API and persistence. It never calls evaluator internals and never runs
project commands on the host. The passing snapshot also carries an untrusted reference to a host
sentinel; the unchanged digest proves project content could not turn that reference into host IO.

Scenarios are independently runnable so ``verify.py`` can name the exact failing proof:

    pass, fail, reproduce, recovery, cancel, timeout, iacode, secret-output, all
"""

from __future__ import annotations

import argparse
import hashlib
import json
import secrets
import shutil
import subprocess
import sys
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
from self_qualification_source import materialize_committed_source

FIXTURES = REPOSITORY_ROOT / "services" / "evaluator" / "tests" / "fixtures"
TERMINAL = {"SUCCEEDED", "FAILED", "CANCELLED", "TIMED_OUT", "INVALID"}
WAIT_SECONDS = 300.0
# Cover the unchanged canonical3600s run deadline plus60s to observe its terminal facts.
# The current-policy regression refuses drift; product/check deadlines are never changed here.
IACODE_WAIT_SECONDS = 3660.0
DURABLE_WAIT_SECONDS = 900.0
POLL_SECONDS = 0.5

# This observer runs inside the API image. It returns only counts and booleans, never history
# payloads, object contents, environment values or the synthetic marker.
HISTORY_OUTPUT_OBSERVER = r"""
import asyncio
import base64
import json
import os
import sys
from minio import Minio
from temporalio.client import Client
from iacode_common.secret_scanning import find_secret_kinds

async def main():
    run_id = sys.argv[1]
    marker = ("gh" + "p_" + "q" * 20).encode()
    client = await Client.connect(
        os.environ.get("IACODE_TEMPORAL_TARGET", "temporal:7233"),
        namespace=os.environ.get("IACODE_TEMPORAL_NAMESPACE", "default"),
    )
    handle = client.get_workflow_handle("iacode-quality-run-" + run_id)
    history = await handle.fetch_history()
    description = await handle.describe()
    payloads = []
    def visit(value):
        if isinstance(value, dict):
            for key, item in value.items():
                if key == "data" and isinstance(item, str):
                    payloads.append(base64.b64decode(item, validate=True))
                else:
                    visit(item)
        elif isinstance(value, list):
            for item in value:
                visit(item)
    document = json.loads(history.to_json())
    visit(document)
    failures = []
    scheduled = {}
    completed = set()
    def failure_metadata(value):
        if not isinstance(value, dict):
            return
        message = str(value.get("message", ""))
        failures.append({
            "type": value.get("applicationFailureInfo", {}).get("type"),
            "activityType": value.get("activityFailureInfo", {}).get(
                "activityType", {}).get("name"),
            "cancelled": "canceledFailureInfo" in value,
            "message": "[redacted]" if find_secret_kinds(message) else message[:300],
        })
        if value.get("cause"):
            failure_metadata(value["cause"])
    for event in document.get("events", []):
        for key, value in event.items():
            if key == "activityTaskScheduledEventAttributes":
                scheduled[str(event["eventId"])] = value.get("activityType", {}).get("name")
            elif key in {
                "activityTaskCompletedEventAttributes", "activityTaskFailedEventAttributes",
                "activityTaskCanceledEventAttributes", "activityTaskTimedOutEventAttributes",
            }:
                completed.add(str(value.get("scheduledEventId")))
            if isinstance(value, dict) and value.get("failure"):
                failure_metadata(value["failure"])
    objects = Minio(
        os.environ["IACODE_MINIO_ENDPOINT"],
        access_key=os.environ["IACODE_MINIO_ACCESS_KEY"],
        secret_key=os.environ["IACODE_MINIO_SECRET_KEY"],
        secure=os.environ.get("IACODE_MINIO_SECURE", "false").lower() == "true",
    )
    count = len(list(objects.list_objects(
        os.environ.get("IACODE_MINIO_BUCKET", "iacode-artifacts"),
        prefix="sandbox/" + run_id + "/", recursive=True,
    )))
    clean = bool(payloads) and all(marker not in item for item in payloads)
    print(json.dumps({"prohibitedBytesAbsent": clean, "payloadsScanned": len(payloads),
                      "workflowStatus": (description.status.name
                                         if description.status else "UNKNOWN"),
                      "sandboxObjects": count, "failures": failures[-10:],
                      "pendingActivityTypes": [v for k, v in scheduled.items()
                                               if k not in completed],
                      "containmentRefusals": sum(b"SANDBOX_OUTPUT_SECRET_DETECTED" in p
                                                 for p in payloads)}))

asyncio.run(main())
"""


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


def wait_check(run_id: str, check_id: str, seconds: float = WAIT_SECONDS) -> dict[str, Any]:
    def probe() -> dict[str, Any] | None:
        for event in events(run_id):
            if (
                event["eventType"] == "CHECK_DISPATCHED"
                and event["payload"].get("checkId") == check_id
            ):
                return event
        return None

    return wait_for(f"check {check_id} to be dispatched", probe, seconds=seconds)


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


def scenario_secret_output() -> dict[str, Any]:
    steps = Steps("secret-output")

    def terminal(identifier: str, label: str) -> dict[str, Any] | None:
        try:
            return wait_terminal(identifier)
        except StackError:
            try:
                state = request("GET", f"/{identifier}")["run"]["state"]
            except StackError:
                state = "UNAVAILABLE"
            steps.record(
                f"{label}.terminal", False, state, "terminal within the unchanged deadline"
            )
            observed = compose(
                "exec",
                "-T",
                "api",
                "python",
                "-c",
                HISTORY_OUTPUT_OBSERVER,
                identifier,
                merge_stderr=False,
            )
            steps.record(f"{label}.diagnostics_available", observed.ok, observed.ok, True)
            if observed.ok:
                steps.artifacts.append(
                    {
                        "kind": "control-history-diagnostics",
                        "runId": identifier,
                        "observation": json.loads(observed.stdout),
                    }
                )
            return None

    control = start(snapshot(FIXTURES / "python-pass", "output-control", steps), "output-control")
    control_detail = terminal(control["runId"], "control")
    if control_detail is None:
        return steps.report()
    steps.record(
        "control.accepted",
        control_detail["run"]["state"] == "SUCCEEDED"
        and control_detail["verdict"]["verdict"] == "PASS",
        control_detail["run"]["state"],
        "SUCCEEDED with PASS",
    )
    marker = "gh" + "p_" + "q" * 20
    for fixture in ("python-secret-output", "python-secret-output-full"):
        created = start(snapshot(FIXTURES / fixture, fixture, steps), fixture)
        detail = terminal(created["runId"], fixture)
        if detail is None:
            return steps.report()
        assert_complete_evidence(steps, detail, "FAILED")
        steps.record(
            f"{fixture}.verdict_fail",
            detail["verdict"]["verdict"] == "FAIL",
            detail["verdict"]["verdict"],
            "FAIL",
        )
        steps.record(
            f"{fixture}.api_output_clean",
            marker not in json.dumps(detail),
            marker not in json.dumps(detail),
            True,
        )
        observed = compose(
            "exec",
            "-T",
            "api",
            "python",
            "-c",
            HISTORY_OUTPUT_OBSERVER,
            created["runId"],
            merge_stderr=False,
        )
        if not observed.ok:
            raise StackError("the bounded history/object observer failed; no payload is recorded")
        proof = json.loads(observed.stdout)
        steps.record(
            f"{fixture}.history_clean",
            proof.get("prohibitedBytesAbsent") is True,
            proof,
            "decoded durable payloads contain no prohibited bytes",
        )
        steps.record(
            f"{fixture}.no_sandbox_artifact",
            proof.get("sandboxObjects") == 0,
            proof.get("sandboxObjects"),
            0,
        )
        steps.record(
            f"{fixture}.causal_containment_refusal",
            proof.get("containmentRefusals", 0) > 0,
            proof.get("containmentRefusals"),
            "one or more explicit output-containment refusals",
        )
        steps.artifacts.append(
            {"kind": "quality-run", "runId": created["runId"], "planId": created["planId"]}
        )
    after = start(
        snapshot(FIXTURES / "python-pass", "after-output-refusal", steps), "after-output-refusal"
    )
    after_detail = terminal(after["runId"], "control.after_refusal")
    if after_detail is None:
        return steps.report()
    assert_complete_evidence(steps, after_detail, "SUCCEEDED")
    steps.record(
        "control.after_refusal_pass",
        after_detail["verdict"]["verdict"] == "PASS",
        after_detail["verdict"]["verdict"],
        "PASS",
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
    wait_check(created["runId"], "q002-unit", seconds=DURABLE_WAIT_SECONDS)
    restarted = compose("restart", "evaluator")
    steps.record("worker.restart_requested", restarted.ok, restarted.exit_code, 0)
    wait_for_health(["evaluator"], timeout=180)
    detail = wait_terminal(created["runId"], seconds=DURABLE_WAIT_SECONDS)
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
    wait_check(created["runId"], "q002-unit", seconds=DURABLE_WAIT_SECONDS)
    request("POST", f"/{created['runId']}/cancel")
    detail = wait_terminal(created["runId"], seconds=DURABLE_WAIT_SECONDS)
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


def quality_timeout_observation(run_id: str) -> dict[str, Any]:
    """Project only bounded closed states/counts, never source, output or exception bodies."""
    try:
        detail = request("GET", f"/{run_id}")
    except (StackError, OSError, ValueError):
        return {"observationStatus": "UNAVAILABLE", "state": "UNKNOWN"}
    malformed = {"observationStatus": "MALFORMED", "state": "UNKNOWN"}
    if type(detail) is not dict or type(detail.get("run")) is not dict:
        return malformed
    state = detail["run"].get("state")
    states = TERMINAL | {"CREATED", "PLANNED", "QUEUED", "RUNNING", "CANCELLING"}
    checks, results = detail.get("checks"), detail.get("results")
    if (
        type(state) is not str
        or state not in states
        or type(checks) is not list
        or type(results) is not list
        or len(checks) > 256
        or len(results) > 256
        or len(results) > len(checks)
        or any(type(row) is not dict or type(row.get("applicable")) is not bool for row in checks)
    ):
        return malformed
    statuses = {"PASSED", "FAILED", "DENIED", "TIMED_OUT", "CANCELLED", "ERROR", "NOT_APPLICABLE"}
    counts: dict[str, int] = {}
    for row in results:
        if type(row) is not dict:
            return malformed
        status = row.get("status")
        if type(status) is not str or status not in statuses:
            return malformed
        counts[status] = counts.get(status, 0) + 1
    return {
        "observationStatus": "AVAILABLE",
        "state": state,
        "declaredChecks": len(checks),
        "applicableChecks": sum(row["applicable"] for row in checks),
        "completedResults": len(results),
        "resultCounts": counts,
    }


def scenario_iacode() -> dict[str, Any]:
    steps = Steps("iacode")
    with tempfile.TemporaryDirectory(prefix="iacode-quality-self-") as directory:
        source = Path(directory) / "iacode"
        selection = materialize_committed_source(REPOSITORY_ROOT, source)
        steps.record(
            "snapshot.immutable_product_inputs_complete",
            selection["allCommittedNonCheckpointPathsPreserved"]
            and not selection["generalSnapshotLimitsChanged"],
            {
                key: selection[key]
                for key in (
                    "subjectCommit",
                    "subjectTree",
                    "selectedFiles",
                    "selectedBytes",
                    "excludedCheckpointFiles",
                    "excludedCheckpointBytes",
                )
            },
            "all immutable non-checkpoint inputs; checkpoint outputs separately validated; "
            "unchanged capacity",
        )
        steps.artifacts.append({"kind": "self-qualification-source", **selection})
        stored = snapshot(source, "iacode", steps)
        created = start(stored, "iacode")
        try:
            detail = wait_terminal(created["runId"], seconds=IACODE_WAIT_SECONDS)
        except StackError:
            observation = quality_timeout_observation(created["runId"])
            steps.record(
                "quality.terminal_observation_completed",
                False,
                observation["state"],
                "terminal facts within the bounded observation window",
            )
            steps.artifacts.append(
                {
                    "kind": "quality-run-observation-failure",
                    "runId": created["runId"],
                    "planId": created["planId"],
                    "observation": observation,
                }
            )
            return steps.report()
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
    "secret-output": scenario_secret_output,
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
