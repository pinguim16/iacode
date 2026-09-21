# Closure Requirements - SETUP-00-CP-0013

Derived from the canonical sources listed below, before implementation. The expected set
is recomputed by `policies.expected_requirement_refs` and compared exactly with the
declared set, so a requirement cannot be dropped and the denominator cannot be reduced.

## Sources

- SOURCE A: docs/SETUP-00-CHECKLIST.md, the canonical SETUP-00 specification
- SOURCE B: docs/MILESTONE-VALIDATION.md, the milestone requirements of the audit
- SOURCE C: LESSON-PREFLIGHT.json, the lessons the engineering memory imposes

## Requirements

| ID | Source | Anchor | Mandatory | Implementation | Final | Description |
|---|---|---|---|---|---|---|
| `REQ-0001` | SETUP | `canonical:SETUP-00#1.1` | yes | `COMPLETE` | `COMPLETE` | A single entry point states the phase, current Gate, latest checkpoint, and start protocol. |
| `REQ-0002` | SETUP | `canonical:SETUP-00#1.2` | yes | `COMPLETE` | `COMPLETE` | A Codex adapter binds the canonical contracts without adding independent policy. |
| `REQ-0003` | SETUP | `canonical:SETUP-00#1.3` | yes | `COMPLETE` | `COMPLETE` | A Claude Code adapter binds the same contracts. |
| `REQ-0004` | SETUP | `canonical:SETUP-00#1.4` | yes | `COMPLETE` | `COMPLETE` | Tool adapters stay semantically equivalent to the canonical roles. |
| `REQ-0005` | SETUP | `canonical:SETUP-00#2.1` | yes | `COMPLETE` | `COMPLETE` | The Gate sequence, dependencies, acceptance, and fail conditions are recorded. |
| `REQ-0006` | SETUP | `canonical:SETUP-00#2.2` | yes | `COMPLETE` | `COMPLETE` | The completion standard, mandatory controls, and Git and evidence discipline are recorded. |
| `REQ-0007` | SETUP | `canonical:SETUP-00#2.3` | yes | `COMPLETE` | `COMPLETE` | Tool-to-tool transfer is formal in both directions. |
| `REQ-0008` | SETUP | `canonical:SETUP-00#2.4` | yes | `COMPLETE` | `COMPLETE` | Checkpoint statuses, required events, required contents, commit semantics, and divergence handling are defined. |
| `REQ-0009` | SETUP | `canonical:SETUP-00#2.5` | yes | `COMPLETE` | `COMPLETE` | Done is defined and excludes assertion-only PASS. |
| `REQ-0010` | SETUP | `canonical:SETUP-00#2.6` | yes | `COMPLETE` | `COMPLETE` | Quality outcomes, required dimensions, and the promotion rule are defined. |
| `REQ-0011` | SETUP | `canonical:SETUP-00#2.7` | yes | `COMPLETE` | `COMPLETE` | Structural decisions are recorded as ADRs. |
| `REQ-0012` | SETUP | `canonical:SETUP-00#2.8` | yes | `COMPLETE` | `COMPLETE` | Architecture, roadmap, provenance, model usage, and detected tool capabilities are documented. |
| `REQ-0013` | SETUP | `canonical:SETUP-00#3.1` | yes | `COMPLETE` | `COMPLETE` | The canonical, tool-neutral role contracts exist, one per role of the delivery protocol. |
| `REQ-0014` | SETUP | `canonical:SETUP-00#3.2` | yes | `COMPLETE` | `COMPLETE` | Documentation, provenance, secret, tool-execution, and training-data policies exist. |
| `REQ-0015` | SETUP | `canonical:SETUP-00#3.3` | yes | `COMPLETE` | `COMPLETE` | Reusable templates exist for ADRs, checkpoints, gate reports, and handoffs. |
| `REQ-0016` | SETUP | `canonical:SETUP-00#4.1` | yes | `COMPLETE` | `COMPLETE` | Checkpoint state, run metadata, command, test, quality, provenance, and decision schemas exist and are loadable. |
| `REQ-0017` | SETUP | `canonical:SETUP-00#4.2` | yes | `COMPLETE` | `COMPLETE` | An experience schema is reserved for Gate 6 and implements no runtime. |
| `REQ-0018` | SETUP | `canonical:SETUP-00#4.3` | yes | `COMPLETE` | `COMPLETE` | Schema evolution is versioned and never invalidates a sealed checkpoint. |
| `REQ-0019` | SETUP | `canonical:SETUP-00#5.1` | yes | `COMPLETE` | `COMPLETE` | A checkpoint can be created with truthful non-PASS defaults. |
| `REQ-0020` | SETUP | `canonical:SETUP-00#5.2` | yes | `COMPLETE` | `COMPLETE` | A checkpoint can be finalized, and every finalization attempt is recorded with its exit code. |
| `REQ-0021` | SETUP | `canonical:SETUP-00#5.3` | yes | `COMPLETE` | `COMPLETE` | A checkpoint is validated against schemas, Git state, inventory, quality evidence, and secrets. |
| `REQ-0022` | SETUP | `canonical:SETUP-00#5.4` | yes | `COMPLETE` | `COMPLETE` | Secret redaction is available and documented to its real scope. |
| `REQ-0023` | SETUP | `canonical:SETUP-00#5.5` | yes | `COMPLETE` | `COMPLETE` | The tooling is standard-library only and portable across Windows and Unix-like checkouts. |
| `REQ-0024` | SETUP | `canonical:SETUP-00#6.1` | yes | `COMPLETE` | `COMPLETE` | Every checkpoint carries status, handoff, run metadata, state, plan, decisions, commands, file inventory, tests, quality, provenance, diff summary, risks, and next action. |
| `REQ-0025` | SETUP | `canonical:SETUP-00#6.2` | yes | `COMPLETE` | `COMPLETE` | `LATEST.md` points textually to the last checkpoint accepted by validation. |
| `REQ-0026` | SETUP | `canonical:SETUP-00#6.3` | yes | `COMPLETE` | `COMPLETE` | The file inventory matches the real change set, with bound content hashes. |
| `REQ-0027` | SETUP | `canonical:SETUP-00#6.4` | yes | `COMPLETE` | `COMPLETE` | Provenance is complete and `trainingAllowed` defaults to `false`. |
| `REQ-0028` | SETUP | `canonical:SETUP-00#6.5` | yes | `COMPLETE` | `COMPLETE` | A quality `PASS` carries resolvable evidence. |
| `REQ-0029` | SETUP | `canonical:SETUP-00#6.6` | yes | `COMPLETE` | `COMPLETE` | Handoff-ready and terminal checkpoints are anchored to an immutable namespaced tag. |
| `REQ-0030` | SETUP | `canonical:SETUP-00#7.1` | yes | `COMPLETE` | `COMPLETE` | A cold-start continuation prompt exists and depends only on checked-in files. |
| `REQ-0031` | SETUP | `canonical:SETUP-00#7.2` | yes | `COMPLETE` | `COMPLETE` | Cold-start validation is executed and recorded truthfully, including a blocked attempt. |
| `REQ-0032` | SETUP | `canonical:SETUP-00#7.3` | yes | `COMPLETE` | `COMPLETE` | Cross-tool validation state is structured and explicit. |
| `REQ-0033` | SETUP | `canonical:SETUP-00#7.4` | yes | `COMPLETE` | `COMPLETE` | A sealed checkpoint can be validated from a detached checkout of its own tag. |
| `REQ-0034` | SETUP | `canonical:SETUP-00#7.5` | yes | `COMPLETE` | `COMPLETE` | The handoff is executable by another tool without the producing session. |
| `REQ-0035` | SETUP | `canonical:SETUP-00#7b.1` | yes | `COMPLETE` | `COMPLETE` | Every requirement of a delivery exists in a versioned matrix before implementation. |
| `REQ-0036` | SETUP | `canonical:SETUP-00#7b.2` | yes | `COMPLETE` | `COMPLETE` | A Test Rework / Green Keeper role forbids shipping anything red and records every cycle. |
| `REQ-0037` | SETUP | `canonical:SETUP-00#7b.3` | yes | `COMPLETE` | `COMPLETE` | A Delivery Completeness Validator audits the matrix before handoff and may not implement. |
| `REQ-0038` | SETUP | `canonical:SETUP-00#7b.4` | yes | `COMPLETE` | `COMPLETE` | `GREEN_KEEPER_GATE` and `DELIVERY_COMPLETENESS_GATE` are preconditions of `READY_FOR_REVIEW`. |
| `REQ-0039` | SETUP | `canonical:SETUP-00#7b.5` | yes | `COMPLETE` | `COMPLETE` | Readiness and blockage can never be claimed together. |
| `REQ-0040` | SETUP | `canonical:SETUP-00#7b.6` | yes | `COMPLETE` | `COMPLETE` | Every operation attempt is recorded, including a refusal decided before execution. |
| `REQ-0041` | SETUP | `canonical:SETUP-00#7b.7` | yes | `COMPLETE` | `COMPLETE` | Every recorded command is reproducible from its declared working directory. |
| `REQ-0042` | SETUP | `canonical:SETUP-00#7b.8` | yes | `COMPLETE` | `COMPLETE` | The mandatory delivery order is stated in full in every governing document and both adapters. |
| `REQ-0043` | SETUP | `canonical:SETUP-00#7c.1` | yes | `COMPLETE` | `COMPLETE` | The project keeps an organizational engineering memory of confirmed failures. |
| `REQ-0044` | SETUP | `canonical:SETUP-00#7c.2` | yes | `COMPLETE` | `COMPLETE` | A lesson is `GUARDED` only when an automated control prevents recurrence. |
| `REQ-0045` | SETUP | `canonical:SETUP-00#7c.3` | yes | `COMPLETE` | `COMPLETE` | A repeat increments recurrence, and a repeat against a guardrail is a `GUARDRAIL_FAILURE`. |
| `REQ-0046` | SETUP | `canonical:SETUP-00#7c.4` | yes | `COMPLETE` | `COMPLETE` | A mandatory preflight selects the lessons that constrain each Gate. |
| `REQ-0047` | SETUP | `canonical:SETUP-00#7c.5` | yes | `COMPLETE` | `COMPLETE` | Applicable lessons become requirements whose absence blocks completeness. |
| `REQ-0048` | SETUP | `canonical:SETUP-00#7c.6` | yes | `COMPLETE` | `COMPLETE` | Lesson candidates can be extracted from recorded delivery evidence, never above `OBSERVED`. |
| `REQ-0049` | SETUP | `canonical:SETUP-00#7c.7` | yes | `COMPLETE` | `COMPLETE` | External validation is grouped into milestones `M0` to `M6`. |
| `REQ-0050` | SETUP | `canonical:SETUP-00#7c.8` | yes | `COMPLETE` | `COMPLETE` | An internal verdict is never described as independent external validation. |
| `REQ-0051` | SETUP | `canonical:SETUP-00#7c.9` | yes | `COMPLETE` | `COMPLETE` | An extraordinary audit requires a recorded trigger. |
| `REQ-0052` | SETUP | `canonical:SETUP-00#7c.10` | yes | `COMPLETE` | `COMPLETE` | Every completed Gate produces a retrospective. |
| `REQ-0053` | SETUP | `canonical:SETUP-00#7d.1` | yes | `COMPLETE` | `COMPLETE` | One promotion invariant governs every positive terminal status, not only `READY_FOR_REVIEW`. |
| `REQ-0054` | SETUP | `canonical:SETUP-00#7d.2` | yes | `COMPLETE` | `COMPLETE` | The mandatory quality gate set is a closed machine-readable registry that an invocation cannot narrow. |
| `REQ-0055` | SETUP | `canonical:SETUP-00#7d.3` | yes | `COMPLETE` | `COMPLETE` | The expected requirement set is derived from canonical sources and compared exactly with the declared set. |
| `REQ-0056` | SETUP | `canonical:SETUP-00#7d.4` | yes | `COMPLETE` | `COMPLETE` | An external milestone PASS is derived from an audit attestation authored by another sealed checkpoint. |
| `REQ-0057` | SETUP | `canonical:SETUP-00#7d.5` | yes | `COMPLETE` | `COMPLETE` | A derived artifact carries a fingerprint of its inputs, and staleness is decided by recomputation. |
| `REQ-0058` | SETUP | `canonical:SETUP-00#7d.6` | yes | `COMPLETE` | `COMPLETE` | Every lesson control, evidence path and provenance locator is resolved against the repository. |
| `REQ-0059` | SETUP | `canonical:SETUP-00#7d.7` | yes | `COMPLETE` | `COMPLETE` | Every `GUARDED` lesson names a registered guardrail, and guardrail effectiveness is measured. |
| `REQ-0060` | SETUP | `canonical:SETUP-00#7d.8` | yes | `COMPLETE` | `COMPLETE` | Sealed checkpoints are anchored by a hash-linked chain over tag, commit and tree. |
| `REQ-0061` | SETUP | `canonical:SETUP-00#7d.9` | yes | `COMPLETE` | `COMPLETE` | Every count used as evidence is derived once and verified wherever a report states it. |
| `REQ-0062` | SETUP | `canonical:SETUP-00#7d.10` | yes | `COMPLETE` | `COMPLETE` | Sealing is monotonic and post-commit, and every recorded command binds its declared inputs by content. |
| `REQ-0063` | SETUP | `canonical:SETUP-00#7d.11` | yes | `COMPLETE` | `COMPLETE` | A milestone delivery carries an internal Red Team and an internal mirror audit, and neither is recorded as external validation. |
| `REQ-0064` | SETUP | `canonical:SETUP-00#7d.12` | yes | `COMPLETE` | `COMPLETE` | Every finding of an independent audit is closed before the corrective delivery is offered. |
| `REQ-0065` | SETUP | `canonical:SETUP-00#7d.13` | yes | `COMPLETE` | `COMPLETE` | A milestone verdict is carried by the audit checkpoint about a sealed subject, and its positive path is executed rather than only its refusals. |
| `REQ-0066` | SETUP | `canonical:SETUP-00#7d.14` | yes | `COMPLETE` | `COMPLETE` | A generic guardrail derives repository state instead of naming a historical checkpoint, and the protocol's own next steps keep every mandatory gate green. |
| `REQ-0067` | SETUP | `canonical:SETUP-00#7d.15` | yes | `COMPLETE` | `COMPLETE` | Every adversarial battery records a null-mutation control, and no count used as evidence is stated in prose. |
| `REQ-0068` | SETUP | `canonical:SETUP-00#7d.16` | yes | `COMPLETE` | `COMPLETE` | An audit control tells an empty applicable set from a missing required set, justifies every `NOT_APPLICABLE` against a canonical derivation no delivery can shrink, and a simulation that claims a control passed executes that control instead of writing its artifact. |
| `REQ-0069` | SETUP | `canonical:SETUP-00#8.1` | yes | `COMPLETE` | `COMPLETE` | An independent review is recorded. |
| `REQ-0070` | SETUP | `canonical:SETUP-00#8.2` | yes | `COMPLETE` | `COMPLETE` | An adversarial Red Team is recorded. |
| `REQ-0071` | SETUP | `canonical:SETUP-00#8.3` | yes | `COMPLETE` | `COMPLETE` | `GATE_PASS` is granted only by a run independent of the implementer. |
| `REQ-0072` | SETUP | `canonical:SETUP-00#9.1` | yes | `COMPLETE` | `COMPLETE` | No Gate 0 or later runtime is implemented during SETUP-00. |
| `REQ-0073` | SETUP | `canonical:SETUP-00#9.2` | yes | `COMPLETE` | `COMPLETE` | Documentation is maintained continuously rather than reconstructed at the end. |
| `REQ-0074` | SETUP | `canonical:SETUP-00#9.3` | yes | `COMPLETE` | `COMPLETE` | No secret, credential, or private chain-of-thought is stored. |
| `REQ-0075` | SETUP | `canonical:SETUP-00#9.4` | yes | `COMPLETE` | `COMPLETE` | Gate advancement requires explicit authorization and a passing previous Gate. |
| `LESSON-REQ-0001` | LESSON | `lesson:LSN-0001` | yes | `COMPLETE` | `COMPLETE` | Verify checkpoint validation must succeed from a detached checkout of the checkpoint tag |
| `LESSON-REQ-0002` | LESSON | `lesson:LSN-0002` | yes | `COMPLETE` | `COMPLETE` | Verify a file inventory must be recomputed from the repository, never trusted as an assertion |
| `LESSON-REQ-0003` | LESSON | `lesson:LSN-0003` | yes | `COMPLETE` | `COMPLETE` | Verify every operation attempt must be auditable, including a refusal decided before execution |
| `LESSON-REQ-0004` | LESSON | `lesson:LSN-0004` | yes | `COMPLETE` | `COMPLETE` | Verify a checkpoint may never claim readiness while it also claims to be blocked |
| `LESSON-REQ-0005` | LESSON | `lesson:LSN-0005` | yes | `COMPLETE` | `COMPLETE` | Verify a PASS requires evidence that can be executed or resolved, not a statement |
| `LESSON-REQ-0006` | LESSON | `lesson:LSN-0006` | yes | `COMPLETE` | `COMPLETE` | Verify the repository must be self-contained; a specification may not live outside it |
| `LESSON-REQ-0007` | LESSON | `lesson:LSN-0007` | yes | `COMPLETE` | `COMPLETE` | Verify independent validation cannot be declared by the run that did the work |
| `LESSON-REQ-0008` | LESSON | `lesson:LSN-0008` | yes | `COMPLETE` | `COMPLETE` | Verify requirement completeness must be total and evidence-backed before handoff |
| `LESSON-REQ-0009` | LESSON | `lesson:LSN-0009` | yes | `COMPLETE` | `COMPLETE` | Verify a red gate requires rework, never a waiver, and never a weakened check |
| `LESSON-REQ-0010` | LESSON | `lesson:LSN-0010` | yes | `COMPLETE` | `COMPLETE` | Verify a recorded command must carry runtime, working directory, commit and purpose to be replayable |
| `LESSON-REQ-0011` | LESSON | `lesson:LSN-0011` | yes | `COMPLETE` | `COMPLETE` | Verify a control over a checkpoint's own evidence must be scoped to the moment it matters |
| `LESSON-REQ-0012` | LESSON | `lesson:LSN-0012` | yes | `COMPLETE` | `COMPLETE` | Verify sealed checkpoints and their tags are immutable, and tooling must keep validating them |
| `LESSON-REQ-0013` | LESSON | `lesson:LSN-0013` | no | `COMPLETE` | `COMPLETE` | Verify an installed capability must be detected by resolved path, not by a bare command lookup |
| `LESSON-REQ-0014` | LESSON | `lesson:LSN-0014` | yes | `COMPLETE` | `COMPLETE` | Verify evidence must be recorded as it happens, not reconstructed at the end of a run |
| `LESSON-REQ-0015` | LESSON | `lesson:LSN-0015` | yes | `COMPLETE` | `COMPLETE` | Verify every positive terminal status needs one shared promotion invariant |
| `LESSON-REQ-0016` | LESSON | `lesson:LSN-0016` | yes | `COMPLETE` | `COMPLETE` | Verify a mandatory set must be closed by policy, never chosen by the caller |
| `LESSON-REQ-0017` | LESSON | `lesson:LSN-0017` | yes | `COMPLETE` | `COMPLETE` | Verify a completeness denominator must come from a source the delivery does not own |
| `LESSON-REQ-0018` | LESSON | `lesson:LSN-0018` | yes | `COMPLETE` | `COMPLETE` | Verify a structured reference must be resolved, not merely well typed |
| `LESSON-REQ-0019` | LESSON | `lesson:LSN-0019` | yes | `COMPLETE` | `COMPLETE` | Verify a derived artifact must carry a fingerprint of the inputs that produced it |
| `LESSON-REQ-0020` | LESSON | `lesson:LSN-0020` | yes | `COMPLETE` | `COMPLETE` | Verify evidence produced from a dirty tree needs immutable input identity |
| `LESSON-REQ-0021` | LESSON | `lesson:LSN-0021` | yes | `COMPLETE` | `COMPLETE` | Verify sealed history needs an anchor outside the content it describes |
| `LESSON-REQ-0022` | LESSON | `lesson:LSN-0022` | yes | `COMPLETE` | `COMPLETE` | Verify an authoritative count must be derived once, never maintained by hand twice |
| `LESSON-REQ-0023` | LESSON | `lesson:LSN-0023` | yes | `COMPLETE` | `COMPLETE` | Verify a lesson must cite a source that actually records the finding it claims |
| `LESSON-REQ-0024` | LESSON | `lesson:LSN-0024` | yes | `COMPLETE` | `COMPLETE` | Verify a control is finished only when its positive path has been executed, not only its refusals |
| `LESSON-REQ-0025` | LESSON | `lesson:LSN-0025` | yes | `COMPLETE` | `COMPLETE` | Verify a generic guardrail derives repository state instead of naming today's checkpoint |
| `LESSON-REQ-0026` | LESSON | `lesson:LSN-0026` | yes | `COMPLETE` | `COMPLETE` | Verify an adversarial battery without a null-mutation control proves nothing |
| `LESSON-REQ-0027` | LESSON | `lesson:LSN-0027` | yes | `COMPLETE` | `COMPLETE` | Verify a lesson's prose may record a residual limit but may never contradict its status |
| `LESSON-REQ-0028` | LESSON | `lesson:LSN-0028` | yes | `COMPLETE` | `COMPLETE` | Verify a configuration key that no code reads is a defect, not documentation |
| `LESSON-REQ-0029` | LESSON | `lesson:LSN-0029` | yes | `COMPLETE` | `COMPLETE` | Verify a required protocol transition must never turn a mandatory gate red |
| `LESSON-REQ-0030` | LESSON | `lesson:LSN-0030` | no | `COMPLETE` | `COMPLETE` | Verify the lesson preflight presumes an implementing delivery and constrains an audit run badly |
| `LESSON-REQ-0031` | LESSON | `lesson:LSN-0031` | yes | `COMPLETE` | `COMPLETE` | Verify an empty applicable set is not a missing required set, and a control must tell them apart |

