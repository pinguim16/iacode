# Requirements Matrix

Gate: `SETUP-00` — Checkpoint: `SETUP-00-CP-0011`

Expected set source: policies.expected_requirement_refs over docs/SETUP-00-CHECKLIST.md, .iacode/policies/canonical-requirements.json, .iacode/policies/audit-registry.json and LESSON-PREFLIGHT.json

| Requirement | Source | Mandatory | Status | Description |
|---|---|---|---|---|
| `REQ-0001` | `canonical:SETUP-00#1.1` | yes | `COMPLETE` | A single entry point states the phase, current Gate, latest checkpoint, and start protocol. |
| `REQ-0002` | `canonical:SETUP-00#1.2` | yes | `COMPLETE` | A Codex adapter binds the canonical contracts without adding independent policy. |
| `REQ-0003` | `canonical:SETUP-00#1.3` | yes | `COMPLETE` | A Claude Code adapter binds the same contracts. |
| `REQ-0004` | `canonical:SETUP-00#1.4` | yes | `COMPLETE` | Tool adapters stay semantically equivalent to the canonical roles. |
| `REQ-0005` | `canonical:SETUP-00#2.1` | yes | `COMPLETE` | The Gate sequence, dependencies, acceptance, and fail conditions are recorded. |
| `REQ-0006` | `canonical:SETUP-00#2.2` | yes | `COMPLETE` | The completion standard, mandatory controls, and Git and evidence discipline are recorded. |
| `REQ-0007` | `canonical:SETUP-00#2.3` | yes | `COMPLETE` | Tool-to-tool transfer is formal in both directions. |
| `REQ-0008` | `canonical:SETUP-00#2.4` | yes | `COMPLETE` | Checkpoint statuses, required events, required contents, commit semantics, and divergence handling are defined. |
| `REQ-0009` | `canonical:SETUP-00#2.5` | yes | `COMPLETE` | Done is defined and excludes assertion-only PASS. |
| `REQ-0010` | `canonical:SETUP-00#2.6` | yes | `COMPLETE` | Quality outcomes, required dimensions, and the promotion rule are defined. |
| `REQ-0011` | `canonical:SETUP-00#2.7` | yes | `COMPLETE` | Structural decisions are recorded as ADRs. |
| `REQ-0012` | `canonical:SETUP-00#2.8` | yes | `COMPLETE` | Architecture, roadmap, provenance, model usage, and detected tool capabilities are documented. |
| `REQ-0013` | `canonical:SETUP-00#3.1` | yes | `COMPLETE` | The canonical, tool-neutral role contracts exist, one per role of the delivery protocol. |
| `REQ-0014` | `canonical:SETUP-00#3.2` | yes | `COMPLETE` | Documentation, provenance, secret, tool-execution, and training-data policies exist. |
| `REQ-0015` | `canonical:SETUP-00#3.3` | yes | `COMPLETE` | Reusable templates exist for ADRs, checkpoints, gate reports, and handoffs. |
| `REQ-0016` | `canonical:SETUP-00#4.1` | yes | `COMPLETE` | Checkpoint state, run metadata, command, test, quality, provenance, and decision schemas exist and are loadable. |
| `REQ-0017` | `canonical:SETUP-00#4.2` | yes | `COMPLETE` | An experience schema is reserved for Gate 6 and implements no runtime. |
| `REQ-0018` | `canonical:SETUP-00#4.3` | yes | `COMPLETE` | Schema evolution is versioned and never invalidates a sealed checkpoint. |
| `REQ-0019` | `canonical:SETUP-00#5.1` | yes | `COMPLETE` | A checkpoint can be created with truthful non-PASS defaults. |
| `REQ-0020` | `canonical:SETUP-00#5.2` | yes | `COMPLETE` | A checkpoint can be finalized, and every finalization attempt is recorded with its exit code. |
| `REQ-0021` | `canonical:SETUP-00#5.3` | yes | `COMPLETE` | A checkpoint is validated against schemas, Git state, inventory, quality evidence, and secrets. |
| `REQ-0022` | `canonical:SETUP-00#5.4` | yes | `COMPLETE` | Secret redaction is available and documented to its real scope. |
| `REQ-0023` | `canonical:SETUP-00#5.5` | yes | `COMPLETE` | The tooling is standard-library only and portable across Windows and Unix-like checkouts. |
| `REQ-0024` | `canonical:SETUP-00#6.1` | yes | `COMPLETE` | Every checkpoint carries status, handoff, run metadata, state, plan, decisions, commands, file inventory, tests, quality, provenance, diff summary, risks, and next action. |
| `REQ-0025` | `canonical:SETUP-00#6.2` | yes | `COMPLETE` | `LATEST.md` points textually to the last checkpoint accepted by validation. |
| `REQ-0026` | `canonical:SETUP-00#6.3` | yes | `COMPLETE` | The file inventory matches the real change set, with bound content hashes. |
| `REQ-0027` | `canonical:SETUP-00#6.4` | yes | `COMPLETE` | Provenance is complete and `trainingAllowed` defaults to `false`. |
| `REQ-0028` | `canonical:SETUP-00#6.5` | yes | `COMPLETE` | A quality `PASS` carries resolvable evidence. |
| `REQ-0029` | `canonical:SETUP-00#6.6` | yes | `COMPLETE` | Handoff-ready and terminal checkpoints are anchored to an immutable namespaced tag. |
| `REQ-0030` | `canonical:SETUP-00#7.1` | yes | `COMPLETE` | A cold-start continuation prompt exists and depends only on checked-in files. |
| `REQ-0031` | `canonical:SETUP-00#7.2` | yes | `COMPLETE` | Cold-start validation is executed and recorded truthfully, including a blocked attempt. |
| `REQ-0032` | `canonical:SETUP-00#7.3` | yes | `COMPLETE` | Cross-tool validation state is structured and explicit. |
| `REQ-0033` | `canonical:SETUP-00#7.4` | yes | `COMPLETE` | A sealed checkpoint can be validated from a detached checkout of its own tag. |
| `REQ-0034` | `canonical:SETUP-00#7.5` | yes | `COMPLETE` | The handoff is executable by another tool without the producing session. |
| `REQ-0035` | `canonical:SETUP-00#7b.1` | yes | `COMPLETE` | Every requirement of a delivery exists in a versioned matrix before implementation. |
| `REQ-0036` | `canonical:SETUP-00#7b.2` | yes | `COMPLETE` | A Test Rework / Green Keeper role forbids shipping anything red and records every cycle. |
| `REQ-0037` | `canonical:SETUP-00#7b.3` | yes | `COMPLETE` | A Delivery Completeness Validator audits the matrix before handoff and may not implement. |
| `REQ-0038` | `canonical:SETUP-00#7b.4` | yes | `COMPLETE` | `GREEN_KEEPER_GATE` and `DELIVERY_COMPLETENESS_GATE` are preconditions of `READY_FOR_REVIEW`. |
| `REQ-0039` | `canonical:SETUP-00#7b.5` | yes | `COMPLETE` | Readiness and blockage can never be claimed together. |
| `REQ-0040` | `canonical:SETUP-00#7b.6` | yes | `COMPLETE` | Every operation attempt is recorded, including a refusal decided before execution. |
| `REQ-0041` | `canonical:SETUP-00#7b.7` | yes | `COMPLETE` | Every recorded command is reproducible from its declared working directory. |
| `REQ-0042` | `canonical:SETUP-00#7b.8` | yes | `COMPLETE` | The mandatory delivery order is stated in full in every governing document and both adapters. |
| `REQ-0043` | `canonical:SETUP-00#7c.1` | yes | `COMPLETE` | The project keeps an organizational engineering memory of confirmed failures. |
| `REQ-0044` | `canonical:SETUP-00#7c.2` | yes | `COMPLETE` | A lesson is `GUARDED` only when an automated control prevents recurrence. |
| `REQ-0045` | `canonical:SETUP-00#7c.3` | yes | `COMPLETE` | A repeat increments recurrence, and a repeat against a guardrail is a `GUARDRAIL_FAILURE`. |
| `REQ-0046` | `canonical:SETUP-00#7c.4` | yes | `COMPLETE` | A mandatory preflight selects the lessons that constrain each Gate. |
| `REQ-0047` | `canonical:SETUP-00#7c.5` | yes | `COMPLETE` | Applicable lessons become requirements whose absence blocks completeness. |
| `REQ-0048` | `canonical:SETUP-00#7c.6` | yes | `COMPLETE` | Lesson candidates can be extracted from recorded delivery evidence, never above `OBSERVED`. |
| `REQ-0049` | `canonical:SETUP-00#7c.7` | yes | `COMPLETE` | External validation is grouped into milestones `M0` to `M6`. |
| `REQ-0050` | `canonical:SETUP-00#7c.8` | yes | `COMPLETE` | An internal verdict is never described as independent external validation. |
| `REQ-0051` | `canonical:SETUP-00#7c.9` | yes | `COMPLETE` | An extraordinary audit requires a recorded trigger. |
| `REQ-0052` | `canonical:SETUP-00#7c.10` | yes | `COMPLETE` | Every completed Gate produces a retrospective. |
| `REQ-0053` | `canonical:SETUP-00#7d.1` | yes | `COMPLETE` | One promotion invariant governs every positive terminal status, not only `READY_FOR_REVIEW`. |
| `REQ-0054` | `canonical:SETUP-00#7d.2` | yes | `COMPLETE` | The mandatory quality gate set is a closed machine-readable registry that an invocation cannot narrow. |
| `REQ-0055` | `canonical:SETUP-00#7d.3` | yes | `COMPLETE` | The expected requirement set is derived from canonical sources and compared exactly with the declared set. |
| `REQ-0056` | `canonical:SETUP-00#7d.4` | yes | `COMPLETE` | An external milestone PASS is derived from an audit attestation authored by another sealed checkpoint. |
| `REQ-0057` | `canonical:SETUP-00#7d.5` | yes | `COMPLETE` | A derived artifact carries a fingerprint of its inputs, and staleness is decided by recomputation. |
| `REQ-0058` | `canonical:SETUP-00#7d.6` | yes | `COMPLETE` | Every lesson control, evidence path and provenance locator is resolved against the repository. |
| `REQ-0059` | `canonical:SETUP-00#7d.7` | yes | `COMPLETE` | Every `GUARDED` lesson names a registered guardrail, and guardrail effectiveness is measured. |
| `REQ-0060` | `canonical:SETUP-00#7d.8` | yes | `COMPLETE` | Sealed checkpoints are anchored by a hash-linked chain over tag, commit and tree. |
| `REQ-0061` | `canonical:SETUP-00#7d.9` | yes | `COMPLETE` | Every count used as evidence is derived once and verified wherever a report states it. |
| `REQ-0062` | `canonical:SETUP-00#7d.10` | yes | `COMPLETE` | Sealing is monotonic and post-commit, and every recorded command binds its declared inputs by content. |
| `REQ-0063` | `canonical:SETUP-00#7d.11` | yes | `COMPLETE` | A milestone delivery carries an internal Red Team and an internal mirror audit, and neither is recorded as external validation. |
| `REQ-0064` | `canonical:SETUP-00#7d.12` | yes | `COMPLETE` | Every finding of an independent audit is closed before the corrective delivery is offered. |
| `REQ-0065` | `canonical:SETUP-00#7d.13` | yes | `COMPLETE` | A milestone verdict is carried by the audit checkpoint about a sealed subject, and its positive path is executed rather than only its refusals. |
| `REQ-0066` | `canonical:SETUP-00#7d.14` | yes | `COMPLETE` | A generic guardrail derives repository state instead of naming a historical checkpoint, and the protocol's own next steps keep every mandatory gate green. |
| `REQ-0067` | `canonical:SETUP-00#7d.15` | yes | `COMPLETE` | Every adversarial battery records a null-mutation control, and no count used as evidence is stated in prose. |
| `REQ-0068` | `canonical:SETUP-00#8.1` | yes | `COMPLETE` | An independent review is recorded. |
| `REQ-0069` | `canonical:SETUP-00#8.2` | yes | `COMPLETE` | An adversarial Red Team is recorded. |
| `REQ-0070` | `canonical:SETUP-00#8.3` | yes | `COMPLETE` | `GATE_PASS` is granted only by a run independent of the implementer. |
| `REQ-0071` | `canonical:SETUP-00#9.1` | yes | `COMPLETE` | No Gate 0 or later runtime is implemented during SETUP-00. |
| `REQ-0072` | `canonical:SETUP-00#9.2` | yes | `COMPLETE` | Documentation is maintained continuously rather than reconstructed at the end. |
| `REQ-0073` | `canonical:SETUP-00#9.3` | yes | `COMPLETE` | No secret, credential, or private chain-of-thought is stored. |
| `REQ-0074` | `canonical:SETUP-00#9.4` | yes | `COMPLETE` | Gate advancement requires explicit authorization and a passing previous Gate. |
| `LESSON-REQ-0001` | `lesson:LSN-0001` | yes | `COMPLETE` | Verify checkpoint validation must succeed from a detached checkout of the checkpoint tag |
| `LESSON-REQ-0002` | `lesson:LSN-0002` | yes | `COMPLETE` | Verify a file inventory must be recomputed from the repository, never trusted as an assertion |
| `LESSON-REQ-0003` | `lesson:LSN-0003` | yes | `COMPLETE` | Verify every operation attempt must be auditable, including a refusal decided before execution |
| `LESSON-REQ-0004` | `lesson:LSN-0004` | yes | `COMPLETE` | Verify a checkpoint may never claim readiness while it also claims to be blocked |
| `LESSON-REQ-0005` | `lesson:LSN-0005` | yes | `COMPLETE` | Verify a PASS requires evidence that can be executed or resolved, not a statement |
| `LESSON-REQ-0006` | `lesson:LSN-0006` | yes | `COMPLETE` | Verify the repository must be self-contained; a specification may not live outside it |
| `LESSON-REQ-0007` | `lesson:LSN-0007` | yes | `COMPLETE` | Verify independent validation cannot be declared by the run that did the work |
| `LESSON-REQ-0008` | `lesson:LSN-0008` | yes | `COMPLETE` | Verify requirement completeness must be total and evidence-backed before handoff |
| `LESSON-REQ-0009` | `lesson:LSN-0009` | yes | `COMPLETE` | Verify a red gate requires rework, never a waiver, and never a weakened check |
| `LESSON-REQ-0010` | `lesson:LSN-0010` | yes | `COMPLETE` | Verify a recorded command must carry runtime, working directory, commit and purpose to be replayable |
| `LESSON-REQ-0011` | `lesson:LSN-0011` | yes | `COMPLETE` | Verify a control over a checkpoint's own evidence must be scoped to the moment it matters |
| `LESSON-REQ-0012` | `lesson:LSN-0012` | yes | `COMPLETE` | Verify sealed checkpoints and their tags are immutable, and tooling must keep validating them |
| `LESSON-REQ-0013` | `lesson:LSN-0013` | no | `COMPLETE` | Verify an installed capability must be detected by resolved path, not by a bare command lookup |
| `LESSON-REQ-0014` | `lesson:LSN-0014` | yes | `COMPLETE` | Verify evidence must be recorded as it happens, not reconstructed at the end of a run |
| `LESSON-REQ-0015` | `lesson:LSN-0015` | yes | `COMPLETE` | Verify every positive terminal status needs one shared promotion invariant |
| `LESSON-REQ-0016` | `lesson:LSN-0016` | yes | `COMPLETE` | Verify a mandatory set must be closed by policy, never chosen by the caller |
| `LESSON-REQ-0017` | `lesson:LSN-0017` | yes | `COMPLETE` | Verify a completeness denominator must come from a source the delivery does not own |
| `LESSON-REQ-0018` | `lesson:LSN-0018` | yes | `COMPLETE` | Verify a structured reference must be resolved, not merely well typed |
| `LESSON-REQ-0019` | `lesson:LSN-0019` | yes | `COMPLETE` | Verify a derived artifact must carry a fingerprint of the inputs that produced it |
| `LESSON-REQ-0020` | `lesson:LSN-0020` | yes | `COMPLETE` | Verify evidence produced from a dirty tree needs immutable input identity |
| `LESSON-REQ-0021` | `lesson:LSN-0021` | yes | `COMPLETE` | Verify sealed history needs an anchor outside the content it describes |
| `LESSON-REQ-0022` | `lesson:LSN-0022` | yes | `COMPLETE` | Verify an authoritative count must be derived once, never maintained by hand twice |
| `LESSON-REQ-0023` | `lesson:LSN-0023` | yes | `COMPLETE` | Verify a lesson must cite a source that actually records the finding it claims |
| `LESSON-REQ-0024` | `lesson:LSN-0024` | yes | `COMPLETE` | Verify a control is finished only when its positive path has been executed, not only its refusals |
| `LESSON-REQ-0025` | `lesson:LSN-0025` | yes | `COMPLETE` | Verify a generic guardrail derives repository state instead of naming today's checkpoint |
| `LESSON-REQ-0026` | `lesson:LSN-0026` | yes | `COMPLETE` | Verify an adversarial battery without a null-mutation control proves nothing |
| `LESSON-REQ-0027` | `lesson:LSN-0027` | yes | `COMPLETE` | Verify a lesson's prose may record a residual limit but may never contradict its status |
| `LESSON-REQ-0028` | `lesson:LSN-0028` | yes | `COMPLETE` | Verify a configuration key that no code reads is a defect, not documentation |
| `LESSON-REQ-0029` | `lesson:LSN-0029` | yes | `COMPLETE` | Verify a required protocol transition must never turn a mandatory gate red |
| `LESSON-REQ-0030` | `lesson:LSN-0030` | no | `COMPLETE` | Verify the lesson preflight presumes an implementing delivery and constrains an audit run badly |
