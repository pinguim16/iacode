# Durability rehearsal

A harness, not a feature. It exists so that one claim of `GATE 2 — AGENT RUNTIME` can be proved
rather than asserted: **a worker restart while a run waits for a tool loses nothing.**

It lives beside the worker's source rather than inside it, and the image copies it to `/app/rehearsal`
while the worker's own code is on `/app/src`. The running worker therefore cannot import any of it:
the separation is a path, not a promise. That is the same arrangement the API image uses for the
suites it carries.

## Why a harness exists at all

Proving the restart needs three things at once: the **real** `AgentRunWorkflow`, a **real** Temporal
server, and a **real** container restart. The first two rule out a unit test; the third rules out
anything running inside one container.

It also needs an agent that asks for a tool, and no builtin profile may request one — Gate 2
executes nothing, so giving a shipped profile a tool would be configuration for a capability that
does not exist. The harness supplies the missing piece the only honest way: it registers the real
workflow and the real persistence activities, and replaces **one** activity — the model call — with
a scripted answer. Nothing of the runtime's behaviour is replaced; the model is.

What is deliberately *not* here: any executor. The scripted agent asks for a tool, the run pauses,
and the result is supplied by this harness over the same API a sandbox would use in Gate 3. No
command is ever run.

## How it is driven

`scripts/iacode/scenarios/agent_runtime_durability.py` on the host, which starts the harness worker
as its own container, creates the run, restarts that container for real, delivers the result and
reads the run back.

```bash
python scripts/iacode/scenarios/agent_runtime_durability.py
```
