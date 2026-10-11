# Plan — deterministic full verification correction

The checkpoint follows the mandatory sequence: lesson preflight, canonical requirement derivation,
baseline, plan, implementation, test and quality, Green Keeper, Delivery Completeness Validator,
internal Red Team, Milestone Closure Auditor, and `READY_FOR_REVIEW`. Independent review and the
Gate verdict remain for a later run.

## Delivery slices

| Step | Scope | Exit evidence |
|---|---|---|
| `G4-D00` | Consume the sealed structured finding and register `G4-CP-0004` without rewriting the audit | Parser regression and a derived row anchored to `finding:G4-F-002` |
| `G4-D01` | Give every full/fast verification a checkout-owned Compose project, dynamic host ports, frozen child environment, clean pre-state and post-run cleanup | Unit regressions prove two checkouts cannot share runtime identity or published ports |
| `G4-D02` | Build every live service image before execution and make image consumers resolve the active project image | Gate and lint regressions prove the running and measured artifacts come from the current checkout |
| `G4-D03` | Derive the Prometheus wait from the versioned scrape interval and share the same bounded observer between infra and smoke | Timing regression proves an initial down sample converges without retrying the action under test |
| `G4-D04` | Preserve failing stage diagnostics in the verification report and document the isolated lifecycle | Report regression, ADR and Quality Engine runbook update |
| `G4-D05` | Execute focused order/isolation repetitions, a complete clean 42-stage run, clean-clone validation and every delivery-assurance role | 42/42 single-run report, determinism evidence, Green Keeper, completeness, Red Team and mirror audit |

## Architectural constraints

- Verification runtime identity is derived by the verifier from the checkout; caller configuration
  cannot collapse it back to the shared developer project.
- Host ports are allocated by Docker for the isolated session and discovered through Compose; no
  fixed or guessed port is introduced.
- Cleanup targets only the verifier-owned Compose project and runs before and after the battery.
- Every stage receives one frozen environment; a later stage cannot select another stack.
- Waiting observes Prometheus on its configured cycle and is bounded from the versioned interval;
  it does not rerun a check or extend an unrelated product deadline.
- A failed stage remains failed, keeps its diagnostics, and contributes to the unchanged 42-stage
  denominator. There is no automatic retry.
- G4-X7 and the canonical scanner path remain unchanged except for regression execution.

## Stop conditions

Stop and record `BLOCKED` for predecessor divergence, unavailable Docker or provider access with no
safe in-scope recovery, any red mandatory stage, escaped mandatory attack, incomplete requirement,
shared-runtime collision after isolation, or attempted Gate 5 change.
