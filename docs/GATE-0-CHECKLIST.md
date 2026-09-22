# GATE 0 — Foundation Checklist

This is the canonical specification of `GATE 0 — FOUNDATION`. It is the source the expected
requirement set is derived from, re-parsed at every run by `policies.canonical_requirements` and
mirrored, row for row, by `.iacode/policies/canonical-requirements.json`. A delivery for this Gate
cannot declare a smaller set, and a row cannot be dropped by editing the mirror.

The objective of the Gate is a **local, reproducible runtime foundation**: an application skeleton,
a backend API, a web frontend, persistence, cache, object storage, a durable workflow engine,
observability, containers, configuration and secret handling, backup and restore, tests and the
operational documentation that lets a new machine reproduce all of it from this repository alone.

The Gate deliberately does **not** implement the Model Gateway, the Agent Runtime, the sandbox,
retrieval, training or model promotion. Those belong to later Gates, and a structural directory that
exists for them declares itself reserved rather than pretending to work.

`GATE 0` belongs to milestone `M1` and does not close it, so it ends at `INTERNAL_GATE_PASS`.

## 1. Gate specification and requirement derivation

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 1.1 | A canonical, machine-readable requirement specification exists for this Gate and the registry mirrors it row for row. | `docs/GATE-0-CHECKLIST.md`, `.iacode/policies/canonical-requirements.json` | `policies.canonical_requirements` parses and mirrors the document; `Gate0CanonicalSpecificationTests`. |
| 1.2 | The derived expected set names the specification of the Gate it describes instead of a fixed document. | `scripts/development-ledger/policies.py`, `scripts/development-ledger/derive_requirements.py` | `test_expected_set_names_the_gate_specification`. |
| 1.3 | The delivery-assurance scope covers the runtime source this Gate introduces, so a gate result becomes stale when the product changes. | `scripts/development-ledger/ledger_common.py` | `test_assurance_scope_covers_the_runtime_source`. |
| 1.4 | The closed mandatory gate registry carries every executable gate this Gate introduces. | `.iacode/policies/quality-gates.json` | A Green Keeper cycle measured against the registry's mandatory set. |
| 1.5 | Every test suite this Gate introduces is declared canonically and is counted by the count derivation and resolvable as evidence. | `.iacode/policies/test-suites.json` | `COUNTS.json` `TESTS`; `test_declared_suites_are_discovered`. |
| 1.6 | The internal mirror audit judges the Gate it runs in rather than a Gate named in its own source. | `scripts/development-ledger/m0_mirror_audit.py` | `M1-INTERNAL-MIRROR.json` with `result` `PASS`. |
| 1.7 | The internal Red Team battery of this Gate is executable, scoped to the Foundation, and records a null-mutation control. | `scripts/development-ledger/gate0_red_team.py` | `M1-INTERNAL-RED-TEAM.json` with a `VALID` `baselineControl`. |

## 2. Monorepo structure

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 2.1 | The repository carries the planned application, service, package and infrastructure directories. | `apps/`, `services/`, `packages/`, `infra/`, `agents/`, `training/`, `evaluation/`, `datasets/` | Directories present; `test_monorepo_structure_exists`. |
| 2.2 | A directory reserved for a later Gate says so and contains no implementation. | `services/*/README.md`, `training/README.md` | `test_reserved_directories_declare_themselves`. |
| 2.3 | No later-Gate capability is implemented, simulated or faked in this Gate. | the whole tree | `test_no_future_gate_capability_is_implemented`; mirror scope check. |

## 3. Backend application

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 3.1 | The backend is a real FastAPI application that starts reliably and fails loudly when it cannot. | `apps/api/src/iacode_api/main.py` | `test_application_starts`; container healthcheck. |
| 3.2 | Shutdown is graceful and releases every client the application opened. | `apps/api/src/iacode_api/lifespan.py` | `test_shutdown_releases_every_client`. |
| 3.3 | Dependency lifecycle is explicit and held on the application, not in ambient mutable globals. | `apps/api/src/iacode_api/dependencies.py` | `test_dependencies_are_held_on_application_state`. |
| 3.4 | `GET /health` reports process liveness and does not depend on external dependencies to answer. | `apps/api/src/iacode_api/routes/health.py` | `test_health_is_up_while_dependencies_are_down`. |
| 3.5 | `GET /ready` probes PostgreSQL, Redis, MinIO and Temporal and refuses readiness when a mandatory dependency is unavailable. | `apps/api/src/iacode_api/routes/health.py`, `apps/api/src/iacode_api/readiness.py` | `test_ready_reports_each_dependency`; dependency-failure scenario. |
| 3.6 | `GET /version` reports the application version and build identity and exposes no secret. | `apps/api/src/iacode_api/routes/version.py` | `test_version_exposes_no_secret`. |
| 3.7 | The application exposes a Prometheus metrics endpoint with request, latency, status and dependency metrics. | `apps/api/src/iacode_api/observability/metrics.py` | `test_metrics_endpoint_exposes_request_metrics`. |
| 3.8 | OpenAPI documentation describes the Foundation endpoints and exposes no internal-only route. | `apps/api/src/iacode_api/main.py` | `test_openapi_documents_the_foundation_endpoints`. |
| 3.9 | CORS is configured explicitly from configuration, without a permissive wildcard, and allows the local frontend. | `apps/api/src/iacode_api/config.py`, `apps/api/src/iacode_api/main.py` | `test_cors_is_explicit_and_not_wildcard`. |

