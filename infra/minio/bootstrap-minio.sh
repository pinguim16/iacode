#!/bin/sh
# Create the artifact bucket, idempotently.
#
# Runs once per `docker compose up` and is a no-op when the bucket already exists, which is what
# makes it safe on a stack that is started and stopped all day. It fails loudly when MinIO refuses
# the credentials, because a bootstrap that exits zero without creating the bucket would let the
# API start and then fail its readiness probe with a confusing message about a missing bucket.
set -eu

ALIAS=iacode
BUCKET="${IACODE_MINIO_BUCKET:-iacode-artifacts}"

mc alias set "$ALIAS" http://minio:9000 "$MINIO_ROOT_USER" "$MINIO_ROOT_PASSWORD" >/dev/null

if mc ls "$ALIAS/$BUCKET" >/dev/null 2>&1; then
  echo "bucket $BUCKET already exists"
else
  mc mb "$ALIAS/$BUCKET"
  echo "bucket $BUCKET created"
fi

# Private by default. An artifact bucket readable without credentials would publish whatever a
# later Gate stores in it.
mc anonymous set none "$ALIAS/$BUCKET" >/dev/null
echo "bucket $BUCKET is private"
