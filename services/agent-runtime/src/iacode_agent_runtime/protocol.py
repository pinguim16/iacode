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
    "envelope_contract",
    "envelope_examples",
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


#: The field each kind carries besides ``version`` and ``kind``. The parser requires exactly this and
#: :func:`envelope_contract` states it, so the prompt and the parser describe one protocol.
KIND_FIELD: dict[EnvelopeKind, str] = {
    EnvelopeKind.FINAL: "content",
    EnvelopeKind.MESSAGE: "content",
    EnvelopeKind.TOOL_REQUEST: "tool",
}

#: When an agent answers with each kind, in the words the contract uses.
KIND_PURPOSE: dict[EnvelopeKind, str] = {
    EnvelopeKind.FINAL: "you have the answer and the stage is over",
    EnvelopeKind.MESSAGE: "you need another turn and say what you have so far",
    EnvelopeKind.TOOL_REQUEST: "you need one tool",
}


def envelope_schema() -> dict[str, Any]:
    """The JSON Schema of the envelope.

    Used two ways from one definition: as the structured-output schema when a model declares the
    capability, and — rendered by :func:`envelope_contract` — as the contract the prompt states when
    it does not. `M1-F-001` found the second use claimed and never made: the prompt described a tool
    request only as a tool "carrying its name and arguments", every capability of the configured
    provider was ``UNKNOWN``, so no model was ever shown the keys, and the configured live model
    could not form one tool request. A second shape written into the prompt by hand would be a
    second thing to keep in step, so the prompt's shape is rendered from this one.
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


def _tool_keys(schema: dict[str, Any]) -> tuple[str, str]:
    """The tool object's two keys, read from the schema: the name (a required string) and the
    arguments (an object)."""
    tool = schema["properties"]["tool"]
    properties = tool["properties"]
    required = [key for key in tool.get("required") or [] if key in properties]
    name = next(key for key in required if properties[key].get("type") == "string")
    arguments = next(key for key, value in properties.items() if value.get("type") == "object")
    return name, arguments


def envelope_examples(*, tool_names: tuple[str, ...] = (),
                      schema: dict[str, Any] | None = None,
                      version: str = ENVELOPE_VERSION) -> dict[str, dict[str, Any]]:
    """One minimal valid envelope per kind, built from the schema rather than written by hand.

    The values are placeholders a model replaces — the runtime proposes no answer — except the tool
    name, which is one of the tools the stage may request when it has any, so the example is a
    request the policy would accept by name.
    """
    schema = schema or envelope_schema()
    name_key, arguments_key = _tool_keys(schema)
    tool_name = sorted(tool_names)[0] if tool_names else "<tool name>"
    placeholders = {
        "content": {EnvelopeKind.FINAL: "<your answer, one string>",
                    EnvelopeKind.MESSAGE: "<what you have so far, one string>"},
    }
    examples: dict[str, dict[str, Any]] = {}
    for raw_kind in schema["properties"]["kind"]["enum"]:
        kind = EnvelopeKind(raw_kind)
        field = KIND_FIELD[kind]
        example: dict[str, Any] = {"version": version, "kind": raw_kind}
        if field == "tool":
            example["tool"] = {name_key: tool_name,
                               arguments_key: {"<argument name>": "<argument value>"}}
        else:
            example[field] = placeholders[field][kind]
        examples[raw_kind] = example
    return examples


def envelope_contract(*, tool_names: tuple[str, ...] = (),
                      schema: dict[str, Any] | None = None,
                      version: str = ENVELOPE_VERSION) -> str:
    """The exact shape of the envelope, as text a model can follow, rendered from the schema.

    It is what a model sees whenever the gateway does not constrain its output with the schema
    itself — which is every model whose structured-output capability is not known, and the
    configured provider publishes none. The runtime cannot know at prompt time whether the gateway
    will honour a structured-output request, so the contract is always stated; with native
    structured output it restates what the schema already enforces.

    Every key, the version, the kinds and the examples come from :func:`envelope_schema` and
    :data:`KIND_FIELD`; a change to either changes this text. Nothing here is a second protocol.
    """
    schema = schema or envelope_schema()
    properties = schema["properties"]
    kinds = list(properties["kind"]["enum"])
    name_key, arguments_key = _tool_keys(schema)
    examples = envelope_examples(tool_names=tool_names, schema=schema, version=version)
    keys = ", ".join(f'"{key}"' for key in properties)
    lines = [
        f"The object has only these keys: {keys}. Any other key is refused.",
        f'"version" is "{version}". "kind" is exactly one of: {", ".join(kinds)}.',
        "",
    ]
    for raw_kind in kinds:
        kind = EnvelopeKind(raw_kind)
        lines.append(f'{raw_kind} — {KIND_PURPOSE[kind]}; it carries "{KIND_FIELD[kind]}":')
        lines.append(json.dumps(examples[raw_kind], ensure_ascii=False))
        lines.append("")
    tool_kinds = [kind for kind in kinds if KIND_FIELD[EnvelopeKind(kind)] == "tool"]
    content_kinds = [kind for kind in kinds if KIND_FIELD[EnvelopeKind(kind)] == "content"]
    for tool_kind in tool_kinds:
        lines.append(
            f'In a {tool_kind}, "tool" is an object with exactly two keys: "{name_key}", the '
            f'tool\'s name as listed, and "{arguments_key}", an object holding that tool\'s own '
            f'arguments. The arguments always go inside "tool", under "{arguments_key}" — never at '
            f'the top level of the object and never under another key. A {tool_kind} carries no '
            f'"content".')
    if content_kinds:
        lines.append(f'{" and ".join(content_kinds)} carry no "tool".')
    return "\n".join(lines)


def _json_type(value: Any) -> str:
    """The JSON name of a decoded value's type, as a refusal sentence can say it."""
    if isinstance(value, bool):
        return "a boolean"
    if isinstance(value, (int, float)):
        return "a number"
    if isinstance(value, list):
        return "an array"
    if isinstance(value, dict):
        return "an object"
    return "null" if value is None else "a string"


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

    schema = envelope_schema()
    unknown = sorted(set(payload) - set(schema["properties"]))
    if unknown:
        name_key, arguments_key = _tool_keys(schema)
        hint = (f'; a tool\'s arguments go inside "tool": {{"{name_key}": ..., '
                f'"{arguments_key}": {{...}}}}, never at the top level'
                if payload.get("kind") == str(EnvelopeKind.TOOL_REQUEST) else "")
        raise InvalidAgentOutputError(
            f"the agent output carries unknown field(s): {', '.join(unknown)}{hint}",
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
        name_key, arguments_key = _tool_keys(schema)
        tool = payload.get("tool")
        if not isinstance(tool, dict) or not str(tool.get(name_key) or "").strip():
            raise InvalidAgentOutputError(
                "a TOOL_REQUEST must carry a tool object with a name",
                details={"reason": "tool-missing-name"})
        # M1-F-001: a key beside the name and the arguments used to be dropped, so a model that
        # wrote its arguments under "args" or "parameters" had a request accepted with none, and
        # the sandbox refused it for a missing argument the model had in fact sent. The schema
        # already closed the tool object; the parser now agrees with it and says where the
        # arguments belong.
        stray = sorted(set(tool) - set(schema["properties"]["tool"]["properties"]))
        if stray:
            raise InvalidAgentOutputError(
                f"the tool object carries unknown field(s): {', '.join(stray)}; its only keys are "
                f'"{name_key}" and "{arguments_key}", and the tool\'s own arguments go inside '
                f'"{arguments_key}"',
                details={"reason": "tool-unknown-field"})
        arguments = tool.get(arguments_key, {})
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
            tool=ToolRequestIntent(name=str(tool[name_key]).strip(), arguments=dict(arguments)))

    content = payload.get("content")
    if content is not None and not isinstance(content, str):
        # A present value of the wrong type is a different defect from an absent one, and the
        # refusal has to say which: the one repair quotes this sentence back, and "must carry
        # content" sent to an agent that did carry content — as an array of plan steps — is
        # answered with the same array again.
        raise InvalidAgentOutputError(
            f"'content' must be one JSON string, and it was {_json_type(content)}; an answer with "
            f"several lines is still one string, with its lines separated by newline characters",
            details={"reason": "content-not-a-string"})
    if not isinstance(content, str) or not content.strip():
        raise InvalidAgentOutputError(
            f"a {kind} envelope must carry non-empty 'content'",
            details={"reason": "missing-content"})
    if payload.get("tool") is not None:
        raise InvalidAgentOutputError(
            f"a {kind} envelope must not carry a tool",
            details={"reason": "content-with-tool"})
    return AgentEnvelope(kind=kind, version=version, content=content, summary=summary)


def repair_instruction(reason: str, *, tool_names: tuple[str, ...] = ()) -> str:
    """The one corrective instruction the runtime is allowed to send.

    It quotes what was wrong and restates the contract — the exact shape, rendered by
    :func:`envelope_contract` from the same schema as the runtime instructions, because a repair
    that says only "answer with valid JSON" leaves the model guessing at the correction
    (`M1-F-001`: the configured model moved its arguments from the top level to "args" and was
    refused again). It does not suggest an answer: the shape's values are placeholders, and a
    repair prompt that proposed content would be the runtime writing the agent's reply.
    """
    return (
        "Your previous answer was rejected: "
        f"{reason}\n\n"
        "Answer again with one JSON object and nothing else — no prose before or after it. "
        f"Use protocol \"{ENVELOPE_VERSION}\" and follow this shape exactly:\n\n"
        + envelope_contract(tool_names=tool_names)
    )
