# GATE 3 — Sandbox and Tool Execution Checklist

This is the canonical specification of `GATE 3 — SANDBOX + TOOL EXECUTION`. It is the source the
expected requirement set is derived from, re-parsed at every run by `policies.canonical_requirements`
and mirrored, row for row, by `.iacode/policies/canonical-requirements.json`. A delivery for this
Gate cannot declare a smaller set, and a row cannot be dropped by editing the mirror.

The objective of the Gate is **the hands that execute, and nothing else**: the layer that takes a
tool request the Agent Runtime persisted, decides it against a canonical policy the agent cannot
change, executes it inside a disposable container that holds only the run's own workspace, and
returns a bounded result that resumes the run.

```
Agent → ToolRequest → Sandbox Policy → Sandbox Workspace → Tool Executor → ToolResult → Agent Runtime resume
```

Every command an agent asks for runs **inside a sandbox**. Never on the Windows host, never in the
shell of the tool that develops this repository, never in the container that holds the engine's
socket, and never with that socket mounted. A subprocess with a different working directory on the
host is not a sandbox, and nothing here is allowed to become one.

The Gate also carries the five defects the previous Gate handed over, and the discipline of a
public development history: atomic commits, pushed while green, with no credential ever reaching
the remote.

`GATE 3` is the last Gate of milestone `M1` and does not close the milestone. It ends at
`INTERNAL_GATE_PASS`; the milestone verdict belongs to a fresh-session audit.

## 1. Gate specification and requirement derivation

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 1.1 | A canonical, machine-readable requirement specification exists for this Gate and the registry mirrors it row for row. | `docs/GATE-3-CHECKLIST.md`, `.iacode/policies/canonical-requirements.json` | `policies.canonical_requirements` parses and mirrors the document; `Gate3CanonicalSpecificationTests`. |
| 1.2 | The closed mandatory gate registry carries the executable gate this Gate introduces, and that gate builds what it measures before measuring it. | `.iacode/policies/quality-gates.json`, `scripts/iacode/gates/sandbox_tests.py` | A Green Keeper cycle measured against the registry's mandatory set; `Gate3MandatoryGateTests`. |
| 1.3 | The test suite this Gate introduces is declared canonically, is counted by the count derivation and is resolvable as evidence. | `.iacode/policies/test-suites.json` | `COUNTS.json` `TESTS`; `Gate3TestSuiteRegistryTests`. |
| 1.4 | The internal Red Team battery of this Gate is executable, scoped to the sandbox, runs its attacks against the real container engine and records a null-mutation control. | `scripts/development-ledger/gate3_red_team.py` | `M1-INTERNAL-RED-TEAM.json` with a `VALID` `baselineControl`; `Gate3RedTeamHarnessTests`. |
| 1.5 | The reservation of the sandbox directory is consumed by the Gate that owns it, and every reservation of a later Gate is still enforced. | `.iacode/policies/gate-scope.json`, `services/sandbox/README.md` | `Gate3ScopeTests`. |
| 1.6 | One documented command verifies this Gate, adds the stages it introduces and keeps a targeted mode that does not restart the stack. | `scripts/iacode/verify.py` | Verification run, targeted and full; `Gate3VerificationStageTests`. |

## 2. Public development history

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 2.1 | The repository publishes to exactly one authorised remote, and a remote pointing anywhere else is refused rather than used. | `scripts/development-ledger/remote_sync.py` | `test_a_remote_other_than_the_authorised_one_fails`; `test_the_authorised_remote_is_the_one_the_policy_names`. |
| 2.2 | The whole history was scanned for credentials before its first publication, and a finding names the commit, the file, the line and the kind but never the value. | `scripts/development-ledger/secret_scan.py`, `.iacode/policies/secret-scan-allowlist.json` | Recorded history scan; `SecretScanTests`; `test_a_finding_never_prints_the_value`. |
| 2.3 | The published history carries no credential, and the check is repeatable against the history as it now stands. | `scripts/development-ledger/secret_scan.py` | `PublishedHistoryTests`; `test_the_published_history_carries_no_credential`. |
| 2.4 | Every push is preceded by a scan of exactly the staged content, and an allowance matches a value's digest rather than a path. | `scripts/development-ledger/secret_scan.py` | `test_the_staged_scan_judges_only_the_staged_content`; `test_the_allowlist_matches_the_value_and_not_the_path`; recorded staged scans. |
| 2.5 | Whether the branch and the checkpoint tag are on the remote is asked of the remote, an unpushed commit or a missing tag fails, and an unreachable remote is never a pass. | `scripts/development-ledger/remote_sync.py` | `RemoteSyncTests`; `test_an_unreachable_remote_is_unavailable_and_never_a_pass`. |
| 2.6 | The commit, push, tag and correction rules are stated in the development contract and recorded as a decision: atomic commits, green commits only, no rewriting of published history, no moving of a published tag, and no credential in a URL, a configuration or a versioned file. | `docs/DEVELOPMENT-CONTRACT.md`, `docs/adr/ADR-0024-public-remote-and-atomic-commits.md`, `.iacode/policies/secret-policy.md` | `GitPolicyDocumentationTests`. |
| 2.7 | The history of this Gate's development is preserved as observable data — requirement, commits, tests, fixes, checkpoint — and nothing in it is marked as training-eligible. | `docs/adr/ADR-0024-public-remote-and-atomic-commits.md` | `test_the_decision_is_recorded_as_an_adr`; the Gate's commits on `origin/main`. |