## Evidence

### REQ-0001 - canonical:SETUP-00#1.1

- Source reference: docs/SETUP-00-CHECKLIST.md row 1.1
- Description: A single entry point states the phase, current Gate, latest checkpoint, and start protocol.
- Implementation: `file:START-HERE.md`
- Test: `file:docs/checkpoints/LATEST.md`
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### REQ-0002 - canonical:SETUP-00#1.2

- Source reference: docs/SETUP-00-CHECKLIST.md row 1.2
- Description: A Codex adapter binds the canonical contracts without adding independent policy.
- Implementation: `file:AGENTS.md`
- Test: _none_
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### REQ-0003 - canonical:SETUP-00#1.3

- Source reference: docs/SETUP-00-CHECKLIST.md row 1.3
- Description: A Claude Code adapter binds the same contracts.
- Implementation: `file:CLAUDE.md`
- Test: _none_
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### REQ-0004 - canonical:SETUP-00#1.4

- Source reference: docs/SETUP-00-CHECKLIST.md row 1.4
- Description: Tool adapters stay semantically equivalent to the canonical roles.
- Implementation: `file:docs/SETUP-00-CHECKLIST.md`
- Test: `test:ClaudeAdapterTests`, `file:tests/test_development_ledger.py`
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### REQ-0005 - canonical:SETUP-00#2.1

