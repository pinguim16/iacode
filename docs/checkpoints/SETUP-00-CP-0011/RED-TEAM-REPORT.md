# Red Team Report — the adversarial battery of this audit

Result: `RED_TEAM_PASS`

- Audit checkpoint: `SETUP-00-CP-0011`
- Subject: `SETUP-00-CP-0010`
- Scenarios executed: 37; defended: 37; escaped: 0
- Null-mutation control: `VALID`

## What the battery attacks

Each scenario runs against its own fresh copy of a sealed snapshot of this checkpoint, so
no refusal can be inherited from a previous scenario. The snapshot is produced by the same
finalize and seal tooling the real checkpoint uses, and it models this checkpoint as
approved, because the defences around a claimed milestone verdict can only be attacked in a
repository that claims one. The models never leave the disposable copy.

The control runs first. If the unmutated snapshot were refused, no refusal afterwards could
be attributed to a mutation, and the battery reports `INVALID` rather than a row of
defences. It was accepted:

```text
CHECKPOINT_VALID
MILESTONE_PASSED milestone=M0 attestations=1 accepted=1
```

## Scenarios

| Attack | Category | Target | Mutation | Expected | Result |
|---|---|---|---|---|---|
| `ATT-01` | additional | attestation subject | Attest a checkpoint other than the sealed subject | reject | `DEFENDED` |
| `ATT-02` | additional | attestation subject | Attest a commit the subject tag does not resolve to | reject | `DEFENDED` |
| `ATT-03` | additional | attestation author | Name the subject as its own auditor | reject | `DEFENDED` |
| `ATT-04` | additional | attestation author | Claim a verdict another checkpoint authored | reject | `DEFENDED` |
| `ATT-05` | additional | attestation verdict | Promote on a review that was not approved | reject | `DEFENDED` |
| `ATT-06` | additional | attestation verdict | Promote on a failed Red Team | reject | `DEFENDED` |
| `ATT-07` | additional | attestation verdict | Promote on incomplete coverage | reject | `DEFENDED` |
| `ATT-08` | additional | attestation verdict | Promote on incomplete evidence coverage | reject | `DEFENDED` |
| `ATT-09` | additional | attestation verdict | Promote on a failing test result | reject | `DEFENDED` |
| `ATT-10` | additional | attestation mechanism | Declare an unrecognised validation mechanism | reject | `DEFENDED` |
| `ATT-11` | additional | attestation mechanism | Claim a fresh-session audit without a fresh session | reject | `DEFENDED` |
| `ATT-12` | additional | attestation mechanism | Claim a cross-tool audit while recording that cross-tool execution was unavailable | reject | `DEFENDED` |
| `ATT-13` | additional | attestation schema | Declare an older attestation schema version | reject | `DEFENDED` |
| `ATT-14` | additional | attestation schema | Remove a required field | reject | `DEFENDED` |
| `ATT-15` | additional | attestation subject | Attest an older, easier checkpoint | reject | `DEFENDED` |
| `ATT-16` | additional | milestone derivation | Remove the attestation and keep the claimed status | reject | `DEFENDED` |
| `ATT-17` | additional | milestone derivation | Derive the verdict with no attestation at all | reject | `DEFENDED` |
| `ATT-18` | additional | pass vocabulary | Record a cross-tool milestone status from a fresh-session audit | reject | `DEFENDED` |
| `INT-01` | mandatory | sealed history | Move a historical checkpoint tag onto another commit | reject | `DEFENDED` |
| `INT-02` | mandatory | sealed history | Rewrite sealed content and move its tag onto the rewrite | reject | `DEFENDED` |
| `INT-03` | mandatory | integrity chain | Break the link between two consecutive anchors | reject | `DEFENDED` |
| `INT-04` | mandatory | integrity chain | Remove the anchor of a sealed checkpoint | reject | `DEFENDED` |
| `INT-05` | mandatory | successor duty | Skip the anchor this checkpoint owes its sealed predecessor | reject | `DEFENDED` |
| `INT-06` | additional | integrity chain | Forge an anchored tree without recomputing the digest | reject | `DEFENDED` |
| `PRE-01` | mandatory | lesson preflight | Change the memory after the preflight was recorded | reject | `DEFENDED` |
| `PRE-02` | additional | lesson preflight | Forge the recorded preflight fingerprint | reject | `DEFENDED` |
| `PRE-03` | additional | lesson preflight | Drop a derived lesson requirement from the preflight | reject | `DEFENDED` |
| `MEM-01` | mandatory | guarded semantics | Replace a preventive control with documentation only | reject | `DEFENDED` |
| `MEM-02` | additional | memory policy | Declare a relocatable guardrail registry the code never reads | reject | `DEFENDED` |
| `MEM-03` | additional | memory prose | Let a GUARDED lesson describe itself as unguarded | reject | `DEFENDED` |
| `MEM-04` | additional | guardrail registry | Remove a guardrail a GUARDED lesson names | reject | `DEFENDED` |
| `STL-01` | mandatory | gate staleness | Edit the assurance scope after the last green cycle | reject | `DEFENDED` |
| `STL-02` | mandatory | derived counts | Forge the derived test count | reject | `DEFENDED` |
| `STL-03` | additional | derived counts | Record more passing cases than the suite contains | reject | `DEFENDED` |
| `STL-04` | mandatory | readiness invariant | Carry a blocker while claiming a milestone verdict | reject | `DEFENDED` |
| `STL-05` | mandatory | file inventory | Remove an entry from the declared change set | reject | `DEFENDED` |
| `SEC-01` | mandatory | secret handling | Insert a credential-shaped value into the memory and require a refusal that does not repeat it | reject | `DEFENDED` |

