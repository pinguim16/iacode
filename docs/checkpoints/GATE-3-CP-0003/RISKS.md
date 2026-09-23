# Risks — GATE-3-CP-0003 (M1 corrective delivery)

The register the M1 audit consolidated (`GATE-3-CP-0002/RISKS.md`), carried forward so no risk of
the milestone is dropped between checkpoints (`M1-O-002`), with what this delivery changed.

## Closed by this delivery

**M1-F-003 — The published history cannot validate GATE-1-CP-0001.** Closed. The three replaced
closure commits sealed evidence names are kept by published tags under
`refs/tags/iacode-preserved/`; validation refuses a checkpoint whose evidence names a commit no
published reference reaches; every control over sealed history clones the published history; a
clean clone of the remote passes the full verification and validates every sealed M1 checkpoint
(`M1-FINDINGS-CLOSURE.json`).

**M1-F-001 — A model is never shown the shape of a tool request.** Closed. The configured model
now makes valid tool requests that execute in the sandbox (`LIVE-CODING-RUN.json`).

**M1-F-002 — A tool result for a sandboxed request is accepted from the API.** Closed. Refused
`403 TOOL_RESULT_ORIGIN_REFUSED` before anything is stored, attacked on the stack by
`sandbox-tool-result-origin` and by the Red Team's `G3-Y`.

## Open

**R-G2-009 — A provider credential was shared in a chat transcript during the Gate 2 closure.**
HIGH until rotated. Outside the repository; this delivery did not look for, display or use any old
value. The live run used the credential configured on this machine, which the provider accepted.
**Owner action**: rotate the key and set the new one only in `infra/compose/.env`.

**R-G3-001 — The sandbox service holds the container engine's socket.** HIGH in its register;
disposition `ACCEPTED_LOCAL_ARCHITECTURAL_RISK` (M1 audit, ten proved controls). Unchanged.

**R-G3-009 — The configured model makes valid tool requests but does not finish a coding task
within its budget.** MEDIUM, new. In the live run `openai:gpt-4o-mini` made eleven valid requests,
all executed, with no repair, then rewrote the same file six times without re-running the tests
and ended `BUDGET_EXCEEDED` at twelve turns. The protocol is no longer the obstacle; the model's
skill and the turn budget are. Tracked with `R-G2-008`; a stronger configured model or a larger
budget is the owner's choice, not a protocol change.

**R-G3-010 — A pre-push check narrower than the change's reach.** MEDIUM. `LSN-0054` recurred:
`3101d31` reached the remote with the lint gate red; the next commit restored it. The lesson stays
`CONFIRMED` — no automated control forces the pre-push gates — and the Green Keeper's full cycle
at closure is what catches a gate left red.

**R-G3-011 — "Published" is judged locally.** LOW. The validator treats branches, tags and
remote-tracking branches of the repository it runs in as published; a local tag that was never
pushed would satisfy it on that machine. `remote_sync.py` now refuses a local checkpoint or
preserved tag missing from the remote, which closes the gap at the moment a delivery claims
synchronisation.

**R-G3-002, R-G3-005, R-G3-007, R-G2-003, R-G2-004, R-G2-008** — MEDIUM, unchanged: a kernel shared
with the host, unscanned image packages, the pre-push discipline as a practice, unbounded
`run_events`, the effects protocol and the activity set, one provider account for all live evidence.

**R-G3-003, R-G3-004, R-G3-006, R-G2-006, R-G2-007, R-G2-013, M1-O-003** — LOW, unchanged.

**The local references `refs/iacode-preserved/*`.** They protected the three commits from garbage
collection before the tags were published. They are kept, as the owner asked, until the correction
is validated by the next audit; they publish nothing and change no published reference.

## Residual limits of the corrections

- `M1-F-002`: under the M1 trust model Temporal is internal; a local process able to schedule the
  worker's activities directly could still act as the sandbox. The public door is closed.
- `M1-F-001`: whether a given model follows the contract is measured by live runs, not guaranteed.
- `M1-F-003`: a published reference can be deleted on the remote by someone with write access;
  `remote_sync.py` and `test_every_preserved_reference_is_what_makes_its_checkpoint_valid` then fail.