- Source reference: docs/SETUP-00-CHECKLIST.md row 2.1
- Description: The Gate sequence, dependencies, acceptance, and fail conditions are recorded.
- Implementation: `file:docs/MASTER-PLAN.md`
- Test: _none_
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### REQ-0006 - canonical:SETUP-00#2.2

- Source reference: docs/SETUP-00-CHECKLIST.md row 2.2
- Description: The completion standard, mandatory controls, and Git and evidence discipline are recorded.
- Implementation: `file:docs/DEVELOPMENT-CONTRACT.md`
- Test: _none_
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### REQ-0007 - canonical:SETUP-00#2.3

- Source reference: docs/SETUP-00-CHECKLIST.md row 2.3
- Description: Tool-to-tool transfer is formal in both directions.
- Implementation: `file:docs/HANDOFF-PROTOCOL.md`
- Test: _none_
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### REQ-0008 - canonical:SETUP-00#2.4

- Source reference: docs/SETUP-00-CHECKLIST.md row 2.4
- Description: Checkpoint statuses, required events, required contents, commit semantics, and divergence handling are defined.
- Implementation: `file:docs/CHECKPOINT-PROTOCOL.md`
- Test: _none_
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### REQ-0009 - canonical:SETUP-00#2.5

- Source reference: docs/SETUP-00-CHECKLIST.md row 2.5
- Description: Done is defined and excludes assertion-only PASS.
- Implementation: `file:docs/DEFINITION-OF-DONE.md`
- Test: _none_
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### REQ-0010 - canonical:SETUP-00#2.6

