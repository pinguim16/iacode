#!/usr/bin/env python3
"""The durability scenario: a run waiting for a tool survives a real worker restart.

`docs/GATE-2-CHECKLIST.md` row 13.3, and the claim of this Gate that is easiest to assert and
hardest to prove. A run that pauses on a tool request holds its state in Temporal's history rather
than in a process, and the only way to show that is to kill the process and watch the run continue.

    create the run          -> the scripted agent asks for a tool
      -> the run reaches WAITING_FOR_TOOL
      -> the worker container is restarted, for real
      -> the tool result is delivered
      -> the run resumes and completes

Nothing is simulated. The workflow is the real one, Temporal is the stack's own server, and the
restart is ``docker restart`` on a container that is polling. The single substitution is the model,
which answers from a script — see `services/orchestrator/rehearsal/README.md` for why that is the
honest way to get an agent that asks for a tool in a Gate where no shipped profile may have one.

**No tool is executed at any point.** The result is supplied over the same store the API writes
through, which is what Gate 3's sandbox will do.

    python scripts/iacode/scenarios/agent_runtime_durability.py
    python scripts/iacode/scenarios/agent_runtime_durability.py --report var/agent-durability.json
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from compose import COMPOSE_DIRECTORY, COMPOSE_FILE, ENV_FILE, StackError, log, main_guard

CONTAINER = "iacode-durability-rehearsal"
HARNESS = "/app/rehearsal/durability.py"

WAIT_SECONDS = 120
POLL_SECONDS = 1.5


def docker(*arguments: str, timeout: float = 180) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["docker", *arguments], text=True, encoding="utf-8",
                          errors="replace", capture_output=True,
                          timeout=timeout, check=False)


def harness(*arguments: str) -> dict:
    """One harness subcommand inside the running rehearsal container, as parsed JSON.

    ``docker exec`` rather than ``docker compose run``: Compose narrates container lifecycle on
    stdout, so a value read that way arrives with "Container ... Created" in front of it.
    """
    completed = docker("exec", CONTAINER, "python", HARNESS, *arguments)
    if completed.returncode != 0:
        raise StackError(
            f"the harness command {' '.join(arguments)} failed:\n{completed.stderr[-800:]}")
    line = completed.stdout.strip().splitlines()[-1] if completed.stdout.strip() else ""
    try:
        return json.loads(line)
    except json.JSONDecodeError as error:
        raise StackError(
            f"the harness answered something that is not JSON: {line[:300]}") from error


def start_container() -> None:
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
    wait_for_poller()


def wait_for_poller() -> None:
    """Wait until Temporal sees a poller on the rehearsal queue.

    Asking the server rather than reading a log line: the worker prints that it started *before* it
    begins polling, so a scenario that waited for the line could start a run against a queue nobody
    was watching yet — and then wait out its whole timeout for a run that had not begun. A restart
    is only meaningful once the queue is being polled again.
    """
    deadline = time.monotonic() + WAIT_SECONDS
    last = "no answer yet"
    while time.monotonic() < deadline:
        completed = docker("exec", CONTAINER, "python", HARNESS, "poller")
        if completed.returncode == 0 and completed.stdout.strip():
            try:
                answer = json.loads(completed.stdout.strip().splitlines()[-1])
            except json.JSONDecodeError:
                answer = {}
            if int(answer.get("pollers") or 0) > 0:
                return
            last = f"{answer.get('pollers', 0)} poller(s)"
        else:
            last = (completed.stderr or completed.stdout).strip()[-160:] or "no answer"
        time.sleep(POLL_SECONDS)
    raise StackError(f"Temporal never saw a poller on the rehearsal queue: {last}")


def wait_for_state(run_id: str, *states: str) -> dict:
    deadline = time.monotonic() + WAIT_SECONDS
    body: dict = {}
    while time.monotonic() < deadline:
        body = harness("state", "--run", run_id)
        if body.get("state") in states:
            return body
        time.sleep(POLL_SECONDS)
    raise StackError(
        f"the run was {body.get('state')} after {WAIT_SECONDS}s, not one of {', '.join(states)}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--report", type=Path, default=None)
    arguments = parser.parse_args()

    steps: list[dict] = []

    def record(name: str, ok: bool, detail: str) -> None:
        steps.append({"step": name, "result": "PASS" if ok else "FAIL", "detail": detail})
        log(f"[{'PASS' if ok else 'FAIL'}] {name:34} {detail}")

    try:
        start_container()
        record("rehearsal.worker_started", True, f"{CONTAINER} is polling")

        created = harness("create")
        run_id = created["runId"]
        record("run.created", bool(run_id), f"run {run_id}")

        paused = wait_for_state(run_id, "WAITING_FOR_TOOL")
        record("run.waiting_for_tool",
               paused["state"] == "WAITING_FOR_TOOL" and bool(paused["pendingToolRequest"]),
               f"pending tool {paused.get('pendingToolName')} "
               f"({paused.get('pendingToolRequest')})")

        before = docker("inspect", "--format", "{{.State.StartedAt}}", CONTAINER).stdout.strip()
        restarted = docker("restart", CONTAINER, timeout=180)
        if restarted.returncode != 0:
            raise StackError(f"the container would not restart: {restarted.stderr[-400:]}")
        wait_for_poller()
        after = docker("inspect", "--format", "{{.State.StartedAt}}", CONTAINER).stdout.strip()
        record("worker.restarted", before != after and bool(after),
               f"the container started again at {after}")

        still = harness("state", "--run", run_id)
        record("run.survived_the_restart", still["state"] == "WAITING_FOR_TOOL",
               f"state {still['state']} after the restart")

        harness("resolve", "--run", run_id)
        record("tool.result_delivered", True, "the result was stored and the workflow signalled")

        finished = wait_for_state(run_id, "SUCCEEDED", "FAILED", "CANCELLED")
        record("run.resumed_and_completed", finished["state"] == "SUCCEEDED",
               f"state {finished['state']}"
               + (f" ({finished.get('errorType')})" if finished["state"] != "SUCCEEDED" else ""))
        record("run.answered", "IACODE_DURABILITY_OK" in (finished.get("result") or ""),
               "the answer produced after the restart is the run's result")

        recorded = harness("events", "--run", run_id)
        types = [item["type"] for item in recorded]
        record("history.records_the_pause_and_the_resume",
               "TOOL_REQUESTED" in types and "TOOL_RESULT_RECEIVED" in types
               and "RUN_COMPLETED" in types,
               ", ".join(types))
        record("history.is_ordered",
               [item["sequence"] for item in recorded]
               == sorted(item["sequence"] for item in recorded),
               f"{len(recorded)} event(s) in sequence order")
    finally:
        docker("rm", "-f", CONTAINER)

    failed = [step for step in steps if step["result"] == "FAIL"]
    if arguments.report:
        arguments.report.parent.mkdir(parents=True, exist_ok=True)
        arguments.report.write_text(json.dumps({
            "result": "PASS" if not failed else "FAIL",
            "container": CONTAINER,
            "steps": steps,
        }, indent=2) + "\n", encoding="utf-8", newline="\n")
        log(f"wrote {arguments.report}")

    log(f"AGENT_RUNTIME_DURABILITY={'PASS' if not failed else 'FAIL'} "
        f"{len(steps) - len(failed)}/{len(steps)} steps")
    return 0 if not failed else 1


if __name__ == "__main__":
    main_guard(main)
