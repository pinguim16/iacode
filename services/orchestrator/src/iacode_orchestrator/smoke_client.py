"""Start the Foundation smoke workflow and print what the worker observed.

Lives in the worker package so it uses the same SDK version, the same configuration model and the
same task queue name as the worker it exercises. A separate client with its own copy of those three
things would eventually test a different system than the one that is running.

    python -m iacode_orchestrator.smoke_client
"""

from __future__ import annotations

import asyncio
import dataclasses
import json
import sys
import uuid

from temporalio.client import Client

from iacode_orchestrator.config import get_worker_settings
from iacode_orchestrator.workflows.smoke import SmokeInput, SmokeWorkflow

# Long enough to survive a worker that is still starting, short enough that a queue nobody polls
# fails the smoke check instead of hanging the verification.
EXECUTION_TIMEOUT_SECONDS = 60.0


async def run() -> int:
    settings = get_worker_settings()
    client = await Client.connect(settings.temporal_target, namespace=settings.namespace)
    result = await asyncio.wait_for(
        client.execute_workflow(
            SmokeWorkflow.run,
            SmokeInput(message="foundation-smoke", requestedBy="smoke_client"),
            id=f"iacode-foundation-smoke-{uuid.uuid4()}",
            task_queue=settings.task_queue,
        ),
        timeout=EXECUTION_TIMEOUT_SECONDS,
    )
    # One line of JSON, so the caller parses a result rather than scraping prose.
    print(json.dumps(dataclasses.asdict(result)))
    return 0


def main() -> int:
    try:
        return asyncio.run(run())
    except TimeoutError:
        print(
            "the smoke workflow did not complete in "
            f"{EXECUTION_TIMEOUT_SECONDS:g}s; no worker is polling the task queue",
            file=sys.stderr)
        return 1
    except Exception as error:
        print(f"the smoke workflow failed: {type(error).__name__}: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
