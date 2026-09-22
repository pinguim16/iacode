# ADR-0021 — A tool request is recorded and waited on; execution belongs to GATE 3

Status: Accepted
Date: 2026-09-22
Owners: GATE 2 — Agent Runtime

## Context

`GATE 2 — AGENT RUNTIME` builds the component that decides what an agent does next. The moment an
agent can say "run this command", the shortest path to a working demonstration is to run it. That
path is closed, deliberately, and this records why and how.

The division the Master Plan draws is:

```text
GATE 2   the brain that coordinates
GATE 3   the hands that execute, inside a sandbox with a policy
```

Between them sits one object: a tool request. The question this ADR answers is what Gate 2 does
with it, and what makes the answer checkable rather than a promise.

Two failure modes were available and both are worse than doing nothing. The first is executing:
a runtime that shells out has, by construction, given a model the machine — and it would have done
so before the Gate that designs the isolation, the policy and the escape tests exists. The second is
**pretending**: a "ShellTool" that returns `{"status": "success"}` without executing. The
Development Contract names that one directly — a functional placeholder that behaves like a
feature — and it is worse than executing, because the run looks correct and the evidence is a lie.

## Decision

**An agent that asks for a tool has its request persisted, the run moves to `WAITING_FOR_TOOL`, and
the workflow waits. Nothing in the runtime or the worker can execute anything, and that is enforced
by a scan rather than by intent.**

Concretely:

- A `TOOL_REQUEST` turn is validated against the profile's `allowedActions`, bounded by the
  configured argument limit, persisted as a `tool_requests` row, recorded as a `TOOL_REQUESTED`
  event, and the run transitions to `WAITING_FOR_TOOL`.
- The workflow then waits on a signal, with the run's own tool-wait timeout, which is separate from
  the run deadline because waiting is not the same as working.
- **The tool name is data.** It is compared against a permitted set and stored. It is never resolved
  to a command, a path, an import or an attribute: the runtime calls no `eval`, no `exec`, no
  `getattr`, no `importlib.import_module` and no `__import__`, anywhere.
- **The arguments are opaque.** They are stored and handed back to the agent as a labelled artifact.
  Nothing reads a key out of them and nothing acts on one.
- A result is accepted through `POST /api/v1/agent-runs/{run_id}/tool-results`, validated against
  the database — the request must exist, belong to this run, still be pending, and the run must not
  be terminal — and only then signalled to the workflow. In Gate 2 the authorised producer is a
  test fixture or the durability rehearsal; from Gate 3 it is the sandbox.
- **No shipped profile is given a tool.** Every builtin profile declares `allowedActions: []`, and a
  control-plane test asserts it. A profile with a permitted action would be configuration for a
  capability that does not exist.

The controls that make this checkable:

| Control | What it refuses |
|---|---|
| `ToolExecutionBoundaryTests` (runtime suite) | any module of the runtime importing `subprocess`, `pty`, `docker`, a Git library or a browser driver; calling `os.system`, `subprocess.run`, `shutil.rmtree`, `path.write_text`, `eval`, `exec` or `compile`; or opening a file for writing |
| `RepositoryToolExecutionBoundaryTests` (control plane) | the same, over the runtime **and** the worker that drives it, because the boundary is the pair |
| `test_no_shipped_profile_is_given_a_tool` | a builtin profile that permits an action |
| Red Team `G2-F` | an agent asking for `shell.exec` with a destructive command: the request must be stored verbatim as data and the run must pause |
| Red Team `G2-G` | a tool outside the profile's permitted set reaching the store |

Every scan carries a null control: the identical scan over a module that does the forbidden thing,
which must fire. `.iacode/memory/lessons.jsonl` records a battery that reported every attack as
defended while its refusals came from leftover state.

## Consequences

**A run can end without ever being answered.** A tool request nobody resolves times out and the run
fails with `TOOL_WAIT_TIMEOUT`. That is the honest outcome in a Gate with no executor, and it is why
no shipped profile asks for a tool.

**The tool lifecycle is proved with fixtures, not with a live agent.** The runtime suite drives it
with a scripted model, and the durability and cancellation scenarios drive it through the real
workflow against a real Temporal server with a real container restart. None of that needs an
executor, which is the point.

**Gate 3 inherits a boundary rather than a rewrite.** The request, the pause, the resume, the
idempotent result and the refusals are all in place. What Gate 3 adds is the thing that answers,
inside its sandbox, and the endpoint it will call already exists and already validates.

**The rehearsal harness is outside the shipped source.** `services/orchestrator/rehearsal/` supplies
the scripted agent the scenarios need. The image copies it to `/app/rehearsal` while the worker's
own code is on `/app/src`, so the running worker cannot import it. The separation is a path, not a
promise, and a control-plane test asserts both halves of it.

## Alternatives considered

**Execute, carefully, with a small allow-list.** Rejected. The isolation, the policy, the filesystem
and network boundaries and the escape suite are what make execution safe, and all four are Gate 3's
deliverables. Building the execution first and the isolation second is the order that produces
incidents.

**A stub executor that returns success.** Rejected outright. It is a functional placeholder that
behaves like a feature, which `docs/DEVELOPMENT-CONTRACT.md` forbids, and it would make every
downstream test green for a capability that does not exist.

**Give one builtin profile a tool so a live agent can exercise the pause.** Rejected. It would ship
configuration for a capability the platform does not have, and a live agent's compliance with an
instruction is not a control. The fixtures and the scenarios prove the same lifecycle
deterministically.
