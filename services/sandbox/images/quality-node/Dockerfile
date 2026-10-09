FROM node:22.23.2-bookworm-slim@sha256:48e4b67d85f87bd551df43704e24d252f56cc5f8e9718841aace50f19948f0f9

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      git=1:2.39.5-0+deb12u3 python3=3.11.2-1+b1 \
 && rm -rf /var/lib/apt/lists/* \
 && groupadd --gid 10001 sandbox \
 && useradd --uid 10001 --gid 10001 --no-create-home --home-dir /tmp \
      --shell /usr/sbin/nologin sandbox \
 && mkdir -p /workspace /opt/iacode/node-toolchain /opt/iacode/npm-cache \
 && chown sandbox:sandbox /workspace

COPY apps/web/package.json apps/web/package-lock.json /opt/iacode/node-toolchain/
RUN cd /opt/iacode/node-toolchain \
 && npm ci --ignore-scripts --cache /opt/iacode/npm-cache \
 && rm -rf /opt/iacode/node-toolchain/node_modules \
 && npm cache verify --cache /opt/iacode/npm-cache

COPY services/sandbox/src/iacode_sandbox/helper.py /opt/iacode/sandbox_helper.py
COPY services/sandbox/src/iacode_sandbox/paths.py /opt/iacode/paths.py
COPY services/sandbox/src/iacode_sandbox/patching.py /opt/iacode/patching.py
COPY .iacode/policies/secret-scan-allowlist.json /opt/iacode/secret-scan-allowlist.json
COPY services/sandbox/images/quality-node/gitconfig /opt/iacode/gitconfig
COPY services/sandbox/images/quality-node/node_install.sh /usr/local/bin/iacode-quality-node-install
COPY services/sandbox/images/quality_secret_scan.py /usr/local/bin/iacode-quality-secret-scan
RUN chmod -R a=rX /opt/iacode \
 && chmod 0555 /usr/local/bin/iacode-quality-node-install \
      /usr/local/bin/iacode-quality-secret-scan

USER sandbox
WORKDIR /workspace
CMD ["python3", "-I", "/opt/iacode/sandbox_helper.py", "--init"]
