# Handoff

Current Gate: GATE-0
Current Status: INTERNAL_GATE_PASS

Last valid commit: recorded in `STATE.json`
Current branch: main

Checkpoint schema version: `3.2.0`. Base checkpoint: `SETUP-00-CP-0013`. Final reference:
`refs/tags/iacode-checkpoints/GATE-0-CP-0001`, to be resolved with `git rev-parse`.

## Objective

Deliver `GATE 0 — FOUNDATION`: a local, reproducible runtime foundation that a new machine can bring
up from this repository alone. Implement nothing that belongs to a later Gate.

## What was completed

- **The Gate's canonical specification**, `docs/GATE-0-CHECKLIST.md`, mirrored row for row by
  `.iacode/policies/canonical-requirements.json`. It is the first deliverable because the expected
  requirement set is derived from it.
- **The backend**: a FastAPI application with typed configuration validated at start-up, an explicit
  dependency lifecycle, `/health`, `/ready`, `/version` and `/metrics`, structured JSON logging,
  request correlation, an error contract that gives the caller a safe summary and the operator the
  traceback, and explicit CORS.
- **Persistence**: PostgreSQL 17 with pgvector, SQLAlchemy 2 with `asyncpg`, Alembic migrations from
  the first commit, UUIDv7 identifiers, and the twelve structural tables later Gates record into.
- **Cache, object storage and durable workflows**: Redis, MinIO with an idempotent bucket bootstrap,
  and Temporal with the worker as a separate process running one real smoke workflow.
- **The web shell**: an Angular application that renders the live backend status and reads its
  backend address at run time, so one image runs against any backend.
- **The stack**: Docker Compose with real healthchecks, health-condition ordering, named volumes,
  an explicit network and every published port bound to loopback and taken from configuration.
- **Observability**: Prometheus scraping the API and the worker, Grafana with the datasource and the
  Foundation dashboard provisioned from files.
- **Backup and restore**, verified end to end with synthetic data in a disposable target.
- **One verification command** that reads the mandatory gate set from policy.
- **Four control-plane controls generalised** so a Gate other than SETUP-00 can be delivered, and
  **the repository secret scan narrowed** to what the repository carries.
- **The Gate's own adversarial battery**, and four new lessons with five guardrails.

## What was NOT completed

No Gate 1 work. `services/model-gateway/` holds a README declaring the reservation and nothing else,
and `.iacode/policies/canonical-requirements.json` declares no requirements for `GATE-1`; authoring
that specification is that Gate's first deliverable.

No model gateway, agent runtime, sandbox, retrieval, experience store, training or promotion. No
endpoint over the domain tables: they are a persistence contract, and an endpoint returning an empty
list would be a capability this Gate does not have.

No independent audit. `M1` covers Gates 0 to 3 and is audited after Gate 3.
`INTERNAL_GATE_PASS` is the project's own verdict and is not described as anything else.

No vector column, and no OpenTelemetry instrumentation. Both are recorded decisions with the Gate
that owns them named: `ADR-0013` and `ADR-0015`.

## Current repository state

Branch `main`. `STATE.json` records the exact commit and the canonical tag. The worktree is clean at
the sealed commit.

`infra/compose/.env` exists on the delivering machine with generated local credentials. It is
ignored by Git, it is not part of the change set, and the repository secret scan is scoped to what
Git carries — which is the narrowing this Gate made, with both paths executed by
`SecretScanScopeTests`.

## Files changed

See `FILES.json` and `DIFF-SUMMARY.md`. No sealed checkpoint was modified, no historical tag was
moved and no commit was rewritten.

## Important decisions

See `DECISIONS.md` and `docs/adr/ADR-0012` to `ADR-0015`. The load-bearing ones: the stack was
adopted as authorised and the choices inside it recorded; four control-plane controls were
generalised rather than worked around; the mirror audit's scope check now judges the Gate under
audit against a reservation registry; Temporal shares the PostgreSQL server in its own databases and
the resulting blast radius is declared and asserted; pgvector is created and unused; OpenTelemetry
is deferred to the Gate that has something to trace.

## Tests executed

Four suites, all green, every one of them executed rather than asserted:

- `python -m unittest discover -s tests` — the control plane.
- `python -m pytest tests` inside the API image — the backend, unit and integration, the integration
  half against the real PostgreSQL, Redis, MinIO and Temporal from the Compose stack.
- `python -m unittest discover -s infra/tests` — what the infrastructure declares, and our
  configuration of each service exercised live.
