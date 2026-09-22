#!/usr/bin/env python3
"""Restore the Foundation's durable state from a backup.

A backup that has never been restored is a hope, not a backup. This is the other half, and it is
what `docs/GATE-0-CHECKLIST.md` row 12.3 requires before the backup counts for anything.

The restore reads the manifest and refuses a backup the manifest describes as incomplete, so a
half-finished backup cannot be restored as if it were whole. It also verifies the recorded
checksums before touching anything: restoring a corrupted dump over a working database is a way to
turn one problem into two.

**This is destructive.** It drops and recreates the target database and mirrors the object storage
over the bucket, so ``--yes`` is required and the target database can be overridden to keep a
verification run away from the real one.

    python scripts/iacode/restore.py var/backups/20260921T203000Z --yes
    python scripts/iacode/restore.py <path> --database iacode_restore_check --yes
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from backup import (
    DATABASE_DUMP,
    MANIFEST_NAME,
    OBJECT_DIRECTORY,
    _digest,
    _directory_digest,
)
from compose import StackError, compose, exec_in, log, main_guard, read_env_file


def load_manifest(path: Path) -> dict:
    manifest_path = path / MANIFEST_NAME
    if not manifest_path.is_file():
        raise StackError(f"{path} carries no {MANIFEST_NAME}; it is not a backup this tool wrote")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("result") != "OK":
        raise StackError(
            f"{path.name} records result={manifest.get('result')!r}; an incomplete backup is not "
            f"restorable and pretending otherwise is how a partial recovery is mistaken for a "
            f"full one")
    return manifest


def verify(path: Path, manifest: dict) -> None:
    """Check the recorded checksums before anything is overwritten."""
    for component in manifest.get("components", []):
        if component.get("component") == "postgres":
            dump = path / str(component.get("file", DATABASE_DUMP))
            if not dump.is_file():
                raise StackError(f"the manifest names {dump.name} but the file is missing")
            actual = _digest(dump)
            if actual != component.get("sha256"):
                raise StackError(
                    f"{dump.name} does not match its recorded checksum; the backup is corrupt")
        elif component.get("component") == "minio":
            directory = path / str(component.get("directory", OBJECT_DIRECTORY))
            if not directory.is_dir():
                raise StackError(
                    f"the manifest names {directory.name}, which is missing")
            checksum, files, _size = _directory_digest(directory)
            if checksum != component.get("sha256"):
                raise StackError(
                    f"{directory.name} does not match its recorded checksum; the backup is corrupt")
            if files != component.get("objectCount"):
                raise StackError(
                    f"{directory.name} holds {files} object(s), the manifest records "
                    f"{component.get('objectCount')}")
    log("every recorded checksum matches")


def restore_database(path: Path, database: str, values: dict[str, str]) -> None:
    user = values.get("IACODE_POSTGRES_USER", "iacode")
    dump = path / DATABASE_DUMP
    log(f"restoring database {database}")

    copy = compose("cp", str(dump), f"postgres:/tmp/{DATABASE_DUMP}")
    if not copy.ok:
        raise StackError(f"the dump could not be copied into the container: {copy.stdout.strip()}")

    # Terminate first. DROP DATABASE fails while any session is connected, and the API holds a
    # pool open: without this the restore fails with a message about other users that reads like a
    # permissions problem.
    result = exec_in(
        "postgres", "sh", "-c",
        f'PGPASSWORD="$POSTGRES_PASSWORD" psql --username="{user}" --dbname=postgres '
        f'--set=ON_ERROR_STOP=1 -c '
        f'"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = \'{database}\' '
        f'AND pid <> pg_backend_pid()" '
        f'-c "DROP DATABASE IF EXISTS \\"{database}\\"" '
        f'-c "CREATE DATABASE \\"{database}\\""',
    )
    if not result.ok:
        raise StackError(f"the target database could not be recreated: {result.stdout.strip()}")

    result = exec_in(
        "postgres", "sh", "-c",
        f'PGPASSWORD="$POSTGRES_PASSWORD" pg_restore --username="{user}" '
        f'--dbname="{database}" --no-owner --no-privileges --exit-on-error /tmp/{DATABASE_DUMP}',
    )
    exec_in("postgres", "rm", "-f", f"/tmp/{DATABASE_DUMP}")
    if not result.ok:
        raise StackError(f"pg_restore failed: {result.stdout.strip()[-800:]}")
    log(f"database {database} restored")


def restore_objects(path: Path, bucket: str) -> None:
    source = (path / OBJECT_DIRECTORY).resolve()
    log(f"restoring object storage bucket {bucket}")
    result = compose(
        "run", "--rm", "--no-deps", "--entrypoint", "/bin/sh",
        "-v", f"{source}:/backup:ro",
        "minio-bootstrap", "-c",
        'mc alias set iacode http://minio:9000 "$MINIO_ROOT_USER" "$MINIO_ROOT_PASSWORD" '
        f'>/dev/null && mc mb --ignore-existing "iacode/{bucket}" >/dev/null && '
        f'mc mirror --overwrite --remove /backup "iacode/{bucket}"',
    )
    if not result.ok:
        raise StackError(f"the object storage restore failed: {result.stdout.strip()[-800:]}")
    log(f"bucket {bucket} restored")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("backup", type=Path, help="the backup directory to restore")
    parser.add_argument("--database", default=None,
                        help="restore into this database instead of the configured one")
    parser.add_argument("--bucket", default=None,
                        help="restore into this bucket instead of the configured one")
    parser.add_argument("--skip-objects", action="store_true",
                        help="restore only the database")
    parser.add_argument("--yes", action="store_true",
                        help="required: the restore overwrites the target database and bucket")
    arguments = parser.parse_args()

    path = arguments.backup.resolve()
    if not path.is_dir():
        raise StackError(f"{path} is not a directory")

    values = read_env_file()
    database = arguments.database or values.get("IACODE_POSTGRES_DB", "iacode")
    bucket = arguments.bucket or values.get("IACODE_MINIO_BUCKET", "iacode-artifacts")

    if not arguments.yes:
        raise StackError(
            f"this would drop and recreate the database {database!r}"
            + ("" if arguments.skip_objects else f" and overwrite the bucket {bucket!r}")
            + ". Re-run with --yes if that is what you want.")

    manifest = load_manifest(path)
    verify(path, manifest)
    restore_database(path, database, values)
    if not arguments.skip_objects:
        restore_objects(path, bucket)

    log(f"RESTORE=OK database={database}"
        + ("" if arguments.skip_objects else f" bucket={bucket}"))
    return 0


if __name__ == "__main__":
    main_guard(main)
