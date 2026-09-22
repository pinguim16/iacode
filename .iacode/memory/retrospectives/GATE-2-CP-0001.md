# Retrospective — GATE 2 — AGENT RUNTIME / GATE-2-CP-0001

Record observations, decisions and evidence. Never record private chain-of-thought, and never record
a secret. Every claim points at an artifact in this repository.

## What went well

**Putting the turn loop behind ports made the Gate testable without its infrastructure.** The
engine performs no I/O: it asks `Effects`, and the worker supplies each method as a Temporal
activity. The result is 209 cases in `services/agent-runtime/tests/` that exercise stages, budgets,
the repair, the tool pause, cancellation and isolation with no provider, no database and no workflow
engine — and a workflow module that contains no logic to get wrong. Evidence:
`services/agent-runtime/src/iacode_agent_runtime/engine.py`,
`services/orchestrator/src/iacode_orchestrator/workflows/agent_run.py`, `WorkflowDeterminismTests`.

**The rehearsal harness turned three unprovable claims into three recorded runs.** Durability,
cancellation and the deadline all needed the real workflow, a real Temporal server and a real
container restart, and all three needed an agent that asks for a tool — which no shipped profile may
have. `services/orchestrator/rehearsal/` supplies exactly one substitution, the model, and lives
outside the shipped source so the running worker cannot import it. Evidence:
`scripts/iacode/scenarios/agent_runtime_durability.py`,
`scripts/iacode/scenarios/agent_runtime_cancellation.py`,
`scripts/iacode/scenarios/agent_runtime_deadline.py`.

**Deriving the evidence from the canonical checklist caught the rows that had none.** The
requirement matrix was filled by re-reading each row's artifact and evidence columns and keeping
only references that resolve. Two rows came back empty, and both were real gaps — a missing
retrospective and a frontend row that named a directory rather than a file — rather than something a
reviewer would have had to notice.

**The Red Team's null control did its job twice.** `G2-N` reported an escape on the first run
because the scan read a docstring that mentions the gateway's error module, and the control made the
difference between a scan that was wrong and a delivery that was. The scan was rewritten to read
imports and non-docstring identifiers, and it now carries its own mutated-module check.

## What failed

**A `\b` written through a shell heredoc became a backspace, and a control silently matched
nothing.** `test_the_page_offers_nothing_that_would_execute_a_tool` compiled, ran and found zero
controls to inspect; only its own "the scan found nothing" assertion caught it. Root cause: the test
was edited through a bash heredoc, which consumed the escape. Recorded as `LSN-0041`.

**Alembic and SQLAlchemy apply a naming convention to a `CHECK` constraint and not to a `UNIQUE`
one, and the first migration got both backwards.** `op.drop_constraint("ck_task_runs_status_is_known")`
produced `ck_task_runs_ck_task_runs_status_is_known`, and the unique constraints were created under
one name and dropped under another, so the downgrade failed for three suites at once. Root cause:
the convention is applied only when its template contains `%(constraint_name)s`. Repaired in
`apps/api/migrations/versions/0003_agent_runtime.py`, which now states the asymmetry where the code
is. Recorded as `LSN-0042`.

**The first attempt at the deadline scenario waited out its whole timeout against a queue nobody
was polling.** The rehearsal worker prints that it started *before* it begins polling, and the
scenario was reading that log line. Root cause: a log line is not the observable fact; Temporal's
own view of the task queue is. Repaired by asking `DescribeTaskQueue`, the same question the
worker's healthcheck asks. Recorded as `LSN-0043`.

**A `version` column was declared twice with two meanings.** `Agent` and `AgentTeam` inherit an
optimistic-locking `version` from `TimestampedEntity`, and the first draft of the schema added a
profile version under the same name. Caught before the migration was applied, by the Gate 0 test
that asserts every lifecycle entity carries a lock counter. The columns are now `profile_version`.

**The wall-clock deadline fired on time and recorded nothing.** A run with a ten-second
deadline was still `RUNNING` two minutes later; Temporal showed the workflow had ended at 10.07
seconds with `Activity cancelled`, having written no state, no event and no reason. Two faults in
the same three lines: `asyncio.wait_for` cancels the task that awaits it, which here was the
workflow's own, so the next activity it scheduled was cancelled before it started; and the wait on
the cancelled work expected `CancelledError` while Temporal surfaces a cancelled activity as
`ActivityError`. This is the Gate's most serious defect, and the reason it matters is that from
outside the store a deadline that fires and records nothing is identical to a deadline that never
fires. Only the scenario could see the difference, and it did. Recorded as `LSN-0046`.

**Two counted suites declared cases through a parametrisation, and the TESTS denominator cannot
read one.** The denominator is derived from the source, so a case produced at run time does not
exist as far as the counter is concerned; `derive_counts.py` refuses one rather than miscounting.
It refuses from inside the counting step, though, so the delivery met the defect as ninety-five
ledger cases erroring at once on a message that named the counter. Every such case is now a loop
over a module-level tuple, and a repository scan asks the same question of the same files and names
the function. Recorded as `LSN-0045`.

