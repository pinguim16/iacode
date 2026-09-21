# Closure Requirements - SETUP-00-CP-0010

Derived from the canonical sources listed below, before implementation. The expected set
is recomputed by `policies.expected_requirement_refs` and compared exactly with the
declared set, so a requirement cannot be dropped and the denominator cannot be reduced.

## Sources

- SOURCE A: docs/SETUP-00-CHECKLIST.md, the canonical SETUP-00 specification
- SOURCE B: docs/MILESTONE-VALIDATION.md, the milestone requirements of the audit
- SOURCE C: docs/checkpoints/SETUP-00-CP-0009/REVIEW-REPORT.md, the findings of M0-CP-0009
- SOURCE D: docs/checkpoints/SETUP-00-CP-0009/RED-TEAM-REPORT.md, the mandatory attacks of M0-CP-0009
- SOURCE E: LESSON-PREFLIGHT.json, the lessons the engineering memory imposes

## Requirements

| ID | Source | Anchor | Mandatory | Implementation | Final | Description |
|---|---|---|---|---|---|---|
| `REQ-0001` | SETUP | `canonical:SETUP-00#1.1` | yes | `NOT_STARTED` | `NOT_STARTED` | A single entry point states the phase, current Gate, latest checkpoint, and start protocol. |
| `REQ-0002` | SETUP | `canonical:SETUP-00#1.2` | yes | `NOT_STARTED` | `NOT_STARTED` | A Codex adapter binds the canonical contracts without adding independent policy. |
| `REQ-0003` | SETUP | `canonical:SETUP-00#1.3` | yes | `NOT_STARTED` | `NOT_STARTED` | A Claude Code adapter binds the same contracts. |
| `REQ-0004` | SETUP | `canonical:SETUP-00#1.4` | yes | `NOT_STARTED` | `NOT_STARTED` | Tool adapters stay semantically equivalent to the canonical roles. |
| `REQ-0005` | SETUP | `canonical:SETUP-00#2.1` | yes | `NOT_STARTED` | `NOT_STARTED` | The Gate sequence, dependencies, acceptance, and fail conditions are recorded. |
| `REQ-0006` | SETUP | `canonical:SETUP-00#2.2` | yes | `NOT_STARTED` | `NOT_STARTED` | The completion standard, mandatory controls, and Git and evidence discipline are recorded. |
| `REQ-0007` | SETUP | `canonical:SETUP-00#2.3` | yes | `NOT_STARTED` | `NOT_STARTED` | Tool-to-tool transfer is formal in both directions. |
| `REQ-0008` | SETUP | `canonical:SETUP-00#2.4` | yes | `NOT_STARTED` | `NOT_STARTED` | Checkpoint statuses, required events, required contents, commit semantics, and divergence handling are defined. |
| `REQ-0009` | SETUP | `canonical:SETUP-00#2.5` | yes | `NOT_STARTED` | `NOT_STARTED` | Done is defined and excludes assertion-only PASS. |
| `REQ-0010` | SETUP | `canonical:SETUP-00#2.6` | yes | `NOT_STARTED` | `NOT_STARTED` | Quality outcomes, required dimensions, and the promotion rule are defined. |
| `REQ-0011` | SETUP | `canonical:SETUP-00#2.7` | yes | `NOT_STARTED` | `NOT_STARTED` | Structural decisions are recorded as ADRs. |
| `REQ-0012` | SETUP | `canonical:SETUP-00#2.8` | yes | `NOT_STARTED` | `NOT_STARTED` | Architecture, roadmap, provenance, model usage, and detected tool capabilities are documented. |
| `REQ-0013` | SETUP | `canonical:SETUP-00#3.1` | yes | `NOT_STARTED` | `NOT_STARTED` | The canonical, tool-neutral role contracts exist, one per role of the delivery protocol. |
| `REQ-0014` | SETUP | `canonical:SETUP-00#3.2` | yes | `NOT_STARTED` | `NOT_STARTED` | Documentation, provenance, secret, tool-execution, and training-data policies exist. |
| `REQ-0015` | SETUP | `canonical:SETUP-00#3.3` | yes | `NOT_STARTED` | `NOT_STARTED` | Reusable templates exist for ADRs, checkpoints, gate reports, and handoffs. |
| `REQ-0016` | SETUP | `canonical:SETUP-00#4.1` | yes | `NOT_STARTED` | `NOT_STARTED` | Checkpoint state, run metadata, command, test, quality, provenance, and decision schemas exist and are loadable. |
| `REQ-0017` | SETUP | `canonical:SETUP-00#4.2` | yes | `NOT_STARTED` | `NOT_STARTED` | An experience schema is reserved for Gate 6 and implements no runtime. |
| `REQ-0018` | SETUP | `canonical:SETUP-00#4.3` | yes | `NOT_STARTED` | `NOT_STARTED` | Schema evolution is versioned and never invalidates a sealed checkpoint. |
| `REQ-0019` | SETUP | `canonical:SETUP-00#5.1` | yes | `NOT_STARTED` | `NOT_STARTED` | A checkpoint can be created with truthful non-PASS defaults. |
| `REQ-0020` | SETUP | `canonical:SETUP-00#5.2` | yes | `NOT_STARTED` | `NOT_STARTED` | A checkpoint can be finalized, and every finalization attempt is recorded with its exit code. |
| `REQ-0021` | SETUP | `canonical:SETUP-00#5.3` | yes | `NOT_STARTED` | `NOT_STARTED` | A checkpoint is validated against schemas, Git state, inventory, quality evidence, and secrets. |
| `REQ-0022` | SETUP | `canonical:SETUP-00#5.4` | yes | `NOT_STARTED` | `NOT_STARTED` | Secret redaction is available and documented to its real scope. |
| `REQ-0023` | SETUP | `canonical:SETUP-00#5.5` | yes | `NOT_STARTED` | `NOT_STARTED` | The tooling is standard-library only and portable across Windows and Unix-like checkouts. |
| `REQ-0024` | SETUP | `canonical:SETUP-00#6.1` | yes | `NOT_STARTED` | `NOT_STARTED` | Every checkpoint carries status, handoff, run metadata, state, plan, decisions, commands, file inventory, tests, quality, provenance, diff summary, risks, and next action. |
| `REQ-0025` | SETUP | `canonical:SETUP-00#6.2` | yes | `NOT_STARTED` | `NOT_STARTED` | `LATEST.md` points textually to the last checkpoint accepted by validation. |
| `REQ-0026` | SETUP | `canonical:SETUP-00#6.3` | yes | `NOT_STARTED` | `NOT_STARTED` | The file inventory matches the real change set, with bound content hashes. |
| `REQ-0027` | SETUP | `canonical:SETUP-00#6.4` | yes | `NOT_STARTED` | `NOT_STARTED` | Provenance is complete and `trainingAllowed` defaults to `false`. |
| `REQ-0028` | SETUP | `canonical:SETUP-00#6.5` | yes | `NOT_STARTED` | `NOT_STARTED` | A quality `PASS` carries resolvable evidence. |
| `REQ-0029` | SETUP | `canonical:SETUP-00#6.6` | yes | `NOT_STARTED` | `NOT_STARTED` | Handoff-ready and terminal checkpoints are anchored to an immutable namespaced tag. |
| `REQ-0030` | SETUP | `canonical:SETUP-00#7.1` | yes | `NOT_STARTED` | `NOT_STARTED` | A cold-start continuation prompt exists and depends only on checked-in files. |
| `REQ-0031` | SETUP | `canonical:SETUP-00#7.2` | yes | `NOT_STARTED` | `NOT_STARTED` | Cold-start validation is executed and recorded truthfully, including a blocked attempt. |
| `REQ-0032` | SETUP | `canonical:SETUP-00#7.3` | yes | `NOT_STARTED` | `NOT_STARTED` | Cross-tool validation state is structured and explicit. |
| `REQ-0033` | SETUP | `canonical:SETUP-00#7.4` | yes | `NOT_STARTED` | `NOT_STARTED` | A sealed checkpoint can be validated from a detached checkout of its own tag. |
| `REQ-0034` | SETUP | `canonical:SETUP-00#7.5` | yes | `NOT_STARTED` | `NOT_STARTED` | The handoff is executable by another tool without the producing session. |
| `REQ-0035` | SETUP | `canonical:SETUP-00#7b.1` | yes | `NOT_STARTED` | `NOT_STARTED` | Every requirement of a delivery exists in a versioned matrix before implementation. |
| `REQ-0036` | SETUP | `canonical:SETUP-00#7b.2` | yes | `NOT_STARTED` | `NOT_STARTED` | A Test Rework / Green Keeper role forbids shipping anything red and records every cycle. |
| `REQ-0037` | SETUP | `canonical:SETUP-00#7b.3` | yes | `NOT_STARTED` | `NOT_STARTED` | A Delivery Completeness Validator audits the matrix before handoff and may not implement. |
| `REQ-0038` | SETUP | `canonical:SETUP-00#7b.4` | yes | `NOT_STARTED` | `NOT_STARTED` | `GREEN_KEEPER_GATE` and `DELIVERY_COMPLETENESS_GATE` are preconditions of `READY_FOR_REVIEW`. |
| `REQ-0039` | SETUP | `canonical:SETUP-00#7b.5` | yes | `NOT_STARTED` | `NOT_STARTED` | Readiness and blockage can never be claimed together. |
| `REQ-0040` | SETUP | `canonical:SETUP-00#7b.6` | yes | `NOT_STARTED` | `NOT_STARTED` | Every operation attempt is recorded, including a refusal decided before execution. |
| `REQ-0041` | SETUP | `canonical:SETUP-00#7b.7` | yes | `NOT_STARTED` | `NOT_STARTED` | Every recorded command is reproducible from its declared working directory. |
| `REQ-0042` | SETUP | `canonical:SETUP-00#7b.8` | yes | `NOT_STARTED` | `NOT_STARTED` | The mandatory delivery order is stated in full in every governing document and both adapters. |
| `REQ-0043` | SETUP | `canonical:SETUP-00#7c.1` | yes | `NOT_STARTED` | `NOT_STARTED` | The project keeps an organizational engineering memory of confirmed failures. |
| `REQ-0044` | SETUP | `canonical:SETUP-00#7c.2` | yes | `NOT_STARTED` | `NOT_STARTED` | A lesson is `GUARDED` only when an automated control prevents recurrence. |
| `REQ-0045` | SETUP | `canonical:SETUP-00#7c.3` | yes | `NOT_STARTED` | `NOT_STARTED` | A repeat increments recurrence, and a repeat against a guardrail is a `GUARDRAIL_FAILURE`. |
| `REQ-0046` | SETUP | `canonical:SETUP-00#7c.4` | yes | `NOT_STARTED` | `NOT_STARTED` | A mandatory preflight selects the lessons that constrain each Gate. |
| `REQ-0047` | SETUP | `canonical:SETUP-00#7c.5` | yes | `NOT_STARTED` | `NOT_STARTED` | Applicable lessons become requirements whose absence blocks completeness. |
| `REQ-0048` | SETUP | `canonical:SETUP-00#7c.6` | yes | `NOT_STARTED` | `NOT_STARTED` | Lesson candidates can be extracted from recorded delivery evidence, never above `OBSERVED`. |
| `REQ-0049` | SETUP | `canonical:SETUP-00#7c.7` | yes | `NOT_STARTED` | `NOT_STARTED` | External validation is grouped into milestones `M0` to `M6`. |
| `REQ-0050` | SETUP | `canonical:SETUP-00#7c.8` | yes | `NOT_STARTED` | `NOT_STARTED` | An internal verdict is never described as independent external validation. |
| `REQ-0051` | SETUP | `canonical:SETUP-00#7c.9` | yes | `NOT_STARTED` | `NOT_STARTED` | An extraordinary audit requires a recorded trigger. |
| `REQ-0052` | SETUP | `canonical:SETUP-00#7c.10` | yes | `NOT_STARTED` | `NOT_STARTED` | Every completed Gate produces a retrospective. |
| `REQ-0053` | SETUP | `canonical:SETUP-00#7d.1` | yes | `NOT_STARTED` | `NOT_STARTED` | One promotion invariant governs every positive terminal status, not only `READY_FOR_REVIEW`. |
| `REQ-0054` | SETUP | `canonical:SETUP-00#7d.2` | yes | `NOT_STARTED` | `NOT_STARTED` | The mandatory quality gate set is a closed machine-readable registry that an invocation cannot narrow. |
| `REQ-0055` | SETUP | `canonical:SETUP-00#7d.3` | yes | `NOT_STARTED` | `NOT_STARTED` | The expected requirement set is derived from canonical sources and compared exactly with the declared set. |
| `REQ-0056` | SETUP | `canonical:SETUP-00#7d.4` | yes | `NOT_STARTED` | `NOT_STARTED` | An external milestone PASS is derived from an audit attestation authored by another sealed checkpoint. |
| `REQ-0057` | SETUP | `canonical:SETUP-00#7d.5` | yes | `NOT_STARTED` | `NOT_STARTED` | A derived artifact carries a fingerprint of its inputs, and staleness is decided by recomputation. |
| `REQ-0058` | SETUP | `canonical:SETUP-00#7d.6` | yes | `NOT_STARTED` | `NOT_STARTED` | Every lesson control, evidence path and provenance locator is resolved against the repository. |
| `REQ-0059` | SETUP | `canonical:SETUP-00#7d.7` | yes | `NOT_STARTED` | `NOT_STARTED` | Every `GUARDED` lesson names a registered guardrail, and guardrail effectiveness is measured. |
| `REQ-0060` | SETUP | `canonical:SETUP-00#7d.8` | yes | `NOT_STARTED` | `NOT_STARTED` | Sealed checkpoints are anchored by a hash-linked chain over tag, commit and tree. |
| `REQ-0061` | SETUP | `canonical:SETUP-00#7d.9` | yes | `NOT_STARTED` | `NOT_STARTED` | Every count used as evidence is derived once and verified wherever a report states it. |
| `REQ-0062` | SETUP | `canonical:SETUP-00#7d.10` | yes | `NOT_STARTED` | `NOT_STARTED` | Sealing is monotonic and post-commit, and every recorded command binds its declared inputs by content. |
| `REQ-0063` | SETUP | `canonical:SETUP-00#7d.11` | yes | `NOT_STARTED` | `NOT_STARTED` | A milestone delivery carries an internal Red Team and an internal mirror audit, and neither is recorded as external validation. |
| `REQ-0064` | SETUP | `canonical:SETUP-00#7d.12` | yes | `NOT_STARTED` | `NOT_STARTED` | Every finding of an independent audit is closed before the corrective delivery is offered. |
| `REQ-0065` | SETUP | `canonical:SETUP-00#7d.13` | yes | `NOT_STARTED` | `NOT_STARTED` | A milestone verdict is carried by the audit checkpoint about a sealed subject, and its positive path is executed rather than only its refusals. |
| `REQ-0066` | SETUP | `canonical:SETUP-00#7d.14` | yes | `NOT_STARTED` | `NOT_STARTED` | A generic guardrail derives repository state instead of naming a historical checkpoint, and the protocol's own next steps keep every mandatory gate green. |
| `REQ-0067` | SETUP | `canonical:SETUP-00#7d.15` | yes | `NOT_STARTED` | `NOT_STARTED` | Every adversarial battery records a null-mutation control, and no count used as evidence is stated in prose. |
| `REQ-0068` | SETUP | `canonical:SETUP-00#8.1` | yes | `NOT_STARTED` | `NOT_STARTED` | An independent review is recorded. |
| `REQ-0069` | SETUP | `canonical:SETUP-00#8.2` | yes | `NOT_STARTED` | `NOT_STARTED` | An adversarial Red Team is recorded. |
| `REQ-0070` | SETUP | `canonical:SETUP-00#8.3` | yes | `NOT_STARTED` | `NOT_STARTED` | `GATE_PASS` is granted only by a run independent of the implementer. |
| `REQ-0071` | SETUP | `canonical:SETUP-00#9.1` | yes | `NOT_STARTED` | `NOT_STARTED` | No Gate 0 or later runtime is implemented during SETUP-00. |
| `REQ-0072` | SETUP | `canonical:SETUP-00#9.2` | yes | `NOT_STARTED` | `NOT_STARTED` | Documentation is maintained continuously rather than reconstructed at the end. |
| `REQ-0073` | SETUP | `canonical:SETUP-00#9.3` | yes | `NOT_STARTED` | `NOT_STARTED` | No secret, credential, or private chain-of-thought is stored. |
| `REQ-0074` | SETUP | `canonical:SETUP-00#9.4` | yes | `NOT_STARTED` | `NOT_STARTED` | Gate advancement requires explicit authorization and a passing previous Gate. |
| `REQ-0075` | AUDIT_FINDING | `finding:CP9-F-001` | yes | `NOT_STARTED` | `NOT_STARTED` | the external audit attestation can be written but never consumed, so `MILESTONE_EXTERNAL_PASS` is unreachable |
| `REQ-0076` | AUDIT_FINDING | `finding:CP9-F-002` | yes | `NOT_STARTED` | `NOT_STARTED` | a guardrail test is bound to a literal checkpoint name, so performing the protocol's own next step turns the mandatory `tests` gate red |
| `REQ-0077` | AUDIT_FINDING | `finding:CP9-F-003` | yes | `NOT_STARTED` | `NOT_STARTED` | a stale count survives in a current artifact because the count guardrail only inspects Markdown |
| `REQ-0078` | AUDIT_FINDING | `finding:CP9-F-004` | yes | `NOT_STARTED` | `NOT_STARTED` | a lesson's own note contradicts its status |
| `REQ-0079` | AUDIT_FINDING | `finding:CP9-F-005` | yes | `NOT_STARTED` | `NOT_STARTED` | a policy key is declared and never read |
| `REQ-0080` | AUDIT_ATTACK | `attack:A` | yes | `NOT_STARTED` | `NOT_STARTED` | Defend attack A: Add a blocker to a READY_FOR_REVIEW checkpoint |
| `REQ-0081` | AUDIT_ATTACK | `attack:B` | yes | `NOT_STARTED` | `NOT_STARTED` | Defend attack B: Set a review-ready quality dimension red |
| `REQ-0082` | AUDIT_ATTACK | `attack:C` | yes | `NOT_STARTED` | `NOT_STARTED` | Defend attack C: Delete a canonical requirement and recompute every count |
| `REQ-0083` | AUDIT_ATTACK | `attack:D` | yes | `NOT_STARTED` | `NOT_STARTED` | Defend attack D: Forge the stored counts of a passing report |
| `REQ-0084` | AUDIT_ATTACK | `attack:E` | yes | `NOT_STARTED` | `NOT_STARTED` | Defend attack E: Remove a lesson-derived requirement from the matrix |
| `REQ-0085` | AUDIT_ATTACK | `attack:F` | yes | `NOT_STARTED` | `NOT_STARTED` | Defend attack F: Replace a preventive control with documentation only |
| `REQ-0086` | AUDIT_ATTACK | `attack:G` | yes | `NOT_STARTED` | `NOT_STARTED` | Defend attack G: Duplicate a lesson identifier |
| `REQ-0087` | AUDIT_ATTACK | `attack:H` | yes | `NOT_STARTED` | `NOT_STARTED` | Defend attack H: Insert a secret-shaped value into a scanned field |
| `REQ-0088` | AUDIT_ATTACK | `attack:I` | yes | `NOT_STARTED` | `NOT_STARTED` | Defend attack I: Rewrite a sealed predecessor, refresh hashes and move its tag |
| `REQ-0089` | AUDIT_ATTACK | `attack:J` | yes | `NOT_STARTED` | `NOT_STARTED` | Defend attack J: Move a checkpoint tag and HEAD together |
| `REQ-0090` | AUDIT_ATTACK | `attack:K` | yes | `NOT_STARTED` | `NOT_STARTED` | Defend attack K: Remove one inventory entry |
| `REQ-0091` | AUDIT_ATTACK | `attack:L` | yes | `NOT_STARTED` | `NOT_STARTED` | Defend attack L: Silently modify a tracked file |
| `REQ-0092` | AUDIT_ATTACK | `attack:M` | yes | `NOT_STARTED` | `NOT_STARTED` | Defend attack M: Set a wrong hashBefore |
| `REQ-0093` | AUDIT_ATTACK | `attack:N` | yes | `NOT_STARTED` | `NOT_STARTED` | Defend attack N: Set a wrong hashAfter |
| `REQ-0094` | AUDIT_ATTACK | `attack:O` | yes | `NOT_STARTED` | `NOT_STARTED` | Defend attack O: Claim PASS with no evidence |
| `REQ-0095` | AUDIT_ATTACK | `attack:P` | yes | `NOT_STARTED` | `NOT_STARTED` | Defend attack P: Reference an unknown command |
| `REQ-0096` | AUDIT_ATTACK | `attack:Q` | yes | `NOT_STARTED` | `NOT_STARTED` | Defend attack Q: Supply complete attribution with empty evidence |
| `REQ-0097` | AUDIT_ATTACK | `attack:R` | yes | `NOT_STARTED` | `NOT_STARTED` | Defend attack R: Promote an internally authored result to an external status |
| `REQ-0098` | AUDIT_ATTACK | `attack:S` | yes | `NOT_STARTED` | `NOT_STARTED` | Defend attack S: Leave review and Red Team pending with a null auditor |
| `REQ-0099` | AUDIT_ATTACK | `attack:T` | yes | `NOT_STARTED` | `NOT_STARTED` | Defend attack T: Request an audit without a known trigger |
| `REQ-0100` | AUDIT_ATTACK | `attack:U` | yes | `NOT_STARTED` | `NOT_STARTED` | Defend attack U: Retire a canonical lesson but keep the active preflight |
| `REQ-0101` | AUDIT_ATTACK | `attack:V` | yes | `NOT_STARTED` | `NOT_STARTED` | Defend attack V: Run the Green Keeper with an empty gate selection |
| `REQ-0102` | AUDIT_ATTACK | `attack:W` | yes | `NOT_STARTED` | `NOT_STARTED` | Defend attack W: Claim PASS with a PARTIAL requirement |
| `REQ-0103` | AUDIT_ATTACK | `attack:X` | yes | `NOT_STARTED` | `NOT_STARTED` | Defend attack X: Remove a required field from a command record |
| `REQ-0104` | AUDIT_ATTACK | `attack:Y` | yes | `NOT_STARTED` | `NOT_STARTED` | Defend attack Y: Point LATEST.md at an older checkpoint |
| `REQ-0105` | AUDIT_ATTACK | `attack:Z` | yes | `NOT_STARTED` | `NOT_STARTED` | Defend attack Z: Use path traversal as the Gate identifier |
| `LESSON-REQ-0001` | LESSON | `lesson:LSN-0001` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify checkpoint validation must succeed from a detached checkout of the checkpoint tag |
| `LESSON-REQ-0002` | LESSON | `lesson:LSN-0002` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a file inventory must be recomputed from the repository, never trusted as an assertion |
| `LESSON-REQ-0003` | LESSON | `lesson:LSN-0003` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify every operation attempt must be auditable, including a refusal decided before execution |
| `LESSON-REQ-0004` | LESSON | `lesson:LSN-0004` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a checkpoint may never claim readiness while it also claims to be blocked |
| `LESSON-REQ-0005` | LESSON | `lesson:LSN-0005` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a PASS requires evidence that can be executed or resolved, not a statement |
| `LESSON-REQ-0006` | LESSON | `lesson:LSN-0006` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify the repository must be self-contained; a specification may not live outside it |
| `LESSON-REQ-0007` | LESSON | `lesson:LSN-0007` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify independent validation cannot be declared by the run that did the work |
| `LESSON-REQ-0008` | LESSON | `lesson:LSN-0008` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify requirement completeness must be total and evidence-backed before handoff |
| `LESSON-REQ-0009` | LESSON | `lesson:LSN-0009` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a red gate requires rework, never a waiver, and never a weakened check |
| `LESSON-REQ-0010` | LESSON | `lesson:LSN-0010` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a recorded command must carry runtime, working directory, commit and purpose to be replayable |
| `LESSON-REQ-0011` | LESSON | `lesson:LSN-0011` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a control over a checkpoint's own evidence must be scoped to the moment it matters |
| `LESSON-REQ-0012` | LESSON | `lesson:LSN-0012` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify sealed checkpoints and their tags are immutable, and tooling must keep validating them |
| `LESSON-REQ-0013` | LESSON | `lesson:LSN-0013` | no | `NOT_STARTED` | `NOT_STARTED` | Verify an installed capability must be detected by resolved path, not by a bare command lookup |
| `LESSON-REQ-0014` | LESSON | `lesson:LSN-0014` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify evidence must be recorded as it happens, not reconstructed at the end of a run |
| `LESSON-REQ-0015` | LESSON | `lesson:LSN-0015` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify every positive terminal status needs one shared promotion invariant |
| `LESSON-REQ-0016` | LESSON | `lesson:LSN-0016` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a mandatory set must be closed by policy, never chosen by the caller |
| `LESSON-REQ-0017` | LESSON | `lesson:LSN-0017` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a completeness denominator must come from a source the delivery does not own |
| `LESSON-REQ-0018` | LESSON | `lesson:LSN-0018` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a structured reference must be resolved, not merely well typed |
| `LESSON-REQ-0019` | LESSON | `lesson:LSN-0019` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a derived artifact must carry a fingerprint of the inputs that produced it |
| `LESSON-REQ-0020` | LESSON | `lesson:LSN-0020` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify evidence produced from a dirty tree needs immutable input identity |
| `LESSON-REQ-0021` | LESSON | `lesson:LSN-0021` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify sealed history needs an anchor outside the content it describes |
| `LESSON-REQ-0022` | LESSON | `lesson:LSN-0022` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify an authoritative count must be derived once, never maintained by hand twice |
| `LESSON-REQ-0023` | LESSON | `lesson:LSN-0023` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a lesson must cite a source that actually records the finding it claims |
| `LESSON-REQ-0024` | LESSON | `lesson:LSN-0024` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a control is finished only when its positive path has been executed, not only its refusals |
| `LESSON-REQ-0025` | LESSON | `lesson:LSN-0025` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a generic guardrail derives repository state instead of naming today's checkpoint |
| `LESSON-REQ-0026` | LESSON | `lesson:LSN-0026` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify an adversarial battery without a null-mutation control proves nothing |
| `LESSON-REQ-0027` | LESSON | `lesson:LSN-0027` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a lesson's prose may record a residual limit but may never contradict its status |
| `LESSON-REQ-0028` | LESSON | `lesson:LSN-0028` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a configuration key that no code reads is a defect, not documentation |
| `LESSON-REQ-0029` | LESSON | `lesson:LSN-0029` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a required protocol transition must never turn a mandatory gate red |

