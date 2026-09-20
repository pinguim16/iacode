# IACode Master Plan

Each Gate requires its named previous Gate to have passed. Acceptance requires implementation evidence, applicable quality checks, the delivery-assurance gates, and a valid checkpoint. A Gate fails when any listed fail condition or the global Development Contract is violated.

## Validation cadence

An intermediate Gate closes at `INTERNAL_GATE_PASS` on the project's own controls: the lesson
preflight, the requirements matrix, the Green Keeper, and the Delivery Completeness Validator.
Independent external validation happens once per milestone and produces `MILESTONE_EXTERNAL_PASS`.

| Milestone | Scope | Gates |
|---|---|---|
| `M0` | Development control plane | `SETUP-00` |
| `M1` | IACode V0 foundation | `GATE 0` – `GATE 3` |
| `M2` | IACode V0 completion and experience | `GATE 4` – `GATE 7` |
| `M3` | Code graph, memory and gap detection | `GATE 8` – `GATE 11` |
| `M4` | Skills and dataset production | `GATE 12` – `GATE 15` |
| `M5` | Dataset audit and model adaptation | `GATE 16` – `GATE 19` |
| `M6` | Evaluation, shadow mode and promotion | `GATE 20` – `GATE 23` |

The auditor evaluates the milestone as a whole, including integration between its Gates, not only the
last Gate. The full policy, including the extraordinary-audit triggers, is in
[MILESTONE-VALIDATION.md](MILESTONE-VALIDATION.md).

## SETUP-00 — Development Control Plane

- Objective: establish tool-neutral contracts, agents, documentation, schemas, ledger tooling, tests, and handoff.
- Dependencies: empty or existing repository baseline.
- Deliverables: every artifact required by [SETUP-00-CHECKLIST.md](SETUP-00-CHECKLIST.md) and a valid checkpoint.
- Acceptance: [SETUP-00-CHECKLIST.md](SETUP-00-CHECKLIST.md), automated tests, Red Team, cold-start simulation, and checkpoint validation pass.
- FAIL: missing mandatory artifact/evidence, undetected corruption/secret, false PASS, or any future-Gate implementation.
- Previous Gate: none.

## IACode V0

| Gate | Objective | Dependencies | Deliverables | Acceptance criteria | FAIL conditions | Previous Gate |
|---|---|---|---|---|---|---|
| GATE 0 — Foundation | Establish runtime repository foundations and stable core contracts. | Approved SETUP-00 control plane. | Chosen stack, build, package layout, configuration contract, CI baseline, tests. | Clean bootstrap and build; contract tests and documented architecture pass. | Non-reproducible setup, partial foundation, missing tests, or scope leak. | SETUP-00 |
| GATE 1 — Model Gateway | Provide provider-neutral model invocation boundaries. | Foundation contracts and build. | Provider interfaces, configuration, error model, observability, tests. | Contract tests cover supported calls, failures, timeouts, and configuration. | Provider coupling, secret leakage, unhandled failure, or fake production response. | GATE 0 |
| GATE 2 — Agent Runtime | Execute governed agents through explicit lifecycle contracts. | Stable model gateway. | Agent lifecycle, role loading, state transitions, orchestration tests. | Deterministic lifecycle and recovery cases pass with observable traces. | Hidden state, unbounded orchestration, broken recovery, or contract drift. | GATE 1 |
| GATE 3 — Sandbox | Isolate tool and code execution by policy. | Agent runtime boundaries. | Sandbox adapters, filesystem/network/process policies, escape tests. | Least-privilege tests and adversarial escape suite pass. | Privilege escape, policy bypass, unsafe default, or sensitive logging. | GATE 2 |
| GATE 4 — Quality Engine | Automate validation and promotion evidence. | Sandboxed execution and agent lifecycle. | Quality model, runners, evidence store, verdict rules, tests. | False PASS cases are rejected and evidence is reproducible. | Assertion-only PASS, mutable evidence, bypassable gates, or missing failure modes. | GATE 3 |
| GATE 5 — VS Code Integration | Expose governed workflows in VS Code. | Stable quality engine and runtime APIs. | Extension, secure IPC, status and approval UX, integration tests. | Fresh install and end-to-end task flow pass without bypassing controls. | UI/runtime divergence, insecure IPC, unavailable recovery, or hidden state. | GATE 4 |

Milestone: **IACode V0** is eligible only after GATE 5 passes.

## IACode V1

| Gate | Objective | Dependencies | Deliverables | Acceptance criteria | FAIL conditions | Previous Gate |
|---|---|---|---|---|---|---|
| GATE 6 — Experience Store | Persist observable engineering experiences with rights metadata. | V0 quality evidence. | Experience API, storage, schemas, retention and rights controls. | Round-trip, migration, redaction, provenance, and access tests pass. | Private reasoning/secrets stored, rights lost, or corrupt recovery. | GATE 5 |
| GATE 7 — Knowledge Engine | Derive and retrieve governed reusable knowledge. | Experience store. | Ingestion, indexing, retrieval, citations, invalidation tests. | Relevant retrieval is traceable to permitted source artifacts. | Uncited output, stale invalidation, rights bypass, or data leakage. | GATE 6 |
| GATE 8 — Code Graph | Model code entities and relationships. | Knowledge engine contracts. | Parsers, graph schema, incremental updates, query tests. | Supported repositories build accurate, incrementally updated graphs. | Silent parse loss, stale graph, unsupported ambiguity hidden as success. | GATE 7 |
| GATE 9 — Project Memory | Maintain bounded, verifiable project context. | Code graph and knowledge retrieval. | Memory lifecycle, relevance, expiry, conflict handling, tests. | Restart and conflict tests preserve traceable current context. | Hidden memory, unverifiable claims, unbounded retention, or stale priority. | GATE 8 |

