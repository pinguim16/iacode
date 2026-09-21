# Plan — final fresh-session independent M0 audit of SETUP-00-CP-0010

## Role and boundary

This run audits. It does not implement, repair or improve product code, and it does not start
Gate 0. The subject is `SETUP-00-CP-0010` at its canonical tag; it is never modified, re-tagged or
re-sealed. The verdict is recorded here, in the audit checkpoint, which is the architecture the
finding `CP9-F-001` produced.

## Independence, stated without inflation

| Property | Value |
|---|---|
| Mechanism | `FRESH_SESSION_INDEPENDENT_AUDIT` |
| Same tool as the implementer | yes |
| Same provider as the implementer | yes |
| Same model as the implementer | yes |
| Session independence | new session, no memory of the run that produced the subject |
| Cross-tool validation | `NOT_AVAILABLE` |

No part of this audit is cross-tool validation and none of it is recorded as such.

## Order of work

1. Read the canonical documents, the sealed `SETUP-00-CP-0009` audit and the complete subject.
2. Establish the baseline and compare the observed Git state with the subject `STATE.json`.
3. Build the final audit matrix, every row `NOT_STARTED`, before any substantive execution. Rows
   that describe repository content are derived from the repository; rows that describe audit
   obligations come from the audit mandate.
4. Execute, recording each result as an append-only record the matrix is rebuilt from:
   - the five `CP-0009` findings, each against the implementation rather than the claim;
   - every declared requirement of the subject, against an independently derived expected set and
     an independent resolution of every evidence reference;
   - every regression and negative test the closure record names, executed by identifier;
   - the positive promotion path and the successor durability path, re-executed;
   - the whole suite, in the working repository and in a clean clone detached at the subject tag;
   - every canonical mandatory validator, in both environments;
   - the Green Keeper, the completeness audit, the engineering memory and the preflight, recomputed;
   - the integrity chain, re-derived from Git without the product helper;
   - the affected adversarial scenarios, including an adversarial battery written for this audit
     over a mandatory null-mutation control.
5. Decide the verdict from the matrix, not from an impression.
6. If the audit passes: anchor the subject, write the attestation, run this checkpoint's own gates
   over the content that will be sealed, seal, and confirm the derived milestone verdict from a
   clean detached checkout.

## Stop conditions

Stop on an unexpected Git divergence, on any need to modify a sealed checkpoint or move a historical
tag, on a secret exposure, and on any request to begin Gate 0. A failing audit does not repair
product code: it records one consolidated finding set and closes at `REWORK_REQUIRED`.

## What a PASS requires

Five findings closed, the positive promotion path reachable, successor durability green, the suite
green, the clean clone green, the Green Keeper and the completeness audit green, the engineering
memory valid with no unresolved guardrail failure, the preflight fresh, history integrity intact,
every affected adversarial scenario defended with the positive control accepted, every mandatory
matrix row executed with evidence, and no blocker. Anything less is `REWORK_REQUIRED`.
