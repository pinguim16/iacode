# ADR-0044 — Process recorders bind launch inputs

Status: Accepted
Date: 2026-10-16
Owners: GATE 4 — Delivery assurance

## Context

The command recorder and Green Keeper constructed declared file digests after their subprocesses
finished. A real child that rewrote its own script and data therefore received post-image input
identity. An interrupted diagnostic also changed helper source while running; its old record cannot
prove launch bytes. Separately, editing tests and the registry during a local broad suite produced
five correct mixed-epoch refusals. None of these results is final validation evidence.

## Decision

Process-owning recorders capture declared input paths and content hashes immediately before launch
and pass that snapshot explicitly to the metadata builder. Actual process results remain unchanged.
The builder itself does not execute commands; callers recording in-process transformation phases
remain responsible for their declared boundary. Finalizer metadata records describe its validated
post-transformation phase, and sealing still validates committed content before granting a seal.

Input pre-images identify the launch boundary, not an assertion that the final working tree passed.
Complete assurance runs against a frozen immutable subject. Source and memory are not edited during
an authoritative invocation. Final closure still requires every full mandatory control.

## Consequences

Real self-rewriting and stable-child controls cover both process recorders. Historical rows, schemas
and seals are not rewritten. Cmd-0200 remains non-successful and is explicitly disqualified as
launch-content evidence; no missing original digest is fabricated. The red local broad run remains
red, and selected diagnostics cannot promote it.