## 3. Defects inherited from the previous Gate

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 3.1 | A command the ledger could not replay is refused before it executes, the refusal is itself recorded, and the recorder and the validator apply one shared replayability rule. | `scripts/development-ledger/ledger_common.py`, `scripts/development-ledger/record_command.py`, `scripts/development-ledger/validate_checkpoint.py` | `LedgerCommandReplayabilityTests`; `test_rejected_command_is_never_executed`; `test_recorder_and_validator_share_one_rule`. |
| 3.2 | A guardrail entry that names a file or a path where a test is required is refused, and lesson validation and guardrail effectiveness resolve an entry through one function. | `scripts/development-ledger/lessons.py` | `GuardrailRegistryResolutionTests`; `test_validation_and_effectiveness_agree`; `test_one_function_resolves_a_guardrail_entry`. |
| 3.3 | The committed lesson index is the render of the memory, and a memory changed without re-rendering it, or an index edited by hand, is refused under the memory policy that introduced the rule. | `scripts/development-ledger/lessons.py`, `.iacode/memory/POLICY.json` | `LessonIndexFreshnessTests`; `test_a_memory_changed_without_rerendering_is_refused`. |
| 3.4 | The event stream of a run that is already terminal delivers every event after the cursor, however many pages that takes, before it closes. | `apps/api/src/iacode_api/routes/agent_runs.py` | `test_a_terminal_stream_drains_every_page_after_the_cursor`. |
| 3.5 | A canonical ADR index exists, lists every record with its title and status, resolves every link, and its test asserts rather than skips. | `docs/adr/README.md` | `AdrIndexTests`; `test_the_index_lists_every_record_with_its_title_and_status`. |

## 4. The sandbox boundary

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 4.1 | The sandbox is its own service in the directory the scope registry reserved for it, with its own contracts, and the decision is recorded. | `services/sandbox/`, `docs/adr/ADR-0025-sandbox-isolation-boundary.md` | `SandboxBoundaryTests`; `ADR-0025`. |
| 4.2 | No sandbox logic lives in the API routes, the Agent Runtime or the Model Gateway: none of them imports the sandbox package or a container client. | `apps/api/src/iacode_api/`, `services/agent-runtime/src/iacode_agent_runtime/`, `services/model-gateway/src/` | `SandboxBoundaryTests`. |
| 4.3 | The Agent Runtime and the workflow that drives it still execute nothing themselves; a tool reaches the sandbox only as an activity on the sandbox's own task queue. | `services/agent-runtime/src/iacode_agent_runtime/`, `services/orchestrator/src/iacode_orchestrator/` | `RepositoryToolExecutionBoundaryTests`; `ToolExecutionBoundaryTests`; `WorkflowSandboxDispatchTests`. |
| 4.4 | Inside the sandbox service only the engine backend and the in-container helper start a process, and the controller never uses a shell. | `services/sandbox/src/iacode_sandbox/backend.py`, `services/sandbox/src/iacode_sandbox/helper.py` | `test_only_the_backend_and_the_helper_start_processes`; `test_no_module_of_the_controller_uses_a_shell`. |
| 4.5 | The controller starts only the container client, with an argument vector, and never a command a request supplied. | `services/sandbox/src/iacode_sandbox/backend.py` | `test_the_backend_starts_only_the_container_client`; `test_the_image_decides_the_command_not_the_request`. |
| 4.6 | The controller is the only service given the container engine, and it holds no capability, cannot gain one, and publishes no port. | `infra/compose/docker-compose.yml` | `test_only_the_sandbox_service_is_given_the_engine_socket`. |

## 5. Contracts

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 5.1 | Versioned contracts exist for the sandbox session, the policy, the workspace, the execution request, the execution result, the command execution, the file operation, the Git operation and the artifact reference. | `services/sandbox/src/iacode_sandbox/contracts.py`, `services/sandbox/src/iacode_sandbox/policy.py`, `packages/contracts/src/iacode_contracts/sandbox.py` | `SandboxContractTests`; `test_the_contract_is_versioned`. |
| 5.2 | A contract of another version is refused rather than interpreted, and a request carrying a field the contract does not declare or missing one it requires is refused. | `services/sandbox/src/iacode_sandbox/contracts.py` | `test_another_version_is_refused_rather_than_interpreted`; `test_a_request_cannot_carry_a_field_the_contract_does_not_declare`; `test_a_missing_required_field_is_refused`. |
| 5.3 | A command result carries the exit code, standard output, standard error, duration, whether it timed out, whether it was truncated and its artifact references, and no exit code is invented for a command that never started. | `services/sandbox/src/iacode_sandbox/contracts.py` | `test_no_exit_code_is_invented_for_a_command_that_never_started`; `test_the_result_round_trips_with_its_artifacts`. |
| 5.4 | The execution status, session state, workspace and operation vocabularies are closed, and the database accepts exactly the declared ones. | `packages/contracts/src/iacode_contracts/sandbox.py` | `test_the_status_vocabulary_is_closed`; `test_the_session_workspace_and_operations_have_closed_vocabularies`; `test_the_session_state_vocabulary_the_database_accepts_is_the_declared_one`. |
| 5.5 | The result an agent receives cannot present a cancellation, a denial or a timeout as a success. | `services/sandbox/src/iacode_sandbox/contracts.py` | `test_the_agent_sees_a_cancellation_as_a_failure_it_cannot_misread`. |

