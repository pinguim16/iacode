# The IACode API image.
#
# Two stages. The builder installs into a virtual environment; the runtime copies that environment
# in, so build tooling and package index metadata never reach the shipped image.
#
# The build context is the repository root, because the API depends on the local packages under
# ``packages/``. A context of ``apps/api`` could not see them.
#
# Layer order is deliberate: the dependency lock is copied and installed before any source, so
# editing a module re-runs one fast layer instead of re-resolving the dependency tree.

# ---------------------------------------------------------------------------------------------
# Builder
# ---------------------------------------------------------------------------------------------
FROM python:3.13.15-slim-bookworm AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /build

# Third-party dependencies from the lock. ``--require-hashes`` is not used: the lock is produced
# from this same image and pins exact versions, and demanding hashes would force every contributor
# to regenerate them for a local change.
COPY apps/api/requirements.lock.txt /build/requirements.lock.txt
RUN pip install --no-cache-dir -r /build/requirements.lock.txt

# The local packages. ``--no-deps`` because their dependencies are already in the lock, and letting
# pip resolve them again could quietly upgrade a package the lock pinned.
COPY packages/common /build/packages/common
COPY packages/contracts /build/packages/contracts
COPY packages/telemetry /build/packages/telemetry
RUN pip install --no-cache-dir --no-deps \
      /build/packages/common /build/packages/contracts /build/packages/telemetry

# ---------------------------------------------------------------------------------------------
# Runtime
# ---------------------------------------------------------------------------------------------
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

# A fixed uid/gid rather than whatever the distro assigns next: a named volume written by this
# container keeps these numbers, and a rebuild that shifted them would make existing files
# unreadable.
RUN groupadd --gid 10001 iacode \
 && useradd --uid 10001 --gid 10001 --create-home --shell /usr/sbin/nologin iacode

COPY --from=builder /opt/venv /opt/venv

WORKDIR /app
COPY --chown=iacode:iacode apps/api/src /app/src
COPY --chown=iacode:iacode apps/api/migrations /app/migrations
COPY --chown=iacode:iacode apps/api/alembic.ini /app/alembic.ini
COPY --chown=iacode:iacode apps/api/pyproject.toml /app/pyproject.toml
COPY --chown=iacode:iacode apps/api/tests /app/tests

USER iacode
EXPOSE 8000

# Exec form, not shell form. With ``CMD command args`` the process would be a child of ``/bin/sh``,
# which does not forward SIGTERM, and the graceful shutdown this application implements would never
# run on ``docker compose stop``.
CMD ["uvicorn", "iacode_api.main:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
