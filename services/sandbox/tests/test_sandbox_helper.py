"""Deterministic controls for the in-sandbox process sweeper."""

from __future__ import annotations

from iacode_sandbox import helper


def test_the_sweep_waits_for_zombies_to_be_reaped_before_returning(monkeypatch) -> None:
    """A zombie still consumes the PID limit even though SIGKILL cannot target it again."""
    process_tables = iter(({1, 42, 100}, {1, 42, 100}, {1, 42}))
    sleeps: list[float] = []

    monkeypatch.setattr(helper.os, "getpid", lambda: 42)
    monkeypatch.setattr(helper, "_pids", lambda: next(process_tables))
    monkeypatch.setattr(helper, "_state", lambda pid: "Z" if pid == 100 else "S")
    monkeypatch.setattr(helper.time, "monotonic", lambda: 0.0)
    monkeypatch.setattr(helper.time, "sleep", sleeps.append)

    assert helper.kill_everything_else(deadline_seconds=1.0, freeze_seconds=0.0) == 0
    assert sleeps == [0.02, 0.02]
