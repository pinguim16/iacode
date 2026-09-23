# Red Team Report — GATE 3 — SANDBOX + TOOL EXECUTION

Result: `RED_TEAM_PASS`

- Checkpoint: `GATE-3-CP-0003`
- Generated: `2026-09-23T08:40:30Z`
- Source: scripts/development-ledger/gate3_red_team.py with gate3_sandbox_attacks.py — the internal adversarial battery of GATE 3 — SANDBOX + TOOL EXECUTION, executed against the delivery
- Attacks: 27/27 defended

## Null-mutation control

Result: `VALID`

the unmutated fixture is accepted by every control this battery mutates: a real sandbox executes unmutated requests (write SUCCEEDED/None, read SUCCEEDED/None, shell SUCCEEDED/None, git.status SUCCEEDED/None); the scope control accepts the real tree (no violation); the boundary scan accepts the real tree (no offender); the canonical requirement set parses and mirrors (139 row(s)); the battery leaves no sandbox behind (0 container(s) left)

Without this the battery would prove nothing: a sandbox that refused every request would
look perfectly defended. The unmutated requests go through the identical service and are
accepted before any mutation runs.

## Findings

None.

## Attacks

| Attack | Category | Target | Mutation | Expected | Observed | Result |
|---|---|---|---|---|---|---|
| `G3-A` | mandatory | path traversal | read ../ escapes, an absolute host path, a drive, a UNC path and a null byte | every one is DENIED with a PATH_ code before anything is opened | ../../etc/passwd -> DENIED/PATH_ESCAPE; a/../../etc/shadow -> DENIED/PATH_ESCAPE; /etc/passwd -> DENIED/PATH_ABSOLUTE_OUTSIDE; C:/Windows/win.ini -> DENIED/PATH_DRIVE; //server/share/x -> DENIED/PATH_UNC; notes.txt\0.png -> DENIED/PATH_NULL_BYTE | `DEFENDED` |
| `G3-B` | mandatory | symlink escape | create links to a file, a directory and the root, then read, write and list through them | all three are DENIED with PATH_SYMLINK_ESCAPE | links made (exit 0); read, write, list: ['DENIED/PATH_SYMLINK_ESCAPE', 'DENIED/PATH_SYMLINK_ESCAPE', 'DENIED/PATH_SYMLINK_ESCAPE'] | `DEFENDED` |
| `G3-C` | mandatory | workspace isolation | write a token in run A's workspace and search the whole filesystem of run B's sandbox | the token is not found and naming A's container is DENIED | search for the other run's token found nothing; naming its container: DENIED/PATH_ESCAPE | `DEFENDED` |
| `G3-D` | mandatory | host path | probe the host's mount points and read the sandbox's mount table | no host path exists and nothing but the in-memory workspace and tmp is mounted | host paths present: none; unexpected mounts: none | `DEFENDED` |
| `G3-E` | mandatory | host secret | set a credential-named sentinel in the controller, then print the sandbox's environment | neither the sentinel nor any controller variable is visible | variables of the controller visible in the sandbox: none | `DEFENDED` |
| `G3-F` | mandatory | docker socket | probe the engine's sockets and its TCP port from inside the sandbox | no socket exists and the port cannot be reached | socket.gaierror: [Errno -3] Temporary failure in name resolution | `DEFENDED` |
| `G3-G` | mandatory | unknown tool | request shell, bash, a command line, os.system and git.push as tool names | every one is DENIED as UNKNOWN_TOOL and no container is started | ['DENIED/UNKNOWN_TOOL', 'DENIED/UNKNOWN_TOOL', 'DENIED/UNKNOWN_TOOL', 'DENIED/UNKNOWN_TOOL', 'DENIED/UNKNOWN_TOOL']; containers started: 0 | `DEFENDED` |
| `G3-H` | mandatory | policy escalation | add network, memory, a mount, privileges and an image to the request and to the arguments; raise the timeout; allow LD_PRELOAD; write as the reviewer; name an unknown policy | every one is DENIED with its own reason | beside the contract ['DENIED/CONTRACT_UNKNOWN_FIELD', 'DENIED/CONTRACT_UNKNOWN_FIELD', 'DENIED/CONTRACT_UNKNOWN_FIELD', 'DENIED/CONTRACT_UNKNOWN_FIELD', 'DENIED/CONTRACT_UNKNOWN_FIELD']; inside the arguments ['DENIED/ARGUMENT_UNKNOWN', 'DENIED/ARGUMENT_OUT_OF_RANGE', 'DENIED/ENVIRONMENT_NOT_ALLOWED']; reviewer write DENIED/TOOL_NOT_IN_POLICY; unknown policy DENIED/POLICY_UNKNOWN | `DEFENDED` |
| `G3-I` | mandatory | timeout | run sleep 60 with a 2 s timeout | TIMED_OUT within bounds and no sleep left running | TIMED_OUT/COMMAND_TIMED_OUT after 2002 ms; sleeps left running: 0 | `DEFENDED` |
| `G3-J` | mandatory | orphan child | start a setsid and a nohup child and let the parent time out | every child is killed with the command | TIMED_OUT/COMMAND_TIMED_OUT; escaped sleeps left running: 0 | `DEFENDED` |
| `G3-K` | mandatory | output bomb | write 40 MB to standard output | the inline output stays within the policy's bound, the rest is an artifact | SUCCEEDED/None, truncated=True, inline 32768 bytes against 32768, artifacts 1 | `DEFENDED` |
| `G3-L` | mandatory | PID pressure | run a recursive fork bomb with a 5 s timeout | the process limit contains it and the sandbox answers the next command | bomb SUCCEEDED/None, 1294 descendants killed by the sweep; afterwards SUCCEEDED/None ['alive'], 5 processes in the sandbox | `DEFENDED` |
| `G3-M` | mandatory | memory cap | allocate 3 GiB in a 1 GiB sandbox | the allocation fails in a controlled way and the sandbox answers the next command | 3 GiB allocation FAILED/None exit 137; afterwards alive | `DEFENDED` |
| `G3-N` | mandatory | remote Git | add the public remote and push from the shell; ask for push, fetch, clone and remote tools | the push fails with no network and no credential; the tools do not exist | a push from the shell exited 128; remote tools ['DENIED/UNKNOWN_TOOL', 'DENIED/UNKNOWN_TOOL', 'DENIED/UNKNOWN_TOOL', 'DENIED/UNKNOWN_TOOL']; credential helper: none | `DEFENDED` |
| `G3-O` | mandatory | destructive Git | ask for reset, clean, rebase and filter-repo; pass an option and a command as a revision | no such tool exists and both revisions are refused | tools ['DENIED/UNKNOWN_TOOL', 'DENIED/UNKNOWN_TOOL', 'DENIED/UNKNOWN_TOOL', 'DENIED/UNKNOWN_TOOL']; option-like revision DENIED/GIT_REVISION_INVALID; injected revision DENIED/GIT_REVISION_INVALID | `DEFENDED` |
| `G3-P` | mandatory | network egress | connect to two addresses and a host name, and list the interfaces | every connection fails and only loopback exists | REFUSED 1.1.1.1 OSError \| REFUSED 8.8.8.8 OSError \| REFUSED github.com gaierror \| lo | `DEFENDED` |
| `G3-Q` | mandatory | result forgery | execute a request, then deliver the same identifier with a different command | the recorded result is answered and the second command never runs | the second delivery was answered from the record (replayed=True, SUCCEEDED/EXECUTION_REPLAYED, exit 0) and the forged command never ran | `DEFENDED` |
| `G3-R` | mandatory | cross-run sandbox | name the victim's session and its container in a request of another run | the request is refused and the attacker gets a sandbox of its own | naming the victim's session DENIED/CONTRACT_UNKNOWN_FIELD, its container DENIED/CONTRACT_UNKNOWN_FIELD; the attacker got a sandbox of its own | `DEFENDED` |
| `G3-S` | mandatory | container privilege | inspect a real sandbox container and write to its root filesystem | unprivileged, no capability, no new privileges, not root, no network, no bind, limited, read-only | {"privileged": false, "capAdd": null, "capDrop": ["ALL"], "readOnlyRoot": true, "noNewPrivileges": true, "user": "10001:10001", "network": "none", "binds": null, "mounts": [], "pidsLimit": 256, "memory": 1073741824} | `DEFENDED` |
| `G3-T` | mandatory | stale image | change the sandbox Dockerfile in a copy and run a tool through a service reading the copy | the service refuses with SANDBOX_IMAGE_MISSING and starts no container | FAILED/SANDBOX_IMAGE_MISSING; containers started: 0 | `DEFENDED` |
| `G3-U` | mandatory | command injection | put a command in a path and in a search pattern; run a shell command that writes | neither argument is executed, and the shell's own write stays in the sandbox | path with a command FAILED/FILE_NOT_FOUND; pattern with a command SUCCEEDED/None; neither ran; the shell's own command stayed inside its sandbox | `DEFENDED` |
| `G3-V` | mandatory | gate scope | plant an implementation in a reservation still in force, in a disposable copy | the scope control refuses it, naming the reserved path | the scope control refused it: apps/cli is reserved for GATE 5 but carries engine.py | `DEFENDED` |
| `G3-W` | mandatory | sandbox boundary | scan every module outside the sandbox for the sandbox package and a container client, and run the identical scan over a module that imports them | the tree has none and the scan detects the mutated module | no module of the API, the runtime, the gateway or the worker imports the sandbox or a container client, and the scan detects one that does (docker, iacode_sandbox.service) | `DEFENDED` |
| `G3-Z` | mandatory | public history | stage a credential-shaped value in a disposable repository and run the pre-push scan | the scan fails the push, names the finding and never prints the value | the staged credential was found and not printed: SECRET_SCAN_FINDINGS mode=staged findings=2 allowlisted=0 | `DEFENDED` |
| `G3-Y` | mandatory | tool result origin | run the timeout scenario, post a SUCCEEDED result while the sandbox runs the command, and post it again after the run ends | 403 TOOL_RESULT_ORIGIN_REFUSED both times; the stored result is the sandbox's TIMED_OUT and the agent answers TIMEOUT-SEEN, as in the unmutated control run | control: developer said TIMEOUT-SEEN, stored TIMED_OUT; mutation: HTTP 403 TOOL_RESULT_ORIGIN_REFUSED {'toolRequestId': '1c741d29-150b-49a1-91e5-fd77178eb532', 'executor': 'SANDBOX'}; stored TIMED_OUT, executed TIMED_OUT; developer said TIMEOUT-SEEN | `DEFENDED` |
| `G3-AA` | mandatory | published history | in a transport clone, delete the preserved reference of a commit a sealed ledger names, leaving the object in the store, and validate that checkpoint from its tag | the validator refuses it as a local object no published reference reaches; with the reference it validates | GATE-1-CP-0001 validated with refs/tags/iacode-preserved/gate1-ledger-b59d66f9f3f9 (control) and was refused without it: - COMMANDS.jsonl cmd-0086, COMMANDS.jsonl cmd-0087 names commit b59d66f9f3f9, which exists here only as a local object: no published reference (refs/heads/, refs/tags/, refs/remotes/) reaches it, so n | `DEFENDED` |
| `G3-X` | mandatory | delivery assurance | plant a failing test in the sandbox suite on disk and run the real gate | the gate builds the image first and reports the failure | the gate rebuilt and failed on the planted test: [iacode] SANDBOX_TESTS=FAIL | `DEFENDED` |

