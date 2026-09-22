# The IACode web shell.
#
# Build in Node, serve from nginx. The runtime image contains static files and a web server; the
# toolchain, the dependencies and the source map generator stay in the builder, where they cannot
# be served to a visitor.
#
# The backend address is **not** baked in. `docker-entrypoint.sh` writes `config.json` from the
# container's environment at start-up, so one image runs against any backend. Compiling the address
# into the bundle would mean an image per environment, which defeats the point of building one.
#
# npm is upgraded to 12.0.2 before any install. The npm that ships with this Node image (10.9.8)
# fails to resolve this dependency tree with "Cannot read properties of null (reading 'edgesOut')",
# so the pin is load-bearing rather than cosmetic.

FROM node:22.23.2-bookworm-slim AS builder

ENV NPM_CONFIG_UPDATE_NOTIFIER=false \
    NPM_CONFIG_FUND=false

RUN npm install --global npm@12.0.2

WORKDIR /build

# The lock alone first: dependencies change far less often than source, and `npm ci` is the slow
# step. `npm ci` rather than `npm install` because it installs exactly the lock and fails when
# package.json and the lock disagree, instead of quietly resolving something new.
COPY apps/web/package.json apps/web/package-lock.json ./
RUN npm ci --no-audit --no-fund

COPY apps/web/ ./
RUN npm run build

FROM nginx:1.30.5-alpine-slim AS runtime

ARG IACODE_VERSION=0.1.0
ARG IACODE_COMMIT=unknown
ARG IACODE_BUILD_TIMESTAMP=unknown

ENV IACODE_VERSION=${IACODE_VERSION} \
    IACODE_COMMIT=${IACODE_COMMIT} \
    IACODE_BUILD_TIMESTAMP=${IACODE_BUILD_TIMESTAMP} \
    IACODE_WEB_API_BASE_URL=""

COPY --from=builder /build/dist/web/browser /usr/share/nginx/html
COPY apps/web/nginx.conf /etc/nginx/conf.d/default.conf
COPY apps/web/docker-entrypoint.sh /docker-entrypoint.d/40-iacode-config.sh

# Port 8080 and a writable prefix, so nginx runs unprivileged. Binding 80 would need the
# capability to bind a privileged port, which is a root requirement for no benefit.
RUN sed -i 's/^user .*$//' /etc/nginx/nginx.conf \
 && sed -i -E 's#^pid .*;#pid /tmp/nginx.pid;#' /etc/nginx/nginx.conf \
 && grep -q 'pid /tmp/nginx.pid;' /etc/nginx/nginx.conf \
 && chmod +x /docker-entrypoint.d/40-iacode-config.sh \
 && mkdir -p /var/cache/nginx /tmp \
 && chown -R nginx:nginx /var/cache/nginx /usr/share/nginx/html

USER nginx
EXPOSE 8080
