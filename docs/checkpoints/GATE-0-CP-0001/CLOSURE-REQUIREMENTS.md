# Closure Requirements - GATE-0-CP-0001

Derived from the canonical sources listed below, before implementation. The expected set
is recomputed by `policies.expected_requirement_refs` and compared exactly with the
declared set, so a requirement cannot be dropped and the denominator cannot be reduced.

## Sources

- SOURCE A: docs/GATE-0-CHECKLIST.md, the canonical GATE-0 specification
- SOURCE B: docs/MILESTONE-VALIDATION.md, the milestone requirements of the audit
- SOURCE C: LESSON-PREFLIGHT.json, the lessons the engineering memory imposes

## Requirements

| ID | Source | Anchor | Mandatory | Implementation | Final | Description |
|---|---|---|---|---|---|---|
| `REQ-0001` | GATE_SPECIFICATION | `canonical:GATE-0#1.1` | yes | `COMPLETE` | `COMPLETE` | A canonical, machine-readable requirement specification exists for this Gate and the registry mirrors it row for row. |
| `REQ-0002` | GATE_SPECIFICATION | `canonical:GATE-0#1.2` | yes | `COMPLETE` | `COMPLETE` | The derived expected set names the specification of the Gate it describes instead of a fixed document. |
| `REQ-0003` | GATE_SPECIFICATION | `canonical:GATE-0#1.3` | yes | `COMPLETE` | `COMPLETE` | The delivery-assurance scope covers the runtime source this Gate introduces, so a gate result becomes stale when the product changes. |
| `REQ-0004` | GATE_SPECIFICATION | `canonical:GATE-0#1.4` | yes | `COMPLETE` | `COMPLETE` | The closed mandatory gate registry carries every executable gate this Gate introduces. |
| `REQ-0005` | GATE_SPECIFICATION | `canonical:GATE-0#1.5` | yes | `COMPLETE` | `COMPLETE` | Every test suite this Gate introduces is declared canonically and is counted by the count derivation and resolvable as evidence. |
| `REQ-0006` | GATE_SPECIFICATION | `canonical:GATE-0#1.6` | yes | `COMPLETE` | `COMPLETE` | The internal mirror audit judges the Gate it runs in rather than a Gate named in its own source. |
| `REQ-0007` | GATE_SPECIFICATION | `canonical:GATE-0#1.7` | yes | `COMPLETE` | `COMPLETE` | The internal Red Team battery of this Gate is executable, scoped to the Foundation, and records a null-mutation control. |
| `REQ-0008` | GATE_SPECIFICATION | `canonical:GATE-0#2.1` | yes | `COMPLETE` | `COMPLETE` | The repository carries the planned application, service, package and infrastructure directories. |
| `REQ-0009` | GATE_SPECIFICATION | `canonical:GATE-0#2.2` | yes | `COMPLETE` | `COMPLETE` | A directory reserved for a later Gate says so and contains no implementation. |
| `REQ-0010` | GATE_SPECIFICATION | `canonical:GATE-0#2.3` | yes | `COMPLETE` | `COMPLETE` | No later-Gate capability is implemented, simulated or faked in this Gate. |
| `REQ-0011` | GATE_SPECIFICATION | `canonical:GATE-0#3.1` | yes | `COMPLETE` | `COMPLETE` | The backend is a real FastAPI application that starts reliably and fails loudly when it cannot. |
| `REQ-0012` | GATE_SPECIFICATION | `canonical:GATE-0#3.2` | yes | `COMPLETE` | `COMPLETE` | Shutdown is graceful and releases every client the application opened. |
| `REQ-0013` | GATE_SPECIFICATION | `canonical:GATE-0#3.3` | yes | `COMPLETE` | `COMPLETE` | Dependency lifecycle is explicit and held on the application, not in ambient mutable globals. |
| `REQ-0014` | GATE_SPECIFICATION | `canonical:GATE-0#3.4` | yes | `COMPLETE` | `COMPLETE` | `GET /health` reports process liveness and does not depend on external dependencies to answer. |
| `REQ-0015` | GATE_SPECIFICATION | `canonical:GATE-0#3.5` | yes | `COMPLETE` | `COMPLETE` | `GET /ready` probes PostgreSQL, Redis, MinIO and Temporal and refuses readiness when a mandatory dependency is unavailable. |
| `REQ-0016` | GATE_SPECIFICATION | `canonical:GATE-0#3.6` | yes | `COMPLETE` | `COMPLETE` | `GET /version` reports the application version and build identity and exposes no secret. |
| `REQ-0017` | GATE_SPECIFICATION | `canonical:GATE-0#3.7` | yes | `COMPLETE` | `COMPLETE` | The application exposes a Prometheus metrics endpoint with request, latency, status and dependency metrics. |
| `REQ-0018` | GATE_SPECIFICATION | `canonical:GATE-0#3.8` | yes | `COMPLETE` | `COMPLETE` | OpenAPI documentation describes the Foundation endpoints and exposes no internal-only route. |
| `REQ-0019` | GATE_SPECIFICATION | `canonical:GATE-0#3.9` | yes | `COMPLETE` | `COMPLETE` | CORS is configured explicitly from configuration, without a permissive wildcard, and allows the local frontend. |
| `REQ-0020` | GATE_SPECIFICATION | `canonical:GATE-0#4.1` | yes | `COMPLETE` | `COMPLETE` | Configuration is typed, validated at load time and rejects an invalid or missing mandatory value. |
| `REQ-0021` | GATE_SPECIFICATION | `canonical:GATE-0#4.2` | yes | `COMPLETE` | `COMPLETE` | Safe defaults, development configuration and test configuration are separated rather than conflated. |
| `REQ-0022` | GATE_SPECIFICATION | `canonical:GATE-0#4.3` | yes | `COMPLETE` | `COMPLETE` | A committed example environment file documents every key and carries no real secret, and the real file is ignored by Git. |
| `REQ-0023` | GATE_SPECIFICATION | `canonical:GATE-0#4.4` | yes | `COMPLETE` | `COMPLETE` | Secret values are redacted wherever configuration, errors or logs could expose them. |
| `REQ-0024` | GATE_SPECIFICATION | `canonical:GATE-0#4.5` | yes | `COMPLETE` | `COMPLETE` | No secret is baked into an image, a compose file, a Dockerfile or a committed configuration file. |
| `REQ-0025` | GATE_SPECIFICATION | `canonical:GATE-0#5.1` | yes | `COMPLETE` | `COMPLETE` | PostgreSQL runs locally from the compose stack at a pinned version with a persistent named volume. |
| `REQ-0026` | GATE_SPECIFICATION | `canonical:GATE-0#5.2` | yes | `COMPLETE` | `COMPLETE` | The persistence layer is real, asynchronous and pooled, built on SQLAlchemy 2. |
| `REQ-0027` | GATE_SPECIFICATION | `canonical:GATE-0#5.3` | yes | `COMPLETE` | `COMPLETE` | Alembic migrations run from zero against an empty database and produce the declared schema. |
| `REQ-0028` | GATE_SPECIFICATION | `canonical:GATE-0#5.4` | yes | `COMPLETE` | `COMPLETE` | Starting against an already-migrated database neither fails nor recreates the schema. |
| `REQ-0029` | GATE_SPECIFICATION | `canonical:GATE-0#5.5` | yes | `COMPLETE` | `COMPLETE` | A failed migration never produces a healthy readiness or a silent partial start. |
| `REQ-0030` | GATE_SPECIFICATION | `canonical:GATE-0#5.6` | yes | `COMPLETE` | `COMPLETE` | The structural domain tables the later Gates build on exist, with their relationships and constraints. |
| `REQ-0031` | GATE_SPECIFICATION | `canonical:GATE-0#5.7` | yes | `COMPLETE` | `COMPLETE` | Identifiers use one consistent strategy, UUIDv7, implemented and tested rather than assumed. |
| `REQ-0032` | GATE_SPECIFICATION | `canonical:GATE-0#5.8` | yes | `COMPLETE` | `COMPLETE` | The common column convention is defined once and applied where it makes sense, not forced everywhere. |
| `REQ-0033` | GATE_SPECIFICATION | `canonical:GATE-0#5.9` | yes | `COMPLETE` | `COMPLETE` | The pgvector position is decided, recorded, and — where the extension is enabled — migrated and tested. |
| `REQ-0034` | GATE_SPECIFICATION | `canonical:GATE-0#6.1` | yes | `COMPLETE` | `COMPLETE` | Redis runs locally from the compose stack at a pinned version. |
| `REQ-0035` | GATE_SPECIFICATION | `canonical:GATE-0#6.2` | yes | `COMPLETE` | `COMPLETE` | The backend holds a real Redis client whose availability the readiness probe verifies. |
| `REQ-0036` | GATE_SPECIFICATION | `canonical:GATE-0#6.3` | yes | `COMPLETE` | `COMPLETE` | An integration test exercises a real Redis round trip against the running service. |
| `REQ-0037` | GATE_SPECIFICATION | `canonical:GATE-0#7.1` | yes | `COMPLETE` | `COMPLETE` | MinIO runs locally from the compose stack at a pinned version with a persistent named volume. |
| `REQ-0038` | GATE_SPECIFICATION | `canonical:GATE-0#7.2` | yes | `COMPLETE` | `COMPLETE` | The buckets the later Gates need are created by an idempotent bootstrap that is safe to re-run. |
| `REQ-0039` | GATE_SPECIFICATION | `canonical:GATE-0#7.3` | yes | `COMPLETE` | `COMPLETE` | The readiness probe verifies real object-storage connectivity rather than a reachable port. |
| `REQ-0040` | GATE_SPECIFICATION | `canonical:GATE-0#7.4` | yes | `COMPLETE` | `COMPLETE` | An integration test writes, reads and deletes a real object. |
| `REQ-0041` | GATE_SPECIFICATION | `canonical:GATE-0#8.1` | yes | `COMPLETE` | `COMPLETE` | Temporal runs locally from the compose stack at a pinned version with its persistent state. |
| `REQ-0042` | GATE_SPECIFICATION | `canonical:GATE-0#8.2` | yes | `COMPLETE` | `COMPLETE` | An IACode worker connects to Temporal and polls its task queue as a first-class service. |
| `REQ-0043` | GATE_SPECIFICATION | `canonical:GATE-0#8.3` | yes | `COMPLETE` | `COMPLETE` | The readiness probe verifies real Temporal connectivity. |
| `REQ-0044` | GATE_SPECIFICATION | `canonical:GATE-0#8.4` | yes | `COMPLETE` | `COMPLETE` | A minimal real workflow and activity execute end to end through the worker and return an observable result. |
| `REQ-0045` | GATE_SPECIFICATION | `canonical:GATE-0#8.5` | yes | `COMPLETE` | `COMPLETE` | No agent workflow, tool call or orchestration of a later Gate is implemented here. |
| `REQ-0046` | GATE_SPECIFICATION | `canonical:GATE-0#9.1` | yes | `COMPLETE` | `COMPLETE` | A real Angular application exists and builds reproducibly with pinned dependencies. |
| `REQ-0047` | GATE_SPECIFICATION | `canonical:GATE-0#9.2` | yes | `COMPLETE` | `COMPLETE` | The Foundation page identifies IACode and renders the live backend health, readiness and version. |
| `REQ-0048` | GATE_SPECIFICATION | `canonical:GATE-0#9.3` | yes | `COMPLETE` | `COMPLETE` | The API base address is centralized in configuration, carries no secret and is not hardcoded across the code. |
| `REQ-0049` | GATE_SPECIFICATION | `canonical:GATE-0#9.4` | yes | `COMPLETE` | `COMPLETE` | Frontend unit tests run headless and are part of the verification command. |
| `REQ-0050` | GATE_SPECIFICATION | `canonical:GATE-0#10.1` | yes | `COMPLETE` | `COMPLETE` | Every image builds from a pinned base, runs as a non-root user where practical, carries no secret and excludes build waste. |
| `REQ-0051` | GATE_SPECIFICATION | `canonical:GATE-0#10.2` | yes | `COMPLETE` | `COMPLETE` | The compose stack declares every Foundation service and nothing that the Foundation does not need. |
| `REQ-0052` | GATE_SPECIFICATION | `canonical:GATE-0#10.3` | yes | `COMPLETE` | `COMPLETE` | Every service that can report health has a real healthcheck, and start-up ordering uses those conditions instead of fixed sleeps. |
| `REQ-0053` | GATE_SPECIFICATION | `canonical:GATE-0#10.4` | yes | `COMPLETE` | `COMPLETE` | Restart behaviour is declared, and the stack recovers its state after a restart. |
| `REQ-0054` | GATE_SPECIFICATION | `canonical:GATE-0#10.5` | yes | `COMPLETE` | `COMPLETE` | Durable state lives in named volumes that are documented, not in the container filesystem. |
| `REQ-0055` | GATE_SPECIFICATION | `canonical:GATE-0#10.6` | yes | `COMPLETE` | `COMPLETE` | The stack uses an explicit network and publishes only the ports local development needs, from configuration. |
| `REQ-0056` | GATE_SPECIFICATION | `canonical:GATE-0#11.1` | yes | `COMPLETE` | `COMPLETE` | The backend and the worker emit structured logs carrying the contract fields, absent rather than invented when there is no context. |
| `REQ-0057` | GATE_SPECIFICATION | `canonical:GATE-0#11.2` | yes | `COMPLETE` | `COMPLETE` | Every HTTP request carries a correlation identifier that is accepted or generated, propagated, returned and logged. |
| `REQ-0058` | GATE_SPECIFICATION | `canonical:GATE-0#11.3` | yes | `COMPLETE` | `COMPLETE` | The API error contract is explicit, extensible and never returns a traceback or internal detail to the client while keeping it in the logs. |
| `REQ-0059` | GATE_SPECIFICATION | `canonical:GATE-0#11.4` | yes | `COMPLETE` | `COMPLETE` | Prometheus is provisioned and scrapes the API and the worker. |
| `REQ-0060` | GATE_SPECIFICATION | `canonical:GATE-0#11.5` | yes | `COMPLETE` | `COMPLETE` | Grafana starts with the Prometheus datasource and a Foundation dashboard provisioned automatically. |
| `REQ-0061` | GATE_SPECIFICATION | `canonical:GATE-0#11.6` | yes | `COMPLETE` | `COMPLETE` | The OpenTelemetry position for the Foundation is decided and recorded rather than left implicit. |
| `REQ-0062` | GATE_SPECIFICATION | `canonical:GATE-0#12.1` | yes | `COMPLETE` | `COMPLETE` | A reproducible backup produces a PostgreSQL dump and the object-storage contents, with a correct exit code and a log, and fails loudly on partial failure. |
| `REQ-0063` | GATE_SPECIFICATION | `canonical:GATE-0#12.2` | yes | `COMPLETE` | `COMPLETE` | The backup never writes a credential into its artifacts or its log. |
| `REQ-0064` | GATE_SPECIFICATION | `canonical:GATE-0#12.3` | yes | `COMPLETE` | `COMPLETE` | A restore reconstructs the database and the object storage from a backup produced by this tooling. |
| `REQ-0065` | GATE_SPECIFICATION | `canonical:GATE-0#12.4` | yes | `COMPLETE` | `COMPLETE` | Backup and restore are verified end to end with synthetic data in a disposable environment, and the restored data is checked rather than assumed. |
| `REQ-0066` | GATE_SPECIFICATION | `canonical:GATE-0#12.5` | yes | `COMPLETE` | `COMPLETE` | Backup retention for the Foundation is either implemented simply or documented as out of scope, with no silent gap. |
| `REQ-0067` | GATE_SPECIFICATION | `canonical:GATE-0#13.1` | yes | `COMPLETE` | `COMPLETE` | One documented command runs the whole Gate verification and works on the primary Windows environment as well as on POSIX. |
| `REQ-0068` | GATE_SPECIFICATION | `canonical:GATE-0#13.2` | yes | `COMPLETE` | `COMPLETE` | The backend suite covers health, readiness, version, configuration, redaction, error handling, correlation, database, cache, object storage, workflows and migrations. |
| `REQ-0069` | GATE_SPECIFICATION | `canonical:GATE-0#13.3` | yes | `COMPLETE` | `COMPLETE` | The frontend suite covers bootstrap, the status rendering and the API configuration, and the production build succeeds. |
| `REQ-0070` | GATE_SPECIFICATION | `canonical:GATE-0#13.4` | yes | `COMPLETE` | `COMPLETE` | Infrastructure smoke validation proves that our own configuration of each service is operational. |
| `REQ-0071` | GATE_SPECIFICATION | `canonical:GATE-0#13.5` | yes | `COMPLETE` | `COMPLETE` | A fresh installation with no previous volume reaches a ready stack, a migrated database, a reachable frontend and a green smoke check. |
| `REQ-0072` | GATE_SPECIFICATION | `canonical:GATE-0#13.6` | yes | `COMPLETE` | `COMPLETE` | A restart of the running stack returns every service to ready with its data intact. |
| `REQ-0073` | GATE_SPECIFICATION | `canonical:GATE-0#13.7` | yes | `COMPLETE` | `COMPLETE` | With a mandatory dependency stopped, liveness may stay up while readiness fails correctly, and readiness recovers when the dependency returns. |
| `REQ-0074` | GATE_SPECIFICATION | `canonical:GATE-0#13.8` | yes | `COMPLETE` | `COMPLETE` | Lint and static analysis run over the backend, the worker and the frontend and are green. |
| `REQ-0075` | GATE_SPECIFICATION | `canonical:GATE-0#13.9` | yes | `COMPLETE` | `COMPLETE` | A dependency vulnerability scan is executed, or its absence is justified, and relevant Critical and High findings block the Gate. |
| `REQ-0076` | GATE_SPECIFICATION | `canonical:GATE-0#14.1` | yes | `COMPLETE` | `COMPLETE` | The repository entry documentation describes what exists after this Gate and how to run it. |
| `REQ-0077` | GATE_SPECIFICATION | `canonical:GATE-0#14.2` | yes | `COMPLETE` | `COMPLETE` | The architecture document describes the Foundation runtime, its boundaries and what is deliberately absent. |
| `REQ-0078` | GATE_SPECIFICATION | `canonical:GATE-0#14.3` | yes | `COMPLETE` | `COMPLETE` | A development guide explains the local workflow end to end for a new machine. |
| `REQ-0079` | GATE_SPECIFICATION | `canonical:GATE-0#14.4` | yes | `COMPLETE` | `COMPLETE` | An operational runbook documents start, stop, rebuild, reset, migrate, health, readiness, Grafana and the smoke checks. |
| `REQ-0080` | GATE_SPECIFICATION | `canonical:GATE-0#14.5` | yes | `COMPLETE` | `COMPLETE` | A backup and restore runbook documents the full procedure and its verification. |
| `REQ-0081` | GATE_SPECIFICATION | `canonical:GATE-0#14.6` | yes | `COMPLETE` | `COMPLETE` | The pinned versions of every runtime, service and principal library are recorded in one place. |
| `REQ-0082` | GATE_SPECIFICATION | `canonical:GATE-0#14.7` | yes | `COMPLETE` | `COMPLETE` | Every structural decision of this Gate that is not already recorded becomes an ADR, and no ADR duplicates an existing decision. |
| `REQ-0083` | GATE_SPECIFICATION | `canonical:GATE-0#15.1` | yes | `COMPLETE` | `COMPLETE` | The entry contract and the plan describe the current Gate and its status truthfully. |
| `REQ-0084` | GATE_SPECIFICATION | `canonical:GATE-0#15.2` | yes | `COMPLETE` | `COMPLETE` | The Gate produces a retrospective from the canonical template. |
| `LESSON-REQ-0001` | LESSON | `lesson:LSN-0001` | yes | `COMPLETE` | `COMPLETE` | Verify checkpoint validation must succeed from a detached checkout of the checkpoint tag |
| `LESSON-REQ-0002` | LESSON | `lesson:LSN-0002` | yes | `COMPLETE` | `COMPLETE` | Verify a file inventory must be recomputed from the repository, never trusted as an assertion |
| `LESSON-REQ-0003` | LESSON | `lesson:LSN-0003` | yes | `COMPLETE` | `COMPLETE` | Verify every operation attempt must be auditable, including a refusal decided before execution |
| `LESSON-REQ-0004` | LESSON | `lesson:LSN-0004` | yes | `COMPLETE` | `COMPLETE` | Verify a checkpoint may never claim readiness while it also claims to be blocked |
| `LESSON-REQ-0005` | LESSON | `lesson:LSN-0005` | yes | `COMPLETE` | `COMPLETE` | Verify a PASS requires evidence that can be executed or resolved, not a statement |
| `LESSON-REQ-0006` | LESSON | `lesson:LSN-0006` | yes | `COMPLETE` | `COMPLETE` | Verify the repository must be self-contained; a specification may not live outside it |
| `LESSON-REQ-0007` | LESSON | `lesson:LSN-0007` | yes | `COMPLETE` | `COMPLETE` | Verify independent validation cannot be declared by the run that did the work |
| `LESSON-REQ-0008` | LESSON | `lesson:LSN-0008` | yes | `COMPLETE` | `COMPLETE` | Verify requirement completeness must be total and evidence-backed before handoff |
| `LESSON-REQ-0009` | LESSON | `lesson:LSN-0009` | yes | `COMPLETE` | `COMPLETE` | Verify a red gate requires rework, never a waiver, and never a weakened check |
| `LESSON-REQ-0010` | LESSON | `lesson:LSN-0010` | yes | `COMPLETE` | `COMPLETE` | Verify a recorded command must carry runtime, working directory, commit and purpose to be replayable |
| `LESSON-REQ-0011` | LESSON | `lesson:LSN-0011` | yes | `COMPLETE` | `COMPLETE` | Verify a control over a checkpoint's own evidence must be scoped to the moment it matters |
| `LESSON-REQ-0012` | LESSON | `lesson:LSN-0012` | yes | `COMPLETE` | `COMPLETE` | Verify sealed checkpoints and their tags are immutable, and tooling must keep validating them |
| `LESSON-REQ-0013` | LESSON | `lesson:LSN-0013` | no | `COMPLETE` | `COMPLETE` | Verify an installed capability must be detected by resolved path, not by a bare command lookup |
| `LESSON-REQ-0014` | LESSON | `lesson:LSN-0014` | yes | `COMPLETE` | `COMPLETE` | Verify evidence must be recorded as it happens, not reconstructed at the end of a run |
| `LESSON-REQ-0015` | LESSON | `lesson:LSN-0015` | yes | `COMPLETE` | `COMPLETE` | Verify every positive terminal status needs one shared promotion invariant |
| `LESSON-REQ-0016` | LESSON | `lesson:LSN-0016` | yes | `COMPLETE` | `COMPLETE` | Verify a mandatory set must be closed by policy, never chosen by the caller |
| `LESSON-REQ-0017` | LESSON | `lesson:LSN-0017` | yes | `COMPLETE` | `COMPLETE` | Verify a completeness denominator must come from a source the delivery does not own |
| `LESSON-REQ-0018` | LESSON | `lesson:LSN-0018` | yes | `COMPLETE` | `COMPLETE` | Verify a structured reference must be resolved, not merely well typed |
| `LESSON-REQ-0019` | LESSON | `lesson:LSN-0019` | yes | `COMPLETE` | `COMPLETE` | Verify a derived artifact must carry a fingerprint of the inputs that produced it |
| `LESSON-REQ-0020` | LESSON | `lesson:LSN-0020` | yes | `COMPLETE` | `COMPLETE` | Verify evidence produced from a dirty tree needs immutable input identity |
| `LESSON-REQ-0021` | LESSON | `lesson:LSN-0021` | yes | `COMPLETE` | `COMPLETE` | Verify sealed history needs an anchor outside the content it describes |
| `LESSON-REQ-0022` | LESSON | `lesson:LSN-0022` | yes | `COMPLETE` | `COMPLETE` | Verify an authoritative count must be derived once, never maintained by hand twice |
| `LESSON-REQ-0023` | LESSON | `lesson:LSN-0023` | yes | `COMPLETE` | `COMPLETE` | Verify a lesson must cite a source that actually records the finding it claims |
| `LESSON-REQ-0024` | LESSON | `lesson:LSN-0024` | yes | `COMPLETE` | `COMPLETE` | Verify a control is finished only when its positive path has been executed, not only its refusals |
| `LESSON-REQ-0025` | LESSON | `lesson:LSN-0025` | yes | `COMPLETE` | `COMPLETE` | Verify a generic guardrail derives repository state instead of naming today's checkpoint |
| `LESSON-REQ-0026` | LESSON | `lesson:LSN-0026` | yes | `COMPLETE` | `COMPLETE` | Verify an adversarial battery without a null-mutation control proves nothing |
| `LESSON-REQ-0027` | LESSON | `lesson:LSN-0027` | yes | `COMPLETE` | `COMPLETE` | Verify a lesson's prose may record a residual limit but may never contradict its status |
| `LESSON-REQ-0028` | LESSON | `lesson:LSN-0028` | yes | `COMPLETE` | `COMPLETE` | Verify a configuration key that no code reads is a defect, not documentation |
| `LESSON-REQ-0029` | LESSON | `lesson:LSN-0029` | yes | `COMPLETE` | `COMPLETE` | Verify a required protocol transition must never turn a mandatory gate red |
| `LESSON-REQ-0030` | LESSON | `lesson:LSN-0031` | yes | `COMPLETE` | `COMPLETE` | Verify an empty applicable set is not a missing required set, and a control must tell them apart |
| `LESSON-REQ-0031` | LESSON | `lesson:LSN-0032` | yes | `COMPLETE` | `COMPLETE` | Verify a control written while one Gate was the only Gate stops being a control when the next one starts |
| `LESSON-REQ-0032` | LESSON | `lesson:LSN-0033` | yes | `COMPLETE` | `COMPLETE` | Verify a value bound in middleware is absent in the handlers that run outside it |
| `LESSON-REQ-0033` | LESSON | `lesson:LSN-0034` | yes | `COMPLETE` | `COMPLETE` | Verify re-deriving what the framework already computed diverges from the framework |
| `LESSON-REQ-0034` | LESSON | `lesson:LSN-0035` | yes | `COMPLETE` | `COMPLETE` | Verify captured subprocess output decoded or re-emitted with the platform codepage crashes the tool, not the work |