## 6. The tool registry and the tool policy

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 6.1 | An explicit registry names every executable tool — list, read, write, patch and search of files, shell execution, and the local Git status, diff, log, show, add and commit — and only a registered name can execute. | `services/sandbox/src/iacode_sandbox/tools.py` | `ToolRegistryTests`; `test_the_registry_is_exactly_the_specified_set`. |
| 6.2 | An unknown tool name is refused, and no name is ever mapped to a shell. | `services/sandbox/src/iacode_sandbox/tools.py`, `services/sandbox/src/iacode_sandbox/service.py` | `test_an_unknown_tool_is_refused_and_never_mapped_to_a_shell`; `test_an_unknown_tool_is_denied_and_nothing_is_started`. |
| 6.3 | A canonical sandbox tool policy defines, per policy, the allowed tools, the resource profile, the network profile, the workspace permissions, the command timeout and the output limits. | `.iacode/policies/sandbox-policy.json`, `services/sandbox/src/iacode_sandbox/policy.py` | `SandboxPolicyTests`; `test_the_canonical_policy_loads`. |
| 6.4 | A tool the run's policy does not allow is refused, a policy naming an unregistered tool is refused, and an unknown policy is refused. | `services/sandbox/src/iacode_sandbox/policy.py`, `services/sandbox/src/iacode_sandbox/service.py` | `test_a_tool_outside_the_policy_is_refused`; `test_a_policy_naming_an_unregistered_tool_is_refused`; `test_an_unknown_policy_is_denied`. |
| 6.5 | Tool arguments are structured and typed: an undeclared argument is refused, and a wrong type, an absent value and a wrong value each carry their own reason. | `services/sandbox/src/iacode_sandbox/tools.py` | `test_an_argument_a_tool_does_not_declare_is_refused`; `test_a_wrong_type_is_refused_with_its_own_reason`. |
| 6.6 | No request can change its policy, its limits, its network or its mounts; a request that tries is denied, and a request may lower a timeout but never raise it. | `services/sandbox/src/iacode_sandbox/service.py`, `services/sandbox/src/iacode_sandbox/tools.py` | `test_a_request_that_tries_to_set_a_limit_is_denied`; `test_no_request_can_change_the_network_the_limits_or_the_mounts`; `test_a_request_may_lower_a_timeout_and_never_raise_it`. |
| 6.7 | The limits a tool runs under come from the policy, and every limit a policy applies is inside its declared bound. | `services/sandbox/src/iacode_sandbox/tools.py`, `services/sandbox/src/iacode_sandbox/policy.py` | `test_the_limits_come_from_the_policy`; `test_every_limit_the_policy_applies_is_inside_its_bound`. |
| 6.8 | A policy document with an unknown key, or a read-only policy that allows a writing tool, is refused when it is loaded. | `services/sandbox/src/iacode_sandbox/policy.py` | `test_an_unknown_key_is_refused`; `test_a_read_only_policy_that_allows_a_writer_is_refused`. |
| 6.9 | Tools the policy allows execute automatically, inside the sandbox, without a confirmation per call; nothing is executed on the host under any policy. | `services/orchestrator/src/iacode_orchestrator/workflows/agent_run.py`, `docs/adr/ADR-0027-tool-execution-policy.md` | `WorkflowSandboxDispatchTests`; `ADR-0027`. |

## 7. Container isolation and privileges

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 7.1 | Every run executes in its own disposable container with its own workspace; two runs never share either. | `services/sandbox/src/iacode_sandbox/service.py`, `services/sandbox/src/iacode_sandbox/backend.py` | `test_two_runs_have_two_containers_and_two_workspaces`; `test_one_run_gets_one_session_and_two_runs_get_two`. |
| 7.2 | The sandbox runs unprivileged, as a non-root user, with every capability dropped and no way to gain privileges. | `services/sandbox/src/iacode_sandbox/backend.py`, `services/sandbox/images/iacode-dev/Dockerfile` | `test_the_sandbox_runs_unprivileged_with_no_capability`; `test_every_isolation_flag_is_emitted`. |
| 7.3 | The root filesystem is read-only, and the only writable places are the workspace and a temporary directory, both in-memory filesystems with a size limit. | `services/sandbox/src/iacode_sandbox/backend.py` | `test_the_root_filesystem_is_read_only`; `test_the_writable_places_are_bounded_in_memory_filesystems`. |
| 7.4 | The container engine's socket, and any other engine endpoint, is absent from a sandbox. | `services/sandbox/src/iacode_sandbox/backend.py` | `test_no_docker_socket_or_engine_endpoint_is_reachable`. |
| 7.5 | No host path is mounted into a sandbox — no drive, no root, no home, no profile, no SSH directory, no credential store, no secret environment file — and no argument of a request can add one. | `services/sandbox/src/iacode_sandbox/backend.py` | `test_no_host_path_is_mounted`; `test_no_privilege_and_no_host_resource_can_be_granted`. |
| 7.6 | Every sandbox container carries labels naming the service instance that owns it, the session, the run, the policy and its expiry, so ownership is read from the engine rather than from memory. | `services/sandbox/src/iacode_sandbox/backend.py` | `test_every_container_carries_the_ownership_labels`. |

