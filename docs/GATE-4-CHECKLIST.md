# GATE 4 — Quality Engine Checklist

This is the canonical specification of `GATE 4 — QUALITY ENGINE`. It is parsed at every delivery
run by `policies.canonical_requirements` and mirrored, row for row, by
`.iacode/policies/canonical-requirements.json`. The delivery cannot reduce this set.

The objective is **executable, reproducible quality evidence**: a project profile selects a closed
quality policy, a plan freezes the checks and inputs, every command runs in the Gate 3 sandbox, and
an evidence-backed verdict is derived from the stored results. A claim, a caller-selected
denominator, mutable evidence, or a command run on the host can never become `PASS`.

```text
Project snapshot → Project profile → Quality policy → Quality plan
  → sandbox runners → results/findings/evidence → derived verdict
```

The engine is project-agnostic. Initial support covers Python, Node, TypeScript, Angular, Java with
Maven, and Java with Gradle. `GATE 4` is the first Gate of milestone `M2`; this implementing run
ends at `READY_FOR_REVIEW` and a later run owns the Gate verdict.

## 1. Canonical scope and delivery controls

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 1.1 | This checklist is the canonical, machine-readable requirement source for the Gate and its registry mirror has exactly the same ordered rows. | `docs/GATE-4-CHECKLIST.md`, `.iacode/policies/canonical-requirements.json` | `Gate4CanonicalSpecificationTests`. |
| 1.2 | The evaluator reservation is consumed by this Gate while every later-Gate reservation remains enforced. | `.iacode/policies/gate-scope.json`, `services/evaluator/` | `Gate4ScopeTests`. |
| 1.3 | The closed mandatory gate registry includes an evaluator gate that builds every image it executes before measuring it. | `.iacode/policies/quality-gates.json`, `scripts/iacode/gates/evaluator_tests.py` | `Gate4MandatoryGateTests`. |
| 1.4 | The evaluator suite is canonical, counted, and available to evidence resolution. | `.iacode/policies/test-suites.json` | `Gate4TestSuiteRegistryTests`; derived `COUNTS.json`. |
| 1.5 | Gate 4 introduces no held-out model evaluation capability reserved for Gate 20 and no CLI or VS Code capability reserved for Gate 5. | `.iacode/policies/gate-scope.json` | `Gate4ScopeTests`. |
| 1.6 | Generated review archives are permanently excluded from Git, while their validation result and digest remain checkpoint evidence. | `.gitignore`, `scripts/development-ledger/review_bundle.py` | `ReviewBundleTests`; staged secret scan. |

## 2. Versioned quality contracts

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 2.1 | Versioned contracts exist for `QualityPlan`, `QualityCheck`, `QualityRun`, `QualityResult`, `QualityFinding`, `QualityEvidence`, `QualityPolicy`, and `QualityVerdict`. | `packages/contracts/src/iacode_contracts/quality.py` | `QualityContractTests`. |
| 2.2 | Contract vocabularies are closed and reject missing fields, extra fields, wrong types, invalid values, duplicate identifiers, and unsupported versions with distinct reasons. | `packages/contracts/src/iacode_contracts/quality.py` | `QualityContractTests`; `test_unknown_fields_and_unsupported_versions_are_refused`. |
| 2.3 | Every contract round-trips without losing identity, ordering, timestamps, digests, policy references, sandbox references, or artifact references. | `packages/contracts/src/iacode_contracts/quality.py` | `test_contracts_round_trip_without_losing_the_frozen_plan`. |
| 2.4 | Every reusable artifact defaults to `trainingAllowed=false`; a quality contract carries no credential, secret, chain-of-thought, or whole environment. | `packages/contracts/src/iacode_contracts/quality.py` | `QualityRightsTests`; `QualitySecretContainmentTests`. |
| 2.5 | Payload sizes are bounded as the receiver measures them, and oversized plans, output summaries, findings, and evidence metadata are refused before persistence. | `packages/contracts/src/iacode_contracts/quality.py`, `services/evaluator/src/iacode_evaluator/limits.py` | `QualityLimitTests`. |