## Evidence

### REQ-0001 - canonical:GATE-0#1.1

- Source reference: docs/GATE-0-CHECKLIST.md row 1.1
- Description: A canonical, machine-readable requirement specification exists for this Gate and the registry mirrors it row for row.
- Implementation: `file:docs/GATE-0-CHECKLIST.md`, `file:.iacode/policies/canonical-requirements.json`
- Test: `test:Gate0CanonicalSpecificationTests`, `test:test_the_registry_mirrors_the_specification`
- Negative test: _none_
- Documentation: `file:docs/GATE-0-CHECKLIST.md`
- Validation: `checkpoint:CLOSURE-REQUIREMENTS.json`, `command:cmd-0005`
- Guardrail: _none_

### REQ-0002 - canonical:GATE-0#1.2

- Source reference: docs/GATE-0-CHECKLIST.md row 1.2
- Description: The derived expected set names the specification of the Gate it describes instead of a fixed document.
- Implementation: `file:scripts/development-ledger/policies.py`, `file:scripts/development-ledger/derive_requirements.py`
- Test: `test:test_expected_set_names_the_gate_specification`, `test:test_the_setup_gate_still_derives_from_its_own_specification`
- Negative test: _none_
- Documentation: `file:docs/checkpoints/GATE-0-CP-0001/DECISIONS.md`
- Validation: `checkpoint:REQUIREMENTS-MATRIX.json`, `command:cmd-0005`
- Guardrail: _none_

