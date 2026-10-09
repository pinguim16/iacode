# The IACode Quality Engine service and mandatory test image.
#
# The evaluator never receives the container engine socket and never mounts a project path. It
# dispatches commands to the sandbox service through Temporal. The image carries the canonical
# quality policy and its own suite so the mandatory gate builds what it measures.

FROM python:3.13.15-slim-bookworm@sha256:2325bb286ec344af3e5898cc224b5844e2707ac6e26b1632516fd3edc84a5e26 AS builder

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
COPY services/evaluator /build/services/evaluator
RUN pip install --no-cache-dir --no-deps \
      /build/packages/common /build/packages/contracts /build/packages/persistence \
      /build/packages/telemetry /build/services/evaluator

FROM python:3.13.15-slim-bookworm@sha256:2325bb286ec344af3e5898cc224b5844e2707ac6e26b1632516fd3edc84a5e26 AS runtime

ARG IACODE_VERSION=0.1.0
ARG IACODE_COMMIT=unknown
ARG IACODE_BUILD_TIMESTAMP=unknown

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    IACODE_VERSION=${IACODE_VERSION} \
    IACODE_COMMIT=${IACODE_COMMIT} \
    IACODE_BUILD_TIMESTAMP=${IACODE_BUILD_TIMESTAMP} \
    IACODE_REPOSITORY_ROOT=/app

RUN groupadd --gid 10001 iacode \
 && useradd --uid 10001 --gid 10001 --create-home --shell /usr/sbin/nologin iacode

COPY --from=builder /opt/venv /opt/venv
WORKDIR /app
COPY --chown=iacode:iacode .iacode/policies /app/.iacode/policies
COPY --chown=iacode:iacode services/evaluator/pyproject.toml /app/pyproject.toml
COPY --chown=iacode:iacode services/evaluator/src /app/evaluator_source
COPY --chown=iacode:iacode services/evaluator/tests /app/evaluator_tests

USER iacode
CMD ["python", "-m", "iacode_evaluator.worker"]