## 3. Project profile and detection

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 3.1 | A project profile records the detected stacks, manifests, workspace root, configuration source, confidence, and unresolved ambiguity without depending on IACode-specific paths. | `services/evaluator/src/iacode_evaluator/projects.py` | `ProjectProfileTests`. |
| 3.2 | Detection recognizes Python, Node, TypeScript, Angular, Maven, and Gradle from repository evidence and supports mixed projects. | `services/evaluator/src/iacode_evaluator/projects.py` | `ProjectProfileTests`; six stack fixtures. |
| 3.3 | Detection never executes project code, follows no symlink outside the snapshot, ignores generated/vendor directories, and reads only bounded manifest content. | `services/evaluator/src/iacode_evaluator/projects.py` | `ProjectDetectionSecurityTests`. |
| 3.4 | Ambiguous or unknown toolchains produce an explicit unsupported/ambiguous result and never an invented stack or a false `PASS`. | `services/evaluator/src/iacode_evaluator/projects.py` | `test_unknown_and_ambiguous_projects_are_explicit`. |
| 3.5 | A versioned project configuration may select declared checks and commands but cannot select an image, mount, network, resource bound, verdict, or undeclared runner. | `iacode-quality.json`, `services/evaluator/src/iacode_evaluator/configuration.py` | `QualityConfigurationTests`. |
| 3.6 | The same source code onboards Python, Java, and TypeScript/Node fixtures through profiles rather than repository-specific branches. | `services/evaluator/tests/fixtures/` | `ProjectAgnosticScenarioTests`. |

## 4. Canonical quality policy

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 4.1 | One canonical policy registry declares profiles, runners, mandatory checks, applicability, timeouts, output limits, evidence requirements, and verdict rules. | `.iacode/policies/quality-policy.json` | `QualityPolicyTests`. |
| 4.2 | Unknown policy keys, runner names, check kinds, result states, evidence kinds, or verdict rules are refused when policy loads. | `services/evaluator/src/iacode_evaluator/policy.py` | `QualityPolicyTests`. |
| 4.3 | The requested project configuration may add checks or lower limits but cannot remove a mandatory check, raise a limit, weaken a threshold, or alter a verdict rule. | `services/evaluator/src/iacode_evaluator/policy.py` | `test_configuration_can_only_add_declared_checks_or_lower_a_limit`. |
| 4.4 | Applicability is derived from the project profile: an empty applicable set is justified `NOT_APPLICABLE`, while a missing required set is `FAIL`. | `services/evaluator/src/iacode_evaluator/policy.py` | `test_unit_checks_are_not_applicable_without_test_sources`; `test_an_empty_applicable_set_is_not_a_vacuous_pass`. |
| 4.5 | Every policy key has an implementation consumer, and the policy and its schema are content-addressed inputs to every plan. | `.iacode/policies/quality-policy.json`, `.iacode/schemas/quality-policy.schema.json` | `QualityPolicyCoverageTests`. |

## 5. Deterministic quality planning

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 5.1 | Planning freezes the project snapshot checksum, profile, policy digest, ordered checks, commands, runner images, limits, and environment before execution begins. | `services/evaluator/src/iacode_evaluator/planner.py` | `QualityPlannerTests`. |
| 5.2 | Plan identity is a deterministic digest of canonical content; equal inputs produce the same plan and any material input change produces a different plan. | `services/evaluator/src/iacode_evaluator/planner.py` | `test_equal_inputs_make_the_same_plan_identity`. |
| 5.3 | Check identifiers are unique, stable, and independent of execution order; dependencies form an acyclic graph and unknown dependencies are refused. | `services/evaluator/src/iacode_evaluator/planner.py` | `QualityPlannerTests`. |
| 5.4 | A plan cannot carry a caller-authored expected verdict, result, evidence digest, sandbox result, or hidden command. | `services/evaluator/src/iacode_evaluator/planner.py` | `test_a_request_cannot_smuggle_execution_or_a_verdict`. |
| 5.5 | The plan exposes why every check is mandatory, optional, or not applicable and identifies the policy rule that decided it. | `services/evaluator/src/iacode_evaluator/planner.py` | `test_plan_freezes_commands_policy_limits_and_reasons`. |

