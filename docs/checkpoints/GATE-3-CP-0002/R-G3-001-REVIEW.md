# R-G3-001 — the container engine socket held by the sandbox controller

Disposition: `ACCEPTED_LOCAL_ARCHITECTURAL_RISK` — 10/10 controls proved (`R-G3-001-REVIEW.json`, `cmd-0011`) and attack `M1-G` defended (`M1-INTERNAL-RED-TEAM.json`).

The owner's mandate accepts the socket for the local MVP only if ten controls are proved from the
running stack and the source, and requires a Critical or High finding the moment any untrusted
input can reach an arbitrary engine operation. No input can: the only argument builder of the
engine reads a specification filled from the policy's image and resources and a generated session
name; the request contract is closed; tool arguments travel as JSON on the helper's standard
input inside the container; and the attack that fed engine-shaped run identifiers and commands
found the engine's containers created from the policy alone.

| Control | Result | Observed |
|---|---|---|
| C1 the agent receives no socket | `PASS` | containers of the stack that mount the engine socket: ['iacode-sandbox']; the worker that runs agents mounts none |
| C2 no child sandbox receives the socket | `PASS` | flags the only container builder can emit that could hand a sandbox a host resource: none; the battery's M1-C inspects a real child |
| C3 no ToolRequest controls engine arguments | `PASS` | ContainerSpec fields ['name', 'image', 'session_id', 'run_id', 'policy', 'expires_at_epoch', 'cpus', 'memory_mb', 'pids', 'workspace_mb', 'tmp_mb', 'owner', 'network', 'labels'] are filled from the policy's image and resources and a generated session name; the request contract is closed to ['agent', 'agentRunId', 'arguments', 'contractVersion', 'policy', 'runId', 'tool', 'toolRequestId', 'workspace'], refused beside it by _strict; tool arguments travel as JSON on the helper's stdin |
| C4 no public API accepts a generic engine operation | `PASS` | the controller serves two activities (['SANDBOX_EXECUTE_ACTIVITY', 'SANDBOX_RELEASE_ACTIVITY']) and no HTTP surface; the API source names no engine client (none) |
| C5 the controller publishes no port | `PASS` | port bindings none; published ports none |
| C6 cap_drop and no-new-privileges remain | `PASS` | CapDrop ['ALL'], CapAdd none, SecurityOpt ['no-new-privileges:true'], Privileged False, User 'iacode' |
| C7 arbitrary host mounts are impossible | `PASS` | the controller's only mount is ['/var/run/docker.sock:/var/run/docker.sock']; the child builder emits no volume, mount or env-file flag; the battery's M1-G checks the children the engine created |
| C8 the network policy is imposed | `PASS` | children start with --network from the spec, 'none' unless the policy grants its own internal network; declared profiles ['none'] |
| C9 the tool policy limits operations | `PASS` | the registry is closed (an unknown name raises ToolRejectedError), each policy names its tools, and no remote Git verb exists |
| C10 only trusted controller code talks to the engine | `PASS` | modules that start a process: ['services/sandbox/src/iacode_sandbox/backend.py', 'services/sandbox/src/iacode_sandbox/helper.py'] (helper.py runs inside the sandbox, never in the controller); backend refuses any executable but docker and never uses a shell |

## Backlog

Replace direct socket access by a rootless container engine or a restricted socket proxy that exposes only the create, exec, inspect, list and remove operations the backend uses.
