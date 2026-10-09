# Closure Requirements - GATE-4-CP-0001

Derived from the canonical sources listed below, before implementation. The expected set
is recomputed by `policies.expected_requirement_refs` and compared exactly with the
declared set, so a requirement cannot be dropped and the denominator cannot be reduced.

## Sources

- SOURCE A: docs/GATE-4-CHECKLIST.md, the canonical GATE-4 specification
- SOURCE B: docs/MILESTONE-VALIDATION.md, the milestone requirements of the audit
- SOURCE C: LESSON-PREFLIGHT.json, the lessons the engineering memory imposes

## Requirements

| ID | Source | Anchor | Mandatory | Implementation | Final | Description |
|---|---|---|---|---|---|---|
| `REQ-0001` | GATE_SPECIFICATION | `canonical:GATE-4#1.1` | yes | `NOT_STARTED` | `NOT_STARTED` | This checklist is the canonical, machine-readable requirement source for the Gate and its registry mirror has exactly the same ordered rows. |
| `REQ-0002` | GATE_SPECIFICATION | `canonical:GATE-4#1.2` | yes | `NOT_STARTED` | `NOT_STARTED` | The evaluator reservation is consumed by this Gate while every later-Gate reservation remains enforced. |
| `REQ-0003` | GATE_SPECIFICATION | `canonical:GATE-4#1.3` | yes | `NOT_STARTED` | `NOT_STARTED` | The closed mandatory gate registry includes an evaluator gate that builds every image it executes before measuring it. |
| `REQ-0004` | GATE_SPECIFICATION | `canonical:GATE-4#1.4` | yes | `NOT_STARTED` | `NOT_STARTED` | The evaluator suite is canonical, counted, and available to evidence resolution. |
| `REQ-0005` | GATE_SPECIFICATION | `canonical:GATE-4#1.5` | yes | `NOT_STARTED` | `NOT_STARTED` | Gate 4 introduces no held-out model evaluation capability reserved for Gate 20 and no CLI or VS Code capability reserved for Gate 5. |
| `REQ-0006` | GATE_SPECIFICATION | `canonical:GATE-4#1.6` | yes | `NOT_STARTED` | `NOT_STARTED` | Generated review archives are permanently excluded from Git, while their validation result and digest remain checkpoint evidence. |
| `REQ-0007` | GATE_SPECIFICATION | `canonical:GATE-4#2.1` | yes | `NOT_STARTED` | `NOT_STARTED` | Versioned contracts exist for `QualityPlan`, `QualityCheck`, `QualityRun`, `QualityResult`, `QualityFinding`, `QualityEvidence`, `QualityPolicy`, and `QualityVerdict`. |
| `REQ-0008` | GATE_SPECIFICATION | `canonical:GATE-4#2.2` | yes | `NOT_STARTED` | `NOT_STARTED` | Contract vocabularies are closed and reject missing fields, extra fields, wrong types, invalid values, duplicate identifiers, and unsupported versions with distinct reasons. |
| `REQ-0009` | GATE_SPECIFICATION | `canonical:GATE-4#2.3` | yes | `NOT_STARTED` | `NOT_STARTED` | Every contract round-trips without losing identity, ordering, timestamps, digests, policy references, sandbox references, or artifact references. |
| `REQ-0010` | GATE_SPECIFICATION | `canonical:GATE-4#2.4` | yes | `NOT_STARTED` | `NOT_STARTED` | Every reusable artifact defaults to `trainingAllowed=false`; a quality contract carries no credential, secret, chain-of-thought, or whole environment. |
| `REQ-0011` | GATE_SPECIFICATION | `canonical:GATE-4#2.5` | yes | `NOT_STARTED` | `NOT_STARTED` | Payload sizes are bounded as the receiver measures them, and oversized plans, output summaries, findings, and evidence metadata are refused before persistence. |
| `REQ-0012` | GATE_SPECIFICATION | `canonical:GATE-4#3.1` | yes | `NOT_STARTED` | `NOT_STARTED` | A project profile records the detected stacks, manifests, workspace root, configuration source, confidence, and unresolved ambiguity without depending on IACode-specific paths. |
| `REQ-0013` | GATE_SPECIFICATION | `canonical:GATE-4#3.2` | yes | `NOT_STARTED` | `NOT_STARTED` | Detection recognizes Python, Node, TypeScript, Angular, Maven, and Gradle from repository evidence and supports mixed projects. |
| `REQ-0014` | GATE_SPECIFICATION | `canonical:GATE-4#3.3` | yes | `NOT_STARTED` | `NOT_STARTED` | Detection never executes project code, follows no symlink outside the snapshot, ignores generated/vendor directories, and reads only bounded manifest content. |
| `REQ-0015` | GATE_SPECIFICATION | `canonical:GATE-4#3.4` | yes | `NOT_STARTED` | `NOT_STARTED` | Ambiguous or unknown toolchains produce an explicit unsupported/ambiguous result and never an invented stack or a false `PASS`. |
| `REQ-0016` | GATE_SPECIFICATION | `canonical:GATE-4#3.5` | yes | `NOT_STARTED` | `NOT_STARTED` | A versioned project configuration may select declared checks and commands but cannot select an image, mount, network, resource bound, verdict, or undeclared runner. |
| `REQ-0017` | GATE_SPECIFICATION | `canonical:GATE-4#3.6` | yes | `NOT_STARTED` | `NOT_STARTED` | The same source code onboards Python, Java, and TypeScript/Node fixtures through profiles rather than repository-specific branches. |
| `REQ-0018` | GATE_SPECIFICATION | `canonical:GATE-4#4.1` | yes | `NOT_STARTED` | `NOT_STARTED` | One canonical policy registry declares profiles, runners, mandatory checks, applicability, timeouts, output limits, evidence requirements, and verdict rules. |
| `REQ-0019` | GATE_SPECIFICATION | `canonical:GATE-4#4.2` | yes | `NOT_STARTED` | `NOT_STARTED` | Unknown policy keys, runner names, check kinds, result states, evidence kinds, or verdict rules are refused when policy loads. |
| `REQ-0020` | GATE_SPECIFICATION | `canonical:GATE-4#4.3` | yes | `NOT_STARTED` | `NOT_STARTED` | The requested project configuration may add checks or lower limits but cannot remove a mandatory check, raise a limit, weaken a threshold, or alter a verdict rule. |
| `REQ-0021` | GATE_SPECIFICATION | `canonical:GATE-4#4.4` | yes | `NOT_STARTED` | `NOT_STARTED` | Applicability is derived from the project profile: an empty applicable set is justified `NOT_APPLICABLE`, while a missing required set is `FAIL`. |
| `REQ-0022` | GATE_SPECIFICATION | `canonical:GATE-4#4.5` | yes | `NOT_STARTED` | `NOT_STARTED` | Every policy key has an implementation consumer, and the policy and its schema are content-addressed inputs to every plan. |
| `REQ-0023` | GATE_SPECIFICATION | `canonical:GATE-4#5.1` | yes | `NOT_STARTED` | `NOT_STARTED` | Planning freezes the project snapshot checksum, profile, policy digest, ordered checks, commands, runner images, limits, and environment before execution begins. |
| `REQ-0024` | GATE_SPECIFICATION | `canonical:GATE-4#5.2` | yes | `NOT_STARTED` | `NOT_STARTED` | Plan identity is a deterministic digest of canonical content; equal inputs produce the same plan and any material input change produces a different plan. |
| `REQ-0025` | GATE_SPECIFICATION | `canonical:GATE-4#5.3` | yes | `NOT_STARTED` | `NOT_STARTED` | Check identifiers are unique, stable, and independent of execution order; dependencies form an acyclic graph and unknown dependencies are refused. |
| `REQ-0026` | GATE_SPECIFICATION | `canonical:GATE-4#5.4` | yes | `NOT_STARTED` | `NOT_STARTED` | A plan cannot carry a caller-authored expected verdict, result, evidence digest, sandbox result, or hidden command. |
| `REQ-0027` | GATE_SPECIFICATION | `canonical:GATE-4#5.5` | yes | `NOT_STARTED` | `NOT_STARTED` | The plan exposes why every check is mandatory, optional, or not applicable and identifies the policy rule that decided it. |
| `REQ-0028` | GATE_SPECIFICATION | `canonical:GATE-4#6.1` | yes | `NOT_STARTED` | `NOT_STARTED` | A closed runner registry maps declared runner identifiers to structured sandbox command requests; unknown identifiers never fall back to a shell command. |
| `REQ-0029` | GATE_SPECIFICATION | `canonical:GATE-4#6.2` | yes | `NOT_STARTED` | `NOT_STARTED` | Initial check kinds cover build, unit, integration, lint, static analysis, dependency/security, secret scan, configured coverage, applicable migration checks, and diff integrity. |
| `REQ-0030` | GATE_SPECIFICATION | `canonical:GATE-4#6.3` | yes | `NOT_STARTED` | `NOT_STARTED` | Commands are argument vectors or policy-owned command text, never concatenated from untrusted project values, and every working directory resolves within the snapshot. |
| `REQ-0031` | GATE_SPECIFICATION | `canonical:GATE-4#6.4` | yes | `NOT_STARTED` | `NOT_STARTED` | A runner normalizes exit code, timeout, denial, cancellation, truncation, duration, sandbox identity, and artifacts without inventing an exit code for work that never started. |
| `REQ-0032` | GATE_SPECIFICATION | `canonical:GATE-4#6.5` | yes | `NOT_STARTED` | `NOT_STARTED` | Required checks execute despite an earlier failure unless their declared dependency makes execution impossible; every skipped check records the exact dependency reason. |
| `REQ-0033` | GATE_SPECIFICATION | `canonical:GATE-4#6.6` | yes | `NOT_STARTED` | `NOT_STARTED` | A cancelled or timed-out run reaches one terminal state, records the reason before the state, and leaves no running check or sandbox session. |
| `REQ-0034` | GATE_SPECIFICATION | `canonical:GATE-4#7.1` | yes | `NOT_STARTED` | `NOT_STARTED` | Every project command is dispatched through the Gate 3 sandbox task queue; the evaluator, API, orchestrator, and host never execute a project command. |
| `REQ-0035` | GATE_SPECIFICATION | `canonical:GATE-4#7.2` | yes | `NOT_STARTED` | `NOT_STARTED` | Only the sandbox service has the container engine socket, and the evaluator service has no host mount, project bind mount, credential, or engine access. |
| `REQ-0036` | GATE_SPECIFICATION | `canonical:GATE-4#7.3` | yes | `NOT_STARTED` | `NOT_STARTED` | The executor origin is frozen as `EVALUATOR` when a quality check is created; a result from another origin is refused before storage. |
| `REQ-0037` | GATE_SPECIFICATION | `canonical:GATE-4#7.4` | yes | `NOT_STARTED` | `NOT_STARTED` | The snapshot, policy, image, resources, network, mounts, and limits cannot be changed by an executing check or its project. |
| `REQ-0038` | GATE_SPECIFICATION | `canonical:GATE-4#7.5` | yes | `NOT_STARTED` | `NOT_STARTED` | A host sentinel and host process observation prove that passing and failing fixtures execute inside the sandbox and cause no host side effect. |
| `REQ-0039` | GATE_SPECIFICATION | `canonical:GATE-4#8.1` | yes | `NOT_STARTED` | `NOT_STARTED` | Python projects have policy-owned runners for build/package validation, unit/integration tests, lint/static checks, dependency/security, secret, configured coverage, migration, and diff integrity as applicable. |
| `REQ-0040` | GATE_SPECIFICATION | `canonical:GATE-4#8.2` | yes | `NOT_STARTED` | `NOT_STARTED` | Node and TypeScript projects have policy-owned runners for install integrity, build, unit/integration tests, lint/static checks, dependency/security, secret, configured coverage, migration, and diff integrity as applicable. |
| `REQ-0041` | GATE_SPECIFICATION | `canonical:GATE-4#8.3` | yes | `NOT_STARTED` | `NOT_STARTED` | Angular projects have policy-owned runners for production build, unit tests, lint/static checks, dependency/security, secret, configured coverage, and diff integrity. |
| `REQ-0042` | GATE_SPECIFICATION | `canonical:GATE-4#8.4` | yes | `NOT_STARTED` | `NOT_STARTED` | Maven projects have policy-owned runners for package, unit/integration tests, static checks, dependency/security, secret, configured coverage, migration, and diff integrity as applicable. |
| `REQ-0043` | GATE_SPECIFICATION | `canonical:GATE-4#8.5` | yes | `NOT_STARTED` | `NOT_STARTED` | Gradle projects have policy-owned runners for build, unit/integration tests, static checks, dependency/security, secret, configured coverage, migration, and diff integrity as applicable. |
| `REQ-0044` | GATE_SPECIFICATION | `canonical:GATE-4#8.6` | yes | `NOT_STARTED` | `NOT_STARTED` | Sandbox image profiles are extensible and content-addressed; a missing or stale required image is a recorded failure and never silently replaced. |
| `REQ-0045` | GATE_SPECIFICATION | `canonical:GATE-4#8.7` | yes | `NOT_STARTED` | `NOT_STARTED` | Dependency installation and checks have no internet access; lockfiles and prebuilt image toolchains decide what can execute reproducibly. |
| `REQ-0046` | GATE_SPECIFICATION | `canonical:GATE-4#9.1` | yes | `NOT_STARTED` | `NOT_STARTED` | Quality evidence uses the existing artifact store and records a content digest, byte size, media type, producer, source inputs, creation time, retention class, and rights. |
| `REQ-0047` | GATE_SPECIFICATION | `canonical:GATE-4#9.2` | yes | `NOT_STARTED` | `NOT_STARTED` | Evidence is content-addressed and immutable: a digest collision with different bytes, overwrite, rename, or deletion through the evaluator is refused. |
| `REQ-0048` | GATE_SPECIFICATION | `canonical:GATE-4#9.3` | yes | `NOT_STARTED` | `NOT_STARTED` | A stored evidence reference is resolved and re-hashed before it can support a verdict; missing, truncated-without-artifact, or digest-mismatched evidence fails the run. |
| `REQ-0049` | GATE_SPECIFICATION | `canonical:GATE-4#9.4` | yes | `NOT_STARTED` | `NOT_STARTED` | Inline summaries are bounded and secret-redacted; complete output is an artifact, never a database field, API response, metric label, or log record. |
| `REQ-0050` | GATE_SPECIFICATION | `canonical:GATE-4#9.5` | yes | `NOT_STARTED` | `NOT_STARTED` | Evidence reproduction replays the frozen plan against the same snapshot and policy, records a new run, and compares result/evidence digests without rewriting the original. |
| `REQ-0051` | GATE_SPECIFICATION | `canonical:GATE-4#10.1` | yes | `NOT_STARTED` | `NOT_STARTED` | Each check produces exactly one terminal result and zero or more typed findings linked to resolvable evidence. |
| `REQ-0052` | GATE_SPECIFICATION | `canonical:GATE-4#10.2` | yes | `NOT_STARTED` | `NOT_STARTED` | A mandatory failure, denial, timeout, cancellation, execution error, missing result, unresolved evidence, stale input, or incomplete check set makes the verdict `FAIL`. |
| `REQ-0053` | GATE_SPECIFICATION | `canonical:GATE-4#10.3` | yes | `NOT_STARTED` | `NOT_STARTED` | `PASS` requires the exact applicable mandatory set, every result successful, every required evidence reference resolved, and every configured threshold satisfied. |
| `REQ-0054` | GATE_SPECIFICATION | `canonical:GATE-4#10.4` | yes | `NOT_STARTED` | `NOT_STARTED` | Coverage is evaluated only when configured; below-threshold or unreadable coverage fails, while legitimately unconfigured coverage is justified `NOT_APPLICABLE` and never counted as `PASS`. |
| `REQ-0055` | GATE_SPECIFICATION | `canonical:GATE-4#10.5` | yes | `NOT_STARTED` | `NOT_STARTED` | Severity, category, location, fingerprint, message, check identity, and evidence identify a finding; equal findings deduplicate deterministically without hiding recurrence. |
| `REQ-0056` | GATE_SPECIFICATION | `canonical:GATE-4#10.6` | yes | `NOT_STARTED` | `NOT_STARTED` | The verdict is a pure derivation from the frozen policy, plan, results, and resolved evidence; no API, runner, database row, or caller may submit it. |
| `REQ-0057` | GATE_SPECIFICATION | `canonical:GATE-4#10.7` | yes | `NOT_STARTED` | `NOT_STARTED` | Re-deriving a stored verdict must produce the same value and digest; disagreement marks the run invalid and never overwrites history. |
| `REQ-0058` | GATE_SPECIFICATION | `canonical:GATE-4#11.1` | yes | `NOT_STARTED` | `NOT_STARTED` | Relational persistence records quality plans, runs, checks, results, findings, evidence references, verdicts, and append-only run events with foreign keys and closed status constraints. |
| `REQ-0059` | GATE_SPECIFICATION | `canonical:GATE-4#11.2` | yes | `NOT_STARTED` | `NOT_STARTED` | Plan content, result content, and verdict content are immutable after insertion; lifecycle updates may change only the declared run state and timestamps. |
| `REQ-0060` | GATE_SPECIFICATION | `canonical:GATE-4#11.3` | yes | `NOT_STARTED` | `NOT_STARTED` | Idempotency keys and uniqueness constraints make duplicate create, dispatch, callback, event, and verdict operations return the recorded fact rather than create a second one. |
| `REQ-0061` | GATE_SPECIFICATION | `canonical:GATE-4#11.4` | yes | `NOT_STARTED` | `NOT_STARTED` | The event that explains a state is committed before the state a reader may act on, including every terminal transition. |
| `REQ-0062` | GATE_SPECIFICATION | `canonical:GATE-4#11.5` | yes | `NOT_STARTED` | `NOT_STARTED` | Migration `0006` upgrades from zero and from `0005`, downgrades cleanly, and leaves no Alembic autogenerate diff. |
| `REQ-0063` | GATE_SPECIFICATION | `canonical:GATE-4#11.6` | yes | `NOT_STARTED` | `NOT_STARTED` | No quality table stores a credential, full command output, host environment, or training eligibility defaulting to true. |
| `REQ-0064` | GATE_SPECIFICATION | `canonical:GATE-4#12.1` | yes | `NOT_STARTED` | `NOT_STARTED` | A durable workflow plans, starts, executes, cancels, resumes, reproduces, and finishes a quality run with a queryable event history. |
| `REQ-0065` | GATE_SPECIFICATION | `canonical:GATE-4#12.2` | yes | `NOT_STARTED` | `NOT_STARTED` | A worker restart during a check preserves the run identity and either receives the owned result or records an explicit failure; it never silently passes or duplicates execution. |
| `REQ-0066` | GATE_SPECIFICATION | `canonical:GATE-4#12.3` | yes | `NOT_STARTED` | `NOT_STARTED` | Cancellation is idempotent, propagates to the sandbox, refuses late results, and finishes only after cleanup is observed. |
| `REQ-0067` | GATE_SPECIFICATION | `canonical:GATE-4#12.4` | yes | `NOT_STARTED` | `NOT_STARTED` | A run deadline and per-check deadlines are policy-owned; when either fires, the store still records the event, result, and terminal verdict. |
| `REQ-0068` | GATE_SPECIFICATION | `canonical:GATE-4#12.5` | yes | `NOT_STARTED` | `NOT_STARTED` | The evaluator health check proves a Temporal poller, database access, artifact-store access, and sandbox availability rather than process existence. |
| `REQ-0069` | GATE_SPECIFICATION | `canonical:GATE-4#13.1` | yes | `NOT_STARTED` | `NOT_STARTED` | A stable internal service API creates a profile and plan, starts a run, retrieves plan/run/results/findings/evidence metadata/verdict, cancels a run, and requests reproduction. |
| `REQ-0070` | GATE_SPECIFICATION | `canonical:GATE-4#13.2` | yes | `NOT_STARTED` | `NOT_STARTED` | The HTTP API exposes the stable quality lifecycle for the future Gate 5 client without exposing commands, credentials, full output, host paths, mutable verdicts, or direct sandbox control. |
| `REQ-0071` | GATE_SPECIFICATION | `canonical:GATE-4#13.3` | yes | `NOT_STARTED` | `NOT_STARTED` | List and event endpoints are bounded and cursor-paginated; a terminal stream drains every event after the cursor before closing. |
| `REQ-0072` | GATE_SPECIFICATION | `canonical:GATE-4#13.4` | yes | `NOT_STARTED` | `NOT_STARTED` | Every response, including validation errors and failures outside middleware, carries correlation identity and canonical error code. |
| `REQ-0073` | GATE_SPECIFICATION | `canonical:GATE-4#13.5` | yes | `NOT_STARTED` | `NOT_STARTED` | API input selects only a snapshot and declared policy/configuration; no request field selects a command, runner implementation, sandbox image, limit, evidence, result, or verdict. |
| `REQ-0074` | GATE_SPECIFICATION | `canonical:GATE-4#14.1` | yes | `NOT_STARTED` | `NOT_STARTED` | An agent run may request a quality plan for its frozen workspace snapshot and receives only the bounded plan identity and applicable check summary. |
| `REQ-0075` | GATE_SPECIFICATION | `canonical:GATE-4#14.2` | yes | `NOT_STARTED` | `NOT_STARTED` | A quality run is owned by its requesting agent run, and a result or callback from another owner/origin is refused before storage or workflow signalling. |
| `REQ-0076` | GATE_SPECIFICATION | `canonical:GATE-4#14.3` | yes | `NOT_STARTED` | `NOT_STARTED` | The agent receives the derived verdict, findings summary, and artifact references as labelled tool data, never as an instruction or unbounded output. |
| `REQ-0077` | GATE_SPECIFICATION | `canonical:GATE-4#14.4` | yes | `NOT_STARTED` | `NOT_STARTED` | Quality failure cannot be transformed into agent-run success by prose, review approval, a missing callback, or a manually posted result. |
| `REQ-0078` | GATE_SPECIFICATION | `canonical:GATE-4#15.1` | yes | `NOT_STARTED` | `NOT_STARTED` | A schema-bound functional acceptance artifact records requirement, feature, scenario, environment, preconditions, execution, expected, observed, result, evidence, timestamp, and artifact references. |
| `REQ-0079` | GATE_SPECIFICATION | `canonical:GATE-4#15.2` | yes | `NOT_STARTED` | `NOT_STARTED` | Functional `PASS` requires observable executed evidence; `FAIL`, `BLOCKED`, and justified `NOT_APPLICABLE` remain distinct and are never counted as passing. |
| `REQ-0080` | GATE_SPECIFICATION | `canonical:GATE-4#15.3` | yes | `NOT_STARTED` | `NOT_STARTED` | Completeness fails when a mandatory functional requirement lacks a passing functional scenario with resolved evidence. |
| `REQ-0081` | GATE_SPECIFICATION | `canonical:GATE-4#15.4` | yes | `NOT_STARTED` | `NOT_STARTED` | The mechanism is reusable by later Gates and derives its mandatory functional set from canonical requirements rather than caller arguments. |
| `REQ-0082` | GATE_SPECIFICATION | `canonical:GATE-4#16.1` | yes | `NOT_STARTED` | `NOT_STARTED` | A passing fixture runs through the real evaluator workflow, artifact store, database, Temporal worker, sandbox service, and container engine and derives `PASS`. |
| `REQ-0083` | GATE_SPECIFICATION | `canonical:GATE-4#16.2` | yes | `NOT_STARTED` | `NOT_STARTED` | A failing fixture runs through the same path and derives `FAIL` with the failed check, finding, and evidence preserved. |
| `REQ-0084` | GATE_SPECIFICATION | `canonical:GATE-4#16.3` | yes | `NOT_STARTED` | `NOT_STARTED` | A real snapshot of IACode runs through the engine with its canonical profile, and the verdict is compared with the repository's own mandatory gate results. |
| `REQ-0085` | GATE_SPECIFICATION | `canonical:GATE-4#16.4` | yes | `NOT_STARTED` | `NOT_STARTED` | The passing run is reproduced from stored inputs, and the report proves equal plan identity and equivalent results while preserving distinct run identity. |
| `REQ-0086` | GATE_SPECIFICATION | `canonical:GATE-4#16.5` | yes | `NOT_STARTED` | `NOT_STARTED` | A false-PASS battery removes a result, flips an exit code, forges evidence, changes policy, changes snapshot, posts from the wrong origin, times out, denies, cancels, and supplies an unknown status; every mutation is rejected and a null control passes. |
| `REQ-0087` | GATE_SPECIFICATION | `canonical:GATE-4#17.1` | yes | `NOT_STARTED` | `NOT_STARTED` | Metrics cover planned, active, completed, failed, cancelled, and timed-out runs; check duration/status; findings by bounded severity/category; evidence writes; and verdict derivations. |
| `REQ-0088` | GATE_SPECIFICATION | `canonical:GATE-4#17.2` | yes | `NOT_STARTED` | `NOT_STARTED` | Metric labels are closed and low-cardinality; project path, command, output, finding message, digest, run identifier, and artifact identifier are never labels. |
| `REQ-0089` | GATE_SPECIFICATION | `canonical:GATE-4#17.3` | yes | `NOT_STARTED` | `NOT_STARTED` | Logs carry correlation, run, plan, check, sandbox, status, duration, and reason but never full output, command content, secret, host environment, or evidence body. |
| `REQ-0090` | GATE_SPECIFICATION | `canonical:GATE-4#17.4` | yes | `NOT_STARTED` | `NOT_STARTED` | Prometheus scrapes the evaluator and the operations runbook covers lifecycle, policy, runners, sandbox boundary, evidence, reproduction, recovery, and troubleshooting. |
| `REQ-0091` | GATE_SPECIFICATION | `canonical:GATE-4#18.1` | yes | `NOT_STARTED` | `NOT_STARTED` | A schema-bound program state records current milestone, Gate, checkpoint, step, last completed step, local and remote commits, status, blockers, next action, and update time. |
| `REQ-0092` | GATE_SPECIFICATION | `canonical:GATE-4#18.2` | yes | `NOT_STARTED` | `NOT_STARTED` | Program state is derived and validated against the checkpoint, Git, remote state, and master plan; contradictory or stale state is refused rather than reconciled silently. |
| `REQ-0093` | GATE_SPECIFICATION | `canonical:GATE-4#18.3` | yes | `NOT_STARTED` | `NOT_STARTED` | Each Gate slice records step identity, requirements, expected behavior, implementation, tests, functional proof, evidence, and truthful status. |
| `REQ-0094` | GATE_SPECIFICATION | `canonical:GATE-4#19.1` | yes | `NOT_STARTED` | `NOT_STARTED` | Untrusted project content is data: manifest text, filenames, output, findings, and artifacts cannot alter policy, plan, instruction hierarchy, runner selection, or verdict logic. |
| `REQ-0095` | GATE_SPECIFICATION | `canonical:GATE-4#19.2` | yes | `NOT_STARTED` | `NOT_STARTED` | Secret scanning runs before evidence persistence and before every push; evidence containing a detected secret is quarantined without exposing the value. |
| `REQ-0096` | GATE_SPECIFICATION | `canonical:GATE-4#19.3` | yes | `NOT_STARTED` | `NOT_STARTED` | Every evaluator artifact records provenance, ownership, license, storage/RAG/training/distillation rights, and `trainingAllowed=false` absent explicit rights evidence. |
| `REQ-0097` | GATE_SPECIFICATION | `canonical:GATE-4#19.4` | yes | `NOT_STARTED` | `NOT_STARTED` | Current advisory scans cover every delivered dependency lock and refuse unsuppressed Critical or High findings without narrowing the source set. |
| `REQ-0098` | GATE_SPECIFICATION | `canonical:GATE-4#20.1` | yes | `NOT_STARTED` | `NOT_STARTED` | The repository's one verification command covers evaluator unit, integration, functional, reproduction, recovery, cancellation, timeout, and false-PASS stages in targeted and full modes. |
| `REQ-0099` | GATE_SPECIFICATION | `canonical:GATE-4#20.2` | yes | `NOT_STARTED` | `NOT_STARTED` | Architecture, development, version, entry, and model-usage documents describe the delivered quality engine and its limits rather than planned behavior. |
| `REQ-0100` | GATE_SPECIFICATION | `canonical:GATE-4#20.3` | yes | `NOT_STARTED` | `NOT_STARTED` | Structural decisions for the quality boundary, immutable evidence/verdict derivation, and project profiles/runners are recorded as indexed ADRs. |
| `REQ-0101` | GATE_SPECIFICATION | `canonical:GATE-4#20.4` | yes | `NOT_STARTED` | `NOT_STARTED` | The Gate retrospective records reusable lessons, and every important confirmed failure becomes an effective automated guardrail before handoff. |
| `REQ-0102` | GATE_SPECIFICATION | `canonical:GATE-4#20.5` | yes | `NOT_STARTED` | `NOT_STARTED` | A deterministic review bundle contains the complete checkpoint, changed source, tests, migrations, schemas, policies, documentation, functional acceptance, quality results, Red Team, changeset, Git/remote state, manifest, and checksums; validation opens it, checks hashes and required files, and scans it for secrets. |
| `REQ-0103` | GATE_SPECIFICATION | `canonical:GATE-4#20.6` | yes | `NOT_STARTED` | `NOT_STARTED` | Every Gate commit and the checkpoint tag are on the authorised remote when the Gate reaches its later independent verdict. |
| `REQ-0104` | GATE_SPECIFICATION | `canonical:GATE-4#20.7` | yes | `NOT_STARTED` | `NOT_STARTED` | This implementing run ends at `READY_FOR_REVIEW` with complete functional and quality evidence, no blocker, and no claim of independent validation or Gate pass. |
| `REQ-0105` | GATE_SPECIFICATION | `canonical:GATE-4#20.8` | yes | `NOT_STARTED` | `NOT_STARTED` | A later independent run performs review, Red Team, and the Gate verdict before Gate 5 begins; Gate 4 starts no Gate 5 implementation. |
| `LESSON-REQ-0001` | LESSON | `lesson:LSN-0001` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify checkpoint validation must succeed from a detached checkout of the checkpoint tag |
| `LESSON-REQ-0002` | LESSON | `lesson:LSN-0002` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a file inventory must be recomputed from the repository, never trusted as an assertion |
| `LESSON-REQ-0003` | LESSON | `lesson:LSN-0003` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify every operation attempt must be auditable, including a refusal decided before execution |
| `LESSON-REQ-0004` | LESSON | `lesson:LSN-0004` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a checkpoint may never claim readiness while it also claims to be blocked |
| `LESSON-REQ-0005` | LESSON | `lesson:LSN-0005` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a PASS requires evidence that can be executed or resolved, not a statement |
| `LESSON-REQ-0006` | LESSON | `lesson:LSN-0006` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify the repository must be self-contained; a specification may not live outside it |
| `LESSON-REQ-0007` | LESSON | `lesson:LSN-0007` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify independent validation cannot be declared by the run that did the work |
| `LESSON-REQ-0008` | LESSON | `lesson:LSN-0008` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify requirement completeness must be total and evidence-backed before handoff |
| `LESSON-REQ-0009` | LESSON | `lesson:LSN-0009` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a red gate requires rework, never a waiver, and never a weakened check |
| `LESSON-REQ-0010` | LESSON | `lesson:LSN-0010` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a recorded command must carry runtime, working directory, commit and purpose to be replayable |
| `LESSON-REQ-0011` | LESSON | `lesson:LSN-0011` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a control over a checkpoint's own evidence must be scoped to the moment it matters |
| `LESSON-REQ-0012` | LESSON | `lesson:LSN-0012` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify sealed checkpoints and their tags are immutable, and tooling must keep validating them |
| `LESSON-REQ-0013` | LESSON | `lesson:LSN-0013` | no | `NOT_STARTED` | `NOT_STARTED` | Verify an installed capability must be detected by resolved path, not by a bare command lookup |
| `LESSON-REQ-0014` | LESSON | `lesson:LSN-0014` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify evidence must be recorded as it happens, not reconstructed at the end of a run |
| `LESSON-REQ-0015` | LESSON | `lesson:LSN-0015` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify every positive terminal status needs one shared promotion invariant |
| `LESSON-REQ-0016` | LESSON | `lesson:LSN-0016` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a mandatory set must be closed by policy, never chosen by the caller |
| `LESSON-REQ-0017` | LESSON | `lesson:LSN-0017` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a completeness denominator must come from a source the delivery does not own |
| `LESSON-REQ-0018` | LESSON | `lesson:LSN-0018` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a structured reference must be resolved, not merely well typed |
| `LESSON-REQ-0019` | LESSON | `lesson:LSN-0019` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a derived artifact must carry a fingerprint of the inputs that produced it |
| `LESSON-REQ-0020` | LESSON | `lesson:LSN-0020` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify evidence produced from a dirty tree needs immutable input identity |
| `LESSON-REQ-0021` | LESSON | `lesson:LSN-0021` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify sealed history needs an anchor outside the content it describes |
| `LESSON-REQ-0022` | LESSON | `lesson:LSN-0022` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify an authoritative count must be derived once, never maintained by hand twice |
| `LESSON-REQ-0023` | LESSON | `lesson:LSN-0023` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a lesson must cite a source that actually records the finding it claims |
| `LESSON-REQ-0024` | LESSON | `lesson:LSN-0024` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a control is finished only when its positive path has been executed, not only its refusals |
| `LESSON-REQ-0025` | LESSON | `lesson:LSN-0025` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a generic guardrail derives repository state instead of naming today's checkpoint |
| `LESSON-REQ-0026` | LESSON | `lesson:LSN-0026` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify an adversarial battery without a null-mutation control proves nothing |
| `LESSON-REQ-0027` | LESSON | `lesson:LSN-0027` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a lesson's prose may record a residual limit but may never contradict its status |
| `LESSON-REQ-0028` | LESSON | `lesson:LSN-0028` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a configuration key that no code reads is a defect, not documentation |
| `LESSON-REQ-0029` | LESSON | `lesson:LSN-0029` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a required protocol transition must never turn a mandatory gate red |
| `LESSON-REQ-0030` | LESSON | `lesson:LSN-0031` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify an empty applicable set is not a missing required set, and a control must tell them apart |
| `LESSON-REQ-0031` | LESSON | `lesson:LSN-0032` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a control written while one Gate was the only Gate stops being a control when the next one starts |
| `LESSON-REQ-0032` | LESSON | `lesson:LSN-0033` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a value bound in middleware is absent in the handlers that run outside it |
| `LESSON-REQ-0033` | LESSON | `lesson:LSN-0034` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify re-deriving what the framework already computed diverges from the framework |
| `LESSON-REQ-0034` | LESSON | `lesson:LSN-0035` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify captured subprocess output decoded or re-emitted with the platform codepage crashes the tool, not the work |
| `LESSON-REQ-0035` | LESSON | `lesson:LSN-0036` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a gate that runs inside an image measures the image, not the source |
| `LESSON-REQ-0036` | LESSON | `lesson:LSN-0037` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a shared control that names an identifier the repository derives stops being a control when that identifier moves |
| `LESSON-REQ-0037` | LESSON | `lesson:LSN-0038` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify two representations of one concept in one module disagree, and the safer one loses |
| `LESSON-REQ-0038` | LESSON | `lesson:LSN-0039` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a test that writes to the operational database leaves production data behind |
| `LESSON-REQ-0039` | LESSON | `lesson:LSN-0040` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a control that judges sealed history only runs once a successor anchors it |
| `LESSON-REQ-0040` | LESSON | `lesson:LSN-0041` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify an editing path that consumes a backslash escape leaves a control character, and the control it belonged to silently matches nothing |
| `LESSON-REQ-0041` | LESSON | `lesson:LSN-0042` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a naming convention rewrites a CHECK constraint's name and leaves a UNIQUE constraint's alone |
| `LESSON-REQ-0042` | LESSON | `lesson:LSN-0043` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a log line is not evidence that another process is ready |
| `LESSON-REQ-0043` | LESSON | `lesson:LSN-0044` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a boundary scan must read the code rather than the prose, and must be shown to fire on a mutated module |
| `LESSON-REQ-0044` | LESSON | `lesson:LSN-0045` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a counted test suite must declare its cases statically, because the denominator is read from the source |
| `LESSON-REQ-0045` | LESSON | `lesson:LSN-0046` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a timeout that cancels the task it runs in leaves nothing able to record what happened |
| `LESSON-REQ-0046` | LESSON | `lesson:LSN-0047` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a refusal that misnames the defect spends the only repair on the wrong correction |
| `LESSON-REQ-0047` | LESSON | `lesson:LSN-0048` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a state and the event that explains it, written in two commits, are written event first |
| `LESSON-REQ-0048` | LESSON | `lesson:LSN-0049` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a metric read the instant after the call that moved it is read before the scrape that carries it |
| `LESSON-REQ-0049` | LESSON | `lesson:LSN-0050` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a checkpoint sealed without naming its own tag cannot be validated from that tag |
| `LESSON-REQ-0050` | LESSON | `lesson:LSN-0051` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a payload one service bounds for another must be bounded as the receiver measures it |
| `LESSON-REQ-0051` | LESSON | `lesson:LSN-0052` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify two processes that meet on a queue must name what crosses it once, and a real run must exercise both |
| `LESSON-REQ-0052` | LESSON | `lesson:LSN-0053` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a process sweep that reads what a forking process holds waits on the processes it has to kill |
| `LESSON-REQ-0053` | LESSON | `lesson:LSN-0054` | no | `NOT_STARTED` | `NOT_STARTED` | Verify a pre-push check narrower than the change's reach lets a red gate reach the public remote |
| `LESSON-REQ-0054` | LESSON | `lesson:LSN-0055` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a contract a model must follow has to reach the model, rendered from the definition the parser enforces |
| `LESSON-REQ-0055` | LESSON | `lesson:LSN-0056` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a result is accepted only from the executor that owns the request, decided when the request is created |
| `LESSON-REQ-0056` | LESSON | `lesson:LSN-0057` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a pinned lock can become unsafe without changing, so advisory state is live evidence |
| `LESSON-REQ-0057` | LESSON | `lesson:LSN-0058` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify container health does not prove Docker Desktop host-port forwarding |
| `LESSON-REQ-0058` | LESSON | `lesson:LSN-0059` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a lesson exclusion must declare the scope it excludes |
| `LESSON-REQ-0059` | LESSON | `lesson:LSN-0060` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify parent and child facts without an ORM relationship require an explicit flush boundary |
| `LESSON-REQ-0060` | LESSON | `lesson:LSN-0061` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify cancellation completion must not bypass cleanup acknowledgement |
| `LESSON-REQ-0061` | LESSON | `lesson:LSN-0062` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify provenance digests are a set even when their sources are distinct |
| `LESSON-REQ-0062` | LESSON | `lesson:LSN-0063` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify an identity shared across services must satisfy the strictest persistence type and remain stable |
| `LESSON-REQ-0063` | LESSON | `lesson:LSN-0064` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a shared execution resource needs an explicit exclusive owner for every owning domain |
| `LESSON-REQ-0064` | LESSON | `lesson:LSN-0065` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a shared execution identifier must not be written into a foreign key owned by another domain |
| `LESSON-REQ-0065` | LESSON | `lesson:LSN-0066` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify immutable content identity excludes observation time and the first observer |
| `LESSON-REQ-0066` | LESSON | `lesson:LSN-0067` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify cancellation semantics must survive orchestration-library exception wrapping |