Milestone: **IACode V1** is eligible only after GATE 9 passes.

## IACode V2

| Gate | Objective | Dependencies | Deliverables | Acceptance criteria | FAIL conditions | Previous Gate |
|---|---|---|---|---|---|---|
| GATE 10 — Knowledge Gap Detector | Detect missing or uncertain knowledge from evidence. | Project memory. | Gap taxonomy, confidence/evidence model, evaluation set, tests. | Known gaps are detected with calibrated false-positive bounds. | Unsupported certainty, no evidence trail, or unusable noise. | GATE 9 |
| GATE 11 — Research Agent | Resolve approved gaps through governed research. | Gap detector. | Source policy, research workflow, citations, verification tests. | Results cite permitted authoritative sources and uncertainty. | Fabricated source, rights breach, unverified claim, or scope escape. | GATE 10 |
| GATE 12 — Skill Graph | Represent capabilities, prerequisites, and evidence. | Verified research outputs. | Skill ontology, graph operations, proficiency evidence, tests. | Skill links and prerequisites are queryable and evidence-backed. | Circular/invalid graph, unsupported proficiency, or provenance loss. | GATE 11 |

Milestone: **IACode V2** is eligible only after GATE 12 passes.

## IACode V3

| Gate | Objective | Dependencies | Deliverables | Acceptance criteria | FAIL conditions | Previous Gate |
|---|---|---|---|---|---|---|
| GATE 13 — Git Learning Engine | Extract permitted learning signals from repository history. | Skill graph and provenance controls. | History ingestion, event normalization, filters, tests. | Signals are reproducible, rights-filtered, and exclude secrets. | History damage, secret capture, rights ambiguity, or false attribution. | GATE 12 |
| GATE 14 — Synthetic Task Factory | Generate controlled tasks with known evaluation criteria. | Git learning signals. | Task generators, constraints, validators, diversity tests. | Generated tasks are solvable, non-leaking, varied, and scored. | Answer leakage, invalid tasks, provenance loss, or unsafe content. | GATE 13 |
| GATE 15 — Curriculum Engine | Order governed tasks by prerequisites and measured difficulty. | Valid synthetic tasks and skill graph. | Curriculum planner, difficulty model, adaptation tests. | Ordering improves held-out progression without evaluation leakage. | Circular curriculum, uncalibrated difficulty, or target leakage. | GATE 14 |
| GATE 16 — Dataset Factory | Build versioned, filtered, auditable training datasets. | Curriculum and rights-qualified experiences. | Dataset pipeline, manifests, splits, deduplication, audits. | Reproducible datasets pass rights, secret, leakage, and quality audits. | Ineligible sample, split contamination, missing lineage, or irreproducibility. | GATE 15 |

Milestone: **IACode V3** is eligible only after GATE 16 passes.

## IACode V4

| Gate | Objective | Dependencies | Deliverables | Acceptance criteria | FAIL conditions | Previous Gate |
|---|---|---|---|---|---|---|
| GATE 17 — Base Model Tournament | Select candidate bases through reproducible evaluation. | Audited datasets and evaluation policy. | Candidate matrix, benchmarks, cost/performance evidence, decision ADR. | Selection wins predefined held-out criteria with reproducible runs. | Benchmark leakage, incomparable runs, undocumented trade-off, or rights issue. | GATE 16 |
| GATE 18 — QLoRA / SFT | Produce supervised adapters from eligible data. | Selected base model and audited dataset. | Training pipeline, configs, checkpoints, safety and quality results. | Reproducible training improves target metrics without critical regression. | Unlicensed data, unreproducible run, regression, or missing baseline. | GATE 17 |
| GATE 19 — Preference Training | Improve behavior using governed preference evidence. | Passing supervised candidate. | Preference dataset, training pipeline, alignment evaluations. | Held-out preference and safety metrics improve without capability collapse. | Biased/invalid labels, leakage, safety regression, or missing provenance. | GATE 18 |
| GATE 20 — Evaluation Lab | Provide independent, repeatable candidate evaluation. | Trained candidates and immutable tests. | Harness, held-out suites, regression dashboard, signed results. | Repeatability and blind evaluation controls pass. | Candidate access to answers, mutable scoring, non-repeatable result, or false promotion. | GATE 19 |

Milestone: **IACode V4** is eligible only after GATE 20 passes.

## IACode V5

| Gate | Objective | Dependencies | Deliverables | Acceptance criteria | FAIL conditions | Previous Gate |
|---|---|---|---|---|---|---|
| GATE 21 — Shadow Mode | Observe candidate behavior without production authority. | Independent evaluation lab. | Traffic replay, isolation, comparison, incident controls. | Candidate completes representative workload with no production side effects. | Any unauthorized effect, data leak, missing comparison, or unsafe behavior. | GATE 20 |
| GATE 22 — Promotion Engine | Promote only demonstrably superior candidates. | Passing shadow-mode evidence. | Promotion policy, rollback, approvals, audit log, tests. | Candidate satisfies every threshold and rollback drill passes. | Metric cherry-picking, missing approval, irreversible promotion, or regression. | GATE 21 |
| GATE 23 — Autonomous Learning Loop | Operate a bounded, governed improvement cycle. | Proven promotion and rollback engine. | Trigger policy, data curation, train/evaluate/shadow/promote loop, kill switch. | Multiple sandboxed cycles preserve rights, safety, quality, and rollback. | Self-promotion, control bypass, runaway cost, data contamination, or no kill switch. | GATE 22 |

Milestone: **IACode V5** is eligible only after GATE 23 passes.

