# Closure Requirements - SETUP-00-CP-0008

Derived from the canonical sources listed below, before implementation. The expected set
is recomputed by `policies.expected_requirement_refs` and compared exactly with the
declared set, so a requirement cannot be dropped and the denominator cannot be reduced.

## Sources

- SOURCE A: docs/SETUP-00-CHECKLIST.md, the canonical SETUP-00 specification
- SOURCE B: docs/MILESTONE-VALIDATION.md, the M0 milestone requirements of the audit
- SOURCE C: docs/checkpoints/SETUP-00-CP-0007/REVIEW-REPORT.md, the audit findings
- SOURCE D: docs/checkpoints/SETUP-00-CP-0007/RED-TEAM-REPORT.md, the A-Z attacks
- SOURCE E: LESSON-PREFLIGHT.json, the lessons the engineering memory imposes

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
| `REQ-0065` | SETUP | `canonical:SETUP-00#8.1` | yes | `COMPLETE` | `COMPLETE` | An independent review is recorded. |
| `REQ-0066` | SETUP | `canonical:SETUP-00#8.2` | yes | `COMPLETE` | `COMPLETE` | An adversarial Red Team is recorded. |
| `REQ-0067` | SETUP | `canonical:SETUP-00#8.3` | yes | `COMPLETE` | `COMPLETE` | `GATE_PASS` is granted only by a run independent of the implementer. |
| `REQ-0068` | SETUP | `canonical:SETUP-00#9.1` | yes | `COMPLETE` | `COMPLETE` | No Gate 0 or later runtime is implemented during SETUP-00. |
| `REQ-0069` | SETUP | `canonical:SETUP-00#9.2` | yes | `COMPLETE` | `COMPLETE` | Documentation is maintained continuously rather than reconstructed at the end. |
| `REQ-0070` | SETUP | `canonical:SETUP-00#9.3` | yes | `COMPLETE` | `COMPLETE` | No secret, credential, or private chain-of-thought is stored. |
| `REQ-0071` | SETUP | `canonical:SETUP-00#9.4` | yes | `COMPLETE` | `COMPLETE` | Gate advancement requires explicit authorization and a passing previous Gate. |
| `REQ-0072` | AUDIT_FINDING | `finding:M0-F-001` | yes | `COMPLETE` | `COMPLETE` | positive terminal status bypasses delivery assurance |
| `REQ-0073` | AUDIT_FINDING | `finding:M0-F-002` | yes | `COMPLETE` | `COMPLETE` | external milestone PASS can be self-asserted on an intermediate Gate |
| `REQ-0074` | AUDIT_FINDING | `finding:M0-F-003` | yes | `COMPLETE` | `COMPLETE` | lesson preflight is not bound to the checkpoint Gate or canonical memory |
| `REQ-0075` | AUDIT_FINDING | `finding:M0-F-004` | yes | `COMPLETE` | `COMPLETE` | Engineering Memory accepts forged controls, missing evidence, and nested secrets |
| `REQ-0076` | AUDIT_FINDING | `finding:M0-F-005` | yes | `COMPLETE` | `COMPLETE` | Green Keeper has a vacuous PASS path |
| `REQ-0077` | AUDIT_FINDING | `finding:M0-F-006` | yes | `COMPLETE` | `COMPLETE` | completeness denominator is not anchored |
| `REQ-0078` | AUDIT_FINDING | `finding:M0-F-007` | yes | `COMPLETE` | `COMPLETE` | historical immutability is not anchored externally |
| `REQ-0079` | AUDIT_FINDING | `finding:M0-F-008` | yes | `COMPLETE` | `COMPLETE` | CP-0006 mandatory count is contradictory and accepted |
| `REQ-0080` | AUDIT_FINDING | `finding:M0-F-009` | yes | `COMPLETE` | `COMPLETE` | command records are not reproducible at their declared commits |
| `REQ-0081` | AUDIT_FINDING | `finding:M0-F-010` | yes | `COMPLETE` | `COMPLETE` | sealed finalization chronology is internally inconsistent |
| `REQ-0082` | AUDIT_FINDING | `finding:M0-F-011` | yes | `COMPLETE` | `COMPLETE` | one lesson source locator is inaccurate |
| `REQ-0083` | AUDIT_ATTACK | `attack:A` | yes | `COMPLETE` | `COMPLETE` | Defend attack A: Add blocker to `READY_FOR_REVIEW` |
| `REQ-0084` | AUDIT_ATTACK | `attack:B` | yes | `COMPLETE` | `COMPLETE` | Defend attack B: Set a review-ready quality gate red |
| `REQ-0085` | AUDIT_ATTACK | `attack:C` | yes | `COMPLETE` | `COMPLETE` | Defend attack C: Delete mandatory `REQ-0001` and recompute all counts |
| `REQ-0086` | AUDIT_ATTACK | `attack:D` | yes | `COMPLETE` | `COMPLETE` | Defend attack D: Forge stored 100% counts |
| `REQ-0087` | AUDIT_ATTACK | `attack:E` | yes | `COMPLETE` | `COMPLETE` | Defend attack E: Remove a derived requirement |
| `REQ-0088` | AUDIT_ATTACK | `attack:F` | yes | `COMPLETE` | `COMPLETE` | Defend attack F: Replace prevention with documentation only |
| `REQ-0089` | AUDIT_ATTACK | `attack:G` | yes | `COMPLETE` | `COMPLETE` | Defend attack G: Duplicate lesson ID |
| `REQ-0090` | AUDIT_ATTACK | `attack:H` | yes | `COMPLETE` | `COMPLETE` | Defend attack H: Insert a secret-shaped value in a scanned field |
| `REQ-0091` | AUDIT_ATTACK | `attack:I` | yes | `COMPLETE` | `COMPLETE` | Defend attack I: Rewrite CP-0005, declare it in CP-0006 inventory, refresh hashes, move CP-0006 tag |
| `REQ-0092` | AUDIT_ATTACK | `attack:J` | yes | `COMPLETE` | `COMPLETE` | Defend attack J: Move CP-0006 tag and HEAD together to a new commit |
| `REQ-0093` | AUDIT_ATTACK | `attack:K` | yes | `COMPLETE` | `COMPLETE` | Defend attack K: Remove one inventory entry |
| `REQ-0094` | AUDIT_ATTACK | `attack:L` | yes | `COMPLETE` | `COMPLETE` | Defend attack L: Silently modify a tracked file |
| `REQ-0095` | AUDIT_ATTACK | `attack:M` | yes | `COMPLETE` | `COMPLETE` | Defend attack M: Set a wrong `hashBefore` |
| `REQ-0096` | AUDIT_ATTACK | `attack:N` | yes | `COMPLETE` | `COMPLETE` | Defend attack N: Set a wrong `hashAfter` |
| `REQ-0097` | AUDIT_ATTACK | `attack:O` | yes | `COMPLETE` | `COMPLETE` | Defend attack O: Claim PASS with no evidence |
| `REQ-0098` | AUDIT_ATTACK | `attack:P` | yes | `COMPLETE` | `COMPLETE` | Defend attack P: Reference an unknown command |
| `REQ-0099` | AUDIT_ATTACK | `attack:Q` | yes | `COMPLETE` | `COMPLETE` | Defend attack Q: Supply arbitrary complete attribution with empty evidence |
| `REQ-0100` | AUDIT_ATTACK | `attack:R` | yes | `COMPLETE` | `COMPLETE` | Defend attack R: Promote an internally authored result to external status |
| `REQ-0101` | AUDIT_ATTACK | `attack:S` | yes | `COMPLETE` | `COMPLETE` | Defend attack S: Leave review/Red Team pending and auditor/time null |
| `REQ-0102` | AUDIT_ATTACK | `attack:T` | yes | `COMPLETE` | `COMPLETE` | Defend attack T: Request audit without a known trigger |
| `REQ-0103` | AUDIT_ATTACK | `attack:U` | yes | `COMPLETE` | `COMPLETE` | Defend attack U: Retire canonical lesson but keep stale active preflight |
| `REQ-0104` | AUDIT_ATTACK | `attack:V` | yes | `COMPLETE` | `COMPLETE` | Defend attack V: Run `--gates ""`, then retain PASS with an actually failing test |
| `REQ-0105` | AUDIT_ATTACK | `attack:W` | yes | `COMPLETE` | `COMPLETE` | Defend attack W: Claim PASS with a PARTIAL row |
| `REQ-0106` | AUDIT_ATTACK | `attack:X` | yes | `COMPLETE` | `COMPLETE` | Defend attack X: Remove required runtime/record field |
| `REQ-0107` | AUDIT_ATTACK | `attack:Y` | yes | `COMPLETE` | `COMPLETE` | Defend attack Y: Point `LATEST.md` at CP-0005 while validating CP-0006 |
| `REQ-0108` | AUDIT_ATTACK | `attack:Z` | yes | `COMPLETE` | `COMPLETE` | Defend attack Z: Use path traversal as checkpoint/Gate input |
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

## Evidence

### REQ-0001 - canonical:SETUP-00#1.1

- Source reference: docs/SETUP-00-CHECKLIST.md row 1.1
- Description: A single entry point states the phase, current Gate, latest checkpoint, and start protocol.
- Implementation: `file:START-HERE.md`
- Test: `file:docs/checkpoints/LATEST.md`
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0002 - canonical:SETUP-00#1.2

- Source reference: docs/SETUP-00-CHECKLIST.md row 1.2
- Description: A Codex adapter binds the canonical contracts without adding independent policy.
- Implementation: `file:AGENTS.md`
- Test: _none_
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0003 - canonical:SETUP-00#1.3

- Source reference: docs/SETUP-00-CHECKLIST.md row 1.3
- Description: A Claude Code adapter binds the same contracts.
- Implementation: `file:CLAUDE.md`
- Test: _none_
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0004 - canonical:SETUP-00#1.4

- Source reference: docs/SETUP-00-CHECKLIST.md row 1.4
- Description: Tool adapters stay semantically equivalent to the canonical roles.
- Implementation: _none_
- Test: `test:ClaudeAdapterTests`, `file:tests/test_development_ledger.py`
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0005 - canonical:SETUP-00#2.1

