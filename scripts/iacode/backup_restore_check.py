#!/usr/bin/env python3
"""Prove that a backup can be restored, with data that is checked rather than assumed.

`docs/GATE-0-CHECKLIST.md` row 12.4: backup does not pass without restore, and restore does not
pass unless the restored data is verified.

The cycle:

    write synthetic rows and objects
      -> back up
      -> destroy the copy that was backed up
      -> restore into a disposable database and bucket
      -> read the synthetic data back and compare it
      -> clean up whatever this run created

**Nothing real is destroyed.** The restore targets a database and a bucket created for this run and
dropped afterwards, so the check can run against a live stack without being a risk to it. Restoring
over the working database would make this the sort of check nobody dares to run, which is the same
as not having one.

    python scripts/iacode/backup_restore_check.py
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import uuid
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from compose import (
    REPOSITORY_ROOT,
    StackError,
    compose,
    log,
    main_guard,
    read_env_file,
)

WORK_ROOT = REPOSITORY_ROOT / "var" / "backup-check"


def _psql(database: str, sql: str, user: str) -> str:
    """Run one statement and return exactly what it printed, raising on failure."""
    result = compose(
        "exec", "-T", "postgres", "sh", "-c",
        f'PGPASSWORD="$POSTGRES_PASSWORD" psql --username="{user}" --dbname="{database}" '
        f'--set=ON_ERROR_STOP=1 --tuples-only --no-align -c {json.dumps(sql)}',
        merge_stderr=False,
    )
    if not result.ok:
        raise StackError(f"psql failed against {database}: {result.output.strip()[-500:]}")
    return result.stdout.strip()


def _mc(script: str, mounts: list[str] | None = None) -> None:
    """Run an `mc` script against the stack's MinIO.

    It returns nothing on purpose. ``docker compose run`` writes its own container lifecycle
    narration to **stdout**, mixed in with whatever the container prints, so the output of a
    command run this way is not a value that can be compared against anything: reading an object
    back through ``mc cat`` produced four hundred bytes of "Container ... Running" followed by the
    content. Data comes out through a mounted file instead, which is exact.
    """
    arguments = ["run", "--rm", "--no-deps", "--entrypoint", "/bin/sh"]
    for mount in mounts or []:
        arguments += ["-v", mount]
    result = compose(
        *arguments, "minio-bootstrap", "-c",
        'mc alias set iacode http://minio:9000 "$MINIO_ROOT_USER" "$MINIO_ROOT_PASSWORD" '
        f">/dev/null && {script}",
    )
    if not result.ok:
        raise StackError(f"the object storage command failed: {result.output.strip()[-500:]}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--keep-artifacts", action="store_true",
                        help="do not delete the backup this check produced")
    parser.add_argument("--json", action="store_true")
    arguments = parser.parse_args()

    values = read_env_file()
    user = values.get("IACODE_POSTGRES_USER", "iacode")
    database = values.get("IACODE_POSTGRES_DB", "iacode")
    bucket = values.get("IACODE_MINIO_BUCKET", "iacode-artifacts")

    marker = uuid.uuid4().hex[:12]
    slug = f"backup-check-{marker}"
    object_key = f"backup-check/{marker}.txt"
    object_body = f"iacode-backup-check-{marker}"
    restore_database = f"iacode_restore_check_{marker}"
    restore_bucket = f"iacode-restore-check-{marker}"
    workdir = WORK_ROOT / marker
    steps: list[dict[str, object]] = []

    def record(name: str, ok: bool, detail: str) -> None:
        steps.append({"step": name, "ok": ok, "detail": detail})
        log(f"[{'OK' if ok else 'FAILED'}] {name}: {detail}")
        if not ok:
            raise StackError(f"{name}: {detail}")

    try:
        WORK_ROOT.mkdir(parents=True, exist_ok=True)
        workdir.mkdir(parents=True)

        # 1. Synthetic data, written through the same database and bucket the stack uses.
        _psql(database,
              f"INSERT INTO projects (id, slug, name, created_at, updated_at, version, metadata) "
              f"VALUES (gen_random_uuid(), '{slug}', 'Backup check {marker}', now(), now(), 1, "
              f"'{{}}'::jsonb)", user)
        (workdir / "object.txt").write_text(object_body, encoding="utf-8", newline="\n")
        _mc(f'mc cp /work/object.txt "iacode/{bucket}/{object_key}"',
            mounts=[f"{workdir.resolve()}:/work"])
        record("seed", True, f"project {slug} and object {object_key} written")

        # 2. Back up.
        from backup import backup_database, backup_objects

        backup_directory = workdir / "backup"
        backup_directory.mkdir()
        database_result = backup_database(backup_directory, values)
        objects_result = backup_objects(backup_directory, values)
        manifest = {
            "schemaVersion": "1.0.0",
            "createdAt": datetime.now(UTC).isoformat(timespec="seconds").replace(
                "+00:00", "Z"),
            "result": "OK" if all(item["status"] == "OK"
                                  for item in (database_result, objects_result)) else "FAILED",
            "stackVersion": values.get("IACODE_VERSION", "unknown"),
            "components": [database_result, objects_result],
        }
        (backup_directory / "manifest.json").write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8", newline="\n")
        record("backup", manifest["result"] == "OK",
               f"database={database_result['status']} objects={objects_result['status']}")

        # 3. Destroy what was backed up, so the restore has something to prove.
        _psql(database, f"DELETE FROM projects WHERE slug = '{slug}'", user)
        _mc(f'mc rm "iacode/{bucket}/{object_key}"')
        remaining = _psql(database, f"SELECT count(*) FROM projects WHERE slug = '{slug}'", user)
        record("destroy", remaining == "0", f"{remaining} row(s) remain in the live database")

        # 4. Restore into a disposable database and bucket.
        from restore import restore_database as do_restore_database
        from restore import restore_objects, verify

        verify(backup_directory, manifest)
        do_restore_database(backup_directory, restore_database, values)
        restore_objects(backup_directory, restore_bucket)
        record("restore", True, f"into {restore_database} and {restore_bucket}")

        # 5. Verify the restored content, which is the whole point.
        restored_rows = _psql(
            restore_database, f"SELECT name FROM projects WHERE slug = '{slug}'", user)
        record("verify.database", restored_rows == f"Backup check {marker}",
               f"read back {restored_rows!r}")

        readback = workdir / "readback"
        readback.mkdir(exist_ok=True)
        _mc(f'mc cp "iacode/{restore_bucket}/{object_key}" /readback/object.txt',
            mounts=[f"{readback.resolve()}:/readback"])
        restored_object = (readback / "object.txt").read_text(encoding="utf-8")
        record("verify.objects", restored_object == object_body,
               f"read back {len(restored_object)} byte(s): {restored_object[:60]!r}")

        # The live copies must still be gone: a check that silently restored over the working
        # database would report success while having done the destructive thing it promises not to.
        live_rows = _psql(database, f"SELECT count(*) FROM projects WHERE slug = '{slug}'", user)
        record("live_untouched", live_rows == "0",
               f"the live database still has {live_rows} matching row(s)")
    finally:
        # Clean up whatever this run created, whether or not it succeeded.
        try:
            _psql("postgres",
                  "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
                  f"WHERE datname = '{restore_database}' AND pid <> pg_backend_pid()", user)
            _psql("postgres", f'DROP DATABASE IF EXISTS "{restore_database}"', user)
        except StackError as error:
            log(f"could not drop {restore_database}: {error}")
        try:
            _mc(f'mc rb --force "iacode/{restore_bucket}" >/dev/null || true')
        except StackError as error:
            log(f"could not remove {restore_bucket}: {error}")
        try:
            _psql(database, f"DELETE FROM projects WHERE slug = '{slug}'", user)
            _mc(f'mc rm --force "iacode/{bucket}/{object_key}" >/dev/null 2>&1 || true')
        except StackError:
            pass
        if not arguments.keep_artifacts and workdir.exists():
            shutil.rmtree(workdir, ignore_errors=True)

    if arguments.json:
        print(json.dumps({"result": "PASS", "steps": steps}, indent=2))
    log(f"BACKUP_RESTORE=PASS {len(steps)} step(s)")
    return 0


if __name__ == "__main__":
    main_guard(main)
