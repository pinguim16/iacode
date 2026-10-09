FROM gradle:8.14.3-jdk21-alpine@sha256:d20561a56ff27350ea778b8151f6af913c76e9d35b6a135f927ee16e3ce8193c AS gradle-toolchain

FROM maven:3.9.12-eclipse-temurin-21@sha256:c3c9d3ac4ce8431a3995c0318b8d390f448e693dd4fabc16e9b68d2e1f3d7b46

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
 && apt-get install -y --no-install-recommends python3=3.12.3-0ubuntu2.1 \
 && rm -rf /var/lib/apt/lists/* \
 && groupadd --gid 10001 sandbox \
 && useradd --uid 10001 --gid 10001 --no-create-home --home-dir /tmp \
      --shell /usr/sbin/nologin sandbox \
 && mkdir -p /workspace /opt/iacode/m2 \
 && chown sandbox:sandbox /workspace

COPY --from=gradle-toolchain /opt/gradle /opt/gradle
RUN for tool in /opt/java/openjdk/bin/*; do ln -s "$tool" "/usr/local/bin/$(basename "$tool")"; done \
 && ln -s /opt/gradle/bin/gradle /usr/local/bin/gradle

COPY services/sandbox/images/quality-java/seed-pom.xml /tmp/seed-pom.xml
RUN mvn --batch-mode --file /tmp/seed-pom.xml dependency:go-offline \
 && cp -R /root/.m2/repository/. /opt/iacode/m2/ \
 && rm -rf /root/.m2 /tmp/seed-pom.xml

COPY services/sandbox/src/iacode_sandbox/helper.py /opt/iacode/sandbox_helper.py
COPY services/sandbox/src/iacode_sandbox/paths.py /opt/iacode/paths.py
COPY services/sandbox/src/iacode_sandbox/patching.py /opt/iacode/patching.py
COPY services/sandbox/images/quality-java/gitconfig /opt/iacode/gitconfig
COPY services/sandbox/images/quality-java/java_dependencies.py /usr/local/bin/iacode-quality-java-dependencies
COPY services/sandbox/images/quality-java/secret_scan.py /usr/local/bin/iacode-quality-secret-scan
RUN chmod -R a=rX /opt/iacode \
 && chmod 0555 /usr/local/bin/iacode-quality-java-dependencies \
      /usr/local/bin/iacode-quality-secret-scan

USER sandbox
WORKDIR /workspace
CMD ["python3", "-I", "/opt/iacode/sandbox_helper.py", "--init"]
