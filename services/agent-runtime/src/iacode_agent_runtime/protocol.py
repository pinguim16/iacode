"""The agent turn protocol: what an agent is allowed to answer, and how it is read.

One turn produces exactly one envelope, and an envelope is exactly one of three kinds:

``FINAL``          the agent has an answer and the stage is over.
``MESSAGE``        the agent has something to say and wants another turn.
``TOOL_REQUEST``   the agent wants a tool. Gate 2 persists the request and pauses; it executes
                   nothing, and the tool name is never resolved to a command.

The envelope carries a version. A consumer that has to discover an incompatible change by crashing
is a consumer that will discover it in production, which is the same argument the gateway's
contract makes for its own version.

**The parser is strict.** It reads exactly one JSON object, optionally wrapped in a single fenced
block because that is what a model trained on chat markup emits, and it refuses everything else:
prose around the object, two objects, an unknown kind, a missing field, a tool request with no name.
An envelope that is "nearly right" is refused, because the alternative — accepting a partial answer
and filling in what is missing — is the runtime inventing the agent's decision.

**The repair path is bounded and honest.** When a turn does not conform, the engine may ask once
more, through the gateway, with :func:`repair_instruction` appended. That call counts against the
budget and is recorded as a repair. A second invalid answer fails the run; there is no third
attempt and no loop.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from iacode_agent_runtime.errors import InvalidAgentOutputError

__all__ = [
    "ENVELOPE_VERSION",
    "AgentEnvelope",
    "EnvelopeKind",
    "ToolRequestIntent",
    "envelope_schema",
    "parse_envelope",
    "repair_instruction",
]

#: The version of this protocol. It changes when an agent or a consumer would have to change too.
ENVELOPE_VERSION = "agent-envelope/1.0"

#: One fenced block, with or without a language tag. Nothing else is unwrapped.
FENCED = re.compile(r"^\s*```[a-zA-Z0-9_-]*\s*\n(?P<body>.*?)\n?\s*```\s*$", re.DOTALL)

#: Longest a summary may be. A summary is a short verifiable statement of what happened, not a
#: narrative, and certainly not a place to put reasoning the runtime has said it will not store.
MAX_SUMMARY = 400


class EnvelopeKind(StrEnum):
    """What an agent answered with."""

    FINAL = "FINAL"
    MESSAGE = "MESSAGE"
    TOOL_REQUEST = "TOOL_REQUEST"


@dataclass(frozen=True)
class ToolRequestIntent:
    """A tool an agent asked for, as it came off the model. Nothing has validated it against a
    policy yet and nothing has executed it."""

    name: str
    arguments: dict[str, Any]


@dataclass(frozen=True)
class AgentEnvelope:
    """One parsed turn."""

    kind: EnvelopeKind
    version: str = ENVELOPE_VERSION
    content: str = ""
    summary: str = ""
    tool: ToolRequestIntent | None = None

    @property
    def is_final(self) -> bool:
        return self.kind is EnvelopeKind.FINAL

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {"version": self.version, "kind": str(self.kind)}
        if self.kind is EnvelopeKind.TOOL_REQUEST and self.tool is not None:
            payload["tool"] = {"name": self.tool.name, "arguments": dict(self.tool.arguments)}
        else:
            payload["content"] = self.content
        if self.summary:
            payload["summary"] = self.summary
        return payload


def envelope_schema() -> dict[str, Any]:
    """The JSON Schema of the envelope.

    Used two ways from one definition: as the structured-output schema when a model declares the
    capability, and as the documentation of what the prompt asks for when it does not. A second
    schema written into the prompt text would be a second thing to keep in step.
    """
    return {
        "type": "object",
        "additionalProperties": False,
        "required": ["kind"],
        "properties": {
            "version": {"type": "string"},
            "kind": {"type": "string", "enum": [str(kind) for kind in EnvelopeKind]},
            "content": {"type": "string"},
            "summary": {"type": "string", "maxLength": MAX_SUMMARY},
            "tool": {
                "type": "object",
                "additionalProperties": False,
                "required": ["name"],
                "properties": {
                    "name": {"type": "string", "minLength": 1, "maxLength": 128},
                    "arguments": {"type": "object"},
                },
            },
        },
    }


def _unwrap(text: str) -> str:
    fenced = FENCED.match(text)
    return fenced.group("body") if fenced else text


def parse_envelope(text: str) -> AgentEnvelope:
    """Read one envelope, or refuse.

    Every refusal says what was wrong in a sentence a repair prompt can quote back, because the one
    permitted repair attempt is only useful if the agent is told what it got wrong.
    """
    if not isinstance(text, str) or not text.strip():
        raise InvalidAgentOutputError("the agent produced no output")

    body = _unwrap(text).strip()
    try:
        payload = json.loads(body)
    except json.JSONDecodeError as error:
        raise InvalidAgentOutputError(
            f"the agent output is not a single JSON object ({error.msg})",
            details={"reason": "not-json"}) from error

    if not isinstance(payload, dict):
        raise InvalidAgentOutputError(
            "the agent output is valid JSON but not an object",
            details={"reason": "not-an-object"})

    unknown = sorted(set(payload) - {"version", "kind", "content", "summary", "tool"})
    if unknown:
        raise InvalidAgentOutputError(
            f"the agent output carries unknown field(s): {', '.join(unknown)}",
            details={"reason": "unknown-field"})

    raw_kind = payload.get("kind")
    try:
        kind = EnvelopeKind(str(raw_kind))
    except ValueError as error:
        raise InvalidAgentOutputError(
            f"'kind' must be one of {', '.join(str(item) for item in EnvelopeKind)}; "
            f"it was {raw_kind!r}",
            details={"reason": "unknown-kind"}) from error

    version = str(payload.get("version") or ENVELOPE_VERSION)
    if version != ENVELOPE_VERSION:
        raise InvalidAgentOutputError(
            f"the agent output declares protocol {version!r}, not {ENVELOPE_VERSION!r}",
            details={"reason": "wrong-version"})

    summary = str(payload.get("summary") or "")[:MAX_SUMMARY]

    if kind is EnvelopeKind.TOOL_REQUEST:
        tool = payload.get("tool")
        if not isinstance(tool, dict) or not str(tool.get("name") or "").strip():
            raise InvalidAgentOutputError(
                "a TOOL_REQUEST must carry a tool object with a name",
                details={"reason": "tool-missing-name"})
        arguments = tool.get("arguments", {})
        if not isinstance(arguments, dict):
            raise InvalidAgentOutputError(
                "tool arguments must be an object",
                details={"reason": "tool-arguments-not-an-object"})
        if "content" in payload and str(payload["content"]).strip():
            raise InvalidAgentOutputError(
                "a TOOL_REQUEST carries a tool, not content",
                details={"reason": "tool-with-content"})
        return AgentEnvelope(
            kind=kind, version=version, summary=summary,
            tool=ToolRequestIntent(name=str(tool["name"]).strip(), arguments=dict(arguments)))

    content = payload.get("content")
    if not isinstance(content, str) or not content.strip():
        raise InvalidAgentOutputError(
            f"a {kind} envelope must carry non-empty 'content'",
            details={"reason": "missing-content"})
    if payload.get("tool") is not None:
        raise InvalidAgentOutputError(
            f"a {kind} envelope must not carry a tool",
            details={"reason": "content-with-tool"})
    return AgentEnvelope(kind=kind, version=version, content=content, summary=summary)


def repair_instruction(reason: str) -> str:
    """The one corrective instruction the runtime is allowed to send.

    It quotes what was wrong and restates the contract. It does not suggest an answer: a repair
    prompt that proposes content is a runtime writing the agent's reply.
    """
    return (
        "Your previous answer was rejected: "
        f"{reason}\n\n"
        "Answer again with one JSON object and nothing else — no prose before or after it. "
        f"Use protocol \"{ENVELOPE_VERSION}\" and one of the kinds FINAL, MESSAGE or "
        "TOOL_REQUEST, exactly as the instructions describe."
    )