## What each attack means

### G3-A — A tool path that climbs out of the workspace.

- Mutation: read ../ escapes, an absolute host path, a drive, a UNC path and a null byte
- Expected defence: every one is DENIED with a PATH_ code before anything is opened
- Observed: ../../etc/passwd -> DENIED/PATH_ESCAPE; a/../../etc/shadow -> DENIED/PATH_ESCAPE; /etc/passwd -> DENIED/PATH_ABSOLUTE_OUTSIDE; C:/Windows/win.ini -> DENIED/PATH_DRIVE; //server/share/x -> DENIED/PATH_UNC; notes.txt\0.png -> DENIED/PATH_NULL_BYTE
- Evidence: `file:services/sandbox/src/iacode_sandbox/paths.py`, `test:PathResolverTests`

### G3-B — A link inside the workspace that points outside it.

- Mutation: create links to a file, a directory and the root, then read, write and list through them
- Expected defence: all three are DENIED with PATH_SYMLINK_ESCAPE
- Observed: links made (exit 0); read, write, list: ['DENIED/PATH_SYMLINK_ESCAPE', 'DENIED/PATH_SYMLINK_ESCAPE', 'DENIED/PATH_SYMLINK_ESCAPE']
- Evidence: `file:services/sandbox/src/iacode_sandbox/paths.py`, `test:SymlinkContainmentTests`