## Evidence

### REQ-0001 - canonical:GATE-4#1.1

- Source reference: docs/GATE-4-CHECKLIST.md row 1.1
- Description: This checklist is the canonical, machine-readable requirement source for the Gate and its registry mirror has exactly the same ordered rows.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0002 - canonical:GATE-4#1.2

- Source reference: docs/GATE-4-CHECKLIST.md row 1.2
- Description: The evaluator reservation is consumed by this Gate while every later-Gate reservation remains enforced.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0003 - canonical:GATE-4#1.3

- Source reference: docs/GATE-4-CHECKLIST.md row 1.3
- Description: The closed mandatory gate registry includes an evaluator gate that builds every image it executes before measuring it.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0004 - canonical:GATE-4#1.4

- Source reference: docs/GATE-4-CHECKLIST.md row 1.4
- Description: The evaluator suite is canonical, counted, and available to evidence resolution.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0005 - canonical:GATE-4#1.5

- Source reference: docs/GATE-4-CHECKLIST.md row 1.5
- Description: Gate 4 introduces no held-out model evaluation capability reserved for Gate 20 and no CLI or VS Code capability reserved for Gate 5.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0006 - canonical:GATE-4#1.6

- Source reference: docs/GATE-4-CHECKLIST.md row 1.6
- Description: Generated review archives are permanently excluded from Git, while their validation result and digest remain checkpoint evidence.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0007 - canonical:GATE-4#2.1

