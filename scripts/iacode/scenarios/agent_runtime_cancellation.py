#!/usr/bin/env python3
"""The cancellation scenario: a paused run is stopped, and stays stopped.

`docs/GATE-2-CHECKLIST.md` rows 12.2 and 12.4. Cancelling a run has to do three things, and only a
real workflow can show all three:

    the run pauses on a tool request
      -> cancel reaches the durable workflow and it stops
      -> the run is CANCELLED, terminal, and its pending request is closed
      -> a tool result that arrives afterwards is refused

The third is the one that matters most. A run that could be woken by a late or forged result would
be a run whose cancellation was a label rather than a decision.

The harness is the same as the durability scenario's: the real workflow, the real persistence, the
real Temporal server, and one scripted model so an agent asks for a tool in a Gate where no shipped
profile may have one. Nothing is executed at any point.

    python scripts/iacode/scenarios/agent_runtime_cancellation.py
    python scripts/iacode/scenarios/agent_runtime_cancellation.py --report var/agent-cancel.json
"""

from __future__ import annotations

import argparse
import json
import sys
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--report", type=Path, default=None)
    arguments = parser.parse_args()

    steps: list[dict] = []

    def record(name: str, ok: bool, detail: str) -> None:
        steps.append({"step": name, "result": "PASS" if ok else "FAIL", "detail": detail})
        log(f"[{'PASS' if ok else 'FAIL'}] {name:36} {detail}")

    try:
        start_container()
        record("rehearsal.worker_started", True, f"{CONTAINER} is polling")

        run_id = harness("create")["runId"]
        record("run.created", bool(run_id), f"run {run_id}")

        paused = wait_for_state(run_id, "WAITING_FOR_TOOL")
        record("run.waiting_for_tool", bool(paused["pendingToolRequest"]),
               f"pending tool {paused.get('pendingToolName')}")

        harness("cancel", "--run", run_id)
        finished = wait_for_state(run_id, "CANCELLED", "SUCCEEDED", "FAILED")
        record("cancel.reached_the_workflow", finished["state"] == "CANCELLED",
               f"state {finished['state']}")

        after = harness("state", "--run", run_id)
        record("cancel.is_terminal", after["state"] == "CANCELLED",
               "the run stayed cancelled")
        record("cancel.closed_the_pending_request", after["pendingToolRequest"] is None,
               "no request is left waiting for an answer nobody will give")

        late = harness("try-resolve", "--run", run_id)
        record("late_result.refused", late.get("accepted") is False,
               str(late.get("reason"))[:120])

        recorded = harness("events", "--run", run_id)
        types = [item["type"] for item in recorded]
        record("history.records_the_cancellation", "RUN_CANCELLED" in types,
               ", ".join(types))
        record("history.has_no_work_after_the_cancellation",
               types.index("RUN_CANCELLED") == len(types) - 1,
               "the cancellation is the last thing that happened")
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

    log(f"AGENT_RUNTIME_CANCELLATION={'PASS' if not failed else 'FAIL'} "
        f"{len(steps) - len(failed)}/{len(steps)} steps")
    return 0 if not failed else 1


if __name__ == "__main__":
    main_guard(main)