### REQ-0003 - canonical:GATE-0#1.3

- Source reference: docs/GATE-0-CHECKLIST.md row 1.3
- Description: The delivery-assurance scope covers the runtime source this Gate introduces, so a gate result becomes stale when the product changes.
- Implementation: `file:scripts/development-ledger/ledger_common.py`
- Test: `test:test_assurance_scope_covers_the_runtime_source`, `test:test_the_fingerprint_changes_when_the_runtime_changes`
- Negative test: _none_
- Documentation: `file:docs/QUALITY-GATES.md`
- Validation: `checkpoint:REWORK-LOG.jsonl`, `command:cmd-0005`
- Guardrail: _none_

### REQ-0004 - canonical:GATE-0#1.4

- Source reference: docs/GATE-0-CHECKLIST.md row 1.4
- Description: The closed mandatory gate registry carries every executable gate this Gate introduces.
- Implementation: `file:.iacode/policies/quality-gates.json`, `file:scripts/iacode/gates/api_tests.py`, `file:scripts/iacode/gates/web_tests.py`, `file:scripts/iacode/gates/lint.py`, `file:scripts/iacode/gates/infra_definition.py`
- Test: `test:test_every_declared_key_is_read_somewhere`
- Negative test: _none_
- Documentation: `file:docs/QUALITY-GATES.md`
- Validation: `checkpoint:REWORK-LOG.jsonl`, `command:cmd-0005`
- Guardrail: _none_

### REQ-0005 - canonical:GATE-0#1.5

- Source reference: docs/GATE-0-CHECKLIST.md row 1.5
- Description: Every test suite this Gate introduces is declared canonically and is counted by the count derivation and resolvable as evidence.
- Implementation: `file:.iacode/policies/test-suites.json`, `file:.iacode/schemas/test-suites.schema.json`, `file:scripts/development-ledger/derive_counts.py`
- Test: `test:test_declared_suites_are_discovered`, `test:test_an_uncounted_suite_declares_why`, `test:test_evidence_resolution_covers_the_runtime_suites`
- Negative test: _none_
- Documentation: `file:docs/checkpoints/GATE-0-CP-0001/DECISIONS.md`
- Validation: `checkpoint:COUNTS.json`
- Guardrail: _none_

### REQ-0006 - canonical:GATE-0#1.6

- Source reference: docs/GATE-0-CHECKLIST.md row 1.6
- Description: The internal mirror audit judges the Gate it runs in rather than a Gate named in its own source.
- Implementation: `file:scripts/development-ledger/m0_mirror_audit.py`, `file:.iacode/policies/gate-scope.json`
- Test: `test:test_no_future_gate_capability_is_implemented`
- Negative test: _none_
- Documentation: `file:docs/checkpoints/GATE-0-CP-0001/DECISIONS.md`
- Validation: `checkpoint:M1-INTERNAL-MIRROR.json`
- Guardrail: _none_

### REQ-0007 - canonical:GATE-0#1.7

- Source reference: docs/GATE-0-CHECKLIST.md row 1.7
- Description: The internal Red Team battery of this Gate is executable, scoped to the Foundation, and records a null-mutation control.
- Implementation: `file:scripts/development-ledger/gate0_red_team.py`, `file:scripts/development-ledger/gate0_runtime_attacks.py`
- Test: `test:test_the_scope_control_detects_an_implementation`
- Negative test: _none_
- Documentation: `checkpoint:RED-TEAM-REPORT.md`
- Validation: `checkpoint:M1-INTERNAL-RED-TEAM.json`
- Guardrail: _none_

### REQ-0008 - canonical:GATE-0#2.1

- Source reference: docs/GATE-0-CHECKLIST.md row 2.1
- Description: The repository carries the planned application, service, package and infrastructure directories.
- Implementation: `file:apps/api/pyproject.toml`, `file:apps/web/package.json`, `file:services/orchestrator/pyproject.toml`, `file:packages/common/pyproject.toml`, `file:infra/compose/docker-compose.yml`
- Test: `test:test_monorepo_structure_exists`
- Negative test: _none_
- Documentation: `file:docs/ARCHITECTURE.md`
- Validation: `command:cmd-0005`
- Guardrail: _none_

### REQ-0009 - canonical:GATE-0#2.2

- Source reference: docs/GATE-0-CHECKLIST.md row 2.2
- Description: A directory reserved for a later Gate says so and contains no implementation.
- Implementation: `file:.iacode/policies/gate-scope.json`, `file:services/model-gateway/README.md`, `file:apps/cli/README.md`, `file:datasets/README.md`
- Test: `test:test_reserved_directories_declare_themselves`
- Negative test: _none_
- Documentation: `file:docs/ARCHITECTURE.md`
- Validation: `command:cmd-0005`
- Guardrail: _none_

### REQ-0010 - canonical:GATE-0#2.3

- Source reference: docs/GATE-0-CHECKLIST.md row 2.3
- Description: No later-Gate capability is implemented, simulated or faked in this Gate.
- Implementation: `file:scripts/development-ledger/policies.py`
- Test: `test:test_no_future_gate_capability_is_implemented`, `test:test_the_scope_control_detects_an_implementation`
- Negative test: _none_
- Documentation: `file:docs/ARCHITECTURE.md`
- Validation: `checkpoint:M1-INTERNAL-MIRROR.json`, `checkpoint:M1-INTERNAL-RED-TEAM.json`
- Guardrail: _none_

### REQ-0011 - canonical:GATE-0#3.1

- Source reference: docs/GATE-0-CHECKLIST.md row 3.1
- Description: The backend is a real FastAPI application that starts reliably and fails loudly when it cannot.
- Implementation: `file:apps/api/src/iacode_api/main.py`, `file:apps/api/src/iacode_api/lifespan.py`
- Test: `test:test_application_starts`
- Negative test: _none_
- Documentation: `file:docs/DEVELOPMENT.md`
- Validation: `checkpoint:VERIFICATION-REPORT.json`, `command:cmd-0005`
- Guardrail: _none_

### REQ-0012 - canonical:GATE-0#3.2

- Source reference: docs/GATE-0-CHECKLIST.md row 3.2
- Description: Shutdown is graceful and releases every client the application opened.
- Implementation: `file:apps/api/src/iacode_api/lifespan.py`
- Test: `test:test_shutdown_releases_every_client`, `test:test_resources_are_released_after_shutdown`
- Negative test: _none_
- Documentation: `file:docs/ARCHITECTURE.md`
- Validation: `command:cmd-0005`
- Guardrail: _none_

### REQ-0013 - canonical:GATE-0#3.3

- Source reference: docs/GATE-0-CHECKLIST.md row 3.3
- Description: Dependency lifecycle is explicit and held on the application, not in ambient mutable globals.
- Implementation: `file:apps/api/src/iacode_api/dependencies.py`
- Test: `test:test_dependencies_are_held_on_application_state`, `test:test_every_mandatory_dependency_is_probed`
- Negative test: _none_
- Documentation: `file:docs/ARCHITECTURE.md`
- Validation: `command:cmd-0005`
- Guardrail: _none_

