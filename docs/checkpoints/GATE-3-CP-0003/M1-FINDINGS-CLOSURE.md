# M1 Findings Closure — GATE-3-CP-0003

Audit `M1-CP-0002` (`docs/checkpoints/GATE-3-CP-0002/REVIEW-REPORT.md`): **3/3 CLOSED** — result `CLOSED`.

## M1-F-003 — HIGH — The published history cannot validate GATE-1-CP-0001, so every clean clone of the remote fails the mandatory tests gate

Status: `CLOSED` · lesson `LSN-0040` · guardrail `GRD-0042`

**What the audit required.** Make the sealed content verifiable from the published history without rewriting it — a published reference that preserves the commit the record names — and repair the guardrail so sealed history is checked through a transport clone that carries only published objects (git clone --no-local, or the remote itself), with a test that fails on an unreachable object; then re-run the clean clone of the remote.

**What the audit observed.** The full verification of a fresh clone of https://github.com/pinguim16/iacode.git passed 30 of 31 stages and failed gate:tests (cmd-0023): test_every_sealed_checkpoint_validates_from_its_own_tag fails for GATE-1-CP-0001, 'COMMANDS.jsonl:84: the record claims a clean tree at b59d66f9f3f9 but the input scripts/development-ledger/validate_checkpoint.py does not exist there'. Validating every sealed M1 checkpoint from a clone of the remote reproduces it on its own (cmd-0029, SEALED-SUBJECTS-PUBLISHED.json, 4/5). In this working repository the same checkpoint validates (cmd-0010, 5/5).

**Root cause.** GATE-1-CP-0001's sealed ledger record cmd-0086 names commit b59d66f9f3f9add2ae9dcd1cd4609fb4a1bf0b55 — a first version of the Gate 1 closure commit, replaced before the history was published — and binds its inputs to that commit. No published reference reaches it: it exists only as an unreachable object in this machine's object store. A clone over a transport (git clone of the remote, git clone --no-local) does not carry it; a clone of the local path with --no-hardlinks copies the object store wholesale and does. Every control that checks sealed history — test_every_sealed_checkpoint_validates_from_its_own_tag, the mirror audit's MIR-016, the Gate batteries — clones the local path, so none of them could see it, and a git gc would make the working repository fail the same way. Measured over the whole ledger before any change, the same class held for two more sealed records: SETUP-00-CP-0009 cmd-0011 (13ab172fcc06) and GATE-2-CP-0001 cmd-0057 (643e721ee519), each a replaced closure commit named by a record of a dirty tree, so validation never read them.

**Implementation.**

- Three lightweight tags under refs/tags/iacode-preserved/, each naming exactly its commit (gate1-ledger-b59d66f9f3f9, setup00-ledger-13ab172fcc06, gate2-ledger-643e721ee519), pushed without force after a clean history scan; no existing reference moved (owner-authorised, DECISIONS.md D-01).
- scripts/development-ledger/ledger_common.py: one definition of the published history — PUBLISHED_REFERENCE_NAMESPACES, published_reachability (PUBLISHED, UNPUBLISHED_LOCAL_OBJECT, ABSENT_OBJECT) and published_clone, a --no-local transport clone; clone_with_worktree clones through it.
- scripts/development-ledger/validate_checkpoint.py: every commit a checkpoint's evidence names (a record's commit, subjectCommit and repositoryState.head; the state's and run metadata's commits) must be reachable from a published reference, for every schema version.
- test_every_sealed_checkpoint_validates_from_its_own_tag, MIR-016 and the Red Team fixture clone the published history; remote_sync.py requires every local checkpoint and preserved tag on the remote.
- ADR-0028; LSN-0040 records the GUARDRAIL_FAILURE of GRD-0042 and its resolution in GATE-3-CP-0003.

**Regression tests.**

- tests/test_gate3_sandbox.py PublishedHistoryTests
- tests/test_gate3_sandbox.py PreservedReferenceTests
- tests/test_gate3_sandbox.py CloneMethodTests
- tests/test_gate1_model_gateway.py test_every_sealed_checkpoint_validates_from_its_own_tag
- tests/test_git_policy.py test_a_preserved_reference_missing_from_the_remote_fails_unnamed

**Negative tests and the old behaviour.**

