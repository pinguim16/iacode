# Milestone Report — M1, IACode V0 foundation

`M1` groups `GATE 0 — FOUNDATION`, `GATE 1 — MODEL GATEWAY`, `GATE 2 — AGENT RUNTIME` and
`GATE 3 — SANDBOX + TOOL EXECUTION`. This report is the consolidated statement the milestone audit
produces for the group, as `docs/MILESTONE-VALIDATION.md` requires. It is written by the fresh-session
audit in `GATE-3-CP-0002`, about sealed content; nothing it describes was implemented by this run.

## Verdict

**`REWORK_REQUIRED` — `M1` is not passed.** The attestation `.iacode/attestations/M1-CP-0002.json`
(`FRESH_SESSION_INDEPENDENT_AUDIT`, cross-tool execution available and not used by mandate) records
review `REWORK_REQUIRED`, Red Team `RED_TEAM_PASS`, completeness and evidence of this checkpoint
100%, and tests `FAIL`: a clean clone of the published remote fails the mandatory tests gate. One
HIGH finding (`M1-F-003`) and two MEDIUM (`M1-F-001`, `M1-F-002`) return to the implementer in the
corrective delivery `GATE-3-CP-0003`, and a new fresh-session audit judges the corrected milestone.
By the owner's rule, `GATE 4` does not start.

## The Gates and their internal verdicts

| Gate | Sealed checkpoint | Commit | Status | Requirements | Tests counted at the seal |
|---|---|---|---|---|---|
| GATE 0 — Foundation | `GATE-0-CP-0001` | `195739f` | `INTERNAL_GATE_PASS` | 118, 100% | 580 |
| GATE 1 — Model Gateway | `GATE-1-CP-0001` | `4de6b2f` | `INTERNAL_GATE_PASS` | 161, 100% | 893 |
| GATE 2 — Agent Runtime | `GATE-2-CP-0001` | `424650d` | `BLOCKED`, superseded | — | — |
| GATE 2 — Agent Runtime | `GATE-2-CP-0002` | `d4a3998` | `INTERNAL_GATE_PASS` | 186, 100% | 1,232 |
| GATE 3 — Sandbox | `GATE-3-CP-0001` | `3bc8e9d` | `INTERNAL_GATE_PASS` | 192, 100% | 1,502 |

Each was validated by this audit detached at its own tag. From this repository all five validate and
each Gate's matrix recomputes complete — 657 requirements across the milestone
(`SEALED-SUBJECTS.json`). From a clone of the published remote, `GATE-1-CP-0001` does not validate:
one of its sealed ledger records binds its inputs to a commit no published reference reaches
(`SEALED-SUBJECTS-PUBLISHED.json`, `M1-F-003`).

## Cross-Gate integration

What no single Gate could show on its own:

- **Task → Agent Runtime → Model Gateway → ToolRequest → Sandbox → ToolResult → Agent Runtime** in
  one live run (`CROSS-GATE-LIVE.json`, `cmd-0016`): seven model calls through
  `/api/v1/gateway/infer`, tool requests executed in a sandbox session of the run, their results
  resolved and delivered, the model called again after a sandbox result, no sandbox left behind, and
  a sentinel file on the host byte-identical afterwards.
- **What was published cannot yet be verified on its own** (`M1-F-003`): every clean clone of the
  remote fails the mandatory tests gate on `GATE-1-CP-0001`, a failure no local control could see
  because every one of them clones the local path, which carries unreachable objects.
- **The live model's side of the crossing is where the product is weakest** (`M1-F-001`): the
  configured model never forms a valid tool request, because the runtime never shows it the tool
  object's keys.
- **The boundary between the runtime and the sandbox has a second door** (`M1-F-002`): the API
  accepts a result for a request the sandbox is executing, and the agent receives it.
- **Nothing an agent asks for runs outside its sandbox**, re-attacked by this audit on the real
  engine: host execution, secrets, the engine socket, workspace escapes, another run's workspace,
  policy escalation, engine arguments from a request, the Git remote and network egress — 9/9.
