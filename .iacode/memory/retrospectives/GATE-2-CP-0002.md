# Retrospective — GATE 2 — AGENT RUNTIME / GATE-2-CP-0002

Record observations, decisions and evidence. Never record private chain-of-thought, and never record
a secret. Every claim points at an artifact in this repository.

This checkpoint closes GATE 2 from `GATE-2-CP-0001`, which was sealed `BLOCKED` on the provider's
quota. The Gate's own retrospective is `GATE-2-CP-0001.md`; this one covers the closure.

## What went well

**The live runs were treated as evidence rather than as a formality.** Of the live runs the closure
made, three failed, and each failure was diagnosed to a real defect and repaired before the next run
was allowed to count: `G2-F-009`, `G2-F-010` and `G2-F-012`. Nothing was retried until it happened to
be green. `docs/checkpoints/GATE-2-CP-0002/DECISIONS.md`.

**A decision that belonged to the operator went to the operator.** Which model the evidence names,
whether to register a second provider, how to correct the ledger, and whether to reopen a sealed
checkpoint were each asked, answered and recorded rather than decided by the delivery.

**Every repair was proven against the code it replaced.** Each new guardrail test was run against the
previous source and failed there, with the message that names the defect, before it was trusted.

## What failed

**`G2-F-009` — a refusal named the wrong defect.** The envelope parser refused a planner's `content`
that was an array of steps with the sentence it uses for a missing `content`, and the one repair
quoted that sentence back. Root cause: one test ("is a non-empty string") reported with one reason.
Recorded as `LSN-0047`.

**`G2-F-010` — a finished run whose log had not finished.** The terminal state was committed before
the terminal event, and a reader between the two commits saw one without the other, once in three
live runs. Root cause: two commits for one fact, written in the unsafe order. Recorded as `LSN-0048`.

**`G2-F-011` — diagnostic records nobody could replay.** Recorded as a recurrence of `LSN-0010`.

**`G2-F-012` — a metric read before the scrape that carries it.** The live gateway smoke failed on a
freshly rebuilt stack because it asked Prometheus once, before the next scrape. Recorded as
`LSN-0049`.

**`G2-F-013` — a sealed checkpoint that could not be validated from its own tag.** `GATE-2-CP-0001`
was sealed at `BLOCKED` with `currentCommit` `HEAD`; the historical check failed on it the moment
this checkpoint anchored it. Root cause: the protocol let that status keep the symbolic HEAD, the
seal tool sealed it, and validation from a tag required the tag to be spelled. Repaired in the
tooling by the operator's decision, `ADR-0023`. Recorded as `LSN-0050`.

**`G2-F-014` — the same race in a second smoke.** The full verification's fresh installation
failed one Foundation smoke check it could not name; once the scenario named it, both Prometheus
targets read `down` before the scrape that follows a fresh start. Root cause: `G2-F-012`'s class, in
code `GRD-0051` did not cover. Recorded against `LSN-0049` as a `GUARDRAIL_FAILURE`.

**The closure was first written into a sealed checkpoint.** `GATE-2-CP-0001/NEXT.md` described the
closure as edits inside it, and they were made there before the seal's tag made the conflict
visible. The working copy was restored and the closure moved to this checkpoint on the operator's
decision; what the first attempt recorded is kept in `DECISIONS.md`.

## What repeated

`LSN-0049`: a metric read before the observer's cycle, again, an hour after the lesson was written.
Its guardrail named the gateway smoke's function, so the Foundation smoke carried the same race
unguarded. That is a `GUARDRAIL_FAILURE`, and the control was investigated rather than only the
defect: `GRD-0051` is now a syntax-tree scan of every script that reads Prometheus, with a null
control, and the failure is resolved in this checkpoint.

`LSN-0010`: a recorded command that cannot be replayed. The validator refused it before commit, so
`GRD-0011` held and this is a recurrence, not a `GUARDRAIL_FAILURE`. The recorder itself still
accepts such a command; that is `R-G2-010` in `RISKS.md`.

## What was learned

A refusal that is quoted back as a correction has to name the defect it found, not the test it
applied. Two commits for one fact have an order, and only one of the two orders is safe to read
between. A check of what another process observes on its own cycle waits for that cycle. A seal is
only as good as the state it seals: a checkpoint has to name the tag it will be validated from. And a
checkpoint's next action can itself be wrong: a sealed checkpoint is closed by its successor.

## What should become a guardrail

| Item | Control | Kind | Where | What breaks without it |
|---|---|---|---|---|
| A wrong-typed value refused as a missing one | `test_content_of_the_wrong_type_is_refused_by_its_real_defect` | test | `services/agent-runtime/tests/test_protocol.py` | the one repair quotes a false reason and the run fails with the same answer |
| A terminal state visible before its event | `test_a_terminal_state_is_never_visible_before_its_terminal_event`, `test_the_workflow_writes_the_terminal_event_before_the_terminal_state` | test | `services/agent-runtime/tests/test_engine.py`, `tests/test_gate2_agent_runtime.py` | a reader that waits for a terminal state finds a log that never ended |
| A metric read before its scrape | `test_every_script_that_reads_prometheus_waits_for_a_scrape`, its null control, and one behavioural test per smoke | test | `tests/test_gate2_agent_runtime.py`, `tests/test_gate1_model_gateway.py` | a smoke passes or fails by how long the stack has been up |
| A checkpoint sealed without naming its own tag | `test_sealing_refuses_a_state_that_does_not_name_its_own_tag`, `test_a_symbolic_head_validates_from_its_own_canonical_tag` | test | `tests/test_development_ledger.py` | a checkpoint is sealed in a state it can never be validated from |

## New lessons

| Lesson | Status | Guarded by |
|---|---|---|
| `LSN-0047` — a refusal that misnames the defect spends the only repair on the wrong correction | `GUARDED` | `GRD-0049` |
| `LSN-0048` — a state and the event that explains it, written in two commits, are written event first | `GUARDED` | `GRD-0050` |
| `LSN-0049` — a metric read the instant after the call that moved it is read before the scrape | `GUARDED` | `GRD-0051` |
| `LSN-0050` — a checkpoint sealed without naming its own tag cannot be validated from that tag | `GUARDED` | `GRD-0052` |

## Updated lessons

| Lesson | Change | Reason |
|---|---|---|
| `LSN-0049` | `GUARDRAIL_FAILURE` recorded and resolved; `GRD-0051` widened to the class | `G2-F-014`: the class recurred in the Foundation smoke, outside the one function the guardrail named. |
| `LSN-0010` | `recurrenceCount` incremented | Three unreplayable diagnostic records; `validate_checkpoint.py` refused them before commit, so `GRD-0011` held. |

## Retired lessons

| Lesson | Superseded by | Reason |
|---|---|---|
| _none_ | | |