- OLD-CODE-M1-F-003.json: the new tests run against the tooling of 0e60b96 fail (9 failures and errors) and pass against the corrected tooling (cmd-0029).
- VALIDATOR-BLIND-SPOT.json: with each preserved tag removed from a transport clone, the old validator accepts the sealed checkpoint and the corrected one refuses it as naming a local-only object; with the tag both accept (cmd-0031).
- PreservedReferenceTests: without each reference the checkpoint is refused in the repository that holds the object and, as absent, in a published clone of it.

**Verification.** `python docs/checkpoints/GATE-3-CP-0003/delivery-harness/clean_clone.py --report docs/checkpoints/GATE-3-CP-0003/CLEAN-CLONE-REPORT.json`

**Evidence.** `command:cmd-0015`, `command:cmd-0016`, `checkpoint:REMOTE-PUBLISHED-OBJECTS.json`, `command:cmd-0029`, `checkpoint:OLD-CODE-M1-F-003.json`, `command:cmd-0031`, `checkpoint:VALIDATOR-BLIND-SPOT.json`, `command:cmd-0100`, `checkpoint:CLEAN-CLONE-REPORT.json`, `command:cmd-0098`, `checkpoint:SEALED-SUBJECTS-PUBLISHED.json`, `command:cmd-0070`

## M1-F-001 — MEDIUM — A model is never shown the shape of a tool request, and the configured live model cannot make one

Status: `CLOSED` · lesson `LSN-0055` · guardrail `GRD-0056`

**What the audit required.** The runtime states the exact envelope of every kind, including the tool object's keys, whenever native structured output is not requested, and the repair instruction restates the shape; a live coding run with the configured model then executes its tools.

**What the audit observed.** Four live coding runs through the deployed stack. With the configured model (openai:gpt-4o-mini) the developer stage failed twice out of two with INVALID_AGENT_OUTPUT: the tool arguments were written at the top of the envelope ('command', 'cwd', 'timeoutSeconds') and, after the one repair, under 'args'. With an explicitly chosen model (openai:gpt-4.1-mini) two tool requests were valid and executed in the sandbox, then the same failure ended the run ('parameters', then 'args'). No run completed the coding task.

**Root cause.** runtime_instructions() describes a TOOL_REQUEST only as '"tool" carries its name and arguments' and never names the 'name' and 'arguments' keys of the tool object; repair_instruction() restates the kinds but not the shape. envelope_schema() documents itself as 'the documentation of what the prompt asks for' when native structured output is not requested, but it reaches a model only as a structured-output schema, which the runtime requests only for a model whose capability is known — and every capability of the configured provider is UNKNOWN. So a model is asked for a shape it is never shown. The parser also dropped a stray key in the tool object, so arguments sent under 'args' or 'parameters' were lost silently and refused later by the sandbox as missing.

**Implementation.**

- services/agent-runtime/src/iacode_agent_runtime/protocol.py: envelope_contract and envelope_examples render, from envelope_schema() and the kind table the parser enforces, the version, every kind, one minimal valid envelope per kind with tool.name and tool.arguments, and where the arguments go.
- context.runtime_instructions carries the contract on every turn, whether or not the gateway honours a structured-output request; repair_instruction restates it verbatim with the stage's tools (engine.py passes them).
- The parser refuses a key beside name and arguments in the tool object (tool-unknown-field) and says where the arguments go; a TOOL_REQUEST with arguments at the top level is refused with the same hint.
- ADR-0022 amendment; LSN-0055 guarded by GRD-0056.

**Regression tests.**

- services/agent-runtime/tests/test_context.py test_the_runtime_instructions_show_the_exact_envelope_of_every_kind (A)
- services/agent-runtime/tests/test_protocol.py test_the_tool_request_example_carries_a_name_and_arguments (B)
- services/agent-runtime/tests/test_protocol.py test_the_repair_restates_the_same_shape (C)
- services/agent-runtime/tests/test_protocol.py test_the_rendered_contract_follows_the_schema and test_context.py test_the_instructions_follow_a_change_of_the_canonical_schema (D)
- services/agent-runtime/tests/test_context.py test_no_second_envelope_contract_is_written_by_hand (E)
- services/agent-runtime/tests/test_engine.py test_the_repair_carries_the_shape_with_the_stage_tools

**Negative tests and the old behaviour.**

