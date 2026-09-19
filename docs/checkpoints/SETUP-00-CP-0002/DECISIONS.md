# Decisions

## Preserve the original checkpoint

`SETUP-00-CP-0001` and its tag remain unchanged. Its statement that Claude Code was absent is retained as historical evidence of a PATH-scoped detection error and is superseded by this checkpoint.

## Detect installations by resolved paths, not PATH alone

The user-local Claude Code executable is recorded at `C:/Users/cesar/.local/bin/claude.exe`, version `2.1.195`. A failed bare command is evidence only that the executable was not resolved from the current PATH.

## Use verified project subagents

The documented `.claude/agents/*.md` mechanism is used for ten thin adapters. `.iacode/agents/` remains canonical; each adapter names and loads its matching contract and uses `model: inherit`. No project hook, MCP server, model, credential, or permission bypass is added.

## Keep cross-tool validation pending on authentication

The installed executable was invoked in a clean clone, but `claude auth status` reports no login and the non-interactive run stopped before a model call. This is `BLOCKED_AUTHENTICATION` for second-tool validation, not evidence of an installation failure and not a PASS.
