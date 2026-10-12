# Plan

## Scope

Correct only Gate 4 publication and Development Ledger evidence portability. Do not alter CP0006,
move its tag, rewrite history, claim independent validation, grant `GATE_PASS`, or begin Gate 5.

## Derived requirement set

The mandatory preflight selected 95 lesson requirements. Canonical derivation produced 201 total
requirements: 105 Gate 4 specification rows, 95 lesson-derived rows and the registered publication
finding `G4-F-003`.

## Implementation sequence

1. Record the `LSN-0040` recurrence as an unresolved `GUARDRAIL_FAILURE` before repair.
2. Introduce a forward-only checkpoint schema revision whose command-input rule distinguishes
   repository-carried inputs from generated local inputs. Preserve validation compatibility for
   sealed predecessors whose ignored inputs were content-bound.
3. Centralize transport classification so recorder auto-detection, caller-supplied inputs, common
   record construction and checkpoint validation cannot disagree. Git metadata and paths outside
   the repository are never repository inputs.
4. Add negative and positive regressions covering `.git`, ignored runtime output, explicit inputs,
   direct records, legacy sealed evidence and validation from a published transport clone.
5. Replace the corrective checkpoint's bundle dependency with repository-carried validation reports
   and digests; keep generated ZIP archives out of the ledger input set.
6. Update the protocol, tool documentation and an ADR; resolve and re-guard `LSN-0040` only after
   the automated control passes.
7. Execute focused tests, the full mandatory verification, Green Keeper, completeness, internal
   Red Team A–T, internal milestone mirror, deterministic bundle checks and clean/published clone
   validation. Every red attempt remains in the ledger and rework log.
8. Declare every changed path, finalize at `READY_FOR_REVIEW`, commit, seal, anchor CP0006, publish
   `main` and the new immutable CP0007 tag, then validate the published tag from a fresh remote
   transport clone.

## Stop condition

Only a real external blocker may stop the run. Any repository-correctable red result returns to
implementation and repeats the full assurance cycle.
