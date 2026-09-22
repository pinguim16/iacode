# Diff Summary — GATE-2-CP-0002

Measured against `424650d58167422cda08ebd580cc70fe75433668`, the seal of `GATE-2-CP-0001` (`BLOCKED`).

## What was added

**`scripts/iacode/agent_envelope_probe.py`** — the replayable diagnostic of `G2-F-009`: one gateway
call with the runtime's own planner context, reporting only the shape of the answer and the
parser's verdict, never its text.

**`docs/checkpoints/GATE-2-CP-0002/`** — this checkpoint. **`.iacode/memory/retrospectives/GATE-2-CP-0002.md`**
— the closure's retrospective.

## What was changed

**Configuration.** `.iacode/policies/providers.json` declares OpenAI beside DevWorld, Chat
Completions only, priority 50. `infra/compose/.env.example` and `docker-compose.yml` carry its two
variables; `docs/runbooks/MODEL-GATEWAY.md` documents them. No adapter, protocol or routing code
changed, and `model-routes.json` is untouched.

**`G2-F-009`.** `services/agent-runtime/.../protocol.py` refuses a wrong-typed `content` as
`content-not-a-string`, naming the JSON type it found; `context.py` states that `content` is one JSON
string. Two tests.

**`G2-F-010`.** `engine.py`, `services/orchestrator/.../workflows/agent_run.py` and
`apps/api/.../routes/agent_runs.py` write the terminal event before the terminal state; the API also
records `RUN_FAILED` when a workflow cannot start. Three tests, one of them structural over the
workflow's syntax tree.

**`G2-F-012`.** `scripts/iacode/gateway_smoke.py` waits for the Prometheus scrape, bounded by three
intervals, and asks only Prometheus. One test.

**`G2-F-013`.** `scripts/development-ledger/validate_checkpoint.py` binds a sealed state that kept the
symbolic `HEAD` to the checkpoint's own canonical tag; `seal_checkpoint.py` refuses to seal a state
that does not name its own tag. `docs/adr/ADR-0023-sealed-checkpoint-binds-its-own-tag.md` records
the decision and `docs/CHECKPOINT-PROTOCOL.md` states the rule. Three tests.

**`G2-F-014`.** `scripts/iacode/smoke.py` waits for both Prometheus targets within a bound;
`scripts/iacode/scenarios/fresh_install.py` names the smoke checks that fail. A syntax-tree scan of
every script that reads Prometheus, its null control, and one behavioural test per smoke.

**Memory.** `LSN-0047` to `LSN-0050`, `GRD-0049` to `GRD-0052`, the `LSN-0010`
recurrence, and `LESSONS.md` regenerated — it had not been rendered since `LSN-0036`.

**Chain.** `.iacode/anchors/checkpoint-chain.json` anchors `GATE-2-CP-0001`;
`docs/checkpoints/LATEST.md` names this checkpoint. `START-HERE.md` and `README.md` state the Gate's
status.

## What was deliberately not changed

`GATE-2-CP-0001` — sealed, and closed here rather than edited. No sandbox, no executor, no shell, no
filesystem tool, no Git tool. No route gained a candidate. `M1` stays `PENDING`.
