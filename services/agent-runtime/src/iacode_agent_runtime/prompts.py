"""Versioned prompt templates, loaded from files rather than assembled out of scattered strings.

A prompt is behaviour. A prompt built by concatenating fragments across three modules is behaviour
nobody can read in one place and nobody can diff, and a run that behaved oddly cannot be reproduced
because there is no artefact to point at. So a template is a file, its name carries its version,
and an agent run records the hash of the exact bytes that produced it.

The version is **derived from the file name** — ``planner.v2.md`` is version ``v2`` — rather than
declared beside the path. Declaring it twice is how a template gets edited without its version
changing, and `.iacode/memory/lessons.jsonl` records that class of duplicate classification.

Templates take named placeholders in ``{name}`` form and nothing else. There is no expression
language, no conditional and no include: a prompt that can compute is a prompt that can be made to
compute something its author did not read.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path

from iacode_agent_runtime.errors import AgentRuntimeError, AgentRuntimeErrorType

__all__ = ["PromptTemplate", "load_template", "template_version"]

#: ``<name>.<version>.md``. The version is part of the identity of the file, so renaming it is a
#: visible change and editing the body without renaming is caught by the hash instead.
TEMPLATE_NAME = re.compile(r"^(?P<name>[a-z0-9-]+)\.(?P<version>v[0-9]+)\.md$")

#: A placeholder, in the only form a template may use.
PLACEHOLDER = re.compile(r"\{([a-zA-Z_][a-zA-Z0-9_]*)\}")


def template_version(path: Path | str) -> str:
    """The version a template file name declares."""
    match = TEMPLATE_NAME.match(Path(str(path)).name)
    if match is None:
        raise AgentRuntimeError(
            AgentRuntimeErrorType.INVALID_REQUEST,
            f"a prompt template is named '<role>.<version>.md'; {Path(str(path)).name!r} is not",
            details={"template": str(path)})
    return match.group("version")


@dataclass(frozen=True)
class PromptTemplate:
    """One template: where it came from, which version it is, and the hash of its bytes."""

    path: str
    version: str
    content_hash: str
    body: str

    @property
    def placeholders(self) -> tuple[str, ...]:
        return tuple(sorted(set(PLACEHOLDER.findall(self.body))))

    def render(self, **values: str) -> str:
        """Fill the placeholders, refusing anything the template did not ask for.

        Both directions are checked. A missing value would render a literal ``{task}`` into a
        prompt, and an extra one usually means a caller renamed a placeholder in the template and
        not at the call site — which would otherwise be a silent no-op.
        """
        required = set(self.placeholders)
        supplied = set(values)
        if required - supplied:
            raise AgentRuntimeError(
                AgentRuntimeErrorType.INTERNAL_AGENT_RUNTIME_ERROR,
                f"prompt template {self.path} needs "
                f"{', '.join(sorted(required - supplied))} and it was not supplied",
                details={"template": self.path})
        if supplied - required:
            raise AgentRuntimeError(
                AgentRuntimeErrorType.INTERNAL_AGENT_RUNTIME_ERROR,
                f"prompt template {self.path} was given "
                f"{', '.join(sorted(supplied - required))}, which it does not use",
                details={"template": self.path})
        rendered = self.body
        for name, value in values.items():
            rendered = rendered.replace("{" + name + "}", value)
        return rendered


def load_template(root: Path, relative: str) -> PromptTemplate:
    """Read a template from the repository, refusing a path that escapes the root.

    The containment check is not theoretical. ``promptTemplate`` comes from a profile file, and a
    profile that named ``../../infra/compose/.env`` would otherwise make the runtime read a
    credential into a prompt.
    """
    candidate = (root / relative).resolve()
    base = root.resolve()
    if base != candidate and base not in candidate.parents:
        raise AgentRuntimeError(
            AgentRuntimeErrorType.INVALID_REQUEST,
            "a prompt template must live inside the repository",
            details={"template": relative})
    if not candidate.is_file():
        raise AgentRuntimeError(
            AgentRuntimeErrorType.PROFILE_NOT_FOUND,
            f"prompt template {relative} does not exist",
            details={"template": relative})
    body = candidate.read_text(encoding="utf-8")
    if not body.strip():
        raise AgentRuntimeError(
            AgentRuntimeErrorType.INVALID_REQUEST,
            f"prompt template {relative} is empty",
            details={"template": relative})
    return PromptTemplate(
        path=str(relative).replace("\\", "/"),
        version=template_version(relative),
        content_hash=hashlib.sha256(body.encode("utf-8")).hexdigest(),
        body=body,
    )
