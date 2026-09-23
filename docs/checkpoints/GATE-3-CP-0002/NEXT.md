# Next

## Required next action

`M1` is **not passed**: this audit closed at `REWORK_REQUIRED` on finding `M1-F-003` (HIGH), with
`M1-F-001` and `M1-F-002` (MEDIUM). By the owner's rule for this execution, **`GATE 4` does not
start**. What follows needs the owner's authorization:

1. **The corrective delivery `GATE-3-CP-0003`** — an implementing run, not this audit — which:
   - anchors this sealed audit checkpoint in `.iacode/anchors/checkpoint-chain.json`;
   - registers this audit in `.iacode/policies/audit-registry.json`: `auditId` `M1-CP-0002`,
     `milestone` `M1`, `gate` `GATE-3`, `auditor` the fresh session of this run,
     `auditCheckpoint` `GATE-3-CP-0002`, `subjectCheckpoint` `GATE-3-CP-0001`, `subjectCommit`
     `3bc8e9d8a94d44163d1af9325ad5b2272f71f8ed`, `verdict` `REWORK_REQUIRED`, `reviewReport`
     `docs/checkpoints/GATE-3-CP-0002/REVIEW-REPORT.md`, `correctiveCheckpoint` `GATE-3-CP-0003`,
     `findingsClosureFile` `M1-FINDINGS-CLOSURE.json` (no `redTeamReport`: this audit's battery
     uses identifiers the registry's attack parser does not read, and none of its attacks escaped);
   - closes the three findings, each with a regression test that fails without the correction;
   - runs the whole delivery order and seals at `READY_FOR_REVIEW`.
2. **A new fresh-session M1 audit** of the corrected delivery, in its own checkpoint. The harness in
   `audit-harness/` re-runs unchanged against a new subject; the clean clone of the remote is the
   control that must now pass.

Before anything, from a clean checkout:

```bash
python scripts/development-ledger/validate_checkpoint.py
```

and `python scripts/development-ledger/milestone_status.py --milestone M1`, which must report the
milestone as not passed and name this attestation's `REWORK_REQUIRED` as the reason.

```bash
python scripts/development-ledger/remote_sync.py --tag iacode-checkpoints/GATE-3-CP-0002
```

## What the corrections are

- **`M1-F-003` (HIGH).** `GATE-1-CP-0001`'s ledger record `cmd-0086` names commit
  `b59d66f9f3f9add2ae9dcd1cd4609fb4a1bf0b55`, which exists only as an unreachable object on this
  machine. Make it verifiable from the published history **without rewriting anything** — publish a
  reference that preserves that commit (it is present locally: `git cat-file -t b59d66f9f3f9`
  answers `commit`), for example a tag in a namespace of its own — and repair the guardrail: the
  sealed-history check (`test_every_sealed_checkpoint_validates_from_its_own_tag`, `MIR-016`) must
  clone through a transport that carries only published objects (`git clone --no-local`), with a
  test that fails when a sealed record names an unreachable commit. Record it as a lesson and a
  `GUARDRAIL_FAILURE` of the control that let it through. Then the clean clone of the remote must
  pass the full verification.
- **`M1-F-001` (MEDIUM).** Show the model the exact envelope of every kind, the tool object's `name`
  and `arguments` keys included, whenever native structured output is not requested; restate the
  shape in the repair; prove it with a live coding run of the configured model that executes its
  tools.
- **`M1-F-002` (MEDIUM).** Refuse, in the API, a tool result for a request of a stage with a sandbox
  policy; attack the refusal with a null control.

## What must not happen

**`GATE 4` is not started** before `M1` passes a fresh-session audit and the owner authorizes it.

**This audit is not rewritten to fit what follows.** A correction is a later checkpoint.

**Published history is not rewritten.** No amend, rebase, reset or force push of `origin/main`, and
no moved tag. The correction for `M1-F-003` adds a reference; it changes no existing one.