- Source reference: docs/SETUP-00-CHECKLIST.md row 2.1
- Description: The Gate sequence, dependencies, acceptance, and fail conditions are recorded.
- Implementation: `file:docs/MASTER-PLAN.md`
- Test: _none_
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0006 - canonical:SETUP-00#2.2

- Source reference: docs/SETUP-00-CHECKLIST.md row 2.2
- Description: The completion standard, mandatory controls, and Git and evidence discipline are recorded.
- Implementation: `file:docs/DEVELOPMENT-CONTRACT.md`
- Test: _none_
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0007 - canonical:SETUP-00#2.3

- Source reference: docs/SETUP-00-CHECKLIST.md row 2.3
- Description: Tool-to-tool transfer is formal in both directions.
- Implementation: `file:docs/HANDOFF-PROTOCOL.md`
- Test: _none_
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0008 - canonical:SETUP-00#2.4

- Source reference: docs/SETUP-00-CHECKLIST.md row 2.4
- Description: Checkpoint statuses, required events, required contents, commit semantics, and divergence handling are defined.
- Implementation: `file:docs/CHECKPOINT-PROTOCOL.md`
- Test: _none_
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0009 - canonical:SETUP-00#2.5

- Source reference: docs/SETUP-00-CHECKLIST.md row 2.5
- Description: Done is defined and excludes assertion-only PASS.
- Implementation: `file:docs/DEFINITION-OF-DONE.md`
- Test: _none_
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0010 - canonical:SETUP-00#2.6

- Source reference: docs/SETUP-00-CHECKLIST.md row 2.6
- Description: Quality outcomes, required dimensions, and the promotion rule are defined.
- Implementation: `file:docs/QUALITY-GATES.md`
- Test: _none_
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0011 - canonical:SETUP-00#2.7

- Source reference: docs/SETUP-00-CHECKLIST.md row 2.7
- Description: Structural decisions are recorded as ADRs.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0012 - canonical:SETUP-00#2.8

- Source reference: docs/SETUP-00-CHECKLIST.md row 2.8
- Description: Architecture, roadmap, provenance, model usage, and detected tool capabilities are documented.
- Implementation: `file:docs/ARCHITECTURE.md`, `file:docs/ROADMAP.md`, `file:docs/PROVENANCE.md`, `file:docs/MODEL-USAGE-POLICY.md`, `file:docs/TOOL-CAPABILITIES.md`
- Test: _none_
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0013 - canonical:SETUP-00#3.1

- Source reference: docs/SETUP-00-CHECKLIST.md row 3.1
- Description: The canonical, tool-neutral role contracts exist, one per role of the delivery protocol.
- Implementation: _none_
- Test: `test:test_project_agents_match_canonical_role_names`
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0014 - canonical:SETUP-00#3.2

- Source reference: docs/SETUP-00-CHECKLIST.md row 3.2
- Description: Documentation, provenance, secret, tool-execution, and training-data policies exist.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0015 - canonical:SETUP-00#3.3

- Source reference: docs/SETUP-00-CHECKLIST.md row 3.3
- Description: Reusable templates exist for ADRs, checkpoints, gate reports, and handoffs.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0016 - canonical:SETUP-00#4.1

- Source reference: docs/SETUP-00-CHECKLIST.md row 4.1
- Description: Checkpoint state, run metadata, command, test, quality, provenance, and decision schemas exist and are loadable.
- Implementation: _none_
- Test: `test:test_all_required_schemas_are_loaded`
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0017 - canonical:SETUP-00#4.2

- Source reference: docs/SETUP-00-CHECKLIST.md row 4.2
- Description: An experience schema is reserved for Gate 6 and implements no runtime.
- Implementation: `file:.iacode/schemas/experience.schema.json`
- Test: _none_
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0018 - canonical:SETUP-00#4.3

- Source reference: docs/SETUP-00-CHECKLIST.md row 4.3
- Description: Schema evolution is versioned and never invalidates a sealed checkpoint.
- Implementation: _none_
- Test: `test:HistoricalCheckpointCompatibilityTests`
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0019 - canonical:SETUP-00#5.1

- Source reference: docs/SETUP-00-CHECKLIST.md row 5.1
- Description: A checkpoint can be created with truthful non-PASS defaults.
- Implementation: `file:scripts/development-ledger/new_checkpoint.py`
- Test: `test:test_new_finalize_commit_validate`
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0020 - canonical:SETUP-00#5.2

- Source reference: docs/SETUP-00-CHECKLIST.md row 5.2
- Description: A checkpoint can be finalized, and every finalization attempt is recorded with its exit code.
- Implementation: `file:scripts/development-ledger/finalize_checkpoint.py`
- Test: `test:FinalizationLedgerTests`
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0021 - canonical:SETUP-00#5.3

- Source reference: docs/SETUP-00-CHECKLIST.md row 5.3
- Description: A checkpoint is validated against schemas, Git state, inventory, quality evidence, and secrets.
- Implementation: `file:scripts/development-ledger/validate_checkpoint.py`
- Test: _none_
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0022 - canonical:SETUP-00#5.4

- Source reference: docs/SETUP-00-CHECKLIST.md row 5.4
- Description: Secret redaction is available and documented to its real scope.
- Implementation: `file:scripts/development-ledger/redact_secrets.py`, `file:.iacode/policies/secret-policy.md`
- Test: _none_
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0023 - canonical:SETUP-00#5.5

- Source reference: docs/SETUP-00-CHECKLIST.md row 5.5
- Description: The tooling is standard-library only and portable across Windows and Unix-like checkouts.
- Implementation: `file:scripts/development-ledger/README.md`
- Test: `file:.gitattributes`
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0024 - canonical:SETUP-00#6.1

- Source reference: docs/SETUP-00-CHECKLIST.md row 6.1
- Description: Every checkpoint carries status, handoff, run metadata, state, plan, decisions, commands, file inventory, tests, quality, provenance, diff summary, risks, and next action.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0025 - canonical:SETUP-00#6.2

- Source reference: docs/SETUP-00-CHECKLIST.md row 6.2
- Description: `LATEST.md` points textually to the last checkpoint accepted by validation.
- Implementation: `file:docs/checkpoints/LATEST.md`
- Test: `test:test_latest_to_nonexistent_checkpoint_fails`
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0026 - canonical:SETUP-00#6.3

- Source reference: docs/SETUP-00-CHECKLIST.md row 6.3
- Description: The file inventory matches the real change set, with bound content hashes.
- Implementation: `checkpoint:FILES.json`
- Test: `test:DeltaInventoryTests`
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0027 - canonical:SETUP-00#6.4

- Source reference: docs/SETUP-00-CHECKLIST.md row 6.4
- Description: Provenance is complete and `trainingAllowed` defaults to `false`.
- Implementation: `checkpoint:PROVENANCE.json`
- Test: `file:.iacode/policies/provenance-policy.md`
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0028 - canonical:SETUP-00#6.5

- Source reference: docs/SETUP-00-CHECKLIST.md row 6.5
- Description: A quality `PASS` carries resolvable evidence.
- Implementation: `checkpoint:QUALITY.json`
- Test: `test:QualityEvidenceTests`
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0029 - canonical:SETUP-00#6.6

- Source reference: docs/SETUP-00-CHECKLIST.md row 6.6
- Description: Handoff-ready and terminal checkpoints are anchored to an immutable namespaced tag.
- Implementation: `checkpoint:STATE.json`
- Test: `test:test_handoff_ready_status_requires_commit_anchor`
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0030 - canonical:SETUP-00#7.1

- Source reference: docs/SETUP-00-CHECKLIST.md row 7.1
- Description: A cold-start continuation prompt exists and depends only on checked-in files.
- Implementation: `file:prompts/RESUME-WORK.md`
- Test: _none_
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0031 - canonical:SETUP-00#7.2

- Source reference: docs/SETUP-00-CHECKLIST.md row 7.2
- Description: Cold-start validation is executed and recorded truthfully, including a blocked attempt.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0032 - canonical:SETUP-00#7.3

- Source reference: docs/SETUP-00-CHECKLIST.md row 7.3
- Description: Cross-tool validation state is structured and explicit.
- Implementation: `checkpoint:STATE.json`
- Test: `test:SecondToolValidationTests`
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0033 - canonical:SETUP-00#7.4

- Source reference: docs/SETUP-00-CHECKLIST.md row 7.4
- Description: A sealed checkpoint can be validated from a detached checkout of its own tag.
- Implementation: _none_
- Test: `test:DetachedHeadValidationTests`
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0034 - canonical:SETUP-00#7.5

- Source reference: docs/SETUP-00-CHECKLIST.md row 7.5
- Description: The handoff is executable by another tool without the producing session.
- Implementation: `checkpoint:HANDOFF.md`
- Test: _none_
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0035 - canonical:SETUP-00#7b.1

- Source reference: docs/SETUP-00-CHECKLIST.md row 7b.1
- Description: Every requirement of a delivery exists in a versioned matrix before implementation.
- Implementation: `checkpoint:REQUIREMENTS-MATRIX.json`, `file:.iacode/schemas/requirements-matrix.schema.json`
- Test: `test:DeliveryCompletenessMatrixTests`
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0036 - canonical:SETUP-00#7b.2

- Source reference: docs/SETUP-00-CHECKLIST.md row 7b.2
- Description: A Test Rework / Green Keeper role forbids shipping anything red and records every cycle.
- Implementation: `file:.iacode/agents/test-rework-greenkeeper.md`, `file:scripts/development-ledger/green_keeper.py`
- Test: `test:GreenKeeperToolTests`
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0037 - canonical:SETUP-00#7b.3

- Source reference: docs/SETUP-00-CHECKLIST.md row 7b.3
- Description: A Delivery Completeness Validator audits the matrix before handoff and may not implement.
- Implementation: `file:.iacode/agents/delivery-completeness-validator.md`, `file:scripts/development-ledger/check_completeness.py`
- Test: `test:DeliveryCompletenessMatrixTests`, `test:DeliveryAssuranceGateTests`
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0038 - canonical:SETUP-00#7b.4

