# Baseline

The corrective run started from published commit
`dfa2871c4fcecf9eedd7df9f135a5cfcdebce9d5`, where local `main`, `origin/main` and
`refs/tags/iacode-checkpoints/GATE-4-CP-0006` agreed and `DIVERGENCE.md` was the only untracked
path.

The mandatory receiver validation preserved these observations:

- local checkpoint validation was red because the truthful divergence record was not declared by
  the sealed CP0006 inventory;
- integrity remained green at 28 anchors;
- local and remote branch/tag synchronization for CP0006 passed;
- a fresh clone of `https://github.com/pinguim16/iacode.git`, detached at CP0006, reproduced the
  publication defect in `cmd-0005`: validation exited 1 because `COMMANDS.jsonl:61` names
  `.git/gate4-cp0006-pre-red-retry.zip`, which the transport does not carry.

`CP0006-REMOTE-TRANSPORT-BASELINE.json` is the machine-readable red baseline. The sealed CP0006
content and its canonical tag remain unchanged.

The root cause has three parts:

1. the shared ignored-path query delegates to `git check-ignore`, which does not classify a path
   inside Git's own metadata directory;
2. command validation treats a locally existing input as sufficient before it asks whether a
   transport clone can carry that path;
3. caller-supplied inputs and direct command-record construction can bypass the recorder's
   auto-detection filter.

This is a recurrence of `LSN-0040` while `GRD-0042` was marked effective, so it is a
`GUARDRAIL_FAILURE`, not an unrelated new failure class.
