# Plan — GATE-2-CP-0001

`GATE 2 — AGENT RUNTIME`. 176 requirements: 137 from `docs/GATE-2-CHECKLIST.md` and 39 derived by
the lesson preflight. The plan below is the order the work is done in, and each step names what
makes it verifiable.

## The shape of the delivery

```text
   HTTP client / operational page
             |
             v
   apps/api  /api/v1/agent-runs           creates, reads, streams, cancels, resolves tools
             |
             |  starts / signals / queries
             v
   Temporal  AgentRunWorkflow             durable, deterministic; every effect is an activity
             |
             v
   iacode_agent_runtime                   provider-neutral: states, events, profiles, protocol,
             |                            budgets, context assembly, tool requests
             v
   ModelGateway (Gate 1)                  routing, retries, circuit, fallback, providers
             v
   provider adapter -> model
```

The runtime knows nothing about a provider and nothing about a web framework. It declares ports —
a store, a model client, a clock — and the processes above it supply them.

## Steps

1. **Shared persistence package.** Move the declarative base, the ORM and the engine helpers out of
   the web application into `packages/persistence`, so the API and the worker read one authoritative
   schema definition instead of two that can drift. The API keeps its settings-shaped wrapper and
   delegates. *Verifiable by:* the existing backend suite staying green, and a control-plane test
   that no second schema definition exists.

2. **Migration `0003`.** Evolve `tasks`, `task_runs`, `agents`, `agent_runs`; add
   `agent_teams`, `run_events`, `tool_requests`, `tool_results`. Extend the run state vocabulary
   from the one authoritative tuple. *Verifiable by:* a fresh database reaching head, and a database
   at the Gate 1 revision upgrading.

3. **The runtime contracts.** `states.py` (state machine), `events.py`, `contracts.py`
   (run plan, budgets, tool request and result, run summary), `errors.py` (taxonomy), `limits.py`,
   `ports.py`. *Verifiable by:* the runtime suite; every transition, allowed and forbidden.

4. **Profiles, teams and prompts.** `agents/profiles/*.json`, `agents/teams/*.json`,
   `agents/prompts/*.md`, loaded and validated by `profiles.py` and `registry.py`, with a content
   hash per template. Four agents — engineering lead, planner, reviewer, generalist — and two
   teams — single agent, planner and reviewer. *Verifiable by:* the registry suite and an
   idempotent bootstrap.

5. **The agent turn protocol.** `protocol.py`: a versioned envelope with exactly three kinds, a
   strict parser and one bounded repair. `context.py`: assembly that keeps runtime instructions,
   role instructions, task content and tool results in separate channels. *Verifiable by:* the
   protocol suite, including an invalid output, a repaired output and two invalid outputs.

6. **The engine.** `engine.py`: the turn loop, provider-neutral and synchronous in its own terms —
   one turn in, one outcome out — with budgets, provenance, events and the tool pause. It performs
   no I/O itself: it asks its ports. *Verifiable by:* the engine suite against deterministic
   doubles.

7. **The gateway client.** `gateway_client.py`: the only path to a model, wrapping
   `ModelGateway`. *Verifiable by:* a boundary scan and a test that the runtime reimplements no
   resilience policy.

8. **The store.** `persistence.py`: the SQL implementation of the runtime's ports, over the shared
   ORM. Append-only events with a monotonic per-run sequence; idempotent appends; a result unique
   per request. *Verifiable by:* the backend integration suite against the real database.

9. **The workflow.** `iacode_orchestrator/workflows/agent_run.py` and its activities. Deterministic
   workflow code; the model call, every write and every notification are activities. A signal
   delivers a tool result; Temporal's own cancellation ends the run; `wait_condition` with a
   timeout implements the tool wait. *Verifiable by:* a determinism scan, the integration suite and
   the restart scenario.

10. **The API.** `/api/v1/agent-runs` with creation, read, list, events as a page and as a stream,
    cancel, tool results, and the profile and team listings. Idempotency on creation. *Verifiable
    by:* the backend suite.

11. **The frontend.** One operational page: write a task, choose a team, optionally a route or a
    model, start, follow, see the result, cancel, and see a waiting tool without any way to run it.
    *Verifiable by:* the frontend suite and a browser smoke.

12. **Live evidence.** `scripts/iacode/agent_runtime_smoke.py`: one single-agent run and one
    planner-reviewer run against the configured provider, three model calls in total, short prompts
    and a low output cap. `BLOCKED` rather than `FAIL` when no credential is configured.

13. **The durability scenario.** `scripts/iacode/scenarios/agent_runtime_durability.py`: a run
    reaches `WAITING_FOR_TOOL`, the worker container is restarted for real, the tool result is
    delivered, the run resumes and completes.

14. **Guardrails.** A tool-execution boundary scan, a direct-provider scan and a workflow
    determinism scan, each written as a property of the boundary rather than of a file, each with a
    null control.

15. **Verification, documentation, decisions.** The Gate's stages in `verify.py`, the runbook,
    `ARCHITECTURE`, `DEVELOPMENT`, `VERSIONS`, `README`, `START-HERE`, and ADRs 0020 to 0022.

16. **Delivery assurance.** Green Keeper until every mandatory gate is green, the completeness
    audit at total coverage, the internal Red Team battery, the internal mirror audit, the
    retrospective, then seal.

## Risks this plan accepts

- **The persistence extraction touches Gate 0 and Gate 1 code.** It is a refactor with a green
  suite on both sides, and the alternative — a second ORM in the worker — is the duplicate
  definition the engineering memory already records as a failure class.
- **Every provider capability is `UNKNOWN`.** The protocol therefore cannot rely on native
  structured output. It uses validated JSON text and asks for the native capability only where a
  model declares it. Nothing in this Gate declares a capability on a model's behalf.
- **Live evidence costs tokens.** Three short calls with a low output cap is the price of proving
  the integration runs. The alternative is a Gate that claims a live run it never made.
- **A restart scenario is slow and infrastructural.** It restarts one container rather than the
  stack, and it is part of the full verification rather than the inner loop.

## Stop conditions

Stop and record rather than repair silently when: a mandatory gate is red for a reason outside this
Gate's scope; the live smoke reports anything other than `PASS` or a `BLOCKED` naming a variable; a
credential appears anywhere outside `infra/compose/.env`; any path lets a model's tool request reach
a host action; or the predecessor's sealed checkpoint stops validating.
