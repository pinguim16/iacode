# Final Report — GATE-2-CP-0002

## Gate

`GATE 2 — AGENT RUNTIME`, milestone `M1` (Gates 0 to 3). This checkpoint closes the Gate from
`GATE-2-CP-0001`, which delivered it and was sealed `BLOCKED` on the provider's quota.

## Status

`INTERNAL_GATE_PASS`.

The project's own controls passed. That is not an independent verdict and is not recorded as one:
`independentReview` is `PENDING`, and the adversarial battery this run executed is the delivery's
internal one, filed as `M1-INTERNAL-RED-TEAM.json`. `M1` is audited by a fresh session after GATE 3.

## Environment

Windows 11 Pro 10.0.26200, Python 3.13.15, Docker Desktop with Compose v2, Git. Branch `main`, base
commit `424650d58167422cda08ebd580cc70fe75433668`. The live provider is OpenAI, model `openai:gpt-4o-mini`, configured by the
operator in the git-ignored `infra/compose/.env`.

## Tool / Model / Effort

Claude Code in the Claude desktop application, model Claude Opus 5.5 (`claude-opus-5-5`). The
reasoning effort is not exposed to the run.

## Deliverables

- Live evidence for rows 19.1, 19.2 and 19.5: the gateway smoke `cmd-0005`, the agent runtime smoke `cmd-0006`, the persisted provenance `cmd-0007`.
- OpenAI declared as a second provider, by configuration only.
- `G2-F-009`, `G2-F-010`, `G2-F-012`, `G2-F-013` and `G2-F-014` repaired, each with a test that
  fails on the replaced code,
  and `G2-F-011` corrected in the ledger on the operator's decision.
- `LSN-0047` to `LSN-0050` and `GRD-0049` to `GRD-0052`; the `LSN-0010` recurrence; `ADR-0023`.
- `GATE-2-CP-0001` anchored, and this checkpoint with its requirement set, evidence and handoff.

## Files Created

`scripts/iacode/agent_envelope_probe.py`, `.iacode/memory/retrospectives/GATE-2-CP-0002.md`,
`docs/adr/ADR-0023-sealed-checkpoint-binds-its-own-tag.md`, and this checkpoint's files. `FILES.json` carries each with its reason and hash.

## Files Modified

The provider policy and its environment wiring, the agent runtime's protocol, context and engine,
the workflow's terminal paths, the API's run creation, the gateway smoke's observability check, the
checkpoint validator and the seal tool, the Foundation smoke and the fresh-installation scenario,
their tests, `docs/CHECKPOINT-PROTOCOL.md`, the engineering memory, the integrity chain, `LATEST.md`, `START-HERE.md`, `README.md` and the
Model Gateway runbook. `FILES.json` carries each with its reason and hash.

## Validation

`validate_checkpoint.py`, `validate_lessons.py` and `verify_integrity.py` over the closure; the
Green Keeper, green on every mandatory gate in its third cycle after a red lint gate in its second
(`REWORK-LOG.jsonl`, `cmd-0056`); the full verification, every stage passing, the fresh
installation, the live smokes and the three agent runtime scenarios included (`cmd-0067`,
`VERIFICATION-REPORT.json`); the completeness audit (`cmd-0069`) and the internal mirror; the checkpoint is validated again from its sealed
content after the commit. Their records are in `COMMANDS.jsonl`.

## Tests

| Suite | Cases | Result | Evidence |
|---|---|---|---|
| Ledger and Gate suites | 578 | PASS | `cmd-0056` |
| Image suites (API, gateway, agent runtime) | 606 | PASS | `cmd-0013` |
| Live infrastructure suite | 48 | PASS | `cmd-0014` |
| **Total** | **1,232 / 1,232 discovered** | **PASS** | `TESTS.json`, `COUNTS.json` |

One ledger case skips itself and is counted as executed without failure, as every run of this suite has counted it: `Gate2AdrTests.test_the_index_lists_them`, because `docs/adr/README.md` does not exist, so it has never asserted anything; see `R-G2-012`.

## Red Team

The Gate's internal battery, unchanged, re-executed after the repairs: every attack defended with a
valid null-mutation control (`cmd-0021`, `M1-INTERNAL-RED-TEAM.json`, `RED-TEAM-REPORT.md`).
It is internal, not independent; the independent Red Team belongs to the `M1` audit after GATE 3.

## Known Risks

See `RISKS.md`. The operator's action item: rotate the OpenAI credential that was shared in a chat
transcript during the closure (`R-G2-009`).

## Remaining Work

Nothing this Gate specifies. Backlog items are the risks `R-G2-007` to `R-G2-013`.

## Handoff Readiness

The checkpoint validates, every mandatory gate is green, the requirement set is complete with every
evidence reference resolving, and `blockedBy` is empty. The next action requires the owner.

## Next Gate

`GATE 3 — SANDBOX`, only after the owner's explicit authorization. `M1` stays `PENDING` until a
fresh session audits it after GATE 3.

## Evidence

`COMMANDS.jsonl` (every command, including the failures), `DECISIONS.md` (the decisions, the
findings, and the records made against the sealed `GATE-2-CP-0001`), `CLOSURE-REQUIREMENTS.json`,
`REQUIREMENTS-MATRIX.json`, `COMPLETENESS-REPORT.json`, `TESTS.json`, `COUNTS.json`,
`M1-INTERNAL-RED-TEAM.json`, `M1-INTERNAL-MIRROR.json`, `REWORK-LOG.jsonl`, `VERIFICATION-REPORT.json`.