### REQ-0014 - canonical:GATE-0#3.4

- Source reference: docs/GATE-0-CHECKLIST.md row 3.4
- Description: `GET /health` reports process liveness and does not depend on external dependencies to answer.
- Implementation: `file:apps/api/src/iacode_api/routes/health.py`
- Test: `test:test_health_is_up_while_dependencies_are_down`, `test:test_health_answers_without_contacting_a_dependency`
- Negative test: _none_
- Documentation: `file:docs/runbooks/FOUNDATION.md`
- Validation: `checkpoint:VERIFICATION-REPORT.json`, `checkpoint:M1-INTERNAL-RED-TEAM.json`
- Guardrail: _none_

### REQ-0015 - canonical:GATE-0#3.5

- Source reference: docs/GATE-0-CHECKLIST.md row 3.5
- Description: `GET /ready` probes PostgreSQL, Redis, MinIO and Temporal and refuses readiness when a mandatory dependency is unavailable.
- Implementation: `file:apps/api/src/iacode_api/routes/health.py`, `file:apps/api/src/iacode_api/readiness.py`
- Test: `test:test_ready_reports_each_dependency`, `test:test_readiness_is_ready_against_the_running_stack`, `test:test_readiness_bounds_a_hanging_probe`
- Negative test: _none_
- Documentation: `file:docs/runbooks/FOUNDATION.md`
- Validation: `checkpoint:VERIFICATION-REPORT.json`, `checkpoint:M1-INTERNAL-RED-TEAM.json`
- Guardrail: _none_

### REQ-0016 - canonical:GATE-0#3.6

- Source reference: docs/GATE-0-CHECKLIST.md row 3.6
- Description: `GET /version` reports the application version and build identity and exposes no secret.
- Implementation: `file:apps/api/src/iacode_api/routes/version.py`
- Test: `test:test_version_exposes_no_secret`
- Negative test: _none_
- Documentation: `file:docs/runbooks/FOUNDATION.md`
- Validation: `checkpoint:VERIFICATION-REPORT.json`, `checkpoint:M1-INTERNAL-RED-TEAM.json`
- Guardrail: _none_

### REQ-0017 - canonical:GATE-0#3.7

- Source reference: docs/GATE-0-CHECKLIST.md row 3.7
- Description: The application exposes a Prometheus metrics endpoint with request, latency, status and dependency metrics.
- Implementation: `file:apps/api/src/iacode_api/observability/metrics.py`
- Test: `test:test_metrics_endpoint_exposes_request_metrics`, `test:test_metrics_label_routes_by_template_not_by_url`, `test:test_readiness_updates_the_dependency_gauge`
- Negative test: _none_
- Documentation: `file:docs/ARCHITECTURE.md`
- Validation: `checkpoint:VERIFICATION-REPORT.json`
- Guardrail: _none_

### REQ-0018 - canonical:GATE-0#3.8

- Source reference: docs/GATE-0-CHECKLIST.md row 3.8
- Description: OpenAPI documentation describes the Foundation endpoints and exposes no internal-only route.
- Implementation: `file:apps/api/src/iacode_api/main.py`
- Test: `test:test_openapi_documents_the_foundation_endpoints`, `test:test_metrics_is_not_part_of_the_api_contract`
- Negative test: _none_
- Documentation: `file:docs/runbooks/FOUNDATION.md`
- Validation: `command:cmd-0005`
- Guardrail: _none_

### REQ-0019 - canonical:GATE-0#3.9

- Source reference: docs/GATE-0-CHECKLIST.md row 3.9
- Description: CORS is configured explicitly from configuration, without a permissive wildcard, and allows the local frontend.
- Implementation: `file:apps/api/src/iacode_api/config.py`, `file:apps/api/src/iacode_api/main.py`
- Test: `test:test_cors_is_explicit_and_not_wildcard`, `test:test_cors_refuses_a_wildcard`, `test:test_cors_allows_the_local_frontend_to_read_the_correlation_header`
- Negative test: _none_
- Documentation: `file:infra/compose/.env.example`
- Validation: `checkpoint:M1-INTERNAL-RED-TEAM.json`
- Guardrail: _none_

### REQ-0020 - canonical:GATE-0#4.1

- Source reference: docs/GATE-0-CHECKLIST.md row 4.1
- Description: Configuration is typed, validated at load time and rejects an invalid or missing mandatory value.
- Implementation: `file:apps/api/src/iacode_api/config.py`
- Test: `test:test_configuration_rejects_invalid_values`
- Negative test: _none_
- Documentation: `file:docs/DEVELOPMENT.md`
- Validation: `checkpoint:M1-INTERNAL-RED-TEAM.json`
- Guardrail: _none_

### REQ-0021 - canonical:GATE-0#4.2

- Source reference: docs/GATE-0-CHECKLIST.md row 4.2
- Description: Safe defaults, development configuration and test configuration are separated rather than conflated.
- Implementation: `file:apps/api/src/iacode_api/config.py`, `file:infra/compose/.env.example`
- Test: `test:test_configuration_layers_are_separate`, `test:test_test_settings_ignore_the_ambient_environment`
- Negative test: _none_
- Documentation: `file:docs/DEVELOPMENT.md`
- Validation: `command:cmd-0005`
- Guardrail: _none_

### REQ-0022 - canonical:GATE-0#4.3

- Source reference: docs/GATE-0-CHECKLIST.md row 4.3
- Description: A committed example environment file documents every key and carries no real secret, and the real file is ignored by Git.
- Implementation: `file:infra/compose/.env.example`, `file:.gitignore`, `file:scripts/iacode/bootstrap_env.py`
- Test: `test:test_env_example_documents_every_key_without_secrets`, `test:test_the_real_environment_file_is_ignored`
- Negative test: _none_
- Documentation: `file:docs/runbooks/FOUNDATION.md`
- Validation: `command:cmd-0005`
- Guardrail: _none_

### REQ-0023 - canonical:GATE-0#4.4

- Source reference: docs/GATE-0-CHECKLIST.md row 4.4
- Description: Secret values are redacted wherever configuration, errors or logs could expose them.
- Implementation: `file:packages/common/src/iacode_common/redaction.py`
- Test: `test:test_secrets_are_redacted_in_logs_and_errors`, `test:test_redaction_masks_a_connection_string_without_hiding_the_host`, `test:test_redaction_reaches_every_depth_of_a_mapping`
- Negative test: _none_
- Documentation: `file:.iacode/policies/secret-policy.md`
- Validation: `checkpoint:M1-INTERNAL-RED-TEAM.json`
- Guardrail: _none_

### REQ-0024 - canonical:GATE-0#4.5

- Source reference: docs/GATE-0-CHECKLIST.md row 4.5
- Description: No secret is baked into an image, a compose file, a Dockerfile or a committed configuration file.
- Implementation: `file:infra/compose/docker-compose.yml`, `file:apps/api/Dockerfile`, `file:apps/web/Dockerfile`
- Test: `test:test_no_secret_is_committed_in_infrastructure`, `test:test_dockerfiles_carry_no_secret`
- Negative test: _none_
- Documentation: `file:.iacode/policies/secret-policy.md`
- Validation: `command:cmd-0005`
- Guardrail: _none_

### REQ-0025 - canonical:GATE-0#5.1

- Source reference: docs/GATE-0-CHECKLIST.md row 5.1
- Description: PostgreSQL runs locally from the compose stack at a pinned version with a persistent named volume.
- Implementation: `file:infra/compose/docker-compose.yml`
- Test: `test:test_postgres_is_pinned_and_persistent`, `test:test_durable_state_uses_named_volumes`
- Negative test: _none_
- Documentation: `file:docs/VERSIONS.md`
- Validation: `checkpoint:VERIFICATION-REPORT.json`
- Guardrail: _none_

### REQ-0026 - canonical:GATE-0#5.2

- Source reference: docs/GATE-0-CHECKLIST.md row 5.2
- Description: The persistence layer is real, asynchronous and pooled, built on SQLAlchemy 2.
- Implementation: `file:apps/api/src/iacode_api/db/engine.py`
- Test: `test:test_database_round_trip`, `test:test_a_failed_statement_does_not_poison_the_pooled_connection`
- Negative test: _none_
- Documentation: `file:docs/ARCHITECTURE.md`
- Validation: `checkpoint:VERIFICATION-REPORT.json`
- Guardrail: _none_

### REQ-0027 - canonical:GATE-0#5.3

- Source reference: docs/GATE-0-CHECKLIST.md row 5.3
- Description: Alembic migrations run from zero against an empty database and produce the declared schema.
- Implementation: `file:apps/api/migrations/versions/0001_foundation_schema.py`, `file:apps/api/migrations/env.py`
- Test: `test:test_migrations_run_from_zero`
- Negative test: _none_
- Documentation: `file:docs/runbooks/FOUNDATION.md`
- Validation: `checkpoint:VERIFICATION-REPORT.json`
- Guardrail: _none_

### REQ-0028 - canonical:GATE-0#5.4

- Source reference: docs/GATE-0-CHECKLIST.md row 5.4
- Description: Starting against an already-migrated database neither fails nor recreates the schema.
- Implementation: `file:apps/api/migrations/env.py`, `file:scripts/iacode/migrate.py`
- Test: `test:test_migrations_are_idempotent_on_restart`
- Negative test: _none_
- Documentation: `file:docs/runbooks/FOUNDATION.md`
- Validation: `checkpoint:VERIFICATION-REPORT.json`
- Guardrail: _none_

### REQ-0029 - canonical:GATE-0#5.5

- Source reference: docs/GATE-0-CHECKLIST.md row 5.5
- Description: A failed migration never produces a healthy readiness or a silent partial start.
- Implementation: `file:apps/api/src/iacode_api/readiness.py`, `file:infra/compose/docker-compose.yml`
- Test: `test:test_failed_migration_does_not_report_ready`, `test:test_the_api_waits_for_the_migration_to_succeed`, `test:test_a_failed_migration_reports_failure`
- Negative test: _none_
- Documentation: `file:docs/runbooks/FOUNDATION.md`
- Validation: `checkpoint:M1-INTERNAL-RED-TEAM.json`
- Guardrail: _none_

### REQ-0030 - canonical:GATE-0#5.6

- Source reference: docs/GATE-0-CHECKLIST.md row 5.6
- Description: The structural domain tables the later Gates build on exist, with their relationships and constraints.
- Implementation: `file:apps/api/src/iacode_api/db/models.py`
- Test: `test:test_structural_tables_exist`, `test:test_relationships_cascade_deliberately`, `test:test_the_schema_matches_the_declared_model`
- Negative test: _none_
- Documentation: `file:docs/ARCHITECTURE.md`
- Validation: `checkpoint:VERIFICATION-REPORT.json`
- Guardrail: _none_

### REQ-0031 - canonical:GATE-0#5.7

- Source reference: docs/GATE-0-CHECKLIST.md row 5.7
- Description: Identifiers use one consistent strategy, UUIDv7, implemented and tested rather than assumed.
- Implementation: `file:packages/common/src/iacode_common/identifiers.py`
- Test: `test:test_uuid7_is_ordered_and_well_formed`, `test:test_uuid7_is_monotonic_within_a_millisecond`, `test:test_identifiers_are_time_ordered_in_the_database`
- Negative test: _none_
- Documentation: `file:docs/ARCHITECTURE.md`
- Validation: `command:cmd-0005`
- Guardrail: _none_