- Source reference: docs/GATE-4-CHECKLIST.md row 2.1
- Description: Versioned contracts exist for `QualityPlan`, `QualityCheck`, `QualityRun`, `QualityResult`, `QualityFinding`, `QualityEvidence`, `QualityPolicy`, and `QualityVerdict`.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0008 - canonical:GATE-4#2.2

- Source reference: docs/GATE-4-CHECKLIST.md row 2.2
- Description: Contract vocabularies are closed and reject missing fields, extra fields, wrong types, invalid values, duplicate identifiers, and unsupported versions with distinct reasons.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0009 - canonical:GATE-4#2.3

- Source reference: docs/GATE-4-CHECKLIST.md row 2.3
- Description: Every contract round-trips without losing identity, ordering, timestamps, digests, policy references, sandbox references, or artifact references.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0010 - canonical:GATE-4#2.4

- Source reference: docs/GATE-4-CHECKLIST.md row 2.4
- Description: Every reusable artifact defaults to `trainingAllowed=false`; a quality contract carries no credential, secret, chain-of-thought, or whole environment.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0011 - canonical:GATE-4#2.5

- Source reference: docs/GATE-4-CHECKLIST.md row 2.5
- Description: Payload sizes are bounded as the receiver measures them, and oversized plans, output summaries, findings, and evidence metadata are refused before persistence.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0012 - canonical:GATE-4#3.1

