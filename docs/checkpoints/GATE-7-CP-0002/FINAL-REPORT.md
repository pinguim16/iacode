# Final report — GATE-7-CP-0002

## Outcome

- Audit execution: `BLOCKED`.
- Independent review: `REWORK_REQUIRED`.
- Independent Red Team: `RED_TEAM_FAIL`.
- M2 verdict: `NOT_GRANTED`.
- `MILESTONE_EXTERNAL_PASS`: not applicable and not claimed.
- Gate 8: not started.

## Principal findings

- `M2-F-001` — High `GUARDRAIL_FAILURE`: checkpoint creation omits a consumed optional `--phase`
  from its supposedly literal command record; a valid-baseline mutation escapes the canonical
  reproducibility validator.
- `M2-F-002` — Critical `GUARDRAIL_FAILURE`: fallible client-container cleanup replaces and loses
  the producing process exit/stdout/stderr in two real canonical tests.

## Executed evidence

- Canonical entry and public no-credential detached validation of the exact subject.
- Complete byte read/parse of all 610 subject checkpoint files.
- Accumulated 404-row M2 requirement derivation and 45 frozen audit criteria.
- Integrity-chain rebuild to 36 anchors.
- Six public review-transport clones plus two final historical-red retry clones; exact independent
  `G4-F-004` red/green reconstruction and final bundle equality.
- Independent command-ledger Red Team with a valid clean control and one confirmed escape.
- Canonical command-reproducibility tests: 13/13 pass, demonstrating the gap.
- Canonical control-plane suite: 984 run in 11,933.798 seconds; 980 pass, 1 skip, 1 fail, 2 errors;
  effective exit 1, preserved without selective replacement.
- Canonical static compilation: exit 0.
- Canonical audit-checkpoint completeness: exit 1; 198 rows `NOT_STARTED`, 0.00% completion
  coverage and 100.00% evidence coverage. This records the failed assurance state and is not used
  to narrow the separate 404-row accumulated M2 audit derivation.
- Canonical final checkpoint validation: exit 1 in 183,091 ms. The retained errors include red
  command evidence, the pre-existing authorized report's secret-scan match, and the auditor's
  preserved `cmd-0003` declaration of a nonexistent input path.

## Limitations and blockers

Docker client/server probing ended with permission denied on the engine named pipe. The auditor did
not change Docker configuration, permissions, WSL/services or applications. The complete verifier,
real Gate 4–7 functional proof, full Red Team, live dependency scan and stack/migration/isolation
evidence are therefore absent. Cross-tool validation was not available.

The first bundle reconstruction failed on Windows path length, the second left only CP0007 blocked
by Schannel credentials, and the third reproduced CP0007 successfully with process-scoped OpenSSL
and long-path settings. The first Red Team harness had an invalid default-phase expectation; its
corrected retry used new clones. All attempts remain distinct.

The final validator initially also identified removable schema/heading defects in this auditor's
own metadata and handoff. Those audit-document forms were corrected after preserving the terminal
receipt; no subject code, test, policy, sealed checkpoint or failed command record was rewritten.
Because the audit checkpoint was not accepted by validation, `docs/checkpoints/LATEST.md` remains
on the last accepted checkpoint, `GATE-7-CP-0001`; the blocked audit evidence remains at
`docs/checkpoints/GATE-7-CP-0002` and must not be represented as sealed or valid.

## Required next action

A later implementer must register and correct `M2-F-001` and `M2-F-002`, add causal regressions,
seal a new immutable Gate 7 corrective delivery, and request another fresh independent M2 audit in
an environment that grants owned Docker Engine access. This audit checkpoint and its failed
evidence must not be rewritten into PASS.
