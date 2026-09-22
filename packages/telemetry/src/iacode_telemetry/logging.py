"""Structured logging for every IACode process.

One contract, one formatter, every component. A log record is a single line of JSON carrying:

    timestamp  level  service  message

plus whichever of ``traceId``, ``correlationId``, ``requestId``, ``taskId``, ``runId`` and
``agentId`` the ambient context actually holds. **A field with no value is absent**, never null and
never a placeholder: `docs/DEVELOPMENT-CONTRACT.md` forbids inventing an identifier, and a record
that always carries ``"taskId": null`` teaches a reader to ignore the field by the time a Gate
finally gives it meaning.

Every record passes through the redactor on its way out. That is deliberate belt and braces: the
call sites are supposed to keep credentials out of log arguments, and one day one of them will not.
"""

from __future__ import annotations

import json
import logging
import sys
import time
from typing import Any

from iacode_common.redaction import redact_mapping, redact_text

from iacode_telemetry.context import CONTEXT_FIELDS, current_context

__all__ = ["JsonLogFormatter", "configure_logging", "get_logger"]

# Attributes ``logging`` puts on every record. Anything else a caller passed through ``extra`` is
# treated as structured payload and is emitted alongside the contract fields.
_STANDARD_ATTRIBUTES = frozenset({
    "args", "asctime", "created", "exc_info", "exc_text", "filename", "funcName", "levelname",
    "levelno", "lineno", "module", "msecs", "message", "msg", "name", "pathname", "process",
    "processName", "relativeCreated", "stack_info", "stacklevel", "thread", "threadName",
    "taskName",
})


class JsonLogFormatter(logging.Formatter):
    """Render a record as one line of JSON that satisfies the logging contract."""

    def __init__(self, service: str, version: str | None = None) -> None:
        super().__init__()
        self.service = service
        self.version = version

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": self._timestamp(record),
            "level": record.levelname,
            "service": self.service,
            "message": redact_text(record.getMessage()),
        }
        if self.version:
            payload["version"] = self.version

        context = current_context()
        for field in CONTEXT_FIELDS:
            value = getattr(record, field, None) or context.get(field)
            if value:
                payload[field] = str(value)

        extra = {
            key: value for key, value in record.__dict__.items()
            if key not in _STANDARD_ATTRIBUTES and key not in CONTEXT_FIELDS
            and not key.startswith("_")
        }
        if extra:
            payload["context"] = redact_mapping(extra)

        payload["logger"] = record.name
        if record.exc_info:
            # The type and the message stay; the traceback is the operator's, and it is written
            # here rather than returned to a client. See apps/api/src/iacode_api/errors.py.
            payload["error"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else "Exception",
                "message": redact_text(str(record.exc_info[1])),
                "traceback": redact_text(self.formatException(record.exc_info)),
            }
        return json.dumps(payload, ensure_ascii=False, default=str)

    @staticmethod
    def _timestamp(record: logging.LogRecord) -> str:
        base = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(record.created))
        return f"{base}.{int(record.msecs):03d}Z"


def configure_logging(service: str, level: str = "INFO", version: str | None = None) -> None:
    """Install the JSON formatter as the only handler of the root logger.

    Existing handlers are replaced rather than added to. Uvicorn and Alembic both install their own
    handlers, and leaving them in place produces every line twice: once as JSON and once as
    whatever that library prints.
    """
    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(JsonLogFormatter(service=service, version=version))

    root = logging.getLogger()
    for existing in list(root.handlers):
        root.removeHandler(existing)
    root.addHandler(handler)
    root.setLevel(level.upper())

    for name in ("uvicorn", "uvicorn.error", "uvicorn.access", "alembic", "sqlalchemy.engine"):
        logger = logging.getLogger(name)
        logger.handlers.clear()
        logger.propagate = True


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