- Source reference: docs/GATE-4-CHECKLIST.md row 3.1
- Description: A project profile records the detected stacks, manifests, workspace root, configuration source, confidence, and unresolved ambiguity without depending on IACode-specific paths.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0013 - canonical:GATE-4#3.2

- Source reference: docs/GATE-4-CHECKLIST.md row 3.2
- Description: Detection recognizes Python, Node, TypeScript, Angular, Maven, and Gradle from repository evidence and supports mixed projects.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0014 - canonical:GATE-4#3.3

- Source reference: docs/GATE-4-CHECKLIST.md row 3.3
- Description: Detection never executes project code, follows no symlink outside the snapshot, ignores generated/vendor directories, and reads only bounded manifest content.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0015 - canonical:GATE-4#3.4

- Source reference: docs/GATE-4-CHECKLIST.md row 3.4
- Description: Ambiguous or unknown toolchains produce an explicit unsupported/ambiguous result and never an invented stack or a false `PASS`.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0016 - canonical:GATE-4#3.5

- Source reference: docs/GATE-4-CHECKLIST.md row 3.5
- Description: A versioned project configuration may select declared checks and commands but cannot select an image, mount, network, resource bound, verdict, or undeclared runner.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0017 - canonical:GATE-4#3.6

- Source reference: docs/GATE-4-CHECKLIST.md row 3.6
- Description: The same source code onboards Python, Java, and TypeScript/Node fixtures through profiles rather than repository-specific branches.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0018 - canonical:GATE-4#4.1