- Source reference: docs/SETUP-00-CHECKLIST.md row 7b.4
- Description: `GREEN_KEEPER_GATE` and `DELIVERY_COMPLETENESS_GATE` are preconditions of `READY_FOR_REVIEW`.
- Implementation: `file:scripts/development-ledger/validate_checkpoint.py`, `file:docs/QUALITY-GATES.md`
- Test: `test:DeliveryAssuranceGateTests`, `test:DeliveryLifecycleTests`
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0039 - canonical:SETUP-00#7b.5

- Source reference: docs/SETUP-00-CHECKLIST.md row 7b.5
- Description: Readiness and blockage can never be claimed together.
- Implementation: _none_
- Test: `test:StatusBlockerInvariantTests`, `test:ResealedBlockerFixtureTests`
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0040 - canonical:SETUP-00#7b.6

- Source reference: docs/SETUP-00-CHECKLIST.md row 7b.6
- Description: Every operation attempt is recorded, including a refusal decided before execution.
- Implementation: `file:scripts/development-ledger/finalize_checkpoint.py`
- Test: `test:FinalizationAttemptRecordingTests`
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0041 - canonical:SETUP-00#7b.7

- Source reference: docs/SETUP-00-CHECKLIST.md row 7b.7
- Description: Every recorded command is reproducible from its declared working directory.
- Implementation: `file:scripts/development-ledger/record_command.py`, `file:.iacode/schemas/command.schema.json`
- Test: `test:CommandReproducibilityTests`
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0042 - canonical:SETUP-00#7b.8

- Source reference: docs/SETUP-00-CHECKLIST.md row 7b.8
- Description: The mandatory delivery order is stated in full in every governing document and both adapters.
- Implementation: `file:docs/DEVELOPMENT-CONTRACT.md`, `file:docs/QUALITY-GATES.md`, `file:docs/CHECKPOINT-PROTOCOL.md`, `file:docs/HANDOFF-PROTOCOL.md`, `file:docs/DEFINITION-OF-DONE.md`, `file:START-HERE.md`, `file:AGENTS.md`, `file:CLAUDE.md`
- Test: _none_
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0043 - canonical:SETUP-00#7c.1

- Source reference: docs/SETUP-00-CHECKLIST.md row 7c.1
- Description: The project keeps an organizational engineering memory of confirmed failures.
- Implementation: `file:.iacode/schemas/lesson.schema.json`
- Test: `test:EngineeringMemoryStructureTests`
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0044 - canonical:SETUP-00#7c.2

- Source reference: docs/SETUP-00-CHECKLIST.md row 7c.2
- Description: A lesson is `GUARDED` only when an automated control prevents recurrence.
- Implementation: `file:scripts/development-ledger/validate_lessons.py`
- Test: `test:LessonValidationTests`
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0045 - canonical:SETUP-00#7c.3

- Source reference: docs/SETUP-00-CHECKLIST.md row 7c.3
- Description: A repeat increments recurrence, and a repeat against a guardrail is a `GUARDRAIL_FAILURE`.
- Implementation: `file:scripts/development-ledger/lessons.py`
- Test: `test:LessonRecurrenceTests`
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0046 - canonical:SETUP-00#7c.4

- Source reference: docs/SETUP-00-CHECKLIST.md row 7c.4
- Description: A mandatory preflight selects the lessons that constrain each Gate.
- Implementation: `file:scripts/development-ledger/lesson_preflight.py`, `checkpoint:LESSON-PREFLIGHT.json`
- Test: `test:LessonPreflightTests`
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0047 - canonical:SETUP-00#7c.5

- Source reference: docs/SETUP-00-CHECKLIST.md row 7c.5
- Description: Applicable lessons become requirements whose absence blocks completeness.
- Implementation: `checkpoint:REQUIREMENTS-MATRIX.json`
- Test: `test:DerivedRequirementCompletenessTests`
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0048 - canonical:SETUP-00#7c.6

- Source reference: docs/SETUP-00-CHECKLIST.md row 7c.6
- Description: Lesson candidates can be extracted from recorded delivery evidence, never above `OBSERVED`.
- Implementation: `file:scripts/development-ledger/extract_lessons.py`
- Test: _none_
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0049 - canonical:SETUP-00#7c.7

- Source reference: docs/SETUP-00-CHECKLIST.md row 7c.7
- Description: External validation is grouped into milestones `M0` to `M6`.
- Implementation: `file:docs/MILESTONE-VALIDATION.md`
- Test: `test:MilestoneValidationPolicyTests`
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0050 - canonical:SETUP-00#7c.8

- Source reference: docs/SETUP-00-CHECKLIST.md row 7c.8
- Description: An internal verdict is never described as independent external validation.
- Implementation: _none_
- Test: `test:MemoryStatusVocabularyTests`, `test:MemoryPolicyValidationTests`
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0051 - canonical:SETUP-00#7c.9

- Source reference: docs/SETUP-00-CHECKLIST.md row 7c.9
- Description: An extraordinary audit requires a recorded trigger.
- Implementation: _none_
- Test: `test:MemoryPolicyValidationTests`
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0052 - canonical:SETUP-00#7c.10

- Source reference: docs/SETUP-00-CHECKLIST.md row 7c.10
- Description: Every completed Gate produces a retrospective.
- Implementation: `file:.iacode/templates/retrospective/TEMPLATE.md`
- Test: _none_
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0053 - canonical:SETUP-00#7d.1

- Source reference: docs/SETUP-00-CHECKLIST.md row 7d.1
- Description: One promotion invariant governs every positive terminal status, not only `READY_FOR_REVIEW`.
- Implementation: `file:scripts/development-ledger/validate_checkpoint.py`
- Test: `test:PromotionInvariantTests`
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0054 - canonical:SETUP-00#7d.2

- Source reference: docs/SETUP-00-CHECKLIST.md row 7d.2
- Description: The mandatory quality gate set is a closed machine-readable registry that an invocation cannot narrow.
- Implementation: `file:.iacode/policies/quality-gates.json`, `file:scripts/development-ledger/green_keeper.py`
- Test: `test:MandatoryGatePolicyTests`
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0055 - canonical:SETUP-00#7d.3

- Source reference: docs/SETUP-00-CHECKLIST.md row 7d.3
- Description: The expected requirement set is derived from canonical sources and compared exactly with the declared set.
- Implementation: `file:.iacode/policies/canonical-requirements.json`, `file:scripts/development-ledger/policies.py`
- Test: `test:ExpectedRequirementSetTests`
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0056 - canonical:SETUP-00#7d.4

- Source reference: docs/SETUP-00-CHECKLIST.md row 7d.4
- Description: An external milestone PASS is derived from an audit attestation authored by another sealed checkpoint.
- Implementation: `file:scripts/development-ledger/attestation.py`
- Test: `test:ExternalAttestationTests`
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0057 - canonical:SETUP-00#7d.5

- Source reference: docs/SETUP-00-CHECKLIST.md row 7d.5
- Description: A derived artifact carries a fingerprint of its inputs, and staleness is decided by recomputation.
- Implementation: `file:scripts/development-ledger/lesson_preflight.py`, `checkpoint:LESSON-PREFLIGHT.json`
- Test: `test:PreflightFreshnessTests`
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0058 - canonical:SETUP-00#7d.6

- Source reference: docs/SETUP-00-CHECKLIST.md row 7d.6
- Description: Every lesson control, evidence path and provenance locator is resolved against the repository.
- Implementation: `file:scripts/development-ledger/lessons.py`
- Test: `test:LessonResolutionTests`, `test:LessonProvenanceTests`
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0059 - canonical:SETUP-00#7d.7

- Source reference: docs/SETUP-00-CHECKLIST.md row 7d.7
- Description: Every `GUARDED` lesson names a registered guardrail, and guardrail effectiveness is measured.
- Implementation: `file:.iacode/memory/guardrails/registry.json`
- Test: `test:GuardrailRegistryTests`, `test:GuardrailEffectivenessGateTests`
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0060 - canonical:SETUP-00#7d.8

- Source reference: docs/SETUP-00-CHECKLIST.md row 7d.8
- Description: Sealed checkpoints are anchored by a hash-linked chain over tag, commit and tree.
- Implementation: `file:.iacode/anchors/checkpoint-chain.json`, `file:scripts/development-ledger/anchors.py`
- Test: `test:IntegrityAnchorTests`
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0061 - canonical:SETUP-00#7d.9

- Source reference: docs/SETUP-00-CHECKLIST.md row 7d.9
- Description: Every count used as evidence is derived once and verified wherever a report states it.
- Implementation: `file:scripts/development-ledger/derive_counts.py`
- Test: `test:DerivedCountTests`
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0062 - canonical:SETUP-00#7d.10

- Source reference: docs/SETUP-00-CHECKLIST.md row 7d.10
- Description: Sealing is monotonic and post-commit, and every recorded command binds its declared inputs by content.
- Implementation: `file:scripts/development-ledger/seal_checkpoint.py`
- Test: `test:SealChronologyTests`, `test:CommandInputBindingTests`
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0063 - canonical:SETUP-00#7d.11

- Source reference: docs/SETUP-00-CHECKLIST.md row 7d.11
- Description: A milestone delivery carries an internal Red Team and an internal mirror audit, and neither is recorded as external validation.
- Implementation: `file:scripts/development-ledger/m0_red_team.py`, `file:.iacode/agents/m0-closure-auditor.md`
- Test: `test:InternalAssuranceTests`, `test:AuditSourceParsingTests`
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0064 - canonical:SETUP-00#7d.12

- Source reference: docs/SETUP-00-CHECKLIST.md row 7d.12
- Description: Every finding of an independent audit is closed before the corrective delivery is offered.
- Implementation: `file:.iacode/policies/audit-registry.json`, `checkpoint:CP7-FINDINGS-CLOSURE.json`
- Test: `test:FindingsClosureTests`
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0065 - canonical:SETUP-00#8.1