## Evidence

### REQ-0001 - canonical:SETUP-00#1.1

- Source reference: docs/SETUP-00-CHECKLIST.md row 1.1
- Description: A single entry point states the phase, current Gate, latest checkpoint, and start protocol.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0002 - canonical:SETUP-00#1.2

- Source reference: docs/SETUP-00-CHECKLIST.md row 1.2
- Description: A Codex adapter binds the canonical contracts without adding independent policy.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0003 - canonical:SETUP-00#1.3

- Source reference: docs/SETUP-00-CHECKLIST.md row 1.3
- Description: A Claude Code adapter binds the same contracts.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0004 - canonical:SETUP-00#1.4

- Source reference: docs/SETUP-00-CHECKLIST.md row 1.4
- Description: Tool adapters stay semantically equivalent to the canonical roles.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0005 - canonical:SETUP-00#2.1

- Source reference: docs/SETUP-00-CHECKLIST.md row 2.1
- Description: The Gate sequence, dependencies, acceptance, and fail conditions are recorded.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0006 - canonical:SETUP-00#2.2

- Source reference: docs/SETUP-00-CHECKLIST.md row 2.2
- Description: The completion standard, mandatory controls, and Git and evidence discipline are recorded.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0007 - canonical:SETUP-00#2.3

- Source reference: docs/SETUP-00-CHECKLIST.md row 2.3
- Description: Tool-to-tool transfer is formal in both directions.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0008 - canonical:SETUP-00#2.4

