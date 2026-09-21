# Handoff

Current Gate: SETUP-00
Current Status: REWORK_REQUIRED

Last valid commit: c53f4c59a77870414324efa6b5f61b35d26c5090
Current branch: main

Checkpoint schema version: `3.2.0`. Base checkpoint: `SETUP-00-CP-0008` at
`c53f4c59a77870414324efa6b5f61b35d26c5090`. Final reference:
`refs/tags/iacode-checkpoints/SETUP-00-CP-0009`, to be resolved with `git rev-parse`.

## Objective

Perform the final `M0` independent audit of `SETUP-00-CP-0008` and decide whether SETUP-00 may
close. The mechanism is `FRESH_SESSION_INDEPENDENT_AUDIT`: a new Claude Code session with no memory
of the implementing run, authorised by the owner because Codex cannot currently execute the flow.
This is not cross-tool validation and is never recorded as one.

## What was completed

- A 183-row audit matrix, written before any substantive step with every row `NOT_STARTED`, and
  completed at 100 per cent execution and 100 per cent evidence.
- The expected requirement set re-derived by an independent parser that does not import
  `policies.py`: 131 expected, 131 declared, 0 missing, 0 unexpected, 0 duplicated.
- All eleven `SETUP-00-CP-0007` findings re-verified by reading each named regression test in its
  source and executing it: 53 of 53 green.
- The twenty-six mandatory attacks and twenty-six additional attacks re-executed by this auditor's
  own harness, which does not import `m0_red_team.py`: 52 of 52 defended, over a null-mutation
  control that validates.
- Thirty-three delivery-assurance, completeness, evidence and staleness scenarios, over an accepted
  baseline; seven history and tag integrity scenarios in temporary repositories; fifteen attestation
  probes; six preflight freshness mutations; the four previously bypassed guardrails plus a
  variation each.
- The engineering memory, the guardrail effectiveness, the semantic counts, the command ledger, the
  documentation links and the sealed history all recomputed independently and found consistent.
- `SETUP-00-CP-0008` anchored in the integrity chain, which its own checkpoint could not do.
- Five findings, eight lesson candidates, and a binary verdict.

## What was NOT completed

No product repair. No attestation. No Gate verdict and no Gate 0 work. The canonical engineering
memory was not modified, and no sealed checkpoint or historical tag was touched.

## Current repository state

Branch `main`, clean after the sealing commits, base commit
`c53f4c59a77870414324efa6b5f61b35d26c5090`, final commit bound by
`refs/tags/iacode-checkpoints/SETUP-00-CP-0009`. `STATE.json` records the exact values.

## Files changed

See `FILES.json` and `DIFF-SUMMARY.md`. Outside this checkpoint only two files changed:
`docs/checkpoints/LATEST.md`, and `.iacode/anchors/checkpoint-chain.json`, which now anchors the
sealed predecessor.

## Important decisions

See `DECISIONS.md`. The load-bearing ones: the attack harness is the auditor's own and carries a
null-mutation control, so a rejection is attributable; and the red mandatory gate was recorded
rather than removed.

## Tests executed

`python -m unittest discover -s tests` — 306/306 in a clean detached clone of the subject's tag,
305/306 in the working repository after this checkpoint anchored its sealed predecessor. The single
failure is finding `CP9-F-002` and was not repaired here.
Also `python -m compileall -q scripts tests`, `validate_lessons.py`, `verify_integrity.py`,
`check_completeness.py`, `derive_requirements.py`, `derive_counts.py`, `m0_red_team.py`,
`m0_mirror_audit.py --clean-clone` and `git diff --check`, all in a clean clone of the subject.

## Known failures

`tests` is red, recorded in `REWORK-LOG.jsonl` and in `QUALITY.json`, with the cause in
`REVIEW-REPORT.md` as `CP9-F-002`. Nothing was weakened to hide it. Two failures in the audit's own
harness are classified `AUDIT_ENVIRONMENT` and described in `AUDIT-EXECUTIONS.md`.

## Known risks

See `RISKS.md`. Especially: the external milestone verdict cannot currently be produced at all; the
mandatory suite is red now; and this audit is session-independent but not tool-independent.

## Do not repeat

