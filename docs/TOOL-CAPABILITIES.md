# Detected Tool Capabilities

Detection was performed locally during SETUP-00; no capability below is inferred from an uninstalled tool.

## Codex

- Version: `codex-cli 0.155.0-alpha.9`.
- Project instructions: `AGENTS.md` is the repository adapter used by the active Codex environment.
- Agents and subagents: `codex features list` reports `multi_agent` as stable and enabled; `codex agents` is exposed by CLI help.
- Hooks: `hooks` is reported stable and enabled. No hook was added because SETUP-00 needs no safe mandatory hook beyond the portable validator.
- MCP: `codex mcp` exposes list, get, add, remove, login, and logout. No project MCP dependency is required by SETUP-00.
- Permissions: CLI help exposes sandbox modes, approval policies, and the explicit dangerous bypass flags. Repository policy does not enable a bypass.
- Configuration: CLI help exposes `--config`, feature toggles, and profiles. User configuration was not read or copied because it may contain machine-local or sensitive values.
- Model and effort: the system identifies the GPT-5 family, but the exact model identifier and active effort are not exposed to the repository; metadata records that limitation.

## Claude Code

`claude --version` failed because the executable is not installed. Project instructions beyond the required `CLAUDE.md`, agents/subagents, hooks, MCP, permissions, and configuration therefore could not be verified. No `.claude/agents/` directory or hook format was invented.

## Portable baseline

Python `3.13.15` and Git `2.52.0.windows.1` are available. The optional `jsonschema` package is absent, so checkpoint validation uses a tested standard-library implementation limited to the schema keywords present in this repository.
