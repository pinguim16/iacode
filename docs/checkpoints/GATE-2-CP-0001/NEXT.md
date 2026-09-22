# Next

## Required next action

Wait for the DevWorld quota to reset — the provider reported roughly 14.6 hours from
2026-09-22T15:40Z, so approximately 2026-09-23T06:20Z — and then run, from the repository root:

```bash
python scripts/development-ledger/record_command.py --purpose "GATE 2 live evidence: the Model Gateway against the configured provider" --phase validation -- python scripts/iacode/gateway_smoke.py --report var/gateway-smoke.json
```

```bash
python scripts/development-ledger/record_command.py --purpose "GATE 2 live evidence: a single-agent run and a planner-reviewer run through the Model Gateway" --phase validation -- python scripts/iacode/agent_runtime_smoke.py --report var/agent-runtime-smoke.json
```

Both must report `PASS`. The second is what rows 19.1, 19.2 and 19.5 require.

## Then

1. Mark `REQ-0127`, `REQ-0128` and `REQ-0131` `COMPLETE` in
   `docs/checkpoints/GATE-2-CP-0001/CLOSURE-REQUIREMENTS.json`, with the recorded command as their
   evidence, and re-derive:
   ```bash
   python scripts/development-ledger/derive_requirements.py --write
   ```
2. Re-run the completeness audit, which must reach 100%:
   ```bash
   python scripts/development-ledger/check_completeness.py --write
   ```
3. Re-run the internal mirror, which must then pass `MIR-001` and `MIR-009`:
   ```bash
   python scripts/development-ledger/m0_mirror_audit.py --write
   ```
4. Clear `blockedBy` in `STATE.json`, finalize at `INTERNAL_GATE_PASS`, commit and seal.

## What must not happen

**The smoke model is not substituted.** If the configured model still will not answer, the Gate
stays `BLOCKED`. Pointing `IACODE_GATEWAY_SMOKE_MODEL` at a model that happens to be available is a
decision about what this project pays for and what its evidence describes, and it belongs to the
operator, recorded as a decision, not to a delivery trying to turn a status green.

**GATE 3 does not start.** The sandbox is reserved, `services/sandbox/` holds its README and
nothing else, and `ADR-0021` states where the executor belongs when that Gate opens.

**`M1` stays `PENDING`.** The milestone is audited after GATE 3, by a fresh session, and the
internal mirror in this checkpoint is not that audit and does not become it.
