# Internal Red Team Report

Result: `RED_TEAM_PASS`

- Checkpoint: `SETUP-00-CP-0008`
- Generated: `2026-09-20T22:12:26Z`
- Target fingerprint: `2dbac889f61f630403805b7a1751b5899ee5dd322a49441691e8db95e82d0d0d`
- Source: Mandatory battery re-parsed from docs/checkpoints/SETUP-00-CP-0007/RED-TEAM-REPORT.md; additional attacks from the same report; new attacks for the surfaces this checkpoint introduces.

This is internal quality assurance executed by the delivery, not independent validation.
Every attack below was executed against an isolated clone; nothing here was asserted.

Defended: `46/46 ATTACKS`; of these, `26` of `26` are the mandatory battery.

| Attack | Target | Mutation | Expected defence | Observed | Result |
|---|---|---|---|---|---|
| `A` | readiness and blocker invariant | Add a blocker to a READY_FOR_REVIEW checkpoint | reject | `exit=1 CHECKPOINT_INVALID / - READY_FOR_REVIEW is incompatible with a non-empty blockedBy: an unresolved blocker` | DEFENDED |
| `B` | mandatory quality | Set a review-ready quality gate red | reject | `exit=1 CHECKPOINT_INVALID / - greenKeeper=PASS contradicts QUALITY.json unitTests=FAIL` | DEFENDED |
| `C` | completeness denominator | Delete a mandatory requirement and recompute every stored count | reject the missing source requirement | `exit=1 CHECKPOINT_INVALID / - READY_FOR_REVIEW blocked by canonical:SETUP-00#1.1: the canonical expected set requires canonical:SETUP-00#1.1 (docs/SETUP-00-CHECKLIST.md row 1.1) but the matrix does not declare it` | DEFENDED |
| `D` | completeness claims | Forge the stored counts of a passing report | reject the mismatch | `exit=1 CHECKPOINT_INVALID / - COMPLETENESS-REPORT.json complete=136 contradicts the recomputed value 131` | DEFENDED |
| `E` | lesson-derived requirement | Remove a derived requirement from the matrix | reject | `exit=1 CHECKPOINT_INVALID / - READY_FOR_REVIEW blocked by LESSON-REQ-0001: the lesson preflight derived this requirement from LSN-0001 but the matrix does not declare it` | DEFENDED |
| `F` | GUARDED semantics | Replace a preventive control with documentation only | reject | `exit=1 LESSONS_INVALID / - LSN-0001: GUARDED requires at least one preventive control of kind test, validator, lint, policy, schema, invariant, automated-check; documentation alone is not a guardrail` | DEFENDED |
| `G` | lesson identity | Duplicate a lesson identifier | reject | `exit=1 LESSONS_INVALID / - LSN-0001: duplicate lessonId` | DEFENDED |
| `H` | lesson secret handling | Insert a secret-shaped value into a scanned field | reject without disclosing the value | `exit=1 LESSONS_INVALID / - LSN-0001: secret pattern detected in $.notes: GitHub credential` | DEFENDED |
| `I` | sealed predecessor | Rewrite a sealed checkpoint and move its tag to the rewritten commit | reject the historical rewrite | `exit=1 INTEGRITY_INVALID / - SETUP-00-CP-0005: tag refs/tags/iacode-checkpoints/SETUP-00-CP-0005 resolves to a0d9f7e1786753cccf3a881ca9290af88db44ad9, not the anchored commit 276645b4498a0e58a1bf38979b5e078669dbb380` | DEFENDED |
| `J` | tag immutability | Move a checkpoint tag and HEAD to a new commit together | reject the moved tag | `exit=1 INTEGRITY_INVALID / - SETUP-00-CP-0007: tag refs/tags/iacode-checkpoints/SETUP-00-CP-0007 resolves to 0be1211e19bd12eeb1c2b7e6bb9ecf2c4b6ea4b3, not the anchored commit 502c554575f717c1d57290e4f4aafa575e41170e` | DEFENDED |
| `K` | file inventory | Remove one inventory entry | reject | `exit=1 CHECKPOINT_INVALID / - FILES.json omits a changed path: .claude/agents/m0-closure-auditor.md (added)` | DEFENDED |
| `L` | file inventory | Silently modify a tracked file | reject | `exit=1 CHECKPOINT_INVALID / - FILES.json omits a changed path: docs/MASTER-PLAN.md (modified)` | DEFENDED |
| `M` | file inventory | Set a wrong hashBefore | reject | `exit=1 CHECKPOINT_INVALID / - FILES.json hashBefore does not match the baseCommit content of .iacode/memory/LESSONS.md` | DEFENDED |
| `N` | file inventory | Set a wrong hashAfter | reject | `exit=1 CHECKPOINT_INVALID / - FILES.json: hash mismatch for .claude/agents/m0-closure-auditor.md` | DEFENDED |
| `O` | quality evidence | Claim PASS with no evidence | reject | `exit=1 CHECKPOINT_INVALID / - QUALITY.json staticAnalysis=PASS requires at least one evidence reference` | DEFENDED |
| `P` | evidence resolution | Reference an unknown command | reject | `exit=1 CHECKPOINT_INVALID / - QUALITY.json staticAnalysis references an unknown command id 'cmd-9999'` | DEFENDED |
| `Q` | second-tool evidence | Supply complete cross-tool attribution with no external evidence | reject unauthenticated validation | `exit=1 CHECKPOINT_INVALID / - external validation: no external audit attestation exists for milestone M0 and checkpoint SETUP-00-CP-0008; an external PASS may not be self-asserted` | DEFENDED |
| `R` | pass vocabulary | Promote an internally authored result to an external status | require an independent verdict | `exit=1 CHECKPOINT_INVALID / - external validation: no external audit attestation exists for milestone M0 and checkpoint SETUP-00-CP-0008; an external PASS may not be self-asserted` | DEFENDED |
| `S` | external milestone review | Leave the review and Red Team pending with a null auditor and timestamp | reject | `exit=1 CHECKPOINT_INVALID / - MILESTONE_EXTERNAL_PASS requires an independent review verdict, found 'PENDING'` | DEFENDED |
| `T` | extraordinary cadence | Request an audit without a known trigger | reject | `exit=1 CHECKPOINT_INVALID / - externalAuditReason must name one of the recorded triggers: security-boundary, sandbox-boundary, rights-or-provenance-change, training-data-policy, training-execution, promotion-logic, secret-handling, destructive-persistence` | DEFENDED |
| `U` | preflight freshness | Retire a canonical lesson but keep the active preflight | reject or recompute | `exit=1 CHECKPOINT_INVALID / - greenKeeper=PASS is STALE: the delivery-assurance scope changed after the last GREEN cycle, so the Green Keeper must run again` | DEFENDED |
| `V` | Green Keeper mandatory set | Run the Green Keeper with an empty gate selection while a test genuinely fails | reject; the mandatory set is not the caller's to choose | `exit=1 [tests] RED exit=1 ledger=cmd-0059` | DEFENDED |
| `W` | partial completeness | Claim PASS with a PARTIAL requirement | reject | `exit=1 CHECKPOINT_INVALID / - STATE.json requirementsMatrix.partial=0 does not match the matrix value 1` | DEFENDED |
| `X` | command audit | Remove a required field from a command record | reject | `exit=1 CHECKPOINT_INVALID / - COMMANDS.jsonl:58: schemaVersion 3.0.0 requires runtime` | DEFENDED |
| `Y` | latest pointer | Point LATEST.md at an older checkpoint | reject | `exit=1 CHECKPOINT_INVALID / - requested checkpoint is not the LATEST target: C:\Users\cesar\AppData\Local\Temp\iacode-red-team-kjdowuwt\fixture\docs\checkpoints\SETUP-00-CP-0008` | DEFENDED |
| `Z` | path safety | Use path traversal as the Gate identifier | reject with no write outside the repository | `exit=2 usage: new_checkpoint.py [-h] [--root ROOT] --gate GATE` | DEFENDED |
| `AA` | aggregate consistency | Declare a mandatory count in state that no artifact agrees with | reject | `exit=1 CHECKPOINT_INVALID / - STATE.json requirementsMatrix.mandatory=132 does not match the matrix value 130` | DEFENDED |
| `AB` | control resolution | Point a GUARDED lesson at a nonexistent test | reject | `exit=1 LESSONS_INVALID / - LSN-0001: control names the test 'NoSuchTests.test_nothing', which does not exist in the suite` | DEFENDED |
| `AC` | evidence resolution | Point lesson evidence at a nonexistent file | reject | `exit=1 LESSONS_INVALID / - LSN-0001: evidence file does not exist: file:docs/this-file-does-not-exist.md` | DEFENDED |
| `AD` | nested secret scan | Hide a secret-shaped value inside prevention.description | reject without disclosing the value | `exit=1 LESSONS_INVALID / - LSN-0001: secret pattern detected in $.prevention[0].description: OpenAI-style key` | DEFENDED |
| `AE` | preflight gate binding | Reuse a SETUP-00 preflight for another Gate | reject | `exit=1 CHECKPOINT_INVALID / - lesson preflight: the preflight was generated for gate 'SETUP-00' but the checkpoint declares 'GATE 1'; a preflight may not be reused across Gates` | DEFENDED |
| `AF` | promotion invariant | Reach an external status while the Green Keeper gate is red | reject | `exit=1 CHECKPOINT_INVALID / - MILESTONE_EXTERNAL_PASS requires GREEN_KEEPER_GATE=PASS, found 'FAIL'` | DEFENDED |
| `AG` | gate registry | Remove a mandatory gate from the policy after a GREEN cycle | reject the mismatch between the cycle and the policy | `exit=1 CHECKPOINT_INVALID / - greenKeeper=PASS was measured against checkpointValidation, integrity, lessons, staticAnalysis, tests, not the canonical mandatory set checkpointValidation, integrity, staticAnalysis, tests` | DEFENDED |
| `AH` | gate staleness | Edit the assurance scope after the last GREEN cycle | reject the stale PASS | `exit=1 CHECKPOINT_INVALID / - greenKeeper=PASS is STALE: the delivery-assurance scope changed after the last GREEN cycle, so the Green Keeper must run again` | DEFENDED |
| `AI` | external attestation | Write an attestation whose audit checkpoint is the audited checkpoint itself | reject self-attestation | `exit=1 CHECKPOINT_INVALID / - external validation: .iacode/attestations/forged.json: the audit checkpoint and the audited checkpoint are the same; an external verdict may not be authored by the delivery it judges` | DEFENDED |
| `AJ` | external attestation | Claim an external PASS over a failed review | reject | `exit=1 CHECKPOINT_INVALID / - external validation: .iacode/attestations/forged.json: reviewResult is 'REWORK_REQUIRED'; an external PASS requires APPROVED` | DEFENDED |
| `AK` | external attestation | Attest a different commit than the one being promoted | reject | `exit=1 CHECKPOINT_INVALID / - external validation: .iacode/attestations/forged.json: attests commit '0000000000000000000000000000000000000000', not the subject commit '8e6cdee64e278d4b0c20e0cb159c71ab4c1bccca'` | DEFENDED |
| `AL` | derived counts | Forge a stored count | reject | `exit=1 CHECKPOINT_INVALID / - COUNTS.json TESTS=313/306 contradicts the derived 306/306` | DEFENDED |
| `AM` | count consistency | State a count in Markdown that contradicts the derived one | reject | `exit=1 CHECKPOINT_INVALID / - FINAL-REPORT.md states 999 of 999 TESTS, which contradicts the derived 306/306` | DEFENDED |
| `AN` | findings closure | Offer the delivery with an audit finding still open | reject | `exit=1 CHECKPOINT_INVALID / - READY_FOR_REVIEW is not available while M0-F-001 of M0-CP-0007 remain open` | DEFENDED |
| `AO` | internal Red Team | Keep a PASS verdict while an attack escaped | reject | `exit=1 CHECKPOINT_INVALID / - M0-INTERNAL-RED-TEAM.json: escaped does not match the recorded attacks` | DEFENDED |
| `AP` | internal mirror audit | Keep a PASS verdict while a mirror check failed | reject | `exit=1 CHECKPOINT_INVALID / - M0-INTERNAL-MIRROR.json: failed does not match the recorded checks` | DEFENDED |
| `AQ` | guardrail registry | Verify a guardrail with a test that does not exist | reject | `exit=1 LESSONS_INVALID / - LSN-0001: guardrail 'GRD-0001' is verified by 'NoSuchTests.test_nothing', which does not exist in the suite` | DEFENDED |
| `AR` | integrity anchors | Break the link between two anchors | reject | `exit=1 INTEGRITY_INVALID / - SETUP-00-CP-0003: previousAnchorHash breaks the chain with 'SETUP-00-CP-0002'` | DEFENDED |
| `AS` | command replay context | Remove the content binding of recorded inputs | reject | `exit=1 CHECKPOINT_INVALID / - COMMANDS.jsonl:1: schemaVersion 3.2.0 requires inputsDigest binding every declared input by content` | DEFENDED |
| `AT` | seal chronology | Remove the post-commit validation of the sealed content | reject | `exit=1 CHECKPOINT_INVALID / - READY_FOR_REVIEW requires a recorded post-commit-validation run with exit code 0 over a clean worktree; the sealed content must be validated as committed, not as a dirty working tree` | DEFENDED |
