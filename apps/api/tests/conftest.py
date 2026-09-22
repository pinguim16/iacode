"""Shared fixtures.

Two kinds of test live here and the split is enforced rather than assumed:

``tests/unit``         no external service. They run in the image with nothing else started, which
                       is what makes them usable as a mandatory gate.
``tests/integration``  the real PostgreSQL, Redis, MinIO and Temporal from the Compose stack. They
                       are marked ``integration`` and are skipped — loudly, with a reason — when
                       the stack is not there.

There is no third kind. `docs/DEVELOPMENT-CONTRACT.md` forbids proving an integration with a mock
when the real service exists in the test stack, so nothing here fakes a database.
"""

from __future__ import annotations

import os
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from iacode_api.config import Settings, settings_for_tests
from iacode_api.main import create_app

# The marker every test that needs the live stack carries.
INTEGRATION = pytest.mark.integration


def stack_settings() -> Settings:
    """Settings pointing at the running stack, taken from the container's own environment.

    The integration tests run inside the API image on the Compose network, so the environment
    already describes the stack correctly. Reading it here is the one place that is deliberate
    rather than accidental: these tests are *about* the configured stack.
    """
    return Settings()


def stack_is_configured() -> bool:
    """Whether this process was given a stack to talk to."""
    return bool(os.environ.get("IACODE_DATABASE_URL"))


@pytest.fixture
def settings() -> Settings:
    """Deterministic settings that read nothing from the environment."""
    return settings_for_tests()


@pytest.fixture
def client(settings: Settings) -> Iterator[TestClient]:
    """An application with its lifespan run, and no dependency reachable.

    Nothing is stubbed. The clients are real; they simply have nothing to connect to, which is
    exactly the state the liveness and readiness contracts are about.
    """
    app = create_app(settings)
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def live_client() -> Iterator[TestClient]:
    """An application wired to the running Compose stack."""
    if not stack_is_configured():
        pytest.skip("the Foundation stack is not configured for this process")
    app = create_app(stack_settings())
    with TestClient(app) as test_client:
        yield test_client
