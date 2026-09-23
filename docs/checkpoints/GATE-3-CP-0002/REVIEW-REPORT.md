# Review Report — M1 fresh-session milestone audit

- Audit checkpoint: `GATE-3-CP-0002`
- Subject: `GATE-3-CP-0001`, sealed at `3bc8e9d8a94d44163d1af9325ad5b2272f71f8ed`, with the sealed
  Gates it builds on: `GATE-0-CP-0001`, `GATE-1-CP-0001`, `GATE-2-CP-0001`, `GATE-2-CP-0002`
- Milestone: `M1 — IACode V0 foundation` (`GATE 0` to `GATE 3`)
- Mechanism: `FRESH_SESSION_INDEPENDENT_AUDIT` — Claude Code, Anthropic, `claude-opus-5-5`, a session
  with no memory of the implementing runs. Not cross-tool validation.
- Verdict: **`REWORK_REQUIRED`**. One HIGH finding (`M1-F-003`) fails two frozen criteria; two
  MEDIUM findings go with it to the corrective delivery. `GATE 4` does not start.

## Scope and method

The audit judged the milestone as a whole — whether the four Gates work *together* and whether what
was published can be verified — rather than re-running each Gate's review. Every verdict below comes
from something this session executed:

| Evidence | What it showed |
|---|---|
| `SEALED-SUBJECTS.json`, `cmd-0010` | from worktrees of this repository, the five sealed M1 checkpoints validate detached at their tags (5/5) |
| `SEALED-SUBJECTS-PUBLISHED.json`, `cmd-0029` | from a clone of the **published** remote, `GATE-1-CP-0001` does not (4/5) — `M1-F-003` |
| `CLEAN-CLONE-REPORT.json`, `cmd-0023` | a fresh clone of the remote passes 30 of 31 verification stages and fails `gate:tests` on the same checkpoint |
| `cmd-0003`, `cmd-0007`, `cmd-0009` | the integrity chain (18 anchors), the remote (`origin/main` and the subject tag), the whole history scanned clean |
| `VERIFICATION-REPORT.json`, `cmd-0012` | the full verification of this repository, 31 of 31 stages, the live gateway and runtime smokes and every sandbox scenario included |
| `CROSS-GATE-LIVE.json`, `cmd-0016` | one live run crossing every Gate: Task → Agent Runtime → Model Gateway → ToolRequest → Sandbox → ToolResult → Agent Runtime |
| `R-G3-001-REVIEW.json`, `cmd-0011` | the ten controls that bound the engine socket |
| `M1-INTERNAL-RED-TEAM.json`, `RED-TEAM-REPORT.md` | fourteen cross-gate attacks over a valid null-mutation control, 14/14 defended |
| `FORGED-RESULT-PROBE.json`, `cmd-0019` | `M1-F-002`, reproduced with a null control |
| `FINAL-M1-AUDIT-MATRIX.json` | the twenty criteria frozen in `PLAN.md` before execution, each computed from those artifacts |

## Findings

### M1-F-003 — HIGH — The published history cannot validate GATE-1-CP-0001, so every clean clone of the remote fails the mandatory tests gate

The full verification of a fresh clone of `https://github.com/pinguim16/iacode.git` passed 30 of 31
stages and failed `gate:tests` (`cmd-0023`):
`test_every_sealed_checkpoint_validates_from_its_own_tag` fails for `GATE-1-CP-0001` with
`COMMANDS.jsonl:84: the record claims a clean tree at b59d66f9f3f9 but the input
scripts/development-ledger/validate_checkpoint.py does not exist there`. Validating every sealed M1
checkpoint from a clone of the remote reproduces it on its own (`cmd-0029`, 4/5). In this working
repository the same checkpoint validates (`cmd-0010`, 5/5).

Root cause: the sealed ledger record `cmd-0086` of `GATE-1-CP-0001` names commit
`b59d66f9f3f9add2ae9dcd1cd4609fb4a1bf0b55` — a first version of the Gate 1 closure commit, replaced
before the history was published — and binds its inputs to that commit. No published reference
reaches it: it survives only as an unreachable object in this machine's object store. A clone over a
transport (the remote, or `git clone --no-local`) does not carry it; a clone of the local path with
`--no-hardlinks` copies the object store wholesale and does. Every control that checks sealed
history — `test_every_sealed_checkpoint_validates_from_its_own_tag`, the mirror audit's `MIR-016`,
the Gate batteries — clones the local path, so none of them could see it, and a `git gc` would make
this repository fail the same way.

Severity rationale: HIGH, for the reason the repository has applied twice to the same class —
`G1-F-007` and `G2-F-013`, each a sealed checkpoint that did not validate from its own tag. It is
also a guardrail failure: the control that exists for this class clones in a way that cannot see it.
Two frozen criteria fail on it: AM-01 (the Gates sealed and valid) and AM-05 (a clean clone is
green).

Required correction: make the sealed content verifiable from the published history **without
rewriting it** — a published reference that preserves the commit the record names — and repair the
guardrail so sealed history is checked through a transport clone that carries only published objects,
with a test that fails on an unreachable object; then re-run the clean clone of the remote.

