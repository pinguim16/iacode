#!/bin/sh
set -eu

test -f package.json
test -f package-lock.json
rm -rf /tmp/iacode-npm-cache
cp -R /opt/iacode/npm-cache /tmp/iacode-npm-cache
npm ci --offline --ignore-scripts --cache /tmp/iacode-npm-cache
exec npm audit --offline --cache /tmp/iacode-npm-cache