- Source reference: docs/SETUP-00-CHECKLIST.md row 8.1
- Description: An independent review is recorded.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0066 - canonical:SETUP-00#8.2

- Source reference: docs/SETUP-00-CHECKLIST.md row 8.2
- Description: An adversarial Red Team is recorded.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0067 - canonical:SETUP-00#8.3

- Source reference: docs/SETUP-00-CHECKLIST.md row 8.3
- Description: `GATE_PASS` is granted only by a run independent of the implementer.
- Implementation: `checkpoint:STATE.json`, `file:docs/QUALITY-GATES.md`
- Test: _none_
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0068 - canonical:SETUP-00#9.1

- Source reference: docs/SETUP-00-CHECKLIST.md row 9.1
- Description: No Gate 0 or later runtime is implemented during SETUP-00.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0069 - canonical:SETUP-00#9.2

- Source reference: docs/SETUP-00-CHECKLIST.md row 9.2
- Description: Documentation is maintained continuously rather than reconstructed at the end.
- Implementation: `checkpoint:COMMANDS.jsonl`, `checkpoint:DECISIONS.md`
- Test: _none_
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0070 - canonical:SETUP-00#9.3

- Source reference: docs/SETUP-00-CHECKLIST.md row 9.3
- Description: No secret, credential, or private chain-of-thought is stored.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0071 - canonical:SETUP-00#9.4

- Source reference: docs/SETUP-00-CHECKLIST.md row 9.4
- Description: Gate advancement requires explicit authorization and a passing previous Gate.
- Implementation: `file:docs/MASTER-PLAN.md`, `checkpoint:NEXT.md`
- Test: _none_
- Negative test: _none_
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0072 - finding:M0-F-001

- Source reference: M0-CP-0007 docs/checkpoints/SETUP-00-CP-0007/REVIEW-REPORT.md M0-F-001
- Description: positive terminal status bypasses delivery assurance
- Implementation: `file:scripts/development-ledger/validate_checkpoint.py`
- Test: `test:PromotionInvariantTests.test_every_positive_status_rejects_a_red_green_keeper`, `test:PromotionInvariantTests.test_every_positive_status_rejects_a_red_completeness_gate`
- Negative test: `test:PromotionInvariantTests.test_every_positive_status_rejects_every_red_quality_dimension`, `test:PromotionInvariantTests.test_every_positive_status_rejects_an_unexecuted_mandatory_dimension`, `test:PromotionInvariantTests.test_every_positive_status_rejects_a_partial_requirement`
- Documentation: `file:docs/adr/ADR-0010-milestone-closure-controls.md`, `checkpoint:CP7-FINDINGS-CLOSURE.md`
- Validation: `checkpoint:CP7-FINDINGS-CLOSURE.json`
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### REQ-0073 - finding:M0-F-002

- Source reference: M0-CP-0007 docs/checkpoints/SETUP-00-CP-0007/REVIEW-REPORT.md M0-F-002
- Description: external milestone PASS can be self-asserted on an intermediate Gate
- Implementation: `file:scripts/development-ledger/attestation.py`, `file:.iacode/schemas/external-audit-attestation.schema.json`
- Test: `test:ExternalAttestationTests.test_an_implementer_checkpoint_cannot_declare_an_external_pass`, `test:ExternalAttestationTests.test_second_tool_validation_alone_is_not_enough`
- Negative test: `test:ExternalAttestationTests.test_an_attestation_naming_the_subject_as_its_own_auditor_is_rejected`, `test:ExternalAttestationTests.test_a_failed_review_cannot_produce_an_external_pass`, `test:ExternalAttestationTests.test_a_failed_red_team_cannot_produce_an_external_pass`, `test:ExternalAttestationTests.test_an_intermediate_gate_cannot_take_the_external_status`
- Documentation: `file:docs/adr/ADR-0010-milestone-closure-controls.md`, `checkpoint:CP7-FINDINGS-CLOSURE.md`
- Validation: `checkpoint:CP7-FINDINGS-CLOSURE.json`
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### REQ-0074 - finding:M0-F-003

- Source reference: M0-CP-0007 docs/checkpoints/SETUP-00-CP-0007/REVIEW-REPORT.md M0-F-003
- Description: lesson preflight is not bound to the checkpoint Gate or canonical memory
- Implementation: `file:scripts/development-ledger/lessons.py`
- Test: `test:PreflightFreshnessTests.test_a_changed_fingerprint_makes_the_preflight_stale`, `test:PreflightFreshnessTests.test_a_preflight_from_another_gate_is_refused`
- Negative test: `test:PreflightFreshnessTests.test_a_dropped_lesson_makes_the_preflight_stale`, `test:PreflightFreshnessTests.test_the_checkpoint_refuses_a_stale_preflight`
- Documentation: `file:docs/adr/ADR-0010-milestone-closure-controls.md`, `checkpoint:CP7-FINDINGS-CLOSURE.md`
- Validation: `checkpoint:CP7-FINDINGS-CLOSURE.json`
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### REQ-0075 - finding:M0-F-004

- Source reference: M0-CP-0007 docs/checkpoints/SETUP-00-CP-0007/REVIEW-REPORT.md M0-F-004
- Description: Engineering Memory accepts forged controls, missing evidence, and nested secrets
- Implementation: `file:scripts/development-ledger/lessons.py`
- Test: `test:LessonResolutionTests.test_a_test_control_must_exist_in_the_suite`, `test:LessonResolutionTests.test_lesson_evidence_must_resolve`
- Negative test: `test:LessonResolutionTests.test_an_invariant_control_must_be_defined_in_the_tooling`, `test:LessonResolutionTests.test_a_control_path_may_not_escape_the_repository`, `test:LessonValidationTests.test_secret_in_a_lesson_fails`
- Documentation: `file:docs/adr/ADR-0010-milestone-closure-controls.md`, `checkpoint:CP7-FINDINGS-CLOSURE.md`
- Validation: `checkpoint:CP7-FINDINGS-CLOSURE.json`
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### REQ-0076 - finding:M0-F-005

- Source reference: M0-CP-0007 docs/checkpoints/SETUP-00-CP-0007/REVIEW-REPORT.md M0-F-005
- Description: Green Keeper has a vacuous PASS path
- Implementation: `file:.iacode/policies/quality-gates.json`, `file:scripts/development-ledger/green_keeper.py`
- Test: `test:MandatoryGatePolicyTests.test_a_cycle_measured_against_no_gate_is_rejected`, `test:MandatoryGatePolicyTests.test_the_policy_declares_a_non_empty_closed_set`
- Negative test: `test:MandatoryGatePolicyTests.test_a_cycle_missing_one_mandatory_gate_is_rejected`, `test:MandatoryGatePolicyTests.test_a_mandatory_gate_that_exited_nonzero_is_rejected`, `test:MandatoryGatePolicyTests.test_a_gate_without_command_evidence_is_rejected`
- Documentation: `file:docs/adr/ADR-0010-milestone-closure-controls.md`, `checkpoint:CP7-FINDINGS-CLOSURE.md`
- Validation: `checkpoint:CP7-FINDINGS-CLOSURE.json`
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### REQ-0077 - finding:M0-F-006

- Source reference: M0-CP-0007 docs/checkpoints/SETUP-00-CP-0007/REVIEW-REPORT.md M0-F-006
- Description: completeness denominator is not anchored
- Implementation: `file:scripts/development-ledger/policies.py`, `file:.iacode/policies/canonical-requirements.json`
- Test: `test:ExpectedRequirementSetTests.test_deleting_a_requirement_and_recomputing_the_counts_still_fails`, `test:ExpectedRequirementSetTests.test_the_expected_set_is_derived_from_the_canonical_sources`
- Negative test: `test:ExpectedRequirementSetTests.test_an_unexpected_anchored_requirement_is_rejected`, `test:ExpectedRequirementSetTests.test_a_requirement_without_an_anchor_is_rejected`, `test:ExpectedRequirementSetTests.test_a_downgraded_matrix_cannot_escape_the_comparison`
- Documentation: `file:docs/adr/ADR-0010-milestone-closure-controls.md`, `checkpoint:CP7-FINDINGS-CLOSURE.md`
- Validation: `checkpoint:CP7-FINDINGS-CLOSURE.json`
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### REQ-0078 - finding:M0-F-007

- Source reference: M0-CP-0007 docs/checkpoints/SETUP-00-CP-0007/REVIEW-REPORT.md M0-F-007
- Description: historical immutability is not anchored externally
- Implementation: `file:scripts/development-ledger/anchors.py`, `file:.iacode/anchors/checkpoint-chain.json`, `file:scripts/development-ledger/verify_integrity.py`
- Test: `test:IntegrityAnchorTests.test_a_moved_historical_tag_is_detected`, `test:IntegrityAnchorTests.test_an_unexpected_tree_is_detected`
- Negative test: `test:IntegrityAnchorTests.test_a_broken_link_between_anchors_is_detected`, `test:IntegrityAnchorTests.test_a_recomputed_anchor_hash_must_match_its_fields`, `test:IntegrityAnchorTests.test_a_sealed_checkpoint_without_an_anchor_is_detected`
- Documentation: `file:docs/adr/ADR-0010-milestone-closure-controls.md`, `checkpoint:CP7-FINDINGS-CLOSURE.md`
- Validation: `checkpoint:CP7-FINDINGS-CLOSURE.json`
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### REQ-0079 - finding:M0-F-008

- Source reference: M0-CP-0007 docs/checkpoints/SETUP-00-CP-0007/REVIEW-REPORT.md M0-F-008
- Description: CP-0006 mandatory count is contradictory and accepted
- Implementation: `file:scripts/development-ledger/derive_counts.py`
- Test: `test:ExpectedRequirementSetTests.test_the_state_mandatory_count_is_cross_checked`, `test:DerivedCountTests.test_the_stored_counts_match_the_derivation`
- Negative test: `test:DerivedCountTests.test_a_forged_count_is_rejected`, `test:DerivedCountTests.test_a_markdown_claim_that_contradicts_the_derivation_is_rejected`
- Documentation: `file:docs/adr/ADR-0010-milestone-closure-controls.md`, `checkpoint:CP7-FINDINGS-CLOSURE.md`
- Validation: `checkpoint:CP7-FINDINGS-CLOSURE.json`
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### REQ-0080 - finding:M0-F-009

