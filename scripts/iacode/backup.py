#!/usr/bin/env python3
"""Back up the Foundation's durable state.

Two things are backed up, because two things cannot be rebuilt:

``postgres``  a ``pg_dump`` of the IACode database in PostgreSQL's custom format, which restores
              selectively and compresses. Temporal's own databases are **not** included: they are
              Temporal's to rebuild, and restoring workflow history into a running cluster is not a
              recovery procedure, it is a way to corrupt one.
``minio``     a mirror of the artifact bucket.

Three rules, each of which exists because the opposite is the common failure:

1. **A partial backup is a failure.** If either part fails, the whole run exits non-zero and the
   manifest records what went wrong. A backup that half-succeeded and exited zero is worse than no
   backup, because it will be trusted.
2. **No credential is written into the output.** The manifest records what was backed up, not how
   the tooling authenticated, and every value it writes passes through the redactor.
3. **A backup is described by its manifest.** The restore reads the manifest rather than guessing
   from file names, so an incomplete backup cannot be restored as if it were complete.

    python scripts/iacode/backup.py
    python scripts/iacode/backup.py --output-dir var/backups --keep 5
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "packages" / "common" / "src"))

from compose import (
    REPOSITORY_ROOT,
    StackError,
    compose,
    exec_in,
    log,
    main_guard,
    read_env_file,
)
from iacode_common.redaction import redact_mapping

DEFAULT_OUTPUT = REPOSITORY_ROOT / "var" / "backups"
MANIFEST_NAME = "manifest.json"
DATABASE_DUMP = "postgres.dump"
OBJECT_DIRECTORY = "minio"


def _timestamp() -> str:
    return datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")


def _digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _directory_digest(directory: Path) -> tuple[str, int, int]:
    """A digest over the directory's contents, its file count and its total size.

    Hashing the relative paths as well as the bytes is what makes the value change when a file is
    renamed or removed, not only when its content changes.
    """
    digest = hashlib.sha256()
    files = 0
    total = 0
    for path in sorted(directory.rglob("*")):
        if not path.is_file():
            continue
        files += 1
        total += path.stat().st_size
        digest.update(str(path.relative_to(directory)).replace("\\", "/").encode("utf-8"))
        digest.update(_digest(path).encode("ascii"))
    return digest.hexdigest(), files, total


def backup_database(destination: Path, values: dict[str, str]) -> dict[str, object]:
    """Dump the IACode database through the running PostgreSQL container."""
    user = values.get("IACODE_POSTGRES_USER", "iacode")
    database = values.get("IACODE_POSTGRES_DB", "iacode")
    log(f"dumping database {database}")
    # --format=custom so the restore can be selective, and because a plain SQL dump is slower to
    # restore for no benefit here.
    #
    # The password is never passed as an argument and never appears in this process. The shell runs
    # *inside* the postgres container, where POSTGRES_PASSWORD is already part of the environment
    # the image was started with, so the credential is read where it already lives.
    result = exec_in(
        "postgres", "sh", "-c",
        f'PGPASSWORD="$POSTGRES_PASSWORD" pg_dump --username="{user}" --dbname="{database}" '
        f'--format=custom --no-owner --no-privileges --file=/tmp/{DATABASE_DUMP}',
    )
    if not result.ok:
        return {"component": "postgres", "status": "FAILED",
                "detail": result.stdout.strip()[-500:] or f"exit {result.exit_code}"}

    target = destination / DATABASE_DUMP
    copy = compose("cp", f"postgres:/tmp/{DATABASE_DUMP}", str(target))
    exec_in("postgres", "rm", "-f", f"/tmp/{DATABASE_DUMP}")
    if not copy.ok or not target.is_file():
        return {"component": "postgres", "status": "FAILED",
                "detail": copy.stdout.strip()[-500:] or "the dump could not be copied out"}

    size = target.stat().st_size
    if size == 0:
        return {"component": "postgres", "status": "FAILED", "detail": "the dump is empty"}
    return {
        "component": "postgres",
        "status": "OK",
        "database": database,
        "file": DATABASE_DUMP,
        "sizeBytes": size,
        "sha256": _digest(target),
    }


def backup_objects(destination: Path, values: dict[str, str]) -> dict[str, object]:
    """Mirror the artifact bucket out of MinIO."""
    bucket = values.get("IACODE_MINIO_BUCKET", "iacode-artifacts")
    log(f"mirroring object storage bucket {bucket}")
    target = destination / OBJECT_DIRECTORY
    target.mkdir(parents=True, exist_ok=True)

    # `mc` runs in its own container on the stack's network. Running it inside the MinIO container
    # would work too, but this keeps the server image free of client tooling.
    result = compose(
        "run", "--rm", "--no-deps", "--entrypoint", "/bin/sh",
        "-v", f"{target.resolve()}:/backup",
        "minio-bootstrap", "-c",
        'mc alias set iacode http://minio:9000 "$MINIO_ROOT_USER" "$MINIO_ROOT_PASSWORD" '
        f'>/dev/null && mc mirror --overwrite --remove "iacode/{bucket}" /backup',
    )
    if not result.ok:
        return {"component": "minio", "status": "FAILED", "bucket": bucket,
                "detail": result.stdout.strip()[-500:] or f"exit {result.exit_code}"}

    checksum, files, size = _directory_digest(target)
    return {
        "component": "minio",
        "status": "OK",
        "bucket": bucket,
        "directory": OBJECT_DIRECTORY,
        "objectCount": files,
        "sizeBytes": size,
        "sha256": checksum,
    }


def prune(output_dir: Path, keep: int) -> list[str]:
    """Delete all but the newest ``keep`` backups.

    Retention is this simple on purpose. `docs/GATE-0-CHECKLIST.md` row 12.5 allows either a simple
    policy or a documented absence; a scheduler, offsite copies and lifecycle rules are an
    operations concern that Gate 0 has no environment to exercise.
    """
    if keep <= 0:
        return []
    candidates = sorted(
        (path for path in output_dir.iterdir()
         if path.is_dir() and (path / MANIFEST_NAME).is_file()),
        key=lambda path: path.name,
    )
    removed: list[str] = []
    for path in candidates[:-keep]:
        shutil.rmtree(path, ignore_errors=True)
        removed.append(path.name)
    return removed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--keep", type=int, default=7,
                        help="how many backups to retain; 0 disables pruning")
    parser.add_argument("--label", default=None, help="suffix for the backup directory name")
    arguments = parser.parse_args()

    values = read_env_file()
    name = _timestamp() + (f"-{arguments.label}" if arguments.label else "")
    destination = (arguments.output_dir / name).resolve()
    if destination.exists():
        raise StackError(f"{destination} already exists")
    destination.mkdir(parents=True)
    log(f"backup directory: {destination}")

    components = [
        backup_database(destination, values),
        backup_objects(destination, values),
    ]
    failed = [item for item in components if item["status"] != "OK"]

    manifest = {
        "schemaVersion": "1.0.0",
        "createdAt": datetime.now(UTC).isoformat(timespec="seconds").replace(
            "+00:00", "Z"),
        "result": "OK" if not failed else "FAILED",
        "stackVersion": values.get("IACODE_VERSION", "unknown"),
        "components": components,
    }
    # Belt and braces: the manifest is written from values that are already non-secret, and it is
    # redacted anyway, because a backup manifest is exactly the sort of file that gets attached to
    # a ticket.
    (destination / MANIFEST_NAME).write_text(
        json.dumps(redact_mapping(manifest), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8", newline="\n")

    for item in components:
        status = item["status"]
        detail = item.get("detail") or ", ".join(
            f"{key}={value}" for key, value in item.items()
            if key in ("database", "bucket", "objectCount", "sizeBytes"))
        log(f"[{status}] {item['component']}: {detail}")

    if failed:
        # Exit non-zero and say so. A partial backup that exited zero is the failure this rule
        # exists to prevent, because it will be trusted the day it is needed.
        print(f"[iacode] FAILED: backup incomplete: "
              f"{', '.join(str(item['component']) for item in failed)}", file=sys.stderr)
        return 1

    removed = prune(arguments.output_dir, arguments.keep)
    if removed:
        log(f"pruned {len(removed)} old backup(s): {', '.join(removed)}")
    log(f"BACKUP=OK path={destination}")
    print(destination)
    return 0


if __name__ == "__main__":
    main_guard(main)
