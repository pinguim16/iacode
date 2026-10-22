# M2 fresh-session independent review

- Subject: sealed `GATE-7-CP-0001` at `823cf164c6931dab7f957c92721ded7a916655bd`.
- Scope: accumulated Gates 4–7.
- Mechanism: `FRESH_SESSION_INDEPENDENT_AUDIT`, Codex CLI `0.163.0-alpha.10.2`, OpenAI, GPT-5.
- Cross-tool validation: `NOT_AVAILABLE`; this is not `MILESTONE_EXTERNAL_PASS`.
- Audit execution: **`BLOCKED`**.
- Review verdict: **`REWORK_REQUIRED`**. M2 PASS is not granted.

## Findings

### M2-F-001 — HIGH — GUARDRAIL_FAILURE

`new_checkpoint.py` consumed the explicit `--phase` used to create this audit checkpoint but omitted
the option and value from `cmd-0001.command` and `cmd-0001.arguments`. A valid-control Red Team
reproduced the defect in two fresh public clones and showed that the canonical reproducibility
validator accepts the non-literal record. This repeats guarded `LSN-0010`.

### M2-F-002 — CRITICAL — GUARDRAIL_FAILURE

Two real Gate 5 test producers failed while Docker was inaccessible. `client_checks.run_node`
captured each producer in `completed`, then its `finally` cleanup raised a generic exception and
discarded the producer exit code/stdout/stderr. This repeats guarded `LSN-0135`: evidence must be
captured before fallible interpretation or cleanup.

## Evidence that held

- Entry from a new public no-credential clone validated the subject, lessons, 35 predecessor
  anchors and the declared review transport.
- The successor anchor rebuild validated 36 anchors.
- The accumulated denominator was independently derived as 254 Gate rows plus 150 applicable
  lesson rows: 404 total.
- `G4-F-004` was reconstructed independently. CP0007 produced identical `07bb…` archives at
  751,518 bytes that mismatch its `8856…` declaration. CP0009 reproduced `54d1…` twice and the final
  M2 subject reproduced `f2c8…` twice, byte-identical and declaration-matching.
- The canonical `LSN-0010` suite passed 13/13, while the independent optional-argument mutation
  escaped, proving the guardrail gap rather than relying on inherited claims.
- Static compilation passed. The integral control-plane suite ran 984 tests: 980 passed, one was
  skipped, one failed and two errored. Its terminal result is red and no selective run replaces it.

## Blocker and unexecuted evidence

Docker CLI 29.8.1 could not read the user configuration and could not open
`//./pipe/docker_engine`. No alternative config, permission change, restart or broader authority
was used. Therefore the full non-fast verifier, real Gate 4–7 functional flows, stack/migration,
native installation, dependency scan, isolation and full M2 Red Team could not execute. These are
`BLOCKED`, never inferred PASS.

## Verdict

The 45 frozen criteria resolve to 14 PASS, 8 FAIL, 7 PARTIAL and 16 BLOCKED. The audit checkpoint is
blocked from complete execution, the review requires rework, and the milestone remains unapproved.
No attestation exists and Gate 8 was not started.
