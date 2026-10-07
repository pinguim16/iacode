# Decisions

## D-01 — The verdict mechanism is fresh-session independence

This Codex session did not implement `GATE-3-CP-0003`; it audits that sealed subject under
`FRESH_SESSION_INDEPENDENT_AUDIT`. The mechanism may author
`MILESTONE_INDEPENDENT_AUDIT_PASS`, never `MILESTONE_EXTERNAL_PASS`.

## D-02 — The audit reuses the frozen M1 battery and adds explicit closure probes

The `GATE-3-CP-0002` audit harness remains the behavioural baseline. Its checkpoint and subject
identities are generalised for `GATE-3-CP-0004`, and the three prior findings receive explicit
independent probes. This changes audit evidence only; product code is outside the auditor's role.

## D-03 — Published history is the verification source

Checks over sealed evidence use Git transport clones of the authorised remote. Worktrees of the
local object store may be useful diagnostics, but cannot establish published reproducibility.

## D-04 — A reproduced Critical dependency finding ends substantive audit execution

The full verification and an immediate independent repetition both found two Critical and four High
npm advisories. The frozen stop condition therefore decides `REWORK_REQUIRED`. The auditor does not
update packages, run the later dedicated live/Red Team/clean-clone criteria, or reinterpret those
criteria as passed. They remain `UNVERIFIED` and the corrective work returns to an implementing run.
