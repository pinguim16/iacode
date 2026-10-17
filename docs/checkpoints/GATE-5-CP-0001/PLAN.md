# Gate 5 execution plan

## Full runtime v2 causal rework — frozen criteria, before corrective implementation

G5-INT-034 additionally requires one synchronous inventory-recorder/validation-recorder sequencer:
the first recorder must actually exit, any first-phase failure prevents the second command, and
other producers must already be quiescent. Existing mandatory hashes and gate sets remain intact.
The reopened LSN-0011 requires actual serial main-tree validation before its status is restored.

Cmd-0277 completes all 45 stages with 41 PASS and four FAIL; cmd-0280 preserves the exact
failed verifier and explicitly unavailable collector outputs. Cmd-0279/0281/0282 and the
digest-verified sandbox evidence cmd-0276 establish the specific causes. Cmd-0283 observes only
expected checkpoint inventory/hash drift after these new reports; Git remains main at runtime v2.

Before repair, escalate G5-INT-028/029/030/031 through the canonical recurrence transition,
confirm LSN-0134/0135, refresh lesson preflight and derive the expanded requirement set.
Correct UTF-8 consumers, decoded literal consumers, the owning-Gate scope expectation, explicit
real-registry test roots and the current producer collector. Preserve all correct assertions,
environment-independent test settings, original scanner taxonomy, historical subjects and every
mandatory stage. Add causal positive/adverse regressions including producer-capture survival after
an actual exception/cleanup. Then repeat affected whole suites, publish a new immutable v3 subject
and execute the full non-fast 45-stage cycle before any prepared acceptance or closure action.

## Additional observed transport obligation — lesson:LSN-0131

Preserve exact archived observation bytes through real Git export, not only through local copies.
Cmd-0216 reproduces CRLF-to-LF mutation; cmd-0217 passes an actual isolated Git positive/adverse/
restored control. Dedicated copied evidence paths are non-text without rewriting original reports.
Restage and compare each actual archive/index blob before publication; preserve raw recorded hashes.

Status: IN_PROGRESS. This plan follows the preflight (cmd-0003, refreshed cmd-0010), canonical
requirement derivation (cmd-0004/0011), and the executed baseline (cmd-0008). None of the planned
work is completion evidence. The initial set was 50 canonical rows plus 115 lesson requirements.
Cmd-0022 extended it to 50 plus 116 after the causal documentation lesson; cmd-0036 extends it
again to 50 plus 117 after the actual mutation-recovery failure. Cmd-0052 extends it to 50 plus
118 after the observed publication/checkpoint scan distinction. Cmd-0070 adds the native installer
lesson; cmd-0081 adds the observed cold-import lesson. At cmd-0161 the set was50 canonical rows plus
126 lesson requirements,176 total including fresh-catalog setup. Current derivation cmd-0310 is184.
Implementation cannot reduce
either set. M2 independent validation stays pending.

## G5-S00 — Entry and baseline

- Objective: validate immutable Gate 4, anchor it, derive the full Gate 5 requirement set and record
  a reproducible baseline before changing behavior.
- Probable paths: AUTHORIZATION.md, BASELINE.md, LESSON-PREFLIGHT.*, REQUIREMENTS-MATRIX.*, STEPS.json,
  the canonical checklist/registry, predecessor anchor and checkpoint inventory.
- Dependencies: owner authorization and published Gate 4 CP0010 internal closure.
- Success criteria: entry observations reconcile with Git; all requirements are initially truthful;
  baseline failures remain recorded and the reopened recurrence is not hidden.
- Tests: entry checkpoint/integrity checks, requirement derivation and current live-state CLI.
- Risks: confusing a fresh same-session check with independent approval, stale metadata, or silently
  repairing historical content.
- Stop: unexpected Git/state divergence or a missing owner authorization. No such blocker has been
  observed at entry; a red baseline is a rework obligation, not approval.

## G5-S01 — Implementation and causal rework

- Objective: first repair G5-INT-001 without weakening assertions; then deliver the complete bounded
  CLI/editor workflow over the existing runtime, sandbox and quality engine.
- Probable paths: tests/test_gate4_quality_engine.py, new Gate 5 tests, apps/cli/,
  apps/vscode-extension/, packages/contracts/, packages/common/, apps/api/, the orchestrator gateway
  adapter, Compose configuration, mandatory gate/test registries, docs/adr/ and runbooks.
- Dependencies: the complete derived requirement set, executed baseline, selected lessons and ADRs
  before structural changes. LSN-0084 remains CONFIRMED until future-Gate controls execute green.
- Design: native editor UI and one packaged dependency-free client core; a closed versioned
  request boundary; request/response authentication over explicit loopback transport; explicit
  bounded snapshot consent and canonical pre-persistence secret scanning. Hardened mode protects
  every domain route including the worker's gateway calls. Legacy development mode is explicit
  and is never accepted as an authenticated desktop connection. Detailed decisions belong to ADRs.
- Success criteria: no host tool execution, no caller verdict/result authority, no workspace-driven
  endpoint or credential, exact approved targets, truthful states and recoverable uncertain work;
  all positive and negative behaviors execute rather than existing only in source assertions.
- Tests: historical/current Gate selection including a future Gate, strict contracts and input
  limits, real HTTP authentication and replay/refusal controls, snapshot persistence and secrets,
  CLI subprocesses, native extension commands/trust/disposal, packaging and installed-host tests,
  real runtime/provider/sandbox/quality integration and running cancellation.
- Risks: local transport impersonation, replay, secret ingress, ambiguous retry, trust/approval
  races, link/path escapes, stale UI, partial install packages and future-Gate scope creep.
