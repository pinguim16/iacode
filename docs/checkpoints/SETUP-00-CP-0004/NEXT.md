# Next

## Required next action

Claude Code must implement a new SETUP-00 corrective checkpoint that:

1. defines and enforces valid `blockedBy`/status combinations, including a regression that rejects
   `READY_FOR_REVIEW` with blockers after a fully resealed fixture;
2. records every finalization attempt, including early refusals such as detached HEAD, invalid target,
   and invalid commit reference;
3. records a command string that is executable from its declared working directory;
4. reruns the entire suite and adversarial battery; and
5. closes at `READY_FOR_REVIEW` for another independent Codex review.

Do not modify or retag CP-0001, CP-0002, CP-0003, or CP-0004. Do not begin Gate 0.

## Next Gate

Gate 0 remains `BLOCKED`.
