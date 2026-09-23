# Risks — GATE-3-CP-0001

Each risk names what would make it real, what currently holds it down, and what would have to change
for it to stop being a risk.

## Open

**R-G3-001 — The sandbox service holds the container engine's socket.** Severity: HIGH. Whoever
controls the controller process controls the engine, and the engine is root-equivalent on the
Docker Desktop VM. Held down by: it is the only service given the socket
(`test_only_the_sandbox_service_is_given_the_engine_socket`); it runs with every capability dropped,
no new privileges and no published port; it starts only the container client, with argument vectors
and never a command a request supplied (`test_the_backend_starts_only_the_container_client`,
`test_the_image_decides_the_command_not_the_request`); and it never hands the socket on
(`test_no_docker_socket_or_engine_endpoint_is_reachable`, Red Team `G3-F`). It would stop being a
risk with a rootless engine or a socket proxy that exposes only the container operations the
backend uses.

**R-G3-002 — A container shares the kernel.** Severity: MEDIUM. A kernel vulnerability reachable
from an unprivileged process escapes any container. Held down by: no capability, no new privileges,
an unprivileged user, a read-only root, no host mount, no network, bounded processes and memory,
and the engine's default seccomp profile (`ADR-0025`). It would stop being a risk with a
user-space kernel or micro-VM runtime, which the backend's single argument builder can adopt.

**R-G3-003 — The sweep is bounded, and a process held in the kernel longer than the bound
survives it.** Severity: LOW. `kill_everything_else` gives up after fifteen seconds; a process
blocked in the kernel that long outlives the command. Held down by: the process limit contains it,
the next command still starts, and the run's release removes the container (`LSN-0053`,
`test_a_fork_bomb_that_detaches_leaves_a_sandbox_that_still_answers`).

**R-G3-004 — Several large tool results can exceed the runtime's context bound.** Severity: LOW.
Each result is bounded to what the runtime accepts (`LSN-0051`), but a stage that reads many large
files accumulates context, and the runtime refuses a context above its bound. Held down by: the
refusal is an explicit, classified failure of the run, never a silent truncation of the task
(`GATE 2` row 9.8).

**R-G3-005 — The sandbox image's system packages and the static Docker client are not scanned.**
Severity: MEDIUM. They are pinned by exact version and by digest, and no scanner for them exists in
the repository (`DECISIONS.md` D-09, runbook "Dependency scanning"). It would stop being a risk
with an image scanner in the dependency scan.

**R-G3-006 — Sandbox runs, sessions and snapshots have no retention.** Severity: LOW. Rehearsal
runs, their sandbox sessions and the snapshots stored for them stay in the database and the bucket.
Held down by: the containers themselves are removed with each run and swept at expiry; only rows and
objects remain. Backlog: a retention policy.

**R-G3-007 — The pre-push discipline is a practice, not a control.** Severity: MEDIUM. Three pushed
commits left a mandatory gate red before it was adopted (`G3-F-002`, `LSN-0054`, `CONFIRMED`). Held
down by: every later push ran the lint gate and the repository-wide scans; the Green Keeper at
closure runs every mandatory gate over the final content. It would stop being a risk with a
pre-push hook or a remote check that runs the gates a change reaches.

**R-G3-008 — No live model has driven the sandbox.** Severity: LOW. The deterministic scenarios
prove the tooling with a scripted model; a live model's tool requests were not exercised, as the
Gate allows (prompt section 120: optional). Held down by: a live model reaches the sandbox only
through the same envelope, the same allowed actions and the same policy the scripted model used.

## Closed

**R-G2-002 — GATE 3 could implement the executor on the wrong side of the boundary.** Closed by this
Gate: the executor is the sandbox service, reached only as an activity on its own queue; the
runtime and the worker still execute nothing (`RepositoryToolExecutionBoundaryTests`,
`ToolExecutionBoundaryTests`), and no module outside the sandbox imports it or a container client
(`SandboxBoundaryTests`, Red Team `G3-W`).
