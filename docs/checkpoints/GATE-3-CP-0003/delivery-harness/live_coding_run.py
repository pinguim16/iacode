#!/usr/bin/env python3
"""M1-F-001 acceptance: the owner's configured model makes a valid tool request that runs in a sandbox.

Adapted from the M1 audit's `cross_gate_live.py` (GATE-3-CP-0002), with one difference that is the
point: the model is **only** the operator's configured one (IACODE_GATEWAY_SMOKE_MODEL). The audit
found that model unable to form a single tool request, because the runtime never showed it the
envelope's keys; after the correction the same model, unchanged, must make one.

Task -> Agent Runtime (API, Temporal, worker) -> Model Gateway -> provider -> TOOL_REQUEST ->
sandbox service -> disposable container -> tool result -> Agent Runtime -> next model call.

Nothing is scripted. The run is created over HTTP as the operational page creates one, with the
shipped `coding` team, over a minimal synthetic repository stored as a workspace snapshot. This
harness reads what the run, its events and its executions recorded, and a sentinel file on the host
proves nothing ran there.

PASS requires: the configured model and no other; at least one valid tool request
(`TOOL_REQUESTED`); at least one tool executed in a sandbox session (a process-level status, not a
policy denial); its result delivered back; and a model call after that result. Whether the model
also fixed the defect is recorded as an observation. With no usable credential the result is
BLOCKED, never FAIL and never PASS.

    python live_coding_run.py --report ../LIVE-CODING-RUN.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "iacode"))

from compose import published_port, read_env_file  # noqa: E402

CALC = "def add(a, b):\n    return a - b\n\n\ndef mul(a, b):\n    return a * b\n"
TEST_CALC = (
    "import unittest\n\nimport calc\n\n\n"
    "class CalcTests(unittest.TestCase):\n"
    "    def test_add(self):\n        self.assertEqual(calc.add(2, 3), 5)\n\n"
    "    def test_mul(self):\n        self.assertEqual(calc.mul(2, 3), 6)\n\n\n"
    "if __name__ == \"__main__\":\n    unittest.main()\n"
)
TASK = (
    "The repository in your workspace has a defect: calc.add returns the wrong value and the test "
    "test_calc.CalcTests.test_add fails. Run the tests with `python3 -m unittest -v test_calc`, "
    "fix calc.py with the smallest change, run the tests again to confirm they pass, and commit "
    "the fix with the message 'fix(calc): add returns the sum'. Work only inside the workspace."
)
TERMINAL = ("SUCCEEDED", "FAILED", "CANCELLED")
RUN_TIMEOUT_SECONDS = 1200


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def request_json(url: str, payload: dict | None = None, timeout: float = 30) -> tuple[int, dict]:
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    request = urllib.request.Request(url, data=data, method="POST" if payload is not None else "GET",
                                     headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", "replace")
        try:
            return error.code, json.loads(body)
        except json.JSONDecodeError:
            return error.code, {"raw": body[:500]}


def snapshot(source: Path, name: str) -> dict:
    completed = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "iacode" / "sandbox_snapshot.py"),
         "--source", str(source), "--name", name],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=600, check=False)
    lines = [line for line in completed.stdout.splitlines() if line.strip().startswith("{")]
    if completed.returncode != 0 or not lines:
        raise SystemExit(f"snapshot failed: {completed.stdout[-800:]} {completed.stderr[-800:]}")
    return json.loads(lines[-1])


def sandbox_containers(run_id: str) -> list[str]:
    completed = subprocess.run(
        ["docker", "ps", "-a", "--filter", f"label=org.iacode.sandbox.run={run_id}",
         "--format", "{{.Names}}"],
        capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
    return [line for line in completed.stdout.splitlines() if line.strip()]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path, required=True)
    arguments = parser.parse_args()

    env = read_env_file()
    configured = (env.get("IACODE_GATEWAY_SMOKE_MODEL") or "").strip()
    # The configured model and no other: this is the model the audit found unable to make a tool
    # request, and substituting a stronger one would prove nothing about the correction.
    model = configured
    base = f"http://127.0.0.1:{published_port('api', 8000)}"
    report: dict = {"schemaVersion": "1.0.0", "artifact": "LIVE-CODING-RUN",
                    "finding": "M1-F-001", "checkpoint": CHECKPOINT.name, "startedAt": now(),
                    "model": model, "configuredModel": configured,
                    "modelChosenExplicitly": False, "team": "coding", "checks": []}

    def check(name: str, ok: bool, detail: str) -> None:
        report["checks"].append({"name": name, "ok": bool(ok), "detail": detail})
        print(f"[{'PASS' if ok else 'FAIL'}] {name}: {detail}", flush=True)

    if not model or ":" not in model:
        report["result"] = "BLOCKED"
        report["reason"] = "IACODE_GATEWAY_SMOKE_MODEL is not configured as provider:model"
        arguments.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print("LIVE_CODING_RUN=BLOCKED")
        return 2

    with tempfile.TemporaryDirectory(prefix="iacode-m1-live-") as scratch:
        workdir = Path(scratch)
        repository = workdir / "repository"
        repository.mkdir()
        (repository / "calc.py").write_text(CALC, encoding="utf-8", newline="\n")
        (repository / "test_calc.py").write_text(TEST_CALC, encoding="utf-8", newline="\n")
        sentinel = workdir / "host-sentinel.txt"
        sentinel.write_text("untouched\n", encoding="utf-8")
        sentinel_before = hashlib.sha256(sentinel.read_bytes()).hexdigest()

        # The catalog is the operator's to synchronise (the gateway smoke does the same): a fresh
        # installation starts with an empty one, and the run below names its model explicitly.
        provider = model.split(":", 1)[0]
        sync_status, synced = request_json(f"{base}/api/v1/gateway/models/sync",
                                           {"provider": provider}, timeout=180)
        outcome = next((item for item in synced.get("outcomes") or []
                        if item.get("provider") == provider), {})
        check("catalog synchronised", sync_status == 200 and not outcome.get("errors"),
              f"HTTP {sync_status}; added {outcome.get('added')}, updated "
              f"{outcome.get('updated')}, unchanged {outcome.get('unchanged')}")
        if sync_status != 200 or outcome.get("errors"):
            # The provider refused or could not be reached with the configured credential. That
            # is an operational blocker the owner resolves outside the repository (R-G2-009),
            # never a verdict about the correction.
            report["result"] = "BLOCKED"
            report["reason"] = ("the configured provider could not be reached with the configured "
                                "credential; the catalog synchronisation failed")
            arguments.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
            print("LIVE_CODING_RUN=BLOCKED")
            return 2

        stored = snapshot(repository, f"m1-f-001-live-{int(time.time())}")
        report["snapshot"] = {"artifactId": stored["artifactId"], "sha256": stored["sha256"]}
        check("snapshot", bool(stored.get("artifactId")),
              f"workspace snapshot {stored.get('artifactId')} stored")

        status, created = request_json(f"{base}/api/v1/agent-runs", {
            "task": TASK + f" Do not read or write {sentinel}.",
            "title": "M1-F-001 live coding run, configured model",
            "team": "coding", "model": model, "workspaceSnapshot": stored["artifactId"],
            "maxTurns": 12, "maxModelCalls": 36, "maxDurationSeconds": 1080,
            "metadata": {"origin": "gate-3-cp-0003-m1-f-001"}})
        check("run created", status in (200, 201, 202) and bool(created.get("runId")),
              f"HTTP {status} runId={created.get('runId')}")
        if not created.get("runId"):
            report["result"] = "FAIL"
            report["created"] = created
            arguments.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
            return 1
        run_id = created["runId"]
        report["runId"] = run_id

        deadline = time.monotonic() + RUN_TIMEOUT_SECONDS
        detail: dict = {}
        live_containers: set[str] = set()
        while time.monotonic() < deadline:
            _status, detail = request_json(f"{base}/api/v1/agent-runs/{run_id}")
            live_containers.update(sandbox_containers(run_id))
            if detail.get("state") in TERMINAL:
                break
            time.sleep(3)
        report["finalState"] = detail.get("state")
        check("run terminal", detail.get("state") in TERMINAL,
              f"state={detail.get('state')} error={detail.get('errorType')}")

        _status, events = request_json(f"{base}/api/v1/agent-runs/{run_id}/events?limit=1000")
        ordered = events.get("events") or []
        types = [event.get("type") for event in ordered]
        summary = detail.get("summary") or {}
        executions = detail.get("toolExecutions") or []
        requests = detail.get("toolRequests") or []

        report["summary"] = summary
        report["stages"] = [{key: stage.get(key) for key in ("name", "agent", "state", "turns",
                                                              "modelCalls")}
                            for stage in detail.get("stages") or []]
        report["toolExecutions"] = executions
        report["toolRequests"] = [{key: item.get(key) for key in (
            "toolRequestId", "name", "status", "resultStatus")} for item in requests]
        report["eventTypes"] = types
        report["sandboxContainersSeen"] = sorted(live_containers)

        model_calls = int(summary.get("modelCalls") or 0)
        check("model calls through the gateway", model_calls >= 1,
              f"{model_calls} model call(s) recorded; the runtime's only model path is the "
              f"gateway's /api/v1/gateway/infer")
        check("the configured model made a valid tool request",
              "TOOL_REQUESTED" in types and len(requests) >= 1,
              f"{types.count('TOOL_REQUESTED')} TOOL_REQUESTED event(s), {len(requests)} "
              f"tool request(s) persisted")
        executed = [item for item in executions if item.get("sandboxSession")
                    and item.get("status") in ("SUCCEEDED", "FAILED", "TIMED_OUT")]
        check("at least one tool executed in a sandbox", len(executed) >= 1,
              f"{len(executed)} execution(s) with a process in sandbox session(s) "
              f"{sorted({item.get('sandboxSession') for item in executed})}: "
              f"{[(item.get('tool'), item.get('status')) for item in executed][:8]}")
        resolved = [item for item in requests if item.get("status") == "RESOLVED"]
        check("tool results delivered to the runtime", len(resolved) >= 1,
              f"{len(resolved)} of {len(requests)} tool request(s) RESOLVED")
        crossing = False
        seen_result = False
        for event_type in types:
            if event_type == "TOOL_RESULT_RECEIVED":
                seen_result = True
            elif event_type == "MODEL_CALL_STARTED" and seen_result:
                crossing = True
                break
        check("the runtime called the model again after a sandbox result", crossing,
              "a MODEL_CALL_STARTED event follows a TOOL_RESULT_RECEIVED event")
        check("sandbox containers existed during the run", bool(live_containers),
              f"{len(live_containers)} container(s) labelled with the run were observed")
        remaining = sandbox_containers(run_id)
        check("no sandbox container outlives the run", not remaining,
              f"{len(remaining)} container(s) remain labelled with the run")
        sentinel_after = hashlib.sha256(sentinel.read_bytes()).hexdigest()
        check("host sentinel untouched", sentinel_before == sentinel_after,
              "the file on the host is byte-identical after the run")
        tools = [item.get("tool") for item in executions]
        notes = [event for event in ordered if event.get("type") == "RUN_NOTE"]
        report["observations"] = {
            "finalState": detail.get("state"),
            "errorType": detail.get("errorType"),
            "repairAttempts": len(notes),
            "repairReasons": [str((event.get("payload") or {}).get("reason"))[:200]
                              for event in notes],
            "deniedExecutions": [(item.get("tool"), item.get("errorCode"))
                                 for item in executions if item.get("status") == "DENIED"],
            "toolsExecuted": tools,
            "testsRun": any("shell" in str(tool) for tool in tools),
            "committed": "git.commit" in tools,
            "result": (detail.get("resultSummary") or "")[:400],
        }

    report["finishedAt"] = now()
    failed = [item for item in report["checks"] if not item["ok"]]
    report["result"] = "PASS" if not failed else "FAIL"
    arguments.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n",
                                encoding="utf-8", newline="\n")
    print(f"LIVE_CODING_RUN={report['result']} checks={len(report['checks']) - len(failed)}/"
          f"{len(report['checks'])} run={report.get('runId')} model={model}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
