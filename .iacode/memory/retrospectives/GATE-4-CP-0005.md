# Retrospective — GATE 4 corrective run / GATE-4-CP-0005

This retrospective records concise repository evidence, decisions and consequences. It contains no
private chain-of-thought, personal data or secret.

## What went well

The independent audit preserved its failed 40/42 complete run instead of replacing it with two
green isolated reruns. That evidence made order and state ownership part of the correction rather
than an unexamined timing adjustment.

The targeted order probe exercised the historical `stack -> integration -> infra -> smoke`
sequence twice from clean project state, with no retry after failure and with project cleanup after
each cycle. Evidence: `docs/checkpoints/GATE-4-CP-0005/ORDER-ISOLATION-PROBE.json`.

## What failed

The full verifier did not own a runtime namespace. Independent checkouts selected the same Compose
project, fixed host ports, image tags and volumes, and the stack stage could measure images built by
another checkout. This became `LSN-0095` and `GRD-0096`.

The infrastructure test queried Prometheus immediately after stack start. That was the same
asynchronous-observation class already guarded by `LSN-0049`, but its control covered scripts and
not the infrastructure test path.

The first published full-verification harness decoded child output as UTF-8 but did not configure
its own Windows stdout. Angular emitted U+276F during `gate:webTests`, reproducing `LSN-0083` and
ending `cmd-0040` before a verifier report could be written.

## What repeated

`LSN-0049` recurred for a second time and is recorded as a `GUARDRAIL_FAILURE`, not a new unrelated
defect. `GRD-0051` now includes the shared, versioned scrape-cycle observer used by both smoke and
the running-stack infrastructure test.

`LSN-0083` recurred once because `GRD-0084` scanned executable files under `scripts/` but not the
current checkpoint's executable evidence harness. The same control now scans both locations.

## What was learned

- A verifier that names an order but does not own the state traversed by that order is not
  deterministic evidence.
- Clean-clone source identity is insufficient when Docker runtime identity is shared across clones.
- An isolated rerun diagnoses a failure but never supersedes the failed complete execution.
- Bounded observation waits are policy derived; repeating the action, restarting the stack, raising
  a timeout, or changing the denominator would conceal rather than repair this failure class.

## What should remain guardrails

| Failure class | Lesson | Guardrail | Permanent evidence |
|---|---|---|---|
| asynchronous observation before its cycle | `LSN-0049` | `GRD-0051` | shared observer policy and infrastructure/smoke regression |
| Compose runtime shared across checkouts | `LSN-0095` | `GRD-0096` | verifier ownership, cleanup, build, frozen-environment and order controls |
| captured UTF-8 re-emitted through platform codepage | `LSN-0083` | `GRD-0084` | repository-wide script/current-harness stream scan |

## New lessons

`LSN-0095` records checkout-scoped ownership of the complete verifier runtime.

## Updated lessons

`LSN-0049` was escalated to `HIGH`, its recurrence count advanced to two, and its guardrail was
widened to the infrastructure test path. `LSN-0083` was escalated to `HIGH`, its recurrence count
advanced to one, and its guardrail was widened to the current checkpoint evidence harness.

## Retired lessons

No lesson was retired by this corrective run.
