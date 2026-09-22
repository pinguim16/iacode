# Baseline — GATE-1-CP-0001

What was true before this Gate changed anything, and the authorization it proceeded under.

## Authorization

GATE 1 — MODEL GATEWAY, milestone `M1`, authorized explicitly and scoped to this Gate alone. Not
GATE 2, not GATE 3, and not the `M1` audit: `M1` stays `PENDING` and is audited after Gate 3.

The Gate closes at `INTERNAL_GATE_PASS` on the project's own controls. No independent, fresh-session
or cross-tool verdict is claimed.

## Predecessor state

| Fact | Value |
|---|---|
| Previous Gate | `GATE 0 — FOUNDATION` |
| Previous checkpoint | `GATE-0-CP-0001`, sealed |
| Previous status | `INTERNAL_GATE_PASS` |
| Base commit | `195739ffd5a588a55096ebd8a6a7f64057e1f66d` |
| Branch | `main` |
| Milestone `M0` | passed its independent audit |
| Milestone `M1` | `PENDING` |

`validate_checkpoint.py` passed against `GATE-0-CP-0001` before any file was changed. The observed
Git state matched `STATE.json`, so no `DIVERGENCE.md` was required.

## What existed

The SETUP-00 development control plane and the Gate 0 Foundation runtime: an API, a Temporal
worker, a web shell, PostgreSQL, Redis, MinIO, Temporal, Prometheus and Grafana on Docker Compose,
with migrations, backup and restore, observability, nine mandatory quality gates and the ledger
tooling.

`services/model-gateway/` existed as a reservation: a README saying `Status: RESERVED` and nothing
else. `.iacode/policies/gate-scope.json` recorded GATE 1 as its owner.

The database already carried the tables this Gate needed to extend — `providers`, `models`,
`model_calls` — created by `0001_foundation` as a persistence contract rather than as a feature.

## What was wrong at the baseline, and was found during this Gate

Two defects existed at `HEAD` before this Gate began and were not visible from the Gate 0 evidence:

1. **A red test behind a green gate.** `test_a_documented_placeholder_is_not_redacted` was failing
   at `HEAD`. The `apiTests` gate executes pytest inside the API image and nothing rebuilt that
   image, so the gate had been reporting on stale source throughout Gate 0. Recorded as `LSN-0036`.
2. **The defect it concealed.** `redact_text` and `redact_value` disagreed about what a placeholder
   is, so the committed example environment file was redacted by one path and not the other.
   Recorded as `LSN-0038`.

Both were repaired inside this Gate, with guardrails, before the Gate's own work was measured. A
Gate that inherits a red test and does not say so is a Gate whose evidence begins with a lie.

## Lesson preflight

`lesson_preflight.py --gate GATE-1 --scope model-gateway`, with the technologies and modules this
Gate actually uses. Thirty-four lessons applicable, thirty-four `LESSON-REQ-` requirements derived
and carried into the matrix.

## Requirement set

| Source | Count |
|---|---|
| `docs/GATE-1-CHECKLIST.md` (18 sections) | 122 |
| Lesson preflight | 34 |
| **Total in `REQUIREMENTS-MATRIX.json`** | **156** |

All 122 canonical rows are mandatory. The mirror in `.iacode/policies/canonical-requirements.json`
was generated from the checklist by `policies.parse_checklist`, not transcribed.

## Credential position at the baseline

No provider credential was configured. The Gate proceeded through every deterministic requirement
and stopped at the live integration, reporting `GATEWAY_SMOKE=BLOCKED` and naming the variable that
was missing. No live result was claimed while that was true.
