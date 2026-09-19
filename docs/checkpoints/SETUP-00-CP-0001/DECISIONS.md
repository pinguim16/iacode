# Decisions

## Confirmed architecture decisions

- ADR-0001 makes documentation a first-class artifact.
- ADR-0002 establishes validated repository checkpoints.
- ADR-0003 makes `.iacode/agents/` canonical and tool-neutral.
- ADR-0004 denies training and distillation rights by default.
- ADR-0005 establishes Gate-bound, non-destructive Git discipline.

## Bootstrap decision

The baseline was an empty directory without Git, scripts, or a checkpoint. Inspection and capability detection therefore preceded repository initialization, and `PLAN.md` was the first content artifact. Pre-existing checkpoint validation was impossible and is not claimed.

## Capability decision

Codex CLI `0.155.0-alpha.9` reports stable multi-agent, hook, and MCP capability. `AGENTS.md` is the verified project adapter required by this setup. Claude Code is not installed, so only the required semantically equivalent `CLAUDE.md` adapter was created; unverified `.claude/agents/` and hooks were not invented.

## Schema decision

The optional third-party `jsonschema` package is absent. A standard-library validator implements and tests the schema features used by this repository, including local references, types, required fields, enums, constants, patterns, formats, item constraints, and additional-property rules.

## Commit evidence decision

A commit cannot contain its own cryptographic hash. Intermediate state may use symbolic `HEAD`; Gate closure uses `refs/tags/iacode-checkpoints/SETUP-00-CP-0001`, created after the final commit and resolved by the validator. This anchors the checkpoint to one commit without self-reference. The Git history is the terminal evidence for the final commit command, avoiding recursive modification of `COMMANDS.jsonl`.
