"""The agent turn protocol: exactly three kinds, a strict parser and one bounded repair."""

from __future__ import annotations

import json

import pytest
from iacode_agent_runtime.errors import InvalidAgentOutputError
from iacode_agent_runtime.protocol import (
    ENVELOPE_VERSION,
    EnvelopeKind,
    envelope_contract,
    envelope_examples,
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
    ('{"kind": "FINAL", "content": ["step one", "step two"]}',
     "a final answer whose content is an array of steps"),
    ('{"kind": "MESSAGE", "content": {"plan": "x"}}', "a message whose content is an object"),
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


WRONGLY_TYPED_CONTENT = (
    (["step one", "step two"], "an array"),
    ({"plan": "x"}, "an object"),
    (3, "a number"),
    (True, "a boolean"),
)


def test_content_of_the_wrong_type_is_refused_by_its_real_defect() -> None:
    """G2-F-009: a planner answered its steps as an array, and the refusal said content was missing.

    The one repair quotes the refusal back, so a reason that misnames the defect spends the repair
    on the wrong correction and the model returns the same array. The parser stays exactly as
    strict — an array is still refused — and the sentence now says what is wrong.
    """
    for value, named in WRONGLY_TYPED_CONTENT:
        with pytest.raises(InvalidAgentOutputError) as raised:
            parse_envelope(json.dumps({"kind": "FINAL", "content": value}))
        reason = str(raised.value)
        assert raised.value.details["reason"] == "content-not-a-string", named
        assert named in reason
        assert "one JSON string" in reason
        assert "non-empty" not in reason, f"{named} content was reported as missing"

        instruction = repair_instruction(reason)
        assert "one JSON string" in instruction
        for forbidden in ("you should answer", "for example", "try:"):
            assert forbidden not in instruction.lower()

    for body in ('{"kind": "FINAL"}', '{"kind": "FINAL", "content": "  "}',
                 '{"kind": "FINAL", "content": null}'):
        with pytest.raises(InvalidAgentOutputError) as raised:
            parse_envelope(body)
        assert raised.value.details["reason"] == "missing-content", body


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


# ---------------------------------------------------------------------------------------------
# M1-F-001: the exact shape, rendered from the schema, in the instructions and in the repair
# ---------------------------------------------------------------------------------------------

TOOLS = ("shell.exec", "filesystem.read")


def test_every_example_is_a_valid_envelope_of_its_kind() -> None:
    """The shape a model is shown is one the parser accepts, kind by kind (mandate test B)."""
    examples = envelope_examples(tool_names=TOOLS)
    assert list(examples) == [str(kind) for kind in EnvelopeKind]
    for kind, example in examples.items():
        parsed = parse_envelope(json.dumps(example))
        assert str(parsed.kind) == kind
        assert parsed.version == ENVELOPE_VERSION


def test_the_tool_request_example_carries_a_name_and_arguments() -> None:
    """Mandate test B: tool.name and tool.arguments, nested, with a tool the stage may request."""
    example = envelope_examples(tool_names=TOOLS)["TOOL_REQUEST"]
    assert set(example) == {"version", "kind", "tool"}
    assert set(example["tool"]) == {"name", "arguments"}
    assert example["tool"]["name"] in TOOLS
    assert isinstance(example["tool"]["arguments"], dict)
    parsed = parse_envelope(json.dumps(example))
    assert parsed.tool is not None and parsed.tool.name in TOOLS

    unnamed = envelope_examples()["TOOL_REQUEST"]
    assert unnamed["tool"]["name"] == "<tool name>"


def test_the_contract_states_the_version_every_kind_and_the_tool_keys() -> None:
    contract = envelope_contract(tool_names=TOOLS)
    assert ENVELOPE_VERSION in contract
    for kind, example in envelope_examples(tool_names=TOOLS).items():
        assert kind in contract
        assert json.dumps(example, ensure_ascii=False) in contract
    for key in envelope_schema()["properties"]:
        assert f'"{key}"' in contract
    assert '"name"' in contract and '"arguments"' in contract
    assert "never at the top level" in contract


def test_the_repair_restates_the_same_shape() -> None:
    """Mandate test C: the repair carries the contract the instructions carry, verbatim."""
    reason = "the agent output carries unknown field(s): command, cwd, timeoutSeconds"
    instruction = repair_instruction(reason, tool_names=TOOLS)
    assert reason in instruction
    assert envelope_contract(tool_names=TOOLS) in instruction
    for forbidden in ("you should answer", "for example", "try:"):
        assert forbidden not in instruction.lower()


def test_the_rendered_contract_follows_the_schema() -> None:
    """Mandate test D: change the canonical schema and the rendered text changes with it."""
    import copy

    schema = copy.deepcopy(envelope_schema())
    tool = schema["properties"]["tool"]
    tool["properties"] = {"tool_id": {"type": "string", "minLength": 1},
                          "parameters": {"type": "object"}}
    tool["required"] = ["tool_id"]
    schema["properties"]["kind"]["enum"] = ["FINAL", "TOOL_REQUEST"]

    contract = envelope_contract(tool_names=TOOLS, schema=schema, version="agent-envelope/9.9")

    assert '"tool_id"' in contract and '"parameters"' in contract
    assert '"arguments"' not in contract
    assert "agent-envelope/9.9" in contract
    assert "MESSAGE" not in contract
    example = envelope_examples(tool_names=TOOLS, schema=schema)["TOOL_REQUEST"]
    assert set(example["tool"]) == {"tool_id", "parameters"}


TOOL_ARGUMENTS_IN_THE_WRONG_PLACE = (
    ({"kind": "TOOL_REQUEST", "command": "ls", "cwd": ".", "tool": {"name": "shell.exec"}},
     "unknown-field", 'go inside "tool"'),
    ({"kind": "TOOL_REQUEST", "tool": {"name": "shell.exec", "args": {"command": "ls"}}},
     "tool-unknown-field", "args"),
    ({"kind": "TOOL_REQUEST", "tool": {"name": "filesystem.read", "parameters": {"path": "a"}}},
     "tool-unknown-field", "parameters"),
    ({"kind": "TOOL_REQUEST", "tool": {"name": "filesystem.read", "path": "a"}},
     "tool-unknown-field", "path"),
)


def test_arguments_outside_tool_arguments_are_refused_by_their_real_defect() -> None:
    """M1-F-001: the configured live model put its arguments at the top level, then under "args".

    The first was refused as an unknown field without saying where arguments belong; the second
    was *accepted* with no arguments, because the parser ignored a stray key in the tool object,
    and the sandbox then refused a request for an argument the model had in fact sent. Both are
    refused now, each by its own reason, and the sentence says where the arguments go (LSN-0047).
    """
    for body, reason, named in TOOL_ARGUMENTS_IN_THE_WRONG_PLACE:
        with pytest.raises(InvalidAgentOutputError) as raised:
            parse_envelope(json.dumps(body))
        assert raised.value.details["reason"] == reason, body
        assert named in str(raised.value), body
        assert '"arguments"' in str(raised.value), body

    accepted = parse_envelope(json.dumps(
        {"kind": "TOOL_REQUEST", "tool": {"name": "shell.exec", "arguments": {"command": "ls"}}}))
    assert accepted.tool is not None and accepted.tool.arguments == {"command": "ls"}
