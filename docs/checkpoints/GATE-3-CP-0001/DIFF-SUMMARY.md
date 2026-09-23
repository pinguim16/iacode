# Diff Summary — GATE-3-CP-0001

Measured against `d4a3998ce745dcbfcf6a8498f267ee302834543f`, the seal of `GATE-2-CP-0002`
(`INTERNAL_GATE_PASS`). Every commit between the two is on `origin/main`.

## What was added

**`services/sandbox/`** — the sandbox service: `contracts.py` (versioned session, workspace,
request, result, command, file and Git operation, artifact reference), `policy.py` (the canonical
policy with hard bounds), `tools.py` (the registry of twelve tools and the helper requests they
build), `paths.py` (the one path resolver), `patching.py` (all-or-nothing unified diffs),
`helper.py` (the program inside a sandbox: files, a shell, local Git, and the sweep that ends every
process a tool leaves), `backend.py` (the container client: hardened sibling containers, the owner
label, the helper exchange), `service.py` (policy decisions, sessions, execution, recovery, the
sweeper), `store.py` (memory and SQL), `artifacts.py`, `snapshots.py`, `image.py`,
`telemetry.py`, `config.py`, `worker.py` and `healthcheck.py`; the `iacode-dev` image profile; the
service's `Dockerfile`; and its suite of 141 cases, against the real engine and, for eight of them,
the stack's database and bucket.

**`.iacode/policies/sandbox-policy.json`** — the canonical Sandbox Tool Policy: the `developer` and
`reviewer` policies, the `iacode-dev` image profile, the `standard` resources, the `none` and
`local-services` networks, the request environment allowlist and the agent's Git identity.

**`apps/api/migrations/versions/0004_sandbox.py`** — `sandbox_sessions`, the evolved `tool_calls`,
and the run's workspace source.

**Agents.** The `developer` and `code-reviewer` profiles with their prompts, and the `coding` team.

**Scenarios and harnesses.** `scripts/iacode/scenarios/sandbox_coding_e2e.py` (coding, timeout,
cancellation, recovery), `services/orchestrator/rehearsal/coding.py`, `scripts/iacode/sandbox_image.py`,
`scripts/iacode/sandbox_snapshot.py`, `scripts/iacode/gates/sandbox_tests.py`.

**Git policy.** `scripts/development-ledger/secret_scan.py`, `scripts/development-ledger/remote_sync.py`,
`.iacode/policies/secret-scan-allowlist.json`, `tests/test_git_policy.py`.

**Red Team.** `scripts/development-ledger/gate3_red_team.py` and `gate3_sandbox_attacks.py`.

**Decisions and documents.** `docs/GATE-3-CHECKLIST.md`, `ADR-0024` to `ADR-0027`, the ADR index,
`docs/runbooks/SANDBOX.md`, `tests/test_gate3_sandbox.py`, the retrospective and this checkpoint.

## What was changed

**Phase 0.** `ledger_common.py`, `record_command.py` and `validate_checkpoint.py` share one
replayability rule; `lessons.py` resolves every guardrail entry through one function and requires
the index to be the render of the memory (memory policies 2.2.0 and 2.3.0); the API's event stream
drains every page of a terminal run; the ADR index exists and its test asserts.

**The Agent Runtime and the worker.** The plan carries each stage's sandbox policy and the run's
workspace; a profile with tools names its policy; the workflow dispatches a sandboxed stage's tool
request to the sandbox's queue, persists the result through the store's validation and releases the
run's sandbox when it ends; the run's detail lists what the sandbox executed.

**Contracts and persistence.** `iacode_contracts.sandbox` names the queue, the activities, the
result keys, the result bound and the vocabularies once; `models.py` gains `SandboxSession` and the
evolved `ToolCall`.

**The page.** The run page shows each executed tool, its status, duration, sandbox and summary.

**Stack and verification.** The `sandbox` compose service (the only one with the engine socket),
its Prometheus job and settings; `verify.py` gains the sandbox integration stage and the four
scenario stages; `image_tests.py` runs the sandbox suite with the API image suites.

**Registries.** `canonical-requirements.json` mirrors the Gate 3 checklist, `quality-gates.json`
adds `sandboxTests`, `test-suites.json` counts the sandbox suite.

**Memory.** `LSN-0051` to `LSN-0054`, `GRD-0053` to `GRD-0055`, the rendered index.

**Documents.** `START-HERE.md`, `README.md`, `ARCHITECTURE.md`, `DEVELOPMENT.md`, `VERSIONS.md`,
`DEVELOPMENT-CONTRACT.md`, `secret-policy.md` and the agent runtime runbook.

## What was removed

Nothing.
