# Next

## Required next action

`FINAL FRESH-SESSION INDEPENDENT M0 AUDIT OF SETUP-00-CP-0010`.

Open a new session with no memory of this run and audit this checkpoint as the `M0` milestone
delivery. The audit is the mechanism `FRESH_SESSION_INDEPENDENT_AUDIT`: independent of the
implementing run, not of the tool, and it is never described as cross-tool validation.

The audit follows the corrected model, which is the whole point of `CP9-F-001`:

1. Audit `SETUP-00-CP-0010` at its canonical tag. Do not modify it, do not move its tag, and do not
   re-seal it. A sealed subject stays immutable.
2. Open your own checkpoint, `SETUP-00-CP-0011`. Anchor `SETUP-00-CP-0010` in
   `.iacode/anchors/checkpoint-chain.json`, which its own checkpoint could not do.
3. Write your attestation to `.iacode/attestations/<auditId>.json` before running your gates, so
   the assurance results describe the content you actually seal. It names
   `subjectCheckpoint: SETUP-00-CP-0010`, the commit that checkpoint's tag resolves to,
   `auditCheckpoint: SETUP-00-CP-0011`, `validationMechanism: FRESH_SESSION_INDEPENDENT_AUDIT`,
   `crossToolValidation: NOT_AVAILABLE`, and the four results.
4. Record the same verdict in your own `STATE.json`: `externalAttestation.subjectCheckpoint`, the
   attestation path and its audit id, `independentReview`, `redTeam`, `secondToolValidation` and
   `milestone`.
5. Close your checkpoint at `MILESTONE_INDEPENDENT_AUDIT_PASS` when the audit passes, or at
   `REWORK_REQUIRED` when it does not. `MILESTONE_EXTERNAL_PASS` is refused for this mechanism, and
   the refusal is a control, not an obstacle.
6. Derive the verdict rather than trusting it:
   `python scripts/development-ledger/milestone_status.py --milestone M0`.

`python scripts/development-ledger/promotion_simulation.py` executes exactly that sequence in a
disposable repository, and `POSITIVE-PROMOTION-VALIDATION.md` records what it observed.

## What to audit

- The five `CP9` findings, against `CP9-FINDINGS-CLOSURE.json` and the regression tests it names.
- The positive paths: that a milestone PASS is reachable and that advancing the sealed chain keeps
  every mandatory gate green.
- Everything the `CP-0009` audit already confirmed, which this delivery did not intend to change.
- The new surfaces: the attestation model, the derived anchor exclusion, the count deduplication,
  the null-mutation control, the memory policy schema, and the two simulation entry points.

## Next Gate

`GATE 0 — FOUNDATION` remains `BLOCKED`. It requires a passing `M0` audit, explicit authorization,
and a new pre-Gate checkpoint. No Gate 0 work exists in this change set, and this delivery did not
begin any.