- Source reference: docs/SETUP-00-CHECKLIST.md row 2.4
- Description: Checkpoint statuses, required events, required contents, commit semantics, and divergence handling are defined.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0009 - canonical:SETUP-00#2.5

- Source reference: docs/SETUP-00-CHECKLIST.md row 2.5
- Description: Done is defined and excludes assertion-only PASS.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0010 - canonical:SETUP-00#2.6

- Source reference: docs/SETUP-00-CHECKLIST.md row 2.6
- Description: Quality outcomes, required dimensions, and the promotion rule are defined.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0011 - canonical:SETUP-00#2.7

- Source reference: docs/SETUP-00-CHECKLIST.md row 2.7
- Description: Structural decisions are recorded as ADRs.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0012 - canonical:SETUP-00#2.8

- Source reference: docs/SETUP-00-CHECKLIST.md row 2.8
- Description: Architecture, roadmap, provenance, model usage, and detected tool capabilities are documented.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0013 - canonical:SETUP-00#3.1

- Source reference: docs/SETUP-00-CHECKLIST.md row 3.1
- Description: The canonical, tool-neutral role contracts exist, one per role of the delivery protocol.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0014 - canonical:SETUP-00#3.2

- Source reference: docs/SETUP-00-CHECKLIST.md row 3.2
- Description: Documentation, provenance, secret, tool-execution, and training-data policies exist.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0015 - canonical:SETUP-00#3.3