- Source reference: docs/GATE-4-CHECKLIST.md row 4.1
- Description: One canonical policy registry declares profiles, runners, mandatory checks, applicability, timeouts, output limits, evidence requirements, and verdict rules.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0019 - canonical:GATE-4#4.2

- Source reference: docs/GATE-4-CHECKLIST.md row 4.2
- Description: Unknown policy keys, runner names, check kinds, result states, evidence kinds, or verdict rules are refused when policy loads.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0020 - canonical:GATE-4#4.3

- Source reference: docs/GATE-4-CHECKLIST.md row 4.3
- Description: The requested project configuration may add checks or lower limits but cannot remove a mandatory check, raise a limit, weaken a threshold, or alter a verdict rule.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0021 - canonical:GATE-4#4.4

- Source reference: docs/GATE-4-CHECKLIST.md row 4.4
- Description: Applicability is derived from the project profile: an empty applicable set is justified `NOT_APPLICABLE`, while a missing required set is `FAIL`.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0022 - canonical:GATE-4#4.5

- Source reference: docs/GATE-4-CHECKLIST.md row 4.5
- Description: Every policy key has an implementation consumer, and the policy and its schema are content-addressed inputs to every plan.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0023 - canonical:GATE-4#5.1

- Source reference: docs/GATE-4-CHECKLIST.md row 5.1
- Description: Planning freezes the project snapshot checksum, profile, policy digest, ordered checks, commands, runner images, limits, and environment before execution begins.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0024 - canonical:GATE-4#5.2

- Source reference: docs/GATE-4-CHECKLIST.md row 5.2
- Description: Plan identity is a deterministic digest of canonical content; equal inputs produce the same plan and any material input change produces a different plan.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0025 - canonical:GATE-4#5.3

- Source reference: docs/GATE-4-CHECKLIST.md row 5.3
- Description: Check identifiers are unique, stable, and independent of execution order; dependencies form an acyclic graph and unknown dependencies are refused.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0026 - canonical:GATE-4#5.4

- Source reference: docs/GATE-4-CHECKLIST.md row 5.4
- Description: A plan cannot carry a caller-authored expected verdict, result, evidence digest, sandbox result, or hidden command.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0027 - canonical:GATE-4#5.5

- Source reference: docs/GATE-4-CHECKLIST.md row 5.5
- Description: The plan exposes why every check is mandatory, optional, or not applicable and identifies the policy rule that decided it.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0028 - canonical:GATE-4#6.1

