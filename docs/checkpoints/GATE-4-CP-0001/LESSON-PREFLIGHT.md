# Lesson Preflight

- Gate: `GATE-4`
- Scope: `quality engine, evaluation runners, immutable evidence store, verdict rules, false-PASS rejection, reproducible evidence, sandboxed execution, agent-runtime integration, promotion evidence`
- Technologies: _none declared_
- Modules: _none declared_
- Generated: `2026-10-10T03:43:21Z`
- Lessons considered: 88
- Lessons applicable: 87

Every applicable lesson below is a requirement of this Gate. The derived identifiers must
appear in `REQUIREMENTS-MATRIX.json`, and the Delivery Completeness Validator fails the
delivery when one is absent.

| Lesson | Status | Severity | Derived requirement | Required check |
|---|---|---|---|---|
| `LSN-0001` Checkpoint validation must succeed from a detached checkout of the checkpoint tag | `GUARDED` | HIGH | `LESSON-REQ-0001` | Validate the checkpoint from a clean clone detached at its own tag, not only on the branch. |
| `LSN-0002` A file inventory must be recomputed from the repository, never trusted as an assertion | `GUARDED` | HIGH | `LESSON-REQ-0002` | Declare every changed path with a reason before finalizing and let the tooling bind the hashes. |
| `LSN-0003` Every operation attempt must be auditable, including a refusal decided before execution | `GUARDED` | HIGH | `LESSON-REQ-0003` | Confirm that a refused operation appends its attempt to the ledger before returning an error. |
| `LSN-0004` A checkpoint may never claim readiness while it also claims to be blocked | `GUARDED` | CRITICAL | `LESSON-REQ-0004` | Verify that the checkpoint carries no blocker while it claims to be ready for review. |
| `LSN-0005` A PASS requires evidence that can be executed or resolved, not a statement | `GUARDED` | CRITICAL | `LESSON-REQ-0005` | Attach a resolvable evidence reference to every PASS recorded by this Gate. |
| `LSN-0006` The repository must be self-contained; a specification may not live outside it | `GUARDED` | MEDIUM | `LESSON-REQ-0006` | Confirm that every specification this Gate depends on is committed to the repository. |
| `LSN-0007` Independent validation cannot be declared by the run that did the work | `GUARDED` | CRITICAL | `LESSON-REQ-0007` | Close the implementing run at an internal status and leave the independent verdict pending. |
| `LSN-0008` Requirement completeness must be total and evidence-backed before handoff | `GUARDED` | CRITICAL | `LESSON-REQ-0008` | Extract every requirement before implementing and audit completeness before handoff. |
| `LSN-0009` A red gate requires rework, never a waiver, and never a weakened check | `GUARDED` | CRITICAL | `LESSON-REQ-0009` | Run the Green Keeper until every mandatory gate is green, repairing causes rather than checks. |
| `LSN-0010` A recorded command must carry runtime, working directory, commit and purpose to be replayable | `GUARDED` | HIGH | `LESSON-REQ-0010` | Record commands with the tooling so each one is executable from its declared working directory. |
| `LSN-0011` A control over a checkpoint's own evidence must be scoped to the moment it matters | `GUARDED` | MEDIUM | `LESSON-REQ-0011` | Check whether any new control would be invalidated by the evidence its own run produces. |
| `LSN-0012` Sealed checkpoints and their tags are immutable, and tooling must keep validating them | `GUARDED` | CRITICAL | `LESSON-REQ-0012` | Confirm that every sealed checkpoint still validates under the tooling this Gate changes. |
| `LSN-0013` An installed capability must be detected by resolved path, not by a bare command lookup | `CONFIRMED` | MEDIUM | `LESSON-REQ-0013` | When this Gate records a capability, resolve the executable path before concluding anything about availability. |
| `LSN-0014` Evidence must be recorded as it happens, not reconstructed at the end of a run | `GUARDED` | MEDIUM | `LESSON-REQ-0014` | Record each command through the tooling while the work happens. |
| `LSN-0015` Every positive terminal status needs one shared promotion invariant | `GUARDED` | CRITICAL | `LESSON-REQ-0015` | Confirm that every positive terminal status this Gate can produce is covered by the shared promotion invariant, not only the status this delivery ends at. |
| `LSN-0016` A mandatory set must be closed by policy, never chosen by the caller | `GUARDED` | CRITICAL | `LESSON-REQ-0016` | Confirm that every control whose scope could be narrowed by an argument derives that scope from policy instead. |
| `LSN-0017` A completeness denominator must come from a source the delivery does not own | `GUARDED` | CRITICAL | `LESSON-REQ-0017` | Confirm that the expected requirement set is derived independently and compared as a set, not only as a count. |
| `LSN-0018` A structured reference must be resolved, not merely well typed | `GUARDED` | CRITICAL | `LESSON-REQ-0018` | Confirm that every reference this Gate records is resolved by a tool, not accepted as a string. |
| `LSN-0019` A derived artifact must carry a fingerprint of the inputs that produced it | `GUARDED` | HIGH | `LESSON-REQ-0019` | Confirm that every derived artifact this Gate stores can be recomputed and is recomputed during validation. |
| `LSN-0020` Evidence produced from a dirty tree needs immutable input identity | `GUARDED` | HIGH | `LESSON-REQ-0020` | Confirm that every recorded command binds its inputs by content and that no timestamp in the ledger is later than the recorded end of the run. |
| `LSN-0021` Sealed history needs an anchor outside the content it describes | `GUARDED` | CRITICAL | `LESSON-REQ-0021` | Confirm that the integrity chain still resolves for every sealed checkpoint and that this Gate anchors every sealed predecessor. |
| `LSN-0022` An authoritative count must be derived once, never maintained by hand twice | `GUARDED` | CRITICAL | `LESSON-REQ-0022` | Confirm that every count used as evidence in this Gate is derived from one source and verified where it is quoted. |
| `LSN-0023` A lesson must cite a source that actually records the finding it claims | `GUARDED` | MEDIUM | `LESSON-REQ-0023` | Confirm that every lesson this Gate writes or updates cites a checkpoint that records the finding identifier it names. |
| `LSN-0024` A control is finished only when its positive path has been executed, not only its refusals | `GUARDED` | CRITICAL | `LESSON-REQ-0024` | For every control this Gate adds or changes that gates a status, execute the path that reaches the status, not only the paths that are refused. |
| `LSN-0025` A generic guardrail derives repository state instead of naming today's checkpoint | `GUARDED` | CRITICAL | `LESSON-REQ-0025` | Confirm that no generic guard, test or policy in this Gate names a historical checkpoint to decide behaviour, and that any such rule is derived from repository state. |
| `LSN-0026` An adversarial battery without a null-mutation control proves nothing | `GUARDED` | HIGH | `LESSON-REQ-0026` | Run every adversarial battery of this Gate with an unmutated control through the same path, and record its result with the battery. |
| `LSN-0027` A lesson's prose may record a residual limit but may never contradict its status | `GUARDED` | MEDIUM | `LESSON-REQ-0027` | Confirm that every lesson this Gate writes or updates describes limits rather than restating its own status. |
| `LSN-0028` A configuration key that no code reads is a defect, not documentation | `GUARDED` | HIGH | `LESSON-REQ-0028` | Confirm that every configuration key this Gate declares is read by the implementation, or remove it and document the fixed behaviour. |
| `LSN-0029` A required protocol transition must never turn a mandatory gate red | `GUARDED` | CRITICAL | `LESSON-REQ-0029` | Before handoff, execute the protocol transitions this Gate's successor will perform and confirm the mandatory gates stay green. |
| `LSN-0031` An empty applicable set is not a missing required set, and a control must tell them apart | `GUARDED` | CRITICAL | `LESSON-REQ-0030` | For every quality or audit control this Gate adds or changes that operates on a derived set, confirm that an empty applicable set is reported as NOT_APPLICABLE with a justification and that a missing required set is reported as a failure. |
| `LSN-0032` A control written while one Gate was the only Gate stops being a control when the next one starts | `GUARDED` | HIGH | `LESSON-REQ-0031` | For every control this Gate adds or changes, confirm that what it judges is derived from a canonical source rather than written into the control, and that it would still be correct for the Gate after this one. |
| `LSN-0033` A value bound in middleware is absent in the handlers that run outside it | `GUARDED` | MEDIUM | `LESSON-REQ-0032` | For every cross-cutting value this Gate binds in middleware, confirm it is present in the responses produced above that middleware, including error responses. |
| `LSN-0034` Re-deriving what the framework already computed diverges from the framework | `GUARDED` | MEDIUM | `LESSON-REQ-0033` | Where this Gate derives a value the framework already computes, confirm it reads the framework's result rather than recomputing it, and that a test asserts the value rather than only its presence. |
| `LSN-0035` Captured subprocess output decoded or re-emitted with the platform codepage crashes the tool, not the work | `GUARDED` | HIGH | `LESSON-REQ-0034` | Confirm every subprocess capture this Gate adds states its decoder explicitly, that every entry point re-emitting captured output configures its own stream, and that the repository-wide control still passes. |
| `LSN-0036` A gate that runs inside an image measures the image, not the source | `GUARDED` | HIGH | `LESSON-REQ-0035` | For every mandatory gate this Gate adds or changes, confirm that a gate executing inside a built artefact rebuilds that artefact before measuring, and that the repository-wide control still passes. |
| `LSN-0037` A shared control that names an identifier the repository derives stops being a control when that identifier moves | `GUARDED` | MEDIUM | `LESSON-REQ-0036` | Confirm that every control this Gate adds which reasons about an identifier the repository derives -- the current Gate, the newest checkpoint, the head migration -- derives it rather than naming it, and that the repository-wide control still passes. |
| `LSN-0038` Two representations of one concept in one module disagree, and the safer one loses | `GUARDED` | MEDIUM | `LESSON-REQ-0037` | Where this Gate defines a classification twice — once anchored and once embedded — confirm one definition is authoritative and the other derives from it or is removed. |
| `LSN-0039` A test that writes to the operational database leaves production data behind | `GUARDED` | HIGH | `LESSON-REQ-0038` | For every test this Gate adds that writes to a shared service rather than to a disposable one, confirm it removes what it created and that an invariant detects residue. |
| `LSN-0040` A control that judges sealed history only runs once a successor anchors it | `GUARDED` | CRITICAL | `LESSON-REQ-0039` | Confirm that every sealed predecessor this Gate anchors validates from a detached checkout of its own tag in a published clone (Git's transport, never a copy of the local object store), that every commit sealed evidence names is reachable from a published reference, and that no command this Gate records declares an input the repository does not carry. |
| `LSN-0041` An editing path that consumes a backslash escape leaves a control character, and the control it belonged to silently matches nothing | `GUARDED` | HIGH | `LESSON-REQ-0040` | Confirm that every scan this Gate adds asserts it found something before judging it, and that no source file carries a stray control character. |
| `LSN-0042` A naming convention rewrites a CHECK constraint's name and leaves a UNIQUE constraint's alone | `GUARDED` | HIGH | `LESSON-REQ-0041` | For every migration this Gate adds, confirm it is applied and reversed against a disposable database, and that autogenerate finds nothing left to do afterwards. |
| `LSN-0043` A log line is not evidence that another process is ready | `GUARDED` | MEDIUM | `LESSON-REQ-0042` | For every wait this Gate adds on another process, confirm it asks that process or its server for the state rather than reading a log line. |
| `LSN-0044` A boundary scan must read the code rather than the prose, and must be shown to fire on a mutated module | `GUARDED` | HIGH | `LESSON-REQ-0043` | For every boundary scan this Gate adds, confirm it reads the syntax tree rather than the text, and that it carries a control which runs the identical scan over a module that violates the rule. |
| `LSN-0045` A counted test suite must declare its cases statically, because the denominator is read from the source | `GUARDED` | MEDIUM | `LESSON-REQ-0044` | Confirm that every case this Gate adds to a counted suite is declared statically, with table-driven inputs written as a loop rather than as a parametrisation. |
| `LSN-0046` A timeout that cancels the task it runs in leaves nothing able to record what happened | `GUARDED` | CRITICAL | `LESSON-REQ-0045` | For every limit this Gate enforces, confirm that the enforcement path is still able to write when it fires, and that a real run is observed reaching the terminal state with the reason recorded. |
| `LSN-0047` A refusal that misnames the defect spends the only repair on the wrong correction | `GUARDED` | HIGH | `LESSON-REQ-0046` | For every validator whose refusal is sent back as the instruction to correct - to a model through a repair, or to a user - confirm that each distinct defect (absent, wrong type, wrong value) has its own reason, and that a wrong-typed value is never reported as missing. |
| `LSN-0048` A state and the event that explains it, written in two commits, are written event first | `GUARDED` | HIGH | `LESSON-REQ-0047` | Wherever a state and the record that explains it are written in separate commits, confirm which one a reader between the two can see alone, and that it is the one a reader may act on - the record before the state it explains. |
| `LSN-0049` A metric read the instant after the call that moved it is read before the scrape that carries it | `GUARDED` | MEDIUM | `LESSON-REQ-0048` | For every check that reads what another process observes on its own cycle - a scrape, a poll, a flush - confirm that the check waits for at least one full cycle, with a bound, and never repeats the action it is observing to make the observation appear. |
| `LSN-0050` A checkpoint sealed without naming its own tag cannot be validated from that tag | `GUARDED` | HIGH | `LESSON-REQ-0049` | Before sealing a checkpoint at any status, confirm that STATE.json currentCommit names the checkpoint's own canonical tag, and that the sealed content validates from that tag with a detached HEAD. |
| `LSN-0051` A payload one service bounds for another must be bounded as the receiver measures it | `GUARDED` | HIGH | `LESSON-REQ-0050` | For every payload one service bounds and another service accepts or refuses by size, confirm both measure it the same way and that the receiver's bound is not smaller than what the sender may hand over. |
| `LSN-0052` Two processes that meet on a queue must name what crosses it once, and a real run must exercise both | `GUARDED` | HIGH | `LESSON-REQ-0051` | For every payload this Gate sends between two processes, confirm its names are defined once in a shared contract, used by both sides, and exercised once by a run in which neither side is a double. |
| `LSN-0053` A process sweep that reads what a forking process holds waits on the processes it has to kill | `GUARDED` | HIGH | `LESSON-REQ-0052` | For every control that must end processes it did not start, confirm it freezes before it kills, reads nothing a forking process holds, and is attacked on the real engine by a process that detaches and forks. |
| `LSN-0054` A pre-push check narrower than the change's reach lets a red gate reach the public remote | `CONFIRMED` | MEDIUM | `LESSON-REQ-0053` | Before each push, run the lint gate and the repository-wide scans as well as the suites of the change, because a change reaches every control that scans the tree. |
| `LSN-0055` A contract a model must follow has to reach the model, rendered from the definition the parser enforces | `GUARDED` | MEDIUM | `LESSON-REQ-0054` | For every structured answer a model must produce, confirm that the exact shape is in the text every model receives — rendered from the definition the parser enforces, not written beside it — and that a live run of the configured model produces it. |
| `LSN-0056` A result is accepted only from the executor that owns the request, decided when the request is created | `GUARDED` | MEDIUM | `LESSON-REQ-0055` | For every result, verdict or callback that more than one producer could deliver, confirm that the owner is recorded when the work is created, that the origin of a delivery comes from the code path and never from the delivery, and that a delivery from any other origin is refused before it is stored. |
| `LSN-0057` A pinned lock can become unsafe without changing, so advisory state is live evidence | `GUARDED` | CRITICAL | `LESSON-REQ-0056` | For every pinned dependency graph delivered by a Gate, run the current advisory scan against every required source and refuse Critical or High findings without suppressing advisories or narrowing the denominator. |
| `LSN-0058` Container health does not prove Docker Desktop host-port forwarding | `GUARDED` | MEDIUM | `LESSON-REQ-0057` | Exercise every required host-published service through its actual loopback port; do not substitute container health for host reachability. |
| `LSN-0059` A lesson exclusion must declare the scope it excludes | `GUARDED` | MEDIUM | `LESSON-REQ-0058` | Confirm every active lesson excluded from a preflight declares a non-empty scope selector, and that incidental metadata does not narrow applicability. |
| `LSN-0060` Parent and child facts without an ORM relationship require an explicit flush boundary | `GUARDED` | MEDIUM | `LESSON-REQ-0059` | Whenever one transaction inserts parent and child ORM facts using raw foreign-key identifiers without a relationship edge, confirm the parent is flushed before the child is added. |
| `LSN-0061` Cancellation completion must not bypass cleanup acknowledgement | `GUARDED` | MEDIUM | `LESSON-REQ-0060` | For every running task that can be cancelled, prove the lifecycle records cancellation requested before it records cancellation completed. |
| `LSN-0062` Provenance digests are a set even when their sources are distinct | `GUARDED` | MEDIUM | `LESSON-REQ-0061` | Whenever provenance is represented by content digests, normalize it as a unique ordered set rather than assuming each semantic source has different bytes. |
| `LSN-0063` An identity shared across services must satisfy the strictest persistence type and remain stable | `GUARDED` | HIGH | `LESSON-REQ-0062` | For every identity crossing a service boundary, verify it satisfies the strictest persisted representation and is stable across delivery retries. |
| `LSN-0064` A shared execution resource needs an explicit exclusive owner for every owning domain | `GUARDED` | HIGH | `LESSON-REQ-0063` | When another durable domain reuses an owned resource, model its real ownership explicitly, require exactly one owner, and preserve every per-owner exclusivity invariant. |
| `LSN-0065` A shared execution identifier must not be written into a foreign key owned by another domain | `GUARDED` | HIGH | `LESSON-REQ-0064` | For a shared execution contract, prove each durable foreign key is populated only for the domain that owns the referenced row, using trusted ownership context rather than identifier shape. |
| `LSN-0066` Immutable content identity excludes observation time and the first observer | `GUARDED` | HIGH | `LESSON-REQ-0065` | For every content-addressed or reusable immutable record, define material identity separately from creation metadata and ownership provenance. |
| `LSN-0067` Cancellation semantics must survive orchestration-library exception wrapping | `GUARDED` | HIGH | `LESSON-REQ-0066` | For cancellation across an orchestration boundary, test the exception shape the real library delivers and derive outcome from the durable request plus executor acknowledgement rather than the wrapper class alone. |
| `LSN-0068` A bounded parser must apply each content limit only to content it interprets | `GUARDED` | HIGH | `LESSON-REQ-0067` | For every parser-specific content limit applied to a broader inventory, prove unrelated content bypasses that limit while every interpreted candidate remains bounded. |
| `LSN-0069` A polyglot plan binds each check to both its project root and its toolchain | `GUARDED` | HIGH | `LESSON-REQ-0068` | For every polyglot or multi-root project plan, prove each check is expanded at the roots that declared its stack and selects execution policy from the frozen runner rather than one run-wide guessed toolchain. |
| `LSN-0070` Project discovery must separate deployable roots, nested fixtures and check applicability | `GUARDED` | HIGH | `LESSON-REQ-0069` | For project discovery over a monorepo, prove nested fixture manifests do not become execution roots and every non-applicable unit check is derived from the frozen source inventory rather than from a failed command. |
| `LSN-0071` Every quality image must provision snapshots on its oldest runtime and prepare each isolated check | `GUARDED` | HIGH | `LESSON-REQ-0070` | For every shared helper and isolated quality runner, test the oldest pinned runtime actually used by an image and prove each check prepares all dependencies it needs without relying on a previous sandbox session. |
| `LSN-0072` Secret findings and reviewed false positives must share one policy-owned taxonomy | `GUARDED` | HIGH | `LESSON-REQ-0071` | Whenever more than one gate scans secrets, prove all scanners share the policy-owned finding taxonomy and digest-bound allowance source, and that an unallowlisted match remains blocking. |
| `LSN-0073` The canonical lint denominator must cover every detected project root | `GUARDED` | HIGH | `LESSON-REQ-0072` | For every manually scoped repository-wide quality command, derive or test its denominator against the current project inventory so a newly detected root cannot remain outside a green gate. |
| `LSN-0074` An importable source tree is not an installed or repository-configured test environment | `GUARDED` | HIGH | `LESSON-REQ-0073` | For Python tests executed from a nested project root, prove the sandbox provides installed distribution metadata and repository-root policy/configuration without reading or writing the host. |
| `LSN-0075` Offline package installation requires its build backend inside the quality image | `GUARDED` | HIGH | `LESSON-REQ-0074` | Whenever a sandbox performs an offline package installation, prove every declared build backend is pinned in the content-addressed execution image and usable by the non-root runtime. |
| `LSN-0076` Projected nested configuration requires an explicit monorepo root | `GUARDED` | HIGH | `LESSON-REQ-0075` | When repository configuration is projected into a nested project, provide an explicit trusted repository root and prove source-boundary scans do not reinterpret the projection as ownership. |
| `LSN-0077` Harness wait bounds must reflect workload size without changing product deadlines | `GUARDED` | HIGH | `LESSON-REQ-0076` | For a functional harness whose workload cardinality differs materially by scenario, prove its bounded wait covers the largest legitimate execution without weakening the product's own timeout or deadline. |
| `LSN-0078` Evidence recorders must resolve caller-supplied commit references before execution | `GUARDED` | HIGH | `LESSON-REQ-0077` | Before an evidence recorder executes a command, resolve every caller-supplied commit reference to a real canonical commit and normalize repeated provenance inputs. |
| `LSN-0079` Test discovery and the unit runner must cover the same project scope | `GUARDED` | HIGH | `LESSON-REQ-0078` | For every test applicability rule, prove the corresponding closed runner collects the same project scope and that a failing source at each recognized location is observed. |
| `LSN-0080` A failed verification stage must not leave an older PASS report addressable | `GUARDED` | HIGH | `LESSON-REQ-0079` | Whenever a verification stage writes to a reusable report path, prove the old artifact is removed before execution and cannot survive a failed rerun as current evidence. |
| `LSN-0081` Canonical requirement evidence must name a test the repository actually discovers | `GUARDED` | HIGH | `LESSON-REQ-0080` | Before a canonical checklist is accepted, resolve every named test identity against the suite registry rather than treating prose-like test labels as evidence. |
| `LSN-0082` Engineering memory cannot depend on an ephemeral generated report | `GUARDED` | HIGH | `LESSON-REQ-0081` | Keep organizational memory evidence in committed source or checkpoint-owned artifacts; reject references to regenerable runtime output. |
| `LSN-0083` A command that decodes captured UTF-8 must also configure the stream that re-emits it | `GUARDED` | MEDIUM | `LESSON-REQ-0082` | For every executable command that captures text from a child process and prints it, configure both the child decoder and the parent output stream explicitly. |
| `LSN-0084` A historical Gate documentation test must derive the current entry-point state | `GUARDED` | MEDIUM | `LESSON-REQ-0083` | When a predecessor regression test inspects a current entry point, derive current lifecycle identifiers and keep only genuinely historical references fixed. |
| `LSN-0085` A source-based control must assert syntax semantics rather than formatter layout | `GUARDED` | MEDIUM | `LESSON-REQ-0084` | When a control judges source structure, parse the language representation and compare semantic nodes instead of binding the rule to formatter whitespace or quote style. |
| `LSN-0086` A subprocess assertion must preserve the exit code when both streams are empty | `GUARDED` | MEDIUM | `LESSON-REQ-0085` | For every subprocess-backed assertion, preserve return code and a non-empty diagnostic even when the child emits nothing; never add a retry that could conceal the outcome. |
| `LSN-0087` A rehearsal worker must register every workflow activity boundary | `GUARDED` | HIGH | `LESSON-REQ-0086` | Every purpose-built worker that hosts a shared workflow must register every activity boundary that workflow can schedule, including not-applicable branches whose decision is made inside an activity. |
| `LSN-0088` A test inside a built image can consume only inputs copied into that image | `GUARDED` | HIGH | `LESSON-REQ-0087` | Whenever a test runs inside a built image and consumes repository content outside its own copied suite, prove the Dockerfile carries that input and the test resolves the same in-image destination. |

## Why each lesson applies

### LSN-0001 — Checkpoint validation must succeed from a detached checkout of the checkpoint tag

- Reason: applies to every Gate; category checkpoint; severity HIGH; already guarded, so the control must keep holding
- Required check: Validate the checkpoint from a clean clone detached at its own tag, not only on the branch.
- Required evidence: A recorded validate_checkpoint.py run from a detached checkout returning CHECKPOINT_VALID.
- Derived requirement: `LESSON-REQ-0001`

### LSN-0002 — A file inventory must be recomputed from the repository, never trusted as an assertion

- Reason: applies to every Gate; category checkpoint; severity HIGH; already guarded, so the control must keep holding
- Required check: Declare every changed path with a reason before finalizing and let the tooling bind the hashes.
- Required evidence: A FILES.json whose declared change set matches the recomputed one, proven by a passing validation.
- Derived requirement: `LESSON-REQ-0002`

### LSN-0003 — Every operation attempt must be auditable, including a refusal decided before execution

- Reason: applies to every Gate; category checkpoint; severity HIGH; already guarded, so the control must keep holding
- Required check: Confirm that a refused operation appends its attempt to the ledger before returning an error.
- Required evidence: A ledger record with result PRECONDITION_REJECTED, a result code and a failure reason.
- Derived requirement: `LESSON-REQ-0003`

### LSN-0004 — A checkpoint may never claim readiness while it also claims to be blocked

- Reason: applies to every Gate; category checkpoint; severity CRITICAL; already guarded, so the control must keep holding
- Required check: Verify that the checkpoint carries no blocker while it claims to be ready for review.
- Required evidence: A passing validation with blockedBy empty at a readiness status.
- Derived requirement: `LESSON-REQ-0004`

### LSN-0005 — A PASS requires evidence that can be executed or resolved, not a statement

- Reason: applies to every Gate; category quality; severity CRITICAL; already guarded, so the control must keep holding
- Required check: Attach a resolvable evidence reference to every PASS recorded by this Gate.
- Required evidence: A validation run confirming that every PASS reference resolves.
- Derived requirement: `LESSON-REQ-0005`

### LSN-0006 — The repository must be self-contained; a specification may not live outside it

- Reason: applies to every Gate; category documentation; severity MEDIUM; already guarded, so the control must keep holding
- Required check: Confirm that every specification this Gate depends on is committed to the repository.
- Required evidence: A passing documentation link and checklist test.
- Derived requirement: `LESSON-REQ-0006`

### LSN-0007 — Independent validation cannot be declared by the run that did the work

- Reason: applies to every Gate; category process; severity CRITICAL; already guarded, so the control must keep holding
- Required check: Close the implementing run at an internal status and leave the independent verdict pending.
- Required evidence: A checkpoint whose independentReview and redTeam are PENDING at handoff.
- Derived requirement: `LESSON-REQ-0007`

### LSN-0008 — Requirement completeness must be total and evidence-backed before handoff

- Reason: applies to every Gate; category process; severity CRITICAL; already guarded, so the control must keep holding
- Required check: Extract every requirement before implementing and audit completeness before handoff.
- Required evidence: A completeness report with total coverage and total evidence coverage.
- Derived requirement: `LESSON-REQ-0008`

### LSN-0009 — A red gate requires rework, never a waiver, and never a weakened check

- Reason: applies to every Gate; category testing; severity CRITICAL; already guarded, so the control must keep holding
- Required check: Run the Green Keeper until every mandatory gate is green, repairing causes rather than checks.
- Required evidence: A rework log whose last cycle is GREEN with zero remaining failures.
- Derived requirement: `LESSON-REQ-0009`

### LSN-0010 — A recorded command must carry runtime, working directory, commit and purpose to be replayable

- Reason: applies to every Gate; category tooling; severity HIGH; already guarded, so the control must keep holding
- Required check: Record commands with the tooling so each one is executable from its declared working directory.
- Required evidence: A validation run over a ledger whose commands all resolve.
- Derived requirement: `LESSON-REQ-0010`

### LSN-0011 — A control over a checkpoint's own evidence must be scoped to the moment it matters

- Reason: applies to every Gate; category tooling; severity MEDIUM; already guarded, so the control must keep holding
- Required check: Check whether any new control would be invalidated by the evidence its own run produces.
- Required evidence: A passing validation executed by the gate harness itself.
- Derived requirement: `LESSON-REQ-0011`

### LSN-0012 — Sealed checkpoints and their tags are immutable, and tooling must keep validating them

- Reason: applies to every Gate; category git; severity CRITICAL; already guarded, so the control must keep holding
- Required check: Confirm that every sealed checkpoint still validates under the tooling this Gate changes.
- Required evidence: A passing historical compatibility run over every sealed tag.
- Derived requirement: `LESSON-REQ-0012`

### LSN-0013 — An installed capability must be detected by resolved path, not by a bare command lookup

- Reason: applies to every Gate; category environment; severity MEDIUM; status CONFIRMED, so it is not yet prevented automatically
- Required check: When this Gate records a capability, resolve the executable path before concluding anything about availability.
- Required evidence: A capability record naming the resolved path, or a justification that this Gate detects no capability.
- Derived requirement: `LESSON-REQ-0013`

### LSN-0014 — Evidence must be recorded as it happens, not reconstructed at the end of a run

- Reason: applies to every Gate; category process; severity MEDIUM; already guarded, so the control must keep holding
- Required check: Record each command through the tooling while the work happens.
- Required evidence: A ledger whose records were produced by the recording tooling during the run.
- Derived requirement: `LESSON-REQ-0014`

### LSN-0015 — Every positive terminal status needs one shared promotion invariant

- Reason: applies to every Gate; category quality; severity CRITICAL; already guarded, so the control must keep holding
- Required check: Confirm that every positive terminal status this Gate can produce is covered by the shared promotion invariant, not only the status this delivery ends at.
- Required evidence: A table-driven validation run that exercises every positive status against every mandatory red dimension.
- Derived requirement: `LESSON-REQ-0015`

### LSN-0016 — A mandatory set must be closed by policy, never chosen by the caller

- Reason: applies to every Gate; category testing; severity CRITICAL; already guarded, so the control must keep holding
- Required check: Confirm that every control whose scope could be narrowed by an argument derives that scope from policy instead.
- Required evidence: A recorded gate run whose requiredGates equal the canonical mandatory set, with a successful command for each one.
- Derived requirement: `LESSON-REQ-0016`

### LSN-0017 — A completeness denominator must come from a source the delivery does not own

- Reason: applies to every Gate; category process; severity CRITICAL; already guarded, so the control must keep holding
- Required check: Confirm that the expected requirement set is derived independently and compared as a set, not only as a count.
- Required evidence: A completeness report whose expected and declared identifier sets are equal.
- Derived requirement: `LESSON-REQ-0017`

### LSN-0018 — A structured reference must be resolved, not merely well typed

- Reason: applies to every Gate; category tooling; severity CRITICAL; already guarded, so the control must keep holding
- Required check: Confirm that every reference this Gate records is resolved by a tool, not accepted as a string.
- Required evidence: A validation run that rejects a nonexistent control, a nonexistent evidence path and a nested secret.
- Derived requirement: `LESSON-REQ-0018`

### LSN-0019 — A derived artifact must carry a fingerprint of the inputs that produced it

- Reason: applies to every Gate; category tooling; severity HIGH; already guarded, so the control must keep holding
- Required check: Confirm that every derived artifact this Gate stores can be recomputed and is recomputed during validation.
- Required evidence: A validation run that rejects a preflight whose inputs have changed.
- Derived requirement: `LESSON-REQ-0019`

### LSN-0020 — Evidence produced from a dirty tree needs immutable input identity

- Reason: applies to every Gate; category tooling; severity HIGH; already guarded, so the control must keep holding
- Required check: Confirm that every recorded command binds its inputs by content and that no timestamp in the ledger is later than the recorded end of the run.
- Required evidence: A validation run over a ledger whose records all carry an input digest, with a post-commit validation record at the sealed commit.
- Derived requirement: `LESSON-REQ-0020`

### LSN-0021 — Sealed history needs an anchor outside the content it describes

- Reason: applies to every Gate; category git; severity CRITICAL; already guarded, so the control must keep holding
- Required check: Confirm that the integrity chain still resolves for every sealed checkpoint and that this Gate anchors every sealed predecessor.
- Required evidence: A verification run over the anchor chain returning no divergence.
- Derived requirement: `LESSON-REQ-0021`

### LSN-0022 — An authoritative count must be derived once, never maintained by hand twice

- Reason: applies to every Gate; category documentation; severity CRITICAL; already guarded, so the control must keep holding
- Required check: Confirm that every count used as evidence in this Gate is derived from one source and verified where it is quoted.
- Required evidence: A validation run that rejects a report whose stated count contradicts the derived one.
- Derived requirement: `LESSON-REQ-0022`

### LSN-0023 — A lesson must cite a source that actually records the finding it claims

- Reason: applies to every Gate; category documentation; severity MEDIUM; already guarded, so the control must keep holding
- Required check: Confirm that every lesson this Gate writes or updates cites a checkpoint that records the finding identifier it names.
- Required evidence: A memory validation run that resolves every lesson source locator.
- Derived requirement: `LESSON-REQ-0023`

### LSN-0024 — A control is finished only when its positive path has been executed, not only its refusals

- Reason: applies to every Gate; category quality; severity CRITICAL; already guarded, so the control must keep holding
- Required check: For every control this Gate adds or changes that gates a status, execute the path that reaches the status, not only the paths that are refused.
- Required evidence: An executed positive-path test or simulation artifact for each such control.
- Derived requirement: `LESSON-REQ-0024`

### LSN-0025 — A generic guardrail derives repository state instead of naming today's checkpoint

- Reason: applies to every Gate; category testing; severity CRITICAL; already guarded, so the control must keep holding
- Required check: Confirm that no generic guard, test or policy in this Gate names a historical checkpoint to decide behaviour, and that any such rule is derived from repository state.
- Required evidence: A derived exclusion with a test proving it moves, or a documented fixture that names a concrete checkpoint on purpose.
- Derived requirement: `LESSON-REQ-0025`

### LSN-0026 — An adversarial battery without a null-mutation control proves nothing

- Reason: applies to every Gate; category testing; severity HIGH; already guarded, so the control must keep holding
- Required check: Run every adversarial battery of this Gate with an unmutated control through the same path, and record its result with the battery.
- Required evidence: A Red Team report whose baselineControl is VALID.
- Derived requirement: `LESSON-REQ-0026`

### LSN-0027 — A lesson's prose may record a residual limit but may never contradict its status

- Reason: applies to every Gate; category documentation; severity MEDIUM; already guarded, so the control must keep holding
- Required check: Confirm that every lesson this Gate writes or updates describes limits rather than restating its own status.
- Required evidence: A memory validation run with no status contradiction reported.
- Derived requirement: `LESSON-REQ-0027`

### LSN-0028 — A configuration key that no code reads is a defect, not documentation

- Reason: applies to every Gate; category tooling; severity HIGH; already guarded, so the control must keep holding
- Required check: Confirm that every configuration key this Gate declares is read by the implementation, or remove it and document the fixed behaviour.
- Required evidence: A validated policy document whose every key has a consumer.
- Derived requirement: `LESSON-REQ-0028`

### LSN-0029 — A required protocol transition must never turn a mandatory gate red

- Reason: applies to every Gate; category process; severity CRITICAL; already guarded, so the control must keep holding
- Required check: Before handoff, execute the protocol transitions this Gate's successor will perform and confirm the mandatory gates stay green.
- Required evidence: A successor durability artifact whose every state is green.
- Derived requirement: `LESSON-REQ-0029`

### LSN-0031 — An empty applicable set is not a missing required set, and a control must tell them apart

- Reason: applies to every Gate; category quality; severity CRITICAL; already guarded, so the control must keep holding
- Required check: For every quality or audit control this Gate adds or changes that operates on a derived set, confirm that an empty applicable set is reported as NOT_APPLICABLE with a justification and that a missing required set is reported as a failure.
- Required evidence: An executed artifact showing both outcomes: a passing run whose empty dimensions are justified, and a failing run whose named items are unsatisfied.
- Derived requirement: `LESSON-REQ-0030`

### LSN-0032 — A control written while one Gate was the only Gate stops being a control when the next one starts

- Reason: applies to every Gate; category quality; severity HIGH; already guarded, so the control must keep holding
- Required check: For every control this Gate adds or changes, confirm that what it judges is derived from a canonical source rather than written into the control, and that it would still be correct for the Gate after this one.
- Required evidence: An executed transition into the next Gate, and a test that the control's subject comes from a registry rather than a literal.
- Derived requirement: `LESSON-REQ-0031`

### LSN-0033 — A value bound in middleware is absent in the handlers that run outside it

- Reason: applies to every Gate; category implementation; severity MEDIUM; already guarded, so the control must keep holding
- Required check: For every cross-cutting value this Gate binds in middleware, confirm it is present in the responses produced above that middleware, including error responses.
- Required evidence: A test that triggers a failure handled outside the middleware chain and asserts the value is still carried.
- Derived requirement: `LESSON-REQ-0032`

### LSN-0034 — Re-deriving what the framework already computed diverges from the framework

- Reason: applies to every Gate; category implementation; severity MEDIUM; already guarded, so the control must keep holding
- Required check: Where this Gate derives a value the framework already computes, confirm it reads the framework's result rather than recomputing it, and that a test asserts the value rather than only its presence.
- Required evidence: A test asserting the specific derived value, not merely that the endpoint answers.
- Derived requirement: `LESSON-REQ-0033`

### LSN-0035 — Captured subprocess output decoded or re-emitted with the platform codepage crashes the tool, not the work

- Reason: applies to every Gate; category tooling; severity HIGH; already guarded, so the control must keep holding
- Required check: Confirm every subprocess capture this Gate adds states its decoder explicitly, that every entry point re-emitting captured output configures its own stream, and that the repository-wide control still passes.
- Required evidence: The control-plane test that parses the tree, green, with the rule exercised against a rejecting case.
- Derived requirement: `LESSON-REQ-0034`

### LSN-0036 — A gate that runs inside an image measures the image, not the source

- Reason: applies to every Gate; category tooling; severity HIGH; already guarded, so the control must keep holding
- Required check: For every mandatory gate this Gate adds or changes, confirm that a gate executing inside a built artefact rebuilds that artefact before measuring, and that the repository-wide control still passes.
- Required evidence: The control-plane test that parses every gate module, green, with the rule exercised against a rejecting case.
- Derived requirement: `LESSON-REQ-0035`

### LSN-0037 — A shared control that names an identifier the repository derives stops being a control when that identifier moves

- Reason: applies to every Gate; category tooling; severity MEDIUM; already guarded, so the control must keep holding
- Required check: Confirm that every control this Gate adds which reasons about an identifier the repository derives -- the current Gate, the newest checkpoint, the head migration -- derives it rather than naming it, and that the repository-wide control still passes.
- Required evidence: The control-plane test that parses every caller, green, with a rejecting case.
- Derived requirement: `LESSON-REQ-0036`

### LSN-0038 — Two representations of one concept in one module disagree, and the safer one loses

- Reason: applies to every Gate; category implementation; severity MEDIUM; already guarded, so the control must keep holding
- Required check: Where this Gate defines a classification twice — once anchored and once embedded — confirm one definition is authoritative and the other derives from it or is removed.
- Required evidence: A test asserting both paths classify the same corpus identically.
- Derived requirement: `LESSON-REQ-0037`

### LSN-0039 — A test that writes to the operational database leaves production data behind

- Reason: applies to every Gate; category testing; severity HIGH; already guarded, so the control must keep holding
- Required check: For every test this Gate adds that writes to a shared service rather than to a disposable one, confirm it removes what it created and that an invariant detects residue.
- Required evidence: The suite run followed by a query of the shared service showing no fixture rows.
- Derived requirement: `LESSON-REQ-0038`

### LSN-0040 — A control that judges sealed history only runs once a successor anchors it

- Reason: applies to every Gate; category checkpoint; severity CRITICAL; already guarded, so the control must keep holding
- Required check: Confirm that every sealed predecessor this Gate anchors validates from a detached checkout of its own tag in a published clone (Git's transport, never a copy of the local object store), that every commit sealed evidence names is reachable from a published reference, and that no command this Gate records declares an input the repository does not carry.
- Required evidence: A validation run against each anchored checkpoint from its tag in a published clone, green, and a clone of the remote that validates every sealed checkpoint of the milestone.
- Derived requirement: `LESSON-REQ-0039`

### LSN-0041 — An editing path that consumes a backslash escape leaves a control character, and the control it belonged to silently matches nothing

- Reason: applies to every Gate; category testing; severity HIGH; already guarded, so the control must keep holding
- Required check: Confirm that every scan this Gate adds asserts it found something before judging it, and that no source file carries a stray control character.
- Required evidence: A green run of the repository-wide control-character scan and of each scan's own non-empty-corpus assertion.
- Derived requirement: `LESSON-REQ-0040`

### LSN-0042 — A naming convention rewrites a CHECK constraint's name and leaves a UNIQUE constraint's alone

- Reason: applies to every Gate; category implementation; severity HIGH; already guarded, so the control must keep holding
- Required check: For every migration this Gate adds, confirm it is applied and reversed against a disposable database, and that autogenerate finds nothing left to do afterwards.
- Required evidence: A green reversibility run and a green autogenerate check against a database migrated from zero.
- Derived requirement: `LESSON-REQ-0041`

### LSN-0043 — A log line is not evidence that another process is ready

- Reason: applies to every Gate; category testing; severity MEDIUM; already guarded, so the control must keep holding
- Required check: For every wait this Gate adds on another process, confirm it asks that process or its server for the state rather than reading a log line.
- Required evidence: The readiness path asserted against the server's own answer, with the log-line path refused by a test.
- Derived requirement: `LESSON-REQ-0042`

### LSN-0044 — A boundary scan must read the code rather than the prose, and must be shown to fire on a mutated module

- Reason: applies to every Gate; category quality; severity HIGH; already guarded, so the control must keep holding
- Required check: For every boundary scan this Gate adds, confirm it reads the syntax tree rather than the text, and that it carries a control which runs the identical scan over a module that violates the rule.
- Required evidence: Each scan's null control executed and green, alongside the scan itself.
- Derived requirement: `LESSON-REQ-0043`

### LSN-0045 — A counted test suite must declare its cases statically, because the denominator is read from the source

- Reason: applies to every Gate; category testing; severity MEDIUM; already guarded, so the control must keep holding
- Required check: Confirm that every case this Gate adds to a counted suite is declared statically, with table-driven inputs written as a loop rather than as a parametrisation.
- Required evidence: A green run of the counted-suite scan alongside the suite itself.
- Derived requirement: `LESSON-REQ-0044`

### LSN-0046 — A timeout that cancels the task it runs in leaves nothing able to record what happened

- Reason: applies to every Gate; category implementation; severity CRITICAL; already guarded, so the control must keep holding
- Required check: For every limit this Gate enforces, confirm that the enforcement path is still able to write when it fires, and that a real run is observed reaching the terminal state with the reason recorded.
- Required evidence: A recorded scenario run in which the limit fires and the store shows the terminal state, the error type and the event.
- Derived requirement: `LESSON-REQ-0045`

### LSN-0047 — A refusal that misnames the defect spends the only repair on the wrong correction

- Reason: applies to every Gate; category implementation; severity HIGH; already guarded, so the control must keep holding
- Required check: For every validator whose refusal is sent back as the instruction to correct - to a model through a repair, or to a user - confirm that each distinct defect (absent, wrong type, wrong value) has its own reason, and that a wrong-typed value is never reported as missing.
- Required evidence: A test per defect class asserting the reason code and that the sentence names the defect it found.
- Derived requirement: `LESSON-REQ-0046`

### LSN-0048 — A state and the event that explains it, written in two commits, are written event first

- Reason: applies to every Gate; category implementation; severity HIGH; already guarded, so the control must keep holding
- Required check: Wherever a state and the record that explains it are written in separate commits, confirm which one a reader between the two can see alone, and that it is the one a reader may act on - the record before the state it explains.
- Required evidence: A test that observes what the log held at the moment each terminal state was written.
- Derived requirement: `LESSON-REQ-0047`

### LSN-0049 — A metric read the instant after the call that moved it is read before the scrape that carries it

- Reason: applies to every Gate; category testing; severity MEDIUM; already guarded, so the control must keep holding
- Required check: For every check that reads what another process observes on its own cycle - a scrape, a poll, a flush - confirm that the check waits for at least one full cycle, with a bound, and never repeats the action it is observing to make the observation appear.
- Required evidence: A test in which the observation arrives only after a delay, and the check still passes within its bound.
- Derived requirement: `LESSON-REQ-0048`

### LSN-0050 — A checkpoint sealed without naming its own tag cannot be validated from that tag

- Reason: applies to every Gate; category checkpoint; severity HIGH; already guarded, so the control must keep holding
- Required check: Before sealing a checkpoint at any status, confirm that STATE.json currentCommit names the checkpoint's own canonical tag, and that the sealed content validates from that tag with a detached HEAD.
- Required evidence: The post-seal validation from the checkpoint's own tag, and the seal tool's refusal of a state that does not name it.
- Derived requirement: `LESSON-REQ-0049`

### LSN-0051 — A payload one service bounds for another must be bounded as the receiver measures it

- Reason: applies to every Gate; category implementation; severity HIGH; already guarded, so the control must keep holding
- Required check: For every payload one service bounds and another service accepts or refuses by size, confirm both measure it the same way and that the receiver's bound is not smaller than what the sender may hand over.
- Required evidence: A test that reads both bounds from their sources and compares them, and a test that the sender's bound holds for the worst-case rendering.
- Derived requirement: `LESSON-REQ-0050`

### LSN-0052 — Two processes that meet on a queue must name what crosses it once, and a real run must exercise both

- Reason: applies to every Gate; category architecture; severity HIGH; already guarded, so the control must keep holding
- Required check: For every payload this Gate sends between two processes, confirm its names are defined once in a shared contract, used by both sides, and exercised once by a run in which neither side is a double.
- Required evidence: The shared definition, a scan of both sides for a literal spelling, and a recorded run through the real producer and consumer.
- Derived requirement: `LESSON-REQ-0051`

### LSN-0053 — A process sweep that reads what a forking process holds waits on the processes it has to kill

- Reason: applies to every Gate; category security; severity HIGH; already guarded, so the control must keep holding
- Required check: For every control that must end processes it did not start, confirm it freezes before it kills, reads nothing a forking process holds, and is attacked on the real engine by a process that detaches and forks.
- Required evidence: An engine test in which a detached fork bomb is swept and the next command still runs.
- Derived requirement: `LESSON-REQ-0052`

### LSN-0054 — A pre-push check narrower than the change's reach lets a red gate reach the public remote

- Reason: applies to every Gate; category git; severity MEDIUM; status CONFIRMED, so it is not yet prevented automatically
- Required check: Before each push, run the lint gate and the repository-wide scans as well as the suites of the change, because a change reaches every control that scans the tree.
- Required evidence: Recorded lint and targeted runs between each push and the one before it.
- Derived requirement: `LESSON-REQ-0053`

### LSN-0055 — A contract a model must follow has to reach the model, rendered from the definition the parser enforces

- Reason: applies to every Gate; category model-behavior; severity MEDIUM; already guarded, so the control must keep holding
- Required check: For every structured answer a model must produce, confirm that the exact shape is in the text every model receives — rendered from the definition the parser enforces, not written beside it — and that a live run of the configured model produces it.
- Required evidence: A test that the instructions contain the rendered shape and follow a change of the schema, and a live run of the configured model that produces the shape.
- Derived requirement: `LESSON-REQ-0054`

### LSN-0056 — A result is accepted only from the executor that owns the request, decided when the request is created

- Reason: applies to every Gate; category security; severity MEDIUM; already guarded, so the control must keep holding
- Required check: For every result, verdict or callback that more than one producer could deliver, confirm that the owner is recorded when the work is created, that the origin of a delivery comes from the code path and never from the delivery, and that a delivery from any other origin is refused before it is stored.
- Required evidence: A test that a delivery from the wrong origin is refused before and after the owner's, with a null control through the same path, and a run on the real stack.
- Derived requirement: `LESSON-REQ-0055`

### LSN-0057 — A pinned lock can become unsafe without changing, so advisory state is live evidence

- Reason: applies to every Gate; category security; severity CRITICAL; already guarded, so the control must keep holding
- Required check: For every pinned dependency graph delivered by a Gate, run the current advisory scan against every required source and refuse Critical or High findings without suppressing advisories or narrowing the denominator.
- Required evidence: A report from every required advisory source showing zero relevant Critical or High findings, plus a test that proves those severities remain blocking.
- Derived requirement: `LESSON-REQ-0056`

### LSN-0058 — Container health does not prove Docker Desktop host-port forwarding

- Reason: applies to every Gate; category environment; severity MEDIUM; already guarded, so the control must keep holding
- Required check: Exercise every required host-published service through its actual loopback port; do not substitute container health for host reachability.
- Required evidence: A live host-facing infrastructure suite after stack health, with the original failure retained if a non-destructive restart is required for recovery.
- Derived requirement: `LESSON-REQ-0057`

### LSN-0059 — A lesson exclusion must declare the scope it excludes

- Reason: applies to every Gate; category process; severity MEDIUM; already guarded, so the control must keep holding
- Required check: Confirm every active lesson excluded from a preflight declares a non-empty scope selector, and that incidental metadata does not narrow applicability.
- Required evidence: A passing repository-preflight coverage test over the complete active lesson set.
- Derived requirement: `LESSON-REQ-0058`

### LSN-0060 — Parent and child facts without an ORM relationship require an explicit flush boundary

- Reason: applies to every Gate; category implementation; severity MEDIUM; already guarded, so the control must keep holding
- Required check: Whenever one transaction inserts parent and child ORM facts using raw foreign-key identifiers without a relationship edge, confirm the parent is flushed before the child is added.
- Required evidence: A real-database integration test that creates the parent and child together and observes both after commit.
- Derived requirement: `LESSON-REQ-0059`

### LSN-0061 — Cancellation completion must not bypass cleanup acknowledgement

- Reason: applies to every Gate; category testing; severity MEDIUM; already guarded, so the control must keep holding
- Required check: For every running task that can be cancelled, prove the lifecycle records cancellation requested before it records cancellation completed.
- Required evidence: A lifecycle test that enters the intermediate cancelling state, acknowledges cleanup, reaches cancelled, and rejects late delivery.
- Derived requirement: `LESSON-REQ-0060`

### LSN-0062 — Provenance digests are a set even when their sources are distinct

- Reason: applies to every Gate; category implementation; severity MEDIUM; already guarded, so the control must keep holding
- Required check: Whenever provenance is represented by content digests, normalize it as a unique ordered set rather than assuming each semantic source has different bytes.
- Required evidence: A test in which distinct provenance roles share one digest and the stored provenance contains it once.
- Derived requirement: `LESSON-REQ-0061`

### LSN-0063 — An identity shared across services must satisfy the strictest persistence type and remain stable

- Reason: applies to every Gate; category architecture; severity HIGH; already guarded, so the control must keep holding
- Required check: For every identity crossing a service boundary, verify it satisfies the strictest persisted representation and is stable across delivery retries.
- Required evidence: A contract or unit test proving syntactic validity, deterministic replay identity and separation between distinct work items.
- Derived requirement: `LESSON-REQ-0062`

### LSN-0064 — A shared execution resource needs an explicit exclusive owner for every owning domain

- Reason: applies to every Gate; category architecture; severity HIGH; already guarded, so the control must keep holding
- Required check: When another durable domain reuses an owned resource, model its real ownership explicitly, require exactly one owner, and preserve every per-owner exclusivity invariant.
- Required evidence: A structural test of the ownership and uniqueness constraints plus a real-database lifecycle test for the new owner.
- Derived requirement: `LESSON-REQ-0063`

### LSN-0065 — A shared execution identifier must not be written into a foreign key owned by another domain

- Reason: applies to every Gate; category implementation; severity HIGH; already guarded, so the control must keep holding
- Required check: For a shared execution contract, prove each durable foreign key is populated only for the domain that owns the referenced row, using trusted ownership context rather than identifier shape.
- Required evidence: A test with both owner domains showing that only the owning domain binds the foreign key.
- Derived requirement: `LESSON-REQ-0064`

### LSN-0066 — Immutable content identity excludes observation time and the first observer

- Reason: applies to every Gate; category architecture; severity HIGH; already guarded, so the control must keep holding
- Required check: For every content-addressed or reusable immutable record, define material identity separately from creation metadata and ownership provenance.
- Required evidence: A replay test where material inputs are equal but time and first observer differ, proving reuse without rewriting the original record.
- Derived requirement: `LESSON-REQ-0065`

### LSN-0067 — Cancellation semantics must survive orchestration-library exception wrapping

- Reason: applies to every Gate; category implementation; severity HIGH; already guarded, so the control must keep holding
- Required check: For cancellation across an orchestration boundary, test the exception shape the real library delivers and derive outcome from the durable request plus executor acknowledgement rather than the wrapper class alone.
- Required evidence: A workflow test for the wrapped cancellation and a live running-cancellation scenario proving cleanup, terminal cancellation and idempotent repeat.
- Derived requirement: `LESSON-REQ-0066`

### LSN-0068 — A bounded parser must apply each content limit only to content it interprets

- Reason: applies to every Gate; category implementation; severity HIGH; already guarded, so the control must keep holding
- Required check: For every parser-specific content limit applied to a broader inventory, prove unrelated content bypasses that limit while every interpreted candidate remains bounded.
- Required evidence: A paired test with an oversized unrelated file accepted and an oversized interpreted file refused, plus a successful real repository evaluation.
- Derived requirement: `LESSON-REQ-0067`

### LSN-0069 — A polyglot plan binds each check to both its project root and its toolchain

- Reason: applies to every Gate; category architecture; severity HIGH; already guarded, so the control must keep holding
- Required check: For every polyglot or multi-root project plan, prove each check is expanded at the roots that declared its stack and selects execution policy from the frozen runner rather than one run-wide guessed toolchain.
- Required evidence: A deterministic planning test over multiple roots and stacks, an execution-boundary test for per-runner images, and a successful real polyglot repository evaluation.
- Derived requirement: `LESSON-REQ-0068`

### LSN-0070 — Project discovery must separate deployable roots, nested fixtures and check applicability

- Reason: applies to every Gate; category architecture; severity HIGH; already guarded, so the control must keep holding
- Required check: For project discovery over a monorepo, prove nested fixture manifests do not become execution roots and every non-applicable unit check is derived from the frozen source inventory rather than from a failed command.
- Required evidence: Paired planner tests proving no-test roots are explicitly non-applicable, test-bearing roots remain mandatory, fixture manifests are excluded, and a real repository evaluation succeeds.
- Derived requirement: `LESSON-REQ-0069`

### LSN-0071 — Every quality image must provision snapshots on its oldest runtime and prepare each isolated check

- Reason: applies to every Gate; category implementation; severity HIGH; already guarded, so the control must keep holding
- Required check: For every shared helper and isolated quality runner, test the oldest pinned runtime actually used by an image and prove each check prepares all dependencies it needs without relying on a previous sandbox session.
- Required evidence: A real snapshot-provisioning test across every quality image, closed-runner assertions for self-contained preparation, and a successful real polyglot repository evaluation.
- Derived requirement: `LESSON-REQ-0070`

### LSN-0072 — Secret findings and reviewed false positives must share one policy-owned taxonomy

- Reason: applies to every Gate; category security; severity HIGH; already guarded, so the control must keep holding
- Required check: Whenever more than one gate scans secrets, prove all scanners share the policy-owned finding taxonomy and digest-bound allowance source, and that an unallowlisted match remains blocking.
- Required evidence: Content-addressing tests for scanner and policy inputs, a real negative scan in every execution image, and consistent PASS over the same reviewed repository snapshot.
- Derived requirement: `LESSON-REQ-0071`

### LSN-0073 — The canonical lint denominator must cover every detected project root

- Reason: applies to every Gate; category quality; severity HIGH; already guarded, so the control must keep holding
- Required check: For every manually scoped repository-wide quality command, derive or test its denominator against the current project inventory so a newly detected root cannot remain outside a green gate.
- Required evidence: A denominator test over all non-fixture manifests plus a successful canonical lint execution and matching real repository Quality Engine verdict.
- Derived requirement: `LESSON-REQ-0072`

### LSN-0074 — An importable source tree is not an installed or repository-configured test environment

- Reason: applies to every Gate; category implementation; severity HIGH; already guarded, so the control must keep holding
- Required check: For Python tests executed from a nested project root, prove the sandbox provides installed distribution metadata and repository-root policy/configuration without reading or writing the host.
- Required evidence: A real snapshot test for metadata and monorepo configuration plus a successful evaluation of a committed multi-package repository.
- Derived requirement: `LESSON-REQ-0073`

### LSN-0075 — Offline package installation requires its build backend inside the quality image

- Reason: applies to every Gate; category implementation; severity HIGH; already guarded, so the control must keep holding
- Required check: Whenever a sandbox performs an offline package installation, prove every declared build backend is pinned in the content-addressed execution image and usable by the non-root runtime.
- Required evidence: A real no-network package-installation test through the canonical image-rebuilding sandbox gate.
- Derived requirement: `LESSON-REQ-0074`

### LSN-0076 — Projected nested configuration requires an explicit monorepo root

- Reason: applies to every Gate; category architecture; severity HIGH; already guarded, so the control must keep holding
- Required check: When repository configuration is projected into a nested project, provide an explicit trusted repository root and prove source-boundary scans do not reinterpret the projection as ownership.
- Required evidence: A real nested sandbox test that observes the explicit root plus the complete source-boundary scan from that environment.
- Derived requirement: `LESSON-REQ-0075`

### LSN-0077 — Harness wait bounds must reflect workload size without changing product deadlines

- Reason: applies to every Gate; category quality; severity HIGH; already guarded, so the control must keep holding
- Required check: For a functional harness whose workload cardinality differs materially by scenario, prove its bounded wait covers the largest legitimate execution without weakening the product's own timeout or deadline.
- Required evidence: A control that binds every large-workload terminal wait to a distinct finite bound plus successful real executions within that bound.
- Derived requirement: `LESSON-REQ-0076`

### LSN-0078 — Evidence recorders must resolve caller-supplied commit references before execution

- Reason: applies to every Gate; category quality; severity HIGH; already guarded, so the control must keep holding
- Required check: Before an evidence recorder executes a command, resolve every caller-supplied commit reference to a real canonical commit and normalize repeated provenance inputs.
- Required evidence: A positive canonicalization test and a negative unresolved-commit test proving the command was not executed and the refusal was appended.
- Derived requirement: `LESSON-REQ-0077`

### LSN-0079 — Test discovery and the unit runner must cover the same project scope

- Reason: applies to every Gate; category testing; severity HIGH; already guarded, so the control must keep holding
- Required check: For every test applicability rule, prove the corresponding closed runner collects the same project scope and that a failing source at each recognized location is observed.
- Required evidence: A runner-registry assertion plus a real failing fixture whose root-level test produces FAIL with preserved finding and evidence.
- Derived requirement: `LESSON-REQ-0078`

### LSN-0080 — A failed verification stage must not leave an older PASS report addressable

- Reason: applies to every Gate; category quality; severity HIGH; already guarded, so the control must keep holding
- Required check: Whenever a verification stage writes to a reusable report path, prove the old artifact is removed before execution and cannot survive a failed rerun as current evidence.
- Required evidence: A control that starts with a stale PASS file and observes it absent before the stage command is launched.
- Derived requirement: `LESSON-REQ-0079`

### LSN-0081 — Canonical requirement evidence must name a test the repository actually discovers

- Reason: applies to every Gate; category testing; severity HIGH; already guarded, so the control must keep holding
- Required check: Before a canonical checklist is accepted, resolve every named test identity against the suite registry rather than treating prose-like test labels as evidence.
- Required evidence: A repository-wide specification-evidence test that rejects an unknown identity and passes every canonical row.
- Derived requirement: `LESSON-REQ-0080`

### LSN-0082 — Engineering memory cannot depend on an ephemeral generated report

- Reason: applies to every Gate; category quality; severity HIGH; already guarded, so the control must keep holding
- Required check: Keep organizational memory evidence in committed source or checkpoint-owned artifacts; reject references to regenerable runtime output.
- Required evidence: A repository-wide control proving no lesson evidence path begins with file:var/.
- Derived requirement: `LESSON-REQ-0081`

### LSN-0083 — A command that decodes captured UTF-8 must also configure the stream that re-emits it

- Reason: applies to every Gate; category tooling; severity MEDIUM; already guarded, so the control must keep holding
- Required check: For every executable command that captures text from a child process and prints it, configure both the child decoder and the parent output stream explicitly.
- Required evidence: A repository-wide entry-point scan plus a rejecting fixture for an unconfigured captured-output command.
- Derived requirement: `LESSON-REQ-0082`

### LSN-0084 — A historical Gate documentation test must derive the current entry-point state

- Reason: applies to every Gate; category testing; severity MEDIUM; already guarded, so the control must keep holding
- Required check: When a predecessor regression test inspects a current entry point, derive current lifecycle identifiers and keep only genuinely historical references fixed.
- Required evidence: A documentation test that resolves the current Gate from repository state while retaining predecessor checklist and runbook links.
- Derived requirement: `LESSON-REQ-0083`

### LSN-0085 — A source-based control must assert syntax semantics rather than formatter layout

- Reason: applies to every Gate; category testing; severity MEDIUM; already guarded, so the control must keep holding
- Required check: When a control judges source structure, parse the language representation and compare semantic nodes instead of binding the rule to formatter whitespace or quote style.
- Required evidence: A source-control test that resolves the relevant syntax nodes and their values without substring adjacency assumptions.
- Derived requirement: `LESSON-REQ-0084`

### LSN-0086 — A subprocess assertion must preserve the exit code when both streams are empty

- Reason: applies to every Gate; category testing; severity MEDIUM; already guarded, so the control must keep holding
- Required check: For every subprocess-backed assertion, preserve return code and a non-empty diagnostic even when the child emits nothing; never add a retry that could conceal the outcome.
- Required evidence: A mutation test for nonzero return with empty stdout and stderr that observes the exact exit code.
- Derived requirement: `LESSON-REQ-0085`

### LSN-0087 — A rehearsal worker must register every workflow activity boundary

- Reason: applies to every Gate; category implementation; severity HIGH; already guarded, so the control must keep holding
- Required check: Every purpose-built worker that hosts a shared workflow must register every activity boundary that workflow can schedule, including not-applicable branches whose decision is made inside an activity.
- Required evidence: A worker-registration control plus a successful real restart rehearsal through the workflow's terminal state.
- Derived requirement: `LESSON-REQ-0086`

### LSN-0088 — A test inside a built image can consume only inputs copied into that image

- Reason: applies to every Gate; category testing; severity HIGH; already guarded, so the control must keep holding
- Required check: Whenever a test runs inside a built image and consumes repository content outside its own copied suite, prove the Dockerfile carries that input and the test resolves the same in-image destination.
- Required evidence: A source-boundary control that binds COPY source and in-image path plus a successful execution through the built image.
- Derived requirement: `LESSON-REQ-0087`
