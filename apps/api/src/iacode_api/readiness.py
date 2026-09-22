"""Readiness: can this process accept work?

The distinction from liveness is the whole point. ``/health`` answers "is the process alive" and
touches nothing external, so an orchestrator does not restart a healthy API because PostgreSQL is
slow. ``/ready`` answers "can it do its job" and therefore probes every mandatory dependency for
real.

Three rules this module exists to enforce:

1. **A probe is an operation, not a reachable port.** Each probe performs work the dependency can
   only complete if it is actually usable: a query, a ``PING``, a bucket lookup, a namespace
   description.
2. **Every probe is bounded.** A dependency that hangs must produce ``DOWN`` after the configured
   timeout, not a readiness request that never returns. A readiness endpoint that can hang is worse
   than one that reports failure, because a load balancer reads a timeout as "still deciding".
3. **A failure is never softened.** One mandatory dependency down means ``NOT_READY`` and a 503.
   There is no partially-ready state, and the payload names which dependency failed so an operator
   does not have to guess.

The probes run concurrently. Serially, four dependencies each timing out at three seconds would
make a readiness request take twelve.
"""

from __future__ import annotations

import asyncio
import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from iacode_common.redaction import redact_text
from iacode_contracts.foundation import DependencyReport, DependencyStatus

__all__ = ["DependencyProbe", "ProbeOutcome", "run_probes"]


@dataclass(frozen=True)
class DependencyProbe:
    """One dependency, how to prove it works, and whether readiness depends on it."""

    name: str
    probe: Callable[[], Awaitable[None]]
    mandatory: bool = True


@dataclass(frozen=True)
class ProbeOutcome:
    """The verdict and the evidence behind it."""

    ready: bool
    reports: list[DependencyReport]


async def _run_one(probe: DependencyProbe, timeout_seconds: float) -> DependencyReport:
    started = time.perf_counter()
    try:
        await asyncio.wait_for(probe.probe(), timeout=timeout_seconds)
    except TimeoutError:
        return DependencyReport(
            name=probe.name,
            status=DependencyStatus.DOWN,
            mandatory=probe.mandatory,
            latencyMs=round((time.perf_counter() - started) * 1000, 2),
            detail=f"probe did not answer within {timeout_seconds:g}s",
        )
    except Exception as error:
        # The message is redacted because a driver error routinely quotes the connection string it
        # failed on, and that string carries the password.
        return DependencyReport(
            name=probe.name,
            status=DependencyStatus.DOWN,
            mandatory=probe.mandatory,
            latencyMs=round((time.perf_counter() - started) * 1000, 2),
            detail=redact_text(f"{type(error).__name__}: {error}")[:300],
        )
    return DependencyReport(
        name=probe.name,
        status=DependencyStatus.UP,
        mandatory=probe.mandatory,
        latencyMs=round((time.perf_counter() - started) * 1000, 2),
        detail=None,
    )


async def run_probes(probes: list[DependencyProbe],
                     timeout_seconds: float) -> ProbeOutcome:
    """Probe every dependency concurrently and decide readiness from the mandatory ones."""
    reports = list(await asyncio.gather(
        *(_run_one(probe, timeout_seconds) for probe in probes)))
    ready = all(
        report.status is DependencyStatus.UP
        for report in reports
        if report.mandatory
    )
    return ProbeOutcome(ready=ready, reports=reports)
