# Red Team Report — the adversarial battery of this audit

Result: `RED_TEAM_PASS`  
Defended: 26 of 26  
Checkpoint: `SETUP-00-CP-0013`  
Target fingerprint: `82c7c20b057414134929c1bc825806d7e6fc27080e52f11082c180ab0a4926eb`

## What this battery is

The adversarial battery of the SETUP-00-CP-0013 fresh-session independent audit, authored by this audit and executed against disposable clones of the sealed SETUP-00-CP-0012 checkout, one clone per scenario. It is independent of m0_red_team.py, which this audit also executed separately and which reported 73 of 73 defended.

## Null-mutation control

Result: `VALID`

the unmutated SETUP-00-CP-0012 checkout, detached at its canonical tag, run through the identical validation path: exit=0 CHECKPOINT_VALID A second null-mutation control, with the declared inventory hashes re-derived by the project's own helper, was also accepted before the three attributable variants ran: the unmutated SETUP-00-CP-0012 checkout with its declared inventory hashes re-derived by the same helper the attacks use (inventory refresh exit=0 ['INVENTORY_REFRESHED']), then validated: exit=0 CHECKPOINT_VALID

A battery without this control proves nothing: the second `M0` audit's first harness reported every attack as defended while the refusals came from leftover state rather than from the mutation under test.

## Scenarios

| Attack | Category | Target | Mutation | Expected | Result |
|---|---|---|---|---|---|
| `NA-01` | mandatory | mirror applicability: inapplicable dimension | MIR-002 declared NOT_APPLICABLE with no reason and no derivation source | reject | `DEFENDED` |
| `NA-02` | mandatory | mirror applicability: inapplicable dimension | MIR-002 declared NOT_APPLICABLE while the registry still names CP11-F-001 | reject | `DEFENDED` |
| `NA-03` | mandatory | mirror applicability: inapplicable dimension | MIR-002 declared NOT_APPLICABLE while carrying four applicable items | reject | `DEFENDED` |
| `NA-04` | mandatory | mirror applicability: report version | an inapplicable dimension recorded under mirror report schemaVersion 1.0.0 | reject | `DEFENDED` |
| `NA-05` | mandatory | mirror applicability: counting | the inapplicable dimension counted as a passing one | reject | `DEFENDED` |
| `NA-06` | mandatory | mirror applicability: whole report | every mirror dimension declared inapplicable at once | reject | `DEFENDED` |
| `MIR-A1` | mandatory | mirror integrity: overall result | a failing dimension kept while the overall result claims PASS | reject | `DEFENDED` |
| `FND-01` | mandatory | audit findings: closure record | the closed audit finding set back to OPEN | reject | `DEFENDED` |
| `FND-02` | mandatory | audit findings: closure record | the closure record the audit registry requires deleted | reject | `DEFENDED` |
| `FND-03` | mandatory | audit findings: expected set | the delivery declaring that it has no finding to close | reject | `DEFENDED` |
| `FND-04` | mandatory | audit findings: audit registry | the audit removed from the registry so its findings stop being applicable | reject | `DEFENDED` |
| `FND-05` | mandatory | audit findings: sealed report | the registry repointed at a report from which no finding can be parsed | reject | `DEFENDED` |
| `INT-01` | mandatory | integrity: anchor chain | the anchor of a sealed checkpoint removed from the chain | reject | `DEFENDED` |
| `INT-02` | mandatory | integrity: anchor chain | an anchored commit replaced with one the tag does not resolve to | reject | `DEFENDED` |
| `INT-03` | mandatory | integrity: sealed history | a historical checkpoint tag moved onto another commit | reject | `DEFENDED` |
| `CNT-01` | mandatory | derived counts: COUNTS.json | the derived test count replaced with a larger one | reject | `DEFENDED` |
| `RDY-01` | mandatory | readiness invariant: STATE.json | a blocker carried while the checkpoint claims READY_FOR_REVIEW | reject | `DEFENDED` |
| `PRM-01` | mandatory | promotion: STATE.json | the delivery promoting itself to a cross-tool milestone status | reject | `DEFENDED` |
| `ATT-01` | mandatory | attestation: mechanism | a fresh-session attestation relabelled as a cross-tool one while it records that cross-tool execution was unavailable | reject | `DEFENDED` |
| `ATT-02` | mandatory | attestation: subject | an attestation approved for a commit the subject tag does not resolve to | reject | `DEFENDED` |
| `MEM-01` | mandatory | engineering memory: guarded semantics | a GUARDED lesson stripped of the guardrail it names | reject | `DEFENDED` |
| `SEC-01` | mandatory | secret handling: engineering memory | a credential-shaped value planted in the engineering memory | reject | `DEFENDED` |
| `STL-01` | mandatory | file inventory: FILES.json | an entry removed from the declared change set | reject | `DEFENDED` |
| `CNT-02` | mandatory | derived counts: COUNTS.json | the derived test count set to 9999/9999, then the declared inventory hashes re-derived; inventory refresh exit=0 ['INVENTORY_REFRESHED'] | reject | `DEFENDED` |
| `PRM-02` | mandatory | promotion: STATE.json | the delivery promoting itself to MILESTONE_EXTERNAL_PASS with a filled secondToolValidation, a matching STATUS.md, and the inventory hashes re-derived; inventory refresh exit=0 ['INVENTORY_REFRESHED'] | reject | `DEFENDED` |
| `STL-02` | mandatory | staleness: assurance scope | a policy file edited after the last green Green Keeper cycle, then the declared inventory hashes re-derived; inventory refresh exit=0 ['INVENTORY_REFRESHED'] | reject | `DEFENDED` |