- Source reference: docs/GATE-4-CHECKLIST.md row 6.1
- Description: A closed runner registry maps declared runner identifiers to structured sandbox command requests; unknown identifiers never fall back to a shell command.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0029 - canonical:GATE-4#6.2

- Source reference: docs/GATE-4-CHECKLIST.md row 6.2
- Description: Initial check kinds cover build, unit, integration, lint, static analysis, dependency/security, secret scan, configured coverage, applicable migration checks, and diff integrity.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0030 - canonical:GATE-4#6.3

- Source reference: docs/GATE-4-CHECKLIST.md row 6.3
- Description: Commands are argument vectors or policy-owned command text, never concatenated from untrusted project values, and every working directory resolves within the snapshot.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0031 - canonical:GATE-4#6.4

- Source reference: docs/GATE-4-CHECKLIST.md row 6.4
- Description: A runner normalizes exit code, timeout, denial, cancellation, truncation, duration, sandbox identity, and artifacts without inventing an exit code for work that never started.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0032 - canonical:GATE-4#6.5

- Source reference: docs/GATE-4-CHECKLIST.md row 6.5
- Description: Required checks execute despite an earlier failure unless their declared dependency makes execution impossible; every skipped check records the exact dependency reason.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0033 - canonical:GATE-4#6.6

- Source reference: docs/GATE-4-CHECKLIST.md row 6.6
- Description: A cancelled or timed-out run reaches one terminal state, records the reason before the state, and leaves no running check or sandbox session.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0034 - canonical:GATE-4#7.1

- Source reference: docs/GATE-4-CHECKLIST.md row 7.1
- Description: Every project command is dispatched through the Gate 3 sandbox task queue; the evaluator, API, orchestrator, and host never execute a project command.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0035 - canonical:GATE-4#7.2

- Source reference: docs/GATE-4-CHECKLIST.md row 7.2
- Description: Only the sandbox service has the container engine socket, and the evaluator service has no host mount, project bind mount, credential, or engine access.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0036 - canonical:GATE-4#7.3

- Source reference: docs/GATE-4-CHECKLIST.md row 7.3
- Description: The executor origin is frozen as `EVALUATOR` when a quality check is created; a result from another origin is refused before storage.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0037 - canonical:GATE-4#7.4

- Source reference: docs/GATE-4-CHECKLIST.md row 7.4
- Description: The snapshot, policy, image, resources, network, mounts, and limits cannot be changed by an executing check or its project.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0038 - canonical:GATE-4#7.5

- Source reference: docs/GATE-4-CHECKLIST.md row 7.5
- Description: A host sentinel and host process observation prove that passing and failing fixtures execute inside the sandbox and cause no host side effect.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0039 - canonical:GATE-4#8.1

- Source reference: docs/GATE-4-CHECKLIST.md row 8.1
- Description: Python projects have policy-owned runners for build/package validation, unit/integration tests, lint/static checks, dependency/security, secret, configured coverage, migration, and diff integrity as applicable.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0040 - canonical:GATE-4#8.2

- Source reference: docs/GATE-4-CHECKLIST.md row 8.2
- Description: Node and TypeScript projects have policy-owned runners for install integrity, build, unit/integration tests, lint/static checks, dependency/security, secret, configured coverage, migration, and diff integrity as applicable.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0041 - canonical:GATE-4#8.3

- Source reference: docs/GATE-4-CHECKLIST.md row 8.3
- Description: Angular projects have policy-owned runners for production build, unit tests, lint/static checks, dependency/security, secret, configured coverage, and diff integrity.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0042 - canonical:GATE-4#8.4

- Source reference: docs/GATE-4-CHECKLIST.md row 8.4
- Description: Maven projects have policy-owned runners for package, unit/integration tests, static checks, dependency/security, secret, configured coverage, migration, and diff integrity as applicable.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0043 - canonical:GATE-4#8.5

- Source reference: docs/GATE-4-CHECKLIST.md row 8.5
- Description: Gradle projects have policy-owned runners for build, unit/integration tests, static checks, dependency/security, secret, configured coverage, migration, and diff integrity as applicable.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0044 - canonical:GATE-4#8.6

- Source reference: docs/GATE-4-CHECKLIST.md row 8.6
- Description: Sandbox image profiles are extensible and content-addressed; a missing or stale required image is a recorded failure and never silently replaced.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0045 - canonical:GATE-4#8.7

- Source reference: docs/GATE-4-CHECKLIST.md row 8.7
- Description: Dependency installation and checks have no internet access; lockfiles and prebuilt image toolchains decide what can execute reproducibly.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0046 - canonical:GATE-4#9.1

- Source reference: docs/GATE-4-CHECKLIST.md row 9.1
- Description: Quality evidence uses the existing artifact store and records a content digest, byte size, media type, producer, source inputs, creation time, retention class, and rights.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0047 - canonical:GATE-4#9.2

- Source reference: docs/GATE-4-CHECKLIST.md row 9.2
- Description: Evidence is content-addressed and immutable: a digest collision with different bytes, overwrite, rename, or deletion through the evaluator is refused.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0048 - canonical:GATE-4#9.3

- Source reference: docs/GATE-4-CHECKLIST.md row 9.3
- Description: A stored evidence reference is resolved and re-hashed before it can support a verdict; missing, truncated-without-artifact, or digest-mismatched evidence fails the run.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0049 - canonical:GATE-4#9.4

- Source reference: docs/GATE-4-CHECKLIST.md row 9.4
- Description: Inline summaries are bounded and secret-redacted; complete output is an artifact, never a database field, API response, metric label, or log record.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0050 - canonical:GATE-4#9.5

- Source reference: docs/GATE-4-CHECKLIST.md row 9.5
- Description: Evidence reproduction replays the frozen plan against the same snapshot and policy, records a new run, and compares result/evidence digests without rewriting the original.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0051 - canonical:GATE-4#10.1

- Source reference: docs/GATE-4-CHECKLIST.md row 10.1
- Description: Each check produces exactly one terminal result and zero or more typed findings linked to resolvable evidence.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0052 - canonical:GATE-4#10.2

- Source reference: docs/GATE-4-CHECKLIST.md row 10.2
- Description: A mandatory failure, denial, timeout, cancellation, execution error, missing result, unresolved evidence, stale input, or incomplete check set makes the verdict `FAIL`.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0053 - canonical:GATE-4#10.3

- Source reference: docs/GATE-4-CHECKLIST.md row 10.3
- Description: `PASS` requires the exact applicable mandatory set, every result successful, every required evidence reference resolved, and every configured threshold satisfied.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0054 - canonical:GATE-4#10.4

- Source reference: docs/GATE-4-CHECKLIST.md row 10.4
- Description: Coverage is evaluated only when configured; below-threshold or unreadable coverage fails, while legitimately unconfigured coverage is justified `NOT_APPLICABLE` and never counted as `PASS`.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0055 - canonical:GATE-4#10.5

- Source reference: docs/GATE-4-CHECKLIST.md row 10.5
- Description: Severity, category, location, fingerprint, message, check identity, and evidence identify a finding; equal findings deduplicate deterministically without hiding recurrence.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0056 - canonical:GATE-4#10.6

- Source reference: docs/GATE-4-CHECKLIST.md row 10.6
- Description: The verdict is a pure derivation from the frozen policy, plan, results, and resolved evidence; no API, runner, database row, or caller may submit it.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0057 - canonical:GATE-4#10.7

- Source reference: docs/GATE-4-CHECKLIST.md row 10.7
- Description: Re-deriving a stored verdict must produce the same value and digest; disagreement marks the run invalid and never overwrites history.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0058 - canonical:GATE-4#11.1

- Source reference: docs/GATE-4-CHECKLIST.md row 11.1
- Description: Relational persistence records quality plans, runs, checks, results, findings, evidence references, verdicts, and append-only run events with foreign keys and closed status constraints.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0059 - canonical:GATE-4#11.2

- Source reference: docs/GATE-4-CHECKLIST.md row 11.2
- Description: Plan content, result content, and verdict content are immutable after insertion; lifecycle updates may change only the declared run state and timestamps.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0060 - canonical:GATE-4#11.3

- Source reference: docs/GATE-4-CHECKLIST.md row 11.3
- Description: Idempotency keys and uniqueness constraints make duplicate create, dispatch, callback, event, and verdict operations return the recorded fact rather than create a second one.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0061 - canonical:GATE-4#11.4

- Source reference: docs/GATE-4-CHECKLIST.md row 11.4
- Description: The event that explains a state is committed before the state a reader may act on, including every terminal transition.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0062 - canonical:GATE-4#11.5

- Source reference: docs/GATE-4-CHECKLIST.md row 11.5
- Description: Migration `0006` upgrades from zero and from `0005`, downgrades cleanly, and leaves no Alembic autogenerate diff.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0063 - canonical:GATE-4#11.6

- Source reference: docs/GATE-4-CHECKLIST.md row 11.6
- Description: No quality table stores a credential, full command output, host environment, or training eligibility defaulting to true.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0064 - canonical:GATE-4#12.1

- Source reference: docs/GATE-4-CHECKLIST.md row 12.1
- Description: A durable workflow plans, starts, executes, cancels, resumes, reproduces, and finishes a quality run with a queryable event history.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0065 - canonical:GATE-4#12.2

