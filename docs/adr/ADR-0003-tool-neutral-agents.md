# ADR-0003 — Canonical tool-neutral agent definitions

Status: ACCEPTED
Date: 2026-09-19
Owners: IACode maintainers

## Context

Codex, Claude Code, and future tools have different adapter mechanisms.

## Decision

Define agent semantics in `.iacode/agents/`; root tool files are adapters only.

## Evidence

- Codex CLI reports stable multi-agent support.
- Claude Code is absent, so its additional local formats cannot be verified.

## Alternatives Considered

- Make one provider format canonical.
- Duplicate independent policies per tool.

## Consequences

Adapters remain small and must be checked for semantic equivalence.

## Risks

Future adapter limitations may require an explicitly documented mapping.

## Reversal Strategy

Version the canonical contract and generate verified adapters from it.

## Related Artifacts

`.iacode/agents/`, `AGENTS.md`, `CLAUDE.md`.

