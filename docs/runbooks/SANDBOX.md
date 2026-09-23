# Runbook — Sandbox

Delivered by `GATE 3 — SANDBOX`. How an agent's tools execute, what bounds them, and how to operate,
inspect and debug the service that runs them.

## The security boundary, in one paragraph

Nothing an agent asks for runs on the host, in the API, in the orchestrator worker, or in the
sandbox service's own process. A tool request becomes a structured execution request; the sandbox
service checks it against the canonical policy and runs it inside a disposable container that
belongs to the run — read-only root, no capabilities, no new privileges, an unprivileged user, no
network, no Docker socket, no host path, no inherited environment, bounded CPU, memory, processes,
disk, time and output. The service is the only component with the container engine's socket, and
it never hands it on. See [ADR-0025](../adr/ADR-0025-sandbox-isolation-boundary.md).

## Lifecycle

```text
tool request ─▶ policy check ─▶ session for the run? ──no──▶ create container ─▶ provision workspace
                    │ refused                 │ yes                                   │
                    ▼                         ▼                                       ▼
                 DENIED                 execute in the helper ◀──────────────────── READY
                                              │
                          result (inline, bounded) + artifacts ─▶ recorded in tool_calls
                                              │
                          workflow persists the tool result and resumes the agent
run ends ─▶ release: container removed, session STOPPED        expiry ─▶ sweeper: EXPIRED
```

Session states: `CREATED`, `STARTING`, `READY`, `RUNNING`, `STOPPING`, `STOPPED`, `FAILED`,
`EXPIRED`. One active session per run, enforced by the database. See
[ADR-0026](../adr/ADR-0026-workspace-lifecycle.md).

## The tool policy

The canonical policy is [`.iacode/policies/sandbox-policy.json`](../../.iacode/policies/sandbox-policy.json).
A request names a policy through its agent's profile, frozen into the run's plan; it can never
supply a limit, a mount, an image or a network. See
[ADR-0027](../adr/ADR-0027-tool-execution-policy.md).

| Policy | Tools | Workspace |
|---|---|---|
| `developer` | `filesystem.list/read/search/write/apply_patch`, `shell.exec`, `git.status/diff/log/show/add/commit` | read-write |
| `reviewer` | `filesystem.list/read/search`, `git.status/diff/log/show` | read-only |

A tool name the registry does not hold is refused with `UNKNOWN_TOOL` and never mapped to a shell.
There is no `git.push`, `git.fetch`, `git.reset`, `git.clean` or `git.rebase` tool.

## Resources

The `standard` resource profile: 1 CPU, 1024 MiB of memory (swap equal), 256 processes, a 256 MiB
workspace and a 64 MiB `/tmp` (both in memory), a 300 s command timeout (a request may lower it,
never raise it), 32 KiB of inline output per stream with up to 4 MiB kept as an artifact. Every
value is checked against hard bounds in `iacode_sandbox.policy.BOUNDS`; zero, negative and absurd
values stop the service from starting.

## Filesystem

Every path goes through `iacode_sandbox.paths.resolve_workspace_path`, the one resolver. It
refuses `..` escapes, absolute paths outside `/workspace`, Windows drives, UNC prefixes,
backslashes, null bytes and control characters, and — inside the sandbox, where the links live —
any path that resolves outside the workspace through a symbolic link. Reads and writes are bounded;
a write replaces the file atomically; a patch applies entirely or not at all.

## Shell

`shell.exec` runs `/bin/sh -c <command>` **inside the sandbox**, in a new session, with an
environment built from a fixed base and the policy's allowlist (`CI`, `PYTHONHASHSEED`,
`PYTHONWARNINGS`, `TZ`, `NO_COLOR`). When it ends or times out, every process it started — including
one that escaped into its own session — is killed. The result carries `exitCode` (only when a
process started), `stdout`, `stderr`, `durationMs`, `timedOut`, `truncated` and artifact references.

## Git

Local only, on the disposable workspace, as `IACode Agent <agent@sandbox.iacode.invalid>`. No
credential helper, no remote protocol but `file`, no hooks, and no network. The Git of IACode's own
development — the owner's identity, the GitHub remote — is a different thing and never enters a
sandbox ([ADR-0024](../adr/ADR-0024-public-remote-and-atomic-commits.md)).

## Network

`none` by default: only loopback exists. `local-services` creates an internal network of the
session's own, with no route out; no policy of this Gate uses it.

## Artifacts

Output beyond the inline bound goes to the Foundation's MinIO bucket under
`sandbox/<run>/<tool request>/`, with a row in `artifacts` and its SHA-256. The tool result carries
the reference.

## Workspace snapshots

A run can start from an authorised snapshot instead of an empty repository:

```bash
python scripts/iacode/sandbox_snapshot.py --source path/to/a/directory --name my-snapshot
```

The command archives the directory's regular files (links refused, `.git` and caches excluded),
stores it, and prints the artifact identifier to pass as `workspaceSnapshot` when creating a run.

## Images

The `iacode-dev` image is built from `services/sandbox/images/iacode-dev/` and the helper modules,
tagged with the digest of those inputs:

```bash
python scripts/iacode/sandbox_image.py          # build what is missing
python scripts/iacode/sandbox_image.py --check  # fail when the current inputs have no image
```

The service refuses to create a session when the image for the current inputs is missing or carries
another fingerprint (`SANDBOX_IMAGE_MISSING`, `SANDBOX_IMAGE_STALE`).

## Operating

```bash
python scripts/iacode/stack.py up                  # the stack, the sandbox service included
python scripts/iacode/gates/sandbox_tests.py       # the suite, against the real engine
docker ps --filter label=org.iacode.sandbox=1      # the sandboxes that exist right now
```

The service reconciles its sessions with the engine at start and sweeps expired ones every
`IACODE_SANDBOX_SWEEP_INTERVAL_SECONDS`, at most `IACODE_SANDBOX_SWEEP_BATCH` at a time, never one
that is running a tool. It lists and removes only containers carrying its own owner label.

## Observability

Metrics on `sandbox:9102`, scraped by Prometheus as `iacode-sandbox`: `sandbox_sessions_total`,
`sandbox_active_sessions`, `sandbox_tool_executions_total`, `sandbox_tool_duration_seconds`,
`sandbox_tool_failures_total`, `sandbox_timeouts_total`, `sandbox_policy_rejections_total`. Labels
are tool names, policy names, statuses and reason codes. Logs carry `runId`, `agentId`, `sandboxId`,
`toolName`, `status` and `durationMs` — never a command, an output, a secret or the host's
environment.

## Debugging

| Symptom | Where to look |
|---|---|
| A tool result says `SANDBOX_IMAGE_MISSING` | Run `python scripts/iacode/sandbox_image.py`. |
| A tool result says `SANDBOX_UNAVAILABLE` | `docker logs iacode-sandbox`; the service is down or not polling. |
| A run keeps a container after it ended | The release failed; the sweeper removes it at expiry. |
| `DENIED` with a `PATH_*` code | The path left the workspace; the code names how. |
| `DENIED` with `TOOL_NOT_IN_POLICY` | The agent's policy does not allow that tool. |
| `TIMED_OUT` | The command outlived its timeout and every process it started was killed. |
