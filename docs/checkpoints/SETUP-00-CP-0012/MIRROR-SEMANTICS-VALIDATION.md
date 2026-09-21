# Mirror Semantics Validation

Result: `PASS`

- Validation: internal mirror audit applicability semantics
- Closes: `CP11-F-001`
- Generated: `2026-09-21T12:40:28Z`

An empty applicable set and a missing required set are different states. Only the first is
benign, and it is recorded as `NOT_APPLICABLE` with a reason, an expected count of zero and
the canonical source the emptiness was derived from. Every row below was produced by
executing `scripts/development-ledger/m0_mirror_audit.py` in a disposable repository;
no row asserts a result and none writes the artifact the tool would have produced.

| Check | State under test | Expected | Observed | Result |
|---|---|---|---|---|
| `MSV-001` | a delivery that corrects no audit | overall=PASS, MIR-002=NOT_APPLICABLE, MIR-003=NOT_APPLICABLE, sealed=True | overall=PASS; MIR-002=NOT_APPLICABLE; MIR-003=NOT_APPLICABLE; sealed=True | `PASS` |
| `MSV-002` | a delivery whose applicable findings and attacks are all satisfied | overall=PASS, MIR-002=PASS, MIR-003=PASS, sealed=True | overall=PASS; MIR-002=PASS; MIR-003=PASS; sealed=True | `PASS` |
| `MSV-003` | a delivery with an applicable finding still open | overall=FAIL, MIR-002=FAIL, MIR-003=PASS, sealed=False | overall=FAIL; MIR-002=FAIL; MIR-003=PASS; sealed=False | `PASS` |
| `MSV-004` | a delivery that omits the closure record the registry requires | overall=FAIL, MIR-002=FAIL, MIR-003=PASS, sealed=False | overall=FAIL; MIR-002=FAIL; MIR-003=PASS; sealed=False | `PASS` |
| `MSV-005` | a delivery declaring that it has nothing to close | overall=FAIL, MIR-002=FAIL, MIR-003=PASS, sealed=False | overall=FAIL; MIR-002=FAIL; MIR-003=PASS; sealed=False | `PASS` |
| `MSV-006` | a delivery that did not execute an applicable mandatory attack | overall=FAIL, MIR-002=PASS, MIR-003=FAIL, sealed=False | overall=FAIL; MIR-002=PASS; MIR-003=FAIL; sealed=False | `PASS` |

## Why each state is the outcome it is

### `MSV-001` — a delivery that corrects no audit

No registered audit names this checkpoint as its corrective delivery, so the applicable set is empty by derivation. This is the state the finding made unreachable, and the delivery must reach a handoff-ready status in it.

- `MIR-002`: `NOT_APPLICABLE` — 0 applicable audit findings derived from the audit registry
- `MIR-003`: `NOT_APPLICABLE` — 0 applicable mandatory attacks derived from the audit registry
- Executed: `python scripts/development-ledger/m0_mirror_audit.py --write --checkpoint C:\Users\cesar\AppData\Local\Temp\iacode-mirror-semantics-74d6reai\no-applicable-audit\docs\checkpoints\SETUP-00-CP-0001`, exit `0`

- `MIR-002` justification: No audit finding is applicable to this checkpoint: no registered audit names it as its corrective delivery, so there is no finding to close.
- `MIR-002` expected items: `0`, derived from .iacode/policies/audit-registry.json matched on gate='SETUP-00' and correctiveCheckpoint='SETUP-00-CP-0001', with every finding and mandatory attack re-parsed from the sealed reports the matching entries name

- `MIR-003` justification: No mandatory attack battery is applicable to this checkpoint: no registered audit names it as its corrective delivery, so no sealed Red Team report hands it a battery to re-defend.
- `MIR-003` expected items: `0`, derived from .iacode/policies/audit-registry.json matched on gate='SETUP-00' and correctiveCheckpoint='SETUP-00-CP-0001', with every finding and mandatory attack re-parsed from the sealed reports the matching entries name

### `MSV-002` — a delivery whose applicable findings and attacks are all satisfied

Three findings are applicable and all three are CLOSED; two mandatory attacks are applicable and both were defended. The repair must not have replaced the check with an unconditional pass.

- `MIR-002`: `PASS` — 3/3 audit findings CLOSED
- `MIR-003`: `PASS` — 2/2 mandatory attacks defended; 2/2 overall
- Executed: `python scripts/development-ledger/m0_mirror_audit.py --write --checkpoint C:\Users\cesar\AppData\Local\Temp\iacode-mirror-semantics-74d6reai\closed-findings\docs\checkpoints\SETUP-00-CP-0001`, exit `0`

### `MSV-003` — a delivery with an applicable finding still open

A non-empty applicable set with an unsatisfied item is a failure, and the delivery cannot be sealed. This is what stops the repair from becoming a vacuous pass.

- `MIR-002`: `FAIL` — 2/3 audit findings CLOSED; FIX-F-003 is OPEN
- `MIR-003`: `PASS` — 1/1 mandatory attacks defended; 1/1 overall
- Executed: `python scripts/development-ledger/m0_mirror_audit.py --write --checkpoint C:\Users\cesar\AppData\Local\Temp\iacode-mirror-semantics-74d6reai\open-finding\docs\checkpoints\SETUP-00-CP-0001`, exit `1`

### `MSV-004` — a delivery that omits the closure record the registry requires

The canonical sources name a finding and the artifact that would close it is absent. A missing required set is never an empty applicable set.

- `MIR-002`: `FAIL` — 0/1 audit findings CLOSED; M0-FIXTURE-AUDIT: FIXTURE-FINDINGS-CLOSURE.json is missing
- `MIR-003`: `PASS` — 1/1 mandatory attacks defended; 1/1 overall
- Executed: `python scripts/development-ledger/m0_mirror_audit.py --write --checkpoint C:\Users\cesar\AppData\Local\Temp\iacode-mirror-semantics-74d6reai\missing-closure-record\docs\checkpoints\SETUP-00-CP-0001`, exit `1`

### `MSV-005` — a delivery declaring that it has nothing to close

The checkpoint declares an empty expected set while the registry and the sealed report name one open finding. The applicable set is derived from the canonical sources and no artifact inside the delivery can shrink it, so the declaration changes nothing and the open finding still fails.

- `MIR-002`: `FAIL` — 0/1 audit findings CLOSED; FIX-F-001 is OPEN
- `MIR-003`: `PASS` — 1/1 mandatory attacks defended; 1/1 overall
- Executed: `python scripts/development-ledger/m0_mirror_audit.py --write --checkpoint C:\Users\cesar\AppData\Local\Temp\iacode-mirror-semantics-74d6reai\forged-empty-applicable-set\docs\checkpoints\SETUP-00-CP-0001`, exit `1`

### `MSV-006` — a delivery that did not execute an applicable mandatory attack

A mandatory attack the sealed report hands the delivery was not executed. The battery dimension is applicable and unsatisfied, which is a failure.

- `MIR-002`: `PASS` — 1/1 audit findings CLOSED
- `MIR-003`: `FAIL` — 1/2 mandatory attacks defended; 1/1 overall; not executed: FIX-02
- Executed: `python scripts/development-ledger/m0_mirror_audit.py --write --checkpoint C:\Users\cesar\AppData\Local\Temp\iacode-mirror-semantics-74d6reai\undefended-mandatory-attack\docs\checkpoints\SETUP-00-CP-0001`, exit `1`

Passed: `6` of `6` states.
