# Live program state

The current pointer is generated, not committed:

```text
python scripts/development-ledger/program_state.py --write
python scripts/development-ledger/program_state.py
```

Canonical policy writes `var/program-state.json`, an ignored runtime observation containing exact
local/remote SHAs, the latest checkpoint, its truthful STEPS and current status. Explicit `--write`
regenerates it after Git/checkpoint boundaries. Validation refuses stale or contradictory data and
never rewrites it. The pointer does not grant a Gate or milestone verdict.

`PROGRAM-STATE.json` beside this document is the unchanged historical schema 1.0 observation, not
the live pointer. Subjects without current policy retain legacy storage/status semantics. See
[ADR-0045](../adr/ADR-0045-live-program-state-is-generated-after-git-boundaries.md).
