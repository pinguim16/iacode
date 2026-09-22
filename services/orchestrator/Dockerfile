# The IACode Temporal worker image.
#
# It installs the same dependency lock as the API. One lock for both processes is deliberate: the
# worker and the API share the workflow SDK and the telemetry package, and two locks would let the
# two sides of a workflow contract drift apart between builds — which surfaces as a
# deserialisation error in an activity rather than as a dependency problem.
#
# The build context is the repository root, because the worker depends on the local packages.

FROM python:3.13.15-slim-bookworm AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /build
COPY apps/api/requirements.lock.txt /build/requirements.lock.txt
RUN pip install --no-cache-dir -r /build/requirements.lock.txt

COPY packages/common /build/packages/common
COPY packages/contracts /build/packages/contracts
COPY packages/persistence /build/packages/persistence
COPY packages/telemetry /build/packages/telemetry
COPY services/agent-runtime /build/services/agent-runtime
RUN pip install --no-cache-dir --no-deps \
      /build/packages/common /build/packages/contracts /build/packages/persistence \
      /build/packages/telemetry /build/services/agent-runtime

FROM python:3.13.15-slim-bookworm AS runtime

ARG IACODE_VERSION=0.1.0
ARG IACODE_COMMIT=unknown
ARG IACODE_BUILD_TIMESTAMP=unknown

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    PYTHONPATH=/app/src \
    IACODE_VERSION=${IACODE_VERSION} \
    IACODE_COMMIT=${IACODE_COMMIT} \
    IACODE_BUILD_TIMESTAMP=${IACODE_BUILD_TIMESTAMP}

RUN groupadd --gid 10001 iacode \
 && useradd --uid 10001 --gid 10001 --create-home --shell /usr/sbin/nologin iacode

COPY --from=builder /opt/venv /opt/venv

WORKDIR /app
COPY --chown=iacode:iacode services/orchestrator/src /app/src
COPY --chown=iacode:iacode services/orchestrator/pyproject.toml /app/pyproject.toml
# The declared agents, teams and prompt templates. The runtime reads them from
# ``IACODE_REPOSITORY_ROOT``, which is /app in this image, so the profiles the worker executes
# are the ones the repository declares rather than a copy somebody kept in step by hand.
COPY --chown=iacode:iacode agents /app/agents
# The durability rehearsal. It lands beside the source rather than inside it, so the running
# worker cannot import any of it: the separation is a path, not a promise. The API image
# carries its suites the same way and for the same reason.
COPY --chown=iacode:iacode services/orchestrator/rehearsal /app/rehearsal

USER iacode

# Exec form so the container receives SIGTERM directly and the worker's graceful shutdown runs.
CMD ["python", "-m", "iacode_orchestrator.worker"]