### REQ-0032 - canonical:GATE-0#5.8

- Source reference: docs/GATE-0-CHECKLIST.md row 5.8
- Description: The common column convention is defined once and applied where it makes sense, not forced everywhere.
- Implementation: `file:apps/api/src/iacode_api/db/base.py`
- Test: `test:test_common_columns_follow_the_convention`, `test:test_the_two_base_classes_are_used_deliberately`
- Negative test: _none_
- Documentation: `file:docs/ARCHITECTURE.md`
- Validation: `command:cmd-0005`
- Guardrail: _none_

### REQ-0033 - canonical:GATE-0#5.9

- Source reference: docs/GATE-0-CHECKLIST.md row 5.9
- Description: The pgvector position is decided, recorded, and — where the extension is enabled — migrated and tested.
- Implementation: `file:apps/api/migrations/versions/0001_foundation_schema.py`
- Test: `test:test_pgvector_extension_is_available`
- Negative test: _none_
- Documentation: `file:docs/adr/ADR-0013-pgvector-prepared-not-used.md`
- Validation: `checkpoint:VERIFICATION-REPORT.json`
- Guardrail: _none_

### REQ-0034 - canonical:GATE-0#6.1

- Source reference: docs/GATE-0-CHECKLIST.md row 6.1
- Description: Redis runs locally from the compose stack at a pinned version.
- Implementation: `file:infra/compose/docker-compose.yml`
- Test: `test:test_redis_is_pinned`, `test:test_redis_answers_on_the_published_port`
- Negative test: _none_
- Documentation: `file:docs/VERSIONS.md`
- Validation: `checkpoint:VERIFICATION-REPORT.json`
- Guardrail: _none_

### REQ-0035 - canonical:GATE-0#6.2

- Source reference: docs/GATE-0-CHECKLIST.md row 6.2
- Description: The backend holds a real Redis client whose availability the readiness probe verifies.
- Implementation: `file:apps/api/src/iacode_api/cache/client.py`
- Test: `test:test_ready_reports_each_dependency`
- Negative test: _none_
- Documentation: `file:docs/ARCHITECTURE.md`
- Validation: `checkpoint:VERIFICATION-REPORT.json`, `checkpoint:M1-INTERNAL-RED-TEAM.json`
- Guardrail: _none_

### REQ-0036 - canonical:GATE-0#6.3

- Source reference: docs/GATE-0-CHECKLIST.md row 6.3
- Description: An integration test exercises a real Redis round trip against the running service.
- Implementation: `file:apps/api/tests/integration/test_dependencies.py`
- Test: `test:test_redis_round_trip`
- Negative test: _none_
- Documentation: `file:docs/DEVELOPMENT.md`
- Validation: `checkpoint:VERIFICATION-REPORT.json`
- Guardrail: _none_

### REQ-0037 - canonical:GATE-0#7.1

- Source reference: docs/GATE-0-CHECKLIST.md row 7.1
- Description: MinIO runs locally from the compose stack at a pinned version with a persistent named volume.
- Implementation: `file:infra/compose/docker-compose.yml`
- Test: `test:test_minio_is_pinned_and_persistent`, `test:test_durable_state_uses_named_volumes`
- Negative test: _none_
- Documentation: `file:docs/VERSIONS.md`
- Validation: `checkpoint:VERIFICATION-REPORT.json`
- Guardrail: _none_

### REQ-0038 - canonical:GATE-0#7.2

- Source reference: docs/GATE-0-CHECKLIST.md row 7.2
- Description: The buckets the later Gates need are created by an idempotent bootstrap that is safe to re-run.
- Implementation: `file:infra/compose/docker-compose.yml`, `file:infra/minio/bootstrap-minio.sh`
- Test: `test:test_bucket_bootstrap_is_idempotent`, `test:test_the_artifact_bucket_exists_and_is_private`
- Negative test: _none_
- Documentation: `file:docs/runbooks/FOUNDATION.md`
- Validation: `checkpoint:VERIFICATION-REPORT.json`
- Guardrail: _none_

### REQ-0039 - canonical:GATE-0#7.3

- Source reference: docs/GATE-0-CHECKLIST.md row 7.3
- Description: The readiness probe verifies real object-storage connectivity rather than a reachable port.
- Implementation: `file:apps/api/src/iacode_api/storage/client.py`
- Test: `test:test_ready_reports_each_dependency`
- Negative test: _none_
- Documentation: `file:docs/ARCHITECTURE.md`
- Validation: `checkpoint:VERIFICATION-REPORT.json`, `checkpoint:M1-INTERNAL-RED-TEAM.json`
- Guardrail: _none_

### REQ-0040 - canonical:GATE-0#7.4

- Source reference: docs/GATE-0-CHECKLIST.md row 7.4
- Description: An integration test writes, reads and deletes a real object.
- Implementation: `file:apps/api/tests/integration/test_dependencies.py`
- Test: `test:test_object_storage_round_trip`
- Negative test: _none_
- Documentation: `file:docs/DEVELOPMENT.md`
- Validation: `checkpoint:VERIFICATION-REPORT.json`
- Guardrail: _none_

### REQ-0041 - canonical:GATE-0#8.1

- Source reference: docs/GATE-0-CHECKLIST.md row 8.1
- Description: Temporal runs locally from the compose stack at a pinned version with its persistent state.
- Implementation: `file:infra/compose/docker-compose.yml`, `file:infra/temporal/dynamicconfig/iacode.yaml`
- Test: `test:test_temporal_is_pinned`, `test:test_the_configured_namespace_exists`
- Negative test: _none_
- Documentation: `file:docs/VERSIONS.md`
- Validation: `checkpoint:VERIFICATION-REPORT.json`
- Guardrail: _none_

### REQ-0042 - canonical:GATE-0#8.2

- Source reference: docs/GATE-0-CHECKLIST.md row 8.2
- Description: An IACode worker connects to Temporal and polls its task queue as a first-class service.
- Implementation: `file:services/orchestrator/src/iacode_orchestrator/worker.py`, `file:services/orchestrator/src/iacode_orchestrator/healthcheck.py`
- Test: `test:test_worker_registers_the_smoke_workflow`, `test:test_the_worker_is_polling_our_task_queue`
- Negative test: _none_
- Documentation: `file:docs/ARCHITECTURE.md`
- Validation: `checkpoint:VERIFICATION-REPORT.json`
- Guardrail: _none_

### REQ-0043 - canonical:GATE-0#8.3

- Source reference: docs/GATE-0-CHECKLIST.md row 8.3
- Description: The readiness probe verifies real Temporal connectivity.
- Implementation: `file:apps/api/src/iacode_api/workflows/client.py`
- Test: `test:test_temporal_connectivity`, `test:test_temporal_readiness_fails_against_an_unknown_namespace`
- Negative test: _none_
- Documentation: `file:docs/ARCHITECTURE.md`
- Validation: `checkpoint:VERIFICATION-REPORT.json`
- Guardrail: _none_

### REQ-0044 - canonical:GATE-0#8.4

- Source reference: docs/GATE-0-CHECKLIST.md row 8.4
- Description: A minimal real workflow and activity execute end to end through the worker and return an observable result.
- Implementation: `file:services/orchestrator/src/iacode_orchestrator/workflows/smoke.py`, `file:services/orchestrator/src/iacode_orchestrator/smoke_client.py`
- Test: `test:test_smoke_workflow_executes_end_to_end`, `test:test_the_workflow_result_is_recorded_in_history`
- Negative test: _none_
- Documentation: `file:docs/runbooks/FOUNDATION.md`
- Validation: `checkpoint:VERIFICATION-REPORT.json`
- Guardrail: _none_

### REQ-0045 - canonical:GATE-0#8.5

- Source reference: docs/GATE-0-CHECKLIST.md row 8.5
- Description: No agent workflow, tool call or orchestration of a later Gate is implemented here.
- Implementation: `file:services/orchestrator/src/iacode_orchestrator/workflows/smoke.py`
- Test: `test:test_no_future_gate_capability_is_implemented`
- Negative test: _none_
- Documentation: `file:docs/ARCHITECTURE.md`
- Validation: `checkpoint:M1-INTERNAL-MIRROR.json`
- Guardrail: _none_

### REQ-0046 - canonical:GATE-0#9.1

- Source reference: docs/GATE-0-CHECKLIST.md row 9.1
- Description: A real Angular application exists and builds reproducibly with pinned dependencies.
- Implementation: `file:apps/web/package.json`, `file:apps/web/package-lock.json`, `file:apps/web/Dockerfile`
- Test: `test:test_web_dependencies_are_locked`
- Negative test: _none_
- Documentation: `file:docs/VERSIONS.md`
- Validation: `checkpoint:VERIFICATION-REPORT.json`
- Guardrail: _none_

### REQ-0047 - canonical:GATE-0#9.2

- Source reference: docs/GATE-0-CHECKLIST.md row 9.2
- Description: The Foundation page identifies IACode and renders the live backend health, readiness and version.
- Implementation: `file:apps/web/src/app/app.ts`, `file:apps/web/src/app/app.html`, `file:apps/web/src/app/foundation-status.service.ts`
- Test: `test:test_the_web_shell_is_served`, `test:test_unknown_paths_serve_the_application_shell`
- Negative test: _none_
- Documentation: `file:docs/runbooks/FOUNDATION.md`
- Validation: `checkpoint:VERIFICATION-REPORT.json`
- Guardrail: _none_

### REQ-0048 - canonical:GATE-0#9.3

- Source reference: docs/GATE-0-CHECKLIST.md row 9.3
- Description: The API base address is centralized in configuration, carries no secret and is not hardcoded across the code.
- Implementation: `file:apps/web/src/app/api-config.ts`, `file:apps/web/docker-entrypoint.sh`
- Test: `test:test_api_base_is_centralised`, `test:test_the_runtime_configuration_is_written_at_start_up`, `test:test_the_runtime_configuration_carries_no_secret`
- Negative test: _none_
- Documentation: `file:docs/ARCHITECTURE.md`
- Validation: `checkpoint:VERIFICATION-REPORT.json`
- Guardrail: _none_

### REQ-0049 - canonical:GATE-0#9.4

- Source reference: docs/GATE-0-CHECKLIST.md row 9.4
- Description: Frontend unit tests run headless and are part of the verification command.
- Implementation: `file:scripts/iacode/gates/web_tests.py`, `file:scripts/iacode/verify.py`
- Test: `test:test_web_dependencies_are_locked`
- Negative test: _none_
- Documentation: `file:docs/DEVELOPMENT.md`
- Validation: `checkpoint:VERIFICATION-REPORT.json`, `command:cmd-0005`
- Guardrail: _none_

### REQ-0050 - canonical:GATE-0#10.1

- Source reference: docs/GATE-0-CHECKLIST.md row 10.1
- Description: Every image builds from a pinned base, runs as a non-root user where practical, carries no secret and excludes build waste.
- Implementation: `file:apps/api/Dockerfile`, `file:apps/web/Dockerfile`, `file:services/orchestrator/Dockerfile`, `file:.dockerignore`
- Test: `test:test_dockerfiles_pin_and_drop_root`, `test:test_the_build_context_excludes_the_ledger_and_the_toolchain`
- Negative test: _none_
- Documentation: `file:docs/VERSIONS.md`
- Validation: `command:cmd-0005`
- Guardrail: _none_

### REQ-0051 - canonical:GATE-0#10.2

- Source reference: docs/GATE-0-CHECKLIST.md row 10.2
- Description: The compose stack declares every Foundation service and nothing that the Foundation does not need.
- Implementation: `file:infra/compose/docker-compose.yml`
- Test: `test:test_compose_declares_the_foundation_services`
- Negative test: _none_
- Documentation: `file:docs/runbooks/FOUNDATION.md`
- Validation: `command:cmd-0005`
- Guardrail: _none_