## 4. Configuration and secrets

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 4.1 | Configuration is typed, validated at load time and rejects an invalid or missing mandatory value. | `apps/api/src/iacode_api/config.py` | `test_configuration_rejects_invalid_values`. |
| 4.2 | Safe defaults, development configuration and test configuration are separated rather than conflated. | `apps/api/src/iacode_api/config.py`, `infra/compose/.env.example` | `test_configuration_layers_are_separate`. |
| 4.3 | A committed example environment file documents every key and carries no real secret, and the real file is ignored by Git. | `infra/compose/.env.example`, `.gitignore` | `test_env_example_documents_every_key_without_secrets`. |
| 4.4 | Secret values are redacted wherever configuration, errors or logs could expose them. | `packages/common/src/iacode_common/redaction.py` | `test_secrets_are_redacted_in_logs_and_errors`. |
| 4.5 | No secret is baked into an image, a compose file, a Dockerfile or a committed configuration file. | `infra/`, `apps/*/Dockerfile` | `test_no_secret_is_committed_in_infrastructure`; repository secret scan. |

## 5. Persistence

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 5.1 | PostgreSQL runs locally from the compose stack at a pinned version with a persistent named volume. | `infra/compose/docker-compose.yml` | Stack up; `test_postgres_is_pinned_and_persistent`. |
| 5.2 | The persistence layer is real, asynchronous and pooled, built on SQLAlchemy 2. | `apps/api/src/iacode_api/db/engine.py` | `test_database_round_trip`. |
| 5.3 | Alembic migrations run from zero against an empty database and produce the declared schema. | `apps/api/migrations/` | Fresh-install scenario; `test_migrations_run_from_zero`. |
| 5.4 | Starting against an already-migrated database neither fails nor recreates the schema. | `apps/api/migrations/env.py`, `scripts/iacode/migrate.py` | Restart scenario; `test_migrations_are_idempotent_on_restart`. |
| 5.5 | A failed migration never produces a healthy readiness or a silent partial start. | `apps/api/src/iacode_api/readiness.py` | `test_failed_migration_does_not_report_ready`; Red Team scenario. |
| 5.6 | The structural domain tables the later Gates build on exist, with their relationships and constraints. | `apps/api/src/iacode_api/db/models.py` | `test_structural_tables_exist`; `test_relationships_cascade_deliberately`. |
| 5.7 | Identifiers use one consistent strategy, UUIDv7, implemented and tested rather than assumed. | `packages/common/src/iacode_common/identifiers.py` | `test_uuid7_is_ordered_and_well_formed`. |
| 5.8 | The common column convention is defined once and applied where it makes sense, not forced everywhere. | `apps/api/src/iacode_api/db/base.py` | `test_common_columns_follow_the_convention`. |
| 5.9 | The pgvector position is decided, recorded, and — where the extension is enabled — migrated and tested. | `apps/api/migrations/`, `docs/adr/` | `test_pgvector_extension_is_available`; `ADR-0013`. |

## 6. Cache

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 6.1 | Redis runs locally from the compose stack at a pinned version. | `infra/compose/docker-compose.yml` | Stack up; `test_redis_is_pinned`. |
| 6.2 | The backend holds a real Redis client whose availability the readiness probe verifies. | `apps/api/src/iacode_api/cache/client.py` | `test_ready_reports_each_dependency`. |
| 6.3 | An integration test exercises a real Redis round trip against the running service. | `apps/api/tests/integration/test_redis.py` | `test_redis_round_trip`. |