- Source reference: docs/SETUP-00-CHECKLIST.md row 3.3
- Description: Reusable templates exist for ADRs, checkpoints, gate reports, and handoffs.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0016 - canonical:SETUP-00#4.1

- Source reference: docs/SETUP-00-CHECKLIST.md row 4.1
- Description: Checkpoint state, run metadata, command, test, quality, provenance, and decision schemas exist and are loadable.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0017 - canonical:SETUP-00#4.2

- Source reference: docs/SETUP-00-CHECKLIST.md row 4.2
- Description: An experience schema is reserved for Gate 6 and implements no runtime.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0018 - canonical:SETUP-00#4.3

- Source reference: docs/SETUP-00-CHECKLIST.md row 4.3
- Description: Schema evolution is versioned and never invalidates a sealed checkpoint.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0019 - canonical:SETUP-00#5.1

- Source reference: docs/SETUP-00-CHECKLIST.md row 5.1
- Description: A checkpoint can be created with truthful non-PASS defaults.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0020 - canonical:SETUP-00#5.2

- Source reference: docs/SETUP-00-CHECKLIST.md row 5.2
- Description: A checkpoint can be finalized, and every finalization attempt is recorded with its exit code.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0021 - canonical:SETUP-00#5.3

- Source reference: docs/SETUP-00-CHECKLIST.md row 5.3
- Description: A checkpoint is validated against schemas, Git state, inventory, quality evidence, and secrets.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0022 - canonical:SETUP-00#5.4