- Source reference: docs/GATE-4-CHECKLIST.md row 12.2
- Description: A worker restart during a check preserves the run identity and either receives the owned result or records an explicit failure; it never silently passes or duplicates execution.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0066 - canonical:GATE-4#12.3

- Source reference: docs/GATE-4-CHECKLIST.md row 12.3
- Description: Cancellation is idempotent, propagates to the sandbox, refuses late results, and finishes only after cleanup is observed.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0067 - canonical:GATE-4#12.4

- Source reference: docs/GATE-4-CHECKLIST.md row 12.4
- Description: A run deadline and per-check deadlines are policy-owned; when either fires, the store still records the event, result, and terminal verdict.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0068 - canonical:GATE-4#12.5

- Source reference: docs/GATE-4-CHECKLIST.md row 12.5
- Description: The evaluator health check proves a Temporal poller, database access, artifact-store access, and sandbox availability rather than process existence.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0069 - canonical:GATE-4#13.1

- Source reference: docs/GATE-4-CHECKLIST.md row 13.1
- Description: A stable internal service API creates a profile and plan, starts a run, retrieves plan/run/results/findings/evidence metadata/verdict, cancels a run, and requests reproduction.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0070 - canonical:GATE-4#13.2

- Source reference: docs/GATE-4-CHECKLIST.md row 13.2
- Description: The HTTP API exposes the stable quality lifecycle for the future Gate 5 client without exposing commands, credentials, full output, host paths, mutable verdicts, or direct sandbox control.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0071 - canonical:GATE-4#13.3

- Source reference: docs/GATE-4-CHECKLIST.md row 13.3
- Description: List and event endpoints are bounded and cursor-paginated; a terminal stream drains every event after the cursor before closing.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0072 - canonical:GATE-4#13.4

- Source reference: docs/GATE-4-CHECKLIST.md row 13.4
- Description: Every response, including validation errors and failures outside middleware, carries correlation identity and canonical error code.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0073 - canonical:GATE-4#13.5

- Source reference: docs/GATE-4-CHECKLIST.md row 13.5
- Description: API input selects only a snapshot and declared policy/configuration; no request field selects a command, runner implementation, sandbox image, limit, evidence, result, or verdict.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0074 - canonical:GATE-4#14.1

- Source reference: docs/GATE-4-CHECKLIST.md row 14.1
- Description: An agent run may request a quality plan for its frozen workspace snapshot and receives only the bounded plan identity and applicable check summary.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0075 - canonical:GATE-4#14.2

- Source reference: docs/GATE-4-CHECKLIST.md row 14.2
- Description: A quality run is owned by its requesting agent run, and a result or callback from another owner/origin is refused before storage or workflow signalling.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0076 - canonical:GATE-4#14.3

- Source reference: docs/GATE-4-CHECKLIST.md row 14.3
- Description: The agent receives the derived verdict, findings summary, and artifact references as labelled tool data, never as an instruction or unbounded output.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0077 - canonical:GATE-4#14.4

- Source reference: docs/GATE-4-CHECKLIST.md row 14.4
- Description: Quality failure cannot be transformed into agent-run success by prose, review approval, a missing callback, or a manually posted result.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0078 - canonical:GATE-4#15.1

- Source reference: docs/GATE-4-CHECKLIST.md row 15.1
- Description: A schema-bound functional acceptance artifact records requirement, feature, scenario, environment, preconditions, execution, expected, observed, result, evidence, timestamp, and artifact references.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0079 - canonical:GATE-4#15.2

- Source reference: docs/GATE-4-CHECKLIST.md row 15.2
- Description: Functional `PASS` requires observable executed evidence; `FAIL`, `BLOCKED`, and justified `NOT_APPLICABLE` remain distinct and are never counted as passing.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0080 - canonical:GATE-4#15.3

- Source reference: docs/GATE-4-CHECKLIST.md row 15.3
- Description: Completeness fails when a mandatory functional requirement lacks a passing functional scenario with resolved evidence.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0081 - canonical:GATE-4#15.4

- Source reference: docs/GATE-4-CHECKLIST.md row 15.4
- Description: The mechanism is reusable by later Gates and derives its mandatory functional set from canonical requirements rather than caller arguments.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0082 - canonical:GATE-4#16.1

- Source reference: docs/GATE-4-CHECKLIST.md row 16.1
- Description: A passing fixture runs through the real evaluator workflow, artifact store, database, Temporal worker, sandbox service, and container engine and derives `PASS`.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0083 - canonical:GATE-4#16.2

- Source reference: docs/GATE-4-CHECKLIST.md row 16.2
- Description: A failing fixture runs through the same path and derives `FAIL` with the failed check, finding, and evidence preserved.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0084 - canonical:GATE-4#16.3

- Source reference: docs/GATE-4-CHECKLIST.md row 16.3
- Description: A real snapshot of IACode runs through the engine with its canonical profile, and the verdict is compared with the repository's own mandatory gate results.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0085 - canonical:GATE-4#16.4

- Source reference: docs/GATE-4-CHECKLIST.md row 16.4
- Description: The passing run is reproduced from stored inputs, and the report proves equal plan identity and equivalent results while preserving distinct run identity.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0086 - canonical:GATE-4#16.5

- Source reference: docs/GATE-4-CHECKLIST.md row 16.5
- Description: A false-PASS battery removes a result, flips an exit code, forges evidence, changes policy, changes snapshot, posts from the wrong origin, times out, denies, cancels, and supplies an unknown status; every mutation is rejected and a null control passes.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0087 - canonical:GATE-4#17.1

- Source reference: docs/GATE-4-CHECKLIST.md row 17.1
- Description: Metrics cover planned, active, completed, failed, cancelled, and timed-out runs; check duration/status; findings by bounded severity/category; evidence writes; and verdict derivations.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0088 - canonical:GATE-4#17.2

- Source reference: docs/GATE-4-CHECKLIST.md row 17.2
- Description: Metric labels are closed and low-cardinality; project path, command, output, finding message, digest, run identifier, and artifact identifier are never labels.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0089 - canonical:GATE-4#17.3

- Source reference: docs/GATE-4-CHECKLIST.md row 17.3
- Description: Logs carry correlation, run, plan, check, sandbox, status, duration, and reason but never full output, command content, secret, host environment, or evidence body.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0090 - canonical:GATE-4#17.4

- Source reference: docs/GATE-4-CHECKLIST.md row 17.4
- Description: Prometheus scrapes the evaluator and the operations runbook covers lifecycle, policy, runners, sandbox boundary, evidence, reproduction, recovery, and troubleshooting.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0091 - canonical:GATE-4#18.1

- Source reference: docs/GATE-4-CHECKLIST.md row 18.1
- Description: A schema-bound program state records current milestone, Gate, checkpoint, step, last completed step, local and remote commits, status, blockers, next action, and update time.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0092 - canonical:GATE-4#18.2

- Source reference: docs/GATE-4-CHECKLIST.md row 18.2
- Description: Program state is derived and validated against the checkpoint, Git, remote state, and master plan; contradictory or stale state is refused rather than reconciled silently.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0093 - canonical:GATE-4#18.3

- Source reference: docs/GATE-4-CHECKLIST.md row 18.3
- Description: Each Gate slice records step identity, requirements, expected behavior, implementation, tests, functional proof, evidence, and truthful status.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0094 - canonical:GATE-4#19.1

- Source reference: docs/GATE-4-CHECKLIST.md row 19.1
- Description: Untrusted project content is data: manifest text, filenames, output, findings, and artifacts cannot alter policy, plan, instruction hierarchy, runner selection, or verdict logic.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0095 - canonical:GATE-4#19.2

- Source reference: docs/GATE-4-CHECKLIST.md row 19.2
- Description: Secret scanning runs before evidence persistence and before every push; evidence containing a detected secret is quarantined without exposing the value.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0096 - canonical:GATE-4#19.3

- Source reference: docs/GATE-4-CHECKLIST.md row 19.3
- Description: Every evaluator artifact records provenance, ownership, license, storage/RAG/training/distillation rights, and `trainingAllowed=false` absent explicit rights evidence.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0097 - canonical:GATE-4#19.4

- Source reference: docs/GATE-4-CHECKLIST.md row 19.4
- Description: Current advisory scans cover every delivered dependency lock and refuse unsuppressed Critical or High findings without narrowing the source set.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0098 - canonical:GATE-4#20.1

- Source reference: docs/GATE-4-CHECKLIST.md row 20.1
- Description: The repository's one verification command covers evaluator unit, integration, functional, reproduction, recovery, cancellation, timeout, and false-PASS stages in targeted and full modes.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0099 - canonical:GATE-4#20.2

- Source reference: docs/GATE-4-CHECKLIST.md row 20.2
- Description: Architecture, development, version, entry, and model-usage documents describe the delivered quality engine and its limits rather than planned behavior.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0100 - canonical:GATE-4#20.3

- Source reference: docs/GATE-4-CHECKLIST.md row 20.3
- Description: Structural decisions for the quality boundary, immutable evidence/verdict derivation, and project profiles/runners are recorded as indexed ADRs.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0101 - canonical:GATE-4#20.4

- Source reference: docs/GATE-4-CHECKLIST.md row 20.4
- Description: The Gate retrospective records reusable lessons, and every important confirmed failure becomes an effective automated guardrail before handoff.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0102 - canonical:GATE-4#20.5

