#!/usr/bin/env python3
"""The deadline scenario: a run that is alive and going nowhere is ended rather than left running.

`docs/GATE-2-CHECKLIST.md` row 11.7. A turn limit stops an agent loop and the runtime's own suite
proves that without a workflow engine. The wall-clock deadline is different: it is the workflow's,
it is what stops a run that is making progress by its own arithmetic and no progress at all in
fact, and only a real workflow can show it firing.

    create a run whose agent answers "still working" for ever, with a short deadline
      -> the run executes turns
      -> the deadline passes
      -> the run is FAILED with RUN_DEADLINE_EXCEEDED, and its history says so

The harness is the durability scenario's: the real workflow, the real persistence, the stack's own
Temporal, and one scripted model. Nothing is executed at any point.

    python scripts/iacode/scenarios/agent_runtime_deadline.py
    python scripts/iacode/scenarios/agent_runtime_deadline.py --report var/agent-deadline.json
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from compose import log, main_guard
from scenarios.agent_runtime_durability import (
    CONTAINER,
    docker,
    harness,
    start_container,
    wait_for_state,
)

#: Short enough that the scenario is quick, long enough that several turns happen first.
DEADLINE_SECONDS = 10


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

        started = time.monotonic()
        run_id = harness("create", "--looping", "--deadline", str(DEADLINE_SECONDS))["runId"]
        record("run.created", bool(run_id),
               f"run {run_id} with a {DEADLINE_SECONDS}s deadline and an agent that never finishes")

        finished = wait_for_state(run_id, "FAILED", "SUCCEEDED", "CANCELLED")
        elapsed = time.monotonic() - started

        record("run.ended", finished["state"] == "FAILED", f"state {finished['state']}")
        record("run.ended_for_the_right_reason",
               finished.get("errorType") == "RUN_DEADLINE_EXCEEDED",
               f"errorType {finished.get('errorType')}")
        record("run.did_not_run_for_ever", elapsed < DEADLINE_SECONDS * 6,
               f"it ended after {elapsed:.1f}s against a {DEADLINE_SECONDS}s deadline")

        recorded = harness("events", "--run", run_id)
        types = [item["type"] for item in recorded]
        record("history.records_the_failure", types and types[-1] == "RUN_FAILED",
               ", ".join(types[-4:]))
        record("history.records_the_work_it_did",
               types.count("MODEL_CALL_COMPLETED") >= 1,
               f"{types.count('MODEL_CALL_COMPLETED')} completed model call(s) before the deadline")
    finally:
        docker("rm", "-f", CONTAINER)

    failed = [step for step in steps if step["result"] == "FAIL"]
    if arguments.report:
        arguments.report.parent.mkdir(parents=True, exist_ok=True)
        arguments.report.write_text(json.dumps({
            "result": "PASS" if not failed else "FAIL",
            "deadlineSeconds": DEADLINE_SECONDS,
            "steps": steps,
        }, indent=2) + "\n", encoding="utf-8", newline="\n")
        log(f"wrote {arguments.report}")

    log(f"AGENT_RUNTIME_DEADLINE={'PASS' if not failed else 'FAIL'} "
        f"{len(steps) - len(failed)}/{len(steps)} steps")
    return 0 if not failed else 1


if __name__ == "__main__":
    main_guard(main)
