#!/bin/sh
# Write the runtime configuration the application reads at start-up.
#
# The nginx image runs every executable in /docker-entrypoint.d before starting the server, which is
# where this belongs: the file has to exist before the first request, and writing it at build time
# would put an environment-specific address into a supposedly portable image.
#
# An empty value is written as an empty string on purpose: the application treats that as "same
# origin", which is correct behind a reverse proxy and fails visibly when it is wrong.
set -eu

TARGET=/usr/share/nginx/html/config.json
BASE_URL="${IACODE_WEB_API_BASE_URL:-}"

# The value is interpolated into a JSON document, so a quote or a backslash in it would produce a
# file the application cannot parse. Refusing beats writing a broken config and failing later in the
# browser, where the cause is invisible.
if [ "$BASE_URL" != "$(printf '%s' "$BASE_URL" | tr -d '"\[:cntrl:]')" ]; then
  echo "IACODE_WEB_API_BASE_URL contains a quote, a backslash or a control character" >&2
  exit 1
fi

printf '{\n  "apiBaseUrl": "%s"\n}\n' "$BASE_URL" > "$TARGET"
echo "config.json written with apiBaseUrl=${BASE_URL:-<same origin>}"
