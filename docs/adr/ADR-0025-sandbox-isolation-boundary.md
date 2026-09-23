# ADR-0025 — Agent tools execute in disposable hardened containers, driven by one controller

Status: Accepted
Date: 2026-09-22
Owners: GATE 3 — Sandbox

## Context

`GATE 2` stopped at the tool request: persisted, the run paused, nothing executed
([ADR-0021](ADR-0021-tool-execution-boundary.md)). `GATE 3` is the hands. The question is where an
agent's command, file write or Git commit may run, and what makes "not on the host" a property
rather than an intention.

Three constraints shaped the answer. The primary environment is Windows with Docker Desktop, so the
isolation primitive available everywhere the project runs is a Linux container. The stack already
runs under Compose, with Temporal as its only durable engine. And other projects share the same
container engine on this machine, so anything the sandbox does to the engine must be scoped to what
it created.

A subprocess with a different working directory on the host is not a sandbox, and neither is a
container that shares the host's filesystem, network, credentials or container engine.

## Decision

**Every tool executes inside a container created for the run from the canonical policy, and the
only process that can create one is the sandbox service.**

- The sandbox **service** (`services/sandbox`) is a Temporal worker on the `iacode-sandbox` queue.
  It is the only Compose service given the engine's socket (`/var/run/docker.sock`), because
  creating containers is its job. It runs as an unprivileged user that joins group 0 for that one
  file, drops every capability, sets `no-new-privileges`, publishes no port and has no HTTP surface.
- A **sandbox** is a sibling container created by `iacode_sandbox.backend.container_arguments` —
  the one function that builds a `docker run` — with a read-only root filesystem, size-limited
  in-memory `/workspace` and `/tmp`, `--cap-drop ALL`, `no-new-privileges`, user `10001:10001`,
  `--network none` (or an internal network of its own), memory equal to memory-plus-swap, a CPU and
  a process limit, and **no** volume, bind mount, device, extra group or inherited variable. The
  image's own init (the helper in `--init` mode) is PID 1, so orphans are reaped and nothing inside
  can signal it away.
- The controller never touches a workspace and never runs an agent's input. A tool becomes one JSON
  request to the helper inside the sandbox over `docker exec`; the helper resolves paths, runs
  processes and Git, and answers with JSON. The controller's only process is the Docker client, with
  a fixed argument vector.
- Every container carries labels naming it managed, its owner, its session, its run and its expiry.
  The service lists and removes only containers with **its own** owner label, so neither another
  project nor a second IACode stack nor a test suite sharing the engine can lose a container to it.
- The sandbox image is addressed by the digest of its inputs, so a stale image cannot be used: the
  service computes the digest from the inputs it was built with and refuses a missing or mislabelled
  image rather than substituting one.

## Consequences

**The controller is root-equivalent on the engine's VM.** Whoever controls the sandbox service can
create any container. That is the price of creating containers at all, and it is contained rather
than denied: the service accepts only structured requests through Temporal, builds every container
from the policy with a fixed flag set the suite reads back, derives no mount, image or network from a
request, and is the only holder of the socket — `ComposeDefinitionTests` fails if any other service
mounts it.

**An agent's shell is a shell, inside the sandbox.** `shell.exec` gives a model `/bin/sh` in its
own disposable container. It can do anything that container allows, including `git reset --hard` on
its own workspace; the Git *tools* do not offer destructive verbs, and the shell cannot reach the
network, the host, another run or a credential. The boundary is the container, not a command list.

**Isolation is claimed where it is measured.** The engine suite asks each sandbox what it can see —
its user, its capabilities, its mounts, its interfaces, its environment, its neighbours' files and
processes — and the red team battery attacks the same claims from outside.

## Alternatives considered

**A host subprocess with a changed working directory.** Rejected: it shares the host's filesystem,
network, credentials and user. It is not a sandbox.

**Docker-in-Docker.** A privileged daemon container, with its own image store and storage driver,
to avoid mounting the host engine's socket into the controller. Rejected for this Gate: it trades a
socket held by one unprivileged controller for a privileged container, and doubles the image and
storage machinery on a development machine. It stays available if the threat model changes.

**The controller on the host.** Rejected: it would take the service out of Compose — out of its
healthchecks, its restart policy, its scrape targets and the one verification command — for the
same engine access.

**gVisor or another sandboxed runtime.** Not available on Docker Desktop for Windows. The design
leaves the runtime as one argument of `container_arguments`, so a later Gate can add it.