### M1-F-001 — MEDIUM — A model is never shown the shape of a tool request, and the configured live model cannot make one

Four live coding runs through the deployed stack. With the operator's configured model
(`openai:gpt-4o-mini`) the developer never produced a valid tool request: the arguments were written
at the top of the envelope, then under `args` after the one repair (`cmd-0014`, `cmd-0015`). With an
explicitly chosen model (`openai:gpt-4.1-mini`, `cmd-0016`) two requests were valid and executed in
the sandbox, and then the same failure ended the run. No run completed the task.

Root cause: `runtime_instructions()` says only that `"tool" carries its name and arguments`, and
never names the `name` and `arguments` keys; `repair_instruction()` restates the kinds but not the
shape. `envelope_schema()` calls itself "the documentation of what the prompt asks for" when native
structured output is not requested, but it reaches a model only as a structured-output schema, which
is requested only for a model whose capability is known — and every capability of the configured
provider is `UNKNOWN`.

Severity rationale: every other dimension of the crossing holds; the parser refused every malformed
request and nothing malformed was executed; a capable model did produce valid requests; the
correction is to the instructions the runtime sends. The counter-argument — that the product's
central flow cannot complete with the configured model — is why the finding is mandatory corrective
work rather than backlog.

Required correction: the runtime states the exact envelope of every kind, the tool object's keys
included, whenever native structured output is not requested; the repair restates the shape; and a
live coding run with the configured model executes its tools.

### M1-F-002 — MEDIUM — The API accepts a tool result for a request the sandbox is executing, and the agent receives it instead of the sandbox's

Deterministic `timeout` scenario (`cmd-0019`). Null control: the developer receives the sandbox's
`TIMED_OUT` result and answers `TIMEOUT-SEEN`. Mutation: while the sandbox runs the command, a
`SUCCEEDED` result for the same request is posted to `POST /api/v1/agent-runs/{run}/tool-results`
and answered `200`; the stored result is the forged one, the sandbox's own execution record still
says `TIMED_OUT`, and the developer answers `TIMEOUT-NOT-SEEN`.

Root cause: `resolve_tool_request()` accepts any `PENDING` request of the run whatever its executor,
and `_execute_in_sandbox()` resumes the agent with the stored result, which answers a second
delivery with the first one.

Severity rationale: an integrity gap on the boundary the next Gates build on, reachable only from
the local machine under the M1 trust model (an unauthenticated API bound to loopback), with no
isolation or credential impact.

Required correction: a tool result for a request of a stage with a sandbox policy is accepted only
from the sandbox, and the refusal is attacked with a null control.

## Observations

These are recorded, not raised as findings.

- **M1-O-001.** `GATE-0-CP-0001` and `GATE-2-CP-0001` do not pass the validator of their own revision
  (`G1-F-007`, `G2-F-013`); both defects were repaired in the tooling by the following Gates, and the
  current validator accepts them from their tags, which is the repository's rule.
- **M1-O-002.** Open risks are not carried from one Gate's register to the next: `GATE-3-CP-0001` is
  silent on `R-G2-003` to `R-G2-013`. `RISKS.md` here consolidates them, states the three `GATE 3`
  closed without saying so, and hands `R-G2-009` — a credential exposed outside the repository —
  to the owner, because no repository control can close it.
- **M1-O-003.** A fresh installation starts with an empty model catalog, and the first live run
  fails until the operator synchronises it (`cmd-0013`).
- **M1-O-004.** `R-G3-001` is bounded by ten proved controls and one attack; disposition
  `ACCEPTED_LOCAL_ARCHITECTURAL_RISK`, backlog a rootless engine or a restricted socket proxy.
- **M1-O-005.** The live evidence of the whole milestone rests on one provider account (`R-G2-008`);
  the audit's three live runs that reached a model spent 5,885 tokens in six calls on the configured
  model and 8,469 tokens in seven calls on the explicitly chosen one.

## The frozen criteria

`FINAL-M1-AUDIT-MATRIX.json` computes each row from the artifacts and is the authoritative statement;
in summary, sixteen of the twenty criteria hold and four fail, all on `M1-F-003`: AM-01 (a sealed
Gate does not validate from the published history), AM-05 (the clean clone's mandatory tests gate),
AM-17 (an unresolved HIGH) and AM-18 (that Gate's evidence does not resolve from the published
history). The isolation claims of the milestone (AM-11 to AM-16), its cross-gate flow (AM-10), the
full verification of this repository (AM-04), `R-G3-001` (AM-19) and the audit's Red Team (AM-20)
all hold.

## Verdict

`REWORK_REQUIRED`. The attestation `.iacode/attestations/M1-CP-0002.json` records the audit with
`reviewResult: REWORK_REQUIRED`, and `milestone_status.py --milestone M1` refuses to derive a pass
from it. `M1` stays unpassed, and by the owner's rule `GATE 4` does not start. The three findings
return to the implementer: the corrective delivery `GATE-3-CP-0003` registers this audit, closes
every finding, and a new fresh-session audit judges the corrected milestone.