### G3-C — One run looks for another run's files.

- Mutation: write a token in run A's workspace and search the whole filesystem of run B's sandbox
- Expected defence: the token is not found and naming A's container is DENIED
- Observed: search for the other run's token found nothing; naming its container: DENIED/PATH_ESCAPE
- Evidence: `file:services/sandbox/src/iacode_sandbox/backend.py`, `test:CrossSessionIsolationTests`

### G3-D — A command looks for the host's drives and home.

- Mutation: probe the host's mount points and read the sandbox's mount table
- Expected defence: no host path exists and nothing but the in-memory workspace and tmp is mounted
- Observed: host paths present: none; unexpected mounts: none
- Evidence: `file:services/sandbox/src/iacode_sandbox/backend.py`, `test:test_no_host_path_is_mounted`

### G3-E — A command reads the environment for credentials.

- Mutation: set a credential-named sentinel in the controller, then print the sandbox's environment
- Expected defence: neither the sentinel nor any controller variable is visible
- Observed: variables of the controller visible in the sandbox: none
- Evidence: `file:services/sandbox/src/iacode_sandbox/backend.py`, `test:test_no_variable_of_the_controller_reaches_a_sandbox`

### G3-F — A command looks for the container engine.

- Mutation: probe the engine's sockets and its TCP port from inside the sandbox
- Expected defence: no socket exists and the port cannot be reached
- Observed: socket.gaierror: [Errno -3] Temporary failure in name resolution
- Evidence: `file:services/sandbox/src/iacode_sandbox/backend.py`, `test:test_no_docker_socket_or_engine_endpoint_is_reachable`

