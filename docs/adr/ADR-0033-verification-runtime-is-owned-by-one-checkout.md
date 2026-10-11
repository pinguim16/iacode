# ADR-0033 — A verification runtime is owned by one checkout

Status: Accepted
Date: 2026-10-11
Owners: GATE 4 — Quality Engine

## Context

The repository's Compose file deliberately defaults to the developer project name `iacode`. A
transport clone copied the same local environment and therefore selected the same container names,
image tags, network, volumes and published ports as the source checkout. Its supposed clean run
could reuse or replace runtime state created by another checkout. The independent Gate 4 audit
observed the consequence: the single full verification failed `infra` and `smoke`, while exact
isolated repetitions passed after the shared stack had converged.

Compose health establishes service readiness, not that Prometheus has already completed a scrape
of the newly created service instances. The live infrastructure suite sampled target health
immediately, while the smoke path carried a separate bounded wait. That duplication made the
result depend on which observer ran after which startup event.

## Decision

The canonical verification command derives a Compose project name from the resolved checkout,
overriding local `COMPOSE_PROJECT_NAME` for every child stage. It asks Docker to allocate every
published host port, freezes that environment for the complete battery, removes only the derived
verification project before execution, and removes that same project and its volumes after
execution. The normal developer stack remains separate and untouched.

The live stack stage builds every service image before it is exercised. Any gate that invokes an
image resolves the image belonging to the frozen project rather than a literal default-project
tag.

Prometheus target checks share one observer. Its deadline is derived from the versioned scrape
interval and it only polls target state; it never restarts a service or retries the action whose
result is being judged. A failing verification stage remains a failure and retains its diagnostic
tail in the machine-readable report.

## Consequences

Two checkouts can execute verification without sharing containers, networks, volumes, image tags
or host ports. A clean Git clone now receives clean runtime state even when a developer stack is
already running. The full run costs a complete live-image build, with normal Docker layer caching,
and cleanup failure makes the verification fail closed.

An interrupted process can leave an isolated project behind, but the next run cleans the same
derived identity before starting. The ordinary `stack.py` commands still operate the developer's
configured project; isolation belongs to `verify.py`, not to every operational command.

## Alternatives considered

Retrying `infra` or `smoke` was rejected because it would replace the audit's red evidence with a
later green sample. Increasing timeouts without relating them to the scrape policy was rejected as
an arbitrary delay. Reordering the stages was rejected because it would hide the dependency rather
than remove it. Stopping the shared developer stack was rejected because a clean-clone check must
not take ownership of another checkout's runtime or data.