- Source reference: docs/GATE-4-CHECKLIST.md row 20.5
- Description: A deterministic review bundle contains the complete checkpoint, changed source, tests, migrations, schemas, policies, documentation, functional acceptance, quality results, Red Team, changeset, Git/remote state, manifest, and checksums; validation opens it, checks hashes and required files, and scans it for secrets.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0103 - canonical:GATE-4#20.6

- Source reference: docs/GATE-4-CHECKLIST.md row 20.6
- Description: Every Gate commit and the checkpoint tag are on the authorised remote when the Gate reaches its later independent verdict.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0104 - canonical:GATE-4#20.7

- Source reference: docs/GATE-4-CHECKLIST.md row 20.7
- Description: This implementing run ends at `READY_FOR_REVIEW` with complete functional and quality evidence, no blocker, and no claim of independent validation or Gate pass.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0105 - canonical:GATE-4#20.8

- Source reference: docs/GATE-4-CHECKLIST.md row 20.8
- Description: A later independent run performs review, Red Team, and the Gate verdict before Gate 5 begins; Gate 4 starts no Gate 5 implementation.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0001 - lesson:LSN-0001

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0001
- Description: Verify checkpoint validation must succeed from a detached checkout of the checkpoint tag
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0002 - lesson:LSN-0002

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0002
- Description: Verify a file inventory must be recomputed from the repository, never trusted as an assertion
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0003 - lesson:LSN-0003

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0003
- Description: Verify every operation attempt must be auditable, including a refusal decided before execution
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0004 - lesson:LSN-0004

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0004
- Description: Verify a checkpoint may never claim readiness while it also claims to be blocked
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0005 - lesson:LSN-0005

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0005
- Description: Verify a PASS requires evidence that can be executed or resolved, not a statement
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0006 - lesson:LSN-0006

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0006
- Description: Verify the repository must be self-contained; a specification may not live outside it
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0007 - lesson:LSN-0007

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0007
- Description: Verify independent validation cannot be declared by the run that did the work
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0008 - lesson:LSN-0008

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0008
- Description: Verify requirement completeness must be total and evidence-backed before handoff
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0009 - lesson:LSN-0009

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0009
- Description: Verify a red gate requires rework, never a waiver, and never a weakened check
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0010 - lesson:LSN-0010

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0010
- Description: Verify a recorded command must carry runtime, working directory, commit and purpose to be replayable
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0011 - lesson:LSN-0011

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0011
- Description: Verify a control over a checkpoint's own evidence must be scoped to the moment it matters
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0012 - lesson:LSN-0012

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0012
- Description: Verify sealed checkpoints and their tags are immutable, and tooling must keep validating them
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0013 - lesson:LSN-0013

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0013
- Description: Verify an installed capability must be detected by resolved path, not by a bare command lookup
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0014 - lesson:LSN-0014

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0014
- Description: Verify evidence must be recorded as it happens, not reconstructed at the end of a run
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0015 - lesson:LSN-0015

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0015
- Description: Verify every positive terminal status needs one shared promotion invariant
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0016 - lesson:LSN-0016

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0016
- Description: Verify a mandatory set must be closed by policy, never chosen by the caller
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0017 - lesson:LSN-0017

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0017
- Description: Verify a completeness denominator must come from a source the delivery does not own
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0018 - lesson:LSN-0018

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0018
- Description: Verify a structured reference must be resolved, not merely well typed
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0019 - lesson:LSN-0019

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0019
- Description: Verify a derived artifact must carry a fingerprint of the inputs that produced it
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0020 - lesson:LSN-0020

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0020
- Description: Verify evidence produced from a dirty tree needs immutable input identity
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0021 - lesson:LSN-0021

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0021
- Description: Verify sealed history needs an anchor outside the content it describes
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0022 - lesson:LSN-0022

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0022
- Description: Verify an authoritative count must be derived once, never maintained by hand twice
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0023 - lesson:LSN-0023

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0023
- Description: Verify a lesson must cite a source that actually records the finding it claims
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0024 - lesson:LSN-0024

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0024
- Description: Verify a control is finished only when its positive path has been executed, not only its refusals
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0025 - lesson:LSN-0025

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0025
- Description: Verify a generic guardrail derives repository state instead of naming today's checkpoint
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0026 - lesson:LSN-0026

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0026
- Description: Verify an adversarial battery without a null-mutation control proves nothing
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0027 - lesson:LSN-0027

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0027
- Description: Verify a lesson's prose may record a residual limit but may never contradict its status
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0028 - lesson:LSN-0028

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0028
- Description: Verify a configuration key that no code reads is a defect, not documentation
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0029 - lesson:LSN-0029

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0029
- Description: Verify a required protocol transition must never turn a mandatory gate red
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0030 - lesson:LSN-0031

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0030
- Description: Verify an empty applicable set is not a missing required set, and a control must tell them apart
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0031 - lesson:LSN-0032

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0031
- Description: Verify a control written while one Gate was the only Gate stops being a control when the next one starts
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0032 - lesson:LSN-0033

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0032
- Description: Verify a value bound in middleware is absent in the handlers that run outside it
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0033 - lesson:LSN-0034

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0033
- Description: Verify re-deriving what the framework already computed diverges from the framework
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0034 - lesson:LSN-0035

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0034
- Description: Verify captured subprocess output decoded or re-emitted with the platform codepage crashes the tool, not the work
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0035 - lesson:LSN-0036

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0035
- Description: Verify a gate that runs inside an image measures the image, not the source
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0036 - lesson:LSN-0037

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0036
- Description: Verify a shared control that names an identifier the repository derives stops being a control when that identifier moves
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0037 - lesson:LSN-0038

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0037
- Description: Verify two representations of one concept in one module disagree, and the safer one loses
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0038 - lesson:LSN-0039

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0038
- Description: Verify a test that writes to the operational database leaves production data behind
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0039 - lesson:LSN-0040

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0039
- Description: Verify a control that judges sealed history only runs once a successor anchors it
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0040 - lesson:LSN-0041

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0040
- Description: Verify an editing path that consumes a backslash escape leaves a control character, and the control it belonged to silently matches nothing
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0041 - lesson:LSN-0042

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0041
- Description: Verify a naming convention rewrites a CHECK constraint's name and leaves a UNIQUE constraint's alone
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0042 - lesson:LSN-0043

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0042
- Description: Verify a log line is not evidence that another process is ready
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0043 - lesson:LSN-0044

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0043
- Description: Verify a boundary scan must read the code rather than the prose, and must be shown to fire on a mutated module
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0044 - lesson:LSN-0045

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0044
- Description: Verify a counted test suite must declare its cases statically, because the denominator is read from the source
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0045 - lesson:LSN-0046

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0045
- Description: Verify a timeout that cancels the task it runs in leaves nothing able to record what happened
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0046 - lesson:LSN-0047

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0046
- Description: Verify a refusal that misnames the defect spends the only repair on the wrong correction
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0047 - lesson:LSN-0048

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0047
- Description: Verify a state and the event that explains it, written in two commits, are written event first
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0048 - lesson:LSN-0049

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0048
- Description: Verify a metric read the instant after the call that moved it is read before the scrape that carries it
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0049 - lesson:LSN-0050

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0049
- Description: Verify a checkpoint sealed without naming its own tag cannot be validated from that tag
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0050 - lesson:LSN-0051

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0050
- Description: Verify a payload one service bounds for another must be bounded as the receiver measures it
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0051 - lesson:LSN-0052

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0051
- Description: Verify two processes that meet on a queue must name what crosses it once, and a real run must exercise both
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0052 - lesson:LSN-0053

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0052
- Description: Verify a process sweep that reads what a forking process holds waits on the processes it has to kill
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0053 - lesson:LSN-0054

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0053
- Description: Verify a pre-push check narrower than the change's reach lets a red gate reach the public remote
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0054 - lesson:LSN-0055

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0054
- Description: Verify a contract a model must follow has to reach the model, rendered from the definition the parser enforces
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0055 - lesson:LSN-0056

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0055
- Description: Verify a result is accepted only from the executor that owns the request, decided when the request is created
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0056 - lesson:LSN-0057

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0056
- Description: Verify a pinned lock can become unsafe without changing, so advisory state is live evidence
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0057 - lesson:LSN-0058

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0057
- Description: Verify container health does not prove Docker Desktop host-port forwarding
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0058 - lesson:LSN-0059

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0058
- Description: Verify a lesson exclusion must declare the scope it excludes
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0059 - lesson:LSN-0060

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0059
- Description: Verify parent and child facts without an ORM relationship require an explicit flush boundary
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0060 - lesson:LSN-0061

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0060
- Description: Verify cancellation completion must not bypass cleanup acknowledgement
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0061 - lesson:LSN-0062

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0061
- Description: Verify provenance digests are a set even when their sources are distinct
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0062 - lesson:LSN-0063

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0062
- Description: Verify an identity shared across services must satisfy the strictest persistence type and remain stable
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0063 - lesson:LSN-0064

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0063
- Description: Verify a shared execution resource needs an explicit exclusive owner for every owning domain
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0064 - lesson:LSN-0065

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0064
- Description: Verify a shared execution identifier must not be written into a foreign key owned by another domain
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0065 - lesson:LSN-0066

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0065
- Description: Verify immutable content identity excludes observation time and the first observer
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0066 - lesson:LSN-0067

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0066
- Description: Verify cancellation semantics must survive orchestration-library exception wrapping
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_
