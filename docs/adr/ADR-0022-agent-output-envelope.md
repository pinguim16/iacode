# ADR-0022 — An agent turn is one versioned envelope, parsed strictly, with exactly one repair

Status: Accepted
Date: 2026-09-22
Owners: GATE 2 — Agent Runtime

## Context

`docs/GATE-2-CHECKLIST.md` section 8 requires a turn to produce exactly one of three outcomes, the
envelope to carry a version, the parser to be strict, and the repair to be bounded. The decision
behind those four is one decision about how a model tells the runtime what it wants.

The constraint that shapes it comes from Gate 1: **every capability of the configured provider is
`UNKNOWN`**. The provider publishes no capability metadata, the catalog refuses to guess, and the
router refuses an unknown capability rather than sending a request hopefully. So the runtime cannot
assume native structured output, cannot assume native tool calling, and must not assert either on a
model's behalf to make a turn work.

That leaves the runtime reading a model's text and deciding what it means, which is where the real
question is: **what does it do with an answer that is nearly right?**

## Decision

**One JSON object per turn, with a declared protocol version and exactly three kinds. The parser
refuses anything else. An invalid answer buys exactly one corrective call, which is charged to the
budget; a second invalid answer fails the run.**

Concretely:

```json
{"version": "agent-envelope/1.0", "kind": "FINAL",   "content": "…", "summary": "…"}
{"version": "agent-envelope/1.0", "kind": "MESSAGE", "content": "…"}
{"version": "agent-envelope/1.0", "kind": "TOOL_REQUEST",
 "tool": {"name": "…", "arguments": {}}}
```

- `FINAL` ends the stage, `MESSAGE` asks for another turn, `TOOL_REQUEST` pauses the run. There is
  no fourth kind and no field outside the five the schema declares.
- The parser unwraps **one** fenced block, because a model trained on chat markup fences its JSON,
  and then reads exactly one object. Prose before or after it, two objects, an unknown kind, a
  missing field, a tool request that also carries content, a final answer that also carries a tool,
  an unknown field, or a version that is not this one: each is a refusal, and each refusal says what
  was wrong.
- **Native structured output is used only where it is known to exist.** The client asks the catalog,
  and turns the provider's own schema enforcement on only for an explicitly named model whose entry
  says `SUPPORTED`. An `UNKNOWN` capability answers no, and so does a request that names a route,
  because a route resolves to a candidate list and a capability that holds for one candidate does
  not hold for the next.
- One JSON Schema serves both uses: it is the structured-output schema when the capability exists,
  and the documentation of what the prompt asks for when it does not.
- The repair appends `repair_instruction(reason)` to the turn's instructions, quoting what was
  wrong and restating the contract. It proposes no answer: a repair prompt that suggested content
  would be the runtime writing the agent's reply.
- The repair is a model call. It is charged to `maxModelCalls` like any other and recorded with
  `repairAttempt=true`. A run that cannot afford the repair does not make it.

## Consequences

**An agent that will not conform fails the run, visibly.** `INVALID_AGENT_OUTPUT` names what
happened, the stage that failed and that a repair was attempted. That is better than a runtime that
guesses, because a guess is the runtime inventing the agent's decision — and better than an
unbounded retry, which turns a badly behaved model into an unbounded bill.

**The protocol works on a provider that declares nothing.** Which is the provider this Gate has.
Validated JSON text is the floor; native enforcement is an improvement the runtime takes when the
catalog offers it and never assumes.

**A consumer detects an incompatible change instead of crashing on one.** The version is in the
envelope and in the prompt. Changing the shape changes the version, and an agent still producing
`agent-envelope/1.0` is refused with a message that says so.

**The three kinds keep the loop small.** The whole run lifecycle is: continue, pause, or finish.
Adding a fourth kind would add a branch the state machine has no state for, and a `kind` nobody
exercises is a `kind` nobody tests.

**A summary is bounded and is not a narrative.** At most 400 characters, and the runtime instructions
say plainly that the agent must not write out its reasoning anywhere in the object. The Development
Contract forbids storing private chain-of-thought, so the runtime does not ask for it: what it keeps
is a short verifiable statement of what was decided.

## Alternatives considered

**Native tool calling.** Rejected for this Gate. The provider declares `tools` as `UNKNOWN` for
every model, and asserting the capability to make the feature work is exactly the guess Gate 1 built
its catalog to refuse. An operator who states the capability in `providers.json` makes it available;
nothing in this Gate depends on it.

**Free text with a heuristic.** Rejected. "If the answer starts with APPROVED it means approval" is a
parser nobody can version and every model breaks differently.

**Unbounded repair until the model conforms.** Rejected. It is an unbounded loop wearing a helpful
name, and the budget is the only thing that would eventually stop it — after paying for every
attempt.

**No repair at all.** Considered seriously. One malformed answer is a frequent and recoverable
event, and refusing to ask again would fail runs for a missing brace. One attempt, charged and
recorded, is the smallest tolerance that is still bounded.
