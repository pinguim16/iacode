"""Privileged test actor executed only inside an explicitly owned live-proof API container.

It temporarily corrupts/removes one exact quality source object, retaining an exclusive bounded
backup in that disposable container. No credential, object key, source bytes or SQL is printed.
This is not a product endpoint or a runtime fallback.
"""

from __future__ import annotations

import hashlib
import io
import json
import sys
import uuid
from pathlib import Path


def main() -> int:
    from iacode_api.config import Settings
    from iacode_persistence.models import Artifact
    from minio import Minio
    from sqlalchemy import create_engine, select
    from sqlalchemy.orm import Session

    identifier = uuid.UUID(sys.argv[1])
    mode = sys.argv[2]
    if mode not in ("corrupt", "remove", "restore"):
        raise ValueError("unknown owned source test mode")
    settings = Settings()
    engine = create_engine(settings.database_url.replace("+asyncpg", "+psycopg", 1))
    try:
        with Session(engine) as session:
            artifact = session.scalar(select(Artifact).where(Artifact.id == identifier))
            if artifact is None or not artifact.kind.startswith("quality."):
                raise ValueError("exact quality source artifact is required")
            bucket, key = artifact.storage_bucket, artifact.storage_key
            checksum, size = artifact.checksum_sha256, artifact.size_bytes
    finally:
        engine.dispose()
    if not 0 <= size <= 4 * 1024 * 1024:
        raise ValueError("owned source object exceeds the test ceiling")
    client = Minio(
        settings.minio_endpoint,
        access_key=settings.minio_access_key.get_secret_value(),
        secret_key=settings.minio_secret_key.get_secret_value(),
        secure=settings.minio_secure,
    )
    backup = Path("/tmp") / ("iacode-experience-source-" + str(identifier) + ".backup")
    if backup.is_symlink():
        raise ValueError("redirected owned source backup refused")
    if mode == "restore":
        raw = backup.read_bytes()
        if len(raw) != size or hashlib.sha256(raw).hexdigest() != checksum:
            raise ValueError("owned source backup integrity failed")
        client.put_object(bucket, key, io.BytesIO(raw), length=len(raw))
        backup.unlink()
    else:
        response = client.get_object(bucket, key)
        try:
            raw = response.read(size + 1)
        finally:
            response.close()
            response.release_conn()
        if len(raw) != size or hashlib.sha256(raw).hexdigest() != checksum:
            raise ValueError("clean owned source premise failed")
        with backup.open("xb") as output:
            output.write(raw)
        if mode == "corrupt":
            altered = raw + b"owned-corruption"
            client.put_object(bucket, key, io.BytesIO(altered), length=len(altered))
        else:
            client.remove_object(bucket, key)
    print(
        json.dumps(
            {
                "mode": mode,
                "artifactId": str(identifier),
                "originalDigest": checksum,
                "result": "APPLIED",
            }
        )
    )
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    raise SystemExit(main())
