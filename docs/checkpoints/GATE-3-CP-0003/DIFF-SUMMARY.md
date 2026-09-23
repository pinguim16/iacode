# Diff Summary

Base: `3a526925cf653ffaa9497cff628d08d50424271a` (`iacode-checkpoints/GATE-3-CP-0002`). Every path
is declared in `FILES.json` with its reason. Published references added, none changed:
`refs/tags/iacode-preserved/gate1-ledger-b59d66f9f3f9`,
`refs/tags/iacode-preserved/setup00-ledger-13ab172fcc06`,
`refs/tags/iacode-preserved/gate2-ledger-643e721ee519`.

| Commit | Scope | What changed |
|---|---|---|
| `0e60b96` | ledger | The checkpoint opened; `GATE-3-CP-0002` anchored; audit `M1-CP-0002` registered; the preserved tags published |
| `15dfaf7` | `M1-F-003` | One definition of the published history in `ledger_common`; the validator's reachability rule; the sealed-history test, `MIR-016`, the clean-clone copy and the Red Team fixture clone the published history; `remote_sync.py` checks every evidence tag; ADR-0028; protocol documents; `LSN-0040` guardrail failure recorded and resolved |
| `3101d31` | `M1-F-001` | `envelope_contract` / `envelope_examples` rendered from the schema; the instructions and the repair carry them; the tool object closed; ADR-0022 amendment; the live run evidence |
| `9e9f49c` | `M1-F-002` | The executor vocabulary; `tool_requests.executor` (migration `0005`); the store's origin check; the API's typed `403`; the activity's `SANDBOX` path; the `forged-result` scenario and the `sandbox-tool-result-origin` stage; runbooks |
| `369f084` | lint | The three lint findings the two commits above left, the migration's backfill as a SQLAlchemy update |
| `ffc612a` | memory | `LSN-0055`, `LSN-0056`, `GRD-0056`, `GRD-0057`, the `LSN-0054` recurrence; Red Team attacks `G3-Y` and `G3-AA` |
| closure | checkpoint | The evidence, the reports, the findings closure and the finalized state |

| Area | Files |
|---|---|
| Ledger tooling | `ledger_common.py`, `validate_checkpoint.py`, `m0_mirror_audit.py`, `m0_red_team.py`, `remote_sync.py`, `gate3_red_team.py` |
| Agent runtime | `protocol.py`, `context.py`, `engine.py`, `contracts.py`, `errors.py`, `ports.py`, `persistence.py`, `service.py` |
| Orchestrator | `workflows/agent_run.py`, `agent_runtime/activities.py`, `rehearsal/durability.py` |
| API and schema | `routes/agent_runs.py`, migration `0005_tool_request_executor.py`, `iacode_contracts/agent_runtime.py`, `iacode_persistence/models.py` |
| Verification | `scenarios/sandbox_coding_e2e.py`, `verify.py` |
| Tests | `tests/test_gate3_sandbox.py`, `tests/test_gate1_model_gateway.py`, `tests/test_git_policy.py`, the agent runtime's `test_protocol.py`, `test_context.py`, `test_engine.py`, the API's `test_agent_runtime_api.py`, `test_agent_runtime_persistence.py`, `test_migrations.py` |
| Memory | `lessons.jsonl`, `LESSONS.md`, `guardrails/registry.json` |
| Documents | `CHECKPOINT-PROTOCOL.md`, `HANDOFF-PROTOCOL.md`, `DEVELOPMENT-CONTRACT.md`, ADR-0022, ADR-0028, the ADR index, `runbooks/SANDBOX.md`, `runbooks/AGENT-RUNTIME.md` |
| Registry and chain | `.iacode/policies/audit-registry.json`, `.iacode/anchors/checkpoint-chain.json`, `LATEST.md` |
