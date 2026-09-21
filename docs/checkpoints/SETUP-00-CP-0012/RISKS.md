# Risks

## R1 — Registering the audit gives this delivery work to close, which can mask the repair

Severity: `HIGH`. `SETUP-00-CP-0011` warned of this explicitly: registering the audit makes the
corrective delivery's mirror satisfiable by giving it a finding and a battery, so a repair that only
worked when there *is* work would still look green here. Mitigation: the repair is proven where
there is nothing to close. `MIRROR-SEMANTICS-VALIDATION.json` executes the tool over a delivery with
no registered audit at all, and `GATE0-TRANSITION-SIMULATION.json` delivers the first checkpoint of
a later Gate to `READY_FOR_REVIEW`. Neither has anything to correct.

## R2 — `NOT_APPLICABLE` is a new way to pass without auditing

Severity: `HIGH`. Before this delivery the state was unreachable; now it is reachable, and a
delivery could reach for it instead of satisfying a dimension. Mitigation, in four layers: the
outcome cannot be constructed without a justification; an unjustified or non-empty record is written
down as `FAIL` by the auditor; the report schema admits the fields only from version `1.1.0`; and
checkpoint validation re-derives the registry-bound dimensions from the canonical sources and
refuses a declaration that contradicts them. Five adversarial scenarios attack exactly this.

## R3 — The Gate transition is proven against a synthetic specification

Severity: `MEDIUM`. The next Gate's checklist in the transition fixture is written by the fixture and
says nothing about what that Gate would build, so the simulation proves the state machine and not the
content of any later Gate. Mitigation: this is stated in the simulation's own report, in the lesson's
residual-limit note and here. The first real Gate 0 delivery still has to author its specification,
which `SETUP-00-CP-0011` recorded as risk `R6` of that audit and which remains open.

## R4 — The parser change touches how sealed audits are read

Severity: `MEDIUM`. The expected requirement set of the sealed `SETUP-00-CP-0008` and
`SETUP-00-CP-0010` checkpoints is derived from these parsers, so a change in what they return would
invalidate sealed history. Mitigation: the two earlier parses are held fixed by explicit cases that
assert the exact identifiers and battery membership, the historical-compatibility dimension
validates every sealed checkpoint from a detached checkout of its own tag, and a table whose first
column is not an attack identifier is not read as a battery.

## R5 — The internal Red Team of the promotion fixture is still modelled

Severity: `LOW`. The simulation now executes the mirror audit but continues to model the internal Red
Team report of the fixture delivery, because executing that battery would require building a fixture
inside a fixture. Mitigation: the simulation declares which artifact was executed and which was
modelled, in `artifactProvenance` and in the artifact's own `source` field, and it never claims the
battery of the fixture checkpoint was run. The condition that would make this a finding is a
simulation that reports the battery as passing.

## R6 — Twelve of this delivery's mandatory attacks re-execute an existing mutation

Severity: `LOW`. The sealed `SETUP-00-CP-0011` battery numbers its scenarios in its own vocabulary,
and most of its mandatory rows name failure classes this battery already attacks. Each is executed
again, in its own fixture, under the identifier the sealed report uses, and the alias records which
mutation it repeats; two rows the earlier reports did not isolate are written out in full.
Mitigation: the aliasing is declared in the battery's own origin field rather than presented as
twelve independent discoveries.

## R7 — The verdict of this delivery is internal

Severity: `HIGH`, and structural rather than specific to this change. Everything recorded here was
produced by the implementing run on the same tooling in the same session. `READY_FOR_REVIEW` is the
only status this run may close at, the internal mirror and the internal Red Team are declared as
internal quality assurance, and no artifact of this delivery is recorded as independent validation.
Mitigation: the next action is a fresh-session independent `M0` audit, which authors its own
checkpoint about this sealed subject.

## R8 — Gate 0 remains blocked and unspecified

Severity: `MEDIUM`. `M0` has not passed, so `GATE 0 — FOUNDATION` stays blocked, and
`.iacode/policies/canonical-requirements.json` still declares no requirements for it. This is not a
defect of `M0` and no Gate 0 work exists in this change set; it is the first deliverable of that
Gate. Mitigation: recorded here and in `NEXT.md` so the next Gate does not discover it after
starting.

## R9 — The finalizer rewrites two checkpoint files with the platform's line endings

Severity: `LOW`, and observed rather than introduced by this delivery.
`finalize_checkpoint.py` writes `STATUS.md` and `HANDOFF.md` with `write_text(encoding="utf-8")`
and no `newline="\n"`, while every other writer in the tooling passes it. On Windows those two
files therefore come back with CRLF in the working tree. Nothing downstream is wrong: `.gitattributes`
normalizes them on commit, `canonical_hash_path` normalizes line endings before hashing, and the
sealed content is LF, which is why no sealed checkpoint has ever failed for it. The only symptom is
Git's own conversion warning at `git add`.

It is recorded here rather than repaired, because repairing it means changing the delivery-assurance
scope and re-running every gate of a delivery whose finding is elsewhere, and because the condition
that would make it a finding is precise: a working tree whose content differs from the sealed
content in a way a hash would notice. Today it does not. The next delivery that touches the
finalizer should pass `newline="\n"` at both call sites.