- Stop: a needed external capability/credential is genuinely unavailable, an unexpected divergence
  appears, or a material owner choice expands authority. Failures otherwise return to causal repair
  with preserved evidence and new/updated lesson controls.

## G5-S02 — Whole-delivery verification and internal assurance

- Objective: prove the frozen complete implementation, then execute every mandatory internal role
  in order. All inherited gates and scenarios remain in their original denominator.
- Probable paths: verification harness and reports, TESTS.json, QUALITY.json, functional acceptance,
  requirements/closure matrices, REWORK-LOG, completeness, internal Red Team and mirror artifacts.
- Dependencies: complete implementation, causal red/green tests, documentation and explicit file
  declarations. Publish only after lint, repository scans and changed suites are green. A frozen
  subject is not a canonical checkpoint seal and cannot promote later edits.
- Success criteria: full non-fast verification, all mandatory Green Keeper gates, 100% completeness,
  an internal Red Team with valid baseline and all mandatory attacks defended, then the full mirror,
  all against identical implementation fingerprints. Failures stay visible and restart the cycle.
- Tests: the complete registry-derived suite, live host-facing services, dependency advisories,
  actual isolated fresh installation/task/recovery/cancellation, canonical functional checker,
  all historical tags with current tooling and clean transported clone proof.
- Risks: stale PASS files, double-counting, self-invalidating evidence, narrow denominators, shared
  runtime residue and claims made before process termination.
- Stop: any red dimension blocks readiness; only a real external blocker yields BLOCKED.

## G5-S03 — Truthful pre-seal assembly

- Objective: assemble exact evidence, counts, provenance, risks and executable handoff. This step
  does not prospectively mark commit, seal, publication or a later Gate complete.
- Probable paths: STATE, RUN-METADATA, FILES, COUNTS, FINAL-REPORT, HANDOFF, NEXT and PROVENANCE.
- Dependencies: all G5-S02 internal controls green and fresh; no implementation changes afterwards.
- Success criteria: checkpoint validation accepts the declared real delta and exact evidence;
  INTERNAL_GATE_PASS only if all implementing obligations are complete and blockedBy is empty.
- Tests: canonical count derivation, evidence resolution, inventory binding and checkpoint validation.
- Risks: self-approved independent verdicts, stale aggregate metadata, undeclared paths and accidental
  Gate 6 work.
- Stop: any missing evidence or blocker; do not label partial implementation ready.

## Subsequent Git boundary actions

Only after actual pre-seal acceptance: canonical finalization, a Gate 5-only content commit,
seal_checkpoint.py, atomic publication, remote synchronization, detached published validation,
final reproducible archive regeneration and a freshly generated live program-state observation.
Gate 6 still requires separate explicit owner authorization. All independent M2 review and second-tool
fields remain pending; implementing-session checks never fill them as approved.

## Lesson requirement commitments

Each row below retains the preflight's exact required check and the evidence expected at closure.
The matrix keeps every identifier NOT_STARTED/PARTIAL until actual evidence is bound. Existing
controls must re-execute; an unchanged file is not a passing test. Reopened guarded failures are
escalated and repaired before the status can return to GUARDED.

### Newly derived obligations after confirmed failures

- LESSON-REQ-0116: whenever a delivered capability is added to detailed architecture, confirm that
  the live overview does not still deny it and distinguishes pending work. Evidence: the causal
  red overview control, its unchanged green execution and full current documentation validation.
- LESSON-REQ-0117: for every refusal after a remote mutation may have been accepted, including
  response authentication, envelope and semantic validation, preserve uncertainty and stable
  reconciliation identity without repeating the mutation. Evidence: real-socket clean and signed
  malformed-result controls proving one server effect, uncertain typed error, original retry
  identity and zero retries; canonical executable-guard registration and full current verification.
  Cmd-0031 is the retained red observation, cmd-0032 archives it exactly, and cmd-0033 passes the
  expanded controls. Registration, cross-client integration and final assurance are not complete.
- LESSON-REQ-0118: treat publication review and strict checkpoint detection as distinct controls;
  execute both unchanged, retain actual secret types when correcting source false positives and
  never infer checkpoint validity from a publication scan. Evidence: retained publication-clean /
  checkpoint-red observations, unchanged strict-source red/green controls, actual SecretStr and
  redaction behavior, and current whole-checkpoint validation with no widened rule or exemption.

### LESSON-REQ-0001

- Required check: Validate the checkpoint from a clean clone detached at its own tag, not only on the branch.
- Required evidence: A recorded validate_checkpoint.py run from a detached checkout returning CHECKPOINT_VALID.

### LESSON-REQ-0002

- Required check: Declare every changed path with a reason before finalizing and let the tooling bind the hashes.
- Required evidence: A FILES.json whose declared change set matches the recomputed one, proven by a passing validation.

### LESSON-REQ-0003

- Required check: Confirm that a refused operation appends its attempt to the ledger before returning an error.
- Required evidence: A ledger record with result PRECONDITION_REJECTED, a result code and a failure reason.

### LESSON-REQ-0004

- Required check: Verify that the checkpoint carries no blocker while it claims to be ready for review.
- Required evidence: A passing validation with blockedBy empty at a readiness status.

### LESSON-REQ-0005

- Required check: Attach a resolvable evidence reference to every PASS recorded by this Gate.
- Required evidence: A validation run confirming that every PASS reference resolves.

### LESSON-REQ-0006

- Required check: Confirm that every specification this Gate depends on is committed to the repository.
- Required evidence: A passing documentation link and checklist test.

### LESSON-REQ-0007

- Required check: Close the implementing run at an internal status and leave the independent verdict pending.
- Required evidence: A checkpoint whose independentReview and redTeam are PENDING at handoff.