## Observed refusals

- `ATT-01`: exit=1 CHECKPOINT_INVALID - FILES.json: hash mismatch for .iacode/attestations/M0-CP-0011.json - dirty-state mismatch: expected False, observed True - greenKeeper=PASS is STALE: the delivery-assurance scope changed after the last GREEN cycle, so the Green Keeper must run again - DELIVERY_COMPLETENESS_GATE is STALE: the code, requirements, lessons or policy changed after the audit, so it must run a
- `ATT-02`: exit=1 CHECKPOINT_INVALID - FILES.json: hash mismatch for .iacode/attestations/M0-CP-0011.json - dirty-state mismatch: expected False, observed True - greenKeeper=PASS is STALE: the delivery-assurance scope changed after the last GREEN cycle, so the Green Keeper must run again - DELIVERY_COMPLETENESS_GATE is STALE: the code, requirements, lessons or policy changed after the audit, so it must run a
- `ATT-03`: exit=1 CHECKPOINT_INVALID - FILES.json: hash mismatch for .iacode/attestations/M0-CP-0011.json - dirty-state mismatch: expected False, observed True - greenKeeper=PASS is STALE: the delivery-assurance scope changed after the last GREEN cycle, so the Green Keeper must run again - DELIVERY_COMPLETENESS_GATE is STALE: the code, requirements, lessons or policy changed after the audit, so it must run a
- `ATT-04`: exit=1 CHECKPOINT_INVALID - FILES.json: hash mismatch for .iacode/attestations/M0-CP-0011.json - dirty-state mismatch: expected False, observed True - greenKeeper=PASS is STALE: the delivery-assurance scope changed after the last GREEN cycle, so the Green Keeper must run again - DELIVERY_COMPLETENESS_GATE is STALE: the code, requirements, lessons or policy changed after the audit, so it must run a
- `ATT-05`: exit=1 CHECKPOINT_INVALID - FILES.json: hash mismatch for .iacode/attestations/M0-CP-0011.json - dirty-state mismatch: expected False, observed True - greenKeeper=PASS is STALE: the delivery-assurance scope changed after the last GREEN cycle, so the Green Keeper must run again - DELIVERY_COMPLETENESS_GATE is STALE: the code, requirements, lessons or policy changed after the audit, so it must run a
- `ATT-06`: exit=1 CHECKPOINT_INVALID - FILES.json: hash mismatch for .iacode/attestations/M0-CP-0011.json - dirty-state mismatch: expected False, observed True - greenKeeper=PASS is STALE: the delivery-assurance scope changed after the last GREEN cycle, so the Green Keeper must run again - DELIVERY_COMPLETENESS_GATE is STALE: the code, requirements, lessons or policy changed after the audit, so it must run a
- `ATT-07`: exit=1 CHECKPOINT_INVALID - FILES.json: hash mismatch for .iacode/attestations/M0-CP-0011.json - dirty-state mismatch: expected False, observed True - greenKeeper=PASS is STALE: the delivery-assurance scope changed after the last GREEN cycle, so the Green Keeper must run again - DELIVERY_COMPLETENESS_GATE is STALE: the code, requirements, lessons or policy changed after the audit, so it must run a
- `ATT-08`: exit=1 CHECKPOINT_INVALID - FILES.json: hash mismatch for .iacode/attestations/M0-CP-0011.json - dirty-state mismatch: expected False, observed True - greenKeeper=PASS is STALE: the delivery-assurance scope changed after the last GREEN cycle, so the Green Keeper must run again - DELIVERY_COMPLETENESS_GATE is STALE: the code, requirements, lessons or policy changed after the audit, so it must run a
- `ATT-09`: exit=1 CHECKPOINT_INVALID - FILES.json: hash mismatch for .iacode/attestations/M0-CP-0011.json - dirty-state mismatch: expected False, observed True - greenKeeper=PASS is STALE: the delivery-assurance scope changed after the last GREEN cycle, so the Green Keeper must run again - DELIVERY_COMPLETENESS_GATE is STALE: the code, requirements, lessons or policy changed after the audit, so it must run a
- `ATT-10`: exit=1 CHECKPOINT_INVALID - FILES.json: hash mismatch for .iacode/attestations/M0-CP-0011.json - dirty-state mismatch: expected False, observed True - greenKeeper=PASS is STALE: the delivery-assurance scope changed after the last GREEN cycle, so the Green Keeper must run again - DELIVERY_COMPLETENESS_GATE is STALE: the code, requirements, lessons or policy changed after the audit, so it must run a
- `ATT-11`: exit=1 CHECKPOINT_INVALID - FILES.json: hash mismatch for .iacode/attestations/M0-CP-0011.json - dirty-state mismatch: expected False, observed True - greenKeeper=PASS is STALE: the delivery-assurance scope changed after the last GREEN cycle, so the Green Keeper must run again - DELIVERY_COMPLETENESS_GATE is STALE: the code, requirements, lessons or policy changed after the audit, so it must run a
- `ATT-12`: exit=1 CHECKPOINT_INVALID - FILES.json: hash mismatch for .iacode/attestations/M0-CP-0011.json - dirty-state mismatch: expected False, observed True - greenKeeper=PASS is STALE: the delivery-assurance scope changed after the last GREEN cycle, so the Green Keeper must run again - DELIVERY_COMPLETENESS_GATE is STALE: the code, requirements, lessons or policy changed after the audit, so it must run a
- `ATT-13`: exit=1 CHECKPOINT_INVALID - FILES.json: hash mismatch for .iacode/attestations/M0-CP-0011.json - dirty-state mismatch: expected False, observed True - greenKeeper=PASS is STALE: the delivery-assurance scope changed after the last GREEN cycle, so the Green Keeper must run again - DELIVERY_COMPLETENESS_GATE is STALE: the code, requirements, lessons or policy changed after the audit, so it must run a
- `ATT-14`: exit=1 CHECKPOINT_INVALID - FILES.json: hash mismatch for .iacode/attestations/M0-CP-0011.json - dirty-state mismatch: expected False, observed True - greenKeeper=PASS is STALE: the delivery-assurance scope changed after the last GREEN cycle, so the Green Keeper must run again - DELIVERY_COMPLETENESS_GATE is STALE: the code, requirements, lessons or policy changed after the audit, so it must run a
- `ATT-15`: exit=1 CHECKPOINT_INVALID - FILES.json: hash mismatch for .iacode/attestations/M0-CP-0011.json - FILES.json: hash mismatch for docs/checkpoints/SETUP-00-CP-0011/STATE.json - dirty-state mismatch: expected False, observed True - greenKeeper=PASS is STALE: the delivery-assurance scope changed after the last GREEN cycle, so the Green Keeper must run again - DELIVERY_COMPLETENESS_GATE is STALE: the co
- `ATT-16`: exit=1 CHECKPOINT_INVALID - FILES.json: hashed path does not exist: .iacode/attestations/M0-CP-0011.json - dirty-state mismatch: expected False, observed True - greenKeeper=PASS is STALE: the delivery-assurance scope changed after the last GREEN cycle, so the Green Keeper must run again - DELIVERY_COMPLETENESS_GATE is STALE: the code, requirements, lessons or policy changed after the audit, so it 
- `ATT-17`: exit=1 MILESTONE_NOT_PASSED milestone=M0 attestations=0 accepted=0 - no independent audit attestation exists for milestone M0
- `ATT-18`: exit=1 CHECKPOINT_INVALID - FILES.json: hash mismatch for docs/checkpoints/SETUP-00-CP-0011/STATE.json - FILES.json: hash mismatch for docs/checkpoints/SETUP-00-CP-0011/STATUS.md - dirty-state mismatch: expected False, observed True - MILESTONE_EXTERNAL_PASS may not be derived from a 'FRESH_SESSION_INDEPENDENT_AUDIT' attestation, which authorises MILESTONE_INDEPENDENT_AUDIT_PASS; MILESTONE_INDEPEN
- `INT-01`: exit=1 INTEGRITY_INVALID - SETUP-00-CP-0005: tag refs/tags/iacode-checkpoints/SETUP-00-CP-0005 resolves to 994bab402873bc4d221c02d8c94bdebeb2b0f3cb, not the anchored commit 276645b4498a0e58a1bf38979b5e078669dbb380
- `INT-02`: exit=1 INTEGRITY_INVALID - SETUP-00-CP-0005: tag refs/tags/iacode-checkpoints/SETUP-00-CP-0005 resolves to 22841ac8d57518d95a768c2911c3bc6dfba8cbdb, not the anchored commit 276645b4498a0e58a1bf38979b5e078669dbb380 - sealed checkpoint SETUP-00-CP-0011 has no integrity anchor
- `INT-03`: exit=1 INTEGRITY_INVALID - SETUP-00-CP-0004: anchorHash does not match its own anchored fields (recorded 'a5c174320d6fae29d2e94c20a5de08c8617cfa3c18d3f4946c6f0915c710b3bb', recomputed '714ded680a4314167420555efdc79d1a6563b0929af2339921a27fb663bbe1d7') - SETUP-00-CP-0004: previousAnchorHash breaks the chain with 'SETUP-00-CP-0003'
- `INT-04`: exit=1 INTEGRITY_INVALID - SETUP-00-CP-0007: previousCheckpoint 'SETUP-00-CP-0006' breaks the chain; expected 'SETUP-00-CP-0005' - SETUP-00-CP-0007: previousAnchorHash breaks the chain with 'SETUP-00-CP-0005' - sealed checkpoint SETUP-00-CP-0006 has no integrity anchor
- `INT-05`: exit=1 CHECKPOINT_INVALID - FILES.json: hash mismatch for .iacode/anchors/checkpoint-chain.json - dirty-state mismatch: expected False, observed True - greenKeeper=PASS is STALE: the delivery-assurance scope changed after the last GREEN cycle, so the Green Keeper must run again - DELIVERY_COMPLETENESS_GATE is STALE: the code, requirements, lessons or policy changed after the audit, so it must run 
- `INT-06`: exit=1 INTEGRITY_INVALID - SETUP-00-CP-0003: anchorHash does not match its own anchored fields (recorded 'df6e7bacb173d4b440b9cfee831968886735528dd77f2a54e3a5ca92041ecad3', recomputed 'e3ee016f2df68110e23ddfd8eb367819b86f045acb330dc24563789ed10cd196') - SETUP-00-CP-0003: commit 5780b0f86dbf46ad84d69b88a637be6f076946f4 has tree 65dfc288c60dec518e5c488db6af8b4e9825fd8c, not the anchored 000000000000
- `PRE-01`: exit=1 CHECKPOINT_INVALID - dirty-state mismatch: expected False, observed True - greenKeeper=PASS is STALE: the delivery-assurance scope changed after the last GREEN cycle, so the Green Keeper must run again - DELIVERY_COMPLETENESS_GATE is STALE: the code, requirements, lessons or policy changed after the audit, so it must run again - lesson preflight: the lesson preflight is STALE: its recorded 
- `PRE-02`: exit=1 CHECKPOINT_INVALID - FILES.json: hash mismatch for docs/checkpoints/SETUP-00-CP-0011/LESSON-PREFLIGHT.json - dirty-state mismatch: expected False, observed True - DELIVERY_COMPLETENESS_GATE is STALE: the code, requirements, lessons or policy changed after the audit, so it must run again - lesson preflight: the lesson preflight is STALE: its recorded inputsFingerprint does not match the curr
- `PRE-03`: exit=1 CHECKPOINT_INVALID - FILES.json: hash mismatch for docs/checkpoints/SETUP-00-CP-0011/LESSON-PREFLIGHT.json - dirty-state mismatch: expected False, observed True - COMPLETENESS-REPORT.json expectedRequirements=104 contradicts the recomputed value 103 - COMPLETENESS-REPORT.json result='PASS' contradicts the recomputed value 'FAIL' - DELIVERY_COMPLETENESS_GATE is STALE: the code, requirements,
- `MEM-01`: exit=1 LESSONS_INVALID - LSN-0001: GUARDED requires at least one preventive control of kind test, validator, lint, policy, schema, invariant, automated-check; documentation alone is not a guardrail
- `MEM-02`: exit=1 LESSONS_INVALID - POLICY.json: $: unexpected property 'guardrailRegistry'
- `MEM-03`: exit=1 LESSONS_INVALID - LSN-0001: the notes state that the lesson is not guarded while its status is GUARDED; describe the residual limit of the control instead of its status
- `MEM-04`: exit=1 CHECKPOINT_INVALID - dirty-state mismatch: expected False, observed True - greenKeeper=PASS is STALE: the delivery-assurance scope changed after the last GREEN cycle, so the Green Keeper must run again - DELIVERY_COMPLETENESS_GATE is STALE: the code, requirements, lessons or policy changed after the audit, so it must run again - engineering memory: LSN-0029: guardrail 'GRD-0029' is not in t
- `STL-01`: exit=1 CHECKPOINT_INVALID - dirty-state mismatch: expected False, observed True - greenKeeper=PASS is STALE: the delivery-assurance scope changed after the last GREEN cycle, so the Green Keeper must run again - DELIVERY_COMPLETENESS_GATE is STALE: the code, requirements, lessons or policy changed after the audit, so it must run again - M0-INTERNAL-RED-TEAM.json is STALE: the attacked content chang
- `STL-02`: exit=1 CHECKPOINT_INVALID - FILES.json: hash mismatch for docs/checkpoints/SETUP-00-CP-0011/COUNTS.json - dirty-state mismatch: expected False, observed True - COUNTS.json TESTS=99999/99999 contradicts the derived 363/363 - FILES.json hashAfter does not match the repository content of docs/checkpoints/SETUP-00-CP-0011/COUNTS.json
- `STL-03`: exit=1 CHECKPOINT_INVALID - FILES.json: hash mismatch for docs/checkpoints/SETUP-00-CP-0011/COUNTS.json - dirty-state mismatch: expected False, observed True - COUNTS.json TESTS=726/363 contradicts the derived 363/363 - FILES.json hashAfter does not match the repository content of docs/checkpoints/SETUP-00-CP-0011/COUNTS.json
- `STL-04`: exit=1 CHECKPOINT_INVALID - FILES.json: hash mismatch for docs/checkpoints/SETUP-00-CP-0011/STATE.json - dirty-state mismatch: expected False, observed True - MILESTONE_INDEPENDENT_AUDIT_PASS is incompatible with a non-empty blockedBy: an unresolved blocker - FILES.json hashAfter does not match the repository content of docs/checkpoints/SETUP-00-CP-0011/STATE.json
- `STL-05`: exit=1 CHECKPOINT_INVALID - dirty-state mismatch: expected False, observed True - FILES.json omits a changed path: docs/checkpoints/SETUP-00-CP-0011/audit-harness/run_suite.py (added)
- `SEC-01`: exit=1 LESSONS_INVALID - LSN-0001: secret pattern detected in $.symptom: GitHub credential

## Corrections made to this battery

The first revision of this battery reported four scenarios as escaped. None of them was an
escape: every mutation was refused, and the four expectations were wrong. One asserted that
a fresh-session attestation recording that cross-tool execution was available must be
rejected, which the model does not claim and does not need to, because the mechanism still
authorises only the independent-audit status; it was replaced by the real control, a
cross-tool mechanism contradicting its own recorded availability. One mutated the
attestation without moving the claim in `STATE.json`, so the refusal named a missing
attestation rather than the older subject; it now moves both. Two asserted message
fragments the validator does not emit. The corrected battery is the one reported here, and
this correction is recorded rather than quietly repaired, because a battery whose
expectations are wrong proves nothing about the product.

## What this battery is not

It is not independent of the tool. It is written and executed by the auditing session, on
the same tooling as the implementing run, and it is recorded as the adversarial position of
this audit rather than as cross-tool validation.
