#!/usr/bin/env python3
"""Run and inspect the database migrations.

The stack already migrates on every start: the `migrate` job runs to completion before the API is
allowed to start. This exists for the times a person needs to do it by hand — inspecting the current
revision during an incident, or applying a new migration without restarting the stack.

    python scripts/iacode/migrate.py upgrade      apply everything outstanding
    python scripts/iacode/migrate.py current      what the database is at
    python scripts/iacode/migrate.py history      what exists to apply
    python scripts/iacode/migrate.py check        does the declared model match the schema?

There is deliberately no `downgrade` here. Reversing a migration against a database that matters is
a decision, not a command, and `alembic downgrade` is available in the container for whoever has
made that decision. The migration's own downgrade path is exercised by the test suite against a
disposable database.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from compose import compose, log, main_guard

COMMANDS = {
    "upgrade": ["alembic", "upgrade", "head"],
    "current": ["alembic", "current", "--verbose"],
    "history": ["alembic", "history", "--verbose"],
    "check": ["alembic", "check"],
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=sorted(COMMANDS))
    arguments = parser.parse_args()

    # A new container of the migrate service rather than an exec into a running one: the job
    # container exits after it succeeds, so there is nothing to exec into.
    result = compose("run", "--rm", "--no-deps", "--entrypoint", "", "migrate",
                     *COMMANDS[arguments.command], capture=False)
    log(f"MIGRATE_{arguments.command.upper()}={'OK' if result.ok else 'FAILED'}")
    return result.exit_code


if __name__ == "__main__":
    main_guard(main)
