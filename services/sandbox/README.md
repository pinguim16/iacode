# Sandbox

Delivered by `GATE 3 — SANDBOX`. The service that executes an agent's tools, and the only place in
IACode where anything an agent asked for is executed.

```text
agent turn ──TOOL_REQUEST──▶ AgentRunWorkflow ──activity──▶ sandbox service ──docker exec──▶ helper
                                   ▲                         (this package)                  (inside a
                                   └──────── ToolResult ◀────────────────────────────────── container)
```

A tool request never runs on the host, in the API, in the worker or in this service's own process.
It runs inside a disposable container the service creates for the run, from the canonical policy in
[`.iacode/policies/sandbox-policy.json`](../../.iacode/policies/sandbox-policy.json):

- a read-only root filesystem, and a size-limited in-memory `/workspace` and `/tmp`;
- no capability, no new privileges, never privileged, an unprivileged user;
- no network (`none`), no Docker socket, no host path, no inherited variable, no credential;
- bounded CPU, memory, processes, command time and output;
- one container per run, removed when the run ends and swept when it expires.

## Layout

| Path | What it is |
|---|---|
| `src/iacode_sandbox/contracts.py` | The versioned contracts: request, result, session, workspace, operations, artifacts. |
| `src/iacode_sandbox/policy.py` | The canonical policy, validated against hard bounds. |
| `src/iacode_sandbox/tools.py` | The closed tool registry and each tool's argument validation. |
| `src/iacode_sandbox/paths.py` | The one path resolver: nothing it returns lies outside the workspace. |
| `src/iacode_sandbox/patching.py` | A unified-diff applier that applies everything or nothing. |
| `src/iacode_sandbox/helper.py` | The program inside a sandbox (also its PID 1): filesystem, processes, Git. |
| `src/iacode_sandbox/backend.py` | The container engine, through its client, with every hardening flag. |
| `src/iacode_sandbox/service.py` | Create a session, execute a tool, inspect, terminate, reconcile, sweep. |
| `src/iacode_sandbox/store.py` | Sessions and executions in the shared schema. |
| `src/iacode_sandbox/snapshots.py` | Authorised workspace snapshots: the only way content reaches a sandbox. |
| `src/iacode_sandbox/worker.py` | The Temporal worker on the `iacode-sandbox` queue, and the sweeper. |
| `images/iacode-dev/` | The sandbox image profile: Git and Python, addressed by the digest of its inputs. |
| `tests/` | The suite, run against the real engine inside this service's image. |

Operating it: [docs/runbooks/SANDBOX.md](../../docs/runbooks/SANDBOX.md).