## 6. Runner registry and check kinds

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 6.1 | A closed runner registry maps declared runner identifiers to structured sandbox command requests; unknown identifiers never fall back to a shell command. | `services/evaluator/src/iacode_evaluator/runners.py` | `RunnerRegistryTests`. |
| 6.2 | Initial check kinds cover build, unit, integration, lint, static analysis, dependency/security, secret scan, configured coverage, applicable migration checks, and diff integrity. | `.iacode/policies/quality-policy.json`, `services/evaluator/src/iacode_evaluator/runners.py` | `QualityCheckKindTests`. |
| 6.3 | Commands are argument vectors or policy-owned command text, never concatenated from untrusted project values, and every working directory resolves within the snapshot. | `services/evaluator/src/iacode_evaluator/runners.py` | `RunnerSecurityTests`. |
| 6.4 | A runner normalizes exit code, timeout, denial, cancellation, truncation, duration, sandbox identity, and artifacts without inventing an exit code for work that never started. | `services/evaluator/src/iacode_evaluator/runners.py` | `QualityRunnerResultTests`. |
| 6.5 | Required checks execute despite an earlier failure unless their declared dependency makes execution impossible; every skipped check records the exact dependency reason. | `services/evaluator/src/iacode_evaluator/engine.py` | `test_one_failure_does_not_hide_independent_results`. |
| 6.6 | A cancelled or timed-out run reaches one terminal state, records the reason before the state, and leaves no running check or sandbox session. | `services/evaluator/src/iacode_evaluator/engine.py` | `QualityCancellationTests`; live scenario. |

## 7. Sandbox-only execution boundary

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 7.1 | Every project command is dispatched through the Gate 3 sandbox task queue; the evaluator, API, orchestrator, and host never execute a project command. | `services/evaluator/src/iacode_evaluator/executor.py` | `QualityExecutionBoundaryTests`; live sandbox proof. |
| 7.2 | Only the sandbox service has the container engine socket, and the evaluator service has no host mount, project bind mount, credential, or engine access. | `infra/compose/docker-compose.yml` | `QualityInfrastructureBoundaryTests`. |
| 7.3 | The executor origin is frozen as `EVALUATOR` when a quality check is created; a result from another origin is refused before storage. | `services/evaluator/src/iacode_evaluator/executor.py`, `packages/contracts/src/iacode_contracts/quality.py` | `QualityResultOriginTests`. |
| 7.4 | The snapshot, policy, image, resources, network, mounts, and limits cannot be changed by an executing check or its project. | `services/evaluator/src/iacode_evaluator/executor.py`, `.iacode/policies/sandbox-policy.json` | `QualitySandboxPolicyTests`. |
| 7.5 | A host sentinel and host process observation prove that passing and failing fixtures execute inside the sandbox and cause no host side effect. | `scripts/iacode/scenarios/quality_engine_e2e.py` | Recorded functional acceptance; `QualityScenarioTests`. |

## 8. Initial stack support

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 8.1 | Python projects have policy-owned runners for build/package validation, unit/integration tests, lint/static checks, dependency/security, secret, configured coverage, migration, and diff integrity as applicable. | `.iacode/policies/quality-policy.json` | Python passing and failing fixture results. |
| 8.2 | Node and TypeScript projects have policy-owned runners for install integrity, build, unit/integration tests, lint/static checks, dependency/security, secret, configured coverage, migration, and diff integrity as applicable. | `.iacode/policies/quality-policy.json` | Node and TypeScript fixture results. |
| 8.3 | Angular projects have policy-owned runners for production build, unit tests, lint/static checks, dependency/security, secret, configured coverage, and diff integrity. | `.iacode/policies/quality-policy.json` | Angular fixture results. |
| 8.4 | Maven projects have policy-owned runners for package, unit/integration tests, static checks, dependency/security, secret, configured coverage, migration, and diff integrity as applicable. | `.iacode/policies/quality-policy.json` | Maven fixture results. |
| 8.5 | Gradle projects have policy-owned runners for build, unit/integration tests, static checks, dependency/security, secret, configured coverage, migration, and diff integrity as applicable. | `.iacode/policies/quality-policy.json` | Gradle fixture results. |
| 8.6 | Sandbox image profiles are extensible and content-addressed; a missing or stale required image is a recorded failure and never silently replaced. | `services/sandbox/images/`, `.iacode/policies/sandbox-policy.json` | `QualityImageProfileTests`. |
| 8.7 | Dependency installation and checks have no internet access; lockfiles and prebuilt image toolchains decide what can execute reproducibly. | `.iacode/policies/sandbox-policy.json`, `services/sandbox/images/` | `QualityNetworkIsolationTests`. |

