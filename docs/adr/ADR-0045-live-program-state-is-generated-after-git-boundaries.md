# ADR-0045 — Live program state is generated after Git boundaries

Status: Accepted
Date: 2026-10-16
Owners: GATE 4 — Resumability and delivery assurance

## Context

The program-state entry point fails for the latest checkpoint without STEPS.json. The tracked
observation names a historical checkpoint/SHA and its schema cannot describe INTERNAL_GATE_PASS.
A file that stores the exact current HEAD cannot remain current after committing itself.

## Decision

Current canonical policy produces schema 1.1 observations in ignored var/program-state.json.
The latest checkpoint, truthful local steps, exact local/remote Git and canonical status remain
authoritative. Explicit --write regenerates the observation; validation never silently reconciles
it. Missing steps, wrong identity, stale state, unsupported versions and unsafe output targets fail.
Checkpoint field types and declared branch/currentCommit must agree with their actual sources;
coercion may not turn invalid metadata into a schema-valid observation.

The old tracked schema 1.0 observation remains unchanged and is labelled historical in adjacent
documentation. Subjects without the new policy keep legacy storage/status semantics. Portable
schema version constraints are also enforced in the program-state loader, not inferred from the
standard-library checker's unsupported combinators. No SHA is replaced with a symbolic assertion.

## Consequences

Real CLI and Git controls must prove generation does not dirty the tree, detects later local and
remote movement, supports internal closure honestly and refuses contradictory or redirected state.
Current checkpoint steps are explicit authored evidence, never invented by the pointer producer.
All source changes require a new immutable full execution; the active v3 subject stays untouched
and cannot approve these later changes. No mandatory gate or requirement is removed.