## Observed refusals

- `NA-01`: exit=1; - M0-INTERNAL-MIRROR.json: check MIR-002 is NOT_APPLICABLE without a reason; an unjustified inapplicable check is indistinguishable from a skipped one
- `NA-02`: exit=1; - M0-INTERNAL-MIRROR.json: check MIR-002 is recorded as NOT_APPLICABLE while the canonical sources name 1 applicable audit finding(s) for this checkpoint (.iacode/policies/audit-registry.json matched on gate='SETUP-00' and correctiveCheckpo
- `NA-03`: exit=1; - M0-INTERNAL-MIRROR.json: check MIR-002 is NOT_APPLICABLE with expectedCount=4; a dimension that has items to audit is not inapplicable
- `NA-04`: exit=1; - M0-INTERNAL-MIRROR.json: a NOT_APPLICABLE check requires the justification fields of report schemaVersion 1.1.0
- `NA-05`: exit=1; - M0-INTERNAL-MIRROR.json: passed does not match the recorded checks
- `NA-06`: exit=1; - M0-INTERNAL-MIRROR.json: check MIR-002 is recorded as NOT_APPLICABLE while the canonical sources name 1 applicable audit finding(s) for this checkpoint (.iacode/policies/audit-registry.json matched on gate='SETUP-00' and correctiveCheckpo
- `MIR-A1`: exit=1; - M0-INTERNAL-MIRROR.json: a failed check cannot produce a PASS
- `FND-01`: exit=1; - FAIL MIR-002: 0/1 audit findings CLOSED; CP11-F-001 is OPEN
- `FND-02`: exit=1; - FAIL MIR-002: 0/1 audit findings CLOSED; M0-CP-0011: CP11-FINDINGS-CLOSURE.json is missing
- `FND-03`: exit=1; - FAIL MIR-002: 0/1 audit findings CLOSED; CP11-F-001 is undeclared
- `FND-04`: exit=1; - FAIL MIR-009: 156/156 complete; 118 anchored against an expected set of 105 and 38 declared locally, coverage 100.00, evidence 100.00
- `FND-05`: exit=1; [MIR-002] FAIL Audit findings: the check itself failed: no finding could be parsed from docs/checkpoints/SETUP-00-CP-0012/NO-FINDINGS.md
- `INT-01`: exit=1; INTEGRITY_INVALID
- `INT-02`: exit=1; INTEGRITY_INVALID
- `INT-03`: exit=1; INTEGRITY_INVALID
- `CNT-01`: exit=1; - FILES.json: hash mismatch for docs/checkpoints/SETUP-00-CP-0012/COUNTS.json
- `RDY-01`: exit=1; - READY_FOR_REVIEW is incompatible with a non-empty blockedBy: INVENTED-BLOCKER
- `PRM-01`: exit=1; - status mismatch: STATE.json='MILESTONE_EXTERNAL_PASS', STATUS.md='READY_FOR_REVIEW'
- `ATT-01`: exit=1; - REJECTED .iacode/attestations/M0-CP-0011.json: a CROSS_TOOL_INDEPENDENT_AUDIT records crossToolValidation=AVAILABLE; 'NOT_AVAILABLE' contradicts the mechanism it claims
- `ATT-02`: exit=1; - REJECTED .iacode/attestations/M0-CP-0011.json: attests commit '0000000000000000000000000000000000000000', not the subject commit '90b67a7e0a11179465bc5c92dee22c78da36801f'
- `MEM-01`: exit=1; LESSONS_INVALID
- `SEC-01`: exit=1; LESSONS_INVALID
- `STL-01`: exit=1; - FILES.json omits a changed path: docs/checkpoints/SETUP-00-CP-0012/AFFECTED-RED-TEAM.json (added)
- `CNT-02`: exit=1; - COUNTS.json TESTS=9999/9999 contradicts the derived 410/410
- `PRM-02`: exit=1; - independent audit: a milestone verdict requires STATE.json externalAttestation.subjectCheckpoint naming the sealed checkpoint this audit judged; the verdict belongs to the audit checkpoint, never to the delivery it judges
- `STL-02`: exit=1; - greenKeeper=PASS is STALE: the delivery-assurance scope changed after the last GREEN cycle, so the Green Keeper must run again

## What this battery is not

It is not the independent Red Team of a later audit, and it is not `m0_red_team.py`. It is this audit's own adversarial work against the sealed subject and against the state the `CP11-F-001` repair opened. Mutating a sealed checkout necessarily makes the worktree dirty and the validator says so, so a scenario is judged by whether the refusal it was aimed at appears, never by a non-zero exit code alone.

Three scenarios were first refused by the file-inventory binding before reaching their target. They were re-run as variants that re-derive the declared hashes with the project's own helper, and each was then refused by the control it was aimed at. Both forms are kept, because removing the weaker one would hide why the stronger one exists.
