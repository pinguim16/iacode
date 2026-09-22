# Decisions — GATE-2-CP-0001

Structural decisions are ADRs. What follows is the checkpoint-local reasoning: choices made inside
this Gate that shaped the delivery but do not change the architecture.

## Recorded as ADRs

| Decision | ADR |
|---|---|
| The runtime is a library, Temporal is its durable engine, and the schema is shared | `ADR-0020` |
| A tool request is recorded and waited on; execution belongs to GATE 3 | `ADR-0021` |
| An agent turn is one versioned envelope, parsed strictly, with exactly one repair | `ADR-0022` |

## Checkpoint-local decisions

**The runtime speaks the gateway's HTTP contract rather than importing its package.** The claim
this Gate has to make is that a model is never reached except through the Model Gateway. As an
import that claim is a habit, and a future refactor can break it without anybody noticing. As a
dependency it is a fact the scan in `RuntimeDependencyDirectionTests` can read off the graph:
`iacode_agent_runtime` imports no provider SDK and no `iacode_model_gateway`, so there is no path to
a provider that does not leave the process through `/api/v1/gateway/infer`.

**The engine performs no I/O; it asks `Effects`.** Every side effect the turn loop needs — call the
model, append an event, record a tool request, wait for a result — is a method on a protocol the
worker satisfies with a Temporal activity. That is what makes the loop testable without Temporal,
and it is also what keeps the workflow module free of logic that could be got wrong: the workflow
sequences activities and holds no branch a test would have to reach through a replay.

**The persistence package was extracted rather than imported across services.** The runtime, the
API and the worker all need the same tables. Importing `iacode_api` from the worker would make the
web application a dependency of the durable engine, which inverts the direction the architecture
depends on everywhere else. `packages/persistence` is the shared schema, and `apps/api/.../db/engine.py`
remains as a thin delegation so Gate 0's and Gate 1's call sites keep working unchanged.

**The state vocabulary has exactly one definition, in `iacode_contracts.agent_runtime`.** The
runtime, the database CHECK constraint and the API all derive `AGENT_RUN_STATES` and
`ALLOWED_RUN_TRANSITIONS` from it. A second copy is the failure class `LSN-0038` already records:
two lists that agree until a state is added to one of them.

**A profile version is `profile_version`, never `version`.** `version` is the optimistic-locking
counter every lifecycle entity inherits. A column that means two things is two bugs waiting for the
first reader who assumes the other meaning.

**No shipped agent profile declares an allowed action.** `allowedActions` is `[]` in all four
profiles. The pause-and-resume path is real and is exercised, but the only agent that can ask for a
tool in this Gate is the scripted one in `services/orchestrator/rehearsal/`, which lives outside the
shipped source tree so the running worker cannot import it. A profile that declared an action would
be a capability nothing in this Gate can satisfy.

**A tool request pauses the run and nothing executes it.** `WAITING_FOR_TOOL` is a durable state,
not a spin. The result arrives over the same store the API writes through, which is the interface
Gate 3's sandbox will implement. No executor, no shell, no filesystem write, no Git. A stub executor
that returned success would be a fake feature, and it would make the Gate's central claim untestable
by making it trivially true.

**The repair is charged to the budget.** An agent that answers with something the envelope parser
refuses gets exactly one corrective turn, and that turn costs a model call like any other. A free
retry is an unbounded loop with a polite name.

**The budget is charged before the call, not after it.** A call that is started and then fails still
consumed a provider's attention and possibly a bill. Charging on success would let a run exceed its
budget by exactly the number of calls that failed.

**A cost is reported only when every call in the run is priced.** One unpriced call makes the total
a lower bound presented as a total. `_usage_for` returns `None` rather than a number that reads as
complete.

**The task never enters the system channel.** Context is assembled from named channels — `RUNTIME`,
`ROLE`, `TASK`, `ARTIFACT`, `TOOL_RESULT` — and the instruction hierarchy is a property of where
content is placed rather than of how it is worded. A task appended to the system prompt is a task
that can rewrite the runtime's own rules.

**The rehearsal harness substitutes exactly one thing: the model.** Durability, cancellation and the
deadline each need a real workflow, a real Temporal server and a real container restart. The harness
supplies a scripted model so an agent can ask for a tool, and changes nothing else. It is mounted at
`/app/rehearsal` while the worker runs from `PYTHONPATH=/app/src`, so the substitution cannot reach
a shipped run.

