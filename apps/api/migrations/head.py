"""Which revision the migration directory declares as head, read rather than written down.

One definition, next to the thing it describes, because more than one consumer needs the answer:
the integration suite asserts the migrated schema is at head, and the fresh-installation scenario
asserts a database created from nothing records it. Both used to carry a literal, and a literal
describes whichever migration was newest on the day it was typed — so the next migration fails a
check about something else entirely. `.iacode/memory/lessons.jsonl` records that failure class.

Standard library only, and no Alembic import: the scenario runs on the host, where Alembic is not
installed, and the suite runs inside the image, where it is. A module that needed the framework
would be a module only one of them could use.
"""

from __future__ import annotations

import re
from pathlib import Path

__all__ = ["head_revision", "revision_graph"]

_REVISION = re.compile(r'^revision: str = "([^"]+)"', re.MULTILINE)
_DOWN_REVISION = re.compile(r'^down_revision: str \| None = (?:"([^"]+)"|None)', re.MULTILINE)


def revision_graph(versions: Path) -> dict[str, str | None]:
    """Every declared revision, mapped to the revision it follows."""
    revisions: dict[str, str | None] = {}
    for path in sorted(versions.glob("*.py")):
        if path.name.startswith("__"):
            continue
        text = path.read_text(encoding="utf-8")
        identifier = _REVISION.search(text)
        if not identifier:
            continue
        parent = _DOWN_REVISION.search(text)
        revisions[identifier.group(1)] = parent.group(1) if parent else None
    return revisions


def head_revision(versions: Path | None = None) -> str:
    """The one revision nothing else follows.

    Raises rather than guessing when the directory declares no head or more than one: a branched
    migration history is a real problem, and returning one of the branches would hide it.
    """
    versions = versions or (Path(__file__).resolve().parent / "versions")
    revisions = revision_graph(versions)
    if not revisions:
        raise ValueError(f"no migration declares a revision under {versions}")
    parents = {parent for parent in revisions.values() if parent}
    heads = sorted(identifier for identifier in revisions if identifier not in parents)
    if len(heads) != 1:
        raise ValueError(f"the migration directory declares {len(heads)} heads: {heads}")
    return heads[0]