### LESSON-REQ-0008

- Required check: Extract every requirement before implementing and audit completeness before handoff.
- Required evidence: A completeness report with total coverage and total evidence coverage.

### LESSON-REQ-0009

- Required check: Run the Green Keeper until every mandatory gate is green, repairing causes rather than checks.
- Required evidence: A rework log whose last cycle is GREEN with zero remaining failures.

### LESSON-REQ-0010

- Required check: Record commands with the tooling so each one is executable from its declared working directory.
- Required evidence: A validation run over a ledger whose commands all resolve.

### LESSON-REQ-0011

- Required check: Check whether any new control would be invalidated by the evidence its own run produces.
- Required evidence: A passing validation executed by the gate harness itself.

### LESSON-REQ-0012

- Required check: Version every changed invariant by the subject's canonical policy, retain mandatory current downgrade controls, and validate all sealed tags with current tooling without altering subjects or narrowing membership.
- Required evidence: Passing current positive/negative and legacy policy controls plus actual current-tool validation over every canonical sealed anchor.

### LESSON-REQ-0013

- Required check: When this Gate records a capability, resolve the executable path before concluding anything about availability.
- Required evidence: A capability record naming the resolved path, or a justification that this Gate detects no capability.

### LESSON-REQ-0014

- Required check: Record each command through the tooling while the work happens.
- Required evidence: A ledger whose records were produced by the recording tooling during the run.

### LESSON-REQ-0015

- Required check: Confirm that every positive terminal status this Gate can produce is covered by the shared promotion invariant, not only the status this delivery ends at.
- Required evidence: A table-driven validation run that exercises every positive status against every mandatory red dimension.

### LESSON-REQ-0016

- Required check: Confirm that every control whose scope could be narrowed by an argument derives that scope from policy instead.
- Required evidence: A recorded gate run whose requiredGates equal the canonical mandatory set, with a successful command for each one.

### LESSON-REQ-0017

- Required check: Confirm that the expected requirement set is derived independently and compared as a set, not only as a count.
- Required evidence: A completeness report whose expected and declared identifier sets are equal.

### LESSON-REQ-0018

- Required check: Confirm that every reference this Gate records is resolved by a tool, not accepted as a string.
- Required evidence: A validation run that rejects a nonexistent control, a nonexistent evidence path and a nested secret.

### LESSON-REQ-0019

- Required check: Confirm that every derived artifact this Gate stores can be recomputed and is recomputed during validation.
- Required evidence: A validation run that rejects a preflight whose inputs have changed.

### LESSON-REQ-0020

- Required check: Confirm that every recorded command binds its inputs by content and that no timestamp in the ledger is later than the recorded end of the run.
- Required evidence: A validation run over a ledger whose records all carry an input digest, with a post-commit validation record at the sealed commit.

### LESSON-REQ-0021

- Required check: Confirm that the integrity chain still resolves for every sealed checkpoint and that this Gate anchors every sealed predecessor.
- Required evidence: A verification run over the anchor chain returning no divergence.

### LESSON-REQ-0022

- Required check: Confirm that every count used as evidence in this Gate is derived from one source and verified where it is quoted.
- Required evidence: A validation run that rejects a report whose stated count contradicts the derived one.

### LESSON-REQ-0023

- Required check: Confirm that every lesson this Gate writes or updates cites a checkpoint that records the finding identifier it names.
- Required evidence: A memory validation run that resolves every lesson source locator.

### LESSON-REQ-0024

- Required check: For every control this Gate adds or changes that gates a status, execute the path that reaches the status, not only the paths that are refused.
- Required evidence: An executed positive-path test or simulation artifact for each such control.

### LESSON-REQ-0025

- Required check: Confirm that no generic guard, test or policy in this Gate names a historical checkpoint to decide behaviour, and that any such rule is derived from repository state.
- Required evidence: A derived exclusion with a test proving it moves, or a documented fixture that names a concrete checkpoint on purpose.

### LESSON-REQ-0026

- Required check: Run every adversarial battery of this Gate with an unmutated control through the same path, and record its result with the battery.
- Required evidence: A Red Team report whose baselineControl is VALID.

### LESSON-REQ-0027

- Required check: Confirm that every lesson this Gate writes or updates describes limits rather than restating its own status.
- Required evidence: A memory validation run with no status contradiction reported.

### LESSON-REQ-0028

- Required check: Confirm that every configuration key this Gate declares is read by the implementation, or remove it and document the fixed behaviour.
- Required evidence: A validated policy document whose every key has a consumer.

### LESSON-REQ-0029

- Required check: Before handoff, execute the protocol transitions this Gate's successor will perform and confirm the mandatory gates stay green.
- Required evidence: A successor durability artifact whose every state is green.

### LESSON-REQ-0030

- Required check: For every quality or audit control this Gate adds or changes that operates on a derived set, confirm that an empty applicable set is reported as NOT_APPLICABLE with a justification and that a missing required set is reported as a failure.
- Required evidence: An executed artifact showing both outcomes: a passing run whose empty dimensions are justified, and a failing run whose named items are unsatisfied.

### LESSON-REQ-0031

- Required check: For every control this Gate adds or changes, confirm that what it judges is derived from a canonical source rather than written into the control, and that it would still be correct for the Gate after this one.
- Required evidence: An executed transition into the next Gate, and a test that the control's subject comes from a registry rather than a literal.

### LESSON-REQ-0032

- Required check: For every cross-cutting value this Gate binds in middleware, confirm it is present in the responses produced above that middleware, including error responses.
- Required evidence: A test that triggers a failure handled outside the middleware chain and asserts the value is still carried.