## 7. Object storage

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 7.1 | MinIO runs locally from the compose stack at a pinned version with a persistent named volume. | `infra/compose/docker-compose.yml` | Stack up; `test_minio_is_pinned_and_persistent`. |
| 7.2 | The buckets the later Gates need are created by an idempotent bootstrap that is safe to re-run. | `infra/compose/docker-compose.yml`, `scripts/iacode/bootstrap_storage.py` | `test_bucket_bootstrap_is_idempotent`. |
| 7.3 | The readiness probe verifies real object-storage connectivity rather than a reachable port. | `apps/api/src/iacode_api/storage/client.py` | `test_ready_reports_each_dependency`. |
| 7.4 | An integration test writes, reads and deletes a real object. | `apps/api/tests/integration/test_object_storage.py` | `test_object_storage_round_trip`. |

## 8. Durable workflows

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 8.1 | Temporal runs locally from the compose stack at a pinned version with its persistent state. | `infra/compose/docker-compose.yml` | Stack up; `test_temporal_is_pinned`. |
| 8.2 | An IACode worker connects to Temporal and polls its task queue as a first-class service. | `services/orchestrator/src/iacode_orchestrator/worker.py` | Worker container healthy; `test_worker_registers_the_smoke_workflow`. |
| 8.3 | The readiness probe verifies real Temporal connectivity. | `apps/api/src/iacode_api/workflows/client.py` | `test_ready_reports_each_dependency`. |
| 8.4 | A minimal real workflow and activity execute end to end through the worker and return an observable result. | `services/orchestrator/src/iacode_orchestrator/workflows/smoke.py` | `test_smoke_workflow_executes_end_to_end`. |
| 8.5 | No agent workflow, tool call or orchestration of a later Gate is implemented here. | `services/orchestrator/` | `test_no_future_gate_capability_is_implemented`. |

## 9. Frontend

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 9.1 | A real Angular application exists and builds reproducibly with pinned dependencies. | `apps/web/` | Production build; `test_web_dependencies_are_locked`. |
| 9.2 | The Foundation page identifies IACode and renders the live backend health, readiness and version. | `apps/web/src/app/` | Frontend unit tests; browser check recorded in the runbook. |
| 9.3 | The API base address is centralized in configuration, carries no secret and is not hardcoded across the code. | `apps/web/src/environments/` | `test_api_base_is_centralised`. |
| 9.4 | Frontend unit tests run headless and are part of the verification command. | `apps/web/`, `scripts/iacode/verify.py` | Frontend test run. |

## 10. Containers and Compose

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 10.1 | Every image builds from a pinned base, runs as a non-root user where practical, carries no secret and excludes build waste. | `apps/api/Dockerfile`, `apps/web/Dockerfile`, `services/orchestrator/Dockerfile` | Image build; `test_dockerfiles_pin_and_drop_root`. |
| 10.2 | The compose stack declares every Foundation service and nothing that the Foundation does not need. | `infra/compose/docker-compose.yml` | `docker compose config`; `test_compose_declares_the_foundation_services`. |
| 10.3 | Every service that can report health has a real healthcheck, and start-up ordering uses those conditions instead of fixed sleeps. | `infra/compose/docker-compose.yml` | `test_compose_uses_health_conditions_not_sleeps`. |
| 10.4 | Restart behaviour is declared, and the stack recovers its state after a restart. | `infra/compose/docker-compose.yml` | Restart scenario. |
| 10.5 | Durable state lives in named volumes that are documented, not in the container filesystem. | `infra/compose/docker-compose.yml`, `docs/runbooks/FOUNDATION.md` | `test_durable_state_uses_named_volumes`. |
| 10.6 | The stack uses an explicit network and publishes only the ports local development needs, from configuration. | `infra/compose/docker-compose.yml`, `infra/compose/.env.example` | `test_published_ports_are_configurable_and_minimal`. |

## 11. Observability

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 11.1 | The backend and the worker emit structured logs carrying the contract fields, absent rather than invented when there is no context. | `packages/telemetry/src/iacode_telemetry/logging.py` | `test_structured_log_contract`. |
| 11.2 | Every HTTP request carries a correlation identifier that is accepted or generated, propagated, returned and logged. | `apps/api/src/iacode_api/middleware/correlation.py` | `test_correlation_identifier_is_propagated`. |
| 11.3 | The API error contract is explicit, extensible and never returns a traceback or internal detail to the client while keeping it in the logs. | `apps/api/src/iacode_api/errors.py` | `test_internal_error_leaks_nothing`. |
| 11.4 | Prometheus is provisioned and scrapes the API and the worker. | `infra/prometheus/prometheus.yml` | Prometheus targets up; `test_prometheus_scrapes_the_foundation_targets`. |
| 11.5 | Grafana starts with the Prometheus datasource and a Foundation dashboard provisioned automatically. | `infra/grafana/provisioning/` | Grafana health; `test_grafana_provisioning_is_declared`. |
| 11.6 | The OpenTelemetry position for the Foundation is decided and recorded rather than left implicit. | `docs/adr/`, `docs/ARCHITECTURE.md` | `ADR-0015`. |