- Source reference: M0-CP-0007 docs/checkpoints/SETUP-00-CP-0007/REVIEW-REPORT.md M0-F-009
- Description: command records are not reproducible at their declared commits
- Implementation: `file:scripts/development-ledger/ledger_common.py`
- Test: `test:CommandInputBindingTests.test_a_bound_record_passes`, `test:CommandInputBindingTests.test_the_recorder_binds_inputs_automatically`
- Negative test: `test:CommandInputBindingTests.test_a_record_without_a_digest_is_rejected`, `test:CommandInputBindingTests.test_a_digest_that_omits_an_input_is_rejected`, `test:CommandInputBindingTests.test_a_clean_tree_claim_is_checked_against_the_declared_commit`
- Documentation: `file:docs/adr/ADR-0010-milestone-closure-controls.md`, `checkpoint:CP7-FINDINGS-CLOSURE.md`
- Validation: `checkpoint:CP7-FINDINGS-CLOSURE.json`
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### REQ-0081 - finding:M0-F-010

- Source reference: M0-CP-0007 docs/checkpoints/SETUP-00-CP-0007/REVIEW-REPORT.md M0-F-010
- Description: sealed finalization chronology is internally inconsistent
- Implementation: `file:scripts/development-ledger/seal_checkpoint.py`
- Test: `test:SealChronologyTests.test_a_record_after_the_end_of_the_run_is_rejected`, `test:DeliveryLifecycleTests.test_full_delivery_assurance_flow_reaches_ready_for_review`
- Negative test: `test:SealChronologyTests.test_a_missing_post_commit_validation_is_rejected`, `test:SealChronologyTests.test_a_dirty_tree_validation_is_not_evidence_of_a_sealed_commit`, `test:SealChronologyTests.test_a_validation_of_an_unrelated_commit_is_rejected`
- Documentation: `file:docs/adr/ADR-0010-milestone-closure-controls.md`, `checkpoint:CP7-FINDINGS-CLOSURE.md`
- Validation: `checkpoint:CP7-FINDINGS-CLOSURE.json`
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### REQ-0082 - finding:M0-F-011

- Source reference: M0-CP-0007 docs/checkpoints/SETUP-00-CP-0007/REVIEW-REPORT.md M0-F-011
- Description: one lesson source locator is inaccurate
- Implementation: `file:.iacode/memory/lessons.jsonl`
- Test: `test:LessonProvenanceTests.test_every_repository_lesson_cites_a_resolvable_source`, `test:LessonProvenanceTests.test_a_correct_locator_resolves`
- Negative test: `test:LessonProvenanceTests.test_a_finding_absent_from_the_cited_checkpoint_is_rejected`, `test:LessonProvenanceTests.test_a_nonexistent_checkpoint_is_rejected`
- Documentation: `file:docs/adr/ADR-0010-milestone-closure-controls.md`, `checkpoint:CP7-FINDINGS-CLOSURE.md`
- Validation: `checkpoint:CP7-FINDINGS-CLOSURE.json`
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### REQ-0083 - attack:A

- Source reference: M0-CP-0007 docs/checkpoints/SETUP-00-CP-0007/RED-TEAM-REPORT.md attack A
- Description: Defend attack A: Add blocker to `READY_FOR_REVIEW`
- Implementation: `file:scripts/development-ledger/m0_red_team.py`
- Test: `test:StatusBlockerInvariantTests.test_ready_for_review_with_blocker_fails`
- Negative test: `test:StatusBlockerInvariantTests.test_ready_for_review_with_blocker_fails`
- Documentation: `file:docs/adr/ADR-0010-milestone-closure-controls.md`
- Validation: `checkpoint:CP7-FINDINGS-CLOSURE.json`
- Guardrail: _none_

### REQ-0084 - attack:B

- Source reference: M0-CP-0007 docs/checkpoints/SETUP-00-CP-0007/RED-TEAM-REPORT.md attack B
- Description: Defend attack B: Set a review-ready quality gate red
- Implementation: `file:scripts/development-ledger/m0_red_team.py`
- Test: `test:DeliveryAssuranceGateTests.test_red_tests_block_review`
- Negative test: `test:DeliveryAssuranceGateTests.test_red_tests_block_review`
- Documentation: `file:docs/adr/ADR-0010-milestone-closure-controls.md`
- Validation: `checkpoint:CP7-FINDINGS-CLOSURE.json`
- Guardrail: _none_

### REQ-0085 - attack:C

- Source reference: M0-CP-0007 docs/checkpoints/SETUP-00-CP-0007/RED-TEAM-REPORT.md attack C
- Description: Defend attack C: Delete mandatory `REQ-0001` and recompute all counts
- Implementation: `file:scripts/development-ledger/m0_red_team.py`
- Test: `test:ExpectedRequirementSetTests.test_deleting_a_requirement_and_recomputing_the_counts_still_fails`
- Negative test: `test:ExpectedRequirementSetTests.test_deleting_a_requirement_and_recomputing_the_counts_still_fails`
- Documentation: `file:docs/adr/ADR-0010-milestone-closure-controls.md`
- Validation: `checkpoint:CP7-FINDINGS-CLOSURE.json`
- Guardrail: _none_

### REQ-0086 - attack:D

- Source reference: M0-CP-0007 docs/checkpoints/SETUP-00-CP-0007/RED-TEAM-REPORT.md attack D
- Description: Defend attack D: Forge stored 100% counts
- Implementation: `file:scripts/development-ledger/m0_red_team.py`
- Test: `test:DeliveryAssuranceGateTests.test_completeness_report_inconsistent_with_the_matrix_is_rejected`
- Negative test: `test:DeliveryAssuranceGateTests.test_completeness_report_inconsistent_with_the_matrix_is_rejected`
- Documentation: `file:docs/adr/ADR-0010-milestone-closure-controls.md`
- Validation: `checkpoint:CP7-FINDINGS-CLOSURE.json`
- Guardrail: _none_

### REQ-0087 - attack:E

- Source reference: M0-CP-0007 docs/checkpoints/SETUP-00-CP-0007/RED-TEAM-REPORT.md attack E
- Description: Defend attack E: Remove a derived requirement
- Implementation: `file:scripts/development-ledger/m0_red_team.py`
- Test: `test:DerivedRequirementCompletenessTests.test_a_missing_derived_requirement_blocks_completeness`
- Negative test: `test:DerivedRequirementCompletenessTests.test_a_missing_derived_requirement_blocks_completeness`
- Documentation: `file:docs/adr/ADR-0010-milestone-closure-controls.md`
- Validation: `checkpoint:CP7-FINDINGS-CLOSURE.json`
- Guardrail: _none_

### REQ-0088 - attack:F

- Source reference: M0-CP-0007 docs/checkpoints/SETUP-00-CP-0007/RED-TEAM-REPORT.md attack F
- Description: Defend attack F: Replace prevention with documentation only
- Implementation: `file:scripts/development-ledger/m0_red_team.py`
- Test: `test:LessonValidationTests.test_documentation_alone_does_not_guard_a_lesson`
- Negative test: `test:LessonValidationTests.test_documentation_alone_does_not_guard_a_lesson`
- Documentation: `file:docs/adr/ADR-0010-milestone-closure-controls.md`
- Validation: `checkpoint:CP7-FINDINGS-CLOSURE.json`
- Guardrail: _none_

### REQ-0089 - attack:G

- Source reference: M0-CP-0007 docs/checkpoints/SETUP-00-CP-0007/RED-TEAM-REPORT.md attack G
- Description: Defend attack G: Duplicate lesson ID
- Implementation: `file:scripts/development-ledger/m0_red_team.py`
- Test: `test:LessonValidationTests.test_duplicate_lesson_id_fails`
- Negative test: `test:LessonValidationTests.test_duplicate_lesson_id_fails`
- Documentation: `file:docs/adr/ADR-0010-milestone-closure-controls.md`
- Validation: `checkpoint:CP7-FINDINGS-CLOSURE.json`
- Guardrail: _none_

### REQ-0090 - attack:H

- Source reference: M0-CP-0007 docs/checkpoints/SETUP-00-CP-0007/RED-TEAM-REPORT.md attack H
- Description: Defend attack H: Insert a secret-shaped value in a scanned field
- Implementation: `file:scripts/development-ledger/m0_red_team.py`
- Test: `test:LessonValidationTests.test_secret_in_a_lesson_fails`
- Negative test: `test:LessonValidationTests.test_secret_in_a_lesson_fails`
- Documentation: `file:docs/adr/ADR-0010-milestone-closure-controls.md`
- Validation: `checkpoint:CP7-FINDINGS-CLOSURE.json`
- Guardrail: _none_

### REQ-0091 - attack:I

- Source reference: M0-CP-0007 docs/checkpoints/SETUP-00-CP-0007/RED-TEAM-REPORT.md attack I
- Description: Defend attack I: Rewrite CP-0005, declare it in CP-0006 inventory, refresh hashes, move CP-0006 tag
- Implementation: `file:scripts/development-ledger/m0_red_team.py`
- Test: `test:IntegrityAnchorTests.test_an_unexpected_tree_is_detected`
- Negative test: `test:IntegrityAnchorTests.test_an_unexpected_tree_is_detected`
- Documentation: `file:docs/adr/ADR-0010-milestone-closure-controls.md`
- Validation: `checkpoint:CP7-FINDINGS-CLOSURE.json`
- Guardrail: _none_

### REQ-0092 - attack:J

