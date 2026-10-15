# Retrospective — GATE 4 / GATE-4-CP-0010

## What went well

A behavioral workflow test reproduced a cancellation defect before production correction. The
null/positive path, unrelated failure and both persistence arrival orders were tested; actual
PostgreSQL concurrency and live sandbox cleanup passed. Evidence: CP0010 commands and cancellation
reports. Sealed CP0009 remained immutable and owner authorization was recorded explicitly.

## What failed

Cmd-0005 confirmed a durable cancellation race. Cmd-0009 caught a noncanonical new verdict fixture.
Cmd-0014 caught overlong new regression source lines. All red attempts remain in the ledger.
Cmd-0022 and cmd-0029 caught metadata drift and an evidence/policy producer still changing content
after the inventory boundary. The unsealed-only synchronizer and a quiescent validation sequence
passed as cmd-0024 and cmd-0034; no terminal evidence was relaxed or rewritten.
Cmd-0007/0008 launched no process because the command recorder refused unreplayable filename tokens;
the intended suites subsequently ran with replayable globs.

## What repeated

LSN-0098/GRD-0099 recurred beyond the old flag/watcher boundary. It was reopened and escalated as a
GUARDRAIL_FAILURE, not repaired silently. The new persistence barrier and complete workflow tests
close the gap; actual SQL and live cleanup proof are recorded as cmd-0016.
LSN-0011/GRD-0006 also recurred during in-progress metadata preparation and was explicitly reopened.
Its correction derives aggregates and commit semantics together, requires evidence producers to
finish first and retains the validator's strict hash and preflight freshness checks.

## What was learned

Durable reads need write-boundary invariants. Cancellation and immutable verdict commitment require
a single serialization point. Internal closure and independent milestone approval are distinct
claims, and live contracts must express one unambiguous cadence.

## What should become a guardrail

Workflow completion/result/verdict cancellation races and unrelated-error propagation are executable
regressions in GRD-0099. Canonical fixture positive paths, honest internal verdicts and unchanged
mandatory lint are registered in GRD-0104 through GRD-0106. None substitutes for independent audit.

## New lessons

LSN-0103 records canonical fixture digests; LSN-0104 records cadence consistency and truthful
independence; LSN-0105 records source-quality coverage for new tests. Their machine records own
status, evidence and provenance rather than duplicated retrospective counts.

## Updated lessons

LSN-0098 retains its earlier resolved recurrence and records the new recurrence and corrective proof.
LSN-0011 retains all earlier failures and adds the quiescent metadata synchronization proof.

## Retired lessons

None.
