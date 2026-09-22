#!/usr/bin/env python3
"""The restart scenario: the stack comes back, and it comes back with its data.

`docs/GATE-0-CHECKLIST.md` rows 10.4 and 13.6. Two claims, and the second is the one that fails
quietly: a service can restart perfectly while its state lives in the container's own filesystem,
and nobody notices until the day the container is recreated rather than restarted.

    write a marker row and a marker object
      -> restart every service
      -> wait for real health
      -> read the markers back
      -> confirm the migration did not run again
      -> clean up the markers

Non-destructive: it only adds and removes its own markers.

    python scripts/iacode/scenarios/restart.py
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from compose import compose, log, main_guard, read_env_file
from stack import restart


def psql(database: str, user: str, sql: str) -> tuple[bool, str]:
    result = compose(
        "exec", "-T", "postgres", "sh", "-c",
        f'PGPASSWORD="$POSTGRES_PASSWORD" psql --username="{user}" --dbname="{database}" '
        f"--set=ON_ERROR_STOP=1 --tuples-only --no-align -c {json.dumps(sql)}",
        merge_stderr=False)
    return result.ok, result.stdout.strip() if result.ok else result.output.strip()[-300:]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--json", action="store_true")
    arguments = parser.parse_args()

    values = read_env_file()
    user = values.get("IACODE_POSTGRES_USER", "iacode")
    database = values.get("IACODE_POSTGRES_DB", "iacode")
    bucket = values.get("IACODE_MINIO_BUCKET", "iacode-artifacts")

    marker = uuid.uuid4().hex[:12]
    slug = f"restart-check-{marker}"
    object_key = f"restart-check/{marker}.txt"
    steps: list[dict[str, object]] = []

    def record(name: str, ok: bool, detail: str) -> None:
        steps.append({"step": name, "ok": ok, "detail": detail})
        log(f"[{'OK' if ok else 'FAILED'}] {name}: {detail}")

    started = time.monotonic()
    try:
        ok, _ = psql(database, user,
                     "INSERT INTO projects (id, slug, name, created_at, updated_at, version, "
                     f"metadata) VALUES (gen_random_uuid(), '{slug}', 'Restart {marker}', now(), "
                     "now(), 1, '{}'::jsonb)")
        object_written = compose(
            "run", "--rm", "--no-deps", "--entrypoint", "/bin/sh", "minio-bootstrap", "-c",
            'mc alias set iacode http://minio:9000 "$MINIO_ROOT_USER" "$MINIO_ROOT_PASSWORD" '
            f'>/dev/null && echo "{marker}" | mc pipe "iacode/{bucket}/{object_key}"')
        record("markers_written", ok and object_written.ok,
               f"project {slug} and object {object_key}")

        before, revision_before = psql(database, user, "SELECT version_num FROM alembic_version")
        record("revision_before", before, f"alembic_version={revision_before!r}")

        log("restarting every service")
        restart(wait=True)
        record("stack_recovered", True,
               f"every service healthy again in {time.monotonic() - started:.0f}s")

        ok, name = psql(database, user, f"SELECT name FROM projects WHERE slug = '{slug}'")
        record("database_persisted", ok and name == f"Restart {marker}", f"read back {name!r}")

        object_survived = compose(
            "run", "--rm", "--no-deps", "--entrypoint", "/bin/sh", "minio-bootstrap", "-c",
            'mc alias set iacode http://minio:9000 "$MINIO_ROOT_USER" "$MINIO_ROOT_PASSWORD" '
            f'>/dev/null && mc stat "iacode/{bucket}/{object_key}"')
        record("objects_persisted", object_survived.ok,
               "the object survived the restart" if object_survived.ok
               else object_survived.output.strip()[-200:])

        ok, revision_after = psql(database, user, "SELECT version_num FROM alembic_version")
        # The same revision, not merely *a* revision: a restart that re-ran the migration would
        # also leave a revision here, and the schema would have been rebuilt underneath the data.
        record("migration_not_repeated", ok and revision_after == revision_before,
               f"alembic_version={revision_after!r}")

        ready = compose("exec", "-T", "api", "python", "-c",
                        "import urllib.request,json;"
                        "print(json.load(urllib.request.urlopen("
                        "'http://127.0.0.1:8000/ready', timeout=10))['status'])",
                        merge_stderr=False)
        record("readiness_recovered", ready.ok and ready.stdout.strip() == "READY",
               f"readiness={ready.stdout.strip() or ready.output.strip()[-200:]!r}")
    finally:
        psql(database, user, f"DELETE FROM projects WHERE slug = '{slug}'")
        compose("run", "--rm", "--no-deps", "--entrypoint", "/bin/sh", "minio-bootstrap", "-c",
                'mc alias set iacode http://minio:9000 "$MINIO_ROOT_USER" "$MINIO_ROOT_PASSWORD" '
                f'>/dev/null && mc rm --force "iacode/{bucket}/{object_key}" '
                '>/dev/null 2>&1 || true')

    failed = [step for step in steps if not step["ok"]]
    elapsed = time.monotonic() - started
    if arguments.json:
        print(json.dumps({
            "scenario": "restart",
            "result": "PASS" if not failed else "FAIL",
            "durationSeconds": round(elapsed, 1),
            "steps": steps,
        }, indent=2))
    log(f"RESTART={'PASS' if not failed else 'FAIL'} "
        f"{len(steps) - len(failed)}/{len(steps)} steps in {elapsed:.0f}s")
    return 0 if not failed else 1


if __name__ == "__main__":
    main_guard(main)
