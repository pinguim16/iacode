# Decisions

## D-01 — The Gate 4 denominator is fixed before product code

The owner mandate, master plan, inherited architecture, and engineering lessons were consolidated
into `docs/GATE-4-CHECKLIST.md`. The canonical parser derives 105 Gate rows and the lesson preflight
derives 58 more, so implementation is measured against 163 requirements. The registry is only a
row-for-row mirror and cannot shrink the source document.

## D-02 — The baseline is focused; the complete suite belongs to Green Keeper

An attempted pre-implementation run of the complete control-plane suite was manually stopped after
roughly nine minutes when historical ledger evidence showed that this suite normally takes 37–72
minutes. The recorder process was also stopped, so it emitted no command record; this paragraph is
the explicit record rather than a fabricated result. The baseline was replaced by focused checks of
the sealed Gate 3 sandbox boundary and the exact Gate 4 derivation (`cmd-0005`, `cmd-0006`). The
complete suite remains mandatory and will run through Green Keeper before handoff.

## D-03 — A normalized identifier is compared with a normalized identifier

The first Gate 4 test run (`cmd-0007`) failed because the new test compared the normal form
`GATE4` with the documentary spelling `GATE-4`. The repository policy was correct; the test mixed
representations. The repair normalizes both operands, and `cmd-0008` passes all seven kickoff tests.
