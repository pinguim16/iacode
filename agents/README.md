# Agent definitions

Delivered by `GATE 2 — AGENT RUNTIME`. This directory is the declared configuration the agent
runtime loads: who the agents are, what teams they form, and the versioned prompts that give each
role its instructions.

```text
profiles/   one JSON file per agent role
teams/      one JSON file per team: an ordered list of stages
prompts/    the prompt templates, named <role>.<version>.md
```

## What a definition is

An **agent profile** is a role, not a model. It names the prompt template that instructs the role,
how many turns the role is allowed, the tool names it may request and an optional default route.
Which model actually serves a turn is the Model Gateway's decision, made from the route or from the
caller's explicit choice — nothing here names a provider or a model.

A **team profile** is an ordered list of stages. Each stage names an agent, the inputs it receives
and the name its output is stored under, so a later stage refers to an earlier one's result by name.
That is the whole language: no branching, no condition and no loop. Composition is configuration —
nothing in this Gate invents a team and no model decides which agents run.

A **prompt template** carries its version in its file name, and the runtime records the SHA-256 of
its bytes on every agent run. Editing a template without renaming it therefore changes the recorded
hash, which is how a run that behaved differently can be traced to the definition that produced it.

## The four agents

| Agent | What it does |
|---|---|
| `generalist` | Answers a single task end to end. Proves one agent against a real model. |
| `planner` | Turns a task into a short ordered plan. Plans only. |
| `reviewer` | Judges the previous stage's output against the task. |
| `engineering-lead` | Consolidates what earlier stages produced into one answer. |

Four, and no more. A profile for a capability this Gate does not exercise would be configuration
with nothing behind it.

## The two teams

| Team | Stages |
|---|---|
| `single-agent` | `generalist` |
| `planner-reviewer` | `planner` then `reviewer`, with the plan reaching the reviewer as a labelled artifact |

## What is deliberately absent

**No tool is permitted to any builtin profile.** `allowedActions` is empty everywhere, because Gate
2 executes nothing: a tool request is persisted, the run pauses at `WAITING_FOR_TOOL`, and Gate 3's
sandbox is what will execute one. The tool lifecycle is proved with fixtures rather than by giving a
real agent a real tool it has nowhere to run.

Operating the runtime: [docs/runbooks/AGENT-RUNTIME.md](../docs/runbooks/AGENT-RUNTIME.md). The
boundary decision: [ADR-0021](../docs/adr/ADR-0021-tool-execution-boundary.md).
