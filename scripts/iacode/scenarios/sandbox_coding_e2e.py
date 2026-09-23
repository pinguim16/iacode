#!/usr/bin/env python3
"""The sandbox scenarios: a coding team changes a repository, and nothing reaches the host.

`docs/GATE-3-CHECKLIST.md` sections 17 and 24. One harness, four scenarios, each a verification
stage of its own:

``coding``    a synthetic repository with a defective function and a failing test is stored as a
              snapshot; a coding run reads the code, runs the red test, patches, runs the green
              test, probes where it is running, reads the diff, commits, and is reviewed. A sentinel
              file on the host is the proof that the shell it used was not the host's.
``timeout``   a command that outlives its timeout is stopped; the agent receives a normalised
              failure and the run carries on to its end instead of waiting for ever.
``cancel``    a run is cancelled while its sandbox is running a long command; the command stops,
              the run ends cancelled, and the sandbox is gone.
``recovery``  the sandbox service is restarted between two tools of a run; the restarted service
              keeps the run's live session, and the second tool sees what the first one wrote.
``forged-result``
              `M1-F-002`, the fresh-session audit's null control and mutation. The control is the
              ``timeout`` run: the agent receives the sandbox's TIMED_OUT and answers TIMEOUT-SEEN.
              The mutation is the same run with a SUCCEEDED result posted to the API's tool-result
              endpoint while the sandbox executes the command: it is refused, the stored result is
              the sandbox's TIMED_OUT, and the agent still answers TIMEOUT-SEEN. A second forgery
              after the run ended is refused the same way.

Everything is real except the model: the run is created by the Agent Runtime's own service, the
workflow and its persistence activities are the real ones, the sandbox service is the stack's, and
the sandboxes are containers on the real engine. Every assertion reads what the run **recorded** —
states, executions, results, sessions, events — never what the harness sent.

Both images this depends on are rebuilt first (`LSN-0036`), and the stack's sandbox service is
brought up to date with them, so the scenario never measures an image built from older source.

    python scripts/iacode/scenarios/sandbox_coding_e2e.py --scenario coding
    python scripts/iacode/scenarios/sandbox_coding_e2e.py --scenario cancel --report var/cancel.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import secrets
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from compose import (
    COMPOSE_DIRECTORY,
    COMPOSE_FILE,
    ENV_FILE,
    REPOSITORY_ROOT,
    StackError,
    build_service,
    compose,
    log,
    main_guard,
    published_port,
    read_env_file,
    wait_for_health,
)
from sandbox_snapshot import create as create_snapshot

CONTAINER = "iacode-coding-rehearsal"
HARNESS = "/app/rehearsal/coding.py"
SANDBOX_QUEUE = "iacode-sandbox"

WAIT_SECONDS = 300
POLL_SECONDS = 2.0

CALC = "def add(a, b):\n    return a - b\n\n\ndef mul(a, b):\n    return a * b\n"
TEST_CALC = (
    "import unittest\n\nimport calc\n\n\n"
    "class CalcTests(unittest.TestCase):\n"
    "    def test_add(self):\n        self.assertEqual(calc.add(2, 3), 5)\n\n"
    "    def test_mul(self):\n        self.assertEqual(calc.mul(2, 3), 6)\n\n\n"
    "if __name__ == \"__main__\":\n    unittest.main()\n"
)
EXPECTED_DEVELOPER_TOOLS = [
    "filesystem.read", "shell.exec", "filesystem.apply_patch", "shell.exec", "shell.exec",
    "git.diff", "git.add", "git.commit",
]


def docker(*arguments: str, timeout: float = 300) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["docker", *arguments], text=True, encoding="utf-8",
                          errors="replace", capture_output=True, timeout=timeout, check=False)


def harness(*arguments: str) -> dict[str, Any]:
    """One harness subcommand inside the rehearsal container, as parsed JSON."""
    completed = docker("exec", CONTAINER, "python", HARNESS, *arguments)
    if completed.returncode != 0:
        raise StackError(
            f"the harness command {' '.join(arguments)} failed:\n{completed.stderr[-1200:]}")
    line = completed.stdout.strip().splitlines()[-1] if completed.stdout.strip() else ""
    try:
        return json.loads(line)
    except json.JSONDecodeError as error:
        raise StackError(f"the harness answered something that is not JSON: {line[:300]}") \
            from error


def wait_for(description: str, probe, seconds: float = WAIT_SECONDS) -> Any:
    """Poll ``probe`` until it returns something truthy, with a bound (`LSN-0049`)."""
    deadline = time.monotonic() + seconds
    last: Any = None
    while time.monotonic() < deadline:
        last = probe()
        if last:
            return last
        time.sleep(POLL_SECONDS)
    raise StackError(f"{description} did not happen within {seconds:.0f}s (last: {last!r})")


def pollers(queue: str) -> int:
    try:
        return int(harness("poller", "--queue", queue).get("pollers") or 0)
    except StackError:
        return 0


def prepare_images() -> None:
    """Rebuild what the scenario runs, and bring the stack's sandbox service up to date."""
    build_service("worker")
    build_service("sandbox")
    images = subprocess.run([sys.executable,
                             str(REPOSITORY_ROOT / "scripts" / "iacode" / "sandbox_image.py")],
                            check=False)
    if images.returncode != 0:
        raise StackError("the sandbox image could not be built")
    started = compose("up", "-d", "--no-deps", "sandbox", capture=True)
    if not started.ok:
        raise StackError(f"the sandbox service would not start:\n{started.output[-1200:]}")
    wait_for_health(["sandbox"], timeout=300)


