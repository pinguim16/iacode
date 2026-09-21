# Closure Requirements

- Gate: `SETUP-00`
- Checkpoint: `SETUP-00-CP-0012`

## Sources

- SOURCE A: docs/SETUP-00-CHECKLIST.md, the canonical SETUP-00 specification
- SOURCE B: docs/MILESTONE-VALIDATION.md, the milestone requirements of the audit
- SOURCE C: docs/checkpoints/SETUP-00-CP-0011/REVIEW-REPORT.md, the findings of M0-CP-0011
- SOURCE D: docs/checkpoints/SETUP-00-CP-0011/RED-TEAM-REPORT.md, the mandatory attacks of M0-CP-0011
- SOURCE E: LESSON-PREFLIGHT.json, the lessons the engineering memory imposes
- SOURCE F: FINAL-CORRECTION-REQUIREMENTS.json, the delivery-local requirements of this correction

Each row carries its anchored source, its implementation status and its final status. The
anchored rows are derived from the canonical sources at every validation; the local rows are
the requirements of this correction and are audited with the rest.

| ID | Source | Anchored reference | Requirement | Implementation | Final |
|---|---|---|---|---|---|
| `REQ-0001` | SETUP | `canonical:SETUP-00#1.1` | A single entry point states the phase, current Gate, latest checkpoint, and start protocol. | `COMPLETE` | `COMPLETE` |
| `REQ-0002` | SETUP | `canonical:SETUP-00#1.2` | A Codex adapter binds the canonical contracts without adding independent policy. | `COMPLETE` | `COMPLETE` |
| `REQ-0003` | SETUP | `canonical:SETUP-00#1.3` | A Claude Code adapter binds the same contracts. | `COMPLETE` | `COMPLETE` |
| `REQ-0004` | SETUP | `canonical:SETUP-00#1.4` | Tool adapters stay semantically equivalent to the canonical roles. | `COMPLETE` | `COMPLETE` |
| `REQ-0005` | SETUP | `canonical:SETUP-00#2.1` | The Gate sequence, dependencies, acceptance, and fail conditions are recorded. | `COMPLETE` | `COMPLETE` |
| `REQ-0006` | SETUP | `canonical:SETUP-00#2.2` | The completion standard, mandatory controls, and Git and evidence discipline are recorded. | `COMPLETE` | `COMPLETE` |
| `REQ-0007` | SETUP | `canonical:SETUP-00#2.3` | Tool-to-tool transfer is formal in both directions. | `COMPLETE` | `COMPLETE` |
| `REQ-0008` | SETUP | `canonical:SETUP-00#2.4` | Checkpoint statuses, required events, required contents, commit semantics, and divergence handling are defined. | `COMPLETE` | `COMPLETE` |
| `REQ-0009` | SETUP | `canonical:SETUP-00#2.5` | Done is defined and excludes assertion-only PASS. | `COMPLETE` | `COMPLETE` |
| `REQ-0010` | SETUP | `canonical:SETUP-00#2.6` | Quality outcomes, required dimensions, and the promotion rule are defined. | `COMPLETE` | `COMPLETE` |
| `REQ-0011` | SETUP | `canonical:SETUP-00#2.7` | Structural decisions are recorded as ADRs. | `COMPLETE` | `COMPLETE` |
| `REQ-0012` | SETUP | `canonical:SETUP-00#2.8` | Architecture, roadmap, provenance, model usage, and detected tool capabilities are documented. | `COMPLETE` | `COMPLETE` |
| `REQ-0013` | SETUP | `canonical:SETUP-00#3.1` | The canonical, tool-neutral role contracts exist, one per role of the delivery protocol. | `COMPLETE` | `COMPLETE` |
| `REQ-0014` | SETUP | `canonical:SETUP-00#3.2` | Documentation, provenance, secret, tool-execution, and training-data policies exist. | `COMPLETE` | `COMPLETE` |
| `REQ-0015` | SETUP | `canonical:SETUP-00#3.3` | Reusable templates exist for ADRs, checkpoints, gate reports, and handoffs. | `COMPLETE` | `COMPLETE` |
| `REQ-0016` | SETUP | `canonical:SETUP-00#4.1` | Checkpoint state, run metadata, command, test, quality, provenance, and decision schemas exist and are loadable. | `COMPLETE` | `COMPLETE` |
| `REQ-0017` | SETUP | `canonical:SETUP-00#4.2` | An experience schema is reserved for Gate 6 and implements no runtime. | `COMPLETE` | `COMPLETE` |
| `REQ-0018` | SETUP | `canonical:SETUP-00#4.3` | Schema evolution is versioned and never invalidates a sealed checkpoint. | `COMPLETE` | `COMPLETE` |
| `REQ-0019` | SETUP | `canonical:SETUP-00#5.1` | A checkpoint can be created with truthful non-PASS defaults. | `COMPLETE` | `COMPLETE` |
| `REQ-0020` | SETUP | `canonical:SETUP-00#5.2` | A checkpoint can be finalized, and every finalization attempt is recorded with its exit code. | `COMPLETE` | `COMPLETE` |
| `REQ-0021` | SETUP | `canonical:SETUP-00#5.3` | A checkpoint is validated against schemas, Git state, inventory, quality evidence, and secrets. | `COMPLETE` | `COMPLETE` |
| `REQ-0022` | SETUP | `canonical:SETUP-00#5.4` | Secret redaction is available and documented to its real scope. | `COMPLETE` | `COMPLETE` |
| `REQ-0023` | SETUP | `canonical:SETUP-00#5.5` | The tooling is standard-library only and portable across Windows and Unix-like checkouts. | `COMPLETE` | `COMPLETE` |
| `REQ-0024` | SETUP | `canonical:SETUP-00#6.1` | Every checkpoint carries status, handoff, run metadata, state, plan, decisions, commands, file inventory, tests, quality, provenance, diff summary, risks, and next action. | `COMPLETE` | `COMPLETE` |
| `REQ-0025` | SETUP | `canonical:SETUP-00#6.2` | `LATEST.md` points textually to the last checkpoint accepted by validation. | `COMPLETE` | `COMPLETE` |
| `REQ-0026` | SETUP | `canonical:SETUP-00#6.3` | The file inventory matches the real change set, with bound content hashes. | `COMPLETE` | `COMPLETE` |
| `REQ-0027` | SETUP | `canonical:SETUP-00#6.4` | Provenance is complete and `trainingAllowed` defaults to `false`. | `COMPLETE` | `COMPLETE` |
| `REQ-0028` | SETUP | `canonical:SETUP-00#6.5` | A quality `PASS` carries resolvable evidence. | `COMPLETE` | `COMPLETE` |
| `REQ-0029` | SETUP | `canonical:SETUP-00#6.6` | Handoff-ready and terminal checkpoints are anchored to an immutable namespaced tag. | `COMPLETE` | `COMPLETE` |
| `REQ-0030` | SETUP | `canonical:SETUP-00#7.1` | A cold-start continuation prompt exists and depends only on checked-in files. | `COMPLETE` | `COMPLETE` |
| `REQ-0031` | SETUP | `canonical:SETUP-00#7.2` | Cold-start validation is executed and recorded truthfully, including a blocked attempt. | `COMPLETE` | `COMPLETE` |
| `REQ-0032` | SETUP | `canonical:SETUP-00#7.3` | Cross-tool validation state is structured and explicit. | `COMPLETE` | `COMPLETE` |
| `REQ-0033` | SETUP | `canonical:SETUP-00#7.4` | A sealed checkpoint can be validated from a detached checkout of its own tag. | `COMPLETE` | `COMPLETE` |
| `REQ-0034` | SETUP | `canonical:SETUP-00#7.5` | The handoff is executable by another tool without the producing session. | `COMPLETE` | `COMPLETE` |
| `REQ-0035` | SETUP | `canonical:SETUP-00#7b.1` | Every requirement of a delivery exists in a versioned matrix before implementation. | `COMPLETE` | `COMPLETE` |
| `REQ-0036` | SETUP | `canonical:SETUP-00#7b.2` | A Test Rework / Green Keeper role forbids shipping anything red and records every cycle. | `COMPLETE` | `COMPLETE` |
| `REQ-0037` | SETUP | `canonical:SETUP-00#7b.3` | A Delivery Completeness Validator audits the matrix before handoff and may not implement. | `COMPLETE` | `COMPLETE` |
| `REQ-0038` | SETUP | `canonical:SETUP-00#7b.4` | `GREEN_KEEPER_GATE` and `DELIVERY_COMPLETENESS_GATE` are preconditions of `READY_FOR_REVIEW`. | `COMPLETE` | `COMPLETE` |
| `REQ-0039` | SETUP | `canonical:SETUP-00#7b.5` | Readiness and blockage can never be claimed together. | `COMPLETE` | `COMPLETE` |
| `REQ-0040` | SETUP | `canonical:SETUP-00#7b.6` | Every operation attempt is recorded, including a refusal decided before execution. | `COMPLETE` | `COMPLETE` |
| `REQ-0041` | SETUP | `canonical:SETUP-00#7b.7` | Every recorded command is reproducible from its declared working directory. | `COMPLETE` | `COMPLETE` |
| `REQ-0042` | SETUP | `canonical:SETUP-00#7b.8` | The mandatory delivery order is stated in full in every governing document and both adapters. | `COMPLETE` | `COMPLETE` |
| `REQ-0043` | SETUP | `canonical:SETUP-00#7c.1` | The project keeps an organizational engineering memory of confirmed failures. | `COMPLETE` | `COMPLETE` |
| `REQ-0044` | SETUP | `canonical:SETUP-00#7c.2` | A lesson is `GUARDED` only when an automated control prevents recurrence. | `COMPLETE` | `COMPLETE` |
| `REQ-0045` | SETUP | `canonical:SETUP-00#7c.3` | A repeat increments recurrence, and a repeat against a guardrail is a `GUARDRAIL_FAILURE`. | `COMPLETE` | `COMPLETE` |
| `REQ-0046` | SETUP | `canonical:SETUP-00#7c.4` | A mandatory preflight selects the lessons that constrain each Gate. | `COMPLETE` | `COMPLETE` |
| `REQ-0047` | SETUP | `canonical:SETUP-00#7c.5` | Applicable lessons become requirements whose absence blocks completeness. | `COMPLETE` | `COMPLETE` |
| `REQ-0048` | SETUP | `canonical:SETUP-00#7c.6` | Lesson candidates can be extracted from recorded delivery evidence, never above `OBSERVED`. | `COMPLETE` | `COMPLETE` |
| `REQ-0049` | SETUP | `canonical:SETUP-00#7c.7` | External validation is grouped into milestones `M0` to `M6`. | `COMPLETE` | `COMPLETE` |
| `REQ-0050` | SETUP | `canonical:SETUP-00#7c.8` | An internal verdict is never described as independent external validation. | `COMPLETE` | `COMPLETE` |
| `REQ-0051` | SETUP | `canonical:SETUP-00#7c.9` | An extraordinary audit requires a recorded trigger. | `COMPLETE` | `COMPLETE` |
| `REQ-0052` | SETUP | `canonical:SETUP-00#7c.10` | Every completed Gate produces a retrospective. | `COMPLETE` | `COMPLETE` |
| `REQ-0053` | SETUP | `canonical:SETUP-00#7d.1` | One promotion invariant governs every positive terminal status, not only `READY_FOR_REVIEW`. | `COMPLETE` | `COMPLETE` |
| `REQ-0054` | SETUP | `canonical:SETUP-00#7d.2` | The mandatory quality gate set is a closed machine-readable registry that an invocation cannot narrow. | `COMPLETE` | `COMPLETE` |
| `REQ-0055` | SETUP | `canonical:SETUP-00#7d.3` | The expected requirement set is derived from canonical sources and compared exactly with the declared set. | `COMPLETE` | `COMPLETE` |
| `REQ-0056` | SETUP | `canonical:SETUP-00#7d.4` | An external milestone PASS is derived from an audit attestation authored by another sealed checkpoint. | `COMPLETE` | `COMPLETE` |
| `REQ-0057` | SETUP | `canonical:SETUP-00#7d.5` | A derived artifact carries a fingerprint of its inputs, and staleness is decided by recomputation. | `COMPLETE` | `COMPLETE` |
| `REQ-0058` | SETUP | `canonical:SETUP-00#7d.6` | Every lesson control, evidence path and provenance locator is resolved against the repository. | `COMPLETE` | `COMPLETE` |
| `REQ-0059` | SETUP | `canonical:SETUP-00#7d.7` | Every `GUARDED` lesson names a registered guardrail, and guardrail effectiveness is measured. | `COMPLETE` | `COMPLETE` |
| `REQ-0060` | SETUP | `canonical:SETUP-00#7d.8` | Sealed checkpoints are anchored by a hash-linked chain over tag, commit and tree. | `COMPLETE` | `COMPLETE` |
| `REQ-0061` | SETUP | `canonical:SETUP-00#7d.9` | Every count used as evidence is derived once and verified wherever a report states it. | `COMPLETE` | `COMPLETE` |
| `REQ-0062` | SETUP | `canonical:SETUP-00#7d.10` | Sealing is monotonic and post-commit, and every recorded command binds its declared inputs by content. | `COMPLETE` | `COMPLETE` |
| `REQ-0063` | SETUP | `canonical:SETUP-00#7d.11` | A milestone delivery carries an internal Red Team and an internal mirror audit, and neither is recorded as external validation. | `COMPLETE` | `COMPLETE` |
| `REQ-0064` | SETUP | `canonical:SETUP-00#7d.12` | Every finding of an independent audit is closed before the corrective delivery is offered. | `COMPLETE` | `COMPLETE` |
| `REQ-0065` | SETUP | `canonical:SETUP-00#7d.13` | A milestone verdict is carried by the audit checkpoint about a sealed subject, and its positive path is executed rather than only its refusals. | `COMPLETE` | `COMPLETE` |
| `REQ-0066` | SETUP | `canonical:SETUP-00#7d.14` | A generic guardrail derives repository state instead of naming a historical checkpoint, and the protocol's own next steps keep every mandatory gate green. | `COMPLETE` | `COMPLETE` |
| `REQ-0067` | SETUP | `canonical:SETUP-00#7d.15` | Every adversarial battery records a null-mutation control, and no count used as evidence is stated in prose. | `COMPLETE` | `COMPLETE` |
| `REQ-0068` | SETUP | `canonical:SETUP-00#7d.16` | An audit control tells an empty applicable set from a missing required set, justifies every `NOT_APPLICABLE` against a canonical derivation no delivery can shrink, and a simulation that claims a control passed executes that control instead of writing its artifact. | `COMPLETE` | `COMPLETE` |
| `REQ-0069` | SETUP | `canonical:SETUP-00#8.1` | An independent review is recorded. | `COMPLETE` | `COMPLETE` |
| `REQ-0070` | SETUP | `canonical:SETUP-00#8.2` | An adversarial Red Team is recorded. | `COMPLETE` | `COMPLETE` |
| `REQ-0071` | SETUP | `canonical:SETUP-00#8.3` | `GATE_PASS` is granted only by a run independent of the implementer. | `COMPLETE` | `COMPLETE` |
| `REQ-0072` | SETUP | `canonical:SETUP-00#9.1` | No Gate 0 or later runtime is implemented during SETUP-00. | `COMPLETE` | `COMPLETE` |
| `REQ-0073` | SETUP | `canonical:SETUP-00#9.2` | Documentation is maintained continuously rather than reconstructed at the end. | `COMPLETE` | `COMPLETE` |
| `REQ-0074` | SETUP | `canonical:SETUP-00#9.3` | No secret, credential, or private chain-of-thought is stored. | `COMPLETE` | `COMPLETE` |
| `REQ-0075` | SETUP | `canonical:SETUP-00#9.4` | Gate advancement requires explicit authorization and a passing previous Gate. | `COMPLETE` | `COMPLETE` |
| `REQ-0076` | AUDIT_FINDING | `finding:CP11-F-001` | the internal mirror audit cannot pass for a delivery that corrects no audit, and checkpoint validation requires it to pass | `COMPLETE` | `COMPLETE` |
| `REQ-0077` | AUDIT_ATTACK | `attack:INT-01` | Defend attack INT-01: Move a historical checkpoint tag onto another commit | `COMPLETE` | `COMPLETE` |
| `REQ-0078` | AUDIT_ATTACK | `attack:INT-02` | Defend attack INT-02: Rewrite sealed content and move its tag onto the rewrite | `COMPLETE` | `COMPLETE` |
| `REQ-0079` | AUDIT_ATTACK | `attack:INT-03` | Defend attack INT-03: Break the link between two consecutive anchors | `COMPLETE` | `COMPLETE` |
| `REQ-0080` | AUDIT_ATTACK | `attack:INT-04` | Defend attack INT-04: Remove the anchor of a sealed checkpoint | `COMPLETE` | `COMPLETE` |
| `REQ-0081` | AUDIT_ATTACK | `attack:INT-05` | Defend attack INT-05: Skip the anchor this checkpoint owes its sealed predecessor | `COMPLETE` | `COMPLETE` |
| `REQ-0082` | AUDIT_ATTACK | `attack:PRE-01` | Defend attack PRE-01: Change the memory after the preflight was recorded | `COMPLETE` | `COMPLETE` |
| `REQ-0083` | AUDIT_ATTACK | `attack:MEM-01` | Defend attack MEM-01: Replace a preventive control with documentation only | `COMPLETE` | `COMPLETE` |
| `REQ-0084` | AUDIT_ATTACK | `attack:STL-01` | Defend attack STL-01: Edit the assurance scope after the last green cycle | `COMPLETE` | `COMPLETE` |
| `REQ-0085` | AUDIT_ATTACK | `attack:STL-02` | Defend attack STL-02: Forge the derived test count | `COMPLETE` | `COMPLETE` |
| `REQ-0086` | AUDIT_ATTACK | `attack:STL-04` | Defend attack STL-04: Carry a blocker while claiming a milestone verdict | `COMPLETE` | `COMPLETE` |
| `REQ-0087` | AUDIT_ATTACK | `attack:STL-05` | Defend attack STL-05: Remove an entry from the declared change set | `COMPLETE` | `COMPLETE` |
| `REQ-0088` | AUDIT_ATTACK | `attack:SEC-01` | Defend attack SEC-01: Insert a credential-shaped value into the memory and require a refusal that does not repeat it | `COMPLETE` | `COMPLETE` |
| `LESSON-REQ-0001` | LESSON | `lesson:LSN-0001` | Verify checkpoint validation must succeed from a detached checkout of the checkpoint tag | `COMPLETE` | `COMPLETE` |
| `LESSON-REQ-0002` | LESSON | `lesson:LSN-0002` | Verify a file inventory must be recomputed from the repository, never trusted as an assertion | `COMPLETE` | `COMPLETE` |
| `LESSON-REQ-0003` | LESSON | `lesson:LSN-0003` | Verify every operation attempt must be auditable, including a refusal decided before execution | `COMPLETE` | `COMPLETE` |
| `LESSON-REQ-0004` | LESSON | `lesson:LSN-0004` | Verify a checkpoint may never claim readiness while it also claims to be blocked | `COMPLETE` | `COMPLETE` |
| `LESSON-REQ-0005` | LESSON | `lesson:LSN-0005` | Verify a PASS requires evidence that can be executed or resolved, not a statement | `COMPLETE` | `COMPLETE` |
| `LESSON-REQ-0006` | LESSON | `lesson:LSN-0006` | Verify the repository must be self-contained; a specification may not live outside it | `COMPLETE` | `COMPLETE` |
| `LESSON-REQ-0007` | LESSON | `lesson:LSN-0007` | Verify independent validation cannot be declared by the run that did the work | `COMPLETE` | `COMPLETE` |
| `LESSON-REQ-0008` | LESSON | `lesson:LSN-0008` | Verify requirement completeness must be total and evidence-backed before handoff | `COMPLETE` | `COMPLETE` |
| `LESSON-REQ-0009` | LESSON | `lesson:LSN-0009` | Verify a red gate requires rework, never a waiver, and never a weakened check | `COMPLETE` | `COMPLETE` |
| `LESSON-REQ-0010` | LESSON | `lesson:LSN-0010` | Verify a recorded command must carry runtime, working directory, commit and purpose to be replayable | `COMPLETE` | `COMPLETE` |
| `LESSON-REQ-0011` | LESSON | `lesson:LSN-0011` | Verify a control over a checkpoint's own evidence must be scoped to the moment it matters | `COMPLETE` | `COMPLETE` |
| `LESSON-REQ-0012` | LESSON | `lesson:LSN-0012` | Verify sealed checkpoints and their tags are immutable, and tooling must keep validating them | `COMPLETE` | `COMPLETE` |
| `LESSON-REQ-0013` | LESSON | `lesson:LSN-0013` | Verify an installed capability must be detected by resolved path, not by a bare command lookup | `COMPLETE` | `COMPLETE` |
| `LESSON-REQ-0014` | LESSON | `lesson:LSN-0014` | Verify evidence must be recorded as it happens, not reconstructed at the end of a run | `COMPLETE` | `COMPLETE` |
| `LESSON-REQ-0015` | LESSON | `lesson:LSN-0015` | Verify every positive terminal status needs one shared promotion invariant | `COMPLETE` | `COMPLETE` |
| `LESSON-REQ-0016` | LESSON | `lesson:LSN-0016` | Verify a mandatory set must be closed by policy, never chosen by the caller | `COMPLETE` | `COMPLETE` |
| `LESSON-REQ-0017` | LESSON | `lesson:LSN-0017` | Verify a completeness denominator must come from a source the delivery does not own | `COMPLETE` | `COMPLETE` |
| `LESSON-REQ-0018` | LESSON | `lesson:LSN-0018` | Verify a structured reference must be resolved, not merely well typed | `COMPLETE` | `COMPLETE` |
| `LESSON-REQ-0019` | LESSON | `lesson:LSN-0019` | Verify a derived artifact must carry a fingerprint of the inputs that produced it | `COMPLETE` | `COMPLETE` |
| `LESSON-REQ-0020` | LESSON | `lesson:LSN-0020` | Verify evidence produced from a dirty tree needs immutable input identity | `COMPLETE` | `COMPLETE` |
| `LESSON-REQ-0021` | LESSON | `lesson:LSN-0021` | Verify sealed history needs an anchor outside the content it describes | `COMPLETE` | `COMPLETE` |
| `LESSON-REQ-0022` | LESSON | `lesson:LSN-0022` | Verify an authoritative count must be derived once, never maintained by hand twice | `COMPLETE` | `COMPLETE` |
| `LESSON-REQ-0023` | LESSON | `lesson:LSN-0023` | Verify a lesson must cite a source that actually records the finding it claims | `COMPLETE` | `COMPLETE` |
| `LESSON-REQ-0024` | LESSON | `lesson:LSN-0024` | Verify a control is finished only when its positive path has been executed, not only its refusals | `COMPLETE` | `COMPLETE` |
| `LESSON-REQ-0025` | LESSON | `lesson:LSN-0025` | Verify a generic guardrail derives repository state instead of naming today's checkpoint | `COMPLETE` | `COMPLETE` |
| `LESSON-REQ-0026` | LESSON | `lesson:LSN-0026` | Verify an adversarial battery without a null-mutation control proves nothing | `COMPLETE` | `COMPLETE` |
| `LESSON-REQ-0027` | LESSON | `lesson:LSN-0027` | Verify a lesson's prose may record a residual limit but may never contradict its status | `COMPLETE` | `COMPLETE` |
| `LESSON-REQ-0028` | LESSON | `lesson:LSN-0028` | Verify a configuration key that no code reads is a defect, not documentation | `COMPLETE` | `COMPLETE` |
| `LESSON-REQ-0029` | LESSON | `lesson:LSN-0029` | Verify a required protocol transition must never turn a mandatory gate red | `COMPLETE` | `COMPLETE` |
| `LESSON-REQ-0030` | LESSON | `lesson:LSN-0031` | Verify an empty applicable set is not a missing required set, and a control must tell them apart | `COMPLETE` | `COMPLETE` |
| `REQ-0089` | LOCAL | `local:FCR-001` | The finding set is taken from the sealed audit checkpoint, not from a summary | `COMPLETE` | `COMPLETE` |
| `REQ-0090` | LOCAL | `local:FCR-002` | CP11-F-001 is closed | `COMPLETE` | `COMPLETE` |
| `REQ-0091` | LOCAL | `local:FCR-003` | MIR-002 reports an empty applicable set as NOT_APPLICABLE | `COMPLETE` | `COMPLETE` |
| `REQ-0092` | LOCAL | `local:FCR-004` | MIR-003 is analysed on its own and repaired on its own terms | `COMPLETE` | `COMPLETE` |
| `REQ-0093` | LOCAL | `local:FCR-005` | The overall verdict treats NOT_APPLICABLE as non-failing without rewriting it | `COMPLETE` | `COMPLETE` |
| `REQ-0094` | LOCAL | `local:FCR-006` | Every NOT_APPLICABLE carries a reason, an empty expected count and a source | `COMPLETE` | `COMPLETE` |
| `REQ-0095` | LOCAL | `local:FCR-007` | NOT_APPLICABLE never becomes a bypass | `COMPLETE` | `COMPLETE` |
| `REQ-0096` | LOCAL | `local:FCR-008` | A checkpoint with no open audit passes the real mirror | `COMPLETE` | `COMPLETE` |
| `REQ-0097` | LOCAL | `local:FCR-009` | The first checkpoint of the next Gate reaches READY_FOR_REVIEW | `COMPLETE` | `COMPLETE` |
| `REQ-0098` | LOCAL | `local:FCR-010` | A real open finding still fails | `COMPLETE` | `COMPLETE` |
| `REQ-0099` | LOCAL | `local:FCR-011` | An expected audit artifact that is absent fails, and is never inapplicable | `COMPLETE` | `COMPLETE` |
| `REQ-0100` | LOCAL | `local:FCR-012` | A forged empty expected set does not reduce the applicable set | `COMPLETE` | `COMPLETE` |
| `REQ-0101` | LOCAL | `local:FCR-013` | A milestone with no findings of its own can pass | `COMPLETE` | `COMPLETE` |
| `REQ-0102` | LOCAL | `local:FCR-014` | A delivery with closed findings passes | `COMPLETE` | `COMPLETE` |
| `REQ-0103` | LOCAL | `local:FCR-015` | A delivery with an open finding does not pass | `COMPLETE` | `COMPLETE` |
| `REQ-0104` | LOCAL | `local:FCR-016` | The schema reuses NOT_APPLICABLE and evolves compatibly under a version gate | `COMPLETE` | `COMPLETE` |
| `REQ-0105` | LOCAL | `local:FCR-017` | Every sealed checkpoint still validates under the new semantics | `COMPLETE` | `COMPLETE` |
| `REQ-0106` | LOCAL | `local:FCR-018` | The positive promotion simulation passes after the repair | `COMPLETE` | `COMPLETE` |
| `REQ-0107` | LOCAL | `local:FCR-019` | Successor durability passes after the repair | `COMPLETE` | `COMPLETE` |
| `REQ-0108` | LOCAL | `local:FCR-020` | The state machine is proven without implementing the next Gate | `COMPLETE` | `COMPLETE` |
| `REQ-0109` | LOCAL | `local:FCR-021` | The lesson is recorded with the precise distinction and is guarded | `COMPLETE` | `COMPLETE` |
| `REQ-0110` | LOCAL | `local:FCR-022` | The recurrence is recorded as a GUARDRAIL_FAILURE and resolved | `COMPLETE` | `COMPLETE` |
| `REQ-0111` | LOCAL | `local:FCR-023` | The positive simulation executes the mirror instead of writing its artifact | `COMPLETE` | `COMPLETE` |
| `REQ-0112` | LOCAL | `local:FCR-024` | A simulation that reports a control as passing calls that control | `COMPLETE` | `COMPLETE` |
| `REQ-0113` | LOCAL | `local:FCR-025` | The canonical CLAUDE.md records the language rule | `COMPLETE` | `COMPLETE` |
| `REQ-0114` | LOCAL | `local:FCR-026` | The Green Keeper is green over the canonical mandatory gate set | `COMPLETE` | `COMPLETE` |
| `REQ-0115` | LOCAL | `local:FCR-027` | Delivery completeness is total over an independently derived expected set | `COMPLETE` | `COMPLETE` |
| `REQ-0116` | LOCAL | `local:FCR-028` | The completeness audit covers this whole execution before handoff | `COMPLETE` | `COMPLETE` |
| `REQ-0117` | LOCAL | `local:FCR-029` | The internal mirror of this delivery is the tool's own output | `COMPLETE` | `COMPLETE` |
| `REQ-0118` | LOCAL | `local:FCR-030` | The adversarial position of the changed surface is executed | `COMPLETE` | `COMPLETE` |
| `REQ-0119` | LOCAL | `local:FCR-031` | The whole suite passes and every skip is accounted for | `COMPLETE` | `COMPLETE` |
| `REQ-0120` | LOCAL | `local:FCR-032` | The delivery validates from a clean clone | `COMPLETE` | `COMPLETE` |
| `REQ-0121` | LOCAL | `local:FCR-033` | The CP-0011 findings closure record exists and is complete | `COMPLETE` | `COMPLETE` |
| `REQ-0122` | LOCAL | `local:FCR-034` | An internal auditor that did not implement audits the delivery | `COMPLETE` | `COMPLETE` |
| `REQ-0123` | LOCAL | `local:FCR-035` | The checkpoint carries every mandatory artifact of the current protocol | `COMPLETE` | `COMPLETE` |
| `REQ-0124` | LOCAL | `local:FCR-036` | The delivery closes at READY_FOR_REVIEW and never grants itself a Gate | `COMPLETE` | `COMPLETE` |
| `REQ-0125` | LOCAL | `local:FCR-037` | The next action is a fresh-session independent M0 audit and Gate 0 stays blocked | `COMPLETE` | `COMPLETE` |
| `REQ-0126` | LOCAL | `local:FCR-038` | No historical checkpoint, commit or tag is rewritten | `COMPLETE` | `COMPLETE` |
