"""Resource limits and process control, exercised against real sandboxes.

The hostile workloads here are synthetic and confined: every one runs inside a sandbox whose limits
the policy sets, and the assertion after each is that the sandbox still answers, that nothing it
started survived, and that this process — the host side of the test — is still running the suite.
"""

from __future__ import annotations

import asyncio
import time

import pytest
from sandbox_fixtures import engine_harness, request


@pytest.fixture
def harness():
    created = engine_harness()
    yield created
    created.close()


def output(result) -> str:
    return str(result.output.get("stdout", ""))


def processes(harness, run_id: str) -> str:
    """What is running in the run's sandbox, read from /proc by a fresh command."""
    result = harness.shell("for p in /proc/[0-9]*; do tr '\\0' ' ' < $p/cmdline; echo; done",
                           run_id=run_id)
    return output(result)


def only_init_and_the_observer(listing: str) -> bool:
    lines = [line.strip() for line in listing.splitlines() if line.strip()]
    unexpected = [line for line in lines if "sandbox_helper.py" not in line
                  and "/proc/[0-9]" not in line and not line.startswith("tr ")
                  and not line.startswith("/bin/sh -c for p in")]
    return not unexpected


class ResourceLimitTests:
    def test_a_fork_bomb_is_contained_by_the_process_limit(self, harness) -> None:
        run_id = harness.run_id()
        bomb = ("python3 -c \"import os, time\n"
                "count = 0\n"
                "while True:\n"
                "    try:\n"
                "        os.fork(); count += 1\n"
                "    except OSError:\n"
                "        time.sleep(0.01)\"")
        started = time.monotonic()
        result = harness.shell(bomb, run_id=run_id, timeoutSeconds=8)
        assert result.status == "TIMED_OUT", result
        assert result.exit_code is None
        assert time.monotonic() - started < 90
        after = harness.shell("echo still-answering", run_id=run_id)
        assert output(after).strip() == "still-answering"
        assert only_init_and_the_observer(processes(harness, run_id))

    def test_a_process_that_exceeds_memory_fails_in_a_controlled_way(self, harness) -> None:
        run_id = harness.run_id()
        limit = harness.service.policies.get("developer").resources.memory_mb
        hog = f"python3 -c \"x = bytearray({limit * 2} * 1024 * 1024); print('allocated')\""
        result = harness.shell(hog, run_id=run_id, timeoutSeconds=60)
        assert result.status == "FAILED", result
        assert "allocated" not in output(result)
        assert result.exit_code not in (None, 0)
        after = harness.shell("echo survived", run_id=run_id)
        assert output(after).strip() == "survived"

    def test_the_workspace_cannot_outgrow_its_limit(self, harness) -> None:
        run_id = harness.run_id()
        limit = harness.service.policies.get("developer").resources.workspace_mb
        result = harness.shell(f"dd if=/dev/zero of=/workspace/fill bs=1M count={limit + 64} "
                               "2>&1; echo dd-exit:$?", run_id=run_id, timeoutSeconds=120)
        assert "No space left on device" in output(result)
        assert "dd-exit:0" not in output(result)
        harness.shell("rm -f /workspace/fill", run_id=run_id)

    def test_a_timeout_kills_the_whole_process_tree(self, harness) -> None:
        run_id = harness.run_id()
        tree = ("sleep 300 & (sleep 301 &) ; setsid sleep 302 & "
                "python3 -c 'import os, time\nif os.fork() == 0:\n"
                "    os.setsid(); time.sleep(303)\ntime.sleep(304)' & sleep 305")
        result = harness.shell(tree, run_id=run_id, timeoutSeconds=3)
        assert result.status == "TIMED_OUT" and result.timed_out
        assert result.exit_code is None
        listing = processes(harness, run_id)
        for survivor in ("sleep 300", "sleep 301", "sleep 302", "303", "304", "sleep 305"):
            assert survivor not in listing, listing
        assert only_init_and_the_observer(listing)

    def test_output_is_bounded_and_the_rest_is_an_artifact(self, harness) -> None:
        run_id = harness.run_id()
        size = 1_000_000
        result = harness.shell(f"python3 -c \"import sys; sys.stdout.write('y' * {size})\"",
                               run_id=run_id)
        limit = harness.service.policies.get("developer").resources.output_bytes
        assert result.status == "SUCCEEDED"
        assert result.truncated is True
        assert len(result.output["stdout"]) == limit
        assert result.output["stdoutBytes"] == size
        assert len(result.artifacts) == 1
        stored = harness.artifacts.objects[result.artifacts[0].key]
        assert len(stored) == size

    def test_a_cancelled_run_stops_its_command_and_leaves_nothing_running(self, harness) -> None:
        run_id = harness.run_id()
        harness.shell("true", run_id=run_id)
        payload = request("shell.exec", {"command": "sleep 120 & sleep 121"}, run_id=run_id)

        async def cancel_midway():
            task = asyncio.ensure_future(harness.service.execute(payload))
            await asyncio.sleep(3)
            task.cancel()
            with pytest.raises(asyncio.CancelledError):
                await task

        started = time.monotonic()
        asyncio.run(cancel_midway())
        assert time.monotonic() - started < 60
        recorded = asyncio.run(harness.store.execution(payload["toolRequestId"]))
        assert recorded is not None and recorded.status == "CANCELLED"
        listing = processes(harness, run_id)
        assert "sleep 120" not in listing and "sleep 121" not in listing
        assert harness.session(run_id).state == "READY"