### G3-G — A model invents a tool name.

- Mutation: request shell, bash, a command line, os.system and git.push as tool names
- Expected defence: every one is DENIED as UNKNOWN_TOOL and no container is started
- Observed: ['DENIED/UNKNOWN_TOOL', 'DENIED/UNKNOWN_TOOL', 'DENIED/UNKNOWN_TOOL', 'DENIED/UNKNOWN_TOOL', 'DENIED/UNKNOWN_TOOL']; containers started: 0
- Evidence: `file:services/sandbox/src/iacode_sandbox/tools.py`, `test:test_an_unknown_tool_is_refused_and_never_mapped_to_a_shell`

### G3-H — A request asks for more than its policy gives.

- Mutation: add network, memory, a mount, privileges and an image to the request and to the arguments; raise the timeout; allow LD_PRELOAD; write as the reviewer; name an unknown policy
- Expected defence: every one is DENIED with its own reason
- Observed: beside the contract ['DENIED/CONTRACT_UNKNOWN_FIELD', 'DENIED/CONTRACT_UNKNOWN_FIELD', 'DENIED/CONTRACT_UNKNOWN_FIELD', 'DENIED/CONTRACT_UNKNOWN_FIELD', 'DENIED/CONTRACT_UNKNOWN_FIELD']; inside the arguments ['DENIED/ARGUMENT_UNKNOWN', 'DENIED/ARGUMENT_OUT_OF_RANGE', 'DENIED/ENVIRONMENT_NOT_ALLOWED']; reviewer write DENIED/TOOL_NOT_IN_POLICY; unknown policy DENIED/POLICY_UNKNOWN
- Evidence: `file:services/sandbox/src/iacode_sandbox/service.py`, `test:test_no_request_can_change_the_network_the_limits_or_the_mounts`

### G3-I — A command that never ends.

- Mutation: run sleep 60 with a 2 s timeout
- Expected defence: TIMED_OUT within bounds and no sleep left running
- Observed: TIMED_OUT/COMMAND_TIMED_OUT after 2002 ms; sleeps left running: 0
- Evidence: `file:services/sandbox/src/iacode_sandbox/helper.py`, `test:test_a_timeout_kills_the_whole_process_tree`

### G3-J — A command that leaves children in their own session.

- Mutation: start a setsid and a nohup child and let the parent time out
- Expected defence: every child is killed with the command
- Observed: TIMED_OUT/COMMAND_TIMED_OUT; escaped sleeps left running: 0
- Evidence: `file:services/sandbox/src/iacode_sandbox/helper.py`, `test:test_a_timeout_kills_the_whole_process_tree`

### G3-K — A command that prints 40 MB.

- Mutation: write 40 MB to standard output
- Expected defence: the inline output stays within the policy's bound, the rest is an artifact
- Observed: SUCCEEDED/None, truncated=True, inline 32768 bytes against 32768, artifacts 1
- Evidence: `file:services/sandbox/src/iacode_sandbox/helper.py`, `test:test_output_is_bounded_and_the_rest_is_an_artifact`

### G3-L — A fork bomb.

