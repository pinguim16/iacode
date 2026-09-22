"""The IACode system of record.

The schema lives here rather than inside the web application because more than one process reads
it. The API accepts a task and answers questions about a run; the Temporal worker executes that run
and records what happened. Two ORM definitions of the same tables would drift, and the drift would
surface as a constraint violation in whichever process was edited second —
`.iacode/memory/lessons.jsonl` records exactly that failure class.

The package depends on SQLAlchemy and on nothing else of ours except the identifier generator and
the shared vocabulary. It knows nothing about FastAPI, about a request, or about a Temporal
workflow, so both consumers can depend on it without inheriting the other.

Alembic still lives with the API, because a migration directory belongs to one deployable unit and
the API is the one that runs it. ``migrations/env.py`` reads this package's metadata.
"""

from iacode_persistence.base import (
    Base,
    IdentifiedEntity,
    ImmutableRecord,
    TimestampedEntity,
)

__all__ = [
    "Base",
    "IdentifiedEntity",
    "ImmutableRecord",
    "TimestampedEntity",
]
