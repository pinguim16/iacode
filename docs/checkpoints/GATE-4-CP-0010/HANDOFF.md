# Handoff

Current Gate: GATE-4
Current Status: INTERNAL_GATE_PASS

Last valid commit: ff2814f7d7bf06fa8a99858b958daf3f22197496
Current branch: main

## Objective

Close the owner-authorized internal Gate 4 corrective run and, only after canonical sealing and
published validation, begin Gate 5 separately. The last-valid commit above identifies the sealed
predecessor at entry. STATE.json at the final canonical tag is authoritative for terminal status.

## What was completed

Published corrective source v4 is f367eaaa8fb7d0571c8b25bb7d6a5c936d98edef, tag
iacode-subjects/GATE-4-CP-0010-internal-corrective-v4. Every final assurance fingerprint matches
b88f8504815f569c7c1156ba6018cf384742d39cf80ef9e12c46b162a34af27f.

The nine-check published live-state proof passed (cmd-0307). One full non-fast verifier passed
all 42 stages in 6657.8 seconds, zero retries (cmd-0308), with unchanged shared resources,
removed owned resources/clone and clean transported checkout. Functional acceptance passed all
thirteen mandatory requirements (cmd-0310). All 220 obligations are evidence-bound (cmd-0311).

Fresh formal Green Keeper cycle 1 passed all thirteen mandatory gates (cmd-0321 through cmd-0334).
Completeness passed with 220 complete, 219 mandatory, total coverage/evidence and no partial or
missing item (cmd-0335). Internal Red Team defended all twenty A-T attacks with a VALID baseline
and zero escapes (cmd-0336). The full mirror passed sixteen applicable dimensions, with two
canonically empty-set dimensions kept NOT_APPLICABLE and zero failures (cmd-0342). All 32 sealed
predecessors, 224 documentation links and the actual clean-clone suite passed. All 25 internal
findings are closed against this evidence, without rewriting original observations.

## What was NOT completed

At this pre-seal assembly boundary, canonical finalization, content/evidence commits, sealing,
published-tag validation and final archive regeneration are subsequent actions. Their actual
state must be inspected; never repeat or move an existing seal. Gate 5 is not implemented here.
Independent M2 review, independent Red Team, second-tool validation and milestone approval remain
pending and are not granted by this session.

## Current repository state

Implementing source, tests and Engineering Memory are frozen. Changes after v4 publication are
operational Gate 4 evidence only; source remains the exact verified v4. CP0009 and all predecessor
tags are unchanged. Completed verification/GK/Red Team/mirror sessions must never be resumed.
The finalizer replaces symbolic HEAD with this checkpoint's canonical tag reference; sealing
then binds committed content and appends only its permitted evidence.

## Files changed

FILES.json explicitly owns the complete delta against sealed CP0009. Finish every producer,
declare every output, refresh hashes and validate before finalization. No future-Gate capability
is included in the Gate 4 commit.

## Important decisions

AUTHORIZATION.md and ADR-0037 through ADR-0045 define internal cadence, durable lifecycle,
pre-persistence containment, historical semantics, launch hashes and generated live state.
Provenance is in PROVENANCE.json; training remains denied by default. The frozen retrospective
records the earlier publication boundary; current final assurance is recorded in these reports.
Internal closure is INTERNAL_GATE_PASS, never an independent GATE_PASS.

## Tests executed

Canonical discovery is 825 root and 1804 total counted cases (cmd-0312). The fresh formal root
passed in 4922.773 seconds (cmd-0321); the separate clean-clone root also passed (cmd-0342).
TESTS.json separates physical executions and does not count e2e/runtime categories twice.
Memory validates: 116 active lessons, 113 GUARDED, 118 effective guardrails and zero unresolved
failures. Full published-history scanning is clean (cmd-0315). COUNTS.json owns derived totals.

The fresh 34-step output proof includes clean controls before/after both adverse runs, explicit
refusals, no sandbox objects and prohibited bytes absent from 120 durable payloads examined in
each adverse run. Formal Red Team also defended scanner failure, legacy-object rescanning and
immutable bundle portability/determinism/declaration binding.

## Known failures

V1 and v2 remain failed, and the local broad mixed-epoch run remains failed. V3's genuine PASS
predates the live-state correction and is ineligible for current promotion. Their exact reports,
failed probes and qualifications remain in attempts/, VERIFICATION-ATTEMPT-ARCHIVE.json,
FINDINGS.json and COMMANDS.jsonl. Closing corrective findings never changes those old outcomes.

## Known risks

Original attempt-2 history was lost and is not reconstructed. Cmd-0200 cannot prove launch
pre-images. Two superseded diagnostic directories remain after native cleanup refusal; their
scope is in PUBLISHED-V2-BROAD-DIAGNOSTIC-ABORT.json. No global cleanup is claimed.
Internal assurance does not satisfy the independent M2 boundary. See RISKS.md.

## Do not repeat

Never edit sealed subjects, move tags, hide red attempts, narrow a mandatory set, splice green
fragments, change source after assurance, overlap producers and hashing, bypass refused cleanup,
assert independence or infer Gate 6 authority. A genuine red/stale control prevents advancement.

## Required next action

Finish the pre-seal assembly slice and actual validation. If not yet finalized, finalize
INTERNAL_GATE_PASS with the canonical reference. If not yet sealed, commit Gate 4 alone and run
the canonical sealer. Then publish and validate fresh transport and the final review archive.
If these actions already succeeded, inspect their evidence rather than repeating them.

## Exact continuation sequence

Complete pre-seal readiness, finalize, commit, seal, publish, validate the canonical transported
tag and regenerate/verify the canonical archive from its declared immutable content commit.
Do not append to the sealed subject. Only after those conditions hold, create Gate 5's own
checkpoint, anchor this predecessor, run lesson preflight and derive its canonical requirements
before baseline/plan/implementation. Gate 6 is not authorized.

## Validation commands

Before finalization, record and await:
`python docs/checkpoints/GATE-4-CP-0010/audit-harness/declare_inventory.py`, then
`python docs/checkpoints/GATE-4-CP-0010/audit-harness/run_checkpoint_validation.py`.
Canonical finalization:
`python scripts/development-ledger/finalize_checkpoint.py --status INTERNAL_GATE_PASS --commit-ref refs/tags/iacode-checkpoints/GATE-4-CP-0010`.
After committing, run `python scripts/development-ledger/seal_checkpoint.py`.
After sealing, run `python scripts/development-ledger/validate_checkpoint.py`,
`python scripts/development-ledger/verify_integrity.py` and
`python scripts/development-ledger/remote_sync.py --tag iacode-checkpoints/GATE-4-CP-0010`.
Fresh published detached validation and exact review-declaration reconstruction are also required.

## Stop conditions

Stop on unexpected Git divergence, a real external blocker, red mandatory control, stale
assurance, reconstruction mismatch, secret finding, false independence or premature Gate work.