### LESSON-REQ-0033

- Required check: Where this Gate derives a value the framework already computes, confirm it reads the framework's result rather than recomputing it, and that a test asserts the value rather than only its presence.
- Required evidence: A test asserting the specific derived value, not merely that the endpoint answers.

### LESSON-REQ-0034

- Required check: Confirm every subprocess capture this Gate adds states its decoder explicitly, that every entry point re-emitting captured output configures its own stream, and that the repository-wide control still passes.
- Required evidence: The control-plane test that parses the tree, green, with the rule exercised against a rejecting case.

### LESSON-REQ-0035

- Required check: For every mandatory gate this Gate adds or changes, confirm that a gate executing inside a built artefact rebuilds that artefact before measuring, and that the repository-wide control still passes.
- Required evidence: The control-plane test that parses every gate module, green, with the rule exercised against a rejecting case.

### LESSON-REQ-0036

- Required check: Confirm that every control this Gate adds which reasons about an identifier the repository derives -- the current Gate, the newest checkpoint, the head migration -- derives it rather than naming it, and that the repository-wide control still passes.
- Required evidence: The control-plane test that parses every caller, green, with a rejecting case.

### LESSON-REQ-0037

- Required check: Where this Gate defines a classification twice — once anchored and once embedded — confirm one definition is authoritative and the other derives from it or is removed.
- Required evidence: A test asserting both paths classify the same corpus identically.

### LESSON-REQ-0038

- Required check: For every test this Gate adds that writes to a shared service rather than to a disposable one, confirm it removes what it created and that an invariant detects residue.
- Required evidence: The suite run followed by a query of the shared service showing no fixture rows.

### LESSON-REQ-0039