## 8. Resource limits

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 8.1 | CPU, memory, process count, workspace size, execution timeout and output size are mandatory, configurable limits, and a zero, negative, absurd or missing value is refused. | `.iacode/policies/sandbox-policy.json`, `services/sandbox/src/iacode_sandbox/policy.py` | `ResourceLimitValidationTests`; `test_zero_negative_and_absurd_values_are_refused`; `test_a_missing_limit_is_refused`. |
| 8.2 | The memory limit holds the in-memory filesystems, so a full workspace cannot starve the processes of the limit they were promised. | `services/sandbox/src/iacode_sandbox/policy.py` | `test_memory_must_hold_the_in_memory_filesystems`. |
| 8.3 | A process that multiplies without end is contained by the process limit, and the sandbox remains usable afterwards. | `services/sandbox/src/iacode_sandbox/backend.py` | `test_a_fork_bomb_is_contained_by_the_process_limit`. |
| 8.4 | A process that exceeds the memory limit fails in a controlled way, and the host is unaffected. | `services/sandbox/src/iacode_sandbox/backend.py` | `test_a_process_that_exceeds_memory_fails_in_a_controlled_way`. |
| 8.5 | The workspace cannot outgrow its limit. | `services/sandbox/src/iacode_sandbox/backend.py` | `test_the_workspace_cannot_outgrow_its_limit`; `test_the_workspace_is_bounded`. |
| 8.6 | A command that exceeds its timeout is ended together with every process it started, including a process that left its session, and nothing is left running. | `services/sandbox/src/iacode_sandbox/helper.py` | `test_a_timeout_kills_the_whole_process_tree`. |
| 8.7 | Standard output and standard error are bounded while they are read; what exceeds the bound is truncated explicitly and stored whole as an artifact, and memory is never unbounded. | `services/sandbox/src/iacode_sandbox/helper.py`, `services/sandbox/src/iacode_sandbox/artifacts.py` | `test_output_is_bounded_and_the_rest_is_an_artifact`; `test_truncated_output_goes_to_the_artifact_store`. |

## 9. Network

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 9.1 | A sandbox has no network by default: only loopback exists, and every policy the Gate ships denies the network. | `services/sandbox/src/iacode_sandbox/backend.py`, `.iacode/policies/sandbox-policy.json` | `test_the_default_network_has_only_loopback`; `test_every_policy_denies_network_by_default`. |
| 9.2 | An attempt to reach an external address from a sandbox without network fails. | `services/sandbox/src/iacode_sandbox/backend.py` | `test_external_egress_fails`. |
| 9.3 | The one other network profile is local services only, on an internal network with no route outside, and it is chosen by the policy, never by a request. | `services/sandbox/src/iacode_sandbox/backend.py`, `services/sandbox/src/iacode_sandbox/policy.py` | `test_a_local_services_network_is_internal`; `test_no_request_can_change_the_network_the_limits_or_the_mounts`. |
| 9.4 | No package installation from the internet is offered; the image carries the toolchain the Gate's tests need. | `services/sandbox/images/iacode-dev/Dockerfile`, `docs/runbooks/SANDBOX.md` | `SandboxImageProfileTests`. |

## 10. Environment and secrets

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 10.1 | A sandbox receives only the variables its policy explicitly allows, and no variable of the controller — provider key, repository token, agent socket, cloud credential or engine address — reaches it. | `services/sandbox/src/iacode_sandbox/backend.py`, `services/sandbox/src/iacode_sandbox/tools.py` | `test_no_variable_of_the_controller_reaches_a_sandbox`; `test_the_command_environment_is_an_allowlist`. |
| 10.2 | A command's environment inside the sandbox is the allowlist and nothing else. | `services/sandbox/src/iacode_sandbox/helper.py` | `test_the_environment_is_the_allowlist_and_nothing_else`. |
| 10.3 | A policy cannot allow a credential-shaped variable into a command's environment. | `services/sandbox/src/iacode_sandbox/policy.py` | `test_a_credential_cannot_be_allowed_into_a_command_environment`. |
| 10.4 | No Git credential, credential helper, SSH key or agent socket exists in a sandbox. | `services/sandbox/images/iacode-dev/gitconfig`, `services/sandbox/src/iacode_sandbox/backend.py` | `test_no_git_or_ssh_credential_exists`. |

## 11. Workspaces

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 11.1 | A workspace has an identity and an explicit lifecycle, belongs to exactly one run, and a run holds at most one active session. | `services/sandbox/src/iacode_sandbox/service.py`, `packages/persistence/src/iacode_persistence/models.py` | `test_one_run_gets_one_session_and_two_runs_get_two`; `SandboxMigrationTests`. |
| 11.2 | A workspace is provisioned only from an authorised snapshot, named by its artifact identifier and never by a path, and becomes a repository the tools can work on. | `services/sandbox/src/iacode_sandbox/snapshots.py`, `services/agent-runtime/src/iacode_agent_runtime/service.py` | `test_a_snapshot_provisions_the_workspace_as_a_repository`; `test_a_coding_run_names_an_authorised_snapshot`. |
| 11.3 | Anything but a workspace snapshot artifact is refused before the run exists, and a snapshot for a team that executes no tool is refused. | `services/agent-runtime/src/iacode_agent_runtime/service.py` | `test_anything_but_a_snapshot_artifact_is_refused`; `test_a_snapshot_for_a_team_without_tools_is_refused`. |
| 11.4 | A snapshot whose digest differs from its record, or that carries a link or an escaping member, is refused, and no session survives the refusal. | `services/sandbox/src/iacode_sandbox/snapshots.py` | `test_a_snapshot_with_a_different_digest_is_refused`; `test_an_unsafe_snapshot_is_refused_and_no_session_survives`; `test_the_snapshot_builder_refuses_a_link`. |
| 11.5 | One run cannot read or write another run's files, nor see its processes. | `services/sandbox/src/iacode_sandbox/backend.py` | `CrossSessionIsolationTests`; `test_one_run_cannot_see_another_runs_files`; `test_one_run_cannot_see_another_runs_processes`. |
| 11.6 | The development working tree of this repository is never an agent's workspace. | `services/sandbox/src/iacode_sandbox/snapshots.py`, `docs/adr/ADR-0026-workspace-lifecycle.md` | `SandboxScenarioTests`; `ADR-0026`. |

