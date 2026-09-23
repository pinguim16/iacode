# The iacode-dev sandbox image profile: where an agent's tools run.
#
# Built from the repository root:
#
#   docker build -f services/sandbox/images/iacode-dev/Dockerfile \
#     --label org.iacode.sandbox.fingerprint=<fingerprint> -t iacode/sandbox-iacode-dev:<tag> .
#
# `scripts/iacode/sandbox_image.py` does exactly that, with the tag derived from the content of this
# directory and of the helper modules below (`iacode_sandbox.image`). Nothing refers to this image
# by a mutable name, so a sandbox can only run from an image built from the inputs in front of it.
#
# What it carries is what the Gate needs and no more: Git, Python 3.13 and the helper. No compiler,
# no package manager usable at run time (the root filesystem is mounted read-only and the process is
# not root), no network client beyond what Git and Python ship, and no credential of any kind.

# The base is pinned by digest as well as by tag: a tag can be moved, a digest cannot.
FROM python:3.13.15-slim-bookworm@sha256:2325bb286ec344af3e5898cc224b5844e2707ac6e26b1632516fd3edc84a5e26

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Git at an exact version. A rebuild that cannot find this version fails loudly instead of quietly
# installing a different Git.
RUN apt-get update \
 && apt-get install -y --no-install-recommends git=1:2.39.5-0+deb12u3 \
 && rm -rf /var/lib/apt/lists/* \
 && groupadd --gid 10001 sandbox \
 && useradd --uid 10001 --gid 10001 --no-create-home --home-dir /tmp --shell /usr/sbin/nologin sandbox \
 && mkdir -p /workspace /opt/iacode \
 && chown sandbox:sandbox /workspace

# The helper and the two modules it runs, from the same files the controller's package holds. The
# path resolver inside the sandbox is therefore the path resolver the repository tests.
COPY services/sandbox/src/iacode_sandbox/helper.py /opt/iacode/sandbox_helper.py
COPY services/sandbox/src/iacode_sandbox/paths.py /opt/iacode/paths.py
COPY services/sandbox/src/iacode_sandbox/patching.py /opt/iacode/patching.py
COPY services/sandbox/images/iacode-dev/gitconfig /opt/iacode/gitconfig
RUN chmod -R a=rX /opt/iacode

USER sandbox
WORKDIR /workspace

# PID 1 is the helper in init mode: it reaps every orphan and exits when the engine stops the
# container. A session's container otherwise idles; every tool runs through `docker exec`.
CMD ["python3", "-I", "/opt/iacode/sandbox_helper.py", "--init"]