- `npm test` inside the frontend toolchain image, with the production build.

`COUNTS.json` carries the derived numbers, and `VERIFICATION-REPORT.json` records every stage of the
verification run with its exit code and duration.

Also executed: the smoke check including a real Temporal workflow, a verified backup-and-restore
cycle, a dependency vulnerability scan over both ecosystems, and the restart, dependency-failure and
fresh-installation scenarios.

## Known failures

None outstanding.

Recorded failures remain in `COMMANDS.jsonl` deliberately. The first verification run exited
non-zero: the control-plane suite was red because two fixtures copied the mandatory gate policy
without the commands it names, and because the repository secret scan flagged this Gate's own test
fixtures and the real `.env`. Both were repaired at the cause — see `DECISIONS.md` — and a failed
attempt keeps its record so corrections stay visible.

## Known risks

See `RISKS.md`. Especially: Docker is now a hard requirement of the repository; the mandatory gate
set takes minutes; stopping PostgreSQL stops Temporal, which is declared and asserted rather than
discovered; the frontend suite is outside the derived `TESTS` denominator with a recorded reason;
and four control-plane controls were generalised by this Gate, of which the mirror's scope check is
the one to watch.

## Do not repeat

- Do not write a control that names the current Gate's content by literal. It will block or blind
  the next Gate, and which one is luck.
- Do not scan the working tree when the policy is about the repository. The first refuses correct
  states, and a control that refuses a correct state gets switched off.
- Do not write a credential-shaped literal into a test fixture. It is indistinguishable from a leak
  to a text scanner, and suppressing the scan for that file is how a real leak gets through.
- Do not add a configuration key before its reader. The application's own test fails on it, and the
  same class already cost this project a guardrail failure.
- Do not re-derive what the framework already computes. The reimplementation agrees until the
  framework changes shape, and then it is silently wrong.
- Do not make a mandatory gate depend on the whole stack being up. It gets skipped rather than
  fixed.

## Required next action

Request explicit authorization to open `GATE 1 — MODEL GATEWAY`, as described in `NEXT.md`. Gate 1
is authorised by its predecessor closing but is not started, and it may not be started without its
own pre-Gate checkpoint.

## Exact continuation sequence

1. Read `START-HERE.md`, `docs/DEVELOPMENT-CONTRACT.md`, `docs/MASTER-PLAN.md`,
   `docs/QUALITY-GATES.md`, `docs/CHECKPOINT-PROTOCOL.md`, `docs/HANDOFF-PROTOCOL.md`,
   `docs/DEFINITION-OF-DONE.md`, `docs/ENGINEERING-MEMORY.md`, `docs/MILESTONE-VALIDATION.md`,
   `docs/checkpoints/LATEST.md` and this complete checkpoint.
2. Read `docs/ARCHITECTURE.md` and `docs/runbooks/FOUNDATION.md`.
3. Run the validation commands below and compare the observed Git state with `STATE.json`.
4. Start the stack and run the smoke check, so the Foundation is confirmed before it is changed.
5. Follow `NEXT.md`.

## Validation commands

- `git status --short --branch`
- `git branch --show-current`
- `git rev-parse HEAD`
- `git rev-parse refs/tags/iacode-checkpoints/GATE-0-CP-0001`
- `python scripts/development-ledger/validate_checkpoint.py`
- `python scripts/development-ledger/validate_lessons.py`
- `python scripts/development-ledger/verify_integrity.py`
- `python scripts/development-ledger/derive_counts.py`
- `python scripts/development-ledger/check_completeness.py`
- `python scripts/development-ledger/derive_requirements.py`
- `python scripts/development-ledger/milestone_status.py --milestone M0` — expect `MILESTONE_PASSED`
- `python -m unittest discover -s tests`
- `python scripts/iacode/bootstrap_env.py`
- `python scripts/iacode/stack.py up`
- `python scripts/iacode/smoke.py`
- `python scripts/iacode/verify.py --fast`
- `python scripts/development-ledger/gate0_red_team.py`
- `python scripts/development-ledger/m0_mirror_audit.py`

The last six need Docker. That is a requirement of this repository from this Gate onwards, stated in
`docs/VERSIONS.md`.

## Stop conditions

Stop on unexpected Git divergence, on a failing validation, on any need to modify a sealed
checkpoint or move a historical tag, on secret exposure, and on any attempt to begin Gate 1 without
explicit authorization and a new pre-Gate checkpoint.