### REQ-0052 - canonical:GATE-0#10.3

- Source reference: docs/GATE-0-CHECKLIST.md row 10.3
- Description: Every service that can report health has a real healthcheck, and start-up ordering uses those conditions instead of fixed sleeps.
- Implementation: `file:infra/compose/docker-compose.yml`
- Test: `test:test_compose_uses_health_conditions_not_sleeps`, `test:test_every_long_running_service_has_a_healthcheck`, `test:test_healthchecks_do_more_than_confirm_a_process_exists`
- Negative test: _none_
- Documentation: `file:docs/runbooks/FOUNDATION.md`
- Validation: `checkpoint:M1-INTERNAL-RED-TEAM.json`
- Guardrail: _none_

### REQ-0053 - canonical:GATE-0#10.4

- Source reference: docs/GATE-0-CHECKLIST.md row 10.4
- Description: Restart behaviour is declared, and the stack recovers its state after a restart.
- Implementation: `file:infra/compose/docker-compose.yml`, `file:scripts/iacode/scenarios/restart.py`
- Test: `test:test_every_long_running_service_declares_a_restart_policy`, `test:test_one_shot_jobs_do_not_restart`
- Negative test: _none_
- Documentation: `file:docs/runbooks/FOUNDATION.md`
- Validation: `checkpoint:VERIFICATION-REPORT.json`
- Guardrail: _none_

### REQ-0054 - canonical:GATE-0#10.5

- Source reference: docs/GATE-0-CHECKLIST.md row 10.5
- Description: Durable state lives in named volumes that are documented, not in the container filesystem.
- Implementation: `file:infra/compose/docker-compose.yml`
- Test: `test:test_durable_state_uses_named_volumes`
- Negative test: _none_
- Documentation: `file:docs/runbooks/FOUNDATION.md`
- Validation: `checkpoint:VERIFICATION-REPORT.json`, `checkpoint:M1-INTERNAL-RED-TEAM.json`
- Guardrail: _none_

### REQ-0055 - canonical:GATE-0#10.6

- Source reference: docs/GATE-0-CHECKLIST.md row 10.6
- Description: The stack uses an explicit network and publishes only the ports local development needs, from configuration.
- Implementation: `file:infra/compose/docker-compose.yml`, `file:infra/compose/.env.example`
- Test: `test:test_published_ports_are_configurable_and_minimal`, `test:test_published_ports_are_loopback_only`, `test:test_every_service_is_on_the_explicit_network`
- Negative test: _none_
- Documentation: `file:docs/runbooks/FOUNDATION.md`
- Validation: `checkpoint:M1-INTERNAL-RED-TEAM.json`
- Guardrail: _none_

### REQ-0056 - canonical:GATE-0#11.1

- Source reference: docs/GATE-0-CHECKLIST.md row 11.1
- Description: The backend and the worker emit structured logs carrying the contract fields, absent rather than invented when there is no context.
- Implementation: `file:packages/telemetry/src/iacode_telemetry/logging.py`, `file:packages/telemetry/src/iacode_telemetry/context.py`
- Test: `test:test_structured_log_contract`, `test:test_a_field_with_no_value_is_absent_rather_than_null`
- Negative test: _none_
- Documentation: `file:docs/ARCHITECTURE.md`
- Validation: `checkpoint:M1-INTERNAL-RED-TEAM.json`
- Guardrail: _none_

### REQ-0057 - canonical:GATE-0#11.2

- Source reference: docs/GATE-0-CHECKLIST.md row 11.2
- Description: Every HTTP request carries a correlation identifier that is accepted or generated, propagated, returned and logged.
- Implementation: `file:apps/api/src/iacode_api/middleware/correlation.py`
- Test: `test:test_correlation_identifier_is_propagated`, `test:test_a_malformed_correlation_identifier_is_replaced`, `test:test_the_request_identifier_differs_per_request`
- Negative test: _none_
- Documentation: `file:docs/ARCHITECTURE.md`
- Validation: `checkpoint:M1-INTERNAL-RED-TEAM.json`
- Guardrail: _none_

### REQ-0058 - canonical:GATE-0#11.3

- Source reference: docs/GATE-0-CHECKLIST.md row 11.3
- Description: The API error contract is explicit, extensible and never returns a traceback or internal detail to the client while keeping it in the logs.
- Implementation: `file:apps/api/src/iacode_api/errors.py`, `file:packages/contracts/src/iacode_contracts/foundation.py`
- Test: `test:test_internal_error_leaks_nothing`, `test:test_internal_error_still_carries_a_correlation_identifier`, `test:test_validation_errors_do_not_echo_the_submitted_value`
- Negative test: _none_
- Documentation: `file:docs/ARCHITECTURE.md`
- Validation: `checkpoint:M1-INTERNAL-RED-TEAM.json`
- Guardrail: _none_

### REQ-0059 - canonical:GATE-0#11.4

- Source reference: docs/GATE-0-CHECKLIST.md row 11.4
- Description: Prometheus is provisioned and scrapes the API and the worker.
- Implementation: `file:infra/prometheus/prometheus.yml`, `file:services/orchestrator/src/iacode_orchestrator/runtime.py`
- Test: `test:test_prometheus_scrapes_the_foundation_targets`, `test:test_the_api_instruments_reach_prometheus`
- Negative test: _none_
- Documentation: `file:docs/runbooks/FOUNDATION.md`
- Validation: `checkpoint:VERIFICATION-REPORT.json`
- Guardrail: _none_

### REQ-0060 - canonical:GATE-0#11.5

- Source reference: docs/GATE-0-CHECKLIST.md row 11.5
- Description: Grafana starts with the Prometheus datasource and a Foundation dashboard provisioned automatically.
- Implementation: `file:infra/grafana/provisioning/datasources/prometheus.yml`, `file:infra/grafana/dashboards/foundation.json`
- Test: `test:test_grafana_provisioning_is_declared`, `test:test_grafana_is_healthy`, `test:test_grafana_refuses_anonymous_access`
- Negative test: _none_
- Documentation: `file:docs/runbooks/FOUNDATION.md`
- Validation: `checkpoint:VERIFICATION-REPORT.json`
- Guardrail: _none_

### REQ-0061 - canonical:GATE-0#11.6

- Source reference: docs/GATE-0-CHECKLIST.md row 11.6
- Description: The OpenTelemetry position for the Foundation is decided and recorded rather than left implicit.
- Implementation: `file:packages/telemetry/src/iacode_telemetry/context.py`
- Test: `test:test_a_field_with_no_value_is_absent_rather_than_null`
- Negative test: _none_
- Documentation: `file:docs/adr/ADR-0015-opentelemetry-deferred.md`
- Validation: `command:cmd-0005`
- Guardrail: _none_

### REQ-0062 - canonical:GATE-0#12.1

- Source reference: docs/GATE-0-CHECKLIST.md row 12.1
- Description: A reproducible backup produces a PostgreSQL dump and the object-storage contents, with a correct exit code and a log, and fails loudly on partial failure.
- Implementation: `file:scripts/iacode/backup.py`
- Test: `test:test_backup_fails_loudly`, `test:test_an_empty_dump_is_a_failure`
- Negative test: _none_
- Documentation: `file:docs/runbooks/BACKUP-RESTORE.md`
- Validation: `checkpoint:VERIFICATION-REPORT.json`, `checkpoint:M1-INTERNAL-RED-TEAM.json`
- Guardrail: _none_

### REQ-0063 - canonical:GATE-0#12.2

- Source reference: docs/GATE-0-CHECKLIST.md row 12.2
- Description: The backup never writes a credential into its artifacts or its log.
- Implementation: `file:scripts/iacode/backup.py`
- Test: `test:test_backup_artifacts_carry_no_secret`, `test:test_the_backup_never_passes_a_password_as_an_argument`
- Negative test: _none_
- Documentation: `file:docs/runbooks/BACKUP-RESTORE.md`
- Validation: `checkpoint:M1-INTERNAL-RED-TEAM.json`
- Guardrail: _none_

### REQ-0064 - canonical:GATE-0#12.3

- Source reference: docs/GATE-0-CHECKLIST.md row 12.3
- Description: A restore reconstructs the database and the object storage from a backup produced by this tooling.
- Implementation: `file:scripts/iacode/restore.py`
- Test: `test:test_an_incomplete_backup_is_refused`, `test:test_a_corrupt_dump_is_detected_before_anything_is_overwritten`, `test:test_a_valid_backup_passes_verification`
- Negative test: _none_
- Documentation: `file:docs/runbooks/BACKUP-RESTORE.md`
- Validation: `checkpoint:VERIFICATION-REPORT.json`, `checkpoint:M1-INTERNAL-RED-TEAM.json`
- Guardrail: _none_

### REQ-0065 - canonical:GATE-0#12.4

- Source reference: docs/GATE-0-CHECKLIST.md row 12.4
- Description: Backup and restore are verified end to end with synthetic data in a disposable environment, and the restored data is checked rather than assumed.
- Implementation: `file:scripts/iacode/backup_restore_check.py`
- Test: `test:test_a_valid_backup_passes_verification`
- Negative test: _none_
- Documentation: `file:docs/runbooks/BACKUP-RESTORE.md`
- Validation: `checkpoint:VERIFICATION-REPORT.json`
- Guardrail: _none_

### REQ-0066 - canonical:GATE-0#12.5

- Source reference: docs/GATE-0-CHECKLIST.md row 12.5
- Description: Backup retention for the Foundation is either implemented simply or documented as out of scope, with no silent gap.
- Implementation: `file:scripts/iacode/backup.py`
- Test: `test:test_retention_keeps_the_newest_and_deletes_the_rest`, `test:test_retention_can_be_disabled`, `test:test_retention_ignores_a_directory_that_is_not_a_backup`
- Negative test: _none_
- Documentation: `file:docs/runbooks/BACKUP-RESTORE.md`
- Validation: `command:cmd-0005`
- Guardrail: _none_

### REQ-0067 - canonical:GATE-0#13.1

- Source reference: docs/GATE-0-CHECKLIST.md row 13.1
- Description: One documented command runs the whole Gate verification and works on the primary Windows environment as well as on POSIX.
- Implementation: `file:scripts/iacode/verify.py`, `file:verify.ps1`, `file:scripts/iacode/policies_bridge.py`
- Test: `test:test_declared_suites_are_discovered`
- Negative test: _none_
- Documentation: `file:docs/DEVELOPMENT.md`
- Validation: `checkpoint:VERIFICATION-REPORT.json`, `command:cmd-0005`
- Guardrail: _none_

### REQ-0068 - canonical:GATE-0#13.2

- Source reference: docs/GATE-0-CHECKLIST.md row 13.2
- Description: The backend suite covers health, readiness, version, configuration, redaction, error handling, correlation, database, cache, object storage, workflows and migrations.
- Implementation: `file:apps/api/tests/conftest.py`
- Test: `test:test_health_is_up_while_dependencies_are_down`, `test:test_database_round_trip`, `test:test_redis_round_trip`, `test:test_object_storage_round_trip`, `test:test_smoke_workflow_executes_end_to_end`, `test:test_migrations_run_from_zero`
- Negative test: _none_
- Documentation: `file:docs/DEVELOPMENT.md`
- Validation: `checkpoint:VERIFICATION-REPORT.json`
- Guardrail: _none_

### REQ-0069 - canonical:GATE-0#13.3

