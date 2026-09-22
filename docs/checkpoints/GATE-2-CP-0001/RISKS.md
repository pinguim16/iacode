# Risks — GATE-2-CP-0001

Each risk names what would make it real, what currently holds it down, and what would have to change
for it to stop being a risk.

## Open

**R-G2-001 — The provider's daily quota is exhausted, so no live model call can be made.**
Severity: HIGH. This is the Gate's blocker. Every paid model in the DevWorld catalogue answers `429
RATE_LIMITED` with `retryAfterSeconds` of roughly 14.6 hours, and the free tier answers `503
PROVIDER_UNAVAILABLE` for all but one very slow model. `IACODE_GATEWAY_SMOKE_MODEL` is configuration
and is never substituted — `GATE-1-CP-0001` recorded that decision, and both smoke scripts refuse to
pick a different model — so checklist rows 19.1, 19.2 and 19.5 cannot be satisfied in this session.
Held down by: nothing in this repository; it is an account condition. Closes when the quota resets
and `scripts/iacode/agent_runtime_smoke.py` runs green, or when the operator changes the configured
smoke model deliberately and records that decision.

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

## Closed in this Gate

**A deadline that fired and recorded nothing.** The most serious defect of this Gate, and the
one a static reading could not have found: the workflow ended exactly on time and left the run
`RUNNING` for ever. Recorded as `G2-F-008` and `LSN-0046`; the deadline scenario `GRD-0048` now
asks the store what the run became, and five static assertions refuse the shape that caused it.

**A `version` column meaning two things.** Caught before the migration was applied. Now
`profile_version`. Recorded as `G2-F-005`, a recurrence of `LSN-0038`; the guardrail held.

**A control that matched nothing and said so.** Recorded as `G2-F-001` and `LSN-0041`; the
repository-wide scan `GRD-0043` now prevents the class.

**A migration that applied and would not reverse.** Recorded as `G2-F-002` and `LSN-0042`; the
reversibility gate `GRD-0044` now runs it both ways against a disposable database.

**A scenario that waited on a log line.** Recorded as `G2-F-003` and `LSN-0043`; readiness is now
asked of Temporal, and `GRD-0045` refuses the log-line path.

**Three boundary scans that read prose.** Recorded as `G2-F-004` and `LSN-0044`; every scan now
reads the syntax tree and carries a control that must fire on a mutated module, which is `GRD-0046`.
