# Planned Architecture

## Current state

Only the SETUP-00 development control plane exists. No model gateway, agent runtime, sandbox, quality runtime, IDE integration, memory system, learning engine, or training pipeline has been implemented.

## Control-plane architecture

The repository is the source of truth:

```text
canonical contracts (.iacode/)
            |
            +-- Codex adapter (AGENTS.md)
            +-- Claude Code adapters (CLAUDE.md, .claude/agents/)
            +-- future verified adapters
            |
            +-- Engineering Ledger (docs/checkpoints/)
            +-- validation tools (scripts/development-ledger/)
```

Canonical agent definitions are independent of any provider. Tool adapters may express supported integration mechanisms but may not alter semantics. Checkpoints contain observable state, evidence, provenance, and continuation instructions.

## Planned runtime boundaries

Future Gates will establish, in order, foundation contracts, a model gateway, agent runtime, sandbox, quality engine, and VS Code integration. Later releases add experience, knowledge, code graph, project memory, gap detection, research, skills, dataset production, model training, evaluation, shadow mode, promotion, and autonomous learning.

These are plans, not current capabilities. See `MASTER-PLAN.md` for prerequisites and acceptance conditions.
