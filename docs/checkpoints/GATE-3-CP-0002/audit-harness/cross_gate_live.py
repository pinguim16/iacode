#!/usr/bin/env python3
"""M1 criterion 10: one live run crosses every Gate of the milestone, read from what it recorded.

Task -> Agent Runtime (API, Temporal, worker) -> Model Gateway -> provider -> TOOL_REQUEST ->
sandbox service -> disposable container -> tool result -> Agent Runtime -> next model call.

Nothing is scripted here. The run is created over HTTP exactly as the operational page creates one,
with the shipped `coding` team, over a synthetic repository stored as a workspace snapshot, and the
model is the one the operator configured for live checks (IACODE_GATEWAY_SMOKE_MODEL). The model
decides which tools to ask for; this harness only reads what the run, its events and its tool
executions recorded, and a sentinel file on the host proves nothing it asked for ran there.

What PASS requires is the crossing, not the model's skill: at least one model call through the
gateway, at least one tool request executed in a sandbox session, its result delivered back to
the runtime, and a model call after that result. Whether the model also fixed the defect is
recorded as an observation, never as the verdict.

    python cross_gate_live.py --report ../CROSS-GATE-LIVE.json
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
    parser.add_argument("--model", default=None,
                        help="an explicit provider:model; the default is the operator's "
                             "IACODE_GATEWAY_SMOKE_MODEL, and any other is recorded as a choice")
    arguments = parser.parse_args()

    env = read_env_file()
    configured = (env.get("IACODE_GATEWAY_SMOKE_MODEL") or "").strip()
    model = (arguments.model or configured).strip()
    base = f"http://127.0.0.1:{published_port('api', 8000)}"
    report: dict = {"schemaVersion": "1.0.0", "artifact": "CROSS-GATE-LIVE",
                    "checkpoint": CHECKPOINT.name, "startedAt": now(), "model": model,
                    "configuredModel": configured, "modelChosenExplicitly": model != configured,
                    "team": "coding", "checks": []}

    def check(name: str, ok: bool, detail: str) -> None:
        report["checks"].append({"name": name, "ok": bool(ok), "detail": detail})
        print(f"[{'PASS' if ok else 'FAIL'}] {name}: {detail}", flush=True)

    if not model or ":" not in model:
        report["result"] = "BLOCKED"
        report["reason"] = "IACODE_GATEWAY_SMOKE_MODEL is not configured as provider:model"
        arguments.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print("CROSS_GATE_LIVE=BLOCKED")
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

        stored = snapshot(repository, f"m1-audit-live-{int(time.time())}")
        report["snapshot"] = {"artifactId": stored["artifactId"], "sha256": stored["sha256"]}
        check("snapshot", bool(stored.get("artifactId")),
              f"workspace snapshot {stored.get('artifactId')} stored")

        status, created = request_json(f"{base}/api/v1/agent-runs", {
            "task": TASK + f" Do not read or write {sentinel}.",
            "title": "M1 audit cross-gate live run",
            "team": "coding", "model": model, "workspaceSnapshot": stored["artifactId"],
            "maxTurns": 12, "maxModelCalls": 36, "maxDurationSeconds": 1080,
            "metadata": {"origin": "m1-fresh-session-audit"}})
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
        sandboxed = [item for item in executions if item.get("sandboxSession")]
        check("tool requests executed in a sandbox", len(sandboxed) >= 1,
              f"{len(sandboxed)} execution(s) in sandbox session(s) "
              f"{sorted({item.get('sandboxSession') for item in sandboxed})}")
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
        report["observations"] = {
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
    print(f"CROSS_GATE_LIVE={report['result']} checks={len(report['checks']) - len(failed)}/"
          f"{len(report['checks'])} run={report.get('runId')}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