## 9. Evidence store and immutability

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 9.1 | Quality evidence uses the existing artifact store and records a content digest, byte size, media type, producer, source inputs, creation time, retention class, and rights. | `services/evaluator/src/iacode_evaluator/evidence.py` | `QualityEvidenceTests`; integration test against MinIO. |
| 9.2 | Evidence is content-addressed and immutable: a digest collision with different bytes, overwrite, rename, or deletion through the evaluator is refused. | `services/evaluator/src/iacode_evaluator/evidence.py` | `test_evidence_tampering_missing_bytes_and_metadata_conflicts_fail`. |
| 9.3 | A stored evidence reference is resolved and re-hashed before it can support a verdict; missing, truncated-without-artifact, or digest-mismatched evidence fails the run. | `services/evaluator/src/iacode_evaluator/evidence.py` | `QualityEvidenceResolutionTests`. |
| 9.4 | Inline summaries are bounded and secret-redacted; complete output is an artifact, never a database field, API response, metric label, or log record. | `services/evaluator/src/iacode_evaluator/evidence.py` | `QualitySecretContainmentTests`. |
| 9.5 | Evidence reproduction replays the frozen plan against the same snapshot and policy, records a new run, and compares result/evidence digests without rewriting the original. | `services/evaluator/src/iacode_evaluator/reproduce.py` | `QualityReproductionTests`; live reproduction report. |

## 10. Results, findings, and verdict rules

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 10.1 | Each check produces exactly one terminal result and zero or more typed findings linked to resolvable evidence. | `services/evaluator/src/iacode_evaluator/verdict.py` | `QualityVerdictTests`. |
| 10.2 | A mandatory failure, denial, timeout, cancellation, execution error, missing result, unresolved evidence, stale input, or incomplete check set makes the verdict `FAIL`. | `services/evaluator/src/iacode_evaluator/verdict.py` | `FalsePassRejectionTests`. |
| 10.3 | `PASS` requires the exact applicable mandatory set, every result successful, every required evidence reference resolved, and every configured threshold satisfied. | `services/evaluator/src/iacode_evaluator/verdict.py` | `FalsePassRejectionTests`; positive simulation. |
| 10.4 | Coverage is evaluated only when configured; below-threshold or unreadable coverage fails, while legitimately unconfigured coverage is justified `NOT_APPLICABLE` and never counted as `PASS`. | `services/evaluator/src/iacode_evaluator/verdict.py` | `CoverageVerdictTests`. |
| 10.5 | Severity, category, location, fingerprint, message, check identity, and evidence identify a finding; equal findings deduplicate deterministically without hiding recurrence. | `services/evaluator/src/iacode_evaluator/findings.py` | `QualityFindingTests`. |
| 10.6 | The verdict is a pure derivation from the frozen policy, plan, results, and resolved evidence; no API, runner, database row, or caller may submit it. | `services/evaluator/src/iacode_evaluator/verdict.py` | `test_complete_resolved_success_is_the_only_pass`; `test_a_request_cannot_smuggle_execution_or_a_verdict`. |
| 10.7 | Re-deriving a stored verdict must produce the same value and digest; disagreement marks the run invalid and never overwrites history. | `services/evaluator/src/iacode_evaluator/verdict.py` | `test_a_stored_verdict_is_rederived_not_overwritten`. |