**Four pre-existing tests had to be updated, and each one was a real statement about the
repository.** `test_structural_tables_exist` and `test_relationships_cascade_deliberately` describe
the schema, which grew; `identifies the product and offers every page it has` and `adds no
conversation capability` describe the shell, which grew a third page. Each was widened to describe
the new fact, and the second was additionally scoped to the page rather than the navigation so it
keeps meaning what it meant.

## What repeated

`LSN-0038` — one classification written twice. It appeared twice in this Gate, in two different
shapes: the run state vocabulary, which is now derived from `iacode_contracts.agent_runtime` by the
runtime, the database and the API alike; and the `version` column above. Neither reached a
delivered artefact, and the lesson stays `GUARDED`: the control that caught the second one is the
Gate 0 convention test. Recorded on the lesson as a recurrence rather than as a
`GUARDRAIL_FAILURE`, because the guardrail held.

No other lesson's `recurrenceKey` matched a failure of this Gate. No `GUARDRAIL_FAILURE` occurred.

## What was learned

**A boundary is only a boundary if a scan can see it.** "The runtime never reaches a provider"
became checkable the moment the runtime stopped importing the gateway package and started speaking
its published contract: the claim is now a property of the dependency graph rather than of anybody's
care. The same move made "the runtime executes nothing" checkable, because there is no execution
module imported anywhere in the boundary to begin with.

**A scan that reads prose protects the wording, not the rule.** Three controls in this Gate had to
be rewritten to read the AST — imports, call targets and non-docstring identifiers — because the
first versions fired on a docstring that explained the rule they were enforcing. A control that
forces the explanation out of the file is a control making the code worse.

**A qualified name is not the same as a bare one.** `os.replace` renames a file and `str.replace`
substitutes a substring; `compile` turns data into code and `re.compile` does not. A scan that
matches the last segment of a call will either be weakened until it passes or forbid ordinary code.

**A log line is not an observable fact about another process.** It says what a process intended to
do next, not what it is doing.

## What should become a guardrail

| Item | Control | Kind | Where | What breaks without it |
|---|---|---|---|---|
| A regex escape mangled by a shell heredoc | `test_the_page_offers_nothing_that_would_execute_a_tool` asserts the scan found controls before judging them | test | `tests/test_gate2_agent_runtime.py` | a control silently matches nothing and reports success |
| A constraint named under the wrong convention | `Gate2MigrationTests.test_the_agent_runtime_migration_is_reversible` applies and reverses the migration against a disposable database | test | `apps/api/tests/integration/test_migrations.py` | a downgrade fails, and every suite that reverses a migration fails with it |
| Waiting on a log line instead of on the fact | `wait_for_poller` asks Temporal's `DescribeTaskQueue` | invariant | `scripts/iacode/scenarios/agent_runtime_durability.py` | a scenario times out against a queue nobody polls and reports a defect that does not exist |
| A limit that fires and records nothing | `scripts/iacode/scenarios/agent_runtime_deadline.py` asks the store what the run became, and `DeadlineEnforcementTests` refuses the shape that caused it | automated-check | `scripts/iacode/scenarios/`, `tests/test_gate2_agent_runtime.py` | a deadline that fires, kills the run and leaves the row RUNNING for ever |
| A counted suite that expands at run time | `CountedSuiteExpansionTests` scans every counted pytest suite and names the function | test | `tests/test_gate2_agent_runtime.py` | the whole ledger errors on a message that names the counter rather than the file |
| A tool request reaching an executor | `ToolExecutionBoundaryTests`, `RepositoryToolExecutionBoundaryTests`, Red Team `G2-F` and `G2-G` | test | `services/agent-runtime/tests/test_boundary.py`, `tests/test_gate2_agent_runtime.py` | a model gets the machine, in the Gate before the one that designs the isolation |
| Workflow code that cannot be replayed | `WorkflowDeterminismTests` and Red Team `G2-U`, each with a mutated-module control | test | `tests/test_gate2_agent_runtime.py` | a run corrupts itself on replay, visibly only under load |

## New lessons

| Lesson | Status | Guarded by |
|---|---|---|
| `LSN-0041` — a shell heredoc consumes a regex escape, and the control silently matches nothing | `GUARDED` | `GRD-0043` |
| `LSN-0042` — a naming convention applies to a CHECK constraint and not to a UNIQUE one | `GUARDED` | `GRD-0044` |
| `LSN-0043` — a log line is not evidence that another process is ready | `GUARDED` | `GRD-0045` |
| `LSN-0044` — a boundary scan must read the AST, and must fire on a mutated module | `GUARDED` | `GRD-0046` |
| `LSN-0045` — a counted suite must declare its cases statically | `GUARDED` | `GRD-0047` |
| `LSN-0046` — a timeout that cancels its own task leaves nothing able to record what happened | `GUARDED` | `GRD-0048` |

## Updated lessons

| Lesson | Change | Reason |
|---|---|---|
| `LSN-0038` | `recurrenceCount` incremented | The class appeared twice in this Gate and was caught both times by existing controls; the guardrail held, so the lesson stays `GUARDED`. |

## Retired lessons

| Lesson | Superseded by | Reason |
|---|---|---|
| _none_ | | |