## 12. The path resolver and the filesystem tools

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 12.1 | One canonical path resolver decides every path a tool touches; no other module re-implements path safety. | `services/sandbox/src/iacode_sandbox/paths.py` | `SinglePathResolverTests`. |
| 12.2 | Traversal, absolute paths, drive letters, UNC paths, null bytes and normalisation tricks are refused, each with its own reason. | `services/sandbox/src/iacode_sandbox/paths.py` | `PathResolverTests`; `test_every_hostile_spelling_is_refused_with_its_own_code`. |
| 12.3 | A link inside the workspace that points outside it cannot be read or written through, whether it names a file, a directory, the root or climbs out relatively; a link that stays inside is followed. | `services/sandbox/src/iacode_sandbox/paths.py` | `SymlinkContainmentTests`; `test_a_symlink_that_points_outside_cannot_be_read_or_written_through`. |
| 12.4 | Listing, reading, writing, searching and patching work inside the workspace of a real sandbox. | `services/sandbox/src/iacode_sandbox/helper.py` | `test_write_read_list_search_and_patch`. |
| 12.5 | A read and a write are bounded in size, an oversized one is refused, and binary content is refused as text rather than mangled. | `services/sandbox/src/iacode_sandbox/helper.py` | `test_oversized_reads_and_writes_are_refused`; `test_binary_content_is_refused_as_text`. |
| 12.6 | A write validates its parent directory and replaces the file atomically. | `services/sandbox/src/iacode_sandbox/helper.py` | `FilesystemToolTests`. |
| 12.7 | A patch applies only inside the workspace; a patch whose context does not match, or that has one bad file, changes nothing. | `services/sandbox/src/iacode_sandbox/patching.py` | `PatchApplyTests`; `test_a_failing_patch_changes_nothing`; `test_a_multi_file_patch_with_one_bad_file_writes_no_file`; `test_a_patch_cannot_reach_outside_the_workspace`. |
| 12.8 | A search is confined to the workspace and bounded in results, output and duration. | `services/sandbox/src/iacode_sandbox/helper.py`, `services/sandbox/src/iacode_sandbox/tools.py` | `test_write_read_list_search_and_patch`; `test_the_limits_come_from_the_policy`. |
| 12.9 | A path refused inside the sandbox reaches the agent as a denial, not as a failure of the sandbox. | `services/sandbox/src/iacode_sandbox/service.py` | `test_a_path_refusal_from_inside_the_sandbox_is_a_denial`; `test_traversal_and_absolute_escapes_are_denied`. |

## 13. Shell execution

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 13.1 | Shell execution runs only inside the sandbox container, with the command, the working directory, the allowed environment and the timeout passed as structured arguments. | `services/sandbox/src/iacode_sandbox/tools.py`, `services/sandbox/src/iacode_sandbox/helper.py` | `ShellToolTests`; `test_a_hostile_path_is_refused_before_the_helper`. |
| 13.2 | Standard output, standard error, a zero and a non-zero exit code, a missing executable and a child process are all reported faithfully. | `services/sandbox/src/iacode_sandbox/helper.py` | `test_echo_stdout_stderr_and_exit_codes`; `test_a_missing_executable_is_a_failure_with_its_exit_code`; `test_a_child_process_runs_and_reports`. |
| 13.3 | The working directory resolves inside the workspace, and an escaping one is refused. | `services/sandbox/src/iacode_sandbox/paths.py` | `test_the_working_directory_is_resolved_inside_the_workspace`. |
| 13.4 | A payload that tries to reach a host command affects only the sandbox, inside its policy, and the host is unchanged. | `services/sandbox/src/iacode_sandbox/helper.py` | `test_an_injected_host_command_only_reaches_the_sandbox`; `SandboxScenarioTests`. |
| 13.5 | A command still running when its run is cancelled is stopped, with every process it started. | `services/sandbox/src/iacode_sandbox/service.py`, `services/sandbox/src/iacode_sandbox/helper.py` | `test_a_cancelled_run_stops_its_command_and_leaves_nothing_running`. |

## 14. Local Git tools

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 14.1 | Inside the workspace an agent can read the status, the working and the staged diff, the log and a commit, stage files and commit locally. | `services/sandbox/src/iacode_sandbox/tools.py`, `services/sandbox/src/iacode_sandbox/helper.py` | `GitToolTests`; `test_status_diff_add_commit_log_and_show`; `test_the_staged_diff_is_asked_for_explicitly`. |
| 14.2 | Every Git tool builds a fixed argument vector, a revision that looks like an option is refused, and a commit skips hooks and carries its message as one argument. | `services/sandbox/src/iacode_sandbox/tools.py` | `GitOperationTests`; `test_every_git_tool_builds_a_fixed_argument_vector`; `test_a_revision_that_looks_like_an_option_is_refused`; `test_a_commit_skips_hooks_and_carries_the_message_as_one_argument`. |
| 14.3 | No remote Git operation is offered or possible — no push, fetch, clone or remote — and no destructive operation — hard reset, clean, rebase, history filtering, forced push — is offered by default. | `services/sandbox/src/iacode_sandbox/tools.py`, `.iacode/policies/sandbox-policy.json` | `test_no_remote_or_destructive_git_verb_exists`; `test_no_remote_operation_is_offered_or_possible`; `test_no_policy_offers_a_remote_git_operation`. |
| 14.4 | An agent's commits carry an explicit sandbox identity that is not a person, separate from the owner's development identity, and the difference is documented. | `services/sandbox/images/iacode-dev/gitconfig`, `docs/runbooks/SANDBOX.md` | `test_the_sandbox_git_identity_is_not_a_person`; `Gate3DocumentationTests`. |
| 14.5 | Git output is bounded like any other output. | `services/sandbox/src/iacode_sandbox/helper.py` | `test_git_output_is_bounded`. |

