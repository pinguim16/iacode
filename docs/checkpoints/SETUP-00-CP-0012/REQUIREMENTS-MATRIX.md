# Requirements Matrix - SETUP-00-CP-0012

Expected set derived by: `policies.expected_requirement_refs over docs/SETUP-00-CHECKLIST.md, .iacode/policies/canonical-requirements.json, .iacode/policies/audit-registry.json and LESSON-PREFLIGHT.json`.

| ID | Anchor | Mandatory | Status | Requirement | Source |
|---|---|---|---|---|---|
| `REQ-0001` | `canonical:SETUP-00#1.1` | yes | `NOT_STARTED` | A single entry point states the phase, current Gate, latest checkpoint, and start protocol. | docs/SETUP-00-CHECKLIST.md row 1.1 |
| `REQ-0002` | `canonical:SETUP-00#1.2` | yes | `NOT_STARTED` | A Codex adapter binds the canonical contracts without adding independent policy. | docs/SETUP-00-CHECKLIST.md row 1.2 |
| `REQ-0003` | `canonical:SETUP-00#1.3` | yes | `NOT_STARTED` | A Claude Code adapter binds the same contracts. | docs/SETUP-00-CHECKLIST.md row 1.3 |
| `REQ-0004` | `canonical:SETUP-00#1.4` | yes | `NOT_STARTED` | Tool adapters stay semantically equivalent to the canonical roles. | docs/SETUP-00-CHECKLIST.md row 1.4 |
| `REQ-0005` | `canonical:SETUP-00#2.1` | yes | `NOT_STARTED` | The Gate sequence, dependencies, acceptance, and fail conditions are recorded. | docs/SETUP-00-CHECKLIST.md row 2.1 |
| `REQ-0006` | `canonical:SETUP-00#2.2` | yes | `NOT_STARTED` | The completion standard, mandatory controls, and Git and evidence discipline are recorded. | docs/SETUP-00-CHECKLIST.md row 2.2 |
| `REQ-0007` | `canonical:SETUP-00#2.3` | yes | `NOT_STARTED` | Tool-to-tool transfer is formal in both directions. | docs/SETUP-00-CHECKLIST.md row 2.3 |
| `REQ-0008` | `canonical:SETUP-00#2.4` | yes | `NOT_STARTED` | Checkpoint statuses, required events, required contents, commit semantics, and divergence handling are defined. | docs/SETUP-00-CHECKLIST.md row 2.4 |
| `REQ-0009` | `canonical:SETUP-00#2.5` | yes | `NOT_STARTED` | Done is defined and excludes assertion-only PASS. | docs/SETUP-00-CHECKLIST.md row 2.5 |
| `REQ-0010` | `canonical:SETUP-00#2.6` | yes | `NOT_STARTED` | Quality outcomes, required dimensions, and the promotion rule are defined. | docs/SETUP-00-CHECKLIST.md row 2.6 |
| `REQ-0011` | `canonical:SETUP-00#2.7` | yes | `NOT_STARTED` | Structural decisions are recorded as ADRs. | docs/SETUP-00-CHECKLIST.md row 2.7 |
| `REQ-0012` | `canonical:SETUP-00#2.8` | yes | `NOT_STARTED` | Architecture, roadmap, provenance, model usage, and detected tool capabilities are documented. | docs/SETUP-00-CHECKLIST.md row 2.8 |
| `REQ-0013` | `canonical:SETUP-00#3.1` | yes | `NOT_STARTED` | The canonical, tool-neutral role contracts exist, one per role of the delivery protocol. | docs/SETUP-00-CHECKLIST.md row 3.1 |
| `REQ-0014` | `canonical:SETUP-00#3.2` | yes | `NOT_STARTED` | Documentation, provenance, secret, tool-execution, and training-data policies exist. | docs/SETUP-00-CHECKLIST.md row 3.2 |
| `REQ-0015` | `canonical:SETUP-00#3.3` | yes | `NOT_STARTED` | Reusable templates exist for ADRs, checkpoints, gate reports, and handoffs. | docs/SETUP-00-CHECKLIST.md row 3.3 |
| `REQ-0016` | `canonical:SETUP-00#4.1` | yes | `NOT_STARTED` | Checkpoint state, run metadata, command, test, quality, provenance, and decision schemas exist and are loadable. | docs/SETUP-00-CHECKLIST.md row 4.1 |
| `REQ-0017` | `canonical:SETUP-00#4.2` | yes | `NOT_STARTED` | An experience schema is reserved for Gate 6 and implements no runtime. | docs/SETUP-00-CHECKLIST.md row 4.2 |
| `REQ-0018` | `canonical:SETUP-00#4.3` | yes | `NOT_STARTED` | Schema evolution is versioned and never invalidates a sealed checkpoint. | docs/SETUP-00-CHECKLIST.md row 4.3 |
| `REQ-0019` | `canonical:SETUP-00#5.1` | yes | `NOT_STARTED` | A checkpoint can be created with truthful non-PASS defaults. | docs/SETUP-00-CHECKLIST.md row 5.1 |
| `REQ-0020` | `canonical:SETUP-00#5.2` | yes | `NOT_STARTED` | A checkpoint can be finalized, and every finalization attempt is recorded with its exit code. | docs/SETUP-00-CHECKLIST.md row 5.2 |
| `REQ-0021` | `canonical:SETUP-00#5.3` | yes | `NOT_STARTED` | A checkpoint is validated against schemas, Git state, inventory, quality evidence, and secrets. | docs/SETUP-00-CHECKLIST.md row 5.3 |
| `REQ-0022` | `canonical:SETUP-00#5.4` | yes | `NOT_STARTED` | Secret redaction is available and documented to its real scope. | docs/SETUP-00-CHECKLIST.md row 5.4 |
| `REQ-0023` | `canonical:SETUP-00#5.5` | yes | `NOT_STARTED` | The tooling is standard-library only and portable across Windows and Unix-like checkouts. | docs/SETUP-00-CHECKLIST.md row 5.5 |
| `REQ-0024` | `canonical:SETUP-00#6.1` | yes | `NOT_STARTED` | Every checkpoint carries status, handoff, run metadata, state, plan, decisions, commands, file inventory, tests, quality, provenance, diff summary, risks, and next action. | docs/SETUP-00-CHECKLIST.md row 6.1 |
| `REQ-0025` | `canonical:SETUP-00#6.2` | yes | `NOT_STARTED` | `LATEST.md` points textually to the last checkpoint accepted by validation. | docs/SETUP-00-CHECKLIST.md row 6.2 |
| `REQ-0026` | `canonical:SETUP-00#6.3` | yes | `NOT_STARTED` | The file inventory matches the real change set, with bound content hashes. | docs/SETUP-00-CHECKLIST.md row 6.3 |
| `REQ-0027` | `canonical:SETUP-00#6.4` | yes | `NOT_STARTED` | Provenance is complete and `trainingAllowed` defaults to `false`. | docs/SETUP-00-CHECKLIST.md row 6.4 |
| `REQ-0028` | `canonical:SETUP-00#6.5` | yes | `NOT_STARTED` | A quality `PASS` carries resolvable evidence. | docs/SETUP-00-CHECKLIST.md row 6.5 |
| `REQ-0029` | `canonical:SETUP-00#6.6` | yes | `NOT_STARTED` | Handoff-ready and terminal checkpoints are anchored to an immutable namespaced tag. | docs/SETUP-00-CHECKLIST.md row 6.6 |
| `REQ-0030` | `canonical:SETUP-00#7.1` | yes | `NOT_STARTED` | A cold-start continuation prompt exists and depends only on checked-in files. | docs/SETUP-00-CHECKLIST.md row 7.1 |
| `REQ-0031` | `canonical:SETUP-00#7.2` | yes | `NOT_STARTED` | Cold-start validation is executed and recorded truthfully, including a blocked attempt. | docs/SETUP-00-CHECKLIST.md row 7.2 |
| `REQ-0032` | `canonical:SETUP-00#7.3` | yes | `NOT_STARTED` | Cross-tool validation state is structured and explicit. | docs/SETUP-00-CHECKLIST.md row 7.3 |
| `REQ-0033` | `canonical:SETUP-00#7.4` | yes | `NOT_STARTED` | A sealed checkpoint can be validated from a detached checkout of its own tag. | docs/SETUP-00-CHECKLIST.md row 7.4 |
| `REQ-0034` | `canonical:SETUP-00#7.5` | yes | `NOT_STARTED` | The handoff is executable by another tool without the producing session. | docs/SETUP-00-CHECKLIST.md row 7.5 |
| `REQ-0035` | `canonical:SETUP-00#7b.1` | yes | `NOT_STARTED` | Every requirement of a delivery exists in a versioned matrix before implementation. | docs/SETUP-00-CHECKLIST.md row 7b.1 |
| `REQ-0036` | `canonical:SETUP-00#7b.2` | yes | `NOT_STARTED` | A Test Rework / Green Keeper role forbids shipping anything red and records every cycle. | docs/SETUP-00-CHECKLIST.md row 7b.2 |
| `REQ-0037` | `canonical:SETUP-00#7b.3` | yes | `NOT_STARTED` | A Delivery Completeness Validator audits the matrix before handoff and may not implement. | docs/SETUP-00-CHECKLIST.md row 7b.3 |
| `REQ-0038` | `canonical:SETUP-00#7b.4` | yes | `NOT_STARTED` | `GREEN_KEEPER_GATE` and `DELIVERY_COMPLETENESS_GATE` are preconditions of `READY_FOR_REVIEW`. | docs/SETUP-00-CHECKLIST.md row 7b.4 |
| `REQ-0039` | `canonical:SETUP-00#7b.5` | yes | `NOT_STARTED` | Readiness and blockage can never be claimed together. | docs/SETUP-00-CHECKLIST.md row 7b.5 |
| `REQ-0040` | `canonical:SETUP-00#7b.6` | yes | `NOT_STARTED` | Every operation attempt is recorded, including a refusal decided before execution. | docs/SETUP-00-CHECKLIST.md row 7b.6 |
| `REQ-0041` | `canonical:SETUP-00#7b.7` | yes | `NOT_STARTED` | Every recorded command is reproducible from its declared working directory. | docs/SETUP-00-CHECKLIST.md row 7b.7 |
| `REQ-0042` | `canonical:SETUP-00#7b.8` | yes | `NOT_STARTED` | The mandatory delivery order is stated in full in every governing document and both adapters. | docs/SETUP-00-CHECKLIST.md row 7b.8 |
| `REQ-0043` | `canonical:SETUP-00#7c.1` | yes | `NOT_STARTED` | The project keeps an organizational engineering memory of confirmed failures. | docs/SETUP-00-CHECKLIST.md row 7c.1 |
| `REQ-0044` | `canonical:SETUP-00#7c.2` | yes | `NOT_STARTED` | A lesson is `GUARDED` only when an automated control prevents recurrence. | docs/SETUP-00-CHECKLIST.md row 7c.2 |
| `REQ-0045` | `canonical:SETUP-00#7c.3` | yes | `NOT_STARTED` | A repeat increments recurrence, and a repeat against a guardrail is a `GUARDRAIL_FAILURE`. | docs/SETUP-00-CHECKLIST.md row 7c.3 |
| `REQ-0046` | `canonical:SETUP-00#7c.4` | yes | `NOT_STARTED` | A mandatory preflight selects the lessons that constrain each Gate. | docs/SETUP-00-CHECKLIST.md row 7c.4 |
| `REQ-0047` | `canonical:SETUP-00#7c.5` | yes | `NOT_STARTED` | Applicable lessons become requirements whose absence blocks completeness. | docs/SETUP-00-CHECKLIST.md row 7c.5 |
| `REQ-0048` | `canonical:SETUP-00#7c.6` | yes | `NOT_STARTED` | Lesson candidates can be extracted from recorded delivery evidence, never above `OBSERVED`. | docs/SETUP-00-CHECKLIST.md row 7c.6 |
| `REQ-0049` | `canonical:SETUP-00#7c.7` | yes | `NOT_STARTED` | External validation is grouped into milestones `M0` to `M6`. | docs/SETUP-00-CHECKLIST.md row 7c.7 |
| `REQ-0050` | `canonical:SETUP-00#7c.8` | yes | `NOT_STARTED` | An internal verdict is never described as independent external validation. | docs/SETUP-00-CHECKLIST.md row 7c.8 |
| `REQ-0051` | `canonical:SETUP-00#7c.9` | yes | `NOT_STARTED` | An extraordinary audit requires a recorded trigger. | docs/SETUP-00-CHECKLIST.md row 7c.9 |
| `REQ-0052` | `canonical:SETUP-00#7c.10` | yes | `NOT_STARTED` | Every completed Gate produces a retrospective. | docs/SETUP-00-CHECKLIST.md row 7c.10 |
| `REQ-0053` | `canonical:SETUP-00#7d.1` | yes | `NOT_STARTED` | One promotion invariant governs every positive terminal status, not only `READY_FOR_REVIEW`. | docs/SETUP-00-CHECKLIST.md row 7d.1 |
| `REQ-0054` | `canonical:SETUP-00#7d.2` | yes | `NOT_STARTED` | The mandatory quality gate set is a closed machine-readable registry that an invocation cannot narrow. | docs/SETUP-00-CHECKLIST.md row 7d.2 |
| `REQ-0055` | `canonical:SETUP-00#7d.3` | yes | `NOT_STARTED` | The expected requirement set is derived from canonical sources and compared exactly with the declared set. | docs/SETUP-00-CHECKLIST.md row 7d.3 |
| `REQ-0056` | `canonical:SETUP-00#7d.4` | yes | `NOT_STARTED` | An external milestone PASS is derived from an audit attestation authored by another sealed checkpoint. | docs/SETUP-00-CHECKLIST.md row 7d.4 |
| `REQ-0057` | `canonical:SETUP-00#7d.5` | yes | `NOT_STARTED` | A derived artifact carries a fingerprint of its inputs, and staleness is decided by recomputation. | docs/SETUP-00-CHECKLIST.md row 7d.5 |
| `REQ-0058` | `canonical:SETUP-00#7d.6` | yes | `NOT_STARTED` | Every lesson control, evidence path and provenance locator is resolved against the repository. | docs/SETUP-00-CHECKLIST.md row 7d.6 |
| `REQ-0059` | `canonical:SETUP-00#7d.7` | yes | `NOT_STARTED` | Every `GUARDED` lesson names a registered guardrail, and guardrail effectiveness is measured. | docs/SETUP-00-CHECKLIST.md row 7d.7 |
| `REQ-0060` | `canonical:SETUP-00#7d.8` | yes | `NOT_STARTED` | Sealed checkpoints are anchored by a hash-linked chain over tag, commit and tree. | docs/SETUP-00-CHECKLIST.md row 7d.8 |
| `REQ-0061` | `canonical:SETUP-00#7d.9` | yes | `NOT_STARTED` | Every count used as evidence is derived once and verified wherever a report states it. | docs/SETUP-00-CHECKLIST.md row 7d.9 |
| `REQ-0062` | `canonical:SETUP-00#7d.10` | yes | `NOT_STARTED` | Sealing is monotonic and post-commit, and every recorded command binds its declared inputs by content. | docs/SETUP-00-CHECKLIST.md row 7d.10 |
| `REQ-0063` | `canonical:SETUP-00#7d.11` | yes | `NOT_STARTED` | A milestone delivery carries an internal Red Team and an internal mirror audit, and neither is recorded as external validation. | docs/SETUP-00-CHECKLIST.md row 7d.11 |
| `REQ-0064` | `canonical:SETUP-00#7d.12` | yes | `NOT_STARTED` | Every finding of an independent audit is closed before the corrective delivery is offered. | docs/SETUP-00-CHECKLIST.md row 7d.12 |
| `REQ-0065` | `canonical:SETUP-00#7d.13` | yes | `NOT_STARTED` | A milestone verdict is carried by the audit checkpoint about a sealed subject, and its positive path is executed rather than only its refusals. | docs/SETUP-00-CHECKLIST.md row 7d.13 |
| `REQ-0066` | `canonical:SETUP-00#7d.14` | yes | `NOT_STARTED` | A generic guardrail derives repository state instead of naming a historical checkpoint, and the protocol's own next steps keep every mandatory gate green. | docs/SETUP-00-CHECKLIST.md row 7d.14 |
| `REQ-0067` | `canonical:SETUP-00#7d.15` | yes | `NOT_STARTED` | Every adversarial battery records a null-mutation control, and no count used as evidence is stated in prose. | docs/SETUP-00-CHECKLIST.md row 7d.15 |
| `REQ-0068` | `canonical:SETUP-00#7d.16` | yes | `NOT_STARTED` | An audit control tells an empty applicable set from a missing required set, justifies every `NOT_APPLICABLE` against a canonical derivation no delivery can shrink, and a simulation that claims a control passed executes that control instead of writing its artifact. | docs/SETUP-00-CHECKLIST.md row 7d.16 |
| `REQ-0069` | `canonical:SETUP-00#8.1` | yes | `NOT_STARTED` | An independent review is recorded. | docs/SETUP-00-CHECKLIST.md row 8.1 |
| `REQ-0070` | `canonical:SETUP-00#8.2` | yes | `NOT_STARTED` | An adversarial Red Team is recorded. | docs/SETUP-00-CHECKLIST.md row 8.2 |
| `REQ-0071` | `canonical:SETUP-00#8.3` | yes | `NOT_STARTED` | `GATE_PASS` is granted only by a run independent of the implementer. | docs/SETUP-00-CHECKLIST.md row 8.3 |
| `REQ-0072` | `canonical:SETUP-00#9.1` | yes | `NOT_STARTED` | No Gate 0 or later runtime is implemented during SETUP-00. | docs/SETUP-00-CHECKLIST.md row 9.1 |
| `REQ-0073` | `canonical:SETUP-00#9.2` | yes | `NOT_STARTED` | Documentation is maintained continuously rather than reconstructed at the end. | docs/SETUP-00-CHECKLIST.md row 9.2 |
| `REQ-0074` | `canonical:SETUP-00#9.3` | yes | `NOT_STARTED` | No secret, credential, or private chain-of-thought is stored. | docs/SETUP-00-CHECKLIST.md row 9.3 |
| `REQ-0075` | `canonical:SETUP-00#9.4` | yes | `NOT_STARTED` | Gate advancement requires explicit authorization and a passing previous Gate. | docs/SETUP-00-CHECKLIST.md row 9.4 |
| `REQ-0076` | `finding:CP11-F-001` | yes | `NOT_STARTED` | the internal mirror audit cannot pass for a delivery that corrects no audit, and checkpoint validation requires it to pass | M0-CP-0011 docs/checkpoints/SETUP-00-CP-0011/REVIEW-REPORT.md CP11-F-001 |
| `REQ-0077` | `attack:INT-01` | yes | `NOT_STARTED` | Defend attack INT-01: Move a historical checkpoint tag onto another commit | M0-CP-0011 docs/checkpoints/SETUP-00-CP-0011/RED-TEAM-REPORT.md attack INT-01 |
| `REQ-0078` | `attack:INT-02` | yes | `NOT_STARTED` | Defend attack INT-02: Rewrite sealed content and move its tag onto the rewrite | M0-CP-0011 docs/checkpoints/SETUP-00-CP-0011/RED-TEAM-REPORT.md attack INT-02 |
| `REQ-0079` | `attack:INT-03` | yes | `NOT_STARTED` | Defend attack INT-03: Break the link between two consecutive anchors | M0-CP-0011 docs/checkpoints/SETUP-00-CP-0011/RED-TEAM-REPORT.md attack INT-03 |
| `REQ-0080` | `attack:INT-04` | yes | `NOT_STARTED` | Defend attack INT-04: Remove the anchor of a sealed checkpoint | M0-CP-0011 docs/checkpoints/SETUP-00-CP-0011/RED-TEAM-REPORT.md attack INT-04 |
| `REQ-0081` | `attack:INT-05` | yes | `NOT_STARTED` | Defend attack INT-05: Skip the anchor this checkpoint owes its sealed predecessor | M0-CP-0011 docs/checkpoints/SETUP-00-CP-0011/RED-TEAM-REPORT.md attack INT-05 |
| `REQ-0082` | `attack:PRE-01` | yes | `NOT_STARTED` | Defend attack PRE-01: Change the memory after the preflight was recorded | M0-CP-0011 docs/checkpoints/SETUP-00-CP-0011/RED-TEAM-REPORT.md attack PRE-01 |
| `REQ-0083` | `attack:MEM-01` | yes | `NOT_STARTED` | Defend attack MEM-01: Replace a preventive control with documentation only | M0-CP-0011 docs/checkpoints/SETUP-00-CP-0011/RED-TEAM-REPORT.md attack MEM-01 |
| `REQ-0084` | `attack:STL-01` | yes | `NOT_STARTED` | Defend attack STL-01: Edit the assurance scope after the last green cycle | M0-CP-0011 docs/checkpoints/SETUP-00-CP-0011/RED-TEAM-REPORT.md attack STL-01 |
| `REQ-0085` | `attack:STL-02` | yes | `NOT_STARTED` | Defend attack STL-02: Forge the derived test count | M0-CP-0011 docs/checkpoints/SETUP-00-CP-0011/RED-TEAM-REPORT.md attack STL-02 |
| `REQ-0086` | `attack:STL-04` | yes | `NOT_STARTED` | Defend attack STL-04: Carry a blocker while claiming a milestone verdict | M0-CP-0011 docs/checkpoints/SETUP-00-CP-0011/RED-TEAM-REPORT.md attack STL-04 |
| `REQ-0087` | `attack:STL-05` | yes | `NOT_STARTED` | Defend attack STL-05: Remove an entry from the declared change set | M0-CP-0011 docs/checkpoints/SETUP-00-CP-0011/RED-TEAM-REPORT.md attack STL-05 |
| `REQ-0088` | `attack:SEC-01` | yes | `NOT_STARTED` | Defend attack SEC-01: Insert a credential-shaped value into the memory and require a refusal that does not repeat it | M0-CP-0011 docs/checkpoints/SETUP-00-CP-0011/RED-TEAM-REPORT.md attack SEC-01 |
| `LESSON-REQ-0001` | `lesson:LSN-0001` | yes | `NOT_STARTED` | Verify checkpoint validation must succeed from a detached checkout of the checkpoint tag | LESSON-PREFLIGHT.json LESSON-REQ-0001 |
| `LESSON-REQ-0002` | `lesson:LSN-0002` | yes | `NOT_STARTED` | Verify a file inventory must be recomputed from the repository, never trusted as an assertion | LESSON-PREFLIGHT.json LESSON-REQ-0002 |
| `LESSON-REQ-0003` | `lesson:LSN-0003` | yes | `NOT_STARTED` | Verify every operation attempt must be auditable, including a refusal decided before execution | LESSON-PREFLIGHT.json LESSON-REQ-0003 |
| `LESSON-REQ-0004` | `lesson:LSN-0004` | yes | `NOT_STARTED` | Verify a checkpoint may never claim readiness while it also claims to be blocked | LESSON-PREFLIGHT.json LESSON-REQ-0004 |
| `LESSON-REQ-0005` | `lesson:LSN-0005` | yes | `NOT_STARTED` | Verify a PASS requires evidence that can be executed or resolved, not a statement | LESSON-PREFLIGHT.json LESSON-REQ-0005 |
| `LESSON-REQ-0006` | `lesson:LSN-0006` | yes | `NOT_STARTED` | Verify the repository must be self-contained; a specification may not live outside it | LESSON-PREFLIGHT.json LESSON-REQ-0006 |
| `LESSON-REQ-0007` | `lesson:LSN-0007` | yes | `NOT_STARTED` | Verify independent validation cannot be declared by the run that did the work | LESSON-PREFLIGHT.json LESSON-REQ-0007 |
| `LESSON-REQ-0008` | `lesson:LSN-0008` | yes | `NOT_STARTED` | Verify requirement completeness must be total and evidence-backed before handoff | LESSON-PREFLIGHT.json LESSON-REQ-0008 |
| `LESSON-REQ-0009` | `lesson:LSN-0009` | yes | `NOT_STARTED` | Verify a red gate requires rework, never a waiver, and never a weakened check | LESSON-PREFLIGHT.json LESSON-REQ-0009 |
| `LESSON-REQ-0010` | `lesson:LSN-0010` | yes | `NOT_STARTED` | Verify a recorded command must carry runtime, working directory, commit and purpose to be replayable | LESSON-PREFLIGHT.json LESSON-REQ-0010 |
| `LESSON-REQ-0011` | `lesson:LSN-0011` | yes | `NOT_STARTED` | Verify a control over a checkpoint's own evidence must be scoped to the moment it matters | LESSON-PREFLIGHT.json LESSON-REQ-0011 |
| `LESSON-REQ-0012` | `lesson:LSN-0012` | yes | `NOT_STARTED` | Verify sealed checkpoints and their tags are immutable, and tooling must keep validating them | LESSON-PREFLIGHT.json LESSON-REQ-0012 |
| `LESSON-REQ-0013` | `lesson:LSN-0013` | no | `NOT_STARTED` | Verify an installed capability must be detected by resolved path, not by a bare command lookup | LESSON-PREFLIGHT.json LESSON-REQ-0013 |
| `LESSON-REQ-0014` | `lesson:LSN-0014` | yes | `NOT_STARTED` | Verify evidence must be recorded as it happens, not reconstructed at the end of a run | LESSON-PREFLIGHT.json LESSON-REQ-0014 |
| `LESSON-REQ-0015` | `lesson:LSN-0015` | yes | `NOT_STARTED` | Verify every positive terminal status needs one shared promotion invariant | LESSON-PREFLIGHT.json LESSON-REQ-0015 |
| `LESSON-REQ-0016` | `lesson:LSN-0016` | yes | `NOT_STARTED` | Verify a mandatory set must be closed by policy, never chosen by the caller | LESSON-PREFLIGHT.json LESSON-REQ-0016 |
| `LESSON-REQ-0017` | `lesson:LSN-0017` | yes | `NOT_STARTED` | Verify a completeness denominator must come from a source the delivery does not own | LESSON-PREFLIGHT.json LESSON-REQ-0017 |
| `LESSON-REQ-0018` | `lesson:LSN-0018` | yes | `NOT_STARTED` | Verify a structured reference must be resolved, not merely well typed | LESSON-PREFLIGHT.json LESSON-REQ-0018 |
| `LESSON-REQ-0019` | `lesson:LSN-0019` | yes | `NOT_STARTED` | Verify a derived artifact must carry a fingerprint of the inputs that produced it | LESSON-PREFLIGHT.json LESSON-REQ-0019 |
| `LESSON-REQ-0020` | `lesson:LSN-0020` | yes | `NOT_STARTED` | Verify evidence produced from a dirty tree needs immutable input identity | LESSON-PREFLIGHT.json LESSON-REQ-0020 |
| `LESSON-REQ-0021` | `lesson:LSN-0021` | yes | `NOT_STARTED` | Verify sealed history needs an anchor outside the content it describes | LESSON-PREFLIGHT.json LESSON-REQ-0021 |
| `LESSON-REQ-0022` | `lesson:LSN-0022` | yes | `NOT_STARTED` | Verify an authoritative count must be derived once, never maintained by hand twice | LESSON-PREFLIGHT.json LESSON-REQ-0022 |
| `LESSON-REQ-0023` | `lesson:LSN-0023` | yes | `NOT_STARTED` | Verify a lesson must cite a source that actually records the finding it claims | LESSON-PREFLIGHT.json LESSON-REQ-0023 |
| `LESSON-REQ-0024` | `lesson:LSN-0024` | yes | `NOT_STARTED` | Verify a control is finished only when its positive path has been executed, not only its refusals | LESSON-PREFLIGHT.json LESSON-REQ-0024 |
| `LESSON-REQ-0025` | `lesson:LSN-0025` | yes | `NOT_STARTED` | Verify a generic guardrail derives repository state instead of naming today's checkpoint | LESSON-PREFLIGHT.json LESSON-REQ-0025 |
| `LESSON-REQ-0026` | `lesson:LSN-0026` | yes | `NOT_STARTED` | Verify an adversarial battery without a null-mutation control proves nothing | LESSON-PREFLIGHT.json LESSON-REQ-0026 |
| `LESSON-REQ-0027` | `lesson:LSN-0027` | yes | `NOT_STARTED` | Verify a lesson's prose may record a residual limit but may never contradict its status | LESSON-PREFLIGHT.json LESSON-REQ-0027 |
| `LESSON-REQ-0028` | `lesson:LSN-0028` | yes | `NOT_STARTED` | Verify a configuration key that no code reads is a defect, not documentation | LESSON-PREFLIGHT.json LESSON-REQ-0028 |
| `LESSON-REQ-0029` | `lesson:LSN-0029` | yes | `NOT_STARTED` | Verify a required protocol transition must never turn a mandatory gate red | LESSON-PREFLIGHT.json LESSON-REQ-0029 |
| `LESSON-REQ-0030` | `lesson:LSN-0031` | yes | `NOT_STARTED` | Verify an empty applicable set is not a missing required set, and a control must tell them apart | LESSON-PREFLIGHT.json LESSON-REQ-0030 |
