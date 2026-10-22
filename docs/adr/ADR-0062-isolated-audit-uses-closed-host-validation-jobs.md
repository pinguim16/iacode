# ADR-0062 — Isolated audit uses closed host validation jobs

Status: Accepted
Date: 2026-10-21
Owners: GATE 7 — M2 audit correction

## Context

The elevated restricted Windows token can launch processes, but cannot access the
Docker Desktop engine pipe. The owner approved a temporary bridge for canonical
validation runners only, not a general CLI sandbox bypass. The owner also requires
removal of task-owned disposable resources without disturbing other applications.

## Decision

Keep the auditor in workspace-write with invocation-local elevated settings. A
host operator freezes a private source snapshot, executable identities, closed job
definitions, arguments and environment before exposing a loopback job service.
The request names one predeclared job only. It cannot supply code, command, path,
environment, Docker API operation or cleanup target. An ephemeral capability is
delivered in the auditor child environment, never in Git or a command argument.
No service is enabled until a real restricted-token probe proves local transport
and refuses writes to the host-owned private directory.

Each job is serialized and idempotent, rechecks frozen inputs, retains safe producer
bytes or a neutral refusal inventory before cleanup, and reports producer and
cleanup outcomes separately. Invalid or unsafe artifacts are not served. Timeouts
terminate only the job's exact native Windows Job Object. The service does not
execute auditor-modified sources. A later independent auditor still performs its
own review, Red Team and verdict; the bridge is transport, not an attestation.

Trusted operator inputs still require a filesystem boundary: refuse parent components and
redirected ancestors, then verify physical containment before inspecting or reading a source
or report. Lexical ancestry alone is insufficient. Available output is captured to its observed
finite end before cleanup; a timed-out writer must not turn capture into an unbounded moving-EOF
loop. Preserve hardlink refusal and exact raw-byte identities for the observed prefix.

Use a dedicated task-owned docker-container Buildx builder, with child-local builder
configuration and selection, when actual canonical build capability is proved.
Do not change the default builder or prune shared caches. Record the before
inventory and exact creation/ownership receipts. After preserving evidence, remove
only confirmed owned resources, including the private builder/cache, generated
images not shared by preexisting consumers, and disposable source/config trees.
Ambiguous ownership or a preexisting reference means preservation and an explicit
remaining-resource report, never a global prune or forced shared-image deletion.

## Verification

Required: real restricted transport and write-refusal probes; allowlist/schema,
source-tamper, link, replay, output/privacy, timeout and cleanup adverse cases;
actual canonical Docker build/run/bind proof; before/after unrelated application
identity/state checks and exact owned-resource absence. No completion is claimed
by this decision record. Canonical quality and milestone controls remain mandatory.

## Alternatives and consequences

Giving the whole auditor unrestricted access, changing pipe ACLs globally, or
exposing arbitrary Docker commands would enlarge authority and was rejected.
Reusing mutable source would allow the auditor to cross the host trust boundary.
Reusing the shared default build cache would prevent precise cleanup. The extra
adapter requires its own adversarial tests and may fail closed; such failure is
not a product or independent milestone PASS.

References: [Docker container driver](https://docs.docker.com/build/builders/drivers/docker-container/),
[builder removal and cache](https://docs.docker.com/build/builders/manage/).