## 15. Session lifecycle, cleanup and recovery

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 15.1 | A session moves through explicit states, is created ready for its run and is removed with it. | `services/sandbox/src/iacode_sandbox/service.py`, `packages/contracts/src/iacode_contracts/sandbox.py` | `SessionLifecycleTests`; `test_a_session_is_created_ready_and_removed_with_its_run`. |
| 15.2 | A running tool holds its session in the running state, and inspecting a session reports the store and the engine side by side. | `services/sandbox/src/iacode_sandbox/service.py` | `test_a_running_tool_holds_the_session_in_running`; `test_inspect_reports_the_store_and_the_engine`. |
| 15.3 | When a run ends or is cancelled its sandbox is removed, and no container or temporary volume is left behind. | `services/sandbox/src/iacode_sandbox/service.py`, `services/orchestrator/src/iacode_orchestrator/workflows/agent_run.py` | `test_releasing_a_run_removes_its_container`; `WorkflowSandboxDispatchTests`. |
| 15.4 | A restarted service reconciles from the store and the engine rather than from memory: it keeps a live session, removes a container no session owns, and fails a session whose container vanished. | `services/sandbox/src/iacode_sandbox/service.py` | `RecoveryTests`; `SessionRecoveryTests`; `test_a_restarted_service_keeps_a_live_session_and_removes_an_orphan`. |
| 15.5 | Reconciliation touches only containers this service instance owns, so another stack or a test on the same engine is never cleaned up by it. | `services/sandbox/src/iacode_sandbox/backend.py`, `services/sandbox/src/iacode_sandbox/service.py` | `test_a_restarted_service_keeps_a_live_session_and_removes_an_orphan`; `test_every_container_carries_the_ownership_labels`. |
| 15.6 | An orphan sweeper expires only sessions that have expired and are not running, in bounded, deterministic batches, and never removes an active workspace. | `services/sandbox/src/iacode_sandbox/service.py` | `test_the_sweeper_expires_only_what_has_expired_and_is_not_running`; `test_the_sweeper_is_bounded`; `test_nothing_unexpired_is_swept`; `test_an_expired_session_is_swept_and_its_container_removed`. |

## 16. Persistence and migrations

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 16.1 | This Gate adds its schema through a new migration and edits no migration that has already been applied. | `apps/api/migrations/versions/0004_sandbox.py` | `test_applied_migrations_are_not_edited`; `SandboxMigrationTests`. |
| 16.2 | The existing tool call, artifact and run entities are evolved rather than duplicated, and the one new table holds only what nothing else could: the sandbox session. | `packages/persistence/src/iacode_persistence/models.py` | `test_the_agent_runtime_created_no_parallel_entity`; `test_structural_tables_exist`. |
| 16.3 | A database created from nothing reaches the head revision, and a database at the previous Gate's head upgrades without losing a row. | `apps/api/migrations/versions/0004_sandbox.py` | `test_fresh_database_reaches_the_sandbox_head`; `test_gate2_database_upgrades_to_gate3_head`; `test_the_sandbox_migration_is_reversible`. |
| 16.4 | Every execution is traceable from the task through the run, the agent run, the tool request, the sandbox session and the execution to the result, and none of it holds private reasoning. | `packages/persistence/src/iacode_persistence/models.py` | `test_relationships_cascade_deliberately`; `test_the_detail_shows_what_the_sandbox_executed_and_not_its_output`. |
| 16.5 | A retried request never executes twice: the execution is keyed by the tool request it answers. | `services/sandbox/src/iacode_sandbox/store.py`, `services/sandbox/src/iacode_sandbox/service.py` | `test_an_execution_is_never_repeated_for_a_retried_request`; `SqlSandboxStoreTests`. |
| 16.6 | The store the service runs against in the stack records sessions and executions in the real database with the same behaviour the suite asserts in memory. | `services/sandbox/src/iacode_sandbox/store.py` | `SqlSandboxStoreTests`. |
| 16.7 | Nothing this Gate persists is training-eligible, and no table stores a credential. | `packages/persistence/src/iacode_persistence/models.py` | `test_rights_default_to_denial`; `test_no_table_stores_a_credential`. |