def start_rehearsal() -> None:
    docker("rm", "-f", CONTAINER)
    completed = subprocess.run(
        ["docker", "compose", "--project-directory", str(COMPOSE_DIRECTORY),
         "--file", str(COMPOSE_FILE), "--env-file", str(ENV_FILE),
         "run", "-d", "--no-deps", "--name", CONTAINER, "--entrypoint", "", "worker",
         "python", HARNESS, "worker"],
        text=True, encoding="utf-8", errors="replace",
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    if completed.returncode != 0:
        raise StackError(f"the rehearsal worker would not start:\n{completed.stdout[-800:]}")
    wait_for("a poller on the rehearsal queue", lambda: pollers(
        "iacode-agent-runtime-coding-rehearsal") > 0)
    wait_for("a poller on the sandbox queue", lambda: pollers(SANDBOX_QUEUE) > 0)


def synthetic_snapshot(workdir: Path) -> str:
    source = workdir / "synthetic-calc"
    source.mkdir()
    (source / "calc.py").write_text(CALC, encoding="utf-8", newline="\n")
    (source / "test_calc.py").write_text(TEST_CALC, encoding="utf-8", newline="\n")
    (source / "README.md").write_text("A synthetic repository with one defect.\n",
                                      encoding="utf-8", newline="\n")
    stored = create_snapshot(source, f"synthetic-calc-{secrets.token_hex(4)}")
    if "artifactId" not in stored:
        raise StackError(f"the snapshot was not stored: {stored}")
    return str(stored["artifactId"])


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def container_exists(name: str) -> bool:
    return docker("inspect", "--format", "{{.State.Status}}", name).returncode == 0


def wait_for_end(run_id: str) -> dict[str, Any]:
    return wait_for("the run's terminal state", lambda: (
        body if (body := harness("state", "--run", run_id)).get("state")
        in ("SUCCEEDED", "FAILED", "CANCELLED") else None))


def by_stage(report: dict[str, Any], stage: str) -> list[dict[str, Any]]:
    return [item for item in report["executions"] if item["stage"] == stage]


def text_of(execution: dict[str, Any]) -> str:
    output = execution.get("resultOutput") or {}
    return "\n".join(str(output.get(key) or "") for key in ("stdout", "stderr", "content"))


class Steps:
    def __init__(self) -> None:
        self.steps: list[dict[str, str]] = []

    def record(self, name: str, ok: bool, detail: str) -> bool:
        self.steps.append({"step": name, "result": "PASS" if ok else "FAIL",
                           "detail": detail[:400]})
        log(f"[{'PASS' if ok else 'FAIL'}] {name:44} {detail[:160]}")
        return ok

    @property
    def failed(self) -> list[dict[str, str]]:
        return [step for step in self.steps if step["result"] == "FAIL"]


def common_checks(steps: Steps, report: dict[str, Any], expected_state: str) -> None:
    steps.record("run.terminal_state", report["state"] == expected_state,
                 f"state {report['state']} ({report.get('errorType')}: "
                 f"{report.get('errorSummary')})")
    sessions = report["sandboxes"]
    steps.record("sandbox.one_session_for_the_run", len(sessions) == 1,
                 f"{len(sessions)} session(s)")
    executed = [item for item in report["executions"] if item["executionStatus"]]
    session_ids = {item["sandboxSession"] for item in executed}
    steps.record("sandbox.every_execution_in_that_session",
                 bool(sessions) and session_ids == {sessions[0]["sessionId"]},
                 f"sessions used: {sorted(str(item) for item in session_ids)}")
    steps.record("sandbox.no_network", all(item["networkProfile"] == "none"
                                           for item in sessions), "network profile none")
    if sessions:
        steps.record("sandbox.released_with_the_run",
                     sessions[0]["state"] == "STOPPED"
                     and not container_exists(sessions[0]["containerName"]),
                     f"session {sessions[0]['state']}, container "
                     f"{'present' if container_exists(sessions[0]['containerName']) else 'gone'}")
    events = report["events"]
    steps.record("history.tool_requests_answered",
                 events.count("TOOL_REQUESTED") >= len(executed),
                 f"{events.count('TOOL_REQUESTED')} requested, {len(executed)} executed")


def scenario_coding(steps: Steps, snapshot: str, workdir: Path) -> None:
    sentinel_directory = workdir / "host-sentinel"
    sentinel_directory.mkdir()
    sentinel = sentinel_directory / "sentinel.txt"
    sentinel.write_text(f"host sentinel {secrets.token_hex(16)}\n", encoding="utf-8")
    before = digest(sentinel)

    created = harness("create", "--snapshot", snapshot, "--scenario", "coding",
                      "--sentinel", str(sentinel))
    run_id = created["runId"]
    steps.record("run.created_over_the_snapshot",
                 created["workspace"].get("artifactId") == snapshot,
                 f"run {run_id}, policies {created['policies']}")
    wait_for_end(run_id)
    report = harness("report", "--run", run_id)
    common_checks(steps, report, "SUCCEEDED")

    stages = [(item["name"], item["agent"], item["status"]) for item in report["stages"]]
    steps.record("team.planner_developer_reviewer",
                 [item[1] for item in stages] == ["planner", "developer", "code-reviewer"]
                 and all(item[2] == "SUCCEEDED" for item in stages), str(stages))
    steps.record("planner.executed_nothing", not by_stage(report, "plan"), "no tool requested")

    developer = by_stage(report, "develop")
    steps.record("developer.tool_sequence",
                 [item["tool"] for item in developer] == EXPECTED_DEVELOPER_TOOLS,
                 ", ".join(item["tool"] for item in developer))
    if len(developer) != len(EXPECTED_DEVELOPER_TOOLS):
        return
    read, red, patch, green, probe, diff, add, commit = developer
    steps.record("read.returned_the_defect", "return a - b" in text_of(read),
                 f"{read['executionStatus']}")
    steps.record("tests.red_before_the_fix",
                 red["exitCode"] not in (None, 0) and "FAILED (failures=1)" in text_of(red),
                 f"exit {red['exitCode']}")
    steps.record("patch.applied", patch["executionStatus"] == "SUCCEEDED",
                 str(patch["resultOutput"])[:200])
    steps.record("tests.green_after_the_fix",
                 green["exitCode"] == 0 and "OK" in text_of(green), f"exit {green['exitCode']}")
    probe_text = text_of(probe)
    steps.record("shell.ran_unprivileged_in_the_sandbox",
                 "UID=10001" in probe_text and "sandbox_helper" in probe_text,
                 " ".join(line for line in probe_text.splitlines()
                          if line.startswith(("UID=", "PID1="))))
    steps.record("shell.saw_no_engine_socket", "SOCKET=ABSENT" in probe_text, "no docker.sock")
    steps.record("shell.host_drive_not_mounted",
                 all(f"WRITE-{index}=REFUSED" in probe_text for index in (1, 2, 3)),
                 " ".join(line for line in probe_text.splitlines() if line.startswith("WRITE-")))
    steps.record("host.sentinel_unchanged", digest(sentinel) == before,
                 "the host file has the digest it had before the run")
    steps.record("host.no_file_appeared",
                 sorted(path.name for path in sentinel_directory.iterdir()) == ["sentinel.txt"],
                 "the host directory holds only the sentinel")
    diff_text = text_of(diff)
    steps.record("diff.shows_the_fix",
                 "-    return a - b" in diff_text and "+    return a + b" in diff_text,
                 f"{len(diff_text)} characters of diff")
    steps.record("git.committed_locally",
                 add["exitCode"] == 0 and commit["exitCode"] == 0, f"commit exit "
                 f"{commit['exitCode']}")

    reviewer = by_stage(report, "review")
    steps.record("reviewer.read_only_inspection",
                 [item["tool"] for item in reviewer] == ["git.show"], str(
                     [item["tool"] for item in reviewer]))
    shown = text_of(reviewer[0]) if reviewer else ""
    steps.record("commit.carries_the_sandbox_identity",
                 "IACode Agent" in shown and "fix(calc)" in shown,
                 "the commit's author is the sandbox's identity, not a person")
    steps.record("review.approved_what_it_saw", report["result"] == "APPROVED",
                 f"result {report['result']}")


def scenario_timeout(steps: Steps, snapshot: str) -> None:
    run_id = harness("create", "--snapshot", snapshot, "--scenario", "timeout")["runId"]
    wait_for_end(run_id)
    report = harness("report", "--run", run_id)
    common_checks(steps, report, "SUCCEEDED")
    developer = by_stage(report, "develop")
    execution = developer[0] if developer else {}
    steps.record("timeout.execution_timed_out",
                 execution.get("executionStatus") == "TIMED_OUT" and execution.get("timedOut"),
                 f"{execution.get('executionStatus')} after {execution.get('durationMs')} ms")
    steps.record("timeout.stopped_at_its_bound",
                 (execution.get("durationMs") or 10 ** 9) < 20000,
                 f"{execution.get('durationMs')} ms against a 3 s timeout and a 60 s command")
    steps.record("timeout.agent_received_a_normalised_failure",
                 execution.get("resultStatus") == "TIMED_OUT"
                 and (execution.get("resultOutput") or {}).get("timedOut") is True,
                 f"result {execution.get('resultStatus')}")
    change = next((item["output"] for item in report["stages"] if item["name"] == "develop"), "")
    steps.record("timeout.run_carried_on", change == "TIMEOUT-SEEN", f"developer said {change}")


def scenario_cancel(steps: Steps, snapshot: str) -> None:
    run_id = harness("create", "--snapshot", snapshot, "--scenario", "cancel")["runId"]
    running = wait_for("the sandbox running the long command", lambda: (
        body if "RUNNING" in (body := harness("state", "--run", run_id))["sandboxStates"]
        else None))
    steps.record("cancel.command_was_running", True, f"sandbox {running['sandboxStates']}")
    report_before = harness("report", "--run", run_id)
    container = report_before["sandboxes"][0]["containerName"]
    processes = docker("top", container)
    steps.record("cancel.long_command_in_the_container", "sleep 600" in processes.stdout,
                 "the command is a process of the sandbox container")

    harness("cancel", "--run", run_id)
    wait_for_end(run_id)
    report = harness("report", "--run", run_id)
    common_checks(steps, report, "CANCELLED")
    execution = next(iter(by_stage(report, "develop")), {})
    steps.record("cancel.execution_recorded_as_cancelled",
                 execution.get("executionStatus") == "CANCELLED",
                 f"execution {execution.get('executionStatus')}")
    steps.record("cancel.request_closed", execution.get("requestStatus") != "PENDING",
                 f"request {execution.get('requestStatus')}")
    events = report["events"]
    steps.record("cancel.is_the_last_event", bool(events) and events[-1] == "RUN_CANCELLED",
                 ", ".join(events[-3:]))


def scenario_recovery(steps: Steps, snapshot: str) -> None:
    run_id = harness("create", "--snapshot", snapshot, "--scenario", "recovery")["runId"]
    wait_for("the model holding its second turn",
             lambda: harness("held", "--run", run_id).get("held"))
    before = harness("report", "--run", run_id)
    session_before = before["sandboxes"][0] if before["sandboxes"] else {}
    steps.record("recovery.first_tool_executed",
                 [item["executionStatus"] for item in before["executions"]] == ["SUCCEEDED"],
                 str([item["tool"] for item in before["executions"]]))

    name = f"{read_env_file().get('COMPOSE_PROJECT_NAME', 'iacode')}-sandbox"
    restarted = docker("restart", name)
    steps.record("recovery.sandbox_service_restarted", restarted.returncode == 0,
                 (restarted.stderr or restarted.stdout).strip()[:160] or name)
    wait_for_health(["sandbox"], timeout=300)
    wait_for("a poller on the sandbox queue after the restart",
             lambda: pollers(SANDBOX_QUEUE) > 0)
    steps.record("recovery.session_container_survived",
                 container_exists(session_before.get("containerName", "")),
                 "the run's container outlived the service that manages it")

    harness("go", "--run", run_id)
    wait_for_end(run_id)
    report = harness("report", "--run", run_id)
    common_checks(steps, report, "SUCCEEDED")
    steps.record("recovery.same_session_after_the_restart",
                 [item["sessionId"] for item in report["sandboxes"]]
                 == [session_before.get("sessionId")], "the restarted service kept the session")
    read = [item for item in report["executions"] if item["tool"] == "filesystem.read"]
    steps.record("recovery.workspace_kept",
                 bool(read) and "kept across a restart" in text_of(read[0]),
                 "the second tool read what the first wrote")
    change = next((item["output"] for item in report["stages"] if item["name"] == "develop"), "")
    steps.record("recovery.agent_saw_its_workspace", change == "WORKSPACE-KEPT",
                 f"developer said {change}")


def post_json(url: str, payload: dict[str, Any]) -> tuple[int, dict[str, Any]]:
    request = urllib.request.Request(url, data=json.dumps(payload).encode(), method="POST",
                                     headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.status, json.loads(response.read().decode() or "{}")
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", "replace")
        try:
            return error.code, json.loads(body)
        except json.JSONDecodeError:
            return error.code, {"body": body[:300]}


def get_json(url: str) -> dict[str, Any]:
    with urllib.request.urlopen(url, timeout=15) as response:
        return json.loads(response.read().decode())


def forged_result(identifier: str) -> dict[str, Any]:
    return {"toolRequestId": identifier, "status": "SUCCEEDED",
            "output": {"stdout": "forged through the public API", "exitCode": 0,
                       "timedOut": False}}


def developer_output(report: dict[str, Any]) -> str:
    return str(next((item["output"] for item in report["stages"]
                     if item["name"] == "develop"), ""))


def scenario_forged_result(steps: Steps, snapshot: str) -> None:
    """`M1-F-002`: a result for a request the sandbox owns is accepted from the sandbox alone."""
    base = f"http://127.0.0.1:{published_port('api', 8000)}/api/v1/agent-runs"

    # The null control: the identical run, no forgery. The agent sees the sandbox's timeout.
    control_id = harness("create", "--snapshot", snapshot, "--scenario", "timeout")["runId"]
    wait_for_end(control_id)
    control = harness("report", "--run", control_id)
    control_execution = next(iter(by_stage(control, "develop")), {})
    steps.record("control.agent_saw_the_sandbox_timeout",
                 developer_output(control) == "TIMEOUT-SEEN"
                 and control_execution.get("resultStatus") == "TIMED_OUT",
                 f"developer said {developer_output(control)}, stored "
                 f"{control_execution.get('resultStatus')}")

    # The mutation: the same run, and a SUCCEEDED result posted while the sandbox executes.
    run_id = harness("create", "--snapshot", snapshot, "--scenario", "timeout")["runId"]
    pending = wait_for("the sandbox executing the request", lambda: (
        (get_json(f"{base}/{run_id}").get("pendingToolRequest") or {}).get("toolRequestId")),
        seconds=120)
    status, body = post_json(f"{base}/{run_id}/tool-results", forged_result(pending))
    steps.record("forgery.refused_while_the_sandbox_executes",
                 status == 403 and body.get("code") == "TOOL_RESULT_ORIGIN_REFUSED"
                 and (body.get("details") or {}).get("executor") == "SANDBOX",
                 f"HTTP {status} {body.get('code')} {(body.get('details') or {})}")

    wait_for_end(run_id)
    report = harness("report", "--run", run_id)
    common_checks(steps, report, "SUCCEEDED")
    execution = next(iter(by_stage(report, "develop")), {})
    steps.record("forgery.stored_result_is_the_sandbox_result",
                 execution.get("resultStatus") == "TIMED_OUT"
                 and execution.get("executionStatus") == "TIMED_OUT"
                 and (execution.get("resultOutput") or {}).get("timedOut") is True,
                 f"stored {execution.get('resultStatus')}, executed "
                 f"{execution.get('executionStatus')}")
    steps.record("forgery.agent_saw_the_sandbox_timeout",
                 developer_output(report) == "TIMEOUT-SEEN",
                 f"developer said {developer_output(report)}")

    late_status, late = post_json(f"{base}/{run_id}/tool-results", forged_result(pending))
    steps.record("forgery.refused_after_the_run_ended",
                 late_status == 403 and late.get("code") == "TOOL_RESULT_ORIGIN_REFUSED",
                 f"HTTP {late_status} {late.get('code')}")
    after = harness("report", "--run", run_id)
    steps.record("forgery.nothing_changed_after_the_refusals",
                 next(iter(by_stage(after, "develop")), {}).get("resultStatus") == "TIMED_OUT",
                 "the stored result is still the sandbox's")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--scenario",
                        choices=("coding", "timeout", "cancel", "recovery", "forged-result"),
                        required=True)
    parser.add_argument("--report", type=Path, default=None)
    arguments = parser.parse_args()

    steps = Steps()
    try:
        prepare_images()
        steps.record("images.rebuilt_and_service_current", True,
                     "worker, sandbox service and sandbox image built from the current source")
        start_rehearsal()
        steps.record("rehearsal.worker_polling", True, f"{CONTAINER} and the sandbox service")
        with tempfile.TemporaryDirectory(prefix="iacode-sandbox-e2e-") as directory:
            workdir = Path(directory)
            snapshot = synthetic_snapshot(workdir)
            steps.record("snapshot.stored", True, f"artifact {snapshot}")
            if arguments.scenario == "coding":
                scenario_coding(steps, snapshot, workdir)
            elif arguments.scenario == "timeout":
                scenario_timeout(steps, snapshot)
            elif arguments.scenario == "cancel":
                scenario_cancel(steps, snapshot)
            elif arguments.scenario == "forged-result":
                scenario_forged_result(steps, snapshot)
            else:
                scenario_recovery(steps, snapshot)
    except StackError as error:
        steps.record("scenario.completed", False, str(error))
    finally:
        docker("rm", "-f", CONTAINER)

    failed = steps.failed
    result = "PASS" if not failed else "FAIL"
    if arguments.report:
        arguments.report.parent.mkdir(parents=True, exist_ok=True)
        arguments.report.write_text(json.dumps({
            "scenario": arguments.scenario, "result": result, "steps": steps.steps,
        }, indent=2) + "\n", encoding="utf-8", newline="\n")
        log(f"wrote {arguments.report}")
    log(f"SANDBOX_{arguments.scenario.upper().replace('-', '_')}={result} "
        f"{len(steps.steps) - len(failed)}/{len(steps.steps)} steps")
    return 0 if not failed else 1


if __name__ == "__main__":
    main_guard(main)
