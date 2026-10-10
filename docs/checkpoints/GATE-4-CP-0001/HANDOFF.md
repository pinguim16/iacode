# Handoff

Current Gate: GATE-4
Current Status: READY_FOR_REVIEW

Last valid commit: recorded by `STATE.json` and the canonical checkpoint tag after sealing
Current branch: main

## Objective

Deliver the Gate 4 Quality Engine with sandbox-only execution, immutable evidence, durable
lifecycle, fail-closed verdicts, reproducible functional proof and complete closure evidence.

## What was completed

- Implemented closed quality contracts, profiles, planning, runners, findings, verdict derivation,
  evidence storage, persistence, Temporal workflow, API and Agent Runtime integration.
- Added pinned Python, Node/TypeScript/Angular and Maven/Gradle toolchain images that execute only
  through the network-disabled sandbox.
- Proved PASS, FAIL, IACode, reproduction, restart recovery, cancellation, timeout, sandbox coding
  and forged-result rejection against the real stack.
- Passed 42/42 complete-verifier stages, 1,675/1,675 counted tests, 13/13 mandatory gates in the
  final Green Keeper cycle, 194/194 requirements with 100% evidence coverage, and 10/10 internal
  false-PASS attacks over a valid control.
- Passed the internal M2 mirror with 16 PASS, two justified `NOT_APPLICABLE` outcomes and zero FAIL;
  its clone passed suite, compilation, lessons, integrity and completeness. The 235-entry review
  bundle also passed manifest, path, content and secret validation.
- Added permanent functional-acceptance, program-state, review-bundle and closure controls plus the
  Gate 4 retrospective and guardrails.

## What was NOT completed

Independent review, independent Red Team, `GATE_PASS`, and Gate 5 were not performed. The internal
Red Team and mirror are same-session assurance and cannot supply those verdicts.

## Current repository state

See `STATE.json`. The implementing checkpoint closes at `READY_FOR_REVIEW`, with no blocker;
independent and milestone verdict fields remain pending.

## Files changed

See `FILES.json` and `DIFF-SUMMARY.md`. The footprint covers quality-domain implementation,
sandbox toolchains, integration surfaces, permanent tests, policies, documentation, engineering
memory and this checkpoint's evidence.

## Important decisions

See `DECISIONS.md` and ADR-0029 through ADR-0031. Project commands remain sandbox-only, evidence
bytes are content-addressed while references remain run-scoped, and verdicts are always re-derived.

## Tests executed

See `TESTS.json`, `COUNTS.json`, `VERIFY.json`, `FUNCTIONAL-ACCEPTANCE-VALIDATION.json`,
`REWORK-LOG.jsonl`, `COMPLETENESS-REPORT.json`, `M2-INTERNAL-RED-TEAM.json` and the internal mirror
report.

## Known failures

None remain open. Preserved red artifacts and nonzero command records document repaired failures;
they are not hidden or reclassified as passing executions.

## Known risks

See `RISKS.md`. In particular, live container behavior must be reproduced by the later reviewer,
and internal assurance is not an independent verdict.

## Do not repeat

- Do not run project commands outside the sandbox or restore network access to quality runners.
- Do not accept caller-supplied verdicts, unresolved evidence, mutable plans or forged origins.
- Do not narrow the 194-row denominator or the mandatory gate set.
- Do not describe this run's internal Red Team or mirror as independent validation.
- Do not start Gate 5 before an independent Gate 4 pass and explicit owner authorization.

## Required next action

Run a later independent review of the sealed `GATE-4-CP-0001` subject in a new checkpoint. See
`NEXT.md`.

## Exact continuation sequence

1. Validate the sealed checkpoint, canonical tag, integrity chain and authorized remote.
2. Open a new independent review checkpoint without changing the sealed subject.
3. Re-derive the Gate 4 requirements and reproduce the required clean, live and adversarial checks.
4. Record independent review and Red Team evidence, including `secondToolValidation`.
5. Grant or refuse `GATE_PASS`; do not start Gate 5 in the same implementing checkpoint.

## Validation commands

```powershell
python scripts/development-ledger/validate_checkpoint.py
```

```powershell
python scripts/development-ledger/verify_integrity.py
```

```powershell
python scripts/development-ledger/remote_sync.py --tag iacode-checkpoints/GATE-4-CP-0001
```

## Stop conditions

Stop on repository/state divergence, a missing or moved tag, remote mismatch, stale assurance,
unresolved evidence, any mandatory-gate failure, or any attempt to rewrite the sealed subject or
advance to Gate 5 without the required independent verdict and owner authorization.
