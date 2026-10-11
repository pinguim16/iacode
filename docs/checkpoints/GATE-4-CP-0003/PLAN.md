# Plan — Gate 4 credential-evidence containment correction

The checkpoint follows the mandatory sequence: lesson preflight, canonical requirement derivation,
baseline, plan, implementation, test and quality, Green Keeper, Delivery Completeness Validator,
internal Red Team, Milestone Closure Auditor, and `READY_FOR_REVIEW`. Independent review and the
Gate verdict remain for a later run.

## Delivery slices

| Step | Scope | Exit evidence |
|---|---|---|
| `G4-C00` | Make the canonical audit parser consume the sealed `## Blocking finding` prose without changing the sealed report or accepting unbounded mentions | Focused parser regression and successful requirement derivation |
| `G4-C01` | Move the canonical secret taxonomy into the shared common package and make the repository scanner derive from it | Common and ledger tests proving one taxonomy |
| `G4-C02` | Scan fully serialized evidence before lookup, object write, or metadata commit; fail closed if scanning fails; refuse secret-bearing legacy objects on resolution | Evidence-store tests proving zero durable writes and failed resolution |
| `G4-C03` | Convert containment refusal into a durable sanitized `ERROR` quality result so the workflow terminates with `FAIL` and leaks no prohibited bytes | Exact activity-to-store regression for an innocuous structured key |
| `G4-C04` | Add mandatory `G4-X7`, lesson, guardrail, ADR, runbook, and closure evidence | Internal attack defended and finding closure resolvable |
| `G4-C05` | Run the full 42-stage verifier and assurance roles in policy order | Green Keeper, completeness, internal Red Team, mirror audit, sealed checkpoint |

## Architectural constraints

- One shared source owns the scanner taxonomy; callers may not carry a weaker copy.
- The scan runs over the exact serialized bytes before any content-addressed lookup or write.
- Detection and scanner failure both fail closed with stable, non-secret reason codes.
- Rejected evidence creates no object or metadata row and cannot support a verdict.
- The activity persists only a sanitized `ERROR` result, with no rejected evidence or raw output.
- The resolution path rechecks stored bytes so pre-existing or externally injected material cannot
  become valid evidence.

## Stop conditions

Stop and record `BLOCKED` for predecessor divergence, an unavailable required service with no safe
in-scope recovery, a scanner false negative, any persisted prohibited marker, a nonterminal workflow
after containment, or an irreparable mandatory-gate failure. Never weaken the scanner, requirement,
denominator, verdict rule, or promotion policy.
