# Baseline — GATE-0-CP-0001

The observed state before any Gate 0 change, recorded so that what this delivery added is
attributable rather than assumed. `docs/DEVELOPMENT-CONTRACT.md` requires the baseline before the
plan.

## Repository

| Observation | Value |
|---|---|
| Branch | `main` |
| HEAD | `b5b594660584092c74738bdda3d8bca9b210b406` |
| Worktree | clean |
| HEAD tag | `refs/tags/iacode-checkpoints/SETUP-00-CP-0013` |
| Latest checkpoint | `docs/checkpoints/SETUP-00-CP-0013` |

## Gate authorization, derived rather than read

The previous Gate's status was confirmed by derivation, not by reading a status field:

```text
python scripts/development-ledger/milestone_status.py --milestone M0
MILESTONE_PASSED milestone=M0 attestations=2 accepted=1
- M0-CP-0013: SETUP-00-CP-0012 at 3f730dca... audited by SETUP-00-CP-0013
  (FRESH_SESSION_INDEPENDENT_AUDIT); authorises MILESTONE_INDEPENDENT_AUDIT_PASS
- REJECTED .iacode/attestations/M0-CP-0011.json: reviewResult is 'REWORK_REQUIRED'
```

`SETUP-00` is closed, `M0` is `PASSED`, and `GATE 0 — FOUNDATION` is authorised by the milestone.
The owner's authorization to open it was given in this run's instruction.

## Control plane at baseline

| Control | Result |
|---|---|
| `validate_checkpoint.py` | `CHECKPOINT_VALID` |
| `validate_lessons.py` | `LESSONS_VALID total=31 active=31 guarded=29` |
| `verify_integrity.py` | `INTEGRITY_VALID anchors=12 latest=SETUP-00-CP-0012` |
| `derive_counts.py` | recomputed the predecessor's counts exactly as `docs/checkpoints/SETUP-00-CP-0013/COUNTS.json` records them |
| `check_completeness.py` | `PASS coverage=100.00 evidenceCoverage=100.00` |
| `python -m unittest discover -s tests` | 410 discovered, 403 run, 1 error |

The baseline counts are not restated here. A count written into a checkpoint document is read as a claim about *that* checkpoint, which is the control that keeps a narrative from drifting from the derivation; the predecessor's sealed `COUNTS.json` is the stronger reference anyway, because it cannot be edited.

The suite error is the baseline's one finding and it was expected: `GateTransitionSimulationTests`
installs a synthetic `GATE-0` specification into a disposable repository, and this Gate's real
specification collided with it. It is recorded here as the starting condition rather than
discovered later; the repair is in `DECISIONS.md`.

## Runtime at baseline

Nothing. No `apps/`, no `services/`, no `packages/`, no `infra/`, no application code of any kind.
The repository carried the SETUP-00 control plane and its documentation.

| Directory | At baseline |
|---|---|
| `apps/` | absent |
| `services/` | absent |
| `packages/` | absent |
| `infra/` | absent |
| `agents/`, `training/`, `evaluation/`, `datasets/` | absent |
| `scripts/` | `development-ledger/` only |
| `tests/` | `test_development_ledger.py` only |

## Environment

Measured on the machine this Gate was delivered on, because the Gate's deliverable is a stack that
runs locally and the versions it can use are a property of that environment.

| Tool | Version | Consequence |
|---|---|---|
| Python | 3.13.15 | the tooling and the API both run on it |
| Docker | 29.6.1 | available; Compose v5.2.0 |
| Git | 2.52.0 | available |
| Node | 18.16.1 | **too old** for the Angular toolchain, which needs 22 |

The Node version is the observation that shaped a decision: the frontend is built and tested inside
a container with a pinned Node, so the repository does not require Node on the developer's machine
at all. See `docs/adr/ADR-0012-foundation-runtime-stack.md`.

Seventeen containers from other projects were already running on this machine, publishing ports
including `9090` and `3000`. Every port this stack publishes is therefore configurable and defaults
to a range chosen to avoid the common ones, verified free before the defaults were fixed.
