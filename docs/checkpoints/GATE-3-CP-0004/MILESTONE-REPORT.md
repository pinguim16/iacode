# Milestone Report — M1, IACode V0 foundation

`M1` groups `GATE 0 — FOUNDATION`, `GATE 1 — MODEL GATEWAY`, `GATE 2 — AGENT RUNTIME` and
`GATE 3 — SANDBOX + TOOL EXECUTION`. This fresh-session audit judged the sealed corrective delivery
`GATE-3-CP-0003` and the accumulated milestone; it did not implement product corrections.

## Verdict

**`REWORK_REQUIRED` — `M1` is not passed.** The complete verification passed 31 of 32 stages and
the dependency advisory gate independently reproduced two Critical and four High npm findings.
`M1-F-004` is open. The frozen stop condition ended substantive audit execution, so the remaining
dedicated live, Red Team and clean-clone repetitions are unverified in this checkpoint. `GATE 4`
does not start.

The internal milestone mirror reports a single deliberate failure, the security quality dimension
for `M1-F-004`; its other applicable probes pass, including final Green Keeper freshness,
completeness, derived counts, integrity, historical compatibility and documentation resolution.

## What held

- All seven sealed M1 checkpoint subjects validate detached at their canonical tags, both locally
  and from a transport clone of the authorised remote.
- All 70 commits named by sealed evidence are reachable from published references; the preserved
  history repair from `M1-F-003` holds.
- The full verification passed every build, test, runtime, stack, backup, restart, failure and
  fresh-install stage other than the dependency advisory gate.
- The embedded configured provider, Agent Runtime, Sandbox, forged-result, cancellation, timeout
  and recovery paths all passed.
- `R-G3-001` remains an accepted local architectural risk bounded by ten passing controls; no
  untrusted request controls an engine operation.
- The history secret scan was clean under the repository allowlist, and `trainingAllowed` remains
  `false` by default.

## What blocks the milestone

The frontend pins and lock graph are currently covered by six blocking npm advisories: two Critical
and four High. This violates the milestone security gate and frozen AM-17 criterion. The next
allowed work is a corrective `GATE-3` delivery that updates and validates the dependency graph,
followed by a new independent M1 audit. The project-agnostic, multi-project and model-federation
requirements in the owner's addendum remain authorised future-program requirements, but cannot be
started in `GATE 4` while `M1` is unpassed.