- Source reference: M0-CP-0007 docs/checkpoints/SETUP-00-CP-0007/RED-TEAM-REPORT.md attack J
- Description: Defend attack J: Move CP-0006 tag and HEAD together to a new commit
- Implementation: `file:scripts/development-ledger/m0_red_team.py`
- Test: `test:IntegrityAnchorTests.test_a_moved_historical_tag_is_detected`
- Negative test: `test:IntegrityAnchorTests.test_a_moved_historical_tag_is_detected`
- Documentation: `file:docs/adr/ADR-0010-milestone-closure-controls.md`
- Validation: `checkpoint:CP7-FINDINGS-CLOSURE.json`
- Guardrail: _none_

### REQ-0093 - attack:K

- Source reference: M0-CP-0007 docs/checkpoints/SETUP-00-CP-0007/RED-TEAM-REPORT.md attack K
- Description: Defend attack K: Remove one inventory entry
- Implementation: `file:scripts/development-ledger/m0_red_team.py`
- Test: `test:DeltaInventoryTests.test_removed_manifest_entry_fails`
- Negative test: `test:DeltaInventoryTests.test_removed_manifest_entry_fails`
- Documentation: `file:docs/adr/ADR-0010-milestone-closure-controls.md`
- Validation: `checkpoint:CP7-FINDINGS-CLOSURE.json`
- Guardrail: _none_

### REQ-0094 - attack:L

- Source reference: M0-CP-0007 docs/checkpoints/SETUP-00-CP-0007/RED-TEAM-REPORT.md attack L
- Description: Defend attack L: Silently modify a tracked file
- Implementation: `file:scripts/development-ledger/m0_red_team.py`
- Test: `test:DeltaInventoryTests.test_silent_tracked_modification_fails`
- Negative test: `test:DeltaInventoryTests.test_silent_tracked_modification_fails`
- Documentation: `file:docs/adr/ADR-0010-milestone-closure-controls.md`
- Validation: `checkpoint:CP7-FINDINGS-CLOSURE.json`
- Guardrail: _none_

### REQ-0095 - attack:M

- Source reference: M0-CP-0007 docs/checkpoints/SETUP-00-CP-0007/RED-TEAM-REPORT.md attack M
- Description: Defend attack M: Set a wrong `hashBefore`
- Implementation: `file:scripts/development-ledger/m0_red_team.py`
- Test: `test:DeltaInventoryTests.test_wrong_hash_before_fails`
- Negative test: `test:DeltaInventoryTests.test_wrong_hash_before_fails`
- Documentation: `file:docs/adr/ADR-0010-milestone-closure-controls.md`
- Validation: `checkpoint:CP7-FINDINGS-CLOSURE.json`
- Guardrail: _none_

### REQ-0096 - attack:N

- Source reference: M0-CP-0007 docs/checkpoints/SETUP-00-CP-0007/RED-TEAM-REPORT.md attack N
- Description: Defend attack N: Set a wrong `hashAfter`
- Implementation: `file:scripts/development-ledger/m0_red_team.py`
- Test: `test:DeltaInventoryTests.test_wrong_hash_after_fails`
- Negative test: `test:DeltaInventoryTests.test_wrong_hash_after_fails`
- Documentation: `file:docs/adr/ADR-0010-milestone-closure-controls.md`
- Validation: `checkpoint:CP7-FINDINGS-CLOSURE.json`
- Guardrail: _none_

### REQ-0097 - attack:O

- Source reference: M0-CP-0007 docs/checkpoints/SETUP-00-CP-0007/RED-TEAM-REPORT.md attack O
- Description: Defend attack O: Claim PASS with no evidence
- Implementation: `file:scripts/development-ledger/m0_red_team.py`
- Test: `test:QualityEvidenceTests.test_pass_without_evidence_fails`
- Negative test: `test:QualityEvidenceTests.test_pass_without_evidence_fails`
- Documentation: `file:docs/adr/ADR-0010-milestone-closure-controls.md`
- Validation: `checkpoint:CP7-FINDINGS-CLOSURE.json`
- Guardrail: _none_

### REQ-0098 - attack:P

- Source reference: M0-CP-0007 docs/checkpoints/SETUP-00-CP-0007/RED-TEAM-REPORT.md attack P
- Description: Defend attack P: Reference an unknown command
- Implementation: `file:scripts/development-ledger/m0_red_team.py`
- Test: `test:QualityEvidenceTests.test_pass_referencing_an_unknown_command_fails`
- Negative test: `test:QualityEvidenceTests.test_pass_referencing_an_unknown_command_fails`
- Documentation: `file:docs/adr/ADR-0010-milestone-closure-controls.md`
- Validation: `checkpoint:CP7-FINDINGS-CLOSURE.json`
- Guardrail: _none_

### REQ-0099 - attack:Q

- Source reference: M0-CP-0007 docs/checkpoints/SETUP-00-CP-0007/RED-TEAM-REPORT.md attack Q
- Description: Defend attack Q: Supply arbitrary complete attribution with empty evidence
- Implementation: `file:scripts/development-ledger/m0_red_team.py`
- Test: `test:ExternalAttestationTests.test_second_tool_validation_alone_is_not_enough`
- Negative test: `test:ExternalAttestationTests.test_second_tool_validation_alone_is_not_enough`
- Documentation: `file:docs/adr/ADR-0010-milestone-closure-controls.md`
- Validation: `checkpoint:CP7-FINDINGS-CLOSURE.json`
- Guardrail: _none_

### REQ-0100 - attack:R

- Source reference: M0-CP-0007 docs/checkpoints/SETUP-00-CP-0007/RED-TEAM-REPORT.md attack R
- Description: Defend attack R: Promote an internally authored result to external status
- Implementation: `file:scripts/development-ledger/m0_red_team.py`
- Test: `test:ExternalAttestationTests.test_an_implementer_checkpoint_cannot_declare_an_external_pass`
- Negative test: `test:ExternalAttestationTests.test_an_implementer_checkpoint_cannot_declare_an_external_pass`
- Documentation: `file:docs/adr/ADR-0010-milestone-closure-controls.md`
- Validation: `checkpoint:CP7-FINDINGS-CLOSURE.json`
- Guardrail: _none_

### REQ-0101 - attack:S

- Source reference: M0-CP-0007 docs/checkpoints/SETUP-00-CP-0007/RED-TEAM-REPORT.md attack S
- Description: Defend attack S: Leave review/Red Team pending and auditor/time null
- Implementation: `file:scripts/development-ledger/m0_red_team.py`
- Test: `test:ExternalAttestationTests.test_a_failed_review_cannot_produce_an_external_pass`
- Negative test: `test:ExternalAttestationTests.test_a_failed_review_cannot_produce_an_external_pass`
- Documentation: `file:docs/adr/ADR-0010-milestone-closure-controls.md`
- Validation: `checkpoint:CP7-FINDINGS-CLOSURE.json`
- Guardrail: _none_

### REQ-0102 - attack:T

- Source reference: M0-CP-0007 docs/checkpoints/SETUP-00-CP-0007/RED-TEAM-REPORT.md attack T
- Description: Defend attack T: Request audit without a known trigger
- Implementation: `file:scripts/development-ledger/m0_red_team.py`
- Test: `test:MemoryPolicyValidationTests.test_an_extraordinary_audit_requires_a_recorded_trigger`
- Negative test: `test:MemoryPolicyValidationTests.test_an_extraordinary_audit_requires_a_recorded_trigger`
- Documentation: `file:docs/adr/ADR-0010-milestone-closure-controls.md`
- Validation: `checkpoint:CP7-FINDINGS-CLOSURE.json`
- Guardrail: _none_

### REQ-0103 - attack:U

- Source reference: M0-CP-0007 docs/checkpoints/SETUP-00-CP-0007/RED-TEAM-REPORT.md attack U
- Description: Defend attack U: Retire canonical lesson but keep stale active preflight
- Implementation: `file:scripts/development-ledger/m0_red_team.py`
- Test: `test:PreflightFreshnessTests.test_a_dropped_lesson_makes_the_preflight_stale`
- Negative test: `test:PreflightFreshnessTests.test_a_dropped_lesson_makes_the_preflight_stale`
- Documentation: `file:docs/adr/ADR-0010-milestone-closure-controls.md`
- Validation: `checkpoint:CP7-FINDINGS-CLOSURE.json`
- Guardrail: _none_

### REQ-0104 - attack:V

- Source reference: M0-CP-0007 docs/checkpoints/SETUP-00-CP-0007/RED-TEAM-REPORT.md attack V
- Description: Defend attack V: Run `--gates ""`, then retain PASS with an actually failing test
- Implementation: `file:scripts/development-ledger/m0_red_team.py`
- Test: `test:MandatoryGatePolicyTests.test_a_cycle_measured_against_no_gate_is_rejected`
- Negative test: `test:MandatoryGatePolicyTests.test_a_cycle_measured_against_no_gate_is_rejected`
- Documentation: `file:docs/adr/ADR-0010-milestone-closure-controls.md`
- Validation: `checkpoint:CP7-FINDINGS-CLOSURE.json`
- Guardrail: _none_

### REQ-0105 - attack:W

- Source reference: M0-CP-0007 docs/checkpoints/SETUP-00-CP-0007/RED-TEAM-REPORT.md attack W
- Description: Defend attack W: Claim PASS with a PARTIAL row
- Implementation: `file:scripts/development-ledger/m0_red_team.py`
- Test: `test:DeliveryCompletenessMatrixTests.test_partial_requirement_fails`
- Negative test: `test:DeliveryCompletenessMatrixTests.test_partial_requirement_fails`
- Documentation: `file:docs/adr/ADR-0010-milestone-closure-controls.md`
- Validation: `checkpoint:CP7-FINDINGS-CLOSURE.json`
- Guardrail: _none_

### REQ-0106 - attack:X

- Source reference: M0-CP-0007 docs/checkpoints/SETUP-00-CP-0007/RED-TEAM-REPORT.md attack X
- Description: Defend attack X: Remove required runtime/record field
- Implementation: `file:scripts/development-ledger/m0_red_team.py`
- Test: `test:CommandReproducibilityTests.test_missing_runtime_fails`
- Negative test: `test:CommandReproducibilityTests.test_missing_runtime_fails`
- Documentation: `file:docs/adr/ADR-0010-milestone-closure-controls.md`
- Validation: `checkpoint:CP7-FINDINGS-CLOSURE.json`
- Guardrail: _none_