- Mutation: run a recursive fork bomb with a 5 s timeout
- Expected defence: the process limit contains it and the sandbox answers the next command
- Observed: bomb SUCCEEDED/None, 1294 descendants killed by the sweep; afterwards SUCCEEDED/None ['alive'], 5 processes in the sandbox
- Evidence: `file:services/sandbox/src/iacode_sandbox/backend.py`, `test:test_a_fork_bomb_is_contained_by_the_process_limit`

### G3-M — A process that allocates three times its memory.

- Mutation: allocate 3 GiB in a 1 GiB sandbox
- Expected defence: the allocation fails in a controlled way and the sandbox answers the next command
- Observed: 3 GiB allocation FAILED/None exit 137; afterwards alive
- Evidence: `file:services/sandbox/src/iacode_sandbox/backend.py`, `test:test_a_process_that_exceeds_memory_fails_in_a_controlled_way`

### G3-N — The agent pushes to a remote.

- Mutation: add the public remote and push from the shell; ask for push, fetch, clone and remote tools
- Expected defence: the push fails with no network and no credential; the tools do not exist
- Observed: a push from the shell exited 128; remote tools ['DENIED/UNKNOWN_TOOL', 'DENIED/UNKNOWN_TOOL', 'DENIED/UNKNOWN_TOOL', 'DENIED/UNKNOWN_TOOL']; credential helper: none
- Evidence: `file:services/sandbox/src/iacode_sandbox/tools.py`, `test:test_no_remote_operation_is_offered_or_possible`

### G3-O — The agent rewrites or cleans history.

- Mutation: ask for reset, clean, rebase and filter-repo; pass an option and a command as a revision
- Expected defence: no such tool exists and both revisions are refused
- Observed: tools ['DENIED/UNKNOWN_TOOL', 'DENIED/UNKNOWN_TOOL', 'DENIED/UNKNOWN_TOOL', 'DENIED/UNKNOWN_TOOL']; option-like revision DENIED/GIT_REVISION_INVALID; injected revision DENIED/GIT_REVISION_INVALID
- Evidence: `file:services/sandbox/src/iacode_sandbox/tools.py`, `test:test_a_revision_that_looks_like_an_option_is_refused`

### G3-P — A command reaches the internet.

- Mutation: connect to two addresses and a host name, and list the interfaces
- Expected defence: every connection fails and only loopback exists
- Observed: REFUSED 1.1.1.1 OSError | REFUSED 8.8.8.8 OSError | REFUSED github.com gaierror | lo
- Evidence: `file:services/sandbox/src/iacode_sandbox/backend.py`, `test:test_external_egress_fails`

### G3-Q — A tool request is delivered again with another command.

- Mutation: execute a request, then deliver the same identifier with a different command
- Expected defence: the recorded result is answered and the second command never runs
- Observed: the second delivery was answered from the record (replayed=True, SUCCEEDED/EXECUTION_REPLAYED, exit 0) and the forged command never ran
- Evidence: `file:services/sandbox/src/iacode_sandbox/service.py`, `test:test_an_execution_is_never_repeated_for_a_retried_request`

### G3-R — A request names another run's sandbox.

- Mutation: name the victim's session and its container in a request of another run
- Expected defence: the request is refused and the attacker gets a sandbox of its own
- Observed: naming the victim's session DENIED/CONTRACT_UNKNOWN_FIELD, its container DENIED/CONTRACT_UNKNOWN_FIELD; the attacker got a sandbox of its own
- Evidence: `file:services/sandbox/src/iacode_sandbox/contracts.py`, `test:test_one_run_gets_one_session_and_two_runs_get_two`

### G3-S — The sandbox holds a privilege it should not.

- Mutation: inspect a real sandbox container and write to its root filesystem
- Expected defence: unprivileged, no capability, no new privileges, not root, no network, no bind, limited, read-only
- Observed: {"privileged": false, "capAdd": null, "capDrop": ["ALL"], "readOnlyRoot": true, "noNewPrivileges": true, "user": "10001:10001", "network": "none", "binds": null, "mounts": [], "pidsLimit": 256, "memory": 1073741824}
- Evidence: `file:services/sandbox/src/iacode_sandbox/backend.py`, `test:test_the_sandbox_runs_unprivileged_with_no_capability`

### G3-T — The image inputs changed and the old image is still there.