- Source reference: docs/SETUP-00-CHECKLIST.md row 2.6
- Description: Quality outcomes, required dimensions, and the promotion rule are defined.
- Implementation: `file:docs/QUALITY-GATES.md`
- Test: _none_
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### REQ-0011 - canonical:SETUP-00#2.7

- Source reference: docs/SETUP-00-CHECKLIST.md row 2.7
- Description: Structural decisions are recorded as ADRs.
- Implementation: `file:docs/SETUP-00-CHECKLIST.md`
- Test: _none_
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### REQ-0012 - canonical:SETUP-00#2.8

- Source reference: docs/SETUP-00-CHECKLIST.md row 2.8
- Description: Architecture, roadmap, provenance, model usage, and detected tool capabilities are documented.
- Implementation: `file:docs/ARCHITECTURE.md`, `file:docs/ROADMAP.md`, `file:docs/PROVENANCE.md`, `file:docs/MODEL-USAGE-POLICY.md`, `file:docs/TOOL-CAPABILITIES.md`
- Test: _none_
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### REQ-0013 - canonical:SETUP-00#3.1

- Source reference: docs/SETUP-00-CHECKLIST.md row 3.1
- Description: The canonical, tool-neutral role contracts exist, one per role of the delivery protocol.
- Implementation: `file:docs/SETUP-00-CHECKLIST.md`
- Test: `test:test_project_agents_match_canonical_role_names`
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### REQ-0014 - canonical:SETUP-00#3.2

- Source reference: docs/SETUP-00-CHECKLIST.md row 3.2
- Description: Documentation, provenance, secret, tool-execution, and training-data policies exist.
- Implementation: `file:docs/SETUP-00-CHECKLIST.md`
- Test: _none_
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### REQ-0015 - canonical:SETUP-00#3.3

- Source reference: docs/SETUP-00-CHECKLIST.md row 3.3
- Description: Reusable templates exist for ADRs, checkpoints, gate reports, and handoffs.
- Implementation: `file:docs/SETUP-00-CHECKLIST.md`
- Test: _none_
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### REQ-0016 - canonical:SETUP-00#4.1

- Source reference: docs/SETUP-00-CHECKLIST.md row 4.1
- Description: Checkpoint state, run metadata, command, test, quality, provenance, and decision schemas exist and are loadable.
- Implementation: `file:docs/SETUP-00-CHECKLIST.md`
- Test: `test:test_all_required_schemas_are_loaded`
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### REQ-0017 - canonical:SETUP-00#4.2

- Source reference: docs/SETUP-00-CHECKLIST.md row 4.2
- Description: An experience schema is reserved for Gate 6 and implements no runtime.
- Implementation: `file:.iacode/schemas/experience.schema.json`
- Test: _none_
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### REQ-0018 - canonical:SETUP-00#4.3

- Source reference: docs/SETUP-00-CHECKLIST.md row 4.3
- Description: Schema evolution is versioned and never invalidates a sealed checkpoint.
- Implementation: `file:docs/SETUP-00-CHECKLIST.md`
- Test: `test:HistoricalCheckpointCompatibilityTests`
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### REQ-0019 - canonical:SETUP-00#5.1

- Source reference: docs/SETUP-00-CHECKLIST.md row 5.1
- Description: A checkpoint can be created with truthful non-PASS defaults.
- Implementation: `file:scripts/development-ledger/new_checkpoint.py`
- Test: `test:test_new_finalize_commit_validate`
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### REQ-0020 - canonical:SETUP-00#5.2

- Source reference: docs/SETUP-00-CHECKLIST.md row 5.2
- Description: A checkpoint can be finalized, and every finalization attempt is recorded with its exit code.
- Implementation: `file:scripts/development-ledger/finalize_checkpoint.py`
- Test: `test:FinalizationLedgerTests`
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### REQ-0021 - canonical:SETUP-00#5.3

- Source reference: docs/SETUP-00-CHECKLIST.md row 5.3
- Description: A checkpoint is validated against schemas, Git state, inventory, quality evidence, and secrets.
- Implementation: `file:scripts/development-ledger/validate_checkpoint.py`
- Test: _none_
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### REQ-0022 - canonical:SETUP-00#5.4

- Source reference: docs/SETUP-00-CHECKLIST.md row 5.4
- Description: Secret redaction is available and documented to its real scope.
- Implementation: `file:scripts/development-ledger/redact_secrets.py`, `file:.iacode/policies/secret-policy.md`
- Test: _none_
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### REQ-0023 - canonical:SETUP-00#5.5

- Source reference: docs/SETUP-00-CHECKLIST.md row 5.5
- Description: The tooling is standard-library only and portable across Windows and Unix-like checkouts.
- Implementation: `file:scripts/development-ledger/README.md`
- Test: `file:.gitattributes`
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### REQ-0024 - canonical:SETUP-00#6.1

- Source reference: docs/SETUP-00-CHECKLIST.md row 6.1
- Description: Every checkpoint carries status, handoff, run metadata, state, plan, decisions, commands, file inventory, tests, quality, provenance, diff summary, risks, and next action.
- Implementation: `file:docs/SETUP-00-CHECKLIST.md`
- Test: _none_
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### REQ-0025 - canonical:SETUP-00#6.2

- Source reference: docs/SETUP-00-CHECKLIST.md row 6.2
- Description: `LATEST.md` points textually to the last checkpoint accepted by validation.
- Implementation: `file:docs/checkpoints/LATEST.md`
- Test: `test:test_latest_to_nonexistent_checkpoint_fails`
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### REQ-0026 - canonical:SETUP-00#6.3

- Source reference: docs/SETUP-00-CHECKLIST.md row 6.3
- Description: The file inventory matches the real change set, with bound content hashes.
- Implementation: `file:docs/SETUP-00-CHECKLIST.md`
- Test: `test:DeltaInventoryTests`
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### REQ-0027 - canonical:SETUP-00#6.4

- Source reference: docs/SETUP-00-CHECKLIST.md row 6.4
- Description: Provenance is complete and `trainingAllowed` defaults to `false`.
- Implementation: `file:docs/SETUP-00-CHECKLIST.md`
- Test: `file:.iacode/policies/provenance-policy.md`
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### REQ-0028 - canonical:SETUP-00#6.5

- Source reference: docs/SETUP-00-CHECKLIST.md row 6.5
- Description: A quality `PASS` carries resolvable evidence.
- Implementation: `file:docs/SETUP-00-CHECKLIST.md`
- Test: `test:QualityEvidenceTests`
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### REQ-0029 - canonical:SETUP-00#6.6

- Source reference: docs/SETUP-00-CHECKLIST.md row 6.6
- Description: Handoff-ready and terminal checkpoints are anchored to an immutable namespaced tag.
- Implementation: `file:docs/SETUP-00-CHECKLIST.md`
- Test: `test:test_handoff_ready_status_requires_commit_anchor`
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### REQ-0030 - canonical:SETUP-00#7.1

- Source reference: docs/SETUP-00-CHECKLIST.md row 7.1
- Description: A cold-start continuation prompt exists and depends only on checked-in files.
- Implementation: `file:prompts/RESUME-WORK.md`
- Test: _none_
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### REQ-0031 - canonical:SETUP-00#7.2

- Source reference: docs/SETUP-00-CHECKLIST.md row 7.2
- Description: Cold-start validation is executed and recorded truthfully, including a blocked attempt.
- Implementation: `file:docs/SETUP-00-CHECKLIST.md`
- Test: _none_
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### REQ-0032 - canonical:SETUP-00#7.3

- Source reference: docs/SETUP-00-CHECKLIST.md row 7.3
- Description: Cross-tool validation state is structured and explicit.
- Implementation: `file:docs/SETUP-00-CHECKLIST.md`
- Test: `test:SecondToolValidationTests`
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### REQ-0033 - canonical:SETUP-00#7.4

- Source reference: docs/SETUP-00-CHECKLIST.md row 7.4
- Description: A sealed checkpoint can be validated from a detached checkout of its own tag.
- Implementation: `file:docs/SETUP-00-CHECKLIST.md`
- Test: `test:DetachedHeadValidationTests`
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### REQ-0034 - canonical:SETUP-00#7.5