## 11. Persistence and migration

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 11.1 | Relational persistence records quality plans, runs, checks, results, findings, evidence references, verdicts, and append-only run events with foreign keys and closed status constraints. | `packages/persistence/src/iacode_persistence/models.py`, `apps/api/migrations/versions/0006_quality_engine.py` | `QualityMigrationTests`; `QualityStoreTests`. |
| 11.2 | Plan content, result content, and verdict content are immutable after insertion; lifecycle updates may change only the declared run state and timestamps. | `services/evaluator/src/iacode_evaluator/store.py` | `QualityStoreImmutabilityTests`. |
| 11.3 | Idempotency keys and uniqueness constraints make duplicate create, dispatch, callback, event, and verdict operations return the recorded fact rather than create a second one. | `services/evaluator/src/iacode_evaluator/store.py` | `QualityIdempotencyTests`. |
| 11.4 | The event that explains a state is committed before the state a reader may act on, including every terminal transition. | `services/evaluator/src/iacode_evaluator/store.py` | `test_event_is_visible_before_the_transitioned_state`. |
| 11.5 | Migration `0006` upgrades from zero and from `0005`, downgrades cleanly, and leaves no Alembic autogenerate diff. | `apps/api/migrations/versions/0006_quality_engine.py` | Recorded migration reversibility and autogenerate checks. |
| 11.6 | No quality table stores a credential, full command output, host environment, or training eligibility defaulting to true. | `packages/persistence/src/iacode_persistence/models.py` | `QualityPersistenceSecurityTests`. |

## 12. Durable run lifecycle

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 12.1 | A durable workflow plans, starts, executes, cancels, resumes, reproduces, and finishes a quality run with a queryable event history. | `services/evaluator/src/iacode_evaluator/workflow.py`, `services/evaluator/src/iacode_evaluator/worker.py` | `QualityWorkflowTests`; live restart scenario. |
| 12.2 | A worker restart during a check preserves the run identity and either receives the owned result or records an explicit failure; it never silently passes or duplicates execution. | `scripts/iacode/scenarios/quality_engine_e2e.py` | Recorded recovery scenario. |
| 12.3 | Cancellation is idempotent, propagates to the sandbox, refuses late results, and finishes only after cleanup is observed. | `services/evaluator/src/iacode_evaluator/workflow.py` | `QualityCancellationTests`; live cancellation scenario. |
| 12.4 | A run deadline and per-check deadlines are policy-owned; when either fires, the store still records the event, result, and terminal verdict. | `services/evaluator/src/iacode_evaluator/workflow.py` | `QualityDeadlineTests`; live timeout scenario. |
| 12.5 | The evaluator health check proves a Temporal poller, database access, artifact-store access, and sandbox availability rather than process existence. | `services/evaluator/src/iacode_evaluator/healthcheck.py` | `QualityHealthTests`; Compose health observation. |

## 13. Stable service and API boundary

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 13.1 | A stable internal service API creates a profile and plan, starts a run, retrieves plan/run/results/findings/evidence metadata/verdict, cancels a run, and requests reproduction. | `services/evaluator/src/iacode_evaluator/service.py` | `QualityServiceTests`. |
| 13.2 | The HTTP API exposes the stable quality lifecycle for the future Gate 5 client without exposing commands, credentials, full output, host paths, mutable verdicts, or direct sandbox control. | `apps/api/src/iacode_api/routes/quality.py` | `QualityApiTests`. |
| 13.3 | List and event endpoints are bounded and cursor-paginated; a terminal stream drains every event after the cursor before closing. | `apps/api/src/iacode_api/routes/quality.py` | `QualityApiPaginationTests`. |
| 13.4 | Every response, including validation errors and failures outside middleware, carries correlation identity and canonical error code. | `apps/api/src/iacode_api/routes/quality.py` | `QualityApiErrorTests`. |
| 13.5 | API input selects only a snapshot and declared policy/configuration; no request field selects a command, runner implementation, sandbox image, limit, evidence, result, or verdict. | `apps/api/src/iacode_api/routes/quality.py` | `QualityApiSecurityTests`. |

## 14. Agent Runtime integration

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 14.1 | An agent run may request a quality plan for its frozen workspace snapshot and receives only the bounded plan identity and applicable check summary. | `services/orchestrator/src/iacode_orchestrator/agent_runtime/activities.py` | `AgentQualityIntegrationTests`. |
| 14.2 | A quality run is owned by its requesting agent run, and a result or callback from another owner/origin is refused before storage or workflow signalling. | `services/evaluator/src/iacode_evaluator/store.py` | `QualityOwnershipTests`. |
| 14.3 | The agent receives the derived verdict, findings summary, and artifact references as labelled tool data, never as an instruction or unbounded output. | `services/agent-runtime/src/iacode_agent_runtime/context.py` | `AgentQualityContextTests`. |
| 14.4 | Quality failure cannot be transformed into agent-run success by prose, review approval, a missing callback, or a manually posted result. | `services/orchestrator/src/iacode_orchestrator/workflows/agent_run.py` | `AgentQualityPromotionTests`. |

