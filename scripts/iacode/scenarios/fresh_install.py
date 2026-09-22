#!/usr/bin/env python3
"""The fresh-installation scenario: nothing on disk, to a working stack.

This is the claim `docs/GATE-0-CHECKLIST.md` row 13.5 and the Gate's definition of done actually
make — that a new machine reaches a working Foundation from this repository alone. It is the one
scenario that cannot be approximated, because every interesting failure of a first installation is a
failure of *ordering*: a service that starts before its schema exists, a bucket nothing created, a
migration that assumed a table was already there.

    stop and delete every volume
      -> start
      -> wait for real health
      -> confirm the schema was created from zero
      -> run the full smoke check
      -> report

**This deletes every volume**, which is what "fresh" means, so it requires ``--yes``. It is meant
for a development machine and for the verification run; it is not a procedure to point at anything
whose data matters.

    python scripts/iacode/scenarios/fresh_install.py --yes
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from compose import (
    REPOSITORY_ROOT,
    StackError,
    compose,
    log,
    main_guard,
    read_env_file,
)
from stack import down, up


def volume_names() -> list[str]:
    result = compose("config", "--volumes")
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def run_smoke() -> tuple[bool, str]:
    completed = subprocess.run(
        [sys.executable, str(REPOSITORY_ROOT / "scripts" / "iacode" / "smoke.py"), "--json"],
        cwd=str(REPOSITORY_ROOT), text=True, encoding="utf-8", errors="replace",
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    payload = None
    for line in completed.stdout.splitlines():
        if line.strip().startswith("{"):
            try:
                payload = json.loads(completed.stdout[completed.stdout.index(line):])
            except json.JSONDecodeError:
                payload = None
            break
    if payload is None:
        return False, completed.stdout.strip()[-400:]
    return (payload.get("result") == "PASS",
            f"{payload.get('passed')}/{payload.get('total')} smoke checks")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--yes", action="store_true",
                        help="required: this deletes every volume before starting")
    parser.add_argument("--json", action="store_true")
    arguments = parser.parse_args()

    if not arguments.yes:
        raise StackError(
            "the fresh-installation scenario deletes every volume, including the database and the "
            "object storage. Re-run with --yes.")

    values = read_env_file()
    database = values.get("IACODE_POSTGRES_DB", "iacode")
    user = values.get("IACODE_POSTGRES_USER", "iacode")
    steps: list[dict[str, object]] = []

    def record(name: str, ok: bool, detail: str) -> None:
        steps.append({"step": name, "ok": ok, "detail": detail})
        log(f"[{'OK' if ok else 'FAILED'}] {name}: {detail}")

    started = time.monotonic()

    log("removing every volume")
    down(remove_volumes=True)
    # Asking Docker, not Compose: "the volume is gone" is a fact about the engine, and a command
    # that exited zero is not evidence that it removed anything.
    remaining = [name for name in volume_names() if _volume_exists(name, values)]
    record("volumes_removed", not remaining,
           "no volume survived the reset" if not remaining
           else f"still present: {', '.join(remaining)}")

    log("starting the stack from nothing")
    up(build=False, wait=True)
    record("stack_healthy", True, f"every service healthy in {time.monotonic() - started:.0f}s")

    # The migration ran as part of start-up. Asking the database directly is the only way to know
    # it produced a schema rather than merely exiting zero.
    result = compose(
        "exec", "-T", "postgres", "sh", "-c",
        f'PGPASSWORD="$POSTGRES_PASSWORD" psql --username="{user}" --dbname="{database}" '
        f"--tuples-only --no-align -c \"SELECT count(*) FROM information_schema.tables "
        f"WHERE table_schema = 'public'\"",
        merge_stderr=False)
    tables = result.stdout.strip()
    record("schema_created_from_zero", result.ok and tables.isdigit() and int(tables) >= 13,
           f"{tables} table(s) in the public schema")

    result = compose(
        "exec", "-T", "postgres", "sh", "-c",
        f'PGPASSWORD="$POSTGRES_PASSWORD" psql --username="{user}" --dbname="{database}" '
        f'--tuples-only --no-align -c "SELECT version_num FROM alembic_version"',
        merge_stderr=False)
    record("migration_recorded", result.stdout.strip() == "0001_foundation",
           f"alembic_version={result.stdout.strip()!r}")

    ok, detail = run_smoke()
    record("smoke", ok, detail)

    failed = [step for step in steps if not step["ok"]]
    elapsed = time.monotonic() - started
    if arguments.json:
        print(json.dumps({
            "scenario": "fresh_install",
            "result": "PASS" if not failed else "FAIL",
            "durationSeconds": round(elapsed, 1),
            "steps": steps,
        }, indent=2))
    log(f"FRESH_INSTALL={'PASS' if not failed else 'FAIL'} "
        f"{len(steps) - len(failed)}/{len(steps)} steps in {elapsed:.0f}s")
    return 0 if not failed else 1


def _volume_exists(name: str, values: dict[str, str]) -> bool:
    project = values.get("COMPOSE_PROJECT_NAME", "iacode")
    completed = subprocess.run(
        ["docker", "volume", "inspect", f"{project}_{name}"],
        text=True, encoding="utf-8", errors="replace",
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
    return completed.returncode == 0


if __name__ == "__main__":
    main_guard(main)
