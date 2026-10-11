# Baseline — GATE-4-CP-0005

## Proven predecessor

- `GATE-4-CP-0004` is sealed and published at
  `73cfa5eeb7fca2bf9312ec777d02f9ddfb2ad3d5` and its canonical tag resolves to the same commit.
- Local `main`, `origin/main`, the published tag and `STATE.json` agreed before this checkpoint was
  created; the worktree was clean and `validate_checkpoint.py` returned `CHECKPOINT_VALID`.
- The predecessor records `REWORK_REQUIRED` with the single open HIGH finding `G4-F-002`. Gate 4,
  M2 and Gate 5 remain unadvanced.

## Derived corrective scope

- The mandatory lesson preflight considered 94 lessons, selected 93 and derived 93
  `LESSON-REQ-` requirements (`cmd-0002`).
- Canonical derivation produced 219 rows: 105 Gate 4 rows, 93 lesson rows, `G4-F-002`, and the 20
  mandatory attacks from the sealed independent Red Team (`cmd-0005`).
- The sealed audit's schema-bound `FINDINGS.json` is now consumed as the finding owner. The focused
  compatibility regression first failed because the JSON parser import was absent (`cmd-0003`) and
  then passed after the correction (`cmd-0004`); the failed attempt remains recorded.

## Observable pre-correction state

- The audit's single full run is immutable evidence: 42 stages executed, `infra` and `smoke`
  failed, and the result was 40/42. Its report did not preserve the failing subprocess output, so
  the exact assertion text cannot be reconstructed from the sealed artifacts.
- The exact stages pass when repeated against the already-running stack: `infra` passed 49 tests
  (`cmd-0009`) and `smoke` passed 18 checks (`cmd-0010`). This confirms the audit's observation and
  does not supersede its red full run.
- `docker compose ls` shows the only project named `iacode` is currently owned by
  `C:\Users\cesar\AppData\Local\Temp\iacode-g4-audit-clone-uc6e59px\iacode`, not by this checkout
  (`cmd-0008`). Both checkouts read `COMPOSE_PROJECT_NAME=iacode`, the same fixed published ports,
  the same container names, network and named volumes.
- The regression added before correction fails in all three required ways (`cmd-0006`): there is
  no checkout-owned verification environment, stage subprocesses cannot receive a frozen isolated
  environment, and the live stack stage does not build every image it exercises.
- The live infrastructure assertion reads Prometheus target state immediately even though the
  configured scrape cycle is asynchronous. The smoke path has a bounded scrape-cycle wait, but
  the infrastructure path does not share it.

## Root-cause diagnosis

`G4-F-002` is the combination of an unisolated verification runtime and an uncoordinated
asynchronous observation:

1. every checkout and transport clone defaults to the same Compose project `iacode`, so a clean
   Git clone reuses or replaces another checkout's containers, volumes, image tags and published
   ports instead of receiving a clean runtime;
2. the verification stack stage omits `--build`, so the shared image namespace may be older than
   the checkout whose source is being judged; and
3. the live infrastructure suite samples Prometheus without waiting for a scrape from the stack
   that was just started or recreated.

The isolated green repetitions are the expected signature: once the shared stack has converged,
both checks pass. A retry would hide the defect; runtime isolation plus a scrape-derived observation
boundary removes it.

## Corrective boundary

This checkpoint may close only `G4-F-002` and the directly required ledger compatibility,
verification isolation, observability coordination, evidence and guardrails. It may not weaken or
reopen G4-X7, reduce the 42-stage denominator, grant `GATE_PASS`, approve M2, or start Gate 5.

## Published full-verification attempt 1 — preserved red

`cmd-0040` ran the canonical verifier once from published commit
`8324662c33cc26a2ebd8d8131d98f66138a4d679`. It remains red and is summarized without
replacement in `PUBLISHED-FULL-VERIFY-FAIL-CMD-0040.json`:

- `gate:tests` ran 763 tests and failed one assertion plus one setup path because the existing
  observer guard required local `time` calls instead of accepting the canonical delegated helper;
- `gate:checkpointValidation` correctly refused a detached pre-final commit with no checkpoint tag;
- the transport harness then reproduced `LSN-0083` by re-emitting Angular's U+276F through cp1252,
  so it ended before the verifier could write its JSON report.

The verifier cleaned its owned Compose project in `finally`; the shared audit-owned `iacode`
project remained untouched. The next complete execution is a new rework cycle, never an isolated
rerun or a replacement for `cmd-0040`.