**Readiness is asked of Temporal, not read from a log line.** `DescribeTaskQueue` reports whether
the queue has a poller. The worker's own container healthcheck asks the same question, so the
scenario and the orchestration agree about what "ready" means. See `LSN-0043`.

**Every boundary scan reads the syntax tree and carries a null control.** Imports by module, calls
by their full dotted name, identifiers with docstrings excluded — and, for each scan, a mutated
module that it must fire on. A scan that matches text forces the explanation out of the file and
cannot tell `str.replace` from `os.replace`. See `LSN-0044`.

**The migration names a CHECK constraint by its bare name and a UNIQUE constraint by its declared
one.** The naming convention is applied only where its template carries the constraint-name token,
which the CHECK template does and the UNIQUE template does not. The asymmetry is stated in a comment
in `apps/api/migrations/versions/0003_agent_runtime.py`, where the next reader will be standing. See
`LSN-0042`.

**The deadline races an explicit child task rather than wrapping the engine in a timeout.**
`asyncio.wait_for` enforces its timeout by cancelling the task that awaits it, which inside a
workflow is the workflow's own task: the timer then fires correctly and the run dies before it can
write down that it died. The engine runs as its own task, raced against a timer, and the wait on
that task accepts `ActivityError` as well as `CancelledError`, because that is what Temporal raises
when a cancelled activity surfaces. See `LSN-0046`.

**Model output is rendered as text in the frontend, never as markup.** The operational page shows a
run's result, its events and its pending tool request, and offers no control that would execute
anything. Both are asserted: one by the component spec, one by a repository-level scan.

## Findings this Gate raised against itself

| Finding | Severity | What it was | Lesson | Guardrail |
|---|---|---|---|---|
| `G2-F-001` | HIGH | a regex escape was consumed by the editing path and left a control character, so a frontend scan compiled, ran, matched nothing and reported success | `LSN-0041` | `GRD-0043` |
| `G2-F-002` | HIGH | the first migration named a CHECK constraint under the convention and a UNIQUE constraint against it, producing `ck_task_runs_ck_task_runs_status_is_known` and a downgrade that could not find its own constraint | `LSN-0042` | `GRD-0044` |
| `G2-F-003` | MEDIUM | the deadline scenario waited for the rehearsal worker's start-up log line, which is printed before polling begins, and then waited out its whole timeout against a queue nobody was polling | `LSN-0043` | `GRD-0045` |
| `G2-F-004` | HIGH | three boundary scans reported escapes that were all false positives — a docstring, a deny-list and `str.replace` read as `os.replace` — because they matched text rather than code | `LSN-0044` | `GRD-0046` |
| `G2-F-005` | MEDIUM | recurrence of `LSN-0038`: a profile version was added under the name `version`, which every lifecycle entity already uses for its optimistic lock. Caught before the migration was applied, by the Gate 0 convention test; the guardrail held, so this is a recurrence and not a `GUARDRAIL_FAILURE` | `LSN-0038` | `GRD-0040` |
| `G2-F-006` | MEDIUM | two requirement rows carried no evidence that resolves — a missing retrospective and a frontend row naming a directory rather than a file — and both looked covered because each also named an artifact that exists | — | `derive_requirements.py`, `check_completeness.py` |
| `G2-F-007` | MEDIUM | two counted suites declared cases through `pytest.mark.parametrize`, which the statically derived TESTS denominator cannot reproduce. The counter already refuses one, but it refuses from inside the counting step, so the delivery met it as ninety-five ledger cases erroring at once rather than as a statement about one function | `LSN-0045` | `GRD-0047` |
| `G2-F-008` | CRITICAL | the wall-clock deadline fired on time and recorded nothing: `asyncio.wait_for` cancelled the workflow's own task, and the handler waiting on the cancelled work expected `CancelledError` while Temporal raises `ActivityError`. The workflow died with `Activity cancelled` at 10.07s and the run row stayed `RUNNING` for ever — indistinguishable from no deadline at all | `LSN-0046` | `GRD-0048` |

No `GUARDRAIL_FAILURE` occurred in this Gate.
