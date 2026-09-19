# Diff Summary

- Corrected the current Claude Code capability record and the PATH-scoped false negative.
- Added ten project-subagent adapters under `.claude/agents/`, one for every canonical role.
- Updated the architecture and tool-neutral agent ADR to include the verified Claude adapter mechanism.
- Added three automated adapter-contract tests; the full suite now contains 37 passing tests.
- Recorded the clean-clone Claude execution attempt and its authentication blocker without claiming cross-provider validation.
- Created `SETUP-00-CP-0002` as the correction ledger; `SETUP-00-CP-0001` is unchanged.
