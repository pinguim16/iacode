# ADR-0026 — A workspace belongs to one run, lives in memory, and is recovered from the store

Status: Accepted
Date: 2026-09-22
Owners: GATE 3 — Sandbox

## Context

An agent that edits code needs a place to edit it. A team — planner, developer, reviewer — needs the
same place across its stages, so the reviewer sees what the developer changed. Two runs must never
share it, the host's own working tree must never be it, and a crash of the service must not strand
it or forget it.

Three questions follow: what a workspace is made of, how long it lives, and what is true about it
after the service restarts.

## Decision

**One run, one session, one container, one workspace.**

- A session is created lazily, by the run's first tool request, and at most one session per run is
  active at a time. The database states it with a partial unique index on `sandbox_sessions`, so a
  race between two requests of one run produces one session rather than two.
- Every stage of the run works in that session's workspace. What each stage may do there was decided
  per request, from its own policy, before the workspace is touched; a reviewer's read-only policy
  therefore reads the developer's changes and cannot alter them.
- The workspace is a size-limited `tmpfs` mounted at `/workspace` inside the container. The limit is
  enforced by the kernel, not by a check, and nothing of it exists on the host's disk.
- Its initial content is either empty — a fresh Git repository — or an **authorised snapshot**: a tar
  archive of a directory an operator chose, stored in the Foundation's bucket with a row in
  `artifacts` of kind `sandbox.workspace-snapshot` and its SHA-256. A run names the artifact, never a
  path. The service checks the digest, the helper refuses links, devices, absolute names and escapes
  before extracting with the standard library's `data` filter, and a repository is initialised over
  the result so the agent's changes are a diff.
- A session ends with its run: the workflow's release activity removes the container and records
  `STOPPED`. A session also carries an expiry; the sweeper expires what outlives it, a bounded number
  at a time, and never a session that is running a tool.
- The store is the truth; the service's memory is a cache. At start the service reconciles the
  store with the containers the engine reports for its own owner label: a session whose container is
  gone is `FAILED` (its workspace went with it), a session caught mid-tool is stopped and returned to
  `READY`, and a labelled container no active session owns is removed.

## Consequences

**A workspace does not survive its container.** Keeping it in memory buys a kernel-enforced size
limit and no host disk, and costs persistence across a container restart. A service restart does
not restart the containers, so sessions survive it; a crashed container does not, and its session
is honestly `FAILED`.

**The workspace's memory counts against the container's memory limit.** The policy validator refuses
a resource profile whose workspace and `/tmp` do not leave room inside `memoryMb`.

**The development tree is never an agent's workspace.** A test or a scenario that wants an agent to
work on IACode's own code snapshots it first; the copy is what the agent changes.

## Alternatives considered

**A named Docker volume per workspace.** Rejected: volumes have no size limit on the default driver,
outlive their container by default, and are one more resource to sweep.

**A host directory bind-mounted into the container.** Rejected: it puts the host's disk behind the
sandbox's path resolver and every symlink an agent can create, and it is exactly the kind of mount
the Gate forbids.

**One workspace per stage.** Rejected: a reviewer that cannot see the developer's change cannot
review it, and copying a workspace between stages is a second provisioning path to secure.
