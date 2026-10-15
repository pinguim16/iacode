#!/usr/bin/env python3
"""Observe the pinned SDK's typed cancellation using its real await implementation."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "scripts/iacode"))
from compose import compose

PROBE = r'''
import asyncio
import importlib.metadata
import json
from types import SimpleNamespace
from temporalio.exceptions import ActivityError, CancelledError
from temporalio.worker._workflow_instance import _WorkflowInstanceImpl

async def main():
    future = asyncio.get_running_loop().create_future()
    requests = []
    def request_cancel(_error):
        requests.append(True)
        error = ActivityError("cancelled polling read", scheduled_event_id=1,
                              started_event_id=2, identity="sdk-probe",
                              activity_type="read", activity_id="read", retry_state=None)
        error.__cause__ = CancelledError("owner cancelled polling read")
        future.set_exception(error)
    instance = SimpleNamespace(_single_batch_activation=False,
                               _cancel_reason=None, _deleting=False)
    task = asyncio.create_task(_WorkflowInstanceImpl._await_temporal_operation(
        instance, future, request_cancel,
    ))
    await asyncio.sleep(0)
    task.cancel()
    try:
        await task
    except ActivityError as error:
        correct = isinstance(error.cause, CancelledError) and len(requests) == 1
        print(json.dumps({"sdkVersion": importlib.metadata.version("temporalio"),
                          "outerError": type(error).__name__,
                          "causeType": type(error.cause).__name__,
                          "cancelCommands": len(requests),
                          "result": "PASS" if correct else "FAIL"}))
        return 0 if correct else 1
    return 1

raise SystemExit(asyncio.run(main()))
'''


def main() -> int:
    result = compose("run", "--rm", "--no-deps", "--entrypoint", "", "evaluator",
                     "python", "-c", PROBE, capture=False)
    return result.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
