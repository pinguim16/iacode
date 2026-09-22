# Risks — GATE-2-CP-0002

Each risk names what would make it real, what currently holds it down, and what would have to change
for it to stop being a risk. `R-G2-002` to `R-G2-006` are the Gate's own, carried from
`GATE-2-CP-0001`; `R-G2-007` onwards were raised by the closure.

## Open

**R-G2-002 — GATE 3 could implement the executor on the wrong side of the boundary.** Severity:
HIGH. A tool request is recorded and waited on; nothing executes it. The next Gate builds the thing
that does. If that executor is placed inside `iacode_agent_runtime` rather than behind the store,
every boundary scan in this Gate becomes a scan of a module that now executes. Held down by:
`ADR-0021` states where the executor belongs, and `RepositoryToolExecutionBoundaryTests` and
`ToolExecutionBoundaryTests` will fail the moment an execution import appears inside the runtime —
which is the outcome wanted, because it turns the mistake into a red test instead of a capability.

**R-G2-003 — A run's history grows without bound in `run_events`.** Severity: MEDIUM. Events are
append-only and nothing prunes them. A long-lived deployment accumulates rows, and the SSE cursor
scan is an index range over a growing table. Held down by: the turn and duration budgets bound how
many events a single run can produce. Not held down at all for the number of runs. Backlog.

**R-G2-004 — The `Effects` protocol and the activity set can drift apart.** Severity: MEDIUM. The
workflow satisfies the protocol by implementing eleven methods, and an activity registered under a
name nothing calls, or a protocol method no activity implements, would fail at run time rather than
at import. Held down by: `WorkflowDeterminismTests.test_every_effect_is_an_activity` compares the
two sets and requires them closed, and the three scenarios execute the whole set for real.

**R-G2-005 — The envelope repair is one turn, and a model that cannot produce the envelope burns
it.** Severity: LOW. An agent whose model consistently answers in prose costs two model calls per
run and fails. That is the designed behaviour and it is bounded, but it is also a cost with nothing
to show for it. Held down by: the budget. Backlog: a profile-level record of repair rate would show
which models are unsuitable before a user pays to find out.

**R-G2-006 — `ensure_registered()` fingerprints the profile definitions and rebuilds on change.**
Severity: LOW. Two workers starting at the same moment against the same changed definitions both
attempt the bootstrap. The write is idempotent and guarded by a unique constraint, so the loser
retries rather than corrupts; but the losing side logs an error that reads worse than it is.

**R-G2-007 — Terminal state and terminal event are still two commits.** Severity: LOW. `G2-F-010`
ordered them event first, so a reader that sees a terminal state always finds the log closed. The
reverse window remains: a closed log over a row one activity behind, and a crash between the two
leaves that until Temporal retries the second activity. Held down by: the order, `GRD-0050`, and
Temporal's retry of the state activity. Closes when one store operation writes both in one
transaction, which changes an activity contract and was not done inside a closure.

**R-G2-008 — The live evidence now depends on the operator's OpenAI account.** Severity: MEDIUM.
The smoke model and the default model of this machine are `openai:gpt-4o-mini`, by the operator's
decision; DevWorld remains declared and its previous values are kept beside the current ones in the
ignored configuration. Held down by: nothing selects a model on its own — a smoke names its model
and a route names no candidate. Changes only by an operator decision, recorded as such.

**R-G2-009 — An OpenAI credential was shared in a chat transcript during the closure.** Severity:
HIGH until rotated. It never entered the repository, a checkpoint or a commit, and the secret scan
of `checkpointValidation` confirms the tree carries none. Held down by: nothing inside the
repository can revoke a credential. Closes when the operator revokes that credential and
configures a new one only in `infra/compose/.env`.

**R-G2-010 — Three ledger controls answer later than they could.** Severity: LOW. The closure met
three gaps that a later control caught: `record_command.py` records a command that
`validate_checkpoint.py` will refuse (`G2-F-011`); `validate_lessons.py` accepts a guardrail
registry entry whose own reference does not resolve, which the internal mirror caught as MIR-006;
and the rendered `LESSONS.md` had not been regenerated since `LSN-0036`, with no control noticing.
Held down by: the later control in each case. Backlog: refuse each at the point of writing.

**R-G2-011 — A stream opened on a finished run ends after its first page.** Severity: LOW. The SSE
endpoint reads the run once, and when it is already terminal it returns after the first page of at
most two hundred events. A run with more events than that, streamed from the start after it ended,
is truncated. Held down by: the turn and duration budgets, which keep a run's history far below
that size today. Backlog: drain every page before ending a stream on a terminal run.

**R-G2-012 — A delivered test that can only skip.** Severity: LOW.
`Gate2AdrTests.test_the_index_lists_them` skips when `docs/adr/README.md` is absent, and it is
absent, so the ADR index it guards has never been checked. It predates the closure and was
counted, like the other conditional skip, as executed without failure. Held down by:
`Gate2AdrTests.test_every_decision_is_recorded`, which checks the ADR files themselves. Backlog: create the index
or turn the skip into a failure.

**R-G2-013 — The observability check proves that some request was scraped, not this one.**
Severity: LOW. `G2-F-012` made the check wait for a scrape; it still counts every gateway request
since the API started, so on a long-running stack an earlier request satisfies it. Held down by: the
inference and persistence checks, which attribute this call to the configured model. Backlog: query
the counter's increase over the smoke's own window.

## Closed by the closure

**R-G2-001 — The provider's daily quota was exhausted.** Closed by the operator's decision to
register OpenAI as a second provider and point the live smoke at `openai:gpt-4o-mini`, recorded in
`DECISIONS.md`; the smoke model was named, not substituted. The live evidence is the gateway smoke `cmd-0005`, the agent runtime smoke `cmd-0006`, the persisted provenance `cmd-0007`.

**A planner's array refused as missing content.** `G2-F-009`. `LSN-0047`, `GRD-0049`.

**A finished run whose log had not finished.** `G2-F-010`. `LSN-0048`, `GRD-0050`.

**A metric read before its scrape.** `G2-F-012`. `LSN-0049`, `GRD-0051`.

**A sealed checkpoint that could not be validated from its own tag.** `G2-F-013`. `ADR-0023`,
`LSN-0050`, `GRD-0052`.

**The same race in the Foundation smoke.** `G2-F-014`, a `GUARDRAIL_FAILURE` against `LSN-0049`,
resolved; `GRD-0051` widened to every Prometheus reader.
