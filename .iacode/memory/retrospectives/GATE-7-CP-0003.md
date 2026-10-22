# Retrospective — GATE 7 / GATE-7-CP-0003

## What went well

Actual producer/replay tests retained causal failures and null controls, then passed after repair.
See CP0003 causal-attempts/run-0005.json and run-0009.json. Host Docker client and API unit gates
passed in owned execution scopes without restarting applications.

## What failed

M2-F-001 omitted consumed invocation options. M2-F-002 replaced producer evidence with cleanup
failure. The original CP0002 FINDINGS.json remains unchanged. The initial local capture harness
also failed on Windows encoding; its failure receipt is retained, not treated as causal evidence.
Fixture setup/path mistakes, missing local lint images, an invalid formatter boolean and actual
Ruff findings are retained in CP0003 baseline/quality attempts rather than removed by a rerun.

## What repeated

LSN-0010 and LSN-0135 recurred despite GUARDED status. Their recurrence counters increased,
severity was escalated where applicable, and both were returned to CONFIRMED with unresolved
guardrail failures. No count was reset and no internal result is independent validation.

## What was learned

Literal producer invocation must come from supplied tokens, not parsed defaults. A return inside
try is not a durable evidence boundary when cleanup can replace it. Byte capture must precede
decoding; replacement text cannot certify the original byte digest. These refine existing lessons,
not a separate invented taxonomy or a new PASS.

## What should become a guardrail

GRD-0011 now includes actual custom-phase/default/nested-directory command replay. GRD-0137 now
includes actual failing child producers, separate cleanup failure and recoverable safe output
after actual temporary-directory cleanup. Full corrective acceptance and immutable assurance
remain pending; these additions alone do not restore the lessons to GUARDED.

## New lessons

None; both failures belong to existing recurrence classes.

## Updated lessons

| Lesson | Change | Reason |
|---|---|---|
| LSN-0010 | Counter increment, Critical, CONFIRMED, new causal producer controls | M2-F-001 escaped existing shape-only controls |
| LSN-0135 | Counter increment, Critical, CONFIRMED, client producer/cleanup controls | M2-F-002 erased real primary observations |

## Retired lessons

None. All historical evidence, failures and denied reuse rights are retained.
