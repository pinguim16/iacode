# Diff Summary

Base commit: `98a9f4ca83d538e9610844086ca74b7ff32492e1`
(`refs/tags/iacode-checkpoints/SETUP-00-CP-0011`).

No sealed checkpoint was modified, no historical tag was moved and no commit was rewritten. Every
correction belongs to this checkpoint.

## The repair

| Path | Change |
|---|---|
| `scripts/development-ledger/m0_mirror_audit.py` | A dimension whose canonically derived applicable set is empty is `NOT_APPLICABLE` with a reason, an expected count of zero and a derivation source. `MIR-002` and `MIR-003` derive that set first; a missing or unsatisfied required set stays `FAIL`. The report is `1.1.0` and only a `FAIL` fails it. |
| `scripts/development-ledger/policies.py` | `audit_applicability` derives the applicable findings and mandatory attacks from the audit registry and the sealed reports at every call, and raises rather than reducing to an empty set when a named report cannot be read. `parse_findings` is bounded to the report's own `## Findings` section; `parse_attacks` reads a table by its header. |
| `scripts/development-ledger/validate_checkpoint.py` | The mirror's three counts must add up; an inapplicable dimension must justify itself; report version `1.0.0` may not carry one; `_validate_mirror_applicability` re-derives the registry-bound dimensions so a delivery cannot declare away work the canonical sources name. |
| `.iacode/schemas/mirror-audit.schema.json` | Report version `1.1.0` adds `reason`, `expectedCount` and `derivationSource`. Sealed `1.0.0` reports keep the rules they were written for. |

## The controls that prove it

| Path | Change |
|---|---|
| `scripts/development-ledger/mirror_semantics_validation.py` | New. Executes the real mirror audit over six applicability states, three of them negative. |
| `scripts/development-ledger/gate_transition_simulation.py` | New. Executes the transition from a closed milestone into the first delivery of the next Gate, to `READY_FOR_REVIEW`. |
| `scripts/development-ledger/promotion_fixture.py` | Executes `m0_mirror_audit.py` instead of writing its artifact; gains the Gate transition and the mirror scenario builders; `deliver_checkpoint` takes the Gate it delivers. |
| `scripts/development-ledger/promotion_simulation.py` | Two new checks: the mirror was executed, and its inapplicable dimensions are justified. Declares which artifacts were executed and which were modelled. |
| `scripts/development-ledger/m0_red_team.py` | Five scenarios against the state the repair opens, and the twelve mandatory attacks the sealed `SETUP-00-CP-0011` battery hands this delivery. |
| `tests/test_development_ledger.py` | Positive and negative regression for the applicability semantics, the sealed report renderings, the Gate transition and the simulation rule. |

## Policy, contract and memory

| Path | Change |
|---|---|
| `docs/SETUP-00-CHECKLIST.md` | Canonical row `7d.16`. |
| `.iacode/policies/canonical-requirements.json` | Mirrors row `7d.16`. |
| `.iacode/policies/audit-registry.json` | Registers `M0-CP-0011` with this checkpoint as its corrective delivery. |
| `docs/QUALITY-GATES.md` | The empty-applicable-set versus missing-required-set distinction, and the rule that a simulation executes the control it reports. |
| `docs/DEVELOPMENT-CONTRACT.md`, `docs/DEFINITION-OF-DONE.md` | The same two rules, in the contract and in the completion standard. |
| `.iacode/agents/m0-closure-auditor.md` | The applicability rule, the verdict rule, and the harness rule. |
| `.iacode/memory/lessons.jsonl`, `.iacode/memory/guardrails/registry.json`, `.iacode/memory/LESSONS.md` | `LSN-0031`; `GRD-0030`, `GRD-0031`, `GRD-0032`; the `GUARDRAIL_FAILURE` recorded against `LSN-0024` and `LSN-0029` and resolved here. |
| `CLAUDE.md` | The permanent rule that every response to the user is written in Brazilian Portuguese, and which technical literals stay unchanged. |
| `.iacode/anchors/checkpoint-chain.json` | This checkpoint anchors its sealed predecessor `SETUP-00-CP-0011`. |
| `docs/checkpoints/LATEST.md` | Points at this checkpoint. |

## The checkpoint

`docs/checkpoints/SETUP-00-CP-0012/` is new in full. Besides the standard ledger it carries
`FINAL-CORRECTION-REQUIREMENTS.*`, `CP11-FINDINGS-CLOSURE.*`, `MIRROR-SEMANTICS-VALIDATION.*`,
`GATE0-TRANSITION-SIMULATION.*`, `POSITIVE-PROMOTION-VALIDATION.*`, `SUCCESSOR-DURABILITY.*`,
`AFFECTED-RED-TEAM.*`, `FINAL-INTERNAL-AUDIT.*`, `M0-INTERNAL-RED-TEAM.*` and
`M0-INTERNAL-MIRROR.*`.

The complete declaration, with a reason and bound content hashes for every path, is in `FILES.json`.
