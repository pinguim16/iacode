# Next

## Required next action

`GATE 2 — AGENT RUNTIME` requires the owner's explicit authorization and a new pre-Gate checkpoint
before any file is changed. Nothing in this change set belongs to Gate 2.

Before that Gate starts:

1. Read `START-HERE.md`, `docs/DEVELOPMENT-CONTRACT.md` and `docs/MASTER-PLAN.md`.
2. Read `docs/checkpoints/LATEST.md` and every file in the checkpoint it names.
3. Run `python scripts/development-ledger/validate_checkpoint.py`.
4. Confirm `git status --short --branch`, `git branch --show-current` and `git rev-parse HEAD`
   against `STATE.json`.
5. Create the pre-Gate checkpoint with `new_checkpoint.py --gate GATE-2 --status BASELINING`.
6. Run the lesson preflight for Gate 2 and carry every derived requirement into the matrix.

## What Gate 2 inherits

- A provider-neutral boundary it can call without knowing a provider exists, and a second consumer
  path that needs no web application: implement `CatalogStore` and `ModelCallStore` and compose
  `ModelGateway` directly.
- A catalog whose capabilities are honest. Every DevWorld model currently reports `tools`,
  `vision`, `structured-output` and `reasoning` as `UNKNOWN`, because the provider publishes
  nothing about them. The router refuses an unknown capability rather than guessing, so an agent
  that requires tool calling will be refused until an operator states the capability in
  `.iacode/policies/providers.json` or a route opts in through `allowUnknownCapability`. That is
  the first thing Gate 2 will meet, and `docs/runbooks/MODEL-GATEWAY.md` says how to resolve it.
- Tool calls that are *normalised* and never executed. Execution is Gate 2's, inside Gate 3's
  sandbox.
- A `model_calls` table that records what a call cost and never what it said.

## What M1 still owes

`M1` is `PENDING` and covers Gates 0 to 3. It is audited after Gate 3 by a fresh-session run
against a sealed subject, which produces `MILESTONE_INDEPENDENT_AUDIT_PASS`, or by a cross-tool run,
which produces `MILESTONE_EXTERNAL_PASS`. Neither may be claimed by an implementing run, and this
checkpoint claims neither.

## Open backlog

None. No Critical, High, Medium or Low finding is open. The six findings this Gate raised against
itself are listed in `DECISIONS.md`; each was repaired inside the Gate and turned into an automated
control.

`RISKS.md` carries the risks that survive into `M1`, each with the condition that turns it into a
defect.