Do not treat a control as finished when only its refusals are tested. Do not bind a guardrail test
to the name of the artifact it excludes. Do not run an adversarial battery without a null-mutation
control. Do not describe a same-tool audit as cross-tool validation. Do not edit a test to turn a
gate green.

## Required next action

The corrective delivery described in `NEXT.md`.

## Exact continuation sequence

1. Read `START-HERE.md`, `docs/DEVELOPMENT-CONTRACT.md`, `docs/MASTER-PLAN.md`,
   `docs/SETUP-00-CHECKLIST.md`, `docs/QUALITY-GATES.md`, `docs/CHECKPOINT-PROTOCOL.md`,
   `docs/HANDOFF-PROTOCOL.md`, `docs/DEFINITION-OF-DONE.md`, `docs/ENGINEERING-MEMORY.md`,
   `docs/MILESTONE-VALIDATION.md`, `docs/checkpoints/LATEST.md`, and this complete checkpoint.
2. Read `REVIEW-REPORT.md` first: it carries the acceptance criteria and the regression scenario
   for each finding.
3. Run the validation commands below and compare the observed Git state with `STATE.json`.
4. Open a new SETUP-00 checkpoint whose first action is the lesson preflight.
5. Correct `CP9-F-001` and `CP9-F-002`, assess the three `LOW` findings and the eight lesson
   candidates, and re-run the whole delivery order.
6. Request a new `M0` audit. Never edit a sealed checkpoint and never move a historical tag.

## Validation commands

- `git status --short --branch`
- `git branch --show-current`
- `git rev-parse HEAD`
- `git rev-parse refs/tags/iacode-checkpoints/SETUP-00-CP-0009`
- `python scripts/development-ledger/validate_checkpoint.py`
- `python scripts/development-ledger/validate_lessons.py`
- `python scripts/development-ledger/verify_integrity.py`
- `python scripts/development-ledger/derive_counts.py`
- `python -m compileall -q scripts tests`
- `python -m unittest discover -s tests` — expect 305/306 until `CP9-F-002` is repaired
- `git diff --check c53f4c59a77870414324efa6b5f61b35d26c5090 HEAD`

## How to reproduce this audit

Every recorded result comes from `audit-harness/`. The scripts resolve the repository from their own
location, or from `IACODE_ROOT`, and write to the directory given as their first argument. From a
clean clone:

- `python docs/checkpoints/SETUP-00-CP-0009/audit-harness/derive_expected.py .`
- `python docs/checkpoints/SETUP-00-CP-0009/audit-harness/attacks.py <output-dir>`
- `python docs/checkpoints/SETUP-00-CP-0009/audit-harness/run_scenarios.py <output-dir>`
- `python docs/checkpoints/SETUP-00-CP-0009/audit-harness/run_attestation.py <output-dir>`
- `python docs/checkpoints/SETUP-00-CP-0009/audit-harness/ext_reachability.py <output-dir>`
- `python docs/checkpoints/SETUP-00-CP-0009/audit-harness/run_preflight.py <output-dir>`
- `python docs/checkpoints/SETUP-00-CP-0009/audit-harness/run_guardrails.py <output-dir>`
- `python docs/checkpoints/SETUP-00-CP-0009/audit-harness/run_history.py <output-dir>`
- `python docs/checkpoints/SETUP-00-CP-0009/audit-harness/run_memory.py <output-dir>`
- `python docs/checkpoints/SETUP-00-CP-0009/audit-harness/run_commands.py <output-dir>`
- `python docs/checkpoints/SETUP-00-CP-0009/audit-harness/run_counts_docs.py <output-dir>`

They write only inside disposable clones and the output directory.

## Criteria for PASS of the next audit

Both critical findings closed with a regression test each; the mandatory suite green after a
successor anchors its predecessor; a `MILESTONE_EXTERNAL_PASS` demonstrated end to end through a
valid attestation; and everything this audit already confirmed still confirmed.

## Criteria for REWORK_REQUIRED

Either critical finding still open; any control whose positive path remains untested; any gate made
green by editing a test; any internal verdict presented as external.

## Stop conditions

Stop on unexpected Git divergence, on a failing validation, on any need to modify a sealed
checkpoint or move a historical tag, on secret exposure, or on any request to begin Gate 0 without
authorization.