- Source reference: docs/SETUP-00-CHECKLIST.md row 5.4
- Description: Secret redaction is available and documented to its real scope.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0023 - canonical:SETUP-00#5.5

- Source reference: docs/SETUP-00-CHECKLIST.md row 5.5
- Description: The tooling is standard-library only and portable across Windows and Unix-like checkouts.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0024 - canonical:SETUP-00#6.1

- Source reference: docs/SETUP-00-CHECKLIST.md row 6.1
- Description: Every checkpoint carries status, handoff, run metadata, state, plan, decisions, commands, file inventory, tests, quality, provenance, diff summary, risks, and next action.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0025 - canonical:SETUP-00#6.2

- Source reference: docs/SETUP-00-CHECKLIST.md row 6.2
- Description: `LATEST.md` points textually to the last checkpoint accepted by validation.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0026 - canonical:SETUP-00#6.3

- Source reference: docs/SETUP-00-CHECKLIST.md row 6.3
- Description: The file inventory matches the real change set, with bound content hashes.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0027 - canonical:SETUP-00#6.4

- Source reference: docs/SETUP-00-CHECKLIST.md row 6.4
- Description: Provenance is complete and `trainingAllowed` defaults to `false`.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0028 - canonical:SETUP-00#6.5

- Source reference: docs/SETUP-00-CHECKLIST.md row 6.5
- Description: A quality `PASS` carries resolvable evidence.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0029 - canonical:SETUP-00#6.6

- Source reference: docs/SETUP-00-CHECKLIST.md row 6.6
- Description: Handoff-ready and terminal checkpoints are anchored to an immutable namespaced tag.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0030 - canonical:SETUP-00#7.1

- Source reference: docs/SETUP-00-CHECKLIST.md row 7.1
- Description: A cold-start continuation prompt exists and depends only on checked-in files.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0031 - canonical:SETUP-00#7.2

