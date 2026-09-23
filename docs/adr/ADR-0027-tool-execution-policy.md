# ADR-0027 — What a tool may do is canonical policy, and the agent can neither choose nor change it

Status: Accepted
Date: 2026-09-22
Owners: GATE 3 — Sandbox

## Context

Gate 2 gave each agent profile `allowedActions` and gave every shipped profile none. Gate 3 makes
tools real, and the question is who decides what executing one may cause: which tools exist, which
role may call which, with what limits, on what network, with which environment, and whether a
request can argue for more.

A model writes the tool request. Whatever the request can express, a model will eventually express,
including `"network": "full"`, `"memory": "unlimited"` and `"mount": "C:\\"`.

## Decision

**The Sandbox Tool Policy is one canonical file, `.iacode/policies/sandbox-policy.json`, and nothing
a request carries can change what it says.**

- The **tool registry** (`iacode_sandbox.tools.REGISTRY`) is closed: `filesystem.list/read/search/
  write/apply_patch`, `shell.exec`, `git.status/diff/log/show/add/commit`. A name it does not hold is
  refused with `UNKNOWN_TOOL`; nothing maps an unknown name to a shell, a module or a path.
- A **policy** names the tools it allows, an image profile, a resource profile, a network profile and
  the workspace access. `developer` reads, writes, patches, runs commands and commits locally;
  `reviewer` reads, searches and inspects history and diffs, and cannot write, run or commit. A
  read-only policy that lists a writing tool is refused when the policy is loaded.
- An **agent profile** that permits a tool must name the sandbox policy that executes it, and the run's
  plan freezes that name per stage when the run is created. The request carries the name; the
  sandbox reads everything else from the policy.
- **Arguments are validated strictly.** Every tool declares its arguments; an undeclared key is
  `ARGUMENT_UNKNOWN`, a wrong type is `ARGUMENT_WRONG_TYPE` (never reported as missing), and a
  request may lower a command's timeout but never raise it. No tool declares an argument for a
  limit, a mount, an image or a network, so there is nothing to argue with.
- **Limits are bounded in code.** `iacode_sandbox.policy.BOUNDS` refuses zero, negative and absurd
  values when the policy is loaded, so a typo in the policy stops the service instead of the machine.
- **The environment is an allowlist.** A command starts from a fixed base and may set only the names
  the policy allows; the loader refuses a name that looks like a credential or a host endpoint.
- **Execution inside the sandbox is automatic.** An allowed tool runs without a human confirming each
  read, write or test — the sandbox is what makes that safe. Nothing runs on the host, ever.
- **The agent's Git is local.** No push, fetch, pull, clone, remote, reset, clean or rebase tool; a
  sandbox identity (`IACode Agent`, an address under `.invalid`); no credential helper, no remote
  protocol, no hooks and no network. The Git of IACode's own development is governed by
  [ADR-0024](ADR-0024-public-remote-and-atomic-commits.md) and never enters a sandbox.
- **Results are data.** A tool result returns to the agent in a labelled block, bounded inline, with
  the rest in the artifact store; it is never merged into the agent's instructions.

## Consequences

**Giving a role a tool is a reviewed change in two files.** The profile and, if the tool is new to
it, the policy. `Gate3AgentToolPolicyTests` proves every permitted action is a registered tool the
named policy allows.

**The shell is the widest tool, and it is bounded by the container, not by the policy.** A policy can
withhold `shell.exec` — the reviewer's does — but cannot restrict what a shell does once granted,
because a command allowlist inside a shell is not a control. The container is.

## Alternatives considered

**Let the request carry limits within a ceiling.** Rejected: it invites the negotiation this ADR
exists to prevent, for no benefit a policy change cannot give.

**Confirm every tool with a human.** Rejected for this project: the sandbox makes the action safe,
and a confirmation on every read would make the platform unusable without adding a control.

**A per-command allowlist for `shell.exec`.** Rejected: shells compose, and an allowlist of command
names is bypassed by the first `sh -c`.