- Required check: Confirm that every sealed predecessor this Gate anchors validates from a detached checkout of its own tag in a published clone (Git's transport, never a copy of the local object store), that every commit sealed evidence names is reachable from a published reference, and that no command this Gate records declares an input the repository does not carry.
- Required evidence: A validation run against each anchored checkpoint from its tag in a published clone, green, and a clone of the remote that validates every sealed checkpoint of the milestone.

### LESSON-REQ-0040

- Required check: Confirm that every scan this Gate adds asserts it found something before judging it, and that no source file carries a stray control character.
- Required evidence: A green run of the repository-wide control-character scan and of each scan's own non-empty-corpus assertion.

### LESSON-REQ-0041

- Required check: For every migration this Gate adds, confirm it is applied and reversed against a disposable database, and that autogenerate finds nothing left to do afterwards.
- Required evidence: A green reversibility run and a green autogenerate check against a database migrated from zero.

### LESSON-REQ-0042

- Required check: For every wait this Gate adds on another process, confirm it asks that process or its server for the state rather than reading a log line.
- Required evidence: The readiness path asserted against the server's own answer, with the log-line path refused by a test.

### LESSON-REQ-0043

- Required check: For every boundary scan this Gate adds, confirm it reads the syntax tree rather than the text, and that it carries a control which runs the identical scan over a module that violates the rule.
- Required evidence: Each scan's null control executed and green, alongside the scan itself.

### LESSON-REQ-0044

- Required check: Confirm that every case this Gate adds to a counted suite is declared statically, with table-driven inputs written as a loop rather than as a parametrisation.
- Required evidence: A green run of the counted-suite scan alongside the suite itself.

### LESSON-REQ-0045

- Required check: For every limit this Gate enforces, confirm that the enforcement path is still able to write when it fires, and that a real run is observed reaching the terminal state with the reason recorded.
- Required evidence: A recorded scenario run in which the limit fires and the store shows the terminal state, the error type and the event.

### LESSON-REQ-0046

- Required check: For every validator whose refusal is sent back as the instruction to correct - to a model through a repair, or to a user - confirm that each distinct defect (absent, wrong type, wrong value) has its own reason, and that a wrong-typed value is never reported as missing.
- Required evidence: A test per defect class asserting the reason code and that the sentence names the defect it found.

### LESSON-REQ-0047

- Required check: Wherever a state and the record that explains it are written in separate commits, confirm which one a reader between the two can see alone, and that it is the one a reader may act on - the record before the state it explains.
- Required evidence: A test that observes what the log held at the moment each terminal state was written.

### LESSON-REQ-0048

- Required check: For every check that reads what another process observes on its own cycle - a scrape, a poll, a flush - confirm that the check waits for at least one full cycle, with a bound, and never repeats the action it is observing to make the observation appear.
- Required evidence: A test in which the observation arrives only after a delay, and the check still passes within its bound.

### LESSON-REQ-0049

- Required check: Before sealing a checkpoint at any status, confirm that STATE.json currentCommit names the checkpoint's own canonical tag, and that the sealed content validates from that tag with a detached HEAD.
- Required evidence: The post-seal validation from the checkpoint's own tag, and the seal tool's refusal of a state that does not name it.

### LESSON-REQ-0050

- Required check: For every payload one service bounds and another service accepts or refuses by size, confirm both measure it the same way and that the receiver's bound is not smaller than what the sender may hand over.
- Required evidence: A test that reads both bounds from their sources and compares them, and a test that the sender's bound holds for the worst-case rendering.

### LESSON-REQ-0051

- Required check: For every payload this Gate sends between two processes, confirm its names are defined once in a shared contract, used by both sides, and exercised once by a run in which neither side is a double.
- Required evidence: The shared definition, a scan of both sides for a literal spelling, and a recorded run through the real producer and consumer.

### LESSON-REQ-0052

- Required check: For every control that must end processes it did not start, confirm it freezes before it kills, reads nothing a forking process holds, waits for killed processes to leave the PID table, and is attacked on the real engine by a process that detaches and forks.
- Required evidence: A deterministic zombie-reaping control plus an engine test in which a detached fork bomb is swept and the next command still runs.

### LESSON-REQ-0053

- Required check: Before each push, run the lint gate and the repository-wide scans as well as the suites of the change, because a change reaches every control that scans the tree.
- Required evidence: Recorded lint and targeted runs between each push and the one before it.

### LESSON-REQ-0054

- Required check: For every structured answer a model must produce, confirm that the exact shape is in the text every model receives — rendered from the definition the parser enforces, not written beside it — and that a live run of the configured model produces it.
- Required evidence: A test that the instructions contain the rendered shape and follow a change of the schema, and a live run of the configured model that produces the shape.

### LESSON-REQ-0055

- Required check: For every result, verdict or callback that more than one producer could deliver, confirm that the owner is recorded when the work is created, that the origin of a delivery comes from the code path and never from the delivery, and that a delivery from any other origin is refused before it is stored.
- Required evidence: A test that a delivery from the wrong origin is refused before and after the owner's, with a null control through the same path, and a run on the real stack.

### LESSON-REQ-0056

- Required check: For every pinned dependency graph delivered by a Gate, run the current advisory scan against every required source and refuse Critical or High findings without suppressing advisories or narrowing the denominator.
- Required evidence: A report from every required advisory source showing zero relevant Critical or High findings, plus a test that proves those severities remain blocking.

### LESSON-REQ-0057

- Required check: Exercise every required host-published service through its actual loopback port; do not substitute container health for host reachability.
- Required evidence: A live host-facing infrastructure suite after stack health, with the original failure retained if a non-destructive restart is required for recovery.

### LESSON-REQ-0058

- Required check: Confirm every active lesson excluded from a preflight declares a non-empty scope selector, and that incidental metadata does not narrow applicability.
- Required evidence: A passing repository-preflight coverage test over the complete active lesson set.

### LESSON-REQ-0059

- Required check: Whenever one transaction inserts parent and child ORM facts using raw foreign-key identifiers without a relationship edge, confirm the parent is flushed before the child is added.
- Required evidence: A real-database integration test that creates the parent and child together and observes both after commit.

### LESSON-REQ-0060

- Required check: For every running task that can be cancelled, prove the lifecycle records cancellation requested before it records cancellation completed.
- Required evidence: A lifecycle test that enters the intermediate cancelling state, acknowledges cleanup, reaches cancelled, and rejects late delivery.

### LESSON-REQ-0061

- Required check: Whenever provenance is represented by content digests, normalize it as a unique ordered set rather than assuming each semantic source has different bytes.
- Required evidence: A test in which distinct provenance roles share one digest and the stored provenance contains it once.

### LESSON-REQ-0062

- Required check: For every identity crossing a service boundary, verify it satisfies the strictest persisted representation and is stable across delivery retries.
- Required evidence: A contract or unit test proving syntactic validity, deterministic replay identity and separation between distinct work items.

### LESSON-REQ-0063

- Required check: When another durable domain reuses an owned resource, model its real ownership explicitly, require exactly one owner, and preserve every per-owner exclusivity invariant.
- Required evidence: A structural test of the ownership and uniqueness constraints plus a real-database lifecycle test for the new owner.

### LESSON-REQ-0064

- Required check: For a shared execution contract, prove each durable foreign key is populated only for the domain that owns the referenced row, using trusted ownership context rather than identifier shape.
- Required evidence: A test with both owner domains showing that only the owning domain binds the foreign key.

### LESSON-REQ-0065

- Required check: For every content-addressed or reusable immutable record, define material identity separately from creation metadata and ownership provenance.
- Required evidence: A replay test where material inputs are equal but time and first observer differ, proving reuse without rewriting the original record.

### LESSON-REQ-0066

- Required check: For cancellation across an orchestration boundary, test the exception shape the real library delivers and derive outcome from the durable request plus executor acknowledgement rather than the wrapper class alone.
- Required evidence: A workflow test for the wrapped cancellation and a live running-cancellation scenario proving cleanup, terminal cancellation and idempotent repeat.

### LESSON-REQ-0067

- Required check: For every parser-specific content limit applied to a broader inventory, prove unrelated content bypasses that limit while every interpreted candidate remains bounded.
- Required evidence: A paired test with an oversized unrelated file accepted and an oversized interpreted file refused, plus a successful real repository evaluation.

### LESSON-REQ-0068

- Required check: For every polyglot or multi-root project plan, prove each check is expanded at the roots that declared its stack and selects execution policy from the frozen runner rather than one run-wide guessed toolchain.
- Required evidence: A deterministic planning test over multiple roots and stacks, an execution-boundary test for per-runner images, and a successful real polyglot repository evaluation.

### LESSON-REQ-0069

- Required check: For project discovery over a monorepo, prove nested fixture manifests do not become execution roots and every non-applicable unit check is derived from the frozen source inventory rather than from a failed command.
- Required evidence: Paired planner tests proving no-test roots are explicitly non-applicable, test-bearing roots remain mandatory, fixture manifests are excluded, and a real repository evaluation succeeds.

### LESSON-REQ-0070

- Required check: For every shared helper and isolated quality runner, test the oldest pinned runtime actually used by an image and prove each check prepares all dependencies it needs without relying on a previous sandbox session.
- Required evidence: A real snapshot-provisioning test across every quality image, closed-runner assertions for self-contained preparation, and a successful real polyglot repository evaluation.

### LESSON-REQ-0071

- Required check: Whenever more than one gate scans secrets, prove all scanners share the policy-owned finding taxonomy and digest-bound allowance source, and that an unallowlisted match remains blocking.
- Required evidence: Content-addressing tests for scanner and policy inputs, a real negative scan in every execution image, and consistent PASS over the same reviewed repository snapshot.

### LESSON-REQ-0072

- Required check: For every manually scoped repository-wide quality command, derive or test its denominator against the current project inventory so a newly detected root cannot remain outside a green gate.
- Required evidence: A denominator test over all non-fixture manifests plus a successful canonical lint execution and matching real repository Quality Engine verdict.

### LESSON-REQ-0073

- Required check: For Python tests executed from a nested project root, prove the sandbox provides installed distribution metadata and repository-root policy/configuration without reading or writing the host.
- Required evidence: A real snapshot test for metadata and monorepo configuration plus a successful evaluation of a committed multi-package repository.

### LESSON-REQ-0074

- Required check: Whenever a sandbox performs an offline package installation, prove every declared build backend is pinned in the content-addressed execution image and usable by the non-root runtime.
- Required evidence: A real no-network package-installation test through the canonical image-rebuilding sandbox gate.

### LESSON-REQ-0075

- Required check: When repository configuration is projected into a nested project, provide an explicit trusted repository root and prove source-boundary scans do not reinterpret the projection as ownership.
- Required evidence: A real nested sandbox test that observes the explicit root plus the complete source-boundary scan from that environment.

### LESSON-REQ-0076

- Required check: For a functional harness whose workload cardinality differs materially by scenario, prove its bounded wait covers the largest legitimate execution without weakening the product's own timeout or deadline.
- Required evidence: A control that binds every large-workload terminal wait to a distinct finite bound plus successful real executions within that bound.

### LESSON-REQ-0077

- Required check: Before an evidence recorder executes a command, resolve every caller-supplied commit reference to a real canonical commit and normalize repeated provenance inputs.
- Required evidence: A positive canonicalization test and a negative unresolved-commit test proving the command was not executed and the refusal was appended.

### LESSON-REQ-0078

- Required check: For every test applicability rule, prove the corresponding closed runner collects the same project scope and that a failing source at each recognized location is observed.
- Required evidence: A runner-registry assertion plus a real failing fixture whose root-level test produces FAIL with preserved finding and evidence.

### LESSON-REQ-0079

- Required check: Whenever a verification stage writes to a reusable report path, prove the old artifact is removed before execution and cannot survive a failed rerun as current evidence.
- Required evidence: A control that starts with a stale PASS file and observes it absent before the stage command is launched.

### LESSON-REQ-0080

- Required check: Before a canonical checklist is accepted, resolve every named test identity against the suite registry rather than treating prose-like test labels as evidence.
- Required evidence: A repository-wide specification-evidence test that rejects an unknown identity and passes every canonical row.

### LESSON-REQ-0081

- Required check: Keep organizational memory evidence in committed source or checkpoint-owned file artifacts; reject unsupported evidence kinds and references to regenerable runtime output.
- Required evidence: Lesson validation proving every evidence reference is a resolvable repository file and no lesson evidence path begins with file:var/.

### LESSON-REQ-0082

- Required check: For every executable command that captures text from a child process and prints it, configure both the child decoder and the parent output stream explicitly.
- Required evidence: A repository-wide entry-point scan plus a rejecting fixture for an unconfigured captured-output command.

### LESSON-REQ-0083

- Required check: When a predecessor regression test inspects a current entry point, derive current lifecycle identifiers and keep only genuinely historical references fixed.
- Required evidence: A documentation test that resolves the current Gate from repository state while retaining predecessor checklist and runbook links.

### LESSON-REQ-0084

- Required check: When a control judges source structure, parse the language representation and compare semantic nodes instead of binding the rule to formatter whitespace or quote style.
- Required evidence: A source-control test that resolves the relevant syntax nodes and their values without substring adjacency assumptions.

### LESSON-REQ-0085

- Required check: For every subprocess-backed assertion, preserve return code and a non-empty diagnostic even when the child emits nothing; never add a retry that could conceal the outcome.
- Required evidence: A mutation test for nonzero return with empty stdout and stderr that observes the exact exit code.

### LESSON-REQ-0086

- Required check: Every purpose-built worker that hosts a shared workflow must register every activity boundary that workflow can schedule, including not-applicable branches whose decision is made inside an activity.
- Required evidence: A worker-registration control plus a successful real restart rehearsal through the workflow's terminal state.

### LESSON-REQ-0087

- Required check: Whenever a test runs inside a built image and consumes repository content outside its own copied suite, prove the Dockerfile carries that input and the test resolves the same in-image destination.
- Required evidence: A source-boundary control that binds COPY source and in-image path plus a successful execution through the built image.

### LESSON-REQ-0088

- Required check: At every optional domain boundary, prove not-applicable conditions return a bounded negative applicability result while operational errors enter a shared failure taxonomy that can write terminal state.
- Required evidence: A classification control plus real scenarios for the not-applicable and failure paths.

### LESSON-REQ-0089

- Required check: Every clean-clone or repository control must consume only versioned configuration inputs; ignored developer-local files may not be preconditions for a passing gate.
- Required evidence: A test that executes the controlled command with an explicitly versioned configuration file and a passing clean-clone reproduction.

### LESSON-REQ-0090

- Required check: For every durable evidence boundary, scan the exact serialized bytes with the canonical taxonomy before lookup or write, fail closed when scanning cannot complete, and prove rejected bytes cannot resolve or support a verdict.
- Required evidence: A direct zero-write persistence test, a scanner-failure test, a resolution test, and an end-to-end activity attack that derives a failing verdict.

### LESSON-REQ-0091

- Required check: Whenever a sealed audit introduces a bounded report rendering, prove canonical derivation parses its own findings without importing mentions from historical or closure sections.
- Required evidence: Regression tests over the exact sealed report, a negative out-of-section fixture, and a successful canonical requirement derivation.

### LESSON-REQ-0092

- Required check: Whenever a repository tool is copied into a disposable or clean repository, copy every versioned repository package it imports and prove the copied entry point imports from that isolated boundary.
- Required evidence: A central fixture installer, an isolated import regression, and a passing end-to-end disposable delivery flow.

### LESSON-REQ-0093

- Required check: Build review transport from both the truthful changeset and the tracked canonical review context; do not infer that an unchanged mandatory category is irrelevant.
- Required evidence: A regression proving unchanged migrations, schemas, and policies are collected, plus a passing bundle validation over the resulting manifest.

### LESSON-REQ-0094

- Required check: Every live multi-stage verifier must prove that one checkout exclusively owns its Compose project, published ports, volumes and image build inputs for the whole ordered run, while cleanup is restricted to that owned namespace.
- Required evidence: Repository controls for project derivation, frozen stage environment, dynamic ports, build-before-measurement and cleanup refusal, plus a clean ordered live execution.

### LESSON-REQ-0095

- Required check: Every evidence publisher must consume the producer's canonical versioned result fields and prove the mapping behaviorally with a contradictory-alias fixture.
- Required evidence: Regressions against the actual publisher plus a publication report bound to the producer result, denominator and cleanup state.

### LESSON-REQ-0096

- Required check: A review-bundle declaration must identify an immutable reconstruction subject, and validation must rebuild twice from transported Git content and compare digest and size with the declaration before handoff.
- Required evidence: A producer/validator regression, an attack-T failure fixture for stale declarations, and two byte-identical detached-transport rebuilds matching the sealed declaration.

### LESSON-REQ-0097

- Required check: When cancellation is accepted durably, the workflow must observe it before starting and while awaiting a long-running activity, cancel any newly assigned handle, give cancellation precedence over a racing normal response, and wait for cleanup before becoming terminal.
- Required evidence: Deterministic dispatch, handle-handoff, in-flight durable-state and response-precedence regressions, the rebuilt evaluator suite, and a live checkout-owned cancellation scenario that reaches CANCELLED with cancellation evidence and cleanup.

### LESSON-REQ-0098

- Required check: A command refused before execution must retain a recomputable refusal without making its deliberately invalid subject part of the published-history evidence denominator.
- Required evidence: A behavioral recorder/validator regression proving no process executes, the refusal remains valid ledger evidence, and the unresolved subject is not treated as a commit that produced evidence.

### LESSON-REQ-0099

- Required check: An exact detached pre-seal verifier must bind an IN_PROGRESS checkpoint to its checkpoint-named iacode-subjects ref without allowing that ref to substitute for the canonical seal tag.
- Required evidence: Positive and negative detached-checkout regressions proving the subject mode is exact, checkpoint-specific and unavailable after pre-seal work.

### LESSON-REQ-0100

- Required check: Whenever a structural record is created or changed, its canonical index must enumerate the same record, title and status before publication.
- Required evidence: A positive full-enumeration test and a negative mutation test proving a missing index row is rejected.

### LESSON-REQ-0101

- Required check: Any assurance partition must derive category counts from its canonical identifier sets instead of maintaining a duplicate literal that can drift.
- Required evidence: A regression mutating the corrective source set and proving the expected partition changes automatically.

### LESSON-REQ-0102

- Required check: Construct the complete canonical verdict before hashing and execute a valid commitment before attributing a refusal to cancellation.
- Required evidence: Executed positive/negative controls and the fresh mandatory gate suite; failures stay in the ledger.

### LESSON-REQ-0103

- Required check: Keep adapters and live Gate rows aligned with the milestone cadence, preserve internal controls and reject independent verdicts on INTERNAL_GATE_PASS.
- Required evidence: Executed positive/negative controls and the fresh mandatory gate suite; failures stay in the ledger.

### LESSON-REQ-0104

- Required check: Run the existing mandatory lint over every changed source and test path before publishing; repair formatting without weakening lint or assertions.
- Required evidence: Executed positive/negative controls and the fresh mandatory gate suite; failures stay in the ledger.

### LESSON-REQ-0105

- Required check: Bind changes to the intended function and execute its real positive and negative service/activity paths before claiming the repair.
- Required evidence: A valid positive control, a premise check and behavioral proof at the actual target; the complete current mandatory suite.

### LESSON-REQ-0106

- Required check: Prove the generated adverse bytes are recognized by the canonical detector before judging rejection, and retain a clean positive path through the identical execution.
- Required evidence: A valid positive control, a premise check and behavioral proof at the actual target; the complete current mandatory suite.

### LESSON-REQ-0107

- Required check: Read the raw command record as JSON and preserve its exact timestamp; validate lesson datetime fields and reject locale renderings before evidence publication.
- Required evidence: A valid positive control, a premise check and behavioral proof at the actual target; the complete current mandatory suite.

### LESSON-REQ-0108

- Required check: Declare input repositories in canonical policy with reasons and require exact agreement with literal pytest collection; use one boundary for counts and evidence while retaining every mandatory live scenario.
- Required evidence: A valid positive control, a premise check and behavioral proof at the actual target; the complete current mandatory suite.

### LESSON-REQ-0109

- Required check: Keep the deadline unchanged, write a red report with sanitized history failure metadata and pending activity types before cleanup, and never continue adverse cases after a failed clean control.
- Required evidence: A valid positive control, a premise check and behavioral proof at the actual target; the complete current mandatory suite.

### LESSON-REQ-0110

- Required check: Accept typed activity cancellation only when this cleanup requested it, propagate unrelated and precompleted failures, and recheck active handle lifetime after durable reads without losing the accepted cancellation flag.
- Required evidence: A valid positive control, a premise check and behavioral proof at the actual target; the complete current mandatory suite.

### LESSON-REQ-0111

- Required check: Use the identical bounded in-memory transport views for runtime and publication, retain exact component-digest review, never expose values, and keep raw/encoded clean and negative controls.
- Required evidence: A valid positive control, a premise check and behavioral proof at the actual target; the complete current mandatory suite.

### LESSON-REQ-0112

- Required check: Version every changed invariant by the subject's canonical policy, retain mandatory current downgrade controls, and validate all sealed tags with current tooling without altering subjects or narrowing membership.
- Required evidence: Passing current positive/negative and legacy policy controls plus actual current-tool validation over every canonical sealed anchor.

### LESSON-REQ-0113

- Required check: Run the measured source-range regression and all existing transport, secret-boundary and immutable-bundle controls without weakening their rules.
- Required evidence: A causal red range-work measurement, unchanged encoded finding and line controls, a green measured regression and the complete mandatory suite.

### LESSON-REQ-0114

- Required check: Run actual-process long-tail, parameter-exclusion, bounded-count and successful-child controls; retain original stage denominator and exit-code semantics.
- Required evidence: A causal red diagnostic regression followed by green controls and the full verifier.

### LESSON-REQ-0115

- Required check: Generate current state from the latest checkpoint, truthful steps and real local/remote Git; validate exact observations, reject stale or contradictory state and prove the live output cannot dirty or overwrite tracked source.
- Required evidence: Real CLI/Git negative and positive controls, current checkpoint steps and a successful current live-state observation after publication.

### LESSON-REQ-0119

- Required check: Resolve native tool installation/CLI entrypoints and verify actual extracted
  package identities before claiming installability; graphical process launch or a guessed metadata
  path is not installation evidence.
- Required evidence: The retained zero-run timeout, contained installed-adapter positive/adverse
  controls and actual fresh isolated native installation/trust execution with observed cleanup.

## Owned live desktop acceptance plan

### LESSON-REQ-0121

- Required check: After a restart, rediscover an engine-allocated published endpoint and explicitly
  reconfigure owned actors before mutation; authenticate actual host reachability and never retry
  a typed domain/authentication refusal as transport readiness.
- Required evidence: The retained live refusal, actual port-change/HTTP/cleanup probe, executed
  positive/adverse endpoint guard and actual replay rerun (cmd-0082/0084/0086/0091).

### LESSON-REQ-0122

- Required check: Bind selected workspace identity independently of filesystem spelling, then
  revalidate canonical root and exact manifest digest without weakening stale trust/root refusal.
- Required evidence: Retained native and decision-case reds (cmd-0091/0093), executed 27-case green
  and real Python-visible Node guard (cmd-0094/0095), then actual native approval/integration.

### LESSON-REQ-0120

- Required check: Test standard-library host tools under actual Python -I -S cold startup; read
  canonical data directly if its package initializer imports application dependencies. Never
  silently install production dependencies on the host to make a probe start.
- Required evidence: Retained cmd-0077 failure, actual isolated positive/adverse controls and the
  eventual real integration proof, not a substitute fake.

Build a separate `iacode-desktop-` Compose project with dynamic loopback ports and a fresh finite
desktop capability kept only in process/container environment. Rebuild all relevant images. Keep
the operational namespace's container identities unchanged. Fresh-install the CLI into an owned npm
prefix and the VSIX into an owned profile. Exercise the real provider using only the configured
authorized smoke model (also set as this disposable runtime's explicit default, never substituted).

Use an owned loopback forwarding proxy only to interrupt the first already-accepted editor create
response. Keep request/response bytes and HMAC intact; count forwarded operations without recording
tasks, source contents or credentials. Exit the host, launch a new actual host with the same owned
profile, query the pending identity read-only and prove one persisted run and no create replay.
Observe real task stages/budget/sandbox tools and quality results; exercise CLI run/quality
cancellation and cursor recovery. Negative controls attack authentication, replay across API
restart, unsafe IPC, secret upload, snapshot tamper and forged result submission, paired with the
valid clean workflow. Remove only owned profiles/processes/project volumes and observe cleanup.

This is implementation/functional proof, not the later complete verifier or internal assurance
verdict. Any failure is retained and repaired causally before full immutable-subject execution.

### LESSON-REQ-0123 and LESSON-REQ-0124

- Run two-host recovery in the actual persistent context, without extensionTestsPath or seeded
  state. Keep the red proof and installed-source diagnosis; require real SecretStorage/workspace
  recovery and executable positive/adverse launch controls.
- Own native descendants before launch and observe job cleanup and temporary removal. Validate
  exact targets, bound sharing-lock retries and retain failures/counts. Passing installation/
  trust/removal does not replace live recovery acceptance.

### LESSON-REQ-0125

- Refuse exact known capability material and the declared encoded forms before domain IO,
  consent and presentation. Retain the canonical unknown-secret detector unchanged. Prove all
  adverse forms plus clean acceptance, and preserve uncertainty after any signed post-effect
  JSON/data refusal. Complete API/client execution is required, not source presence.

### LESSON-REQ-0126

- Explicitly synchronize the existing operator-managed catalog in a fresh isolated runtime,
  require the exact authorized active model, and refuse missing models/sync failures without
  substitution. Keep desktop IPC closed and production routing unchanged. Require the real
  worker/provider diagnostic, executable negatives and repeated complete workflow.
