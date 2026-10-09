# ADR-0031 — Project profiles select closed policy-owned quality runners

Status: Accepted
Date: 2026-10-09
Owners: GATE 4 — Quality Engine

## Context

The Quality Engine must evaluate unrelated Python, Node, TypeScript, Angular, Maven and Gradle
projects without repository-specific branches. Letting a project supply arbitrary commands or an
image would make onboarding flexible by moving the execution and verdict boundary into untrusted
input. Treating every project as one stack would instead invent support and permit false PASS when
the manifests are ambiguous.

## Decision

Bounded manifest inspection produces a versioned project profile. Detection reads regular files
only, follows no link outside the snapshot, ignores generated or vendor directories and records
every detected stack, manifest, confidence and ambiguity. A supported profile must match exactly
one profile in `.iacode/policies/quality-policy.json`; unknown and ambiguous combinations stop
planning.

The canonical policy maps that profile to a closed ordered runner set. Each runner owns its argument
vector, check kind, timeout ceiling and required evidence kinds. Project configuration may add only
a runner the profile already declares optional, lower a timeout or raise a coverage threshold. It
cannot select an image, mount, network, resource bound, hidden command, result, evidence or verdict.
The frozen plan content-addresses the snapshot, profile, policy and ordered checks before execution.

Stack-specific sandbox image profiles are content-addressed separately. A missing or stale image is
a recorded failure; another image is never substituted. This keeps profile detection independent
of infrastructure while preserving the sandbox as the sole executor.

## Consequences

Adding a stack requires a detector, a policy profile, registered runners, a pinned sandbox image and
passing/failing fixtures. A project with a novel mixed stack is unsupported until that complete set
exists. The initial runners intentionally prefer reproducible offline checks over package download,
so lockfiles and prebuilt toolchains decide what can run.

The same source path onboards every supported project, and malicious manifest text remains data.
The tradeoff is deliberate rigidity: a useful command not yet declared by policy cannot be run by
the Quality Engine merely because a repository asks for it.

## Alternatives considered

Executing scripts from a project manifest was rejected because project input would select the
command and could bypass the closed runner registry. Choosing an image from request input was
rejected because it would bypass the sandbox policy. Guessing the closest profile was rejected
because ambiguity would become an unexplained denominator change. Repository-name-specific
configuration was rejected because it would not be a project-agnostic engine.