## 15. Functional acceptance mechanism

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 15.1 | A schema-bound functional acceptance artifact records requirement, feature, scenario, environment, preconditions, execution, expected, observed, result, evidence, timestamp, and artifact references. | `.iacode/schemas/functional-acceptance.schema.json`, `FUNCTIONAL-ACCEPTANCE.json` | `FunctionalAcceptanceTests`. |
| 15.2 | Functional `PASS` requires observable executed evidence; `FAIL`, `BLOCKED`, and justified `NOT_APPLICABLE` remain distinct and are never counted as passing. | `scripts/development-ledger/check_functional_acceptance.py` | `FunctionalAcceptanceTests`. |
| 15.3 | Completeness fails when a mandatory functional requirement lacks a passing functional scenario with resolved evidence. | `scripts/development-ledger/check_completeness.py` | `FunctionalCompletenessTests`. |
| 15.4 | The mechanism is reusable by later Gates and derives its mandatory functional set from canonical requirements rather than caller arguments. | `scripts/development-ledger/check_functional_acceptance.py` | `FunctionalAcceptanceScopeTests`. |

## 16. Required functional proofs

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 16.1 | A passing fixture runs through the real evaluator workflow, artifact store, database, Temporal worker, sandbox service, and container engine and derives `PASS`. | `scripts/iacode/scenarios/quality_engine_e2e.py` | `FUNCTIONAL-ACCEPTANCE.json`; passing report. |
| 16.2 | A failing fixture runs through the same path and derives `FAIL` with the failed check, finding, and evidence preserved. | `scripts/iacode/scenarios/quality_engine_e2e.py` | `FUNCTIONAL-ACCEPTANCE.json`; failing report. |
| 16.3 | A real snapshot of IACode runs through the engine with its canonical profile, and the verdict is compared with the repository's own mandatory gate results. | `scripts/iacode/scenarios/quality_engine_e2e.py` | `FUNCTIONAL-ACCEPTANCE.json`; IACode report. |
| 16.4 | The passing run is reproduced from stored inputs, and the report proves equal plan identity and equivalent results while preserving distinct run identity. | `scripts/iacode/scenarios/quality_engine_e2e.py` | Reproduction report. |
| 16.5 | A false-PASS battery removes a result, flips an exit code, forges evidence, changes policy, changes snapshot, posts from the wrong origin, times out, denies, cancels, and supplies an unknown status; every mutation is rejected and a null control passes. | `scripts/development-ledger/gate4_red_team.py` | `M2-INTERNAL-RED-TEAM.json` with `baselineControl=VALID`. |

## 17. Observability and operations

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 17.1 | Metrics cover planned, active, completed, failed, cancelled, and timed-out runs; check duration/status; findings by bounded severity/category; evidence writes; and verdict derivations. | `services/evaluator/src/iacode_evaluator/telemetry.py` | `QualityMetricsTests`. |
| 17.2 | Metric labels are closed and low-cardinality; project path, command, output, finding message, digest, run identifier, and artifact identifier are never labels. | `services/evaluator/src/iacode_evaluator/telemetry.py` | `test_metric_names_and_labels_are_closed_and_low_cardinality`. |
| 17.3 | Logs carry correlation, run, plan, check, sandbox, status, duration, and reason but never full output, command content, secret, host environment, or evidence body. | `services/evaluator/src/iacode_evaluator/telemetry.py` | `QualityLogTests`. |
| 17.4 | Prometheus scrapes the evaluator and the operations runbook covers lifecycle, policy, runners, sandbox boundary, evidence, reproduction, recovery, and troubleshooting. | `infra/prometheus/prometheus.yml`, `docs/runbooks/QUALITY-ENGINE.md` | `QualityDocumentationTests`; live scrape. |