## 12. Backup and restore

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 12.1 | A reproducible backup produces a PostgreSQL dump and the object-storage contents, with a correct exit code and a log, and fails loudly on partial failure. | `scripts/iacode/backup.py` | Backup run; `BackupFailureTests`. |
| 12.2 | The backup never writes a credential into its artifacts or its log. | `scripts/iacode/backup.py` | `test_backup_artifacts_carry_no_secret`; `BackupSecrecyTests`. |
| 12.3 | A restore reconstructs the database and the object storage from a backup produced by this tooling. | `scripts/iacode/restore.py` | Restore run; `RestoreRefusalTests`. |
| 12.4 | Backup and restore are verified end to end with synthetic data in a disposable environment, and the restored data is checked rather than assumed. | `scripts/iacode/backup_restore_check.py` | Verified backup-restore cycle. |
| 12.5 | Backup retention for the Foundation is either implemented simply or documented as out of scope, with no silent gap. | `scripts/iacode/backup.py`, `docs/runbooks/BACKUP-RESTORE.md` | `RetentionTests`; runbook and implementation agree. |

## 13. Verification, tests and scenarios

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 13.1 | One documented command runs the whole Gate verification and works on the primary Windows environment as well as on POSIX. | `scripts/iacode/verify.py`, `verify.ps1` | Verification run. |
| 13.2 | The backend suite covers health, readiness, version, configuration, redaction, error handling, correlation, database, cache, object storage, workflows and migrations. | `apps/api/tests/` | Backend test run. |
| 13.3 | The frontend suite covers bootstrap, the status rendering and the API configuration, and the production build succeeds. | `apps/web/src/` | Frontend test and build run. |
| 13.4 | Infrastructure smoke validation proves that our own configuration of each service is operational. | `infra/tests/` | Infrastructure smoke run. |
| 13.5 | A fresh installation with no previous volume reaches a ready stack, a migrated database, a reachable frontend and a green smoke check. | `scripts/iacode/scenarios/fresh_install.py` | Fresh-install scenario. |
| 13.6 | A restart of the running stack returns every service to ready with its data intact. | `scripts/iacode/scenarios/restart.py` | Restart scenario. |
| 13.7 | With a mandatory dependency stopped, liveness may stay up while readiness fails correctly, and readiness recovers when the dependency returns. | `scripts/iacode/scenarios/dependency_failure.py` | Dependency-failure scenario. |
| 13.8 | Lint and static analysis run over the backend, the worker and the frontend and are green. | `apps/api/pyproject.toml`, `apps/web/eslint.config.js` | Lint run. |
| 13.9 | A dependency vulnerability scan is executed, or its absence is justified, and relevant Critical and High findings block the Gate. | `scripts/iacode/dependency_scan.py` | Scan run over both ecosystems, or a recorded justification. |

## 14. Documentation and decisions

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 14.1 | The repository entry documentation describes what exists after this Gate and how to run it. | `README.md` | File content consistent with the runtime. |
| 14.2 | The architecture document describes the Foundation runtime, its boundaries and what is deliberately absent. | `docs/ARCHITECTURE.md` | File content. |
| 14.3 | A development guide explains the local workflow end to end for a new machine. | `docs/DEVELOPMENT.md` | File content. |
| 14.4 | An operational runbook documents start, stop, rebuild, reset, migrate, health, readiness, Grafana and the smoke checks. | `docs/runbooks/FOUNDATION.md` | Procedure reproduced during the delivery. |
| 14.5 | A backup and restore runbook documents the full procedure and its verification. | `docs/runbooks/BACKUP-RESTORE.md` | Procedure reproduced during the delivery. |
| 14.6 | The pinned versions of every runtime, service and principal library are recorded in one place. | `docs/VERSIONS.md` | Recorded versions match the lock files and the compose file. |
| 14.7 | Every structural decision of this Gate that is not already recorded becomes an ADR, and no ADR duplicates an existing decision. | `docs/adr/` | `ADR-0012` to `ADR-0015`. |

## 15. Gate consistency

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 15.1 | The entry contract and the plan describe the current Gate and its status truthfully. | `START-HERE.md`, `docs/MASTER-PLAN.md` | File content consistent with `docs/checkpoints/LATEST.md`. |
| 15.2 | The Gate produces a retrospective from the canonical template. | `.iacode/memory/retrospectives/` | Retrospective file. |
