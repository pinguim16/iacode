# The IACode sandbox service image: the controller that creates and drives sandboxes.
#
# It is the only image in the stack with the container engine's client, and the compose service that
# runs it is the only one given the engine's socket. It never hands that socket, or any host path,
# to a sandbox: `iacode_sandbox.backend.container_arguments` builds every sandbox without a volume,
# a bind mount or an inherited variable, and the Gate's suite asserts it.
#
# It installs the same dependency lock as the API and the worker, for the reason the worker's image
# gives: one lock keeps the two sides of a Temporal contract from drifting apart between builds.
#
# The build context is the repository root.

# --- The container client, pinned by version and by digest -------------------------------------
FROM python:3.13.15-slim-bookworm@sha256:2325bb286ec344af3e5898cc224b5844e2707ac6e26b1632516fd3edc84a5e26 AS docker-client

ARG DOCKER_VERSION=29.6.1
ARG DOCKER_SHA256=b0df4a43a98d7ecb708acbdb5a34a3416e13b6e39bcbbdf296f51f0f3442b29f

WORKDIR /download
RUN python - <<'PY'
import hashlib, os, tarfile, urllib.request
version, expected = os.environ["DOCKER_VERSION"], os.environ["DOCKER_SHA256"]
url = f"https://download.docker.com/linux/static/stable/x86_64/docker-{version}.tgz"
urllib.request.urlretrieve(url, "docker.tgz")
digest = hashlib.sha256(open("docker.tgz", "rb").read()).hexdigest()
if digest != expected:
    raise SystemExit(f"docker-{version}.tgz has digest {digest}, expected {expected}")
with tarfile.open("docker.tgz") as archive:
    member = archive.getmember("docker/docker")
    archive.extract(member, path="/download", filter="data")
PY

# --- Dependencies -------------------------------------------------------------------------------
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
COPY services/sandbox /build/services/sandbox
RUN pip install --no-cache-dir --no-deps \
      /build/packages/common /build/packages/contracts /build/packages/persistence \
      /build/packages/telemetry /build/services/sandbox

# --- Runtime ------------------------------------------------------------------------------------
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

COPY --from=docker-client /download/docker/docker /usr/local/bin/docker
COPY --from=builder /opt/venv /opt/venv

WORKDIR /app
# The canonical policy the service reads, and the inputs the sandbox image is built from, at the
# same repository-relative paths: the service computes the image fingerprint from these files and
# refuses to run a sandbox from an image built from anything else.
COPY --chown=iacode:iacode .iacode/policies /app/.iacode/policies
COPY --chown=iacode:iacode services/sandbox/images /app/services/sandbox/images
COPY --chown=iacode:iacode services/sandbox/src/iacode_sandbox/helper.py services/sandbox/src/iacode_sandbox/paths.py services/sandbox/src/iacode_sandbox/patching.py /app/services/sandbox/src/iacode_sandbox/
# The suite, beside the source rather than inside it, as the API image carries its suites, and the
# project file whose pytest settings collect it.
COPY --chown=iacode:iacode services/sandbox/pyproject.toml /app/pyproject.toml
COPY --chown=iacode:iacode services/sandbox/tests /app/sandbox_tests

USER iacode

CMD ["python", "-m", "iacode_sandbox.worker"]
