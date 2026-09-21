# Red Team Report — M0 / SETUP-00

Result: `RED_TEAM_PASS`
Mandatory battery: `26/26` defended
Additional battery: `26/26` defended
Escapes: `0`

Every attack in this report was written by the auditor. The delivery's own
`m0_red_team.py` was executed once, separately, as one of the handoff's validation commands,
but no attack below imports it: a `DEFENDED` verdict here is a statement about the product,
not about the product's own harness.

Every mutation ran inside a disposable clone under the session scratchpad. No tag, commit or
artifact of the real repository was written to. The harness re-seals each mutation the way
`seal_checkpoint.py` does, and restores every namespaced tag between attacks, so a rejection
is attributable to the mutation under test; a null-mutation control through the same path
validates, which is what makes that claim checkable.

## Mandatory battery, re-parsed from the sealed `SETUP-00-CP-0007` report

| Attack | Target | Mutation | Expected | Observed | Result |
|---|---|---|---|---|---|
| A | readiness and blocker invariant | Add a blocker to a READY_FOR_REVIEW checkpoint | reject | exit=1 CHECKPOINT_INVALID / - READY_FOR_REVIEW is incompatible with a non-empty blockedBy: an unresolved blocker planted by the CP-0009 audit | `DEFENDED` |
| B | mandatory quality | Set a review-ready quality dimension red | reject | exit=1 CHECKPOINT_INVALID / - greenKeeper=PASS contradicts QUALITY.json unitTests=FAIL / - READY_FOR_REVIEW cannot have QUALITY.json unitTests=FAIL | `DEFENDED` |
| C | completeness denominator | Delete a canonical requirement and recompute every count | reject | exit=1 CHECKPOINT_INVALID / - COMPLETENESS-REPORT.json expectedRequirements=130 contradicts the recomputed value 131 / - COMPLETENESS-REPORT.json result='PASS' contradicts the reco… | `DEFENDED` |
| D | completeness claims | Forge the stored counts of a passing report | reject | exit=1 CHECKPOINT_INVALID / - COMPLETENESS-REPORT.json totalRequirements=999 contradicts the recomputed value 131 / - COMPLETENESS-REPORT.json complete=999 contradicts the recomput… | `DEFENDED` |
| E | lesson-derived requirement | Remove a lesson-derived requirement from the matrix | reject | exit=1 CHECKPOINT_INVALID / - COMPLETENESS-REPORT.json expectedRequirements=130 contradicts the recomputed value 131 / - COMPLETENESS-REPORT.json result='PASS' contradicts the reco… | `DEFENDED` |
| F | GUARDED semantics | Replace a preventive control with documentation only | reject | exit=1 LESSONS_INVALID / - LSN-0001: GUARDED requires at least one preventive control of kind test, validator, lint, policy, schema, invariant, automated-check; documentation alone… | `DEFENDED` |
| G | lesson identity | Duplicate a lesson identifier | reject | exit=1 LESSONS_INVALID / - LSN-0001: duplicate lessonId / - LSN-0001: recurrenceKey 'checkpoint/removing-entry-files-json-silently-altering' is already used by LSN-0002; a repeat m… | `DEFENDED` |
| H | lesson secret handling | Insert a secret-shaped value into a scanned field | reject | exit=1 LESSONS_INVALID / - LSN-0001: secret pattern detected in $.symptom: GitHub credential | `DEFENDED` |
| I | sealed predecessor | Rewrite a sealed predecessor, refresh hashes and move its tag | reject | exit=1 CHECKPOINT_INVALID / - checkpoint integrity: SETUP-00-CP-0007: tag refs/tags/iacode-checkpoints/SETUP-00-CP-0007 resolves to a552e918df0d3c5eb632fdc931f0c2dc90ea51c7, not th… | `DEFENDED` |
| J | tag immutability | Move a checkpoint tag and HEAD together | reject | exit=1 CHECKPOINT_INVALID / - checkpoint integrity: SETUP-00-CP-0006: tag refs/tags/iacode-checkpoints/SETUP-00-CP-0006 resolves to 855edcfcfc19bbb9281670f18e2bc88a746de3f2, not th… | `DEFENDED` |
| K | file inventory | Remove one inventory entry | reject | exit=1 CHECKPOINT_INVALID / - FILES.json omits a changed path: .claude/agents/m0-closure-auditor.md (added) | `DEFENDED` |
| L | file inventory | Silently modify a tracked file | reject | exit=1 CHECKPOINT_INVALID / - greenKeeper=PASS is STALE: the delivery-assurance scope changed after the last GREEN cycle, so the Green Keeper must run again / - DELIVERY_COMPLETENE… | `DEFENDED` |
| M | file inventory | Set a wrong hashBefore | reject | exit=1 CHECKPOINT_INVALID / - FILES.json hashBefore does not match the baseCommit content of .iacode/memory/LESSONS.md | `DEFENDED` |
| N | file inventory | Set a wrong hashAfter | reject | exit=1 CHECKPOINT_INVALID / - FILES.json: hash mismatch for .claude/agents/m0-closure-auditor.md / - FILES.json hashAfter does not match the repository content of .claude/agents/m0… | `DEFENDED` |
| O | quality evidence | Claim PASS with no evidence | reject | exit=1 CHECKPOINT_INVALID / - QUALITY.json staticAnalysis=PASS requires at least one evidence reference | `DEFENDED` |
| P | evidence resolution | Reference an unknown command | reject | exit=1 CHECKPOINT_INVALID / - QUALITY.json staticAnalysis references an unknown command id 'cmd-9999' | `DEFENDED` |
| Q | second-tool evidence | Supply complete attribution with empty evidence | reject | exit=1 CHECKPOINT_INVALID / - GATE_PASS requires an independent review verdict, found 'PENDING' / - GATE_PASS requires a Red Team verdict, found 'PENDING' / - external validation: … | `DEFENDED` |
| R | pass vocabulary | Promote an internally authored result to an external status | reject | exit=1 CHECKPOINT_INVALID / - MILESTONE_EXTERNAL_PASS requires an independent review verdict, found 'PENDING' / - MILESTONE_EXTERNAL_PASS requires a Red Team verdict, found 'PENDIN… | `DEFENDED` |
| S | external milestone review | Leave review and Red Team pending with a null auditor | reject | exit=1 CHECKPOINT_INVALID / - MILESTONE_EXTERNAL_PASS requires an independent review verdict, found 'PENDING' / - MILESTONE_EXTERNAL_PASS requires a Red Team verdict, found 'PENDIN… | `DEFENDED` |
| T | extraordinary cadence | Request an audit without a known trigger | reject | exit=1 CHECKPOINT_INVALID / - externalAuditReason must name one of the recorded triggers: security-boundary, sandbox-boundary, rights-or-provenance-change, training-data-policy, tr… | `DEFENDED` |
| U | preflight freshness | Retire a canonical lesson but keep the active preflight | reject | exit=1 CHECKPOINT_INVALID / - greenKeeper=PASS is STALE: the delivery-assurance scope changed after the last GREEN cycle, so the Green Keeper must run again / - DELIVERY_COMPLETENE… | `DEFENDED` |
| V | Green Keeper mandatory set | Run the Green Keeper with an empty gate selection | reject | exit=1 recorded cycle measured checkpointValidation,integrity,lessons,staticAnalysis,tests against the canonical checkpointValidation,integrity,lessons,staticAnalysis,tests; comman… | `DEFENDED` |
| W | partial completeness | Claim PASS with a PARTIAL requirement | reject | exit=1 CHECKPOINT_INVALID / - STATE.json requirementsMatrix.complete=131 does not match the matrix value 130 / - STATE.json requirementsMatrix.partial=0 does not match the matrix v… | `DEFENDED` |
| X | command audit | Remove a required field from a command record | reject | exit=1 CHECKPOINT_INVALID / - COMMANDS.jsonl:1: schemaVersion 3.0.0 requires runtime | `DEFENDED` |
| Y | latest pointer | Point LATEST.md at an older checkpoint | reject | exit=1 CHECKPOINT_INVALID / - requested checkpoint is not the LATEST target: C:\Users\cesar\AppData\Local\Temp\claude\E--iacode\b305dd77-f117-4885-9aeb-0239c66d22e6\scratchpad\audi… | `DEFENDED` |
| Z | path safety | Use path traversal as the Gate identifier | reject | exit=2 usage: new_checkpoint.py [-h] [--root ROOT] --gate GATE / [--status {NOT_STARTED,BASELINING,IN_PROGRESS,BLOCKED,READY_FOR_REVIEW,REWORK_REQUIRED,READY_FOR_RED_TEAM,INTERNAL_… | `DEFENDED` |

## Additional battery, including every surface `SETUP-00-CP-0008` introduced

| Attack | Target | Mutation | Expected | Observed | Result |
|---|---|---|---|---|---|
| AA | aggregate consistency | Contradict the matrix in the recorded state aggregate | reject | exit=1 CHECKPOINT_INVALID / - STATE.json requirementsMatrix.mandatory=999 does not match the matrix value 130 | `DEFENDED` |
| AB | control resolution | Point a GUARDED lesson at a nonexistent test | reject | exit=1 LESSONS_INVALID / - LSN-0001: control names the test 'NoSuchTests.test_nothing', which does not exist in the suite | `DEFENDED` |
| AC | evidence resolution | Point lesson evidence at a nonexistent file | reject | exit=1 LESSONS_INVALID / - LSN-0001: evidence file does not exist: file:docs/does-not-exist.md | `DEFENDED` |
| AD | nested secret scan | Hide a secret-shaped value inside prevention.description | reject | exit=1 LESSONS_INVALID / - LSN-0001: secret pattern detected in $.prevention[0].description: GitHub credential | `DEFENDED` |
| AE | preflight gate binding | Reuse a SETUP-00 preflight for another Gate | reject | exit=1 CHECKPOINT_INVALID / - STATE.json lessonPreflight.gate does not match LESSON-PREFLIGHT.json / - lesson preflight: the preflight was generated for gate 'SETUP-00' but the che… | `DEFENDED` |
| AF | promotion invariant | External status with a red Green Keeper | reject | exit=1 CHECKPOINT_INVALID / - MILESTONE_EXTERNAL_PASS requires GREEN_KEEPER_GATE=PASS, found 'FAIL' / - MILESTONE_EXTERNAL_PASS requires an independent review verdict, found 'PENDI… | `DEFENDED` |
| AG | gate registry | Remove a mandatory gate from the policy after a green cycle | reject | exit=1 CHECKPOINT_INVALID / - greenKeeper=PASS was measured against checkpointValidation, integrity, lessons, staticAnalysis, tests, not the canonical mandatory set checkpointValid… | `DEFENDED` |
| AH | gate staleness | Edit the assurance scope after the last green cycle | reject | exit=1 CHECKPOINT_INVALID / - COMMANDS.jsonl:60: the record claims a clean tree at 3a143911fc01 but the input scripts/development-ledger/validate_checkpoint.py had different conten… | `DEFENDED` |
| AI | external attestation | Attest the subject with the subject's own checkpoint | reject | exit=1 CHECKPOINT_INVALID / - greenKeeper=PASS is STALE: the delivery-assurance scope changed after the last GREEN cycle, so the Green Keeper must run again / - DELIVERY_COMPLETENE… | `DEFENDED` |
| AJ | external attestation | Claim an external PASS over a failed review | reject | exit=1 CHECKPOINT_INVALID / - greenKeeper=PASS is STALE: the delivery-assurance scope changed after the last GREEN cycle, so the Green Keeper must run again / - DELIVERY_COMPLETENE… | `DEFENDED` |
| AK | external attestation | Attest a different commit than the one promoted | reject | exit=1 CHECKPOINT_INVALID / - greenKeeper=PASS is STALE: the delivery-assurance scope changed after the last GREEN cycle, so the Green Keeper must run again / - DELIVERY_COMPLETENE… | `DEFENDED` |
| AL | derived counts | Forge a stored derived count | reject | exit=1 CHECKPOINT_INVALID / - COUNTS.json TESTS=999/999 contradicts the derived 306/306 | `DEFENDED` |
| AM | count consistency | State a contradicting count in Markdown | reject | exit=1 CHECKPOINT_INVALID / - FINAL-REPORT.md states 999/999 TESTS, which contradicts the derived 306/306 | `DEFENDED` |
| AN | findings closure | Offer the delivery with an audit finding still open | reject | exit=1 CHECKPOINT_INVALID / - CP7-FINDINGS-CLOSURE.json: closed does not match the recorded findings / - CP7-FINDINGS-CLOSURE.json: a finding that is not CLOSED cannot produce resu… | `DEFENDED` |
| AO | internal Red Team | Keep a PASS verdict while an attack escaped | reject | exit=1 CHECKPOINT_INVALID / - M0-INTERNAL-RED-TEAM.json: defended does not match the recorded attacks / - M0-INTERNAL-RED-TEAM.json: escaped does not match the recorded attacks / -… | `DEFENDED` |
| AP | internal mirror audit | Keep a PASS verdict while a mirror check failed | reject | exit=1 CHECKPOINT_INVALID / - M0-INTERNAL-MIRROR.json: failed does not match the recorded checks / - M0-INTERNAL-MIRROR.json: a failed check cannot produce a PASS | `DEFENDED` |
| AQ | guardrail registry | Verify a guardrail with a test that does not exist | reject | exit=1 LESSONS_INVALID / - LSN-0001: guardrail 'GRD-0001' is verified by 'NoSuchTests.test_nothing', which does not exist in the suite | `DEFENDED` |
| AR | integrity anchors | Break the link between two anchors | reject | exit=1 INTEGRITY_INVALID / - SETUP-00-CP-0004: anchorHash does not match its own anchored fields (recorded 'a5c174320d6fae29d2e94c20a5de08c8617cfa3c18d3f4946c6f0915c710b3bb', recom… | `DEFENDED` |
| AS | command replay context | Remove the content binding of recorded inputs | reject | exit=1 CHECKPOINT_INVALID / - COMMANDS.jsonl:1: schemaVersion 3.2.0 requires inputsDigest binding every declared input by content / - COMMANDS.jsonl:2: schemaVersion 3.2.0 requires… | `DEFENDED` |
| AT | seal chronology | Remove the post-commit validation of the sealed content | reject | exit=1 CHECKPOINT_INVALID / - READY_FOR_REVIEW requires a recorded post-commit-validation run with exit code 0 over a clean worktree; the sealed content must be validated as commit… | `DEFENDED` |
| AU | external attestation | Reuse an attestation written for another checkpoint | reject | exit=1 CHECKPOINT_INVALID / - greenKeeper=PASS is STALE: the delivery-assurance scope changed after the last GREEN cycle, so the Green Keeper must run again / - DELIVERY_COMPLETENE… | `DEFENDED` |
| AV | external attestation | Claim an external PASS over a failed Red Team | reject | exit=1 CHECKPOINT_INVALID / - greenKeeper=PASS is STALE: the delivery-assurance scope changed after the last GREEN cycle, so the Green Keeper must run again / - DELIVERY_COMPLETENE… | `DEFENDED` |
| AW | external attestation | Claim an external PASS over an incomplete audit | reject | exit=1 CHECKPOINT_INVALID / - greenKeeper=PASS is STALE: the delivery-assurance scope changed after the last GREEN cycle, so the Green Keeper must run again / - DELIVERY_COMPLETENE… | `DEFENDED` |
| AX | external attestation | Attest from a checkpoint that is unsealed and unanchored | reject | exit=1 CHECKPOINT_INVALID / - greenKeeper=PASS is STALE: the delivery-assurance scope changed after the last GREEN cycle, so the Green Keeper must run again / - DELIVERY_COMPLETENE… | `DEFENDED` |
| AY | external attestation | Attest with no auditor role recorded | reject | exit=1 CHECKPOINT_INVALID / - greenKeeper=PASS is STALE: the delivery-assurance scope changed after the last GREEN cycle, so the Green Keeper must run again / - DELIVERY_COMPLETENE… | `DEFENDED` |
| AZ | external attestation | Claim an external PASS over a failed test result | reject | exit=1 CHECKPOINT_INVALID / - greenKeeper=PASS is STALE: the delivery-assurance scope changed after the last GREEN cycle, so the Green Keeper must run again / - DELIVERY_COMPLETENE… | `DEFENDED` |

## Positive control

A battery that only shows refusals cannot distinguish a control from a wall.

| Control | Expectation | Observed | Result |
|---|---|---|---|
| POS-EXT | A structurally legitimate external PASS is accepted | exit=1 CHECKPOINT_INVALID / - greenKeeper=PASS is STALE: the delivery-assurance scope changed after the last GREEN cycle, so the Green Keeper must run again / - DELIVERY_COMPLETENESS_GATE is STALE: the code, requirements, lessons or policy … | `REFUSED` |

`POS-EXT` is the only control in this report that did not behave as a working mechanism
should. It is not an attack escape, so it does not change `RED_TEAM_PASS`; it is reported as
finding `CP9-F-001` in `REVIEW-REPORT.md`, because a control that refuses the legitimate case
is a defect of the control rather than a defence.

## Assurance scenarios executed through the product's validation entry points

| Scenario | Mutation | Observed | Result |
|---|---|---|---|
| GK-001 | requiredGates empty in the recorded cycle | greenKeeper=PASS was measured against no gate, not the canonical mandatory set checkpointValidation, integrity, lessons, staticAnalysis, tests | `DEFENDED` |
| GK-002 | one mandatory gate omitted from the cycle | greenKeeper=PASS was measured against checkpointValidation, integrity, staticAnalysis, tests, not the canonical mandatory set checkpointValidation, integrity, lessons, staticAnalys… | `DEFENDED` |
| GK-003 | a mandatory gate recorded as not executed | greenKeeper=PASS records the mandatory gate 'tests' exiting None | `DEFENDED` |
| GK-004 | a mandatory gate that exited nonzero | greenKeeper=PASS records the mandatory gate 'tests' exiting 1 | `DEFENDED` |
| GK-005 | a mandatory gate with no command evidence | greenKeeper=PASS records no command evidence for the gate 'checkpointValidation' greenKeeper=PASS records no command evidence for the gate 'integrity' greenKeeper=PASS records no c… | `DEFENDED` |
| GK-006 | a PASS carrying remaining failures | greenKeeper=PASS requires remainingFailures to be zero | `DEFENDED` |
| GK-007 | a PASS carrying unresolved rework items | greenKeeper=PASS requires unresolvedReworkItems to be zero | `DEFENDED` |
| GK-008 | a fabricated PASS over a red cycle in the log | greenKeeper=PASS contradicts the last rework cycle result 'RED' | `DEFENDED` |
| GK-009 | a PASS whose fingerprint no longer describes the scope | greenKeeper=PASS is STALE: the delivery-assurance scope changed after the last GREEN cycle, so the Green Keeper must run again | `DEFENDED` |
| GK-010 | the mandatory set is the policy registry, not the caller's argument | mandatory_gates(ROOT) = tests,staticAnalysis,lessons,integrity,checkpointValidation | `DEFENDED` |
| DC-001 | a canonical requirement removed | READY_FOR_REVIEW blocked by canonical:SETUP-00#1.1: the canonical expected set requires canonical:SETUP-00#1.1 (docs/SETUP-00-CHECKLIST.md row 1.1) but the matrix does not declare … | `DEFENDED` |
| DC-002 | a lesson-derived requirement removed | READY_FOR_REVIEW blocked by lesson:LSN-0001: the canonical expected set requires lesson:LSN-0001 (LESSON-PREFLIGHT.json LESSON-REQ-0001) but the matrix does not declare it | `DEFENDED` |
| DC-003 | an audit-finding requirement removed | READY_FOR_REVIEW blocked by finding:M0-F-001: the canonical expected set requires finding:M0-F-001 (M0-CP-0007 docs/checkpoints/SETUP-00-CP-0007/REVIEW-REPORT.md M0-F-001) but the … | `DEFENDED` |
| DC-004 | an audit-attack requirement removed | READY_FOR_REVIEW blocked by attack:A: the canonical expected set requires attack:A (M0-CP-0007 docs/checkpoints/SETUP-00-CP-0007/RED-TEAM-REPORT.md attack A) but the matrix does no… | `DEFENDED` |
| DC-005 | the denominator decreased with every stored count recomputed | READY_FOR_REVIEW blocked by canonical:SETUP-00#1.1: the canonical expected set requires canonical:SETUP-00#1.1 (docs/SETUP-00-CHECKLIST.md row 1.1) but the matrix does not declare … | `DEFENDED` |
| DC-006 | the declared total falsified upward | STATE.json requirementsMatrix.total=171 does not match the matrix value 131 | `DEFENDED` |
| DC-007 | coverage forged to 100 over an incomplete matrix | COMPLETENESS-REPORT.json complete=131 contradicts the recomputed value 130 COMPLETENESS-REPORT.json partial=0 contradicts the recomputed value 1 COMPLETENESS-REPORT.json coveragePe… | `DEFENDED` |
| DC-008 | a report claiming PASS over a MISSING requirement | COMPLETENESS-REPORT.json complete=131 contradicts the recomputed value 130 COMPLETENESS-REPORT.json missing=0 contradicts the recomputed value 1 COMPLETENESS-REPORT.json coveragePe… | `DEFENDED` |
| DC-009 | a COMPLETE requirement with no evidence at all | READY_FOR_REVIEW blocked by REQ-0001: COMPLETE requires at least one evidence reference | `DEFENDED` |
| DC-010 | evidence pointing at a path that does not exist | READY_FOR_REVIEW blocked by REQ-0001: evidence file does not exist: file:docs/does-not-exist.md | `DEFENDED` |
| DC-011 | evidence referencing a command whose record failed | READY_FOR_REVIEW blocked by REQ-0001: evidence references command 'cmd-0002', which did not complete successfully (result='FAILED', exitCode=3) | `DEFENDED` |
| EVD-001 | a quality PASS with no evidence reference | QUALITY.json staticAnalysis=PASS requires at least one evidence reference | `DEFENDED` |
| EVD-002 | quality evidence naming a file that does not exist | QUALITY.json staticAnalysis references a missing or empty file 'NO-SUCH-FILE.md' | `DEFENDED` |
| EVD-003 | quality evidence naming a command that does not exist | QUALITY.json staticAnalysis references an unknown command id 'cmd-9999' | `DEFENDED` |
| EVD-004 | quality evidence naming a command that failed | QUALITY.json staticAnalysis references command 'cmd-0002', which exited 5 | `DEFENDED` |
| EVD-005 | quality evidence naming an existing but empty file | QUALITY.json staticAnalysis references a missing or empty file 'EMPTY-EVIDENCE.md' | `DEFENDED` |
| EVD-006 | a completeness verdict describing content that has since changed | DELIVERY_COMPLETENESS_GATE is STALE: the code, requirements, lessons or policy changed after the audit, so it must run again | `DEFENDED` |
| STL-001 | a Green Keeper PASS whose recorded scope is no longer the current one | greenKeeper=PASS is STALE: the delivery-assurance scope changed after the last GREEN cycle, so the Green Keeper must run again | `DEFENDED` |
| STL-002 | a completeness PASS that predates a relevant scope change | DELIVERY_COMPLETENESS_GATE is STALE: the code, requirements, lessons or policy changed after the audit, so it must run again | `DEFENDED` |
| STL-003a | an internal Red Team result that predates a change to an attacked control | M0-INTERNAL-RED-TEAM.json is STALE: the attacked content changed after the run, so the affected attacks must be executed again | `DEFENDED` |
| STL-003b | an internal mirror result that predates a change to the audited content | M0-INTERNAL-MIRROR.json is STALE: the audited content changed after the mirror ran | `DEFENDED` |
| STL-004 | an internal Red Team PASS while one attack escaped | M0-INTERNAL-RED-TEAM.json: escaped does not match the recorded attacks M0-INTERNAL-RED-TEAM.json: 1 attack(s) escaped but the result is 'RED_TEAM_PASS' | `DEFENDED` |
| STL-005 | an internal mirror PASS while one mirrored check failed | M0-INTERNAL-MIRROR.json: failed does not match the recorded checks M0-INTERNAL-MIRROR.json: a failed check cannot produce a PASS | `DEFENDED` |

The baseline control `BASE-001`, an unmutated consistent copy of the delivery, is `ACCEPTED`
by the delivery-assurance, memory, internal-assurance and quality-evidence validators, which
is what makes every rejection above attributable.

## History and tag integrity, in temporary repositories only

| Scenario | Mutation | Observed | Result |
|---|---|---|---|
| HIST-001 | a historical tag moved to another commit | - SETUP-00-CP-0003: tag refs/tags/iacode-checkpoints/SETUP-00-CP-0003 resolves to c2eea150de9c97cfab5429d1e1eb3d5285e585f7, not the anchored commit 5780b0f86dbf46ad84d69b88a637be6f… | `DEFENDED` |
| HIST-002 | an anchor naming the wrong tag | - SETUP-00-CP-0003: anchored tag 'refs/tags/iacode-checkpoints/SETUP-00-CP-0099' is not the canonical 'refs/tags/iacode-checkpoints/SETUP-00-CP-0003' - SETUP-00-CP-0003: anchorHash… | `DEFENDED` |
| HIST-003 | an anchor naming the wrong commit | - SETUP-00-CP-0003: anchorHash does not match its own anchored fields (recorded 'df6e7bacb173d4b440b9cfee831968886735528dd77f2a54e3a5ca92041ecad3', recomputed 'ac8e664c2cb99264a472… | `DEFENDED` |
| HIST-004 | an anchor naming the wrong tree, with the chain recomputed around it | - SETUP-00-CP-0003: commit 5780b0f86dbf46ad84d69b88a637be6f076946f4 has tree 65dfc288c60dec518e5c488db6af8b4e9825fd8c, not the anchored 0000000000000000000000000000000000000000 | `DEFENDED` |
| HIST-005 | a wrong previous-anchor digest | - SETUP-00-CP-0004: anchorHash does not match its own anchored fields (recorded 'a5c174320d6fae29d2e94c20a5de08c8617cfa3c18d3f4946c6f0915c710b3bb', recomputed '714ded680a4314167420… | `DEFENDED` |
| HIST-006 | a link removed from the chain | - sealed checkpoint SETUP-00-CP-0007 has no integrity anchor | `DEFENDED` |
| HIST-007 | an anchor naming the wrong predecessor | - SETUP-00-CP-0004: previousCheckpoint 'SETUP-00-CP-0001' breaks the chain; expected 'SETUP-00-CP-0003' | `DEFENDED` |
| HIST-008 | CP-0001 to CP-0007 intact under read-only inspection | {'checkpointId': 'SETUP-00-CP-0001', 'commitMatches': True, 'treeMatches': True, 'linkMatches': True, 'digestMatches': True} {'checkpointId': 'SETUP-00-CP-0002', 'commitMatches': T… | `DEFENDED` |

## The four guardrails `SETUP-00-CP-0007` reported as ineffective

| Guardrail | Scenario | Observed | Result |
|---|---|---|---|
| GRD-LSN-0005-original | original bypass: MILESTONE_EXTERNAL_PASS carrying a red Green Keeper | MILESTONE_EXTERNAL_PASS requires GREEN_KEEPER_GATE=PASS, found 'FAIL' | `DEFENDED` |
| GRD-LSN-0005-variation | variation: a red completeness gate under every positive terminal status | statuses that escaped: none | `DEFENDED` |
| GRD-LSN-0007-original | original bypass: complete second-tool attribution written by the delivery itself | external validation: no external audit attestation exists for milestone M0 and checkpoint SETUP-00-CP-0008; an external PASS may not be self-asserted | `DEFENDED` |
| GRD-LSN-0007-variation | variation: externalAttestation declared VERIFIED against a file that does not exist | external validation: no external audit attestation exists for milestone M0 and checkpoint SETUP-00-CP-0008; an external PASS may not be self-asserted | `DEFENDED` |
| GRD-LSN-0008-original | original bypass: delete a mandatory requirement and recompute every stored count | READY_FOR_REVIEW blocked by canonical:SETUP-00#1.1: the canonical expected set requires canonical:SETUP-00#1.1 (docs/SETUP-00-CHECKLIST.md row 1.1) but the matrix does not declare … | `DEFENDED` |
| GRD-LSN-0008-variation | variation: keep the row count but substitute a canonical anchor with a local one | READY_FOR_REVIEW blocked by canonical:SETUP-00#1.1: the canonical expected set requires canonical:SETUP-00#1.1 (docs/SETUP-00-CHECKLIST.md row 1.1) but the matrix does not declare … | `DEFENDED` |
| GRD-LSN-0009-original | original bypass: a GREEN cycle measured against no gate at all | greenKeeper=PASS was measured against no gate, not the canonical mandatory set checkpointValidation, integrity, lessons, staticAnalysis, tests | `DEFENDED` |
| GRD-LSN-0009-variation | variation: a GREEN cycle measured against a single mandatory gate | greenKeeper=PASS was measured against tests, not the canonical mandatory set checkpointValidation, integrity, lessons, staticAnalysis, tests | `DEFENDED` |
| GRD-LSN-0009-policy | the mandatory gate set is read from policy, and --gates only adds to a run | canonical mandatory set = tests, staticAnalysis, lessons, integrity, checkpointValidation | `DEFENDED` |

## External attestation, checked one rule at a time

| Probe | Scenario | Observed | Result |
|---|---|---|---|
| EXT-000 | a structurally valid attestation | no error | `ACCEPTED` |
| EXT-001 | a forged secondToolValidation with no attestation in the repository | no external audit attestation exists for milestone M0 and checkpoint SETUP-00-CP-0008; an external PASS may not be self-asserted | `DEFENDED` |
| EXT-002 | a forged MILESTONE_EXTERNAL_PASS backed by an attestation for nothing | probe-attestation.json: attests checkpoint 'SETUP-00-CP-0001', not 'SETUP-00-CP-0008' | `DEFENDED` |
| EXT-003 | an attestation copied from an audit of another checkpoint | probe-attestation.json: attests checkpoint 'SETUP-00-CP-0006', not 'SETUP-00-CP-0008' | `DEFENDED` |
| EXT-004 | an attestation whose auditor is the audited checkpoint itself | probe-attestation.json: the audit checkpoint and the audited checkpoint are the same; an external verdict may not be authored by the delivery it judges | `DEFENDED` |
| EXT-005 | an attestation naming a subject checkpoint that is not the one promoted | probe-attestation.json: attests checkpoint 'SETUP-00-CP-0005', not 'SETUP-00-CP-0008' | `DEFENDED` |
| EXT-006 | an attestation naming a different subject commit | probe-attestation.json: attests commit '0000000000000000000000000000000000000000', not the subject commit 'c53f4c59a77870414324efa6b5f61b35d26c5090' | `DEFENDED` |
| EXT-007 | review REWORK_REQUIRED with an external PASS claimed | probe-attestation.json: reviewResult is 'REWORK_REQUIRED'; an external PASS requires APPROVED | `DEFENDED` |
| EXT-008 | Red Team FAIL with an external PASS claimed | probe-attestation.json: redTeamResult is 'RED_TEAM_FAIL'; an external PASS requires RED_TEAM_PASS | `DEFENDED` |
| EXT-009 | an incomplete audit with an external PASS claimed | probe-attestation.json: completeness is 93.22; an external PASS requires 100.0 | `DEFENDED` |
| EXT-009b | an audit with incomplete evidence coverage | probe-attestation.json: evidenceCoverage is 99.0; an external PASS requires 100.0 | `DEFENDED` |
| EXT-009c | an audit whose test result is FAIL | probe-attestation.json: testResult is 'FAIL'; an external PASS requires PASS | `DEFENDED` |
| EXT-010 | an attestation whose audit checkpoint does not exist | probe-attestation.json: audit checkpoint SETUP-00-CP-9999 does not exist | `DEFENDED` |
| EXT-010b | an attestation with no auditor role recorded | probe-attestation.json: an external audit attestation requires auditorRole | `DEFENDED` |
| EXT-010c | an attestation with no auditing tool recorded | probe-attestation.json: an external audit attestation requires tool | `DEFENDED` |

## Conclusion

`RED_TEAM_PASS`. Every mandatory attack of the sealed `SETUP-00-CP-0007` battery and every
additional attack against the surfaces `SETUP-00-CP-0008` introduced was defended, and each
of the four previously bypassed guardrails now blocks both its original bypass and a
variation of it. The milestone still fails, on the review findings rather than on an escape.