- services/agent-runtime/tests/test_protocol.py test_arguments_outside_tool_arguments_are_refused_by_their_real_defect: the audit's top-level arguments and 'args', plus 'parameters' and a bare argument, each refused by its own reason; the correct shape accepted.
- The audit's live attempts with the same model before the correction (GATE-3-CP-0002 CROSS-GATE-LIVE-ATTEMPT-2.json, -3.json): no valid tool request.

**Verification.** `python docs/checkpoints/GATE-3-CP-0003/delivery-harness/live_coding_run.py --report docs/checkpoints/GATE-3-CP-0003/LIVE-CODING-RUN.json`

**Evidence.** `command:cmd-0035`, `command:cmd-0041`, `checkpoint:LIVE-CODING-RUN.json`, `command:cmd-0070`

## M1-F-002 — MEDIUM — The API accepts a tool result for a request the sandbox is executing, and the agent receives it instead of the sandbox's

Status: `CLOSED` · lesson `LSN-0056` · guardrail `GRD-0057`

**What the audit required.** A tool result for a request of a stage with a sandbox policy is accepted only from the sandbox: the API refuses it, and the refusal is attacked with a null control.

**What the audit observed.** Deterministic timeout scenario on the stack. Null control: the developer receives the sandbox's TIMED_OUT result and answers TIMEOUT-SEEN. Mutation: while the sandbox runs the command, POST /api/v1/agent-runs/{run}/tool-results with a SUCCEEDED result for the same request is answered 200; the stored result is the forged one, the sandbox's own execution record still says TIMED_OUT, and the developer answers TIMEOUT-NOT-SEEN.

**Root cause.** resolve_tool_request() accepts any PENDING request of the run whatever its executor, and _execute_in_sandbox() resumes the agent with the stored result, which answers a second delivery with the first one. Nothing records that the executor of a sandboxed stage's request is the sandbox.

**Implementation.**

- packages/contracts: TOOL_REQUEST_EXECUTORS (EXTERNAL, SANDBOX), written once; tool_requests.executor with its constraint (migration 0005, backfilled from the executions the sandbox recorded).
- The workflow records the executor from the stage's sandbox policy when the request is created.
- SqlAgentRunStore.resolve_tool_request(run, result, *, origin): a result whose origin is not the request's executor is refused with ToolResultOriginRefusedError before the idempotent answer and the terminal check, so nothing is stored and nothing is signalled.
- The API's service passes origin EXTERNAL; the workflow's internal activity iacode_agent_runtime_resolve_tool_request passes SANDBOX; the submission contract cannot carry an origin. The API answers 403 TOOL_RESULT_ORIGIN_REFUSED with the executor in its safe details.
- The verification stage sandbox-tool-result-origin runs the audit's null control and mutation; LSN-0056 guarded by GRD-0057; Red Team attack G3-Y.

**Regression tests.**

- apps/api/tests/integration/test_agent_runtime_persistence.py test_a_forged_result_cannot_displace_the_sandbox_result
- apps/api/tests/integration/test_agent_runtime_persistence.py test_a_manual_result_for_a_manual_request_is_accepted
- apps/api/tests/integration/test_agent_runtime_persistence.py test_a_duplicate_sandbox_result_is_idempotent
- apps/api/tests/unit/test_agent_runtime_api.py test_a_result_for_a_request_the_sandbox_owns_is_refused_and_never_signalled
- apps/api/tests/integration/test_migrations.py ToolRequestExecutorMigrationTests
- tests/test_gate3_sandbox.py ToolResultOriginTests

**Negative tests and the old behaviour.**

- test_a_manual_result_for_a_sandbox_request_is_refused
- test_a_forged_result_after_the_run_ended_is_refused
- test_a_sandbox_request_of_another_run_is_refused_as_another_run
- test_a_sandbox_result_for_a_manual_request_is_refused
- test_the_submission_cannot_claim_an_origin
- scripts/iacode/scenarios/sandbox_coding_e2e.py --scenario forged-result: control TIMEOUT-SEEN; forgery during execution 403; stored TIMED_OUT; agent TIMEOUT-SEEN; forgery after the run 403.

**Verification.** `python scripts/iacode/scenarios/sandbox_coding_e2e.py --scenario forged-result --report var/sandbox-tool-result-origin.json`

**Evidence.** `command:cmd-0038`, `command:cmd-0039`, `command:cmd-0055`, `checkpoint:TOOL-RESULT-ORIGIN.json`, `command:cmd-0087`, `command:cmd-0070`