- Source reference: docs/SETUP-00-CHECKLIST.md row 7.2
- Description: Cold-start validation is executed and recorded truthfully, including a blocked attempt.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0032 - canonical:SETUP-00#7.3

- Source reference: docs/SETUP-00-CHECKLIST.md row 7.3
- Description: Cross-tool validation state is structured and explicit.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0033 - canonical:SETUP-00#7.4

- Source reference: docs/SETUP-00-CHECKLIST.md row 7.4
- Description: A sealed checkpoint can be validated from a detached checkout of its own tag.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0034 - canonical:SETUP-00#7.5

- Source reference: docs/SETUP-00-CHECKLIST.md row 7.5
- Description: The handoff is executable by another tool without the producing session.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0035 - canonical:SETUP-00#7b.1

- Source reference: docs/SETUP-00-CHECKLIST.md row 7b.1
- Description: Every requirement of a delivery exists in a versioned matrix before implementation.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0036 - canonical:SETUP-00#7b.2

- Source reference: docs/SETUP-00-CHECKLIST.md row 7b.2
- Description: A Test Rework / Green Keeper role forbids shipping anything red and records every cycle.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0037 - canonical:SETUP-00#7b.3

- Source reference: docs/SETUP-00-CHECKLIST.md row 7b.3
- Description: A Delivery Completeness Validator audits the matrix before handoff and may not implement.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0038 - canonical:SETUP-00#7b.4

- Source reference: docs/SETUP-00-CHECKLIST.md row 7b.4
- Description: `GREEN_KEEPER_GATE` and `DELIVERY_COMPLETENESS_GATE` are preconditions of `READY_FOR_REVIEW`.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0039 - canonical:SETUP-00#7b.5

- Source reference: docs/SETUP-00-CHECKLIST.md row 7b.5
- Description: Readiness and blockage can never be claimed together.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0040 - canonical:SETUP-00#7b.6

- Source reference: docs/SETUP-00-CHECKLIST.md row 7b.6
- Description: Every operation attempt is recorded, including a refusal decided before execution.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0041 - canonical:SETUP-00#7b.7

- Source reference: docs/SETUP-00-CHECKLIST.md row 7b.7
- Description: Every recorded command is reproducible from its declared working directory.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0042 - canonical:SETUP-00#7b.8

- Source reference: docs/SETUP-00-CHECKLIST.md row 7b.8
- Description: The mandatory delivery order is stated in full in every governing document and both adapters.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0043 - canonical:SETUP-00#7c.1

- Source reference: docs/SETUP-00-CHECKLIST.md row 7c.1
- Description: The project keeps an organizational engineering memory of confirmed failures.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0044 - canonical:SETUP-00#7c.2

- Source reference: docs/SETUP-00-CHECKLIST.md row 7c.2
- Description: A lesson is `GUARDED` only when an automated control prevents recurrence.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0045 - canonical:SETUP-00#7c.3

- Source reference: docs/SETUP-00-CHECKLIST.md row 7c.3
- Description: A repeat increments recurrence, and a repeat against a guardrail is a `GUARDRAIL_FAILURE`.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0046 - canonical:SETUP-00#7c.4

- Source reference: docs/SETUP-00-CHECKLIST.md row 7c.4
- Description: A mandatory preflight selects the lessons that constrain each Gate.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0047 - canonical:SETUP-00#7c.5

- Source reference: docs/SETUP-00-CHECKLIST.md row 7c.5
- Description: Applicable lessons become requirements whose absence blocks completeness.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0048 - canonical:SETUP-00#7c.6

- Source reference: docs/SETUP-00-CHECKLIST.md row 7c.6
- Description: Lesson candidates can be extracted from recorded delivery evidence, never above `OBSERVED`.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0049 - canonical:SETUP-00#7c.7

- Source reference: docs/SETUP-00-CHECKLIST.md row 7c.7
- Description: External validation is grouped into milestones `M0` to `M6`.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0050 - canonical:SETUP-00#7c.8

- Source reference: docs/SETUP-00-CHECKLIST.md row 7c.8
- Description: An internal verdict is never described as independent external validation.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0051 - canonical:SETUP-00#7c.9

- Source reference: docs/SETUP-00-CHECKLIST.md row 7c.9
- Description: An extraordinary audit requires a recorded trigger.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0052 - canonical:SETUP-00#7c.10

- Source reference: docs/SETUP-00-CHECKLIST.md row 7c.10
- Description: Every completed Gate produces a retrospective.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0053 - canonical:SETUP-00#7d.1

- Source reference: docs/SETUP-00-CHECKLIST.md row 7d.1
- Description: One promotion invariant governs every positive terminal status, not only `READY_FOR_REVIEW`.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0054 - canonical:SETUP-00#7d.2

- Source reference: docs/SETUP-00-CHECKLIST.md row 7d.2
- Description: The mandatory quality gate set is a closed machine-readable registry that an invocation cannot narrow.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0055 - canonical:SETUP-00#7d.3

- Source reference: docs/SETUP-00-CHECKLIST.md row 7d.3
- Description: The expected requirement set is derived from canonical sources and compared exactly with the declared set.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0056 - canonical:SETUP-00#7d.4

- Source reference: docs/SETUP-00-CHECKLIST.md row 7d.4
- Description: An external milestone PASS is derived from an audit attestation authored by another sealed checkpoint.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0057 - canonical:SETUP-00#7d.5

- Source reference: docs/SETUP-00-CHECKLIST.md row 7d.5
- Description: A derived artifact carries a fingerprint of its inputs, and staleness is decided by recomputation.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0058 - canonical:SETUP-00#7d.6

- Source reference: docs/SETUP-00-CHECKLIST.md row 7d.6
- Description: Every lesson control, evidence path and provenance locator is resolved against the repository.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0059 - canonical:SETUP-00#7d.7

- Source reference: docs/SETUP-00-CHECKLIST.md row 7d.7
- Description: Every `GUARDED` lesson names a registered guardrail, and guardrail effectiveness is measured.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0060 - canonical:SETUP-00#7d.8

- Source reference: docs/SETUP-00-CHECKLIST.md row 7d.8
- Description: Sealed checkpoints are anchored by a hash-linked chain over tag, commit and tree.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0061 - canonical:SETUP-00#7d.9

- Source reference: docs/SETUP-00-CHECKLIST.md row 7d.9
- Description: Every count used as evidence is derived once and verified wherever a report states it.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0062 - canonical:SETUP-00#7d.10

- Source reference: docs/SETUP-00-CHECKLIST.md row 7d.10
- Description: Sealing is monotonic and post-commit, and every recorded command binds its declared inputs by content.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0063 - canonical:SETUP-00#7d.11