- **The runtime reaches a model only through the gateway**: forged provider fields refused `422`, no
  provider variable in the worker, the sandbox or the web, no provider module below the gateway
  (`M1-J`).
- **Durable lifecycle across the Gates**: cancellation stops the sandboxed command and leaves no
  sandbox (`M1-K`), a run past its deadline is ended (`M1-L`), and the verification's durability and
  recovery scenarios pass.

## Tests and regressions

The full verification of this repository passed 31 of 31 stages (`cmd-0012`, 27 minutes). A fresh
clone of the public remote passed 30 of 31 and failed `gate:tests` (`CLEAN-CLONE-REPORT.json`,
`M1-F-003`); every other stage, the live ones and the fresh installation included, passed there too.
The image suites and the infrastructure suite passed (`cmd-0027`, `cmd-0028`), and this checkpoint's
Green Keeper ran the twelve mandatory gates (`REWORK-LOG.jsonl`); the counts are derived in
`COUNTS.json`. No regression of the product was found.

## Architecture

Sixteen decisions record the milestone's structure, `ADR-0012` to `ADR-0027`: the runtime stack
and its boundaries, the gateway as an inward-pointing library, tri-state capabilities, the streaming
commitment point, credentials named rather than stored, the runtime as a library over Temporal, the
tool-request boundary, the strict envelope, the self-binding seal, the public atomic history, the
sandbox isolation boundary, per-run workspaces and the canonical tool policy. The audit found them
implemented as recorded, with one gap between a statement and the code: `envelope_schema()`
describes itself as the prompt's documentation of the envelope and is not in the prompt
(`M1-F-001`).

## Engineering memory

54 lessons (31 from `SETUP-00`, 4 from `GATE 0`, 5 from `GATE 1`, 10 from `GATE 2`, 4 from
`GATE 3`), 51 `GUARDED`, 3 `CONFIRMED`; 55 guardrails, every one resolved, tested and effective, and
no `GUARDRAIL_FAILURE` recorded (`validate_lessons.py`, `cmd-0006`). `M1-F-003` is one the memory
does not yet record: the control that guards sealed history against a checkpoint that does not
validate from its tag let this one through, because it clones the local path. Recording it, and
repairing the control, belongs to the corrective delivery. The audit ran under a preflight scoped
`independent-audit` that applied all 54 lessons.

## Open risks and technical debt

The consolidated register is `RISKS.md`. The headline items:

- `R-G3-001` — the engine socket: `ACCEPTED_LOCAL_ARCHITECTURAL_RISK`, ten controls proved; backlog a
  rootless engine or a restricted socket proxy.
- `R-G2-009` — a credential exposed outside the repository: **owner action**, rotate it.
- `M1-F-003` — HIGH, the published history cannot validate `GATE-1-CP-0001`; corrective delivery
  `GATE-3-CP-0003`. Keep `refs/iacode-preserved/b59d66f9f3f9` until it is corrected.
- `M1-F-001`, `M1-F-002` — MEDIUM, in the same corrective delivery.
- A kernel shared with the host, unscanned image packages, a pre-push discipline that is a practice,
  unbounded event history, no retention of sandbox rows — MEDIUM or LOW, backlog.

## Provenance and rights

Every artifact of the milestone is project-owned and repository-generated. `trainingAllowed` is
`false` everywhere: in every checkpoint's provenance, in every lesson, and at the database level in
`experiences`. The live runs of this audit stored no prompt, no completion and no credential:
`model_calls` has no column that could hold one.

## Cost and model usage

The milestone's live evidence rests on the operator's OpenAI account (`R-G2-008`). This audit's live
runs that reached a model spent 5,885 tokens in six calls on the configured `openai:gpt-4o-mini` and
8,469 tokens in seven calls on the explicitly chosen `openai:gpt-4.1-mini`; the provider reports no
price through the catalog, so the cost is recorded as unknown rather than estimated.
