# IACode

IACode is a planned private, autonomous, general-purpose, self-improving software engineering
platform. This repository contains the development control plane established by **SETUP-00** and the
runtime foundation delivered by **GATE 0 — FOUNDATION**, the provider-neutral model
boundary delivered by **GATE 1 — MODEL GATEWAY**, and the durable agent execution
delivered by **GATE 2 — AGENT RUNTIME**.

Begin with [START-HERE.md](START-HERE.md). The repository is the source of truth; chat history is
not.

## Current boundary

- Current Gate: `GATE 2 — AGENT RUNTIME`, milestone `M1`.
- What runs: an API, a Temporal worker, a web shell, PostgreSQL, Redis, MinIO, Temporal, Prometheus
  and Grafana, locally on Docker Compose — and the Model Gateway, which discovers a provider's
  models and invokes them behind one provider-neutral contract.
- And the Agent Runtime, which executes a team of agents as a durable Temporal workflow and
  reaches a model only through that gateway.
- What does not: **tool execution**. An agent that asks for a tool has its request recorded
  and the run pauses; the sandbox that will execute one is `GATE 3`. Retrieval, the
  experience store and training belong to later Gates too; the directories reserved for them
  say so and contain nothing else.
- Canonical agent definitions: `.iacode/agents/`.
- Latest reconstructible state: [docs/checkpoints/LATEST.md](docs/checkpoints/LATEST.md).

## Running it

You need Docker with Compose v2, Python 3.12 or newer, and Git. Nothing else: every service and
every build runs in a container.

```bash
python scripts/iacode/bootstrap_env.py
python scripts/iacode/stack.py up --build
python scripts/iacode/smoke.py
```

To reach a model provider, set `IACODE_DEVWORLD_BASE_URL` and `IACODE_DEVWORLD_API_KEY` in
`infra/compose/.env` — the file Git ignores — and then:

```bash
python scripts/iacode/gateway_smoke.py
```

Without a credential that check exits `BLOCKED` and names the variable that is missing. It never
claims a result it did not obtain.

To run an agent through that gateway:

```bash
python scripts/iacode/agent_runtime_smoke.py
```

Then the API is at <http://localhost:18080>, the Foundation page at <http://localhost:18081>,
the Model Gateway page at <http://localhost:18081/gateway> and the Agent Runtime page at
<http://localhost:18081/agent-runtime>.
Every port is configurable and bound to loopback; the defaults and the rest of the operator's
commands are in [docs/runbooks/FOUNDATION.md](docs/runbooks/FOUNDATION.md).

## Verifying it

```bash
python scripts/iacode/verify.py --fast   # everything that does not restart the stack
python scripts/iacode/verify.py          # everything, including a fresh installation
```

On Windows, `.\verify.ps1` does the same. The full run ends by deleting every volume and rebuilding
from nothing, because that is the claim this Gate makes.

## Reading it

| Question | Document |
|---|---|
| How do I work on this? | [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) |
| How do I operate the stack? | [docs/runbooks/FOUNDATION.md](docs/runbooks/FOUNDATION.md) |
| How do I configure and operate a model provider? | [docs/runbooks/MODEL-GATEWAY.md](docs/runbooks/MODEL-GATEWAY.md) |
| How do I back it up and restore it? | [docs/runbooks/BACKUP-RESTORE.md](docs/runbooks/BACKUP-RESTORE.md) |
| What is the shape of the system? | [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) |
| What version is everything on? | [docs/VERSIONS.md](docs/VERSIONS.md) |
| What comes next, and when? | [docs/MASTER-PLAN.md](docs/MASTER-PLAN.md) |
| Why is it built this way? | [docs/adr/](docs/adr/) |

## Validating the ledger

```bash
python scripts/development-ledger/validate_checkpoint.py
python -m unittest discover -s tests
```
