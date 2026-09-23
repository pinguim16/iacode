# Agent definitions

Delivered by `GATE 2 — AGENT RUNTIME` and extended by `GATE 3 — SANDBOX`. This directory is the declared configuration the agent
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

## The agents

| Agent | Gate | What it does | Tools |
|---|---|---|---|
| `generalist` | 2 | Answers a single task end to end. Proves one agent against a real model. | none |
| `planner` | 2 | Turns a task into a short ordered plan. Plans only. | none |
| `reviewer` | 2 | Judges the previous stage's output against the task. | none |
| `engineering-lead` | 2 | Consolidates what earlier stages produced into one answer. | none |
| `developer` | 3 | Changes a repository in the run's sandbox: reads, edits, runs tests, commits locally. | the `developer` sandbox policy |
| `code-reviewer` | 3 | Inspects what the developer changed, read-only, and approves or asks for changes. | the `reviewer` sandbox policy |

A role is given a tool only together with the **sandbox policy** that executes it
(`sandboxPolicy`), and the loader refuses a profile that permits a tool and names no policy. What
executing a tool may cause is decided by that policy in
[`.iacode/policies/sandbox-policy.json`](../.iacode/policies/sandbox-policy.json), never by the
profile and never by the request ([ADR-0027](../docs/adr/ADR-0027-tool-execution-policy.md)). The four
roles `GATE 2` declared still have no tool.

## The teams

| Team | Stages |
|---|---|
| `single-agent` | `generalist` |
| `planner-reviewer` | `planner` then `reviewer`, with the plan reaching the reviewer as a labelled artifact |
| `coding` | `planner`, then `developer`, then `code-reviewer`, sharing the run's one sandbox workspace |

## Where tools run

From `GATE 3` a tool request from a stage with a sandbox policy is executed automatically inside
the run's own disposable container by the sandbox service
([docs/runbooks/SANDBOX.md](../docs/runbooks/SANDBOX.md)), and the result returns to the agent as
labelled data. Nothing is ever executed on the host. A stage without a sandbox policy keeps `GATE 2`'s
behaviour: the request is recorded, the run pauses, and a result arrives through the API.

Operating the runtime: [docs/runbooks/AGENT-RUNTIME.md](../docs/runbooks/AGENT-RUNTIME.md). The
boundary decision: [ADR-0021](../docs/adr/ADR-0021-tool-execution-boundary.md).