## 17. Agent Runtime integration

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 17.1 | A pending tool request of a stage with a sandbox policy is checked against the policy, executed in the run's sandbox, its result persisted, and the workflow resumes. | `services/orchestrator/src/iacode_orchestrator/workflows/agent_run.py`, `services/orchestrator/src/iacode_orchestrator/agent_runtime/activities.py` | `WorkflowSandboxDispatchTests`; recorded synthetic coding scenario run. |
| 17.2 | A stage without a sandbox policy keeps the previous Gate's behaviour: the request waits for a result delivered through the API. | `services/orchestrator/src/iacode_orchestrator/workflows/agent_run.py` | `WorkflowSandboxDispatchTests`; `test_tool_request_pauses_the_run`. |
| 17.3 | The run plan names the sandbox policy of each stage and the workspace source, frozen when the run is created. | `services/agent-runtime/src/iacode_agent_runtime/contracts.py` | `SandboxPlanContractTests`; `test_the_sandbox_policy_and_the_workspace_round_trip`. |
| 17.4 | A tool result returns to the agent as labelled data in its own channel and never as an instruction. | `services/agent-runtime/src/iacode_agent_runtime/context.py` | `InstructionHierarchyTests`; `test_each_source_lands_in_its_own_channel`. |
| 17.5 | A large result reaches the model truncated inline with an artifact reference, within the size the runtime accepts for a tool result. | `services/sandbox/src/iacode_sandbox/contracts.py` | `test_truncated_output_goes_to_the_artifact_store`; `Gate3AgentToolPolicyTests`. |
| 17.6 | A tool that times out returns a normalised error result the agent receives, and the run never stays waiting for a tool for ever. | `services/sandbox/src/iacode_sandbox/service.py`, `services/orchestrator/src/iacode_orchestrator/workflows/agent_run.py` | `test_a_timeout_kills_the_whole_process_tree`; `WorkflowSandboxDispatchTests`; recorded synthetic coding scenario run. |
| 17.7 | Cancelling a run during a long command stops the command, records the cancellation, ends the run cancelled and leaves no process behind. | `scripts/iacode/scenarios/sandbox_coding_e2e.py` | `test_a_cancelled_run_stops_its_command_and_leaves_nothing_running`; recorded sandbox cancellation scenario run. |
| 17.8 | A sandbox service restart while a run executes does not lose the run: the session is reconciled and the run completes. | `scripts/iacode/scenarios/sandbox_coding_e2e.py` | `RecoveryTests`; recorded sandbox recovery scenario run. |

## 18. Agent profiles and the coding team

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 18.1 | A profile that may request tools names the sandbox policy that governs them, and a profile with tools and no policy is refused. | `services/agent-runtime/src/iacode_agent_runtime/profiles.py` | `SandboxProfileTests`; `test_a_profile_with_tools_and_no_policy_is_refused`. |
| 18.2 | No agent is given every tool: each profile's permitted actions are within its policy's tools. | `agents/profiles/`, `.iacode/policies/sandbox-policy.json` | `Gate3AgentToolPolicyTests`. |
| 18.3 | A developer profile may read, search, write, patch, run tests and use the local Git tools its policy allows. | `agents/profiles/developer.json` | `test_the_developer_and_the_reviewer_name_their_policies`. |
| 18.4 | The reviewer is read-only: read, search, diff and test results, and no writing tool. | `agents/profiles/code-reviewer.json` | `test_the_code_reviewer_is_given_no_writing_tool`; `test_the_reviewer_is_read_only`. |
| 18.5 | The planner has no writing tool and works from context alone. | `agents/profiles/planner.json` | `Gate3AgentToolPolicyTests`. |
| 18.6 | A minimal coding team — planner, developer, reviewer — proves the flow, and no larger team is built. | `agents/teams/coding.json` | `test_the_coding_team_is_planner_developer_reviewer`. |

## 19. Artifacts

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 19.1 | Full output, large diffs and workspace snapshots are stored in the existing artifact infrastructure, recorded as artifacts, and no second store is created. | `services/sandbox/src/iacode_sandbox/artifacts.py`, `services/sandbox/src/iacode_sandbox/snapshots.py` | `test_truncated_output_goes_to_the_artifact_store`; `SandboxArtifactStoreTests`. |
| 19.2 | A workspace snapshot is created from an explicit source directory by a documented command, and never from the development working tree implicitly. | `scripts/iacode/sandbox_snapshot.py` | `test_the_snapshot_builder_refuses_a_link`; `SandboxScenarioTests`. |

## 20. The sandbox image

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 20.1 | A registry of sandbox image profiles exists, the architecture accepts new profiles, and one functional profile for this project carries Git and Python. | `.iacode/policies/sandbox-policy.json`, `services/sandbox/images/iacode-dev/Dockerfile` | `SandboxImageProfileTests`. |
| 20.2 | The image is built as part of the Gate from a base pinned by digest and packages pinned by version, and never from a moving tag. | `services/sandbox/images/iacode-dev/Dockerfile` | `SandboxImageProfileTests`. |
| 20.3 | The image is addressed by a fingerprint of its inputs, and a missing or stale image is refused rather than substituted. | `services/sandbox/src/iacode_sandbox/image.py`, `scripts/iacode/sandbox_image.py` | `test_a_missing_or_stale_image_is_refused_rather_than_substituted`; `SandboxImageProfileTests`. |
| 20.4 | The sandbox gate builds the service image and the sandbox image before it measures anything. | `scripts/iacode/gates/sandbox_tests.py` | `Gate3MandatoryGateTests`. |
| 20.5 | The sandbox service installs the one dependency lock the dependency scan reads, so its Python dependencies are scanned with the rest; the sandbox image's system packages are pinned by version, and what the scan does not cover is documented rather than implied. | `services/sandbox/Dockerfile`, `scripts/iacode/dependency_scan.py`, `docs/runbooks/SANDBOX.md` | Recorded dependency scan; `SandboxImageProfileTests`. |

