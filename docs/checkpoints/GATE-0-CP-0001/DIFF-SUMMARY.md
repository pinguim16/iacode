# Diff Summary — GATE-0-CP-0001

What changed, grouped by why. The authoritative, hash-bound list is `FILES.json`.

## New: the Foundation runtime

Everything under `apps/`, `services/`, `packages/` and `infra/` is new. The repository had no
runtime before this Gate.

| Area | What it is |
|---|---|
| `apps/api/` | the FastAPI application: configuration, lifecycle, routes, persistence, clients, migrations and its own suite |
| `apps/web/` | the Angular shell, built and tested in a container, with the backend address read at run time |
| `services/orchestrator/` | the Temporal worker, the smoke workflow and the worker healthcheck |
| `packages/common/` | UUIDv7 and credential redaction, standard library only |
| `packages/contracts/` | the response shapes that cross a process boundary |
| `packages/telemetry/` | the logging contract and the ambient correlation context |
| `infra/compose/` | the stack: nine long-running services and two one-shot jobs |
| `infra/prometheus/`, `infra/grafana/`, `infra/postgres/`, `infra/minio/`, `infra/temporal/` | the configuration each service is provisioned from |
| `infra/tests/` | what the infrastructure declares, and our configuration of each service exercised live |

## New: the operational tooling

`scripts/iacode/` — everything an operator or a contributor runs. Python driving Docker, so it works
on Windows and on POSIX.

`bootstrap_env.py`, `stack.py`, `migrate.py`, `smoke.py`, `backup.py`, `restore.py`,
`backup_restore_check.py`, `dependency_scan.py`, `lock_dependencies.py`, `verify.py`, the four
mandatory-gate entry points under `gates/`, and the three scenarios under `scenarios/`. `verify.ps1`
at the root is a wrapper with no logic of its own.

## New: the Gate's specification and its policies

| File | Why |
|---|---|
| `docs/GATE-0-CHECKLIST.md` | the canonical specification the requirement set is derived from |
| `.iacode/policies/gate-scope.json` + schema | which path is reserved for which later Gate |
| `.iacode/policies/test-suites.json` + schema | which suites exist, which are counted, and why one is not |
| `ruff.toml` | one static-analysis configuration, with every exception justified in place |

## Changed: four control-plane controls that were coupled to SETUP-00

Each blocked Gate 0 outright. `DECISIONS.md` records why each change generalises rather than
weakens.

| File | Change |
|---|---|
| `scripts/development-ledger/policies.py` | the specification path comes from the registry; the test-suite registry and the scope reservations are read here |
| `scripts/development-ledger/derive_requirements.py` | the derivation names the Gate's own specification |
| `scripts/development-ledger/ledger_common.py` | the assurance scope covers the runtime; the placeholder convention matches the committed example |
| `scripts/development-ledger/derive_counts.py` | the TESTS denominator sums every counted suite |
| `scripts/development-ledger/delivery_assurance.py` | evidence resolution covers every counted Python suite |
| `scripts/development-ledger/m0_mirror_audit.py` | `MIR-001`, `MIR-015` and `MIR-018` judge the Gate under audit |
| `scripts/development-ledger/validate_checkpoint.py` | the secret scan covers what the repository carries rather than every file on disk |
| `scripts/development-ledger/promotion_fixture.py` | a fixture's policies are restricted to the content the fixture has |
| `.iacode/policies/quality-gates.json` | four executable gates added to the mandatory set |
| `.iacode/schemas/closure-requirements.schema.json` | `GATE_SPECIFICATION` added to the source vocabulary |

## New: the Gate's own adversarial battery

`scripts/development-ledger/gate0_red_team.py` and `gate0_runtime_attacks.py`. Split because the
attacks against the application need FastAPI and pydantic, which the host deliberately does not
have; they run inside the API image and their verdicts are merged.

## Changed: the engineering memory

Three lessons added and one recurrence recorded against a `GUARDED` lesson, with four guardrails.
See `.iacode/memory/retrospectives/GATE-0-CP-0001.md`.

## New and changed: documentation

| File | Change |
|---|---|
| `README.md`, `START-HERE.md`, `docs/ARCHITECTURE.md` | describe what now exists and what deliberately does not |
| `docs/DEVELOPMENT.md` | new: the contributor's path end to end |
| `docs/runbooks/FOUNDATION.md`, `docs/runbooks/BACKUP-RESTORE.md` | new: the operator's procedures |
| `docs/VERSIONS.md` | new: every pinned version in one place |
| `docs/adr/ADR-0012` … `ADR-0015` | the stack, pgvector, the shared database, and the OpenTelemetry deferral |
| `docs/MASTER-PLAN.md` | the Gate 0 row points at its specification |

## New: the suite this Gate added to the control plane

`tests/test_gate0_foundation.py` — the Gate's specification, the derivation, the assurance scope,
the suite registry, the monorepo structure, the scope control and the secret-scan scoping.

## Not changed

No sealed checkpoint, no historical tag, no commit. Nothing under `docs/checkpoints/` other than
this checkpoint's own directory and `LATEST.md`.