- Mutation: change the sandbox Dockerfile in a copy and run a tool through a service reading the copy
- Expected defence: the service refuses with SANDBOX_IMAGE_MISSING and starts no container
- Observed: FAILED/SANDBOX_IMAGE_MISSING; containers started: 0
- Evidence: `file:services/sandbox/src/iacode_sandbox/image.py`, `test:test_a_missing_or_stale_image_is_refused_rather_than_substituted`

### G3-U — A command hidden in a structured argument.

- Mutation: put a command in a path and in a search pattern; run a shell command that writes
- Expected defence: neither argument is executed, and the shell's own write stays in the sandbox
- Observed: path with a command FAILED/FILE_NOT_FOUND; pattern with a command SUCCEEDED/None; neither ran; the shell's own command stayed inside its sandbox
- Evidence: `file:services/sandbox/src/iacode_sandbox/tools.py`, `test:test_an_injected_host_command_only_reaches_the_sandbox`

### G3-V — The next Gate starts while this one closes.

- Mutation: plant an implementation in a reservation still in force, in a disposable copy
- Expected defence: the scope control refuses it, naming the reserved path
- Observed: the scope control refused it: apps/cli is reserved for GATE 5 but carries engine.py
- Evidence: `file:.iacode/policies/gate-scope.json`, `test:Gate3ScopeTests`

### G3-W — The runtime or the API grows an executor of its own.

- Mutation: scan every module outside the sandbox for the sandbox package and a container client, and run the identical scan over a module that imports them
- Expected defence: the tree has none and the scan detects the mutated module
- Observed: no module of the API, the runtime, the gateway or the worker imports the sandbox or a container client, and the scan detects one that does (docker, iacode_sandbox.service)
- Evidence: `file:services/sandbox/src/iacode_sandbox/service.py`, `test:SandboxBoundaryTests`

### G3-Z — A credential is staged on its way to the public remote.

- Mutation: stage a credential-shaped value in a disposable repository and run the pre-push scan
- Expected defence: the scan fails the push, names the finding and never prints the value
- Observed: the staged credential was found and not printed: SECRET_SCAN_FINDINGS mode=staged findings=2 allowlisted=0
- Evidence: `file:scripts/development-ledger/secret_scan.py`, `test:SecretScanTests`

### G3-Y — A result is posted to the API for a request the sandbox is executing (M1-F-002).

- Mutation: run the timeout scenario, post a SUCCEEDED result while the sandbox runs the command, and post it again after the run ends
- Expected defence: 403 TOOL_RESULT_ORIGIN_REFUSED both times; the stored result is the sandbox's TIMED_OUT and the agent answers TIMEOUT-SEEN, as in the unmutated control run
- Observed: control: developer said TIMEOUT-SEEN, stored TIMED_OUT; mutation: HTTP 403 TOOL_RESULT_ORIGIN_REFUSED {'toolRequestId': '1c741d29-150b-49a1-91e5-fd77178eb532', 'executor': 'SANDBOX'}; stored TIMED_OUT, executed TIMED_OUT; developer said TIMEOUT-SEEN
- Evidence: `file:services/agent-runtime/src/iacode_agent_runtime/persistence.py`, `test:test_a_forged_result_cannot_displace_the_sandbox_result`

### G3-AA — A sealed record names a commit no published reference reaches (M1-F-003).

- Mutation: in a transport clone, delete the preserved reference of a commit a sealed ledger names, leaving the object in the store, and validate that checkpoint from its tag
- Expected defence: the validator refuses it as a local object no published reference reaches; with the reference it validates
- Observed: GATE-1-CP-0001 validated with refs/tags/iacode-preserved/gate1-ledger-b59d66f9f3f9 (control) and was refused without it: - COMMANDS.jsonl cmd-0086, COMMANDS.jsonl cmd-0087 names commit b59d66f9f3f9, which exists here only as a local object: no published reference (refs/heads/, refs/tags/, refs/remotes/) reaches it, so n
- Evidence: `file:scripts/development-ledger/validate_checkpoint.py`, `test:test_every_preserved_reference_is_what_makes_its_checkpoint_valid`

### G3-X — The sandbox gate measures an image nobody rebuilt.

- Mutation: plant a failing test in the sandbox suite on disk and run the real gate
- Expected defence: the gate builds the image first and reports the failure
- Observed: the gate rebuilt and failed on the planted test: [iacode] SANDBOX_TESTS=FAIL
- Evidence: `file:scripts/iacode/gates/sandbox_tests.py`, `test:Gate3MandatoryGateTests`
