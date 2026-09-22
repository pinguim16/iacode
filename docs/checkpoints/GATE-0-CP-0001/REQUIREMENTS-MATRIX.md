# Requirements Matrix - GATE-0-CP-0001

Expected set derived by: `policies.expected_requirement_refs over docs/GATE-0-CHECKLIST.md, .iacode/policies/canonical-requirements.json, .iacode/policies/audit-registry.json and LESSON-PREFLIGHT.json`.

| ID | Anchor | Mandatory | Status | Requirement | Source |
|---|---|---|---|---|---|
| `REQ-0001` | `canonical:GATE-0#1.1` | yes | `COMPLETE` | A canonical, machine-readable requirement specification exists for this Gate and the registry mirrors it row for row. | docs/GATE-0-CHECKLIST.md row 1.1 |
| `REQ-0002` | `canonical:GATE-0#1.2` | yes | `COMPLETE` | The derived expected set names the specification of the Gate it describes instead of a fixed document. | docs/GATE-0-CHECKLIST.md row 1.2 |
| `REQ-0003` | `canonical:GATE-0#1.3` | yes | `COMPLETE` | The delivery-assurance scope covers the runtime source this Gate introduces, so a gate result becomes stale when the product changes. | docs/GATE-0-CHECKLIST.md row 1.3 |
| `REQ-0004` | `canonical:GATE-0#1.4` | yes | `COMPLETE` | The closed mandatory gate registry carries every executable gate this Gate introduces. | docs/GATE-0-CHECKLIST.md row 1.4 |
| `REQ-0005` | `canonical:GATE-0#1.5` | yes | `COMPLETE` | Every test suite this Gate introduces is declared canonically and is counted by the count derivation and resolvable as evidence. | docs/GATE-0-CHECKLIST.md row 1.5 |
| `REQ-0006` | `canonical:GATE-0#1.6` | yes | `COMPLETE` | The internal mirror audit judges the Gate it runs in rather than a Gate named in its own source. | docs/GATE-0-CHECKLIST.md row 1.6 |
| `REQ-0007` | `canonical:GATE-0#1.7` | yes | `COMPLETE` | The internal Red Team battery of this Gate is executable, scoped to the Foundation, and records a null-mutation control. | docs/GATE-0-CHECKLIST.md row 1.7 |
| `REQ-0008` | `canonical:GATE-0#2.1` | yes | `COMPLETE` | The repository carries the planned application, service, package and infrastructure directories. | docs/GATE-0-CHECKLIST.md row 2.1 |
| `REQ-0009` | `canonical:GATE-0#2.2` | yes | `COMPLETE` | A directory reserved for a later Gate says so and contains no implementation. | docs/GATE-0-CHECKLIST.md row 2.2 |
| `REQ-0010` | `canonical:GATE-0#2.3` | yes | `COMPLETE` | No later-Gate capability is implemented, simulated or faked in this Gate. | docs/GATE-0-CHECKLIST.md row 2.3 |
| `REQ-0011` | `canonical:GATE-0#3.1` | yes | `COMPLETE` | The backend is a real FastAPI application that starts reliably and fails loudly when it cannot. | docs/GATE-0-CHECKLIST.md row 3.1 |
| `REQ-0012` | `canonical:GATE-0#3.2` | yes | `COMPLETE` | Shutdown is graceful and releases every client the application opened. | docs/GATE-0-CHECKLIST.md row 3.2 |
| `REQ-0013` | `canonical:GATE-0#3.3` | yes | `COMPLETE` | Dependency lifecycle is explicit and held on the application, not in ambient mutable globals. | docs/GATE-0-CHECKLIST.md row 3.3 |
| `REQ-0014` | `canonical:GATE-0#3.4` | yes | `COMPLETE` | `GET /health` reports process liveness and does not depend on external dependencies to answer. | docs/GATE-0-CHECKLIST.md row 3.4 |
| `REQ-0015` | `canonical:GATE-0#3.5` | yes | `COMPLETE` | `GET /ready` probes PostgreSQL, Redis, MinIO and Temporal and refuses readiness when a mandatory dependency is unavailable. | docs/GATE-0-CHECKLIST.md row 3.5 |
| `REQ-0016` | `canonical:GATE-0#3.6` | yes | `COMPLETE` | `GET /version` reports the application version and build identity and exposes no secret. | docs/GATE-0-CHECKLIST.md row 3.6 |
| `REQ-0017` | `canonical:GATE-0#3.7` | yes | `COMPLETE` | The application exposes a Prometheus metrics endpoint with request, latency, status and dependency metrics. | docs/GATE-0-CHECKLIST.md row 3.7 |
| `REQ-0018` | `canonical:GATE-0#3.8` | yes | `COMPLETE` | OpenAPI documentation describes the Foundation endpoints and exposes no internal-only route. | docs/GATE-0-CHECKLIST.md row 3.8 |
| `REQ-0019` | `canonical:GATE-0#3.9` | yes | `COMPLETE` | CORS is configured explicitly from configuration, without a permissive wildcard, and allows the local frontend. | docs/GATE-0-CHECKLIST.md row 3.9 |
| `REQ-0020` | `canonical:GATE-0#4.1` | yes | `COMPLETE` | Configuration is typed, validated at load time and rejects an invalid or missing mandatory value. | docs/GATE-0-CHECKLIST.md row 4.1 |
| `REQ-0021` | `canonical:GATE-0#4.2` | yes | `COMPLETE` | Safe defaults, development configuration and test configuration are separated rather than conflated. | docs/GATE-0-CHECKLIST.md row 4.2 |
| `REQ-0022` | `canonical:GATE-0#4.3` | yes | `COMPLETE` | A committed example environment file documents every key and carries no real secret, and the real file is ignored by Git. | docs/GATE-0-CHECKLIST.md row 4.3 |
| `REQ-0023` | `canonical:GATE-0#4.4` | yes | `COMPLETE` | Secret values are redacted wherever configuration, errors or logs could expose them. | docs/GATE-0-CHECKLIST.md row 4.4 |
| `REQ-0024` | `canonical:GATE-0#4.5` | yes | `COMPLETE` | No secret is baked into an image, a compose file, a Dockerfile or a committed configuration file. | docs/GATE-0-CHECKLIST.md row 4.5 |
| `REQ-0025` | `canonical:GATE-0#5.1` | yes | `COMPLETE` | PostgreSQL runs locally from the compose stack at a pinned version with a persistent named volume. | docs/GATE-0-CHECKLIST.md row 5.1 |
| `REQ-0026` | `canonical:GATE-0#5.2` | yes | `COMPLETE` | The persistence layer is real, asynchronous and pooled, built on SQLAlchemy 2. | docs/GATE-0-CHECKLIST.md row 5.2 |
| `REQ-0027` | `canonical:GATE-0#5.3` | yes | `COMPLETE` | Alembic migrations run from zero against an empty database and produce the declared schema. | docs/GATE-0-CHECKLIST.md row 5.3 |
| `REQ-0028` | `canonical:GATE-0#5.4` | yes | `COMPLETE` | Starting against an already-migrated database neither fails nor recreates the schema. | docs/GATE-0-CHECKLIST.md row 5.4 |
| `REQ-0029` | `canonical:GATE-0#5.5` | yes | `COMPLETE` | A failed migration never produces a healthy readiness or a silent partial start. | docs/GATE-0-CHECKLIST.md row 5.5 |
| `REQ-0030` | `canonical:GATE-0#5.6` | yes | `COMPLETE` | The structural domain tables the later Gates build on exist, with their relationships and constraints. | docs/GATE-0-CHECKLIST.md row 5.6 |
| `REQ-0031` | `canonical:GATE-0#5.7` | yes | `COMPLETE` | Identifiers use one consistent strategy, UUIDv7, implemented and tested rather than assumed. | docs/GATE-0-CHECKLIST.md row 5.7 |
| `REQ-0032` | `canonical:GATE-0#5.8` | yes | `COMPLETE` | The common column convention is defined once and applied where it makes sense, not forced everywhere. | docs/GATE-0-CHECKLIST.md row 5.8 |
| `REQ-0033` | `canonical:GATE-0#5.9` | yes | `COMPLETE` | The pgvector position is decided, recorded, and — where the extension is enabled — migrated and tested. | docs/GATE-0-CHECKLIST.md row 5.9 |
| `REQ-0034` | `canonical:GATE-0#6.1` | yes | `COMPLETE` | Redis runs locally from the compose stack at a pinned version. | docs/GATE-0-CHECKLIST.md row 6.1 |
| `REQ-0035` | `canonical:GATE-0#6.2` | yes | `COMPLETE` | The backend holds a real Redis client whose availability the readiness probe verifies. | docs/GATE-0-CHECKLIST.md row 6.2 |
| `REQ-0036` | `canonical:GATE-0#6.3` | yes | `COMPLETE` | An integration test exercises a real Redis round trip against the running service. | docs/GATE-0-CHECKLIST.md row 6.3 |
| `REQ-0037` | `canonical:GATE-0#7.1` | yes | `COMPLETE` | MinIO runs locally from the compose stack at a pinned version with a persistent named volume. | docs/GATE-0-CHECKLIST.md row 7.1 |
| `REQ-0038` | `canonical:GATE-0#7.2` | yes | `COMPLETE` | The buckets the later Gates need are created by an idempotent bootstrap that is safe to re-run. | docs/GATE-0-CHECKLIST.md row 7.2 |
| `REQ-0039` | `canonical:GATE-0#7.3` | yes | `COMPLETE` | The readiness probe verifies real object-storage connectivity rather than a reachable port. | docs/GATE-0-CHECKLIST.md row 7.3 |
| `REQ-0040` | `canonical:GATE-0#7.4` | yes | `COMPLETE` | An integration test writes, reads and deletes a real object. | docs/GATE-0-CHECKLIST.md row 7.4 |
| `REQ-0041` | `canonical:GATE-0#8.1` | yes | `COMPLETE` | Temporal runs locally from the compose stack at a pinned version with its persistent state. | docs/GATE-0-CHECKLIST.md row 8.1 |
| `REQ-0042` | `canonical:GATE-0#8.2` | yes | `COMPLETE` | An IACode worker connects to Temporal and polls its task queue as a first-class service. | docs/GATE-0-CHECKLIST.md row 8.2 |
| `REQ-0043` | `canonical:GATE-0#8.3` | yes | `COMPLETE` | The readiness probe verifies real Temporal connectivity. | docs/GATE-0-CHECKLIST.md row 8.3 |
| `REQ-0044` | `canonical:GATE-0#8.4` | yes | `COMPLETE` | A minimal real workflow and activity execute end to end through the worker and return an observable result. | docs/GATE-0-CHECKLIST.md row 8.4 |
| `REQ-0045` | `canonical:GATE-0#8.5` | yes | `COMPLETE` | No agent workflow, tool call or orchestration of a later Gate is implemented here. | docs/GATE-0-CHECKLIST.md row 8.5 |
| `REQ-0046` | `canonical:GATE-0#9.1` | yes | `COMPLETE` | A real Angular application exists and builds reproducibly with pinned dependencies. | docs/GATE-0-CHECKLIST.md row 9.1 |
| `REQ-0047` | `canonical:GATE-0#9.2` | yes | `COMPLETE` | The Foundation page identifies IACode and renders the live backend health, readiness and version. | docs/GATE-0-CHECKLIST.md row 9.2 |
| `REQ-0048` | `canonical:GATE-0#9.3` | yes | `COMPLETE` | The API base address is centralized in configuration, carries no secret and is not hardcoded across the code. | docs/GATE-0-CHECKLIST.md row 9.3 |
| `REQ-0049` | `canonical:GATE-0#9.4` | yes | `COMPLETE` | Frontend unit tests run headless and are part of the verification command. | docs/GATE-0-CHECKLIST.md row 9.4 |
| `REQ-0050` | `canonical:GATE-0#10.1` | yes | `COMPLETE` | Every image builds from a pinned base, runs as a non-root user where practical, carries no secret and excludes build waste. | docs/GATE-0-CHECKLIST.md row 10.1 |
| `REQ-0051` | `canonical:GATE-0#10.2` | yes | `COMPLETE` | The compose stack declares every Foundation service and nothing that the Foundation does not need. | docs/GATE-0-CHECKLIST.md row 10.2 |
| `REQ-0052` | `canonical:GATE-0#10.3` | yes | `COMPLETE` | Every service that can report health has a real healthcheck, and start-up ordering uses those conditions instead of fixed sleeps. | docs/GATE-0-CHECKLIST.md row 10.3 |
| `REQ-0053` | `canonical:GATE-0#10.4` | yes | `COMPLETE` | Restart behaviour is declared, and the stack recovers its state after a restart. | docs/GATE-0-CHECKLIST.md row 10.4 |
| `REQ-0054` | `canonical:GATE-0#10.5` | yes | `COMPLETE` | Durable state lives in named volumes that are documented, not in the container filesystem. | docs/GATE-0-CHECKLIST.md row 10.5 |
| `REQ-0055` | `canonical:GATE-0#10.6` | yes | `COMPLETE` | The stack uses an explicit network and publishes only the ports local development needs, from configuration. | docs/GATE-0-CHECKLIST.md row 10.6 |
| `REQ-0056` | `canonical:GATE-0#11.1` | yes | `COMPLETE` | The backend and the worker emit structured logs carrying the contract fields, absent rather than invented when there is no context. | docs/GATE-0-CHECKLIST.md row 11.1 |
| `REQ-0057` | `canonical:GATE-0#11.2` | yes | `COMPLETE` | Every HTTP request carries a correlation identifier that is accepted or generated, propagated, returned and logged. | docs/GATE-0-CHECKLIST.md row 11.2 |
| `REQ-0058` | `canonical:GATE-0#11.3` | yes | `COMPLETE` | The API error contract is explicit, extensible and never returns a traceback or internal detail to the client while keeping it in the logs. | docs/GATE-0-CHECKLIST.md row 11.3 |
| `REQ-0059` | `canonical:GATE-0#11.4` | yes | `COMPLETE` | Prometheus is provisioned and scrapes the API and the worker. | docs/GATE-0-CHECKLIST.md row 11.4 |
| `REQ-0060` | `canonical:GATE-0#11.5` | yes | `COMPLETE` | Grafana starts with the Prometheus datasource and a Foundation dashboard provisioned automatically. | docs/GATE-0-CHECKLIST.md row 11.5 |
| `REQ-0061` | `canonical:GATE-0#11.6` | yes | `COMPLETE` | The OpenTelemetry position for the Foundation is decided and recorded rather than left implicit. | docs/GATE-0-CHECKLIST.md row 11.6 |
| `REQ-0062` | `canonical:GATE-0#12.1` | yes | `COMPLETE` | A reproducible backup produces a PostgreSQL dump and the object-storage contents, with a correct exit code and a log, and fails loudly on partial failure. | docs/GATE-0-CHECKLIST.md row 12.1 |
| `REQ-0063` | `canonical:GATE-0#12.2` | yes | `COMPLETE` | The backup never writes a credential into its artifacts or its log. | docs/GATE-0-CHECKLIST.md row 12.2 |
| `REQ-0064` | `canonical:GATE-0#12.3` | yes | `COMPLETE` | A restore reconstructs the database and the object storage from a backup produced by this tooling. | docs/GATE-0-CHECKLIST.md row 12.3 |
| `REQ-0065` | `canonical:GATE-0#12.4` | yes | `COMPLETE` | Backup and restore are verified end to end with synthetic data in a disposable environment, and the restored data is checked rather than assumed. | docs/GATE-0-CHECKLIST.md row 12.4 |
| `REQ-0066` | `canonical:GATE-0#12.5` | yes | `COMPLETE` | Backup retention for the Foundation is either implemented simply or documented as out of scope, with no silent gap. | docs/GATE-0-CHECKLIST.md row 12.5 |
| `REQ-0067` | `canonical:GATE-0#13.1` | yes | `COMPLETE` | One documented command runs the whole Gate verification and works on the primary Windows environment as well as on POSIX. | docs/GATE-0-CHECKLIST.md row 13.1 |
| `REQ-0068` | `canonical:GATE-0#13.2` | yes | `COMPLETE` | The backend suite covers health, readiness, version, configuration, redaction, error handling, correlation, database, cache, object storage, workflows and migrations. | docs/GATE-0-CHECKLIST.md row 13.2 |
| `REQ-0069` | `canonical:GATE-0#13.3` | yes | `COMPLETE` | The frontend suite covers bootstrap, the status rendering and the API configuration, and the production build succeeds. | docs/GATE-0-CHECKLIST.md row 13.3 |
| `REQ-0070` | `canonical:GATE-0#13.4` | yes | `COMPLETE` | Infrastructure smoke validation proves that our own configuration of each service is operational. | docs/GATE-0-CHECKLIST.md row 13.4 |
| `REQ-0071` | `canonical:GATE-0#13.5` | yes | `COMPLETE` | A fresh installation with no previous volume reaches a ready stack, a migrated database, a reachable frontend and a green smoke check. | docs/GATE-0-CHECKLIST.md row 13.5 |
| `REQ-0072` | `canonical:GATE-0#13.6` | yes | `COMPLETE` | A restart of the running stack returns every service to ready with its data intact. | docs/GATE-0-CHECKLIST.md row 13.6 |
| `REQ-0073` | `canonical:GATE-0#13.7` | yes | `COMPLETE` | With a mandatory dependency stopped, liveness may stay up while readiness fails correctly, and readiness recovers when the dependency returns. | docs/GATE-0-CHECKLIST.md row 13.7 |
| `REQ-0074` | `canonical:GATE-0#13.8` | yes | `COMPLETE` | Lint and static analysis run over the backend, the worker and the frontend and are green. | docs/GATE-0-CHECKLIST.md row 13.8 |
| `REQ-0075` | `canonical:GATE-0#13.9` | yes | `COMPLETE` | A dependency vulnerability scan is executed, or its absence is justified, and relevant Critical and High findings block the Gate. | docs/GATE-0-CHECKLIST.md row 13.9 |
| `REQ-0076` | `canonical:GATE-0#14.1` | yes | `COMPLETE` | The repository entry documentation describes what exists after this Gate and how to run it. | docs/GATE-0-CHECKLIST.md row 14.1 |
| `REQ-0077` | `canonical:GATE-0#14.2` | yes | `COMPLETE` | The architecture document describes the Foundation runtime, its boundaries and what is deliberately absent. | docs/GATE-0-CHECKLIST.md row 14.2 |
| `REQ-0078` | `canonical:GATE-0#14.3` | yes | `COMPLETE` | A development guide explains the local workflow end to end for a new machine. | docs/GATE-0-CHECKLIST.md row 14.3 |
| `REQ-0079` | `canonical:GATE-0#14.4` | yes | `COMPLETE` | An operational runbook documents start, stop, rebuild, reset, migrate, health, readiness, Grafana and the smoke checks. | docs/GATE-0-CHECKLIST.md row 14.4 |
| `REQ-0080` | `canonical:GATE-0#14.5` | yes | `COMPLETE` | A backup and restore runbook documents the full procedure and its verification. | docs/GATE-0-CHECKLIST.md row 14.5 |
| `REQ-0081` | `canonical:GATE-0#14.6` | yes | `COMPLETE` | The pinned versions of every runtime, service and principal library are recorded in one place. | docs/GATE-0-CHECKLIST.md row 14.6 |
| `REQ-0082` | `canonical:GATE-0#14.7` | yes | `COMPLETE` | Every structural decision of this Gate that is not already recorded becomes an ADR, and no ADR duplicates an existing decision. | docs/GATE-0-CHECKLIST.md row 14.7 |
| `REQ-0083` | `canonical:GATE-0#15.1` | yes | `COMPLETE` | The entry contract and the plan describe the current Gate and its status truthfully. | docs/GATE-0-CHECKLIST.md row 15.1 |
| `REQ-0084` | `canonical:GATE-0#15.2` | yes | `COMPLETE` | The Gate produces a retrospective from the canonical template. | docs/GATE-0-CHECKLIST.md row 15.2 |
| `LESSON-REQ-0001` | `lesson:LSN-0001` | yes | `COMPLETE` | Verify checkpoint validation must succeed from a detached checkout of the checkpoint tag | LESSON-PREFLIGHT.json LESSON-REQ-0001 |
| `LESSON-REQ-0002` | `lesson:LSN-0002` | yes | `COMPLETE` | Verify a file inventory must be recomputed from the repository, never trusted as an assertion | LESSON-PREFLIGHT.json LESSON-REQ-0002 |
| `LESSON-REQ-0003` | `lesson:LSN-0003` | yes | `COMPLETE` | Verify every operation attempt must be auditable, including a refusal decided before execution | LESSON-PREFLIGHT.json LESSON-REQ-0003 |
| `LESSON-REQ-0004` | `lesson:LSN-0004` | yes | `COMPLETE` | Verify a checkpoint may never claim readiness while it also claims to be blocked | LESSON-PREFLIGHT.json LESSON-REQ-0004 |
| `LESSON-REQ-0005` | `lesson:LSN-0005` | yes | `COMPLETE` | Verify a PASS requires evidence that can be executed or resolved, not a statement | LESSON-PREFLIGHT.json LESSON-REQ-0005 |
| `LESSON-REQ-0006` | `lesson:LSN-0006` | yes | `COMPLETE` | Verify the repository must be self-contained; a specification may not live outside it | LESSON-PREFLIGHT.json LESSON-REQ-0006 |
| `LESSON-REQ-0007` | `lesson:LSN-0007` | yes | `COMPLETE` | Verify independent validation cannot be declared by the run that did the work | LESSON-PREFLIGHT.json LESSON-REQ-0007 |
| `LESSON-REQ-0008` | `lesson:LSN-0008` | yes | `COMPLETE` | Verify requirement completeness must be total and evidence-backed before handoff | LESSON-PREFLIGHT.json LESSON-REQ-0008 |
| `LESSON-REQ-0009` | `lesson:LSN-0009` | yes | `COMPLETE` | Verify a red gate requires rework, never a waiver, and never a weakened check | LESSON-PREFLIGHT.json LESSON-REQ-0009 |
| `LESSON-REQ-0010` | `lesson:LSN-0010` | yes | `COMPLETE` | Verify a recorded command must carry runtime, working directory, commit and purpose to be replayable | LESSON-PREFLIGHT.json LESSON-REQ-0010 |
| `LESSON-REQ-0011` | `lesson:LSN-0011` | yes | `COMPLETE` | Verify a control over a checkpoint's own evidence must be scoped to the moment it matters | LESSON-PREFLIGHT.json LESSON-REQ-0011 |
| `LESSON-REQ-0012` | `lesson:LSN-0012` | yes | `COMPLETE` | Verify sealed checkpoints and their tags are immutable, and tooling must keep validating them | LESSON-PREFLIGHT.json LESSON-REQ-0012 |
| `LESSON-REQ-0013` | `lesson:LSN-0013` | no | `COMPLETE` | Verify an installed capability must be detected by resolved path, not by a bare command lookup | LESSON-PREFLIGHT.json LESSON-REQ-0013 |
| `LESSON-REQ-0014` | `lesson:LSN-0014` | yes | `COMPLETE` | Verify evidence must be recorded as it happens, not reconstructed at the end of a run | LESSON-PREFLIGHT.json LESSON-REQ-0014 |
| `LESSON-REQ-0015` | `lesson:LSN-0015` | yes | `COMPLETE` | Verify every positive terminal status needs one shared promotion invariant | LESSON-PREFLIGHT.json LESSON-REQ-0015 |
| `LESSON-REQ-0016` | `lesson:LSN-0016` | yes | `COMPLETE` | Verify a mandatory set must be closed by policy, never chosen by the caller | LESSON-PREFLIGHT.json LESSON-REQ-0016 |
| `LESSON-REQ-0017` | `lesson:LSN-0017` | yes | `COMPLETE` | Verify a completeness denominator must come from a source the delivery does not own | LESSON-PREFLIGHT.json LESSON-REQ-0017 |
| `LESSON-REQ-0018` | `lesson:LSN-0018` | yes | `COMPLETE` | Verify a structured reference must be resolved, not merely well typed | LESSON-PREFLIGHT.json LESSON-REQ-0018 |
| `LESSON-REQ-0019` | `lesson:LSN-0019` | yes | `COMPLETE` | Verify a derived artifact must carry a fingerprint of the inputs that produced it | LESSON-PREFLIGHT.json LESSON-REQ-0019 |
| `LESSON-REQ-0020` | `lesson:LSN-0020` | yes | `COMPLETE` | Verify evidence produced from a dirty tree needs immutable input identity | LESSON-PREFLIGHT.json LESSON-REQ-0020 |
| `LESSON-REQ-0021` | `lesson:LSN-0021` | yes | `COMPLETE` | Verify sealed history needs an anchor outside the content it describes | LESSON-PREFLIGHT.json LESSON-REQ-0021 |
| `LESSON-REQ-0022` | `lesson:LSN-0022` | yes | `COMPLETE` | Verify an authoritative count must be derived once, never maintained by hand twice | LESSON-PREFLIGHT.json LESSON-REQ-0022 |
| `LESSON-REQ-0023` | `lesson:LSN-0023` | yes | `COMPLETE` | Verify a lesson must cite a source that actually records the finding it claims | LESSON-PREFLIGHT.json LESSON-REQ-0023 |
| `LESSON-REQ-0024` | `lesson:LSN-0024` | yes | `COMPLETE` | Verify a control is finished only when its positive path has been executed, not only its refusals | LESSON-PREFLIGHT.json LESSON-REQ-0024 |
| `LESSON-REQ-0025` | `lesson:LSN-0025` | yes | `COMPLETE` | Verify a generic guardrail derives repository state instead of naming today's checkpoint | LESSON-PREFLIGHT.json LESSON-REQ-0025 |
| `LESSON-REQ-0026` | `lesson:LSN-0026` | yes | `COMPLETE` | Verify an adversarial battery without a null-mutation control proves nothing | LESSON-PREFLIGHT.json LESSON-REQ-0026 |
| `LESSON-REQ-0027` | `lesson:LSN-0027` | yes | `COMPLETE` | Verify a lesson's prose may record a residual limit but may never contradict its status | LESSON-PREFLIGHT.json LESSON-REQ-0027 |
| `LESSON-REQ-0028` | `lesson:LSN-0028` | yes | `COMPLETE` | Verify a configuration key that no code reads is a defect, not documentation | LESSON-PREFLIGHT.json LESSON-REQ-0028 |
| `LESSON-REQ-0029` | `lesson:LSN-0029` | yes | `COMPLETE` | Verify a required protocol transition must never turn a mandatory gate red | LESSON-PREFLIGHT.json LESSON-REQ-0029 |
| `LESSON-REQ-0030` | `lesson:LSN-0031` | yes | `COMPLETE` | Verify an empty applicable set is not a missing required set, and a control must tell them apart | LESSON-PREFLIGHT.json LESSON-REQ-0030 |
| `LESSON-REQ-0031` | `lesson:LSN-0032` | yes | `COMPLETE` | Verify a control written while one Gate was the only Gate stops being a control when the next one starts | LESSON-PREFLIGHT.json LESSON-REQ-0031 |
| `LESSON-REQ-0032` | `lesson:LSN-0033` | yes | `COMPLETE` | Verify a value bound in middleware is absent in the handlers that run outside it | LESSON-PREFLIGHT.json LESSON-REQ-0032 |
| `LESSON-REQ-0033` | `lesson:LSN-0034` | yes | `COMPLETE` | Verify re-deriving what the framework already computed diverges from the framework | LESSON-PREFLIGHT.json LESSON-REQ-0033 |
| `LESSON-REQ-0034` | `lesson:LSN-0035` | yes | `COMPLETE` | Verify captured subprocess output decoded or re-emitted with the platform codepage crashes the tool, not the work | LESSON-PREFLIGHT.json LESSON-REQ-0034 |