### REQ-0107 - attack:Y

- Source reference: M0-CP-0007 docs/checkpoints/SETUP-00-CP-0007/RED-TEAM-REPORT.md attack Y
- Description: Defend attack Y: Point `LATEST.md` at CP-0005 while validating CP-0006
- Implementation: `file:scripts/development-ledger/m0_red_team.py`
- Test: `test:LedgerValidationTests.test_latest_to_nonexistent_checkpoint_fails`
- Negative test: `test:LedgerValidationTests.test_latest_to_nonexistent_checkpoint_fails`
- Documentation: `file:docs/adr/ADR-0010-milestone-closure-controls.md`
- Validation: `checkpoint:CP7-FINDINGS-CLOSURE.json`
- Guardrail: _none_

### REQ-0108 - attack:Z

- Source reference: M0-CP-0007 docs/checkpoints/SETUP-00-CP-0007/RED-TEAM-REPORT.md attack Z
- Description: Defend attack Z: Use path traversal as checkpoint/Gate input
- Implementation: `file:scripts/development-ledger/m0_red_team.py`
- Test: `test:LedgerLifecycleTests.test_new_checkpoint_rejects_path_traversal_gate`
- Negative test: `test:LedgerLifecycleTests.test_new_checkpoint_rejects_path_traversal_gate`
- Documentation: `file:docs/adr/ADR-0010-milestone-closure-controls.md`
- Validation: `checkpoint:CP7-FINDINGS-CLOSURE.json`
- Guardrail: _none_

### LESSON-REQ-0001 - lesson:LSN-0001

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0001
- Description: Verify checkpoint validation must succeed from a detached checkout of the checkpoint tag
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:scripts/development-ledger/validate_checkpoint.py`
- Test: `test:DetachedHeadValidationTests.test_detached_head_at_checkpoint_tag_validates`, `test:DetachedHeadValidationTests.test_detached_head_at_wrong_commit_fails`
- Negative test: _none_
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/ENGINEERING-MEMORY.md`
- Validation: `checkpoint:LESSON-PREFLIGHT.json`
- Guardrail: `file:.iacode/memory/guardrails/registry.json`, `test:DetachedHeadValidationTests.test_detached_head_at_checkpoint_tag_validates`, `test:DetachedHeadValidationTests.test_detached_head_at_wrong_commit_fails`

### LESSON-REQ-0002 - lesson:LSN-0002

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0002
- Description: Verify a file inventory must be recomputed from the repository, never trusted as an assertion
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:scripts/development-ledger/validate_checkpoint.py`
- Test: `test:DeltaInventoryTests.test_removed_manifest_entry_fails`, `test:DeltaInventoryTests.test_silent_tracked_modification_fails`
- Negative test: _none_
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/ENGINEERING-MEMORY.md`
- Validation: `checkpoint:LESSON-PREFLIGHT.json`
- Guardrail: `file:.iacode/memory/guardrails/registry.json`, `test:DeltaInventoryTests.test_removed_manifest_entry_fails`, `test:DeltaInventoryTests.test_silent_tracked_modification_fails`

### LESSON-REQ-0003 - lesson:LSN-0003

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0003
- Description: Verify every operation attempt must be auditable, including a refusal decided before execution
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:scripts/development-ledger/finalize_checkpoint.py`
- Test: `test:FinalizationAttemptRecordingTests.test_detached_head_refusal_is_recorded`, `test:FinalizationAttemptRecordingTests.test_non_latest_checkpoint_refusal_is_recorded`
- Negative test: _none_
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/ENGINEERING-MEMORY.md`
- Validation: `checkpoint:LESSON-PREFLIGHT.json`
- Guardrail: `file:.iacode/memory/guardrails/registry.json`, `test:FinalizationAttemptRecordingTests.test_detached_head_refusal_is_recorded`, `test:FinalizationAttemptRecordingTests.test_non_latest_checkpoint_refusal_is_recorded`

### LESSON-REQ-0004 - lesson:LSN-0004

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0004
- Description: Verify a checkpoint may never claim readiness while it also claims to be blocked
- Implementation: `file:.iacode/memory/lessons.jsonl`
- Test: `test:StatusBlockerInvariantTests.test_ready_for_review_with_blocker_fails`, `test:ResealedBlockerFixtureTests.test_resealed_ready_for_review_with_blocker_is_rejected`
- Negative test: _none_
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/ENGINEERING-MEMORY.md`
- Validation: `checkpoint:LESSON-PREFLIGHT.json`
- Guardrail: `file:.iacode/memory/guardrails/registry.json`, `test:StatusBlockerInvariantTests.test_ready_for_review_with_blocker_fails`, `test:ResealedBlockerFixtureTests.test_resealed_ready_for_review_with_blocker_is_rejected`

### LESSON-REQ-0005 - lesson:LSN-0005

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0005
- Description: Verify a PASS requires evidence that can be executed or resolved, not a statement
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:scripts/development-ledger/validate_checkpoint.py`
- Test: `test:QualityEvidenceTests.test_pass_without_evidence_fails`, `test:QualityEvidenceTests.test_pass_referencing_a_failed_command_fails`, `test:PromotionInvariantTests.test_every_positive_status_rejects_every_red_quality_dimension`
- Negative test: _none_
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/ENGINEERING-MEMORY.md`
- Validation: `checkpoint:LESSON-PREFLIGHT.json`
- Guardrail: `file:.iacode/memory/guardrails/registry.json`, `test:QualityEvidenceTests.test_pass_without_evidence_fails`, `test:QualityEvidenceTests.test_pass_referencing_a_failed_command_fails`

### LESSON-REQ-0006 - lesson:LSN-0006

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0006
- Description: Verify the repository must be self-contained; a specification may not live outside it
- Implementation: `file:.iacode/memory/lessons.jsonl`
- Test: `test:SetupChecklistTests.test_checklist_exists_and_is_referenced`, `test:SetupChecklistTests.test_documentation_links_resolve`
- Negative test: _none_
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/ENGINEERING-MEMORY.md`
- Validation: `checkpoint:LESSON-PREFLIGHT.json`
- Guardrail: `file:.iacode/memory/guardrails/registry.json`, `test:SetupChecklistTests.test_checklist_exists_and_is_referenced`, `test:SetupChecklistTests.test_documentation_links_resolve`

### LESSON-REQ-0007 - lesson:LSN-0007

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0007
- Description: Verify independent validation cannot be declared by the run that did the work
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:.iacode/schemas/checkpoint.schema.json`, `file:scripts/development-ledger/attestation.py`
- Test: `test:SecondToolValidationTests.test_failed_cross_tool_validation_cannot_grant_gate_pass`, `test:DeliveryAssuranceGateTests.test_self_claimed_independent_review_blocks_review`, `test:ExternalAttestationTests.test_an_implementer_checkpoint_cannot_declare_an_external_pass`
- Negative test: _none_
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/ENGINEERING-MEMORY.md`
- Validation: `checkpoint:LESSON-PREFLIGHT.json`
- Guardrail: `file:.iacode/memory/guardrails/registry.json`, `test:ExternalAttestationTests.test_an_implementer_checkpoint_cannot_declare_an_external_pass`, `test:ExternalAttestationTests.test_an_attestation_naming_the_subject_as_its_own_auditor_is_rejected`, `test:ExternalAttestationTests.test_second_tool_validation_alone_is_not_enough`

### LESSON-REQ-0008 - lesson:LSN-0008

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0008
- Description: Verify requirement completeness must be total and evidence-backed before handoff
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:scripts/development-ledger/check_completeness.py`
- Test: `test:DeliveryCompletenessMatrixTests.test_one_requirement_short_of_total_fails`, `test:DeliveryAssuranceGateTests.test_completeness_validator_not_executed_blocks_review`, `test:ExpectedRequirementSetTests.test_deleting_a_requirement_and_recomputing_the_counts_still_fails`
- Negative test: _none_
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/ENGINEERING-MEMORY.md`
- Validation: `checkpoint:LESSON-PREFLIGHT.json`
- Guardrail: `file:.iacode/memory/guardrails/registry.json`, `test:ExpectedRequirementSetTests.test_deleting_a_requirement_and_recomputing_the_counts_still_fails`, `test:ExpectedRequirementSetTests.test_an_unexpected_anchored_requirement_is_rejected`

### LESSON-REQ-0009 - lesson:LSN-0009

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0009
- Description: Verify a red gate requires rework, never a waiver, and never a weakened check
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:.iacode/policies/quality-gates.json`
- Test: `test:GreenKeeperToolTests.test_red_gate_is_reported_as_still_red`, `test:DeliveryAssuranceGateTests.test_green_keeper_pass_with_a_real_failure_is_rejected`, `test:DeliveryAssuranceGateTests.test_red_tests_block_review`, `test:MandatoryGatePolicyTests.test_a_cycle_measured_against_no_gate_is_rejected`
- Negative test: _none_
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/ENGINEERING-MEMORY.md`
- Validation: `checkpoint:LESSON-PREFLIGHT.json`
- Guardrail: `file:.iacode/memory/guardrails/registry.json`, `test:MandatoryGatePolicyTests.test_a_cycle_measured_against_no_gate_is_rejected`, `test:MandatoryGatePolicyTests.test_the_policy_declares_a_non_empty_closed_set`

### LESSON-REQ-0010 - lesson:LSN-0010

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0010
- Description: Verify a recorded command must carry runtime, working directory, commit and purpose to be replayable
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:.iacode/schemas/command.schema.json`
- Test: `test:CommandReproducibilityTests.test_bare_script_name_is_rejected`, `test:CommandReproducibilityTests.test_unresolvable_script_path_is_rejected`, `test:CommandInputBindingTests.test_a_record_without_a_digest_is_rejected`
- Negative test: _none_
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/ENGINEERING-MEMORY.md`
- Validation: `checkpoint:LESSON-PREFLIGHT.json`
- Guardrail: `file:.iacode/memory/guardrails/registry.json`, `test:CommandInputBindingTests.test_a_record_without_a_digest_is_rejected`, `test:CommandInputBindingTests.test_a_clean_tree_claim_is_checked_against_the_declared_commit`

