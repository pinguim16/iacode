# Status

INTERNAL_GATE_PASS

## Why

GATE 2 — AGENT RUNTIME was delivered and sealed `BLOCKED` in `GATE-2-CP-0001`, because rows 19.1,
19.2 and 19.5 of `docs/GATE-2-CHECKLIST.md` need a live model call and DevWorld's quota was
exhausted. This checkpoint is the closure: the sealed checkpoint is untouched and anchored, and the
three requirements are satisfied here by live evidence recorded in this checkpoint's own ledger.

The operator registered OpenAI as a second provider, by configuration only, and pointed the live
smoke at `openai:gpt-4o-mini`. That decision is the operator's and is recorded in `DECISIONS.md`;
the smoke model was named explicitly and never substituted, and no check was changed to accept it.

The live runs found real defects before they passed, and each was repaired rather than retried
until green: `G2-F-009` (a refusal that named the wrong defect), `G2-F-010` (a terminal state
visible before its terminal event) and `G2-F-012` (a metric read before the scrape that carries it).
Anchoring the sealed checkpoint exposed a fourth, `G2-F-013`: sealed at `BLOCKED` with the symbolic
`HEAD`, it had never been valid from its own tag. The operator decided to repair the tooling rather
than hold the Gate (`ADR-0023`). The full verification then exposed `G2-F-014`: `G2-F-012`'s race in
the Foundation smoke after a fresh installation, which `GRD-0051` had not covered — a
`GUARDRAIL_FAILURE` against `LSN-0049`, resolved here by widening the control to the class.

## What is green

- The live evidence: the gateway smoke `cmd-0005`, the agent runtime smoke `cmd-0006`, the persisted provenance `cmd-0007`.
- 186 of 186 requirements complete, 100% of evidence references resolving (`cmd-0069`).
- 1,232 of 1,232 discovered test cases executed and passed: 578 in the ledger and
  Gate suites (`cmd-0056`), 606 in the image suites (`cmd-0013`) and 48 in the
  live infrastructure suite (`cmd-0014`).
- The internal Red Team battery, unchanged, re-executed after the repairs (`cmd-0021`).
- The Green Keeper green on every mandatory gate (`cmd-0056`), and the full verification
  passing all of its stages, the fresh installation included (`cmd-0067`).
- 52 of 52 guardrails effective and 48 of 50 lessons guarded.

## What is not

Nothing this Gate specifies. The independent validation of the milestone belongs to `M1`, which is
audited by a fresh session after GATE 3 and stays `PENDING`.