- Source reference: docs/SETUP-00-CHECKLIST.md row 7.5
- Description: The handoff is executable by another tool without the producing session.
- Implementation: `file:docs/SETUP-00-CHECKLIST.md`
- Test: _none_
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### REQ-0035 - canonical:SETUP-00#7b.1

- Source reference: docs/SETUP-00-CHECKLIST.md row 7b.1
- Description: Every requirement of a delivery exists in a versioned matrix before implementation.
- Implementation: `file:.iacode/schemas/requirements-matrix.schema.json`
- Test: `test:DeliveryCompletenessMatrixTests`
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### REQ-0036 - canonical:SETUP-00#7b.2

- Source reference: docs/SETUP-00-CHECKLIST.md row 7b.2
- Description: A Test Rework / Green Keeper role forbids shipping anything red and records every cycle.
- Implementation: `file:.iacode/agents/test-rework-greenkeeper.md`, `file:scripts/development-ledger/green_keeper.py`
- Test: `test:GreenKeeperToolTests`
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### REQ-0037 - canonical:SETUP-00#7b.3

- Source reference: docs/SETUP-00-CHECKLIST.md row 7b.3
- Description: A Delivery Completeness Validator audits the matrix before handoff and may not implement.
- Implementation: `file:.iacode/agents/delivery-completeness-validator.md`, `file:scripts/development-ledger/check_completeness.py`
- Test: `test:DeliveryCompletenessMatrixTests`, `test:DeliveryAssuranceGateTests`
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### REQ-0038 - canonical:SETUP-00#7b.4

- Source reference: docs/SETUP-00-CHECKLIST.md row 7b.4
- Description: `GREEN_KEEPER_GATE` and `DELIVERY_COMPLETENESS_GATE` are preconditions of `READY_FOR_REVIEW`.
- Implementation: `file:scripts/development-ledger/validate_checkpoint.py`, `file:docs/QUALITY-GATES.md`
- Test: `test:DeliveryAssuranceGateTests`, `test:DeliveryLifecycleTests`
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### REQ-0039 - canonical:SETUP-00#7b.5

- Source reference: docs/SETUP-00-CHECKLIST.md row 7b.5
- Description: Readiness and blockage can never be claimed together.
- Implementation: `file:docs/SETUP-00-CHECKLIST.md`
- Test: `test:StatusBlockerInvariantTests`, `test:ResealedBlockerFixtureTests`
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### REQ-0040 - canonical:SETUP-00#7b.6

- Source reference: docs/SETUP-00-CHECKLIST.md row 7b.6
- Description: Every operation attempt is recorded, including a refusal decided before execution.
- Implementation: `file:scripts/development-ledger/finalize_checkpoint.py`
- Test: `test:FinalizationAttemptRecordingTests`
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### REQ-0041 - canonical:SETUP-00#7b.7

- Source reference: docs/SETUP-00-CHECKLIST.md row 7b.7
- Description: Every recorded command is reproducible from its declared working directory.
- Implementation: `file:scripts/development-ledger/record_command.py`, `file:.iacode/schemas/command.schema.json`
- Test: `test:CommandReproducibilityTests`
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### REQ-0042 - canonical:SETUP-00#7b.8

- Source reference: docs/SETUP-00-CHECKLIST.md row 7b.8
- Description: The mandatory delivery order is stated in full in every governing document and both adapters.
- Implementation: `file:docs/DEVELOPMENT-CONTRACT.md`, `file:docs/QUALITY-GATES.md`, `file:docs/CHECKPOINT-PROTOCOL.md`, `file:docs/HANDOFF-PROTOCOL.md`, `file:docs/DEFINITION-OF-DONE.md`, `file:START-HERE.md`, `file:AGENTS.md`, `file:CLAUDE.md`
- Test: _none_
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### REQ-0043 - canonical:SETUP-00#7c.1

- Source reference: docs/SETUP-00-CHECKLIST.md row 7c.1
- Description: The project keeps an organizational engineering memory of confirmed failures.
- Implementation: `file:.iacode/schemas/lesson.schema.json`
- Test: `test:EngineeringMemoryStructureTests`
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### REQ-0044 - canonical:SETUP-00#7c.2

- Source reference: docs/SETUP-00-CHECKLIST.md row 7c.2
- Description: A lesson is `GUARDED` only when an automated control prevents recurrence.
- Implementation: `file:scripts/development-ledger/validate_lessons.py`
- Test: `test:LessonValidationTests`
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### REQ-0045 - canonical:SETUP-00#7c.3

- Source reference: docs/SETUP-00-CHECKLIST.md row 7c.3
- Description: A repeat increments recurrence, and a repeat against a guardrail is a `GUARDRAIL_FAILURE`.
- Implementation: `file:scripts/development-ledger/lessons.py`
- Test: `test:LessonRecurrenceTests`
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### REQ-0046 - canonical:SETUP-00#7c.4

- Source reference: docs/SETUP-00-CHECKLIST.md row 7c.4
- Description: A mandatory preflight selects the lessons that constrain each Gate.
- Implementation: `file:scripts/development-ledger/lesson_preflight.py`
- Test: `test:LessonPreflightTests`
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### REQ-0047 - canonical:SETUP-00#7c.5

- Source reference: docs/SETUP-00-CHECKLIST.md row 7c.5
- Description: Applicable lessons become requirements whose absence blocks completeness.
- Implementation: `file:docs/SETUP-00-CHECKLIST.md`
- Test: `test:DerivedRequirementCompletenessTests`
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### REQ-0048 - canonical:SETUP-00#7c.6

- Source reference: docs/SETUP-00-CHECKLIST.md row 7c.6
- Description: Lesson candidates can be extracted from recorded delivery evidence, never above `OBSERVED`.
- Implementation: `file:scripts/development-ledger/extract_lessons.py`
- Test: _none_
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### REQ-0049 - canonical:SETUP-00#7c.7

- Source reference: docs/SETUP-00-CHECKLIST.md row 7c.7
- Description: External validation is grouped into milestones `M0` to `M6`.
- Implementation: `file:docs/MILESTONE-VALIDATION.md`
- Test: `test:MilestoneValidationPolicyTests`
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### REQ-0050 - canonical:SETUP-00#7c.8

- Source reference: docs/SETUP-00-CHECKLIST.md row 7c.8
- Description: An internal verdict is never described as independent external validation.
- Implementation: `file:docs/SETUP-00-CHECKLIST.md`
- Test: `test:MemoryStatusVocabularyTests`, `test:MemoryPolicyValidationTests`
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### REQ-0051 - canonical:SETUP-00#7c.9

- Source reference: docs/SETUP-00-CHECKLIST.md row 7c.9
- Description: An extraordinary audit requires a recorded trigger.
- Implementation: `file:docs/SETUP-00-CHECKLIST.md`
- Test: `test:MemoryPolicyValidationTests`
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### REQ-0052 - canonical:SETUP-00#7c.10

- Source reference: docs/SETUP-00-CHECKLIST.md row 7c.10
- Description: Every completed Gate produces a retrospective.
- Implementation: `file:.iacode/templates/retrospective/TEMPLATE.md`
- Test: _none_
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### REQ-0053 - canonical:SETUP-00#7d.1

- Source reference: docs/SETUP-00-CHECKLIST.md row 7d.1
- Description: One promotion invariant governs every positive terminal status, not only `READY_FOR_REVIEW`.
- Implementation: `file:scripts/development-ledger/validate_checkpoint.py`
- Test: `test:PromotionInvariantTests`
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### REQ-0054 - canonical:SETUP-00#7d.2

- Source reference: docs/SETUP-00-CHECKLIST.md row 7d.2
- Description: The mandatory quality gate set is a closed machine-readable registry that an invocation cannot narrow.
- Implementation: `file:.iacode/policies/quality-gates.json`, `file:scripts/development-ledger/green_keeper.py`
- Test: `test:MandatoryGatePolicyTests`
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### REQ-0055 - canonical:SETUP-00#7d.3

- Source reference: docs/SETUP-00-CHECKLIST.md row 7d.3
- Description: The expected requirement set is derived from canonical sources and compared exactly with the declared set.
- Implementation: `file:.iacode/policies/canonical-requirements.json`, `file:scripts/development-ledger/policies.py`
- Test: `test:ExpectedRequirementSetTests`
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### REQ-0056 - canonical:SETUP-00#7d.4