- Source reference: docs/GATE-0-CHECKLIST.md row 13.3
- Description: The frontend suite covers bootstrap, the status rendering and the API configuration, and the production build succeeds.
- Implementation: `file:apps/web/src/app/app.spec.ts`, `file:apps/web/src/app/foundation-status.service.spec.ts`, `file:apps/web/src/app/api-config.spec.ts`
- Test: `test:test_web_dependencies_are_locked`
- Negative test: _none_
- Documentation: `file:docs/DEVELOPMENT.md`
- Validation: `checkpoint:VERIFICATION-REPORT.json`, `command:cmd-0005`
- Guardrail: _none_

### REQ-0070 - canonical:GATE-0#13.4

- Source reference: docs/GATE-0-CHECKLIST.md row 13.4
- Description: Infrastructure smoke validation proves that our own configuration of each service is operational.
- Implementation: `file:infra/tests/test_running_stack.py`, `file:infra/tests/test_compose_definition.py`
- Test: `test:test_prometheus_scrapes_the_foundation_targets`, `test:test_the_temporal_databases_exist_beside_ours`
- Negative test: _none_
- Documentation: `file:docs/DEVELOPMENT.md`
- Validation: `checkpoint:VERIFICATION-REPORT.json`
- Guardrail: _none_

### REQ-0071 - canonical:GATE-0#13.5

- Source reference: docs/GATE-0-CHECKLIST.md row 13.5
- Description: A fresh installation with no previous volume reaches a ready stack, a migrated database, a reachable frontend and a green smoke check.
- Implementation: `file:scripts/iacode/scenarios/fresh_install.py`
- Test: `test:test_migrations_run_from_zero`
- Negative test: _none_
- Documentation: `file:docs/runbooks/FOUNDATION.md`
- Validation: `checkpoint:VERIFICATION-REPORT.json`
- Guardrail: _none_

### REQ-0072 - canonical:GATE-0#13.6

- Source reference: docs/GATE-0-CHECKLIST.md row 13.6
- Description: A restart of the running stack returns every service to ready with its data intact.
- Implementation: `file:scripts/iacode/scenarios/restart.py`
- Test: `test:test_migrations_are_idempotent_on_restart`
- Negative test: _none_
- Documentation: `file:docs/runbooks/FOUNDATION.md`
- Validation: `checkpoint:VERIFICATION-REPORT.json`
- Guardrail: _none_

### REQ-0073 - canonical:GATE-0#13.7

- Source reference: docs/GATE-0-CHECKLIST.md row 13.7
- Description: With a mandatory dependency stopped, liveness may stay up while readiness fails correctly, and readiness recovers when the dependency returns.
- Implementation: `file:scripts/iacode/scenarios/dependency_failure.py`
- Test: `test:test_health_is_up_while_dependencies_are_down`, `test:test_ready_reports_each_dependency`
- Negative test: _none_
- Documentation: `file:docs/runbooks/FOUNDATION.md`
- Validation: `checkpoint:VERIFICATION-REPORT.json`, `checkpoint:M1-INTERNAL-RED-TEAM.json`
- Guardrail: _none_

### REQ-0074 - canonical:GATE-0#13.8

- Source reference: docs/GATE-0-CHECKLIST.md row 13.8
- Description: Lint and static analysis run over the backend, the worker and the frontend and are green.
- Implementation: `file:ruff.toml`, `file:scripts/iacode/gates/lint.py`, `file:apps/web/package.json`
- Test: `test:test_declared_suites_are_discovered`
- Negative test: _none_
- Documentation: `file:docs/DEVELOPMENT.md`
- Validation: `checkpoint:VERIFICATION-REPORT.json`, `command:cmd-0005`
- Guardrail: _none_

### REQ-0075 - canonical:GATE-0#13.9

- Source reference: docs/GATE-0-CHECKLIST.md row 13.9
- Description: A dependency vulnerability scan is executed, or its absence is justified, and relevant Critical and High findings block the Gate.
- Implementation: `file:scripts/iacode/dependency_scan.py`
- Test: `test:test_web_dependencies_are_locked`
- Negative test: _none_
- Documentation: `file:docs/VERSIONS.md`
- Validation: `checkpoint:VERIFICATION-REPORT.json`, `command:cmd-0005`
- Guardrail: _none_

### REQ-0076 - canonical:GATE-0#14.1

- Source reference: docs/GATE-0-CHECKLIST.md row 14.1
- Description: The repository entry documentation describes what exists after this Gate and how to run it.
- Implementation: `file:README.md`
- Test: `test:test_monorepo_structure_exists`
- Negative test: _none_
- Documentation: `file:README.md`
- Validation: `command:cmd-0005`
- Guardrail: _none_

### REQ-0077 - canonical:GATE-0#14.2

- Source reference: docs/GATE-0-CHECKLIST.md row 14.2
- Description: The architecture document describes the Foundation runtime, its boundaries and what is deliberately absent.
- Implementation: `file:docs/ARCHITECTURE.md`
- Test: `test:test_no_future_gate_capability_is_implemented`
- Negative test: _none_
- Documentation: `file:docs/ARCHITECTURE.md`
- Validation: `checkpoint:M1-INTERNAL-MIRROR.json`
- Guardrail: _none_

### REQ-0078 - canonical:GATE-0#14.3

- Source reference: docs/GATE-0-CHECKLIST.md row 14.3
- Description: A development guide explains the local workflow end to end for a new machine.
- Implementation: `file:docs/DEVELOPMENT.md`
- Test: `test:test_declared_suites_are_discovered`
- Negative test: _none_
- Documentation: `file:docs/DEVELOPMENT.md`
- Validation: `command:cmd-0005`
- Guardrail: _none_

### REQ-0079 - canonical:GATE-0#14.4

- Source reference: docs/GATE-0-CHECKLIST.md row 14.4
- Description: An operational runbook documents start, stop, rebuild, reset, migrate, health, readiness, Grafana and the smoke checks.
- Implementation: `file:docs/runbooks/FOUNDATION.md`
- Test: `test:test_the_web_shell_is_served`
- Negative test: _none_
- Documentation: `file:docs/runbooks/FOUNDATION.md`
- Validation: `checkpoint:VERIFICATION-REPORT.json`
- Guardrail: _none_

### REQ-0080 - canonical:GATE-0#14.5

- Source reference: docs/GATE-0-CHECKLIST.md row 14.5
- Description: A backup and restore runbook documents the full procedure and its verification.
- Implementation: `file:docs/runbooks/BACKUP-RESTORE.md`
- Test: `test:test_a_valid_backup_passes_verification`
- Negative test: _none_
- Documentation: `file:docs/runbooks/BACKUP-RESTORE.md`
- Validation: `checkpoint:VERIFICATION-REPORT.json`
- Guardrail: _none_

### REQ-0081 - canonical:GATE-0#14.6

- Source reference: docs/GATE-0-CHECKLIST.md row 14.6
- Description: The pinned versions of every runtime, service and principal library are recorded in one place.
- Implementation: `file:docs/VERSIONS.md`
- Test: `test:test_every_image_is_pinned`, `test:test_web_dependencies_are_locked`
- Negative test: _none_
- Documentation: `file:docs/VERSIONS.md`
- Validation: `command:cmd-0005`
- Guardrail: _none_

### REQ-0082 - canonical:GATE-0#14.7

- Source reference: docs/GATE-0-CHECKLIST.md row 14.7
- Description: Every structural decision of this Gate that is not already recorded becomes an ADR, and no ADR duplicates an existing decision.
- Implementation: `file:docs/adr/ADR-0012-foundation-runtime-stack.md`, `file:docs/adr/ADR-0013-pgvector-prepared-not-used.md`, `file:docs/adr/ADR-0014-one-postgresql-server-for-the-foundation.md`, `file:docs/adr/ADR-0015-opentelemetry-deferred.md`
- Test: `test:test_no_future_gate_capability_is_implemented`
- Negative test: _none_
- Documentation: `file:docs/adr/ADR-0012-foundation-runtime-stack.md`
- Validation: `checkpoint:M1-INTERNAL-MIRROR.json`
- Guardrail: _none_

### REQ-0083 - canonical:GATE-0#15.1

- Source reference: docs/GATE-0-CHECKLIST.md row 15.1
- Description: The entry contract and the plan describe the current Gate and its status truthfully.
- Implementation: `file:START-HERE.md`, `file:docs/MASTER-PLAN.md`
- Test: `test:test_the_specification_exists_and_is_parseable`
- Negative test: _none_
- Documentation: `file:START-HERE.md`
- Validation: `command:cmd-0005`
- Guardrail: _none_

### REQ-0084 - canonical:GATE-0#15.2

- Source reference: docs/GATE-0-CHECKLIST.md row 15.2
- Description: The Gate produces a retrospective from the canonical template.
- Implementation: `file:.iacode/memory/retrospectives/GATE-0-CP-0001.md`
- Test: `test:test_declared_suites_are_discovered`
- Negative test: _none_
- Documentation: `file:docs/ENGINEERING-MEMORY.md`
- Validation: `command:cmd-0005`
- Guardrail: _none_

