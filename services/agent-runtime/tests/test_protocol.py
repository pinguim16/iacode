"""The agent turn protocol: exactly three kinds, a strict parser and one bounded repair."""

from __future__ import annotations

import json

import pytest
from iacode_agent_runtime.errors import InvalidAgentOutputError
from iacode_agent_runtime.protocol import (
    ENVELOPE_VERSION,
    EnvelopeKind,
    envelope_schema,
    parse_envelope,
    repair_instruction,
)


class AgentEnvelopeTests:
    """One turn produces exactly one of a final answer, a message or a tool request."""

    def test_the_three_kinds_are_the_whole_vocabulary(self) -> None:
        assert [str(kind) for kind in EnvelopeKind] == ["FINAL", "MESSAGE", "TOOL_REQUEST"]

    def test_a_final_envelope_carries_the_answer(self) -> None:
        parsed = parse_envelope(json.dumps({
            "version": ENVELOPE_VERSION, "kind": "FINAL",
            "content": "IACODE_AGENT_OK", "summary": "answered"}))
        assert parsed.is_final
        assert parsed.content == "IACODE_AGENT_OK"
        assert parsed.summary == "answered"
        assert parsed.tool is None

    def test_a_message_envelope_asks_for_another_turn(self) -> None:
        parsed = parse_envelope(json.dumps({"kind": "MESSAGE", "content": "thinking about it"}))
        assert parsed.kind is EnvelopeKind.MESSAGE
        assert not parsed.is_final

    def test_a_tool_request_carries_a_tool_and_no_content(self) -> None:
        parsed = parse_envelope(json.dumps({
            "kind": "TOOL_REQUEST",
            "tool": {"name": "shell.exec", "arguments": {"command": "rm -rf /"}}}))
        assert parsed.kind is EnvelopeKind.TOOL_REQUEST
        assert parsed.tool is not None
        # The name and the arguments are *data*. Parsing one does not resolve it, look it up or
        # run it; the most hostile possible command here is a string in a dictionary.
        assert parsed.tool.name == "shell.exec"
        assert parsed.tool.arguments == {"command": "rm -rf /"}
        assert parsed.content == ""

    def test_a_fenced_block_is_unwrapped_once(self) -> None:
        """A model trained on chat markup fences its JSON. One fence is tolerated; prose is not."""
        body = json.dumps({"kind": "FINAL", "content": "fenced"})
        assert parse_envelope(f"```json\n{body}\n```").content == "fenced"
        assert parse_envelope(f"```\n{body}\n```").content == "fenced"

    def test_round_trip_is_stable(self) -> None:
        parsed = parse_envelope(json.dumps({"kind": "FINAL", "content": "x", "summary": "s"}))
        again = parse_envelope(json.dumps(parsed.to_dict()))
        assert again.to_dict() == parsed.to_dict()


def test_envelope_version_is_declared() -> None:
    """A consumer that has to discover an incompatible change by crashing discovers it late."""
    assert ENVELOPE_VERSION.startswith("agent-envelope/")
    parsed = parse_envelope(json.dumps({"kind": "FINAL", "content": "x"}))
    assert parsed.version == ENVELOPE_VERSION
    assert parsed.to_dict()["version"] == ENVELOPE_VERSION

    with pytest.raises(InvalidAgentOutputError) as raised:
        parse_envelope(json.dumps({
            "version": "agent-envelope/9.9", "kind": "FINAL", "content": "x"}))
    assert "protocol" in str(raised.value)


INVALID_ENVELOPES = (
    ("", "an empty answer"),
    ("   ", "whitespace"),
    ("I think the answer is 4.", "prose instead of an object"),
    ('{"kind": "FINAL", "content": "x"} trailing words', "prose after the object"),
    ('["FINAL"]', "an array rather than an object"),
    ('{"kind": "FINISHED", "content": "x"}', "a kind nobody declared"),
    ('{"content": "x"}', "no kind at all"),
    ('{"kind": "FINAL"}', "a final answer with no content"),
    ('{"kind": "FINAL", "content": "  "}', "a final answer with blank content"),
    ('{"kind": "TOOL_REQUEST"}', "a tool request with no tool"),
    ('{"kind": "TOOL_REQUEST", "tool": {"arguments": {}}}', "a tool with no name"),
    ('{"kind": "TOOL_REQUEST", "tool": {"name": "x", "arguments": []}}',
     "tool arguments that are not an object"),
    ('{"kind": "TOOL_REQUEST", "tool": {"name": "x"}, "content": "also this"}',
     "a tool request that also carries content"),
    ('{"kind": "FINAL", "content": "x", "tool": {"name": "y"}}',
     "a final answer that also carries a tool"),
    ('{"kind": "FINAL", "content": "x", "notes": "extra"}', "a field nobody declared"),
)


def test_invalid_envelope_is_not_accepted_silently() -> None:
    """Every refusal explains itself, because the one repair attempt quotes the reason back.

    Written as a loop rather than as a parametrisation: the TESTS denominator is derived
    statically from the source, and a runtime expansion cannot be counted that way.
    """
    for body, because in INVALID_ENVELOPES:
        with pytest.raises(InvalidAgentOutputError) as raised:
            parse_envelope(body)
        assert str(raised.value).strip(), f"the refusal of {because} said nothing"


def test_the_schema_describes_exactly_the_parser() -> None:
    """One definition serves the prompt and the structured-output request."""
    schema = envelope_schema()
    assert schema["additionalProperties"] is False
    assert set(schema["properties"]) == {"version", "kind", "content", "summary", "tool"}
    assert schema["properties"]["kind"]["enum"] == [str(kind) for kind in EnvelopeKind]


def test_the_repair_instruction_quotes_the_reason_and_proposes_nothing() -> None:
    """A repair prompt that suggested an answer would be the runtime writing the agent's reply."""
    instruction = repair_instruction("'kind' must be one of FINAL, MESSAGE, TOOL_REQUEST")
    assert "'kind' must be one of" in instruction
    assert ENVELOPE_VERSION in instruction
    for forbidden in ("you should answer", "for example", "try:"):
        assert forbidden not in instruction.lower()


def test_a_summary_is_bounded() -> None:
    """A summary is a short verifiable statement, not somewhere to narrate reasoning."""
    parsed = parse_envelope(json.dumps({
        "kind": "FINAL", "content": "x", "summary": "y" * 5000}))
    assert len(parsed.summary) <= 400
