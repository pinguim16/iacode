FROM python:3.13.15-slim-bookworm@sha256:2325bb286ec344af3e5898cc224b5844e2707ac6e26b1632516fd3edc84a5e26

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update \
 && apt-get install -y --no-install-recommends git=1:2.39.5-0+deb12u3 \
 && rm -rf /var/lib/apt/lists/* \
 && python -m pip install --no-cache-dir \
      alembic==1.20.0 coverage==7.13.4 pytest==9.1.1 ruff==0.16.8 \
 && groupadd --gid 10001 sandbox \
 && useradd --uid 10001 --gid 10001 --no-create-home --home-dir /tmp \
      --shell /usr/sbin/nologin sandbox \
 && mkdir -p /workspace /opt/iacode \
 && chown sandbox:sandbox /workspace

COPY services/sandbox/src/iacode_sandbox/helper.py /opt/iacode/sandbox_helper.py
COPY services/sandbox/src/iacode_sandbox/paths.py /opt/iacode/paths.py
COPY services/sandbox/src/iacode_sandbox/patching.py /opt/iacode/patching.py
COPY services/sandbox/images/quality-python/gitconfig /opt/iacode/gitconfig
COPY services/sandbox/images/quality-python/secret_scan.py /usr/local/bin/iacode-quality-secret-scan
RUN chmod -R a=rX /opt/iacode \
 && chmod 0555 /usr/local/bin/iacode-quality-secret-scan

USER sandbox
WORKDIR /workspace
CMD ["python3", "-I", "/opt/iacode/sandbox_helper.py", "--init"]
