# ADR-0029 — Quality plans execute through stack-specific content-addressed sandboxes

Status: Accepted
Date: 2026-10-09
Owners: GATE 4 — Quality Engine

## Context

Gate 4 evaluates untrusted project code. A quality check is therefore another form of tool
execution, not a trusted controller operation. Running a compiler, package script, test suite or
migration check from the evaluator would bypass the Gate 3 boundary and expose the evaluator's
filesystem, environment and network. One mutable all-purpose image would also let a changed
toolchain evaluate a frozen plan without changing its identity.

## Decision

Every quality command is sent as a structured `shell.exec` request to the Gate 3 sandbox task
queue. The canonical sandbox policy maps Python, Node/TypeScript/Angular and Maven/Gradle checks to
three stack-specific image profiles. Those policies expose only `shell.exec`, use `network=none`,
carry fixed resource bounds and accept no caller-provided image, mount, network or limit.

Each image reference is derived from every file that can affect the image. A context may declare
additional repository-relative inputs in `image-inputs.json`; the fingerprint loader refuses an
absolute, escaping or missing input. This makes the Node dependency lock part of the image address
even though it lives beside the frontend source. A missing image or a fingerprint mismatch remains
a recorded failure; there is no mutable fallback tag.

Dependency downloads happen only while the pinned image is built. Runtime policies have no
network. Node installs from the prebuilt npm cache and its lockfile; Maven resolves from the
read-only prebuilt local repository; Gradle and Python use the tools already present in the image.

## Consequences

Toolchain images are larger and take longer to build, particularly Angular and Java. In return, a
quality run cannot reach the host or internet, and a lockfile or toolchain change produces a new
image address before a project command can execute. Supporting another ecosystem means adding an
image profile, a bounded policy and a runner mapping; it does not add an execution branch to the
evaluator.

The sandbox workspace is writable because compilers and test tools produce build outputs, but it
is a size-limited in-memory copy of an authorised snapshot. The image root remains read-only and
the container remains unprivileged, capability-free and disposable.

## Alternatives considered

Running quality commands in the evaluator was rejected because it would make orchestration code an
execution boundary and give project scripts its identity. Reusing the developer image was rejected
because it lacks the required toolchains and would turn tool installation into a networked runtime
step. Mounting host dependency caches was rejected because it would expose a host path and make
results depend on mutable state outside the plan.