- Source reference: docs/SETUP-00-CHECKLIST.md row 7d.11
- Description: A milestone delivery carries an internal Red Team and an internal mirror audit, and neither is recorded as external validation.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0064 - canonical:SETUP-00#7d.12

- Source reference: docs/SETUP-00-CHECKLIST.md row 7d.12
- Description: Every finding of an independent audit is closed before the corrective delivery is offered.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0065 - canonical:SETUP-00#7d.13

- Source reference: docs/SETUP-00-CHECKLIST.md row 7d.13
- Description: A milestone verdict is carried by the audit checkpoint about a sealed subject, and its positive path is executed rather than only its refusals.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0066 - canonical:SETUP-00#7d.14

- Source reference: docs/SETUP-00-CHECKLIST.md row 7d.14
- Description: A generic guardrail derives repository state instead of naming a historical checkpoint, and the protocol's own next steps keep every mandatory gate green.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0067 - canonical:SETUP-00#7d.15

- Source reference: docs/SETUP-00-CHECKLIST.md row 7d.15
- Description: Every adversarial battery records a null-mutation control, and no count used as evidence is stated in prose.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0068 - canonical:SETUP-00#8.1

- Source reference: docs/SETUP-00-CHECKLIST.md row 8.1
- Description: An independent review is recorded.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0069 - canonical:SETUP-00#8.2

- Source reference: docs/SETUP-00-CHECKLIST.md row 8.2
- Description: An adversarial Red Team is recorded.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0070 - canonical:SETUP-00#8.3

- Source reference: docs/SETUP-00-CHECKLIST.md row 8.3
- Description: `GATE_PASS` is granted only by a run independent of the implementer.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0071 - canonical:SETUP-00#9.1

- Source reference: docs/SETUP-00-CHECKLIST.md row 9.1
- Description: No Gate 0 or later runtime is implemented during SETUP-00.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0072 - canonical:SETUP-00#9.2

- Source reference: docs/SETUP-00-CHECKLIST.md row 9.2
- Description: Documentation is maintained continuously rather than reconstructed at the end.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0073 - canonical:SETUP-00#9.3

- Source reference: docs/SETUP-00-CHECKLIST.md row 9.3
- Description: No secret, credential, or private chain-of-thought is stored.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0074 - canonical:SETUP-00#9.4

- Source reference: docs/SETUP-00-CHECKLIST.md row 9.4
- Description: Gate advancement requires explicit authorization and a passing previous Gate.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0075 - finding:CP9-F-001

- Source reference: M0-CP-0009 docs/checkpoints/SETUP-00-CP-0009/REVIEW-REPORT.md CP9-F-001
- Description: the external audit attestation can be written but never consumed, so `MILESTONE_EXTERNAL_PASS` is unreachable
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0076 - finding:CP9-F-002

- Source reference: M0-CP-0009 docs/checkpoints/SETUP-00-CP-0009/REVIEW-REPORT.md CP9-F-002
- Description: a guardrail test is bound to a literal checkpoint name, so performing the protocol's own next step turns the mandatory `tests` gate red
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0077 - finding:CP9-F-003

- Source reference: M0-CP-0009 docs/checkpoints/SETUP-00-CP-0009/REVIEW-REPORT.md CP9-F-003
- Description: a stale count survives in a current artifact because the count guardrail only inspects Markdown
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0078 - finding:CP9-F-004

- Source reference: M0-CP-0009 docs/checkpoints/SETUP-00-CP-0009/REVIEW-REPORT.md CP9-F-004
- Description: a lesson's own note contradicts its status
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0079 - finding:CP9-F-005

- Source reference: M0-CP-0009 docs/checkpoints/SETUP-00-CP-0009/REVIEW-REPORT.md CP9-F-005
- Description: a policy key is declared and never read
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0080 - attack:A

- Source reference: M0-CP-0009 docs/checkpoints/SETUP-00-CP-0009/RED-TEAM-REPORT.md attack A
- Description: Defend attack A: Add a blocker to a READY_FOR_REVIEW checkpoint
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0081 - attack:B

- Source reference: M0-CP-0009 docs/checkpoints/SETUP-00-CP-0009/RED-TEAM-REPORT.md attack B
- Description: Defend attack B: Set a review-ready quality dimension red
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0082 - attack:C

- Source reference: M0-CP-0009 docs/checkpoints/SETUP-00-CP-0009/RED-TEAM-REPORT.md attack C
- Description: Defend attack C: Delete a canonical requirement and recompute every count
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0083 - attack:D

- Source reference: M0-CP-0009 docs/checkpoints/SETUP-00-CP-0009/RED-TEAM-REPORT.md attack D
- Description: Defend attack D: Forge the stored counts of a passing report
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0084 - attack:E

- Source reference: M0-CP-0009 docs/checkpoints/SETUP-00-CP-0009/RED-TEAM-REPORT.md attack E
- Description: Defend attack E: Remove a lesson-derived requirement from the matrix
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0085 - attack:F

- Source reference: M0-CP-0009 docs/checkpoints/SETUP-00-CP-0009/RED-TEAM-REPORT.md attack F
- Description: Defend attack F: Replace a preventive control with documentation only
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0086 - attack:G

- Source reference: M0-CP-0009 docs/checkpoints/SETUP-00-CP-0009/RED-TEAM-REPORT.md attack G
- Description: Defend attack G: Duplicate a lesson identifier
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0087 - attack:H

- Source reference: M0-CP-0009 docs/checkpoints/SETUP-00-CP-0009/RED-TEAM-REPORT.md attack H
- Description: Defend attack H: Insert a secret-shaped value into a scanned field
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0088 - attack:I

- Source reference: M0-CP-0009 docs/checkpoints/SETUP-00-CP-0009/RED-TEAM-REPORT.md attack I
- Description: Defend attack I: Rewrite a sealed predecessor, refresh hashes and move its tag
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0089 - attack:J

- Source reference: M0-CP-0009 docs/checkpoints/SETUP-00-CP-0009/RED-TEAM-REPORT.md attack J
- Description: Defend attack J: Move a checkpoint tag and HEAD together
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0090 - attack:K

- Source reference: M0-CP-0009 docs/checkpoints/SETUP-00-CP-0009/RED-TEAM-REPORT.md attack K
- Description: Defend attack K: Remove one inventory entry
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0091 - attack:L

- Source reference: M0-CP-0009 docs/checkpoints/SETUP-00-CP-0009/RED-TEAM-REPORT.md attack L
- Description: Defend attack L: Silently modify a tracked file
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0092 - attack:M