### LESSON-REQ-0001 - lesson:LSN-0001

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0001
- Description: Verify checkpoint validation must succeed from a detached checkout of the checkpoint tag
- Implementation: `file:scripts/development-ledger/validate_checkpoint.py`
- Test: `test:DetachedHeadValidationTests`
- Negative test: _none_
- Documentation: `file:.iacode/memory/LESSONS.md`
- Validation: `checkpoint:HANDOFF.md`
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0002 - lesson:LSN-0002

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0002
- Description: Verify a file inventory must be recomputed from the repository, never trusted as an assertion
- Implementation: `checkpoint:FILES.json`
- Test: `test:DeltaInventoryTests`
- Negative test: _none_
- Documentation: `file:.iacode/memory/LESSONS.md`
- Validation: `command:cmd-0005`
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0003 - lesson:LSN-0003

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0003
- Description: Verify every operation attempt must be auditable, including a refusal decided before execution
- Implementation: `checkpoint:COMMANDS.jsonl`
- Test: `test:FinalizationAttemptRecordingTests`
- Negative test: _none_
- Documentation: `file:.iacode/memory/LESSONS.md`
- Validation: `command:cmd-0005`
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0004 - lesson:LSN-0004

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0004
- Description: Verify a checkpoint may never claim readiness while it also claims to be blocked
- Implementation: `checkpoint:STATE.json`
- Test: `test:StatusBlockerInvariantTests`
- Negative test: _none_
- Documentation: `file:.iacode/memory/LESSONS.md`
- Validation: `command:cmd-0005`
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0005 - lesson:LSN-0005

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0005
- Description: Verify a PASS requires evidence that can be executed or resolved, not a statement
- Implementation: `checkpoint:QUALITY.json`
- Test: `test:QualityEvidenceTests`
- Negative test: _none_
- Documentation: `file:.iacode/memory/LESSONS.md`
- Validation: `command:cmd-0005`
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0006 - lesson:LSN-0006

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0006
- Description: Verify the repository must be self-contained; a specification may not live outside it
- Implementation: `file:docs/GATE-0-CHECKLIST.md`
- Test: `test:Gate0CanonicalSpecificationTests`
- Negative test: _none_
- Documentation: `file:.iacode/memory/LESSONS.md`
- Validation: `command:cmd-0005`
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0007 - lesson:LSN-0007

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0007
- Description: Verify independent validation cannot be declared by the run that did the work
- Implementation: `checkpoint:STATE.json`
- Test: `test:SecondToolValidationTests`
- Negative test: _none_
- Documentation: `file:.iacode/memory/LESSONS.md`
- Validation: `command:cmd-0005`
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0008 - lesson:LSN-0008

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0008
- Description: Verify requirement completeness must be total and evidence-backed before handoff
- Implementation: `checkpoint:REQUIREMENTS-MATRIX.json`
- Test: `test:test_declared_suites_are_discovered`
- Negative test: _none_
- Documentation: `file:.iacode/memory/LESSONS.md`
- Validation: `checkpoint:COMPLETENESS-REPORT.json`
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0009 - lesson:LSN-0009

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0009
- Description: Verify a red gate requires rework, never a waiver, and never a weakened check
- Implementation: `checkpoint:REWORK-LOG.jsonl`
- Test: `test:GreenKeeperToolTests`
- Negative test: _none_
- Documentation: `file:.iacode/memory/LESSONS.md`
- Validation: `command:cmd-0005`
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0010 - lesson:LSN-0010

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0010
- Description: Verify a recorded command must carry runtime, working directory, commit and purpose to be replayable
- Implementation: `checkpoint:COMMANDS.jsonl`
- Test: `test:CommandReproducibilityTests`
- Negative test: _none_
- Documentation: `file:.iacode/memory/LESSONS.md`
- Validation: `command:cmd-0005`
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0011 - lesson:LSN-0011

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0011
- Description: Verify a control over a checkpoint's own evidence must be scoped to the moment it matters
- Implementation: `file:scripts/development-ledger/green_keeper.py`
- Test: `test:DeliveryAssuranceGateTests`
- Negative test: _none_
- Documentation: `file:.iacode/memory/LESSONS.md`
- Validation: `checkpoint:REWORK-LOG.jsonl`
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0012 - lesson:LSN-0012

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0012
- Description: Verify sealed checkpoints and their tags are immutable, and tooling must keep validating them
- Implementation: `file:.iacode/anchors/checkpoint-chain.json`
- Test: `test:HistoricalCheckpointCompatibilityTests`
- Negative test: _none_
- Documentation: `file:.iacode/memory/LESSONS.md`
- Validation: `checkpoint:M1-INTERNAL-MIRROR.json`
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0013 - lesson:LSN-0013

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0013
- Description: Verify an installed capability must be detected by resolved path, not by a bare command lookup
- Implementation: `file:docs/VERSIONS.md`
- Test: `test:test_every_image_is_pinned`
- Negative test: _none_
- Documentation: `file:.iacode/memory/LESSONS.md`
- Validation: `checkpoint:BASELINE.md`
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0014 - lesson:LSN-0014

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0014
- Description: Verify evidence must be recorded as it happens, not reconstructed at the end of a run
- Implementation: `checkpoint:COMMANDS.jsonl`
- Test: `test:CommandReproducibilityTests`
- Negative test: _none_
- Documentation: `file:.iacode/memory/LESSONS.md`
- Validation: `command:cmd-0005`
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0015 - lesson:LSN-0015

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0015
- Description: Verify every positive terminal status needs one shared promotion invariant
- Implementation: `file:scripts/development-ledger/validate_checkpoint.py`
- Test: `test:PromotionInvariantTests`
- Negative test: _none_
- Documentation: `file:.iacode/memory/LESSONS.md`
- Validation: `command:cmd-0005`
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0016 - lesson:LSN-0016

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0016
- Description: Verify a mandatory set must be closed by policy, never chosen by the caller
- Implementation: `file:.iacode/policies/quality-gates.json`, `file:scripts/iacode/policies_bridge.py`
- Test: `test:MandatoryGatePolicyTests`
- Negative test: _none_
- Documentation: `file:.iacode/memory/LESSONS.md`
- Validation: `checkpoint:REWORK-LOG.jsonl`
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0017 - lesson:LSN-0017

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0017
- Description: Verify a completeness denominator must come from a source the delivery does not own
- Implementation: `file:scripts/development-ledger/policies.py`
- Test: `test:test_expected_set_names_the_gate_specification`
- Negative test: _none_
- Documentation: `file:.iacode/memory/LESSONS.md`
- Validation: `checkpoint:CLOSURE-REQUIREMENTS.json`
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0018 - lesson:LSN-0018

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0018
- Description: Verify a structured reference must be resolved, not merely well typed
- Implementation: `file:.iacode/policies/test-suites.json`
- Test: `test:test_evidence_resolution_covers_the_runtime_suites`
- Negative test: _none_
- Documentation: `file:.iacode/memory/LESSONS.md`
- Validation: `checkpoint:COMPLETENESS-REPORT.json`
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0019 - lesson:LSN-0019

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0019
- Description: Verify a derived artifact must carry a fingerprint of the inputs that produced it
- Implementation: `file:scripts/development-ledger/derive_counts.py`
- Test: `test:test_declared_suites_are_discovered`
- Negative test: _none_
- Documentation: `file:.iacode/memory/LESSONS.md`
- Validation: `checkpoint:COUNTS.json`
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0020 - lesson:LSN-0020

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0020
- Description: Verify evidence produced from a dirty tree needs immutable input identity
- Implementation: `checkpoint:COMMANDS.jsonl`
- Test: `test:CommandReproducibilityTests`
- Negative test: _none_
- Documentation: `file:.iacode/memory/LESSONS.md`
- Validation: `command:cmd-0005`
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0021 - lesson:LSN-0021

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0021
- Description: Verify sealed history needs an anchor outside the content it describes
- Implementation: `file:.iacode/anchors/checkpoint-chain.json`
- Test: `test:test_the_scope_control_ignores_a_gate_that_has_already_run`
- Negative test: _none_
- Documentation: `file:.iacode/memory/LESSONS.md`
- Validation: `checkpoint:M1-INTERNAL-MIRROR.json`
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0022 - lesson:LSN-0022

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0022
- Description: Verify an authoritative count must be derived once, never maintained by hand twice
- Implementation: `checkpoint:COUNTS.json`
- Test: `test:DerivedCountTests`
- Negative test: _none_
- Documentation: `file:.iacode/memory/LESSONS.md`
- Validation: `command:cmd-0005`
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0023 - lesson:LSN-0023

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0023
- Description: Verify a lesson must cite a source that actually records the finding it claims
- Implementation: `file:.iacode/memory/lessons.jsonl`
- Test: `test:LessonProvenanceTests`
- Negative test: _none_
- Documentation: `file:.iacode/memory/LESSONS.md`
- Validation: `file:.iacode/memory/LESSONS.md`
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0024 - lesson:LSN-0024

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0024
- Description: Verify a control is finished only when its positive path has been executed, not only its refusals
- Implementation: `file:scripts/development-ledger/gate0_red_team.py`
- Test: `test:test_a_valid_backup_passes_verification`, `test:test_readiness_is_ready_when_every_probe_succeeds`
- Negative test: _none_
- Documentation: `file:.iacode/memory/LESSONS.md`
- Validation: `checkpoint:M1-INTERNAL-RED-TEAM.json`
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0025 - lesson:LSN-0025

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0025
- Description: Verify a generic guardrail derives repository state instead of naming today's checkpoint
- Implementation: `file:.iacode/policies/gate-scope.json`
- Test: `test:test_the_scope_control_ignores_a_gate_that_has_already_run`
- Negative test: _none_
- Documentation: `file:.iacode/memory/LESSONS.md`
- Validation: `checkpoint:M1-INTERNAL-MIRROR.json`
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0026 - lesson:LSN-0026

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0026
- Description: Verify an adversarial battery without a null-mutation control proves nothing
- Implementation: `file:scripts/development-ledger/gate0_red_team.py`
- Test: `test:test_the_scope_control_detects_an_implementation`
- Negative test: _none_
- Documentation: `file:.iacode/memory/LESSONS.md`
- Validation: `checkpoint:M1-INTERNAL-RED-TEAM.json`
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0027 - lesson:LSN-0027

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0027
- Description: Verify a lesson's prose may record a residual limit but may never contradict its status
- Implementation: `file:.iacode/memory/lessons.jsonl`
- Test: `test:test_a_guarded_lesson_may_not_describe_itself_as_unguarded`
- Negative test: _none_
- Documentation: `file:.iacode/memory/LESSONS.md`
- Validation: `file:.iacode/memory/LESSONS.md`
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0028 - lesson:LSN-0028

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0028
- Description: Verify a configuration key that no code reads is a defect, not documentation
- Implementation: `file:apps/api/src/iacode_api/config.py`
- Test: `test:test_every_declared_key_is_read_somewhere`
- Negative test: _none_
- Documentation: `file:.iacode/memory/LESSONS.md`
- Validation: `file:.iacode/memory/LESSONS.md`
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0029 - lesson:LSN-0029

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0029
- Description: Verify a required protocol transition must never turn a mandatory gate red
- Implementation: `file:scripts/development-ledger/gate_transition_simulation.py`
- Test: `test:GateTransitionSimulationTests`
- Negative test: _none_
- Documentation: `file:.iacode/memory/LESSONS.md`
- Validation: `command:cmd-0005`
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0030 - lesson:LSN-0031

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0030
- Description: Verify an empty applicable set is not a missing required set, and a control must tell them apart
- Implementation: `file:scripts/development-ledger/m0_mirror_audit.py`
- Test: `test:MirrorApplicabilitySemanticsTests`
- Negative test: _none_
- Documentation: `file:.iacode/memory/LESSONS.md`
- Validation: `checkpoint:M1-INTERNAL-MIRROR.json`
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0031 - lesson:LSN-0032

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0031
- Description: Verify a control written while one Gate was the only Gate stops being a control when the next one starts
- Implementation: `file:.iacode/policies/gate-scope.json`, `file:scripts/development-ledger/policies.py`
- Test: `test:test_expected_set_names_the_gate_specification`, `test:test_assurance_scope_covers_the_runtime_source`, `test:test_declared_suites_are_discovered`
- Negative test: _none_
- Documentation: `file:.iacode/memory/LESSONS.md`
- Validation: `checkpoint:M1-INTERNAL-MIRROR.json`, `checkpoint:DECISIONS.md`
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0032 - lesson:LSN-0033

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0032
- Description: Verify a value bound in middleware is absent in the handlers that run outside it
- Implementation: `file:apps/api/src/iacode_api/errors.py`
- Test: `test:test_internal_error_still_carries_a_correlation_identifier`
- Negative test: _none_
- Documentation: `file:.iacode/memory/LESSONS.md`
- Validation: `checkpoint:M1-INTERNAL-RED-TEAM.json`
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0033 - lesson:LSN-0034

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0033
- Description: Verify re-deriving what the framework already computed diverges from the framework
- Implementation: `file:apps/api/src/iacode_api/observability/metrics.py`
- Test: `test:test_metrics_label_routes_by_template_not_by_url`, `test:test_the_api_instruments_reach_prometheus`
- Negative test: _none_
- Documentation: `file:.iacode/memory/LESSONS.md`
- Validation: `checkpoint:M1-INTERNAL-RED-TEAM.json`, `checkpoint:VERIFICATION-REPORT.json`
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0034 - lesson:LSN-0035

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0034
- Description: Verify captured subprocess output decoded or re-emitted with the platform codepage crashes the tool, not the work
- Implementation: `file:scripts/development-ledger/ledger_common.py`, `file:scripts/iacode/compose.py`
- Test: `test:test_no_capture_relies_on_the_platform_codepage`, `test:test_every_tool_that_re_emits_captured_output_configures_its_own_stream`, `test:test_the_rule_detects_a_capture_that_would_fail`
- Negative test: _none_
- Documentation: `file:.iacode/memory/LESSONS.md`
- Validation: `checkpoint:REWORK-LOG.jsonl`, `command:cmd-0005`
- Guardrail: `file:.iacode/memory/guardrails/registry.json`