## 18. Program state and resumability

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 18.1 | A schema-bound program state records current milestone, Gate, checkpoint, step, last completed step, local and remote commits, status, blockers, next action, and update time. | `docs/program/PROGRAM-STATE.json`, `.iacode/schemas/program-state.schema.json` | `ProgramStateTests`. |
| 18.2 | Program state is derived and validated against the checkpoint, Git, remote state, and master plan; contradictory or stale state is refused rather than reconciled silently. | `scripts/development-ledger/program_state.py` | `ProgramStateTests`. |
| 18.3 | Each Gate slice records step identity, requirements, expected behavior, implementation, tests, functional proof, evidence, and truthful status. | `docs/checkpoints/GATE-4-CP-0001/STEPS.json` | `GateStepTests`. |

## 19. Security and provenance

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 19.1 | Untrusted project content is data: manifest text, filenames, output, findings, and artifacts cannot alter policy, plan, instruction hierarchy, runner selection, or verdict logic. | `services/evaluator/src/iacode_evaluator/` | `QualityPromptInjectionTests`; internal Red Team. |
| 19.2 | Secret scanning runs before evidence persistence and before every push; evidence containing a detected secret is quarantined without exposing the value. | `services/evaluator/src/iacode_evaluator/evidence.py`, `scripts/development-ledger/secret_scan.py` | `QualitySecretContainmentTests`; recorded staged scans. |
| 19.3 | Every evaluator artifact records provenance, ownership, license, storage/RAG/training/distillation rights, and `trainingAllowed=false` absent explicit rights evidence. | `services/evaluator/src/iacode_evaluator/evidence.py` | `QualityRightsTests`; checkpoint provenance validation. |
| 19.4 | Current advisory scans cover every delivered dependency lock and refuse unsuppressed Critical or High findings without narrowing the source set. | `scripts/iacode/dependency_scan.py` | Recorded dependency scan; `DependencyScanTests`. |

## 20. Verification, documentation, and closure

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 20.1 | The repository's one verification command covers evaluator unit, integration, functional, reproduction, recovery, cancellation, timeout, and false-PASS stages in targeted and full modes. | `scripts/iacode/verify.py` | `Gate4VerificationStageTests`; recorded verification. |
| 20.2 | Architecture, development, version, entry, and model-usage documents describe the delivered quality engine and its limits rather than planned behavior. | `docs/ARCHITECTURE.md`, `docs/DEVELOPMENT.md`, `docs/VERSIONS.md`, `README.md`, `START-HERE.md`, `docs/MODEL-USAGE-POLICY.md` | `QualityDocumentationTests`. |
| 20.3 | Structural decisions for the quality boundary, immutable evidence/verdict derivation, and project profiles/runners are recorded as indexed ADRs. | `docs/adr/` | `Gate4AdrTests`. |
| 20.4 | The Gate retrospective records reusable lessons, and every important confirmed failure becomes an effective automated guardrail before handoff. | `.iacode/memory/retrospectives/GATE-4-CP-0001.md`, `.iacode/memory/lessons.jsonl` | `validate_lessons.py`; guardrail effectiveness report. |
| 20.5 | A deterministic review bundle contains the complete checkpoint, changed source, tests, migrations, schemas, policies, documentation, functional acceptance, quality results, Red Team, changeset, Git/remote state, manifest, and checksums; validation opens it, checks hashes and required files, and scans it for secrets. | `scripts/development-ledger/review_bundle.py` | `ReviewBundleTests`; review validation report. |
| 20.6 | Every Gate commit and the checkpoint tag are on the authorised remote when the Gate reaches its later independent verdict. | `scripts/development-ledger/remote_sync.py` | Recorded remote synchronization check. |
| 20.7 | This implementing run ends at `READY_FOR_REVIEW` with complete functional and quality evidence, no blocker, and no claim of independent validation or Gate pass. | `docs/checkpoints/GATE-4-CP-0001/STATE.json` | Checkpoint validation; completeness; internal reviews. |
| 20.8 | A later independent run performs review, Red Team, and the Gate verdict before Gate 5 begins; Gate 4 starts no Gate 5 implementation. | `docs/DEVELOPMENT-CONTRACT.md`, `docs/checkpoints/GATE-4-CP-0001/NEXT.md` | Independent review checkpoint. |
