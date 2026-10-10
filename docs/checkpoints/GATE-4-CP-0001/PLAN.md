# Plan — GATE 4 Quality Engine

The derived requirement set is 191 rows: 105 canonical Gate requirements and 86 lesson-derived
requirements. Every slice below ends with targeted tests, an observable functional proof where it
has runnable behavior, completeness evidence for its assigned rows, a staged secret scan, an atomic
commit, and an authorised push. A red check causes rework in the same slice.

## Delivery slices

| Step | Scope | Principal requirements | Exit evidence |
|---|---|---|---|
| `G4-S00` | Specification, preflight, derived requirements, baseline, plan | 1.1, 18.3, lesson controls | Canonical mirror, 191-row matrix, this baseline and plan |
| `G4-S01` | Contracts, policy schema/loader, profiles, planner, runner registry, verdict kernel | 2.1–6.6, 10.1–10.7 | Unit suites with positive and false-PASS cases |
| `G4-S02` | Sandbox profiles and stack support | 7.1–8.7 | Python/Node/TypeScript/Angular/Maven/Gradle fixture executions in containers |
| `G4-S03` | Immutable evidence, persistence, migration, service | 9.1–13.1 | MinIO/PostgreSQL integration, migration reversal, reproduction |
| `G4-S04` | Temporal workflow, API, Agent Runtime, health and telemetry | 12.1–14.4, 17.1–17.4 | Live lifecycle, restart, cancel, deadline, API and scrape evidence |
| `G4-S05` | Functional acceptance, program state, review bundle | 15.1–15.4, 18.1–18.3, 20.5 | Reusable validators exercised on positive and negative fixtures |
| `G4-S06` | Required real scenarios and adversarial battery | 16.1–16.5, 19.1–19.4 | PASS fixture, FAIL fixture, IACode snapshot, reproduction, valid null control |
| `G4-S07` | Repository verification, docs, ADRs, memory and closure evidence | 20.1–20.8 plus every lesson row | Full verification, Green Keeper, completeness, reviews, `READY_FOR_REVIEW` |

## Architectural constraints

- `iacode_contracts.quality` owns cross-process names and serialization.
- `services/evaluator` owns profile detection, planning, orchestration of checks, evidence
  resolution, and verdict derivation; it never starts a process.
- The existing sandbox owns all project command execution and all container-engine access.
- PostgreSQL stores immutable metadata and append-only events; MinIO stores content-addressed bodies.
- Policy and project configuration select only declared behavior. Neither may carry a verdict,
  result, arbitrary image, mount, network, or raised limit.
- Gate 20's held-out model evaluation and Gate 5's CLI/VS Code surfaces remain reserved.

## Required delivery order

Lesson preflight → requirement derivation → baseline → plan → implementation slices → test and
quality → Green Keeper → Delivery Completeness Validator → internal Red Team → Milestone Closure
Auditor → `READY_FOR_REVIEW`. Independent review and the Gate verdict belong to a later run.

## Stop conditions

Stop and record `BLOCKED` on predecessor divergence, unavailable required infrastructure that has no
safe in-scope substitute, a credential finding, or an irreparable mandatory-gate failure. Do not
weaken policy, tests, denominators, sandboxing, evidence resolution, or verdict rules.
