# Decisions

## D-001 — Preserve the sealed audit and extend the canonical parser

The predecessor is immutable. Its finding is rendered as a backticked identifier followed by an
explicit severity under `## Blocking finding`, rather than as a level-three finding heading. The
canonical parser will accept that bounded single-finding rendering, with regression coverage for
the exact sealed report and for refusal of unstructured text. This is a compatibility correction,
not a transcription of the finding into this delivery.

## D-002 — Correct the preflight record's declared memory input

`cmd-0002` executed the canonical lesson preflight successfully, but its manually supplied extra
input named nonexistent `LESSONS.json` instead of the `lessons.jsonl` the command actually read.
The record's input path and digest were corrected to the committed pre-command bytes; command,
arguments, time, outcome, and repository state were not changed. The original metadata defect was
observable in checkpoint validation and is not represented as a command failure.

## D-003 — Reject unsafe serialized evidence before every durable operation

The evaluator scans the exact UTF-8 bytes that would be committed before object lookup, filesystem
inspection, write, or metadata construction. A scanner failure is treated as unsafe. The activity
boundary converts only this containment failure into a sanitized `ERROR` result with no evidence or
findings, and the resulting policy verdict is `FAIL`; unrelated implementation faults still
propagate. Existing objects are rescanned when resolved so legacy unsafe content cannot bypass the
current boundary.

## D-004 — Wait for reaping, not only signaling, in the sandbox process sweep

The final Green Keeper exposed an intermittent PID-cgroup exhaustion after a detached fork bomb.
The helper previously returned when only zombies remained, even though those PIDs still occupied
the cgroup. The bounded sweep now continues observing `/proc` until killed descendants are reaped,
while sending `SIGKILL` only to live targets. A deterministic unit test guards this behavior.

## D-005 — Keep same-session assurance separate from independent promotion

The Delivery Completeness Validator, Green Keeper, internal Red Team, milestone mirror, and bundle
validation in this checkpoint are implementation-session evidence. They may justify
`READY_FOR_REVIEW`, but they cannot populate `independentReview`, `secondToolValidation`, or the Gate
verdict. Gate 4 therefore remains pending until a later fresh-session review examines the sealed
checkpoint and records its own attestation.

## D-006 — Bundle canonical review context separately from the changeset

The deterministic review bundle must contain the complete checkpoint, the truthful Git changeset,
and the tracked migrations, schemas, and policies needed to interpret that changeset. Unchanged
canonical context is included as review material without being represented as modified. The
failed pre-fix bundle and its evidence-reference recurrence remain in the command ledger; the
final bundle must pass category, manifest, hash, path-safety, uniqueness, and secret checks.

## D-007 — Freeze bytes only after a holistic metadata audit

A repeated full Green Keeper cycle is too expensive to use as the first detector of correlated
checkpoint metadata defects. Before cycle 7, the run therefore renewed lesson preflight and the
216-row requirement set, verified the 25-anchor chain, executed 117 focused inventory, evidence,
chronology, freshness, assurance, and promotion tests, re-audited completeness and counts, checked
the diff, refreshed only already-declared hashes, and obtained `CHECKPOINT_VALID` at `cmd-0182`.
Only then were the content bytes frozen for the all-green cycle. This does not narrow or replace
any mandatory gate; it prevents a known metadata defect from wasting another complete run.