- Source reference: docs/SETUP-00-CHECKLIST.md row 7d.4
- Description: An external milestone PASS is derived from an audit attestation authored by another sealed checkpoint.
- Implementation: `file:scripts/development-ledger/attestation.py`
- Test: `test:ExternalAttestationTests`
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### REQ-0057 - canonical:SETUP-00#7d.5

- Source reference: docs/SETUP-00-CHECKLIST.md row 7d.5
- Description: A derived artifact carries a fingerprint of its inputs, and staleness is decided by recomputation.
- Implementation: `file:scripts/development-ledger/lesson_preflight.py`
- Test: `test:PreflightFreshnessTests`
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### REQ-0058 - canonical:SETUP-00#7d.6

- Source reference: docs/SETUP-00-CHECKLIST.md row 7d.6
- Description: Every lesson control, evidence path and provenance locator is resolved against the repository.
- Implementation: `file:scripts/development-ledger/lessons.py`
- Test: `test:LessonResolutionTests`, `test:LessonProvenanceTests`
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### REQ-0059 - canonical:SETUP-00#7d.7

- Source reference: docs/SETUP-00-CHECKLIST.md row 7d.7
- Description: Every `GUARDED` lesson names a registered guardrail, and guardrail effectiveness is measured.
- Implementation: `file:.iacode/memory/guardrails/registry.json`
- Test: `test:GuardrailRegistryTests`, `test:GuardrailEffectivenessGateTests`
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### REQ-0060 - canonical:SETUP-00#7d.8

- Source reference: docs/SETUP-00-CHECKLIST.md row 7d.8
- Description: Sealed checkpoints are anchored by a hash-linked chain over tag, commit and tree.
- Implementation: `file:.iacode/anchors/checkpoint-chain.json`, `file:scripts/development-ledger/anchors.py`
- Test: `test:IntegrityAnchorTests`
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### REQ-0061 - canonical:SETUP-00#7d.9

- Source reference: docs/SETUP-00-CHECKLIST.md row 7d.9
- Description: Every count used as evidence is derived once and verified wherever a report states it.
- Implementation: `file:scripts/development-ledger/derive_counts.py`
- Test: `test:DerivedCountTests`
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### REQ-0062 - canonical:SETUP-00#7d.10

- Source reference: docs/SETUP-00-CHECKLIST.md row 7d.10
- Description: Sealing is monotonic and post-commit, and every recorded command binds its declared inputs by content.
- Implementation: `file:scripts/development-ledger/seal_checkpoint.py`
- Test: `test:SealChronologyTests`, `test:CommandInputBindingTests`
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### REQ-0063 - canonical:SETUP-00#7d.11

- Source reference: docs/SETUP-00-CHECKLIST.md row 7d.11
- Description: A milestone delivery carries an internal Red Team and an internal mirror audit, and neither is recorded as external validation.
- Implementation: `file:scripts/development-ledger/m0_red_team.py`, `file:.iacode/agents/m0-closure-auditor.md`
- Test: `test:InternalAssuranceTests`, `test:AuditSourceParsingTests`
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### REQ-0064 - canonical:SETUP-00#7d.12

- Source reference: docs/SETUP-00-CHECKLIST.md row 7d.12
- Description: Every finding of an independent audit is closed before the corrective delivery is offered.
- Implementation: `file:.iacode/policies/audit-registry.json`
- Test: `test:FindingsClosureTests`
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### REQ-0065 - canonical:SETUP-00#7d.13

- Source reference: docs/SETUP-00-CHECKLIST.md row 7d.13
- Description: A milestone verdict is carried by the audit checkpoint about a sealed subject, and its positive path is executed rather than only its refusals.
- Implementation: `file:scripts/development-ledger/attestation.py`, `file:scripts/development-ledger/milestone_status.py`, `file:scripts/development-ledger/promotion_simulation.py`
- Test: `test:AuditAttestationModelTests.test_a_legitimate_attestation_over_the_sealed_history_is_accepted`, `test:PositivePromotionTests.test_the_milestone_verdict_is_derived_as_passed`, `test:PositivePromotionTests.test_the_subject_is_not_rewritten_by_its_own_audit`, `test:AuditAttestationModelTests.test_an_attestation_naming_the_subject_as_its_own_auditor_is_rejected`, `test:AuditAttestationModelTests.test_a_checkpoint_may_not_claim_a_verdict_another_checkpoint_authored`
- Negative test: _none_
- Documentation: `file:docs/MILESTONE-VALIDATION.md`, `file:docs/adr/ADR-0011-audit-checkpoint-carries-the-verdict.md`, `file:.iacode/attestations/README.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### REQ-0066 - canonical:SETUP-00#7d.14

- Source reference: docs/SETUP-00-CHECKLIST.md row 7d.14
- Description: A generic guardrail derives repository state instead of naming a historical checkpoint, and the protocol's own next steps keep every mandatory gate green.
- Implementation: `file:scripts/development-ledger/anchors.py`, `file:scripts/development-ledger/verify_integrity.py`, `file:scripts/development-ledger/successor_durability.py`
- Test: `test:SuccessorDurabilityTests.test_every_state_of_the_chain_verifies`, `test:SuccessorDurabilityTests.test_the_pending_exclusion_moves_with_the_chain`, `test:IntegrityAnchorTests.test_the_pending_exclusion_is_the_newest_sealed_checkpoint`, `test:SuccessorDurabilityTests.test_a_missing_anchor_is_still_detected_after_the_chain_advances`, `test:IntegrityAnchorTests.test_a_sealed_checkpoint_without_an_anchor_is_detected`
- Negative test: _none_
- Documentation: `file:docs/CHECKPOINT-PROTOCOL.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### REQ-0067 - canonical:SETUP-00#7d.15

