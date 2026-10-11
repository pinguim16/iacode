"""Shared, policy-derived observation of asynchronous Prometheus target state."""

from __future__ import annotations

import re
import time
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any

from compose import REPOSITORY_ROOT, StackError

PROMETHEUS_CONFIG = REPOSITORY_ROOT / "infra" / "prometheus" / "prometheus.yml"
OBSERVATION_SCRAPE_CYCLES = 3


def prometheus_scrape_interval_seconds(path: Path = PROMETHEUS_CONFIG) -> float:
    """Read the global scrape interval from the versioned Prometheus configuration."""
    text = path.read_text(encoding="utf-8")
    match = re.search(r"(?m)^\s*scrape_interval:\s*([0-9]+(?:\.[0-9]+)?)(ms|s|m)\s*$", text)
    if match is None:
        raise StackError(f"{path} declares no supported global scrape_interval")
    value = float(match.group(1))
    scale = {"ms": 0.001, "s": 1.0, "m": 60.0}[match.group(2)]
    seconds = value * scale
    if seconds <= 0:
        raise StackError(f"{path} declares a non-positive scrape_interval")
    return seconds


def prometheus_wait_budget_seconds(path: Path = PROMETHEUS_CONFIG) -> float:
    """A bounded budget of complete scrape cycles, derived rather than hand-tuned."""
    return prometheus_scrape_interval_seconds(path) * OBSERVATION_SCRAPE_CYCLES


def wait_for_prometheus_targets(
    fetch: Callable[[], dict[str, Any]],
    required_jobs: Sequence[str],
    *,
    config_path: Path = PROMETHEUS_CONFIG,
    monotonic: Callable[[], float] | None = None,
    sleeper: Callable[[float], None] | None = None,
) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str | None, Any]]:
    """Observe until every required job is up or the configured scrape budget expires.

    ``fetch`` only reads Prometheus.  The helper never restarts a target and never repeats the
    action being judged, so a failed service or check cannot be converted into a pass by retry.
    """
    monotonic = monotonic or time.monotonic
    sleeper = sleeper or time.sleep
    scrape_interval = prometheus_scrape_interval_seconds(config_path)
    deadline = monotonic() + scrape_interval * OBSERVATION_SCRAPE_CYCLES
    poll_seconds = min(3.0, max(0.1, scrape_interval / 5.0))
    payload: dict[str, Any] = {}
    targets: list[dict[str, Any]] = []
    by_job: dict[str | None, Any] = {}
    while True:
        payload = fetch()
        raw_targets = payload.get("data", {}).get("activeTargets", [])
        targets = [item for item in raw_targets if isinstance(item, dict)]
        by_job = {
            item.get("labels", {}).get("job"): item.get("health")
            for item in targets
            if isinstance(item.get("labels"), dict)
        }
        if all(by_job.get(job) == "up" for job in required_jobs):
            return payload, targets, by_job
        remaining = deadline - monotonic()
        if remaining <= 0:
            return payload, targets, by_job
        sleeper(min(poll_seconds, remaining))
