"""Liveness and readiness, including the case the two exist to distinguish.

The decisive test is :func:`test_health_is_up_while_dependencies_are_down`. Nothing is stubbed to
produce it: the application is built with settings that point at services which are not running, so
every dependency really is unreachable. That is the state a liveness probe must survive and a
readiness probe must refuse.
"""

from __future__ import annotations

import asyncio

from fastapi.testclient import TestClient
from iacode_api.readiness import DependencyProbe, run_probes


def test_health_is_up_while_dependencies_are_down(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "UP"
    assert body["service"] == "iacode-api"
    assert body["version"] == "0.0.0-test"
    assert body["timestamp"].endswith("Z")


def test_health_answers_without_contacting_a_dependency(client: TestClient) -> None:
    """A liveness probe must be fast because it touches nothing.

    Timing is the only way to observe "contacted nothing" from outside. Each dependency probe is
    bounded at two seconds in the test profile, so a /health that reached even one of them could
    not answer in well under that.
    """
    import time

    started = time.perf_counter()
    response = client.get("/health")
    elapsed = time.perf_counter() - started

    assert response.status_code == 200
    assert elapsed < 0.5, f"/health took {elapsed:.3f}s, which means it probed something"


def test_ready_refuses_when_dependencies_are_unreachable(client: TestClient) -> None:
    response = client.get("/ready")

    assert response.status_code == 503
    body = response.json()
    assert body["status"] == "NOT_READY"


def test_ready_reports_each_dependency(client: TestClient) -> None:
    body = client.get("/ready").json()

    reported = {item["name"] for item in body["dependencies"]}
    assert reported == {"postgres", "redis", "minio", "temporal"}
    for item in body["dependencies"]:
        assert item["mandatory"] is True
        assert item["status"] == "DOWN"
        assert item["detail"], f"{item['name']} failed without saying why"
        assert item["latencyMs"] is not None


def test_readiness_detail_carries_no_credential(client: TestClient) -> None:
    """A driver error quotes the connection string it failed on, password included."""
    body = client.get("/ready").json()

    for item in body["dependencies"]:
        detail = item["detail"] or ""
        assert "iacode:iacode@" not in detail
        assert "test-secret" not in detail


def test_readiness_is_ready_when_every_probe_succeeds() -> None:
    """The positive path, executed rather than assumed.

    A control that has only ever been observed refusing is a control nobody has proved can pass;
    `.iacode/memory/lessons.jsonl` records exactly that failure class.
    """

    async def succeed() -> None:
        return None

    outcome = asyncio.run(run_probes(
        [DependencyProbe(name="one", probe=succeed),
         DependencyProbe(name="two", probe=succeed)],
        timeout_seconds=1.0,
    ))

    assert outcome.ready is True
    assert [report.status.value for report in outcome.reports] == ["UP", "UP"]


def test_readiness_ignores_a_failing_optional_dependency() -> None:
    async def succeed() -> None:
        return None

    async def fail() -> None:
        raise RuntimeError("nope")

    outcome = asyncio.run(run_probes(
        [DependencyProbe(name="mandatory", probe=succeed, mandatory=True),
         DependencyProbe(name="optional", probe=fail, mandatory=False)],
        timeout_seconds=1.0,
    ))

    assert outcome.ready is True
    assert [report.status.value for report in outcome.reports] == ["UP", "DOWN"]


def test_readiness_bounds_a_hanging_probe() -> None:
    """A readiness endpoint that can hang is worse than one that reports failure."""

    async def hang() -> None:
        await asyncio.sleep(30)

    outcome = asyncio.run(
        run_probes([DependencyProbe(name="slow", probe=hang)], timeout_seconds=0.2))

    assert outcome.ready is False
    assert "did not answer within" in (outcome.reports[0].detail or "")


def test_readiness_probes_run_concurrently() -> None:
    """Four dependencies each timing out serially would make readiness take four timeouts."""
    import time

    async def slow() -> None:
        await asyncio.sleep(0.3)

    started = time.perf_counter()
    asyncio.run(run_probes([DependencyProbe(name=f"d{index}", probe=slow) for index in range(4)],
                           timeout_seconds=2.0))
    elapsed = time.perf_counter() - started

    assert elapsed < 0.9, f"probes took {elapsed:.3f}s, which is serial rather than concurrent"
