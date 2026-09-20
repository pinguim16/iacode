# Detected Tool Capabilities

Detection was performed locally during SETUP-00 and its correction checkpoint. Capability claims are based on local executable help/version output or official tool documentation.

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

- Installed version: `2.1.195 (Claude Code)` at `C:/Users/cesar/.local/bin/claude.exe`. A second bundled copy reports `2.1.187` at `C:/Users/cesar/AppData/Local/Claude-3p/claude-code/2.1.187/claude.exe`.
- PATH caveat: the user-local binary directory was not in the detecting process's `PATH`; therefore bare `claude --version` failed even though Claude Code was installed.
- Project instructions: `CLAUDE.md` is loaded as repository context.
- Agents and subagents: project definitions use the documented `.claude/agents/*.md` format. The ten adapters map one-to-one to `.iacode/agents/` and inherit the selected session model.
- Hooks: local CLI help exposes hooks, and project configuration supports hooks in `.claude/settings.json`; SETUP-00 requires no mandatory Claude-specific hook.
- MCP: local CLI help exposes MCP commands, and project MCP configuration is supported through `.mcp.json`; SETUP-00 has no MCP dependency.
- Permissions and configuration: local CLI help exposes allowed/disallowed tools, permission modes, settings sources, agent selection, and effort levels. The repository does not enable a permission bypass.
- Authentication: `claude auth status` reported `loggedIn: false` and `authMethod: none` on 2026-09-19 and again on 2026-09-20 for the `C:/Users/cesar/.local/bin/claude.exe` CLI installation. A clean-clone non-interactive validation reached the executable but stopped with `Not logged in`; no model call or file modification occurred.
- Executed sessions: an authenticated Claude Code desktop session performed the independent review, the Red Team battery, and the `SETUP-00-CP-0003` implementation on 2026-09-20. The desktop session and the unauthenticated CLI installation are separate; the CLI cold-start blocker is unchanged. The ten project subagents in `.claude/agents/` were observed loaded by that session, which confirms the adapter format is accepted by the runtime.

## Portable baseline

Python `3.13.15` and Git `2.52.0.windows.1` are available. The optional `jsonschema` package is absent, so checkpoint validation uses a tested standard-library implementation limited to the schema keywords present in this repository.