## 21. The sandbox service API

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 21.1 | An internal service contract creates a session, executes a tool, inspects a session and terminates it, and it is reached only as activities on the sandbox's task queue. | `services/sandbox/src/iacode_sandbox/service.py`, `services/sandbox/src/iacode_sandbox/worker.py` | `SandboxServiceDecisionTests`; `WorkflowSandboxDispatchTests`. |
| 21.2 | A refusal is recorded as an execution with its reason, so a denied request is as traceable as an executed one. | `services/sandbox/src/iacode_sandbox/service.py` | `test_a_denial_is_recorded_as_an_execution`. |
| 21.3 | The service's health is a poller on its queue and an engine that answers, not a process that exists. | `services/sandbox/src/iacode_sandbox/healthcheck.py` | `SandboxBoundaryTests`. |

## 22. Observability

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 22.1 | The service publishes instruments for sessions created and active, tool executions, their duration, failures, timeouts and policy refusals. | `services/sandbox/src/iacode_sandbox/telemetry.py` | `SandboxMetricsTests`; `test_every_required_instrument_exists`. |
| 22.2 | Every metric label is low cardinality, a command never becomes a label, and a refusal is counted by its reason. | `services/sandbox/src/iacode_sandbox/telemetry.py` | `test_no_instrument_declares_a_label_outside_the_permitted_set`; `test_a_command_never_becomes_a_label`; `test_a_refusal_is_counted_by_reason`. |
| 22.3 | Logs carry the run, the agent, the sandbox, the tool, the status and the duration, and never a whole result, a secret or the host environment. | `services/sandbox/src/iacode_sandbox/telemetry.py` | `SandboxLogTests`; `test_an_execution_log_record_holds_no_command_or_output`. |
| 22.4 | The observability stack scrapes the sandbox service. | `infra/prometheus/prometheus.yml` | `SandboxBoundaryTests`. |

## 23. The operational frontend

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 23.1 | The run page shows each tool the sandbox executed: the tool, its status, its duration, the abbreviated sandbox identifier and a summary. | `apps/web/src/app/agent-runtime/agent-runtime.html` | `apps/web/src/app/agent-runtime/agent-runtime.spec.ts`. |
| 23.2 | The page never receives a tool's output and offers no interactive shell. | `apps/web/src/app/agent-runtime/agent-runtime.html`, `packages/contracts/src/iacode_contracts/sandbox.py` | `test_the_page_offers_nothing_that_would_execute_a_tool`; `test_the_detail_shows_what_the_sandbox_executed_and_not_its_output`. |
| 23.3 | The command line interface stays reserved for the Gate that owns it. | `.iacode/policies/gate-scope.json` | `Gate3ScopeTests`. |

## 24. The deterministic coding scenario

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 24.1 | A synthetic repository with a defective function and a failing test is provisioned as a snapshot, and a coding run over it reads the code, runs the failing test, patches the code, runs the passing test, reads the diff, commits locally, is reviewed and finishes. | `scripts/iacode/scenarios/sandbox_coding_e2e.py` | Recorded synthetic coding scenario run; `SandboxScenarioTests`. |
| 24.2 | The scenario drives the real workflow, the real activities, the real sandbox service and the real container engine, with only the model replaced by a deterministic script. | `scripts/iacode/scenarios/sandbox_coding_e2e.py`, `services/orchestrator/rehearsal/` | `SandboxScenarioTests`. |
| 24.3 | An automatic proof shows a shell request did not execute on the host: a sentinel outside the sandbox is neither created nor modified. | `scripts/iacode/scenarios/sandbox_coding_e2e.py` | Recorded synthetic coding scenario run; `SandboxScenarioTests`. |
| 24.4 | The scenario asserts what the run recorded — its terminal state, its tool executions and the test that passed — rather than what the harness sent. | `scripts/iacode/scenarios/sandbox_coding_e2e.py` | `SandboxScenarioTests`. |

## 25. Verification, documentation and decisions

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 25.1 | The repository's one verification command covers this Gate, in its targeted and its full mode. | `scripts/iacode/verify.py` | `Gate3VerificationStageTests`; full verification run recorded in `VERIFICATION-REPORT.json`. |
| 25.2 | A runbook documents the lifecycle, the tool policy, the filesystem, the shell, Git, the network, resources, artifacts, cleanup, debugging and the security boundary. | `docs/runbooks/SANDBOX.md` | `Gate3DocumentationTests`. |
| 25.3 | The architecture, development, version and entry documents describe what this Gate delivered rather than what was planned. | `docs/ARCHITECTURE.md`, `docs/DEVELOPMENT.md`, `docs/VERSIONS.md`, `README.md`, `START-HERE.md` | `Gate3DocumentationTests`. |
| 25.4 | The structural decisions of this Gate are recorded as ADRs and listed in the index. | `docs/adr/` | `ADR-0024`, `ADR-0025`, `ADR-0026`, `ADR-0027`; `Gate3AdrTests`. |
| 25.5 | The Gate produces its retrospective from the canonical template, and its reusable lessons are recorded with the guardrail that protects the property rather than one file. | `.iacode/memory/retrospectives/GATE-3-CP-0001.md`, `.iacode/memory/lessons.jsonl` | `validate_lessons.py`; the retrospective is present and follows `.iacode/templates/retrospective/TEMPLATE.md`. |
| 25.6 | Every commit of the Gate and its checkpoint tag are on the authorised remote when the Gate closes. | `scripts/development-ledger/remote_sync.py` | Recorded remote synchronisation check reporting `PASS`. |
| 25.7 | The Gate closes at the project's own internal verdict, leaves the milestone verdict to a fresh-session audit, and starts no part of the Gate that follows it. | `docs/checkpoints/GATE-3-CP-0001/STATE.json` | Checkpoint validation; `Gate3ScopeTests`. |
