# Requirements Matrix - SETUP-00-CP-0008

Expected set derived by: `policies.expected_requirement_refs over docs/SETUP-00-CHECKLIST.md, .iacode/policies/canonical-requirements.json, .iacode/policies/audit-registry.json and LESSON-PREFLIGHT.json`.

| ID | Anchor | Mandatory | Status | Requirement | Source |
|---|---|---|---|---|---|
| `REQ-0001` | `canonical:SETUP-00#1.1` | yes | `COMPLETE` | A single entry point states the phase, current Gate, latest checkpoint, and start protocol. | docs/SETUP-00-CHECKLIST.md row 1.1 |
| `REQ-0002` | `canonical:SETUP-00#1.2` | yes | `COMPLETE` | A Codex adapter binds the canonical contracts without adding independent policy. | docs/SETUP-00-CHECKLIST.md row 1.2 |
| `REQ-0003` | `canonical:SETUP-00#1.3` | yes | `COMPLETE` | A Claude Code adapter binds the same contracts. | docs/SETUP-00-CHECKLIST.md row 1.3 |
| `REQ-0004` | `canonical:SETUP-00#1.4` | yes | `COMPLETE` | Tool adapters stay semantically equivalent to the canonical roles. | docs/SETUP-00-CHECKLIST.md row 1.4 |
| `REQ-0005` | `canonical:SETUP-00#2.1` | yes | `COMPLETE` | The Gate sequence, dependencies, acceptance, and fail conditions are recorded. | docs/SETUP-00-CHECKLIST.md row 2.1 |
| `REQ-0006` | `canonical:SETUP-00#2.2` | yes | `COMPLETE` | The completion standard, mandatory controls, and Git and evidence discipline are recorded. | docs/SETUP-00-CHECKLIST.md row 2.2 |
| `REQ-0007` | `canonical:SETUP-00#2.3` | yes | `COMPLETE` | Tool-to-tool transfer is formal in both directions. | docs/SETUP-00-CHECKLIST.md row 2.3 |
| `REQ-0008` | `canonical:SETUP-00#2.4` | yes | `COMPLETE` | Checkpoint statuses, required events, required contents, commit semantics, and divergence handling are defined. | docs/SETUP-00-CHECKLIST.md row 2.4 |
| `REQ-0009` | `canonical:SETUP-00#2.5` | yes | `COMPLETE` | Done is defined and excludes assertion-only PASS. | docs/SETUP-00-CHECKLIST.md row 2.5 |
| `REQ-0010` | `canonical:SETUP-00#2.6` | yes | `COMPLETE` | Quality outcomes, required dimensions, and the promotion rule are defined. | docs/SETUP-00-CHECKLIST.md row 2.6 |
| `REQ-0011` | `canonical:SETUP-00#2.7` | yes | `COMPLETE` | Structural decisions are recorded as ADRs. | docs/SETUP-00-CHECKLIST.md row 2.7 |
| `REQ-0012` | `canonical:SETUP-00#2.8` | yes | `COMPLETE` | Architecture, roadmap, provenance, model usage, and detected tool capabilities are documented. | docs/SETUP-00-CHECKLIST.md row 2.8 |
| `REQ-0013` | `canonical:SETUP-00#3.1` | yes | `COMPLETE` | The canonical, tool-neutral role contracts exist, one per role of the delivery protocol. | docs/SETUP-00-CHECKLIST.md row 3.1 |
| `REQ-0014` | `canonical:SETUP-00#3.2` | yes | `COMPLETE` | Documentation, provenance, secret, tool-execution, and training-data policies exist. | docs/SETUP-00-CHECKLIST.md row 3.2 |
| `REQ-0015` | `canonical:SETUP-00#3.3` | yes | `COMPLETE` | Reusable templates exist for ADRs, checkpoints, gate reports, and handoffs. | docs/SETUP-00-CHECKLIST.md row 3.3 |
| `REQ-0016` | `canonical:SETUP-00#4.1` | yes | `COMPLETE` | Checkpoint state, run metadata, command, test, quality, provenance, and decision schemas exist and are loadable. | docs/SETUP-00-CHECKLIST.md row 4.1 |
| `REQ-0017` | `canonical:SETUP-00#4.2` | yes | `COMPLETE` | An experience schema is reserved for Gate 6 and implements no runtime. | docs/SETUP-00-CHECKLIST.md row 4.2 |
| `REQ-0018` | `canonical:SETUP-00#4.3` | yes | `COMPLETE` | Schema evolution is versioned and never invalidates a sealed checkpoint. | docs/SETUP-00-CHECKLIST.md row 4.3 |
| `REQ-0019` | `canonical:SETUP-00#5.1` | yes | `COMPLETE` | A checkpoint can be created with truthful non-PASS defaults. | docs/SETUP-00-CHECKLIST.md row 5.1 |
| `REQ-0020` | `canonical:SETUP-00#5.2` | yes | `COMPLETE` | A checkpoint can be finalized, and every finalization attempt is recorded with its exit code. | docs/SETUP-00-CHECKLIST.md row 5.2 |
| `REQ-0021` | `canonical:SETUP-00#5.3` | yes | `COMPLETE` | A checkpoint is validated against schemas, Git state, inventory, quality evidence, and secrets. | docs/SETUP-00-CHECKLIST.md row 5.3 |
| `REQ-0022` | `canonical:SETUP-00#5.4` | yes | `COMPLETE` | Secret redaction is available and documented to its real scope. | docs/SETUP-00-CHECKLIST.md row 5.4 |
| `REQ-0023` | `canonical:SETUP-00#5.5` | yes | `COMPLETE` | The tooling is standard-library only and portable across Windows and Unix-like checkouts. | docs/SETUP-00-CHECKLIST.md row 5.5 |
| `REQ-0024` | `canonical:SETUP-00#6.1` | yes | `COMPLETE` | Every checkpoint carries status, handoff, run metadata, state, plan, decisions, commands, file inventory, tests, quality, provenance, diff summary, risks, and next action. | docs/SETUP-00-CHECKLIST.md row 6.1 |
| `REQ-0025` | `canonical:SETUP-00#6.2` | yes | `COMPLETE` | `LATEST.md` points textually to the last checkpoint accepted by validation. | docs/SETUP-00-CHECKLIST.md row 6.2 |
| `REQ-0026` | `canonical:SETUP-00#6.3` | yes | `COMPLETE` | The file inventory matches the real change set, with bound content hashes. | docs/SETUP-00-CHECKLIST.md row 6.3 |
| `REQ-0027` | `canonical:SETUP-00#6.4` | yes | `COMPLETE` | Provenance is complete and `trainingAllowed` defaults to `false`. | docs/SETUP-00-CHECKLIST.md row 6.4 |
| `REQ-0028` | `canonical:SETUP-00#6.5` | yes | `COMPLETE` | A quality `PASS` carries resolvable evidence. | docs/SETUP-00-CHECKLIST.md row 6.5 |
| `REQ-0029` | `canonical:SETUP-00#6.6` | yes | `COMPLETE` | Handoff-ready and terminal checkpoints are anchored to an immutable namespaced tag. | docs/SETUP-00-CHECKLIST.md row 6.6 |
| `REQ-0030` | `canonical:SETUP-00#7.1` | yes | `COMPLETE` | A cold-start continuation prompt exists and depends only on checked-in files. | docs/SETUP-00-CHECKLIST.md row 7.1 |
| `REQ-0031` | `canonical:SETUP-00#7.2` | yes | `COMPLETE` | Cold-start validation is executed and recorded truthfully, including a blocked attempt. | docs/SETUP-00-CHECKLIST.md row 7.2 |
| `REQ-0032` | `canonical:SETUP-00#7.3` | yes | `COMPLETE` | Cross-tool validation state is structured and explicit. | docs/SETUP-00-CHECKLIST.md row 7.3 |
| `REQ-0033` | `canonical:SETUP-00#7.4` | yes | `COMPLETE` | A sealed checkpoint can be validated from a detached checkout of its own tag. | docs/SETUP-00-CHECKLIST.md row 7.4 |
| `REQ-0034` | `canonical:SETUP-00#7.5` | yes | `COMPLETE` | The handoff is executable by another tool without the producing session. | docs/SETUP-00-CHECKLIST.md row 7.5 |
| `REQ-0035` | `canonical:SETUP-00#7b.1` | yes | `COMPLETE` | Every requirement of a delivery exists in a versioned matrix before implementation. | docs/SETUP-00-CHECKLIST.md row 7b.1 |
| `REQ-0036` | `canonical:SETUP-00#7b.2` | yes | `COMPLETE` | A Test Rework / Green Keeper role forbids shipping anything red and records every cycle. | docs/SETUP-00-CHECKLIST.md row 7b.2 |
| `REQ-0037` | `canonical:SETUP-00#7b.3` | yes | `COMPLETE` | A Delivery Completeness Validator audits the matrix before handoff and may not implement. | docs/SETUP-00-CHECKLIST.md row 7b.3 |
| `REQ-0038` | `canonical:SETUP-00#7b.4` | yes | `COMPLETE` | `GREEN_KEEPER_GATE` and `DELIVERY_COMPLETENESS_GATE` are preconditions of `READY_FOR_REVIEW`. | docs/SETUP-00-CHECKLIST.md row 7b.4 |
| `REQ-0039` | `canonical:SETUP-00#7b.5` | yes | `COMPLETE` | Readiness and blockage can never be claimed together. | docs/SETUP-00-CHECKLIST.md row 7b.5 |
| `REQ-0040` | `canonical:SETUP-00#7b.6` | yes | `COMPLETE` | Every operation attempt is recorded, including a refusal decided before execution. | docs/SETUP-00-CHECKLIST.md row 7b.6 |
| `REQ-0041` | `canonical:SETUP-00#7b.7` | yes | `COMPLETE` | Every recorded command is reproducible from its declared working directory. | docs/SETUP-00-CHECKLIST.md row 7b.7 |
| `REQ-0042` | `canonical:SETUP-00#7b.8` | yes | `COMPLETE` | The mandatory delivery order is stated in full in every governing document and both adapters. | docs/SETUP-00-CHECKLIST.md row 7b.8 |
| `REQ-0043` | `canonical:SETUP-00#7c.1` | yes | `COMPLETE` | The project keeps an organizational engineering memory of confirmed failures. | docs/SETUP-00-CHECKLIST.md row 7c.1 |
| `REQ-0044` | `canonical:SETUP-00#7c.2` | yes | `COMPLETE` | A lesson is `GUARDED` only when an automated control prevents recurrence. | docs/SETUP-00-CHECKLIST.md row 7c.2 |
| `REQ-0045` | `canonical:SETUP-00#7c.3` | yes | `COMPLETE` | A repeat increments recurrence, and a repeat against a guardrail is a `GUARDRAIL_FAILURE`. | docs/SETUP-00-CHECKLIST.md row 7c.3 |
| `REQ-0046` | `canonical:SETUP-00#7c.4` | yes | `COMPLETE` | A mandatory preflight selects the lessons that constrain each Gate. | docs/SETUP-00-CHECKLIST.md row 7c.4 |
| `REQ-0047` | `canonical:SETUP-00#7c.5` | yes | `COMPLETE` | Applicable lessons become requirements whose absence blocks completeness. | docs/SETUP-00-CHECKLIST.md row 7c.5 |
| `REQ-0048` | `canonical:SETUP-00#7c.6` | yes | `COMPLETE` | Lesson candidates can be extracted from recorded delivery evidence, never above `OBSERVED`. | docs/SETUP-00-CHECKLIST.md row 7c.6 |
| `REQ-0049` | `canonical:SETUP-00#7c.7` | yes | `COMPLETE` | External validation is grouped into milestones `M0` to `M6`. | docs/SETUP-00-CHECKLIST.md row 7c.7 |
| `REQ-0050` | `canonical:SETUP-00#7c.8` | yes | `COMPLETE` | An internal verdict is never described as independent external validation. | docs/SETUP-00-CHECKLIST.md row 7c.8 |
| `REQ-0051` | `canonical:SETUP-00#7c.9` | yes | `COMPLETE` | An extraordinary audit requires a recorded trigger. | docs/SETUP-00-CHECKLIST.md row 7c.9 |
| `REQ-0052` | `canonical:SETUP-00#7c.10` | yes | `COMPLETE` | Every completed Gate produces a retrospective. | docs/SETUP-00-CHECKLIST.md row 7c.10 |
| `REQ-0053` | `canonical:SETUP-00#7d.1` | yes | `COMPLETE` | One promotion invariant governs every positive terminal status, not only `READY_FOR_REVIEW`. | docs/SETUP-00-CHECKLIST.md row 7d.1 |
| `REQ-0054` | `canonical:SETUP-00#7d.2` | yes | `COMPLETE` | The mandatory quality gate set is a closed machine-readable registry that an invocation cannot narrow. | docs/SETUP-00-CHECKLIST.md row 7d.2 |
| `REQ-0055` | `canonical:SETUP-00#7d.3` | yes | `COMPLETE` | The expected requirement set is derived from canonical sources and compared exactly with the declared set. | docs/SETUP-00-CHECKLIST.md row 7d.3 |
| `REQ-0056` | `canonical:SETUP-00#7d.4` | yes | `COMPLETE` | An external milestone PASS is derived from an audit attestation authored by another sealed checkpoint. | docs/SETUP-00-CHECKLIST.md row 7d.4 |
| `REQ-0057` | `canonical:SETUP-00#7d.5` | yes | `COMPLETE` | A derived artifact carries a fingerprint of its inputs, and staleness is decided by recomputation. | docs/SETUP-00-CHECKLIST.md row 7d.5 |
| `REQ-0058` | `canonical:SETUP-00#7d.6` | yes | `COMPLETE` | Every lesson control, evidence path and provenance locator is resolved against the repository. | docs/SETUP-00-CHECKLIST.md row 7d.6 |
| `REQ-0059` | `canonical:SETUP-00#7d.7` | yes | `COMPLETE` | Every `GUARDED` lesson names a registered guardrail, and guardrail effectiveness is measured. | docs/SETUP-00-CHECKLIST.md row 7d.7 |
| `REQ-0060` | `canonical:SETUP-00#7d.8` | yes | `COMPLETE` | Sealed checkpoints are anchored by a hash-linked chain over tag, commit and tree. | docs/SETUP-00-CHECKLIST.md row 7d.8 |
| `REQ-0061` | `canonical:SETUP-00#7d.9` | yes | `COMPLETE` | Every count used as evidence is derived once and verified wherever a report states it. | docs/SETUP-00-CHECKLIST.md row 7d.9 |
| `REQ-0062` | `canonical:SETUP-00#7d.10` | yes | `COMPLETE` | Sealing is monotonic and post-commit, and every recorded command binds its declared inputs by content. | docs/SETUP-00-CHECKLIST.md row 7d.10 |
| `REQ-0063` | `canonical:SETUP-00#7d.11` | yes | `COMPLETE` | A milestone delivery carries an internal Red Team and an internal mirror audit, and neither is recorded as external validation. | docs/SETUP-00-CHECKLIST.md row 7d.11 |
| `REQ-0064` | `canonical:SETUP-00#7d.12` | yes | `COMPLETE` | Every finding of an independent audit is closed before the corrective delivery is offered. | docs/SETUP-00-CHECKLIST.md row 7d.12 |
| `REQ-0065` | `canonical:SETUP-00#8.1` | yes | `COMPLETE` | An independent review is recorded. | docs/SETUP-00-CHECKLIST.md row 8.1 |
| `REQ-0066` | `canonical:SETUP-00#8.2` | yes | `COMPLETE` | An adversarial Red Team is recorded. | docs/SETUP-00-CHECKLIST.md row 8.2 |
| `REQ-0067` | `canonical:SETUP-00#8.3` | yes | `COMPLETE` | `GATE_PASS` is granted only by a run independent of the implementer. | docs/SETUP-00-CHECKLIST.md row 8.3 |
| `REQ-0068` | `canonical:SETUP-00#9.1` | yes | `COMPLETE` | No Gate 0 or later runtime is implemented during SETUP-00. | docs/SETUP-00-CHECKLIST.md row 9.1 |
| `REQ-0069` | `canonical:SETUP-00#9.2` | yes | `COMPLETE` | Documentation is maintained continuously rather than reconstructed at the end. | docs/SETUP-00-CHECKLIST.md row 9.2 |
| `REQ-0070` | `canonical:SETUP-00#9.3` | yes | `COMPLETE` | No secret, credential, or private chain-of-thought is stored. | docs/SETUP-00-CHECKLIST.md row 9.3 |
| `REQ-0071` | `canonical:SETUP-00#9.4` | yes | `COMPLETE` | Gate advancement requires explicit authorization and a passing previous Gate. | docs/SETUP-00-CHECKLIST.md row 9.4 |
| `REQ-0072` | `finding:M0-F-001` | yes | `COMPLETE` | positive terminal status bypasses delivery assurance | M0-CP-0007 docs/checkpoints/SETUP-00-CP-0007/REVIEW-REPORT.md M0-F-001 |
| `REQ-0073` | `finding:M0-F-002` | yes | `COMPLETE` | external milestone PASS can be self-asserted on an intermediate Gate | M0-CP-0007 docs/checkpoints/SETUP-00-CP-0007/REVIEW-REPORT.md M0-F-002 |
| `REQ-0074` | `finding:M0-F-003` | yes | `COMPLETE` | lesson preflight is not bound to the checkpoint Gate or canonical memory | M0-CP-0007 docs/checkpoints/SETUP-00-CP-0007/REVIEW-REPORT.md M0-F-003 |
| `REQ-0075` | `finding:M0-F-004` | yes | `COMPLETE` | Engineering Memory accepts forged controls, missing evidence, and nested secrets | M0-CP-0007 docs/checkpoints/SETUP-00-CP-0007/REVIEW-REPORT.md M0-F-004 |
| `REQ-0076` | `finding:M0-F-005` | yes | `COMPLETE` | Green Keeper has a vacuous PASS path | M0-CP-0007 docs/checkpoints/SETUP-00-CP-0007/REVIEW-REPORT.md M0-F-005 |
| `REQ-0077` | `finding:M0-F-006` | yes | `COMPLETE` | completeness denominator is not anchored | M0-CP-0007 docs/checkpoints/SETUP-00-CP-0007/REVIEW-REPORT.md M0-F-006 |
| `REQ-0078` | `finding:M0-F-007` | yes | `COMPLETE` | historical immutability is not anchored externally | M0-CP-0007 docs/checkpoints/SETUP-00-CP-0007/REVIEW-REPORT.md M0-F-007 |
| `REQ-0079` | `finding:M0-F-008` | yes | `COMPLETE` | CP-0006 mandatory count is contradictory and accepted | M0-CP-0007 docs/checkpoints/SETUP-00-CP-0007/REVIEW-REPORT.md M0-F-008 |
| `REQ-0080` | `finding:M0-F-009` | yes | `COMPLETE` | command records are not reproducible at their declared commits | M0-CP-0007 docs/checkpoints/SETUP-00-CP-0007/REVIEW-REPORT.md M0-F-009 |
| `REQ-0081` | `finding:M0-F-010` | yes | `COMPLETE` | sealed finalization chronology is internally inconsistent | M0-CP-0007 docs/checkpoints/SETUP-00-CP-0007/REVIEW-REPORT.md M0-F-010 |
| `REQ-0082` | `finding:M0-F-011` | yes | `COMPLETE` | one lesson source locator is inaccurate | M0-CP-0007 docs/checkpoints/SETUP-00-CP-0007/REVIEW-REPORT.md M0-F-011 |
| `REQ-0083` | `attack:A` | yes | `COMPLETE` | Defend attack A: Add blocker to `READY_FOR_REVIEW` | M0-CP-0007 docs/checkpoints/SETUP-00-CP-0007/RED-TEAM-REPORT.md attack A |
| `REQ-0084` | `attack:B` | yes | `COMPLETE` | Defend attack B: Set a review-ready quality gate red | M0-CP-0007 docs/checkpoints/SETUP-00-CP-0007/RED-TEAM-REPORT.md attack B |
| `REQ-0085` | `attack:C` | yes | `COMPLETE` | Defend attack C: Delete mandatory `REQ-0001` and recompute all counts | M0-CP-0007 docs/checkpoints/SETUP-00-CP-0007/RED-TEAM-REPORT.md attack C |
| `REQ-0086` | `attack:D` | yes | `COMPLETE` | Defend attack D: Forge stored 100% counts | M0-CP-0007 docs/checkpoints/SETUP-00-CP-0007/RED-TEAM-REPORT.md attack D |
| `REQ-0087` | `attack:E` | yes | `COMPLETE` | Defend attack E: Remove a derived requirement | M0-CP-0007 docs/checkpoints/SETUP-00-CP-0007/RED-TEAM-REPORT.md attack E |
| `REQ-0088` | `attack:F` | yes | `COMPLETE` | Defend attack F: Replace prevention with documentation only | M0-CP-0007 docs/checkpoints/SETUP-00-CP-0007/RED-TEAM-REPORT.md attack F |
| `REQ-0089` | `attack:G` | yes | `COMPLETE` | Defend attack G: Duplicate lesson ID | M0-CP-0007 docs/checkpoints/SETUP-00-CP-0007/RED-TEAM-REPORT.md attack G |
| `REQ-0090` | `attack:H` | yes | `COMPLETE` | Defend attack H: Insert a secret-shaped value in a scanned field | M0-CP-0007 docs/checkpoints/SETUP-00-CP-0007/RED-TEAM-REPORT.md attack H |
| `REQ-0091` | `attack:I` | yes | `COMPLETE` | Defend attack I: Rewrite CP-0005, declare it in CP-0006 inventory, refresh hashes, move CP-0006 tag | M0-CP-0007 docs/checkpoints/SETUP-00-CP-0007/RED-TEAM-REPORT.md attack I |
| `REQ-0092` | `attack:J` | yes | `COMPLETE` | Defend attack J: Move CP-0006 tag and HEAD together to a new commit | M0-CP-0007 docs/checkpoints/SETUP-00-CP-0007/RED-TEAM-REPORT.md attack J |
| `REQ-0093` | `attack:K` | yes | `COMPLETE` | Defend attack K: Remove one inventory entry | M0-CP-0007 docs/checkpoints/SETUP-00-CP-0007/RED-TEAM-REPORT.md attack K |
| `REQ-0094` | `attack:L` | yes | `COMPLETE` | Defend attack L: Silently modify a tracked file | M0-CP-0007 docs/checkpoints/SETUP-00-CP-0007/RED-TEAM-REPORT.md attack L |
| `REQ-0095` | `attack:M` | yes | `COMPLETE` | Defend attack M: Set a wrong `hashBefore` | M0-CP-0007 docs/checkpoints/SETUP-00-CP-0007/RED-TEAM-REPORT.md attack M |
| `REQ-0096` | `attack:N` | yes | `COMPLETE` | Defend attack N: Set a wrong `hashAfter` | M0-CP-0007 docs/checkpoints/SETUP-00-CP-0007/RED-TEAM-REPORT.md attack N |
| `REQ-0097` | `attack:O` | yes | `COMPLETE` | Defend attack O: Claim PASS with no evidence | M0-CP-0007 docs/checkpoints/SETUP-00-CP-0007/RED-TEAM-REPORT.md attack O |
| `REQ-0098` | `attack:P` | yes | `COMPLETE` | Defend attack P: Reference an unknown command | M0-CP-0007 docs/checkpoints/SETUP-00-CP-0007/RED-TEAM-REPORT.md attack P |
| `REQ-0099` | `attack:Q` | yes | `COMPLETE` | Defend attack Q: Supply arbitrary complete attribution with empty evidence | M0-CP-0007 docs/checkpoints/SETUP-00-CP-0007/RED-TEAM-REPORT.md attack Q |
| `REQ-0100` | `attack:R` | yes | `COMPLETE` | Defend attack R: Promote an internally authored result to external status | M0-CP-0007 docs/checkpoints/SETUP-00-CP-0007/RED-TEAM-REPORT.md attack R |
| `REQ-0101` | `attack:S` | yes | `COMPLETE` | Defend attack S: Leave review/Red Team pending and auditor/time null | M0-CP-0007 docs/checkpoints/SETUP-00-CP-0007/RED-TEAM-REPORT.md attack S |
| `REQ-0102` | `attack:T` | yes | `COMPLETE` | Defend attack T: Request audit without a known trigger | M0-CP-0007 docs/checkpoints/SETUP-00-CP-0007/RED-TEAM-REPORT.md attack T |
| `REQ-0103` | `attack:U` | yes | `COMPLETE` | Defend attack U: Retire canonical lesson but keep stale active preflight | M0-CP-0007 docs/checkpoints/SETUP-00-CP-0007/RED-TEAM-REPORT.md attack U |
| `REQ-0104` | `attack:V` | yes | `COMPLETE` | Defend attack V: Run `--gates ""`, then retain PASS with an actually failing test | M0-CP-0007 docs/checkpoints/SETUP-00-CP-0007/RED-TEAM-REPORT.md attack V |
| `REQ-0105` | `attack:W` | yes | `COMPLETE` | Defend attack W: Claim PASS with a PARTIAL row | M0-CP-0007 docs/checkpoints/SETUP-00-CP-0007/RED-TEAM-REPORT.md attack W |
| `REQ-0106` | `attack:X` | yes | `COMPLETE` | Defend attack X: Remove required runtime/record field | M0-CP-0007 docs/checkpoints/SETUP-00-CP-0007/RED-TEAM-REPORT.md attack X |
| `REQ-0107` | `attack:Y` | yes | `COMPLETE` | Defend attack Y: Point `LATEST.md` at CP-0005 while validating CP-0006 | M0-CP-0007 docs/checkpoints/SETUP-00-CP-0007/RED-TEAM-REPORT.md attack Y |
| `REQ-0108` | `attack:Z` | yes | `COMPLETE` | Defend attack Z: Use path traversal as checkpoint/Gate input | M0-CP-0007 docs/checkpoints/SETUP-00-CP-0007/RED-TEAM-REPORT.md attack Z |
| `LESSON-REQ-0001` | `lesson:LSN-0001` | yes | `COMPLETE` | Verify checkpoint validation must succeed from a detached checkout of the checkpoint tag | LESSON-PREFLIGHT.json LESSON-REQ-0001 |
| `LESSON-REQ-0002` | `lesson:LSN-0002` | yes | `COMPLETE` | Verify a file inventory must be recomputed from the repository, never trusted as an assertion | LESSON-PREFLIGHT.json LESSON-REQ-0002 |
| `LESSON-REQ-0003` | `lesson:LSN-0003` | yes | `COMPLETE` | Verify every operation attempt must be auditable, including a refusal decided before execution | LESSON-PREFLIGHT.json LESSON-REQ-0003 |
| `LESSON-REQ-0004` | `lesson:LSN-0004` | yes | `COMPLETE` | Verify a checkpoint may never claim readiness while it also claims to be blocked | LESSON-PREFLIGHT.json LESSON-REQ-0004 |
| `LESSON-REQ-0005` | `lesson:LSN-0005` | yes | `COMPLETE` | Verify a PASS requires evidence that can be executed or resolved, not a statement | LESSON-PREFLIGHT.json LESSON-REQ-0005 |
| `LESSON-REQ-0006` | `lesson:LSN-0006` | yes | `COMPLETE` | Verify the repository must be self-contained; a specification may not live outside it | LESSON-PREFLIGHT.json LESSON-REQ-0006 |
| `LESSON-REQ-0007` | `lesson:LSN-0007` | yes | `COMPLETE` | Verify independent validation cannot be declared by the run that did the work | LESSON-PREFLIGHT.json LESSON-REQ-0007 |
| `LESSON-REQ-0008` | `lesson:LSN-0008` | yes | `COMPLETE` | Verify requirement completeness must be total and evidence-backed before handoff | LESSON-PREFLIGHT.json LESSON-REQ-0008 |
| `LESSON-REQ-0009` | `lesson:LSN-0009` | yes | `COMPLETE` | Verify a red gate requires rework, never a waiver, and never a weakened check | LESSON-PREFLIGHT.json LESSON-REQ-0009 |
| `LESSON-REQ-0010` | `lesson:LSN-0010` | yes | `COMPLETE` | Verify a recorded command must carry runtime, working directory, commit and purpose to be replayable | LESSON-PREFLIGHT.json LESSON-REQ-0010 |
| `LESSON-REQ-0011` | `lesson:LSN-0011` | yes | `COMPLETE` | Verify a control over a checkpoint's own evidence must be scoped to the moment it matters | LESSON-PREFLIGHT.json LESSON-REQ-0011 |
| `LESSON-REQ-0012` | `lesson:LSN-0012` | yes | `COMPLETE` | Verify sealed checkpoints and their tags are immutable, and tooling must keep validating them | LESSON-PREFLIGHT.json LESSON-REQ-0012 |
| `LESSON-REQ-0013` | `lesson:LSN-0013` | no | `COMPLETE` | Verify an installed capability must be detected by resolved path, not by a bare command lookup | LESSON-PREFLIGHT.json LESSON-REQ-0013 |
| `LESSON-REQ-0014` | `lesson:LSN-0014` | yes | `COMPLETE` | Verify evidence must be recorded as it happens, not reconstructed at the end of a run | LESSON-PREFLIGHT.json LESSON-REQ-0014 |
| `LESSON-REQ-0015` | `lesson:LSN-0015` | yes | `COMPLETE` | Verify every positive terminal status needs one shared promotion invariant | LESSON-PREFLIGHT.json LESSON-REQ-0015 |
| `LESSON-REQ-0016` | `lesson:LSN-0016` | yes | `COMPLETE` | Verify a mandatory set must be closed by policy, never chosen by the caller | LESSON-PREFLIGHT.json LESSON-REQ-0016 |
| `LESSON-REQ-0017` | `lesson:LSN-0017` | yes | `COMPLETE` | Verify a completeness denominator must come from a source the delivery does not own | LESSON-PREFLIGHT.json LESSON-REQ-0017 |
| `LESSON-REQ-0018` | `lesson:LSN-0018` | yes | `COMPLETE` | Verify a structured reference must be resolved, not merely well typed | LESSON-PREFLIGHT.json LESSON-REQ-0018 |
| `LESSON-REQ-0019` | `lesson:LSN-0019` | yes | `COMPLETE` | Verify a derived artifact must carry a fingerprint of the inputs that produced it | LESSON-PREFLIGHT.json LESSON-REQ-0019 |
| `LESSON-REQ-0020` | `lesson:LSN-0020` | yes | `COMPLETE` | Verify evidence produced from a dirty tree needs immutable input identity | LESSON-PREFLIGHT.json LESSON-REQ-0020 |
| `LESSON-REQ-0021` | `lesson:LSN-0021` | yes | `COMPLETE` | Verify sealed history needs an anchor outside the content it describes | LESSON-PREFLIGHT.json LESSON-REQ-0021 |
| `LESSON-REQ-0022` | `lesson:LSN-0022` | yes | `COMPLETE` | Verify an authoritative count must be derived once, never maintained by hand twice | LESSON-PREFLIGHT.json LESSON-REQ-0022 |
| `LESSON-REQ-0023` | `lesson:LSN-0023` | yes | `COMPLETE` | Verify a lesson must cite a source that actually records the finding it claims | LESSON-PREFLIGHT.json LESSON-REQ-0023 |