- Source reference: M0-CP-0009 docs/checkpoints/SETUP-00-CP-0009/RED-TEAM-REPORT.md attack M
- Description: Defend attack M: Set a wrong hashBefore
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0093 - attack:N

- Source reference: M0-CP-0009 docs/checkpoints/SETUP-00-CP-0009/RED-TEAM-REPORT.md attack N
- Description: Defend attack N: Set a wrong hashAfter
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0094 - attack:O

- Source reference: M0-CP-0009 docs/checkpoints/SETUP-00-CP-0009/RED-TEAM-REPORT.md attack O
- Description: Defend attack O: Claim PASS with no evidence
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0095 - attack:P

- Source reference: M0-CP-0009 docs/checkpoints/SETUP-00-CP-0009/RED-TEAM-REPORT.md attack P
- Description: Defend attack P: Reference an unknown command
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0096 - attack:Q

- Source reference: M0-CP-0009 docs/checkpoints/SETUP-00-CP-0009/RED-TEAM-REPORT.md attack Q
- Description: Defend attack Q: Supply complete attribution with empty evidence
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0097 - attack:R

- Source reference: M0-CP-0009 docs/checkpoints/SETUP-00-CP-0009/RED-TEAM-REPORT.md attack R
- Description: Defend attack R: Promote an internally authored result to an external status
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0098 - attack:S

- Source reference: M0-CP-0009 docs/checkpoints/SETUP-00-CP-0009/RED-TEAM-REPORT.md attack S
- Description: Defend attack S: Leave review and Red Team pending with a null auditor
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0099 - attack:T

- Source reference: M0-CP-0009 docs/checkpoints/SETUP-00-CP-0009/RED-TEAM-REPORT.md attack T
- Description: Defend attack T: Request an audit without a known trigger
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0100 - attack:U

- Source reference: M0-CP-0009 docs/checkpoints/SETUP-00-CP-0009/RED-TEAM-REPORT.md attack U
- Description: Defend attack U: Retire a canonical lesson but keep the active preflight
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0101 - attack:V

- Source reference: M0-CP-0009 docs/checkpoints/SETUP-00-CP-0009/RED-TEAM-REPORT.md attack V
- Description: Defend attack V: Run the Green Keeper with an empty gate selection
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0102 - attack:W

- Source reference: M0-CP-0009 docs/checkpoints/SETUP-00-CP-0009/RED-TEAM-REPORT.md attack W
- Description: Defend attack W: Claim PASS with a PARTIAL requirement
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0103 - attack:X

- Source reference: M0-CP-0009 docs/checkpoints/SETUP-00-CP-0009/RED-TEAM-REPORT.md attack X
- Description: Defend attack X: Remove a required field from a command record
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0104 - attack:Y

- Source reference: M0-CP-0009 docs/checkpoints/SETUP-00-CP-0009/RED-TEAM-REPORT.md attack Y
- Description: Defend attack Y: Point LATEST.md at an older checkpoint
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0105 - attack:Z

- Source reference: M0-CP-0009 docs/checkpoints/SETUP-00-CP-0009/RED-TEAM-REPORT.md attack Z
- Description: Defend attack Z: Use path traversal as the Gate identifier
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0001 - lesson:LSN-0001

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0001
- Description: Verify checkpoint validation must succeed from a detached checkout of the checkpoint tag
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0002 - lesson:LSN-0002

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0002
- Description: Verify a file inventory must be recomputed from the repository, never trusted as an assertion
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0003 - lesson:LSN-0003

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0003
- Description: Verify every operation attempt must be auditable, including a refusal decided before execution
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0004 - lesson:LSN-0004

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0004
- Description: Verify a checkpoint may never claim readiness while it also claims to be blocked
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0005 - lesson:LSN-0005

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0005
- Description: Verify a PASS requires evidence that can be executed or resolved, not a statement
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0006 - lesson:LSN-0006

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0006
- Description: Verify the repository must be self-contained; a specification may not live outside it
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0007 - lesson:LSN-0007

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0007
- Description: Verify independent validation cannot be declared by the run that did the work
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0008 - lesson:LSN-0008

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0008
- Description: Verify requirement completeness must be total and evidence-backed before handoff
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0009 - lesson:LSN-0009

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0009
- Description: Verify a red gate requires rework, never a waiver, and never a weakened check
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0010 - lesson:LSN-0010

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0010
- Description: Verify a recorded command must carry runtime, working directory, commit and purpose to be replayable
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0011 - lesson:LSN-0011

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0011
- Description: Verify a control over a checkpoint's own evidence must be scoped to the moment it matters
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0012 - lesson:LSN-0012

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0012
- Description: Verify sealed checkpoints and their tags are immutable, and tooling must keep validating them
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0013 - lesson:LSN-0013

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0013
- Description: Verify an installed capability must be detected by resolved path, not by a bare command lookup
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0014 - lesson:LSN-0014

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0014
- Description: Verify evidence must be recorded as it happens, not reconstructed at the end of a run
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0015 - lesson:LSN-0015

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0015
- Description: Verify every positive terminal status needs one shared promotion invariant
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0016 - lesson:LSN-0016

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0016
- Description: Verify a mandatory set must be closed by policy, never chosen by the caller
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0017 - lesson:LSN-0017

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0017
- Description: Verify a completeness denominator must come from a source the delivery does not own
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0018 - lesson:LSN-0018

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0018
- Description: Verify a structured reference must be resolved, not merely well typed
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0019 - lesson:LSN-0019

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0019
- Description: Verify a derived artifact must carry a fingerprint of the inputs that produced it
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0020 - lesson:LSN-0020

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0020
- Description: Verify evidence produced from a dirty tree needs immutable input identity
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0021 - lesson:LSN-0021

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0021
- Description: Verify sealed history needs an anchor outside the content it describes
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0022 - lesson:LSN-0022

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0022
- Description: Verify an authoritative count must be derived once, never maintained by hand twice
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0023 - lesson:LSN-0023

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0023
- Description: Verify a lesson must cite a source that actually records the finding it claims
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0024 - lesson:LSN-0024

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0024
- Description: Verify a control is finished only when its positive path has been executed, not only its refusals
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0025 - lesson:LSN-0025

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0025
- Description: Verify a generic guardrail derives repository state instead of naming today's checkpoint
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0026 - lesson:LSN-0026

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0026
- Description: Verify an adversarial battery without a null-mutation control proves nothing
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0027 - lesson:LSN-0027

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0027
- Description: Verify a lesson's prose may record a residual limit but may never contradict its status
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0028 - lesson:LSN-0028

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0028
- Description: Verify a configuration key that no code reads is a defect, not documentation
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0029 - lesson:LSN-0029

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0029
- Description: Verify a required protocol transition must never turn a mandatory gate red
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_