### LESSON-REQ-0011 - lesson:LSN-0011

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0011
- Description: Verify a control over a checkpoint's own evidence must be scoped to the moment it matters
- Implementation: `file:.iacode/memory/lessons.jsonl`
- Test: `test:DeliveryAssuranceGateTests.test_gate_consistency_is_provisional_while_work_is_in_progress`
- Negative test: _none_
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/ENGINEERING-MEMORY.md`
- Validation: `checkpoint:LESSON-PREFLIGHT.json`
- Guardrail: `file:.iacode/memory/guardrails/registry.json`, `test:DeliveryAssuranceGateTests.test_gate_consistency_is_provisional_while_work_is_in_progress`

### LESSON-REQ-0012 - lesson:LSN-0012

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0012
- Description: Verify sealed checkpoints and their tags are immutable, and tooling must keep validating them
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:docs/CHECKPOINT-PROTOCOL.md`, `file:scripts/development-ledger/anchors.py`
- Test: `test:HistoricalCheckpointCompatibilityTests.test_first_sealed_checkpoint_still_validates`, `test:HistoricalCheckpointCompatibilityTests.test_fourth_sealed_checkpoint_still_validates`, `test:IntegrityAnchorTests.test_a_moved_historical_tag_is_detected`
- Negative test: _none_
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/ENGINEERING-MEMORY.md`
- Validation: `checkpoint:LESSON-PREFLIGHT.json`
- Guardrail: `file:.iacode/memory/guardrails/registry.json`, `test:IntegrityAnchorTests.test_a_moved_historical_tag_is_detected`, `test:IntegrityAnchorTests.test_a_broken_link_between_anchors_is_detected`

### LESSON-REQ-0013 - lesson:LSN-0013

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0013
- Description: Verify an installed capability must be detected by resolved path, not by a bare command lookup
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:docs/TOOL-CAPABILITIES.md`
- Test: _none_
- Negative test: _none_
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/ENGINEERING-MEMORY.md`
- Validation: `checkpoint:LESSON-PREFLIGHT.json`
- Guardrail: _none_

### LESSON-REQ-0014 - lesson:LSN-0014

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0014
- Description: Verify evidence must be recorded as it happens, not reconstructed at the end of a run
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:scripts/development-ledger/record_command.py`
- Test: `test:SealChronologyTests.test_a_record_after_the_end_of_the_run_is_rejected`
- Negative test: _none_
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/ENGINEERING-MEMORY.md`
- Validation: `checkpoint:LESSON-PREFLIGHT.json`
- Guardrail: `file:.iacode/memory/guardrails/registry.json`, `test:SealChronologyTests.test_a_record_after_the_end_of_the_run_is_rejected`, `test:SealChronologyTests.test_a_missing_post_commit_validation_is_rejected`, `test:SealChronologyTests.test_a_dirty_tree_validation_is_not_evidence_of_a_sealed_commit`

### LESSON-REQ-0015 - lesson:LSN-0015

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0015
- Description: Verify every positive terminal status needs one shared promotion invariant
- Implementation: `file:.iacode/memory/lessons.jsonl`
- Test: `test:PromotionInvariantTests.test_every_positive_status_rejects_a_red_green_keeper`
- Negative test: _none_
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/ENGINEERING-MEMORY.md`
- Validation: `checkpoint:LESSON-PREFLIGHT.json`
- Guardrail: `file:.iacode/memory/guardrails/registry.json`, `test:PromotionInvariantTests.test_every_positive_status_rejects_a_red_green_keeper`, `test:PromotionInvariantTests.test_every_positive_status_rejects_every_red_quality_dimension`, `test:PromotionInvariantTests.test_a_terminal_status_requires_an_independent_verdict`

### LESSON-REQ-0016 - lesson:LSN-0016

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0016
- Description: Verify a mandatory set must be closed by policy, never chosen by the caller
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:.iacode/policies/quality-gates.json`
- Test: _none_
- Negative test: _none_
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/ENGINEERING-MEMORY.md`
- Validation: `checkpoint:LESSON-PREFLIGHT.json`
- Guardrail: `file:.iacode/memory/guardrails/registry.json`, `test:MandatoryGatePolicyTests.test_a_cycle_missing_one_mandatory_gate_is_rejected`, `test:MandatoryGatePolicyTests.test_a_mandatory_gate_that_exited_nonzero_is_rejected`, `test:MandatoryGatePolicyTests.test_a_pass_measured_before_a_source_change_is_stale`

### LESSON-REQ-0017 - lesson:LSN-0017

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0017
- Description: Verify a completeness denominator must come from a source the delivery does not own
- Implementation: `file:.iacode/memory/lessons.jsonl`
- Test: `test:ExpectedRequirementSetTests.test_an_unexpected_anchored_requirement_is_rejected`
- Negative test: _none_
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/ENGINEERING-MEMORY.md`
- Validation: `checkpoint:LESSON-PREFLIGHT.json`
- Guardrail: `file:.iacode/memory/guardrails/registry.json`, `test:ExpectedRequirementSetTests.test_the_expected_set_is_derived_from_the_canonical_sources`, `test:ExpectedRequirementSetTests.test_the_checklist_is_reparsed_rather_than_trusted`, `test:ExpectedRequirementSetTests.test_a_downgraded_matrix_cannot_escape_the_comparison`

### LESSON-REQ-0018 - lesson:LSN-0018

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0018
- Description: Verify a structured reference must be resolved, not merely well typed
- Implementation: `file:.iacode/memory/lessons.jsonl`
- Test: `test:LessonResolutionTests.test_a_test_control_must_exist_in_the_suite`
- Negative test: _none_
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/ENGINEERING-MEMORY.md`
- Validation: `checkpoint:LESSON-PREFLIGHT.json`
- Guardrail: `file:.iacode/memory/guardrails/registry.json`, `test:LessonResolutionTests.test_a_test_control_must_exist_in_the_suite`, `test:LessonResolutionTests.test_an_invariant_control_must_be_defined_in_the_tooling`, `test:LessonResolutionTests.test_lesson_evidence_must_resolve`

### LESSON-REQ-0019 - lesson:LSN-0019

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0019
- Description: Verify a derived artifact must carry a fingerprint of the inputs that produced it
- Implementation: `file:.iacode/memory/lessons.jsonl`
- Test: `test:PreflightFreshnessTests.test_a_dropped_lesson_makes_the_preflight_stale`
- Negative test: _none_
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/ENGINEERING-MEMORY.md`
- Validation: `checkpoint:LESSON-PREFLIGHT.json`
- Guardrail: `file:.iacode/memory/guardrails/registry.json`, `test:PreflightFreshnessTests.test_a_changed_fingerprint_makes_the_preflight_stale`, `test:PreflightFreshnessTests.test_a_dropped_lesson_makes_the_preflight_stale`, `test:PreflightFreshnessTests.test_a_preflight_from_another_gate_is_refused`

### LESSON-REQ-0020 - lesson:LSN-0020

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0020
- Description: Verify evidence produced from a dirty tree needs immutable input identity
- Implementation: `file:.iacode/memory/lessons.jsonl`
- Test: `test:CommandInputBindingTests.test_the_recorder_binds_inputs_automatically`
- Negative test: _none_
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/ENGINEERING-MEMORY.md`
- Validation: `checkpoint:LESSON-PREFLIGHT.json`
- Guardrail: `file:.iacode/memory/guardrails/registry.json`, `test:CommandInputBindingTests.test_the_recorder_binds_inputs_automatically`, `test:CommandInputBindingTests.test_a_digest_that_omits_an_input_is_rejected`

### LESSON-REQ-0021 - lesson:LSN-0021

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0021
- Description: Verify sealed history needs an anchor outside the content it describes
- Implementation: `file:.iacode/memory/lessons.jsonl`
- Test: `test:IntegrityAnchorTests.test_a_broken_link_between_anchors_is_detected`
- Negative test: _none_
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/ENGINEERING-MEMORY.md`
- Validation: `checkpoint:LESSON-PREFLIGHT.json`
- Guardrail: `file:.iacode/memory/guardrails/registry.json`, `test:IntegrityAnchorTests.test_an_unexpected_tree_is_detected`, `test:IntegrityAnchorTests.test_a_sealed_checkpoint_without_an_anchor_is_detected`, `test:IntegrityAnchorTests.test_a_recomputed_anchor_hash_must_match_its_fields`

### LESSON-REQ-0022 - lesson:LSN-0022

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0022
- Description: Verify an authoritative count must be derived once, never maintained by hand twice
- Implementation: `file:.iacode/memory/lessons.jsonl`
- Test: `test:DerivedCountTests.test_a_markdown_claim_that_contradicts_the_derivation_is_rejected`
- Negative test: _none_
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/ENGINEERING-MEMORY.md`
- Validation: `checkpoint:LESSON-PREFLIGHT.json`
- Guardrail: `file:.iacode/memory/guardrails/registry.json`, `test:DerivedCountTests.test_a_forged_count_is_rejected`, `test:DerivedCountTests.test_a_markdown_claim_that_contradicts_the_derivation_is_rejected`

### LESSON-REQ-0023 - lesson:LSN-0023

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0023
- Description: Verify a lesson must cite a source that actually records the finding it claims
- Implementation: `file:.iacode/memory/lessons.jsonl`
- Test: `test:LessonProvenanceTests.test_a_finding_absent_from_the_cited_checkpoint_is_rejected`
- Negative test: _none_
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/ENGINEERING-MEMORY.md`
- Validation: `checkpoint:LESSON-PREFLIGHT.json`
- Guardrail: `file:.iacode/memory/guardrails/registry.json`, `test:LessonProvenanceTests.test_a_finding_absent_from_the_cited_checkpoint_is_rejected`, `test:LessonProvenanceTests.test_a_nonexistent_checkpoint_is_rejected`