- Source reference: docs/SETUP-00-CHECKLIST.md row 7d.15
- Description: Every adversarial battery records a null-mutation control, and no count used as evidence is stated in prose.
- Implementation: `file:scripts/development-ledger/m0_red_team.py`, `file:.iacode/schemas/red-team-report.schema.json`, `file:scripts/development-ledger/derive_counts.py`
- Test: `test:DerivedTestCountTests.test_one_run_recorded_in_two_categories_counts_once`, `test:SourceCardinalityPolicyTests.test_no_comment_or_docstring_states_a_derived_count_claim`, `test:InternalAssuranceTests.test_a_report_without_a_null_mutation_control_is_rejected`, `test:DerivedTestCountTests.test_a_count_larger_than_what_exists_is_refused`
- Negative test: _none_
- Documentation: `file:docs/QUALITY-GATES.md`, `file:docs/MILESTONE-VALIDATION.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### REQ-0068 - canonical:SETUP-00#7d.16

- Source reference: docs/SETUP-00-CHECKLIST.md row 7d.16
- Description: An audit control tells an empty applicable set from a missing required set, justifies every `NOT_APPLICABLE` against a canonical derivation no delivery can shrink, and a simulation that claims a control passed executes that control instead of writing its artifact.
- Implementation: `file:scripts/development-ledger/m0_mirror_audit.py`, `file:scripts/development-ledger/mirror_semantics_validation.py`, `file:scripts/development-ledger/gate_transition_simulation.py`, `file:.iacode/schemas/mirror-audit.schema.json`
- Test: `test:MirrorApplicabilitySemanticsTests.test_every_applicability_state_behaves_as_specified`, `test:GateTransitionSimulationTests.test_the_first_checkpoint_of_the_next_gate_reaches_review_readiness`, `test:SimulationExecutesProductionControlsTests.test_the_sealed_artifact_is_the_tools_own_output`, `test:LocalRequirementDeclarationTests.test_the_anchored_count_excludes_a_locally_declared_requirement`
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`, `file:docs/QUALITY-GATES.md`, `file:.iacode/agents/m0-closure-auditor.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### REQ-0069 - canonical:SETUP-00#8.1

- Source reference: docs/SETUP-00-CHECKLIST.md row 8.1
- Description: An independent review is recorded.
- Implementation: `file:docs/SETUP-00-CHECKLIST.md`
- Test: _none_
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### REQ-0070 - canonical:SETUP-00#8.2

- Source reference: docs/SETUP-00-CHECKLIST.md row 8.2
- Description: An adversarial Red Team is recorded.
- Implementation: `file:docs/SETUP-00-CHECKLIST.md`
- Test: _none_
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### REQ-0071 - canonical:SETUP-00#8.3

- Source reference: docs/SETUP-00-CHECKLIST.md row 8.3
- Description: `GATE_PASS` is granted only by a run independent of the implementer.
- Implementation: `file:docs/QUALITY-GATES.md`
- Test: _none_
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### REQ-0072 - canonical:SETUP-00#9.1

- Source reference: docs/SETUP-00-CHECKLIST.md row 9.1
- Description: No Gate 0 or later runtime is implemented during SETUP-00.
- Implementation: `file:docs/SETUP-00-CHECKLIST.md`
- Test: _none_
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### REQ-0073 - canonical:SETUP-00#9.2

- Source reference: docs/SETUP-00-CHECKLIST.md row 9.2
- Description: Documentation is maintained continuously rather than reconstructed at the end.
- Implementation: `file:docs/SETUP-00-CHECKLIST.md`
- Test: _none_
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### REQ-0074 - canonical:SETUP-00#9.3

- Source reference: docs/SETUP-00-CHECKLIST.md row 9.3
- Description: No secret, credential, or private chain-of-thought is stored.
- Implementation: `file:docs/SETUP-00-CHECKLIST.md`
- Test: _none_
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### REQ-0075 - canonical:SETUP-00#9.4

- Source reference: docs/SETUP-00-CHECKLIST.md row 9.4
- Description: Gate advancement requires explicit authorization and a passing previous Gate.
- Implementation: `file:docs/MASTER-PLAN.md`
- Test: _none_
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### LESSON-REQ-0001 - lesson:LSN-0001

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0001
- Description: Verify checkpoint validation must succeed from a detached checkout of the checkpoint tag
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:scripts/development-ledger/validate_checkpoint.py`
- Test: `test:DetachedHeadValidationTests.test_detached_head_at_checkpoint_tag_validates`, `test:DetachedHeadValidationTests.test_detached_head_at_wrong_commit_fails`
- Negative test: _none_
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/ENGINEERING-MEMORY.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### LESSON-REQ-0002 - lesson:LSN-0002

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0002
- Description: Verify a file inventory must be recomputed from the repository, never trusted as an assertion
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:scripts/development-ledger/validate_checkpoint.py`
- Test: `test:DeltaInventoryTests.test_removed_manifest_entry_fails`, `test:DeltaInventoryTests.test_silent_tracked_modification_fails`
- Negative test: _none_
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/ENGINEERING-MEMORY.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### LESSON-REQ-0003 - lesson:LSN-0003

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0003
- Description: Verify every operation attempt must be auditable, including a refusal decided before execution
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:scripts/development-ledger/finalize_checkpoint.py`
- Test: `test:FinalizationAttemptRecordingTests.test_detached_head_refusal_is_recorded`, `test:FinalizationAttemptRecordingTests.test_non_latest_checkpoint_refusal_is_recorded`
- Negative test: _none_
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/ENGINEERING-MEMORY.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### LESSON-REQ-0004 - lesson:LSN-0004

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0004
- Description: Verify a checkpoint may never claim readiness while it also claims to be blocked
- Implementation: `file:.iacode/memory/lessons.jsonl`
- Test: `test:StatusBlockerInvariantTests.test_ready_for_review_with_blocker_fails`, `test:ResealedBlockerFixtureTests.test_resealed_ready_for_review_with_blocker_is_rejected`
- Negative test: _none_
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/ENGINEERING-MEMORY.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### LESSON-REQ-0005 - lesson:LSN-0005

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0005
- Description: Verify a PASS requires evidence that can be executed or resolved, not a statement
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:scripts/development-ledger/validate_checkpoint.py`
- Test: `test:QualityEvidenceTests.test_pass_without_evidence_fails`, `test:QualityEvidenceTests.test_pass_referencing_a_failed_command_fails`, `test:PromotionInvariantTests.test_every_positive_status_rejects_every_red_quality_dimension`
- Negative test: _none_
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/ENGINEERING-MEMORY.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### LESSON-REQ-0006 - lesson:LSN-0006

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0006
- Description: Verify the repository must be self-contained; a specification may not live outside it
- Implementation: `file:.iacode/memory/lessons.jsonl`
- Test: `test:SetupChecklistTests.test_checklist_exists_and_is_referenced`, `test:SetupChecklistTests.test_documentation_links_resolve`
- Negative test: _none_
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/ENGINEERING-MEMORY.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### LESSON-REQ-0007 - lesson:LSN-0007

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0007
- Description: Verify independent validation cannot be declared by the run that did the work
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:.iacode/schemas/checkpoint.schema.json`, `file:scripts/development-ledger/attestation.py`
- Test: `test:SecondToolValidationTests.test_failed_cross_tool_validation_cannot_grant_gate_pass`, `test:DeliveryAssuranceGateTests.test_self_claimed_independent_review_blocks_review`, `test:ExternalAttestationTests.test_an_implementer_checkpoint_cannot_declare_an_external_pass`
- Negative test: _none_
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/ENGINEERING-MEMORY.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### LESSON-REQ-0008 - lesson:LSN-0008

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0008
- Description: Verify requirement completeness must be total and evidence-backed before handoff
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:scripts/development-ledger/check_completeness.py`
- Test: `test:DeliveryCompletenessMatrixTests.test_one_requirement_short_of_total_fails`, `test:DeliveryAssuranceGateTests.test_completeness_validator_not_executed_blocks_review`, `test:ExpectedRequirementSetTests.test_deleting_a_requirement_and_recomputing_the_counts_still_fails`
- Negative test: _none_
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/ENGINEERING-MEMORY.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### LESSON-REQ-0009 - lesson:LSN-0009

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0009
- Description: Verify a red gate requires rework, never a waiver, and never a weakened check
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:.iacode/policies/quality-gates.json`
- Test: `test:GreenKeeperToolTests.test_red_gate_is_reported_as_still_red`, `test:DeliveryAssuranceGateTests.test_green_keeper_pass_with_a_real_failure_is_rejected`, `test:DeliveryAssuranceGateTests.test_red_tests_block_review`, `test:MandatoryGatePolicyTests.test_a_cycle_measured_against_no_gate_is_rejected`
- Negative test: _none_
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/ENGINEERING-MEMORY.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### LESSON-REQ-0010 - lesson:LSN-0010

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0010
- Description: Verify a recorded command must carry runtime, working directory, commit and purpose to be replayable
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:.iacode/schemas/command.schema.json`
- Test: `test:CommandReproducibilityTests.test_bare_script_name_is_rejected`, `test:CommandReproducibilityTests.test_unresolvable_script_path_is_rejected`, `test:CommandInputBindingTests.test_a_record_without_a_digest_is_rejected`
- Negative test: _none_
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/ENGINEERING-MEMORY.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### LESSON-REQ-0011 - lesson:LSN-0011

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0011
- Description: Verify a control over a checkpoint's own evidence must be scoped to the moment it matters
- Implementation: `file:.iacode/memory/lessons.jsonl`
- Test: `test:DeliveryAssuranceGateTests.test_gate_consistency_is_provisional_while_work_is_in_progress`
- Negative test: _none_
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/ENGINEERING-MEMORY.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### LESSON-REQ-0012 - lesson:LSN-0012

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0012
- Description: Verify sealed checkpoints and their tags are immutable, and tooling must keep validating them
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:docs/CHECKPOINT-PROTOCOL.md`, `file:scripts/development-ledger/anchors.py`
- Test: `test:HistoricalCheckpointCompatibilityTests.test_first_sealed_checkpoint_still_validates`, `test:HistoricalCheckpointCompatibilityTests.test_fourth_sealed_checkpoint_still_validates`, `test:IntegrityAnchorTests.test_a_moved_historical_tag_is_detected`
- Negative test: _none_
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/ENGINEERING-MEMORY.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### LESSON-REQ-0013 - lesson:LSN-0013

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0013
- Description: Verify an installed capability must be detected by resolved path, not by a bare command lookup
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:docs/TOOL-CAPABILITIES.md`
- Test: _none_
- Negative test: _none_
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/ENGINEERING-MEMORY.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### LESSON-REQ-0014 - lesson:LSN-0014

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0014
- Description: Verify evidence must be recorded as it happens, not reconstructed at the end of a run
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:scripts/development-ledger/record_command.py`
- Test: `test:SealChronologyTests.test_a_record_after_the_end_of_the_run_is_rejected`
- Negative test: _none_
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/ENGINEERING-MEMORY.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### LESSON-REQ-0015 - lesson:LSN-0015

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0015
- Description: Verify every positive terminal status needs one shared promotion invariant
- Implementation: `file:.iacode/memory/lessons.jsonl`
- Test: `test:PromotionInvariantTests.test_every_positive_status_rejects_a_red_green_keeper`
- Negative test: _none_
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/ENGINEERING-MEMORY.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### LESSON-REQ-0016 - lesson:LSN-0016

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0016
- Description: Verify a mandatory set must be closed by policy, never chosen by the caller
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:.iacode/policies/quality-gates.json`
- Test: _none_
- Negative test: _none_
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/ENGINEERING-MEMORY.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### LESSON-REQ-0017 - lesson:LSN-0017

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0017
- Description: Verify a completeness denominator must come from a source the delivery does not own
- Implementation: `file:.iacode/memory/lessons.jsonl`
- Test: `test:ExpectedRequirementSetTests.test_an_unexpected_anchored_requirement_is_rejected`
- Negative test: _none_
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/ENGINEERING-MEMORY.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### LESSON-REQ-0018 - lesson:LSN-0018

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0018
- Description: Verify a structured reference must be resolved, not merely well typed
- Implementation: `file:.iacode/memory/lessons.jsonl`
- Test: `test:LessonResolutionTests.test_a_test_control_must_exist_in_the_suite`
- Negative test: _none_
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/ENGINEERING-MEMORY.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### LESSON-REQ-0019 - lesson:LSN-0019

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0019
- Description: Verify a derived artifact must carry a fingerprint of the inputs that produced it
- Implementation: `file:.iacode/memory/lessons.jsonl`
- Test: `test:PreflightFreshnessTests.test_a_dropped_lesson_makes_the_preflight_stale`
- Negative test: _none_
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/ENGINEERING-MEMORY.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### LESSON-REQ-0020 - lesson:LSN-0020

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0020
- Description: Verify evidence produced from a dirty tree needs immutable input identity
- Implementation: `file:.iacode/memory/lessons.jsonl`
- Test: `test:CommandInputBindingTests.test_the_recorder_binds_inputs_automatically`
- Negative test: _none_
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/ENGINEERING-MEMORY.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### LESSON-REQ-0021 - lesson:LSN-0021

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0021
- Description: Verify sealed history needs an anchor outside the content it describes
- Implementation: `file:.iacode/memory/lessons.jsonl`
- Test: `test:IntegrityAnchorTests.test_a_broken_link_between_anchors_is_detected`
- Negative test: _none_
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/ENGINEERING-MEMORY.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### LESSON-REQ-0022 - lesson:LSN-0022

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0022
- Description: Verify an authoritative count must be derived once, never maintained by hand twice
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:scripts/development-ledger/derive_counts.py`, `file:tests/test_development_ledger.py`
- Test: `test:SourceCardinalityPolicyTests.test_no_comment_or_docstring_states_a_derived_count_claim`, `test:DerivedCountTests.test_the_stored_counts_match_the_derivation`, `test:DerivedTestCountTests.test_one_run_recorded_in_two_categories_counts_once`, `test:DerivedCountTests.test_a_forged_count_is_rejected`, `test:DerivedTestCountTests.test_a_count_larger_than_what_exists_is_refused`
- Negative test: _none_
- Documentation: `file:docs/QUALITY-GATES.md`, `file:.iacode/memory/LESSONS.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### LESSON-REQ-0023 - lesson:LSN-0023

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0023
- Description: Verify a lesson must cite a source that actually records the finding it claims
- Implementation: `file:.iacode/memory/lessons.jsonl`
- Test: `test:LessonProvenanceTests.test_a_finding_absent_from_the_cited_checkpoint_is_rejected`
- Negative test: _none_
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/ENGINEERING-MEMORY.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### LESSON-REQ-0024 - lesson:LSN-0024

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0024
- Description: Verify a control is finished only when its positive path has been executed, not only its refusals
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:scripts/development-ledger/promotion_simulation.py`
- Test: `test:PositivePromotionTests.test_the_milestone_verdict_is_derived_as_passed`, `test:PositivePromotionTests.test_the_subject_is_not_rewritten_by_its_own_audit`, `test:PositivePromotionTests.test_a_fresh_session_audit_cannot_reach_the_external_status`
- Negative test: _none_
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/DEFINITION-OF-DONE.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### LESSON-REQ-0025 - lesson:LSN-0025

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0025
- Description: Verify a generic guardrail derives repository state instead of naming today's checkpoint
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:scripts/development-ledger/anchors.py`
- Test: `test:IntegrityAnchorTests.test_the_pending_exclusion_is_the_newest_sealed_checkpoint`, `test:SuccessorDurabilityTests.test_the_pending_exclusion_moves_with_the_chain`, `test:IntegrityAnchorTests.test_a_sealed_checkpoint_without_an_anchor_is_detected`
- Negative test: _none_
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/CHECKPOINT-PROTOCOL.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### LESSON-REQ-0026 - lesson:LSN-0026

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0026
- Description: Verify an adversarial battery without a null-mutation control proves nothing
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:scripts/development-ledger/m0_red_team.py`, `file:.iacode/schemas/red-team-report.schema.json`
- Test: `test:InternalAssuranceTests.test_the_consistent_fixture_passes`, `test:InternalAssuranceTests.test_a_report_without_a_null_mutation_control_is_rejected`, `test:InternalAssuranceTests.test_a_failed_null_mutation_control_cannot_produce_a_pass`
- Negative test: _none_
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/MILESTONE-VALIDATION.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### LESSON-REQ-0027 - lesson:LSN-0027

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0027
- Description: Verify a lesson's prose may record a residual limit but may never contradict its status
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:scripts/development-ledger/lessons.py`
- Test: `test:MemoryPolicyDocumentTests.test_the_repository_memory_has_no_status_contradiction`, `test:MemoryPolicyDocumentTests.test_a_guarded_lesson_may_not_describe_itself_as_unguarded`
- Negative test: _none_
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/ENGINEERING-MEMORY.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### LESSON-REQ-0028 - lesson:LSN-0028

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0028
- Description: Verify a configuration key that no code reads is a defect, not documentation
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:.iacode/schemas/memory-policy.schema.json`, `file:.iacode/memory/POLICY.json`
- Test: `test:MemoryPolicyDocumentTests.test_the_declared_policy_validates_against_its_schema`, `test:MemoryPolicyDocumentTests.test_a_setting_no_code_reads_cannot_be_declared`
- Negative test: _none_
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/ENGINEERING-MEMORY.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### LESSON-REQ-0029 - lesson:LSN-0029

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0029
- Description: Verify a required protocol transition must never turn a mandatory gate red
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:scripts/development-ledger/successor_durability.py`
- Test: `test:SuccessorDurabilityTests.test_every_state_of_the_chain_verifies`, `test:SuccessorDurabilityTests.test_three_checkpoints_were_sealed_in_succession`, `test:SuccessorDurabilityTests.test_a_missing_anchor_is_still_detected_after_the_chain_advances`
- Negative test: _none_
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/DEFINITION-OF-DONE.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### LESSON-REQ-0030 - lesson:LSN-0030

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0030
- Description: Verify the lesson preflight presumes an implementing delivery and constrains an audit run badly
- Implementation: `file:.iacode/memory/lessons.jsonl`
- Test: `test:LessonPreflightTests.test_the_repository_preflight_covers_every_applicable_lesson`
- Negative test: _none_
- Documentation: `file:docs/ENGINEERING-MEMORY.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_

### LESSON-REQ-0031 - lesson:LSN-0031

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0031
- Description: Verify an empty applicable set is not a missing required set, and a control must tell them apart
- Implementation: `file:scripts/development-ledger/m0_mirror_audit.py`
- Test: `test:MirrorApplicabilitySemanticsTests`, `test:MirrorApplicabilityValidationTests`
- Negative test: _none_
- Documentation: `file:docs/QUALITY-GATES.md`
- Validation: `checkpoint:FINAL-M0-AUDIT-MATRIX.json`, `checkpoint:AUDIT-EXECUTIONS.json`
- Guardrail: _none_
