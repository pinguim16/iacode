# Plan — GATE-3-CP-0003, the M1 corrective delivery

An implementing run. It corrects the three findings of the fresh-session `M1` audit
`GATE-3-CP-0002` (`M1-CP-0002`, `REWORK_REQUIRED`) and nothing else: no architecture change, no new
scope, no `GATE 4`. It closes at `READY_FOR_REVIEW`; `M1` stays unpassed until a new fresh-session
audit judges the corrected milestone.

## Inputs

- Owner authorisation for `GATE-3-CP-0003`: correct `M1-F-001`, `M1-F-002`, `M1-F-003`; atomic commits
  pushed to `origin/main`; a new published reference preserving
  `b59d66f9f3f9add2ae9dcd1cd4609fb4a1bf0b55`; no rewrite, no moved tag, no force push.
- During baseline the property behind `M1-F-003` was measured over the whole ledger
  (`SEALED-EVIDENCE-COMMITS-BASELINE.json`): three commits named by sealed evidence are local
  objects no published reference reaches — `b59d66f9f3f9` (`GATE-1-CP-0001`), `13ab172fcc06`
  (`SETUP-00-CP-0009`) and `643e721ee519` (`GATE-2-CP-0001`), each a replaced closure commit. The
  owner authorised publishing a preserved reference for all three (`DECISIONS.md` D-01).
- `.iacode/policies/audit-registry.json` registers `M1-CP-0002` as `NEXT.md` of `GATE-3-CP-0002`
  states; the derived requirement set is 139 canonical `GATE 3` rows, 53 lesson requirements and
  the three findings: 195 rows.

## Work, in commit order

1. **Preserve the published historical objects.** Three lightweight tags in a namespace of their
   own, `refs/tags/iacode-preserved/`, each naming exactly its commit; history scanned first; pushed
   without force; checked with `git ls-remote` and over the remote's transport
   (`REMOTE-PUBLISHED-OBJECTS.json`). Open the checkpoint, anchor `GATE-3-CP-0002`, register the
   audit, record `M1-F-003` as a `GUARDRAIL_FAILURE` of `GRD-0042` (`LSN-0040`), preflight,
   requirements.
2. **`M1-F-003` — the property, not the instance.** "Every object sealed evidence references is
   reachable from the published history." One definition in `ledger_common`: the published
   references (branches, tags, remote-tracking branches), `published_reachability`, and
   `published_clone` — a clone over Git's transport (`--no-local`) that carries only what those
   references reach. The validator refuses a record whose commit no published reference reaches,
   saying whether the object is absent or only a local unreachable object.
   `test_every_sealed_checkpoint_validates_from_its_own_tag`, `MIR-016`, the clean-clone copy and
   the Red Team fixture use the shared clone. `remote_sync.py` requires every local preserved and
   checkpoint tag to be on the remote at the same object. A fixture test fails on the old code:
   an orphan commit named by a sealed record, no published reference → FAIL, in the source and in
   a transport clone; a published reference → PASS.
3. **`M1-F-001` — the envelope shape.** One renderer in `protocol.py` derives the textual contract
   from `envelope_schema()` and the kind table the parser enforces: the version, every kind, a
   minimal valid example of `FINAL`, `MESSAGE` and `TOOL_REQUEST` with `tool.name` and
   `tool.arguments`. `runtime_instructions()` and `repair_instruction()` both carry it, because the
   instructions cannot know whether the gateway will honour native structured output; the parser
   refuses a key beside `name` and `arguments` in the tool object instead of dropping it. Tests
   A–E of the owner's mandate, then a live coding run with the configured model.
4. **`M1-F-002` — executor ownership.** A tool request records its executor when it is created:
   `SANDBOX` for a stage with a sandbox policy, `EXTERNAL` otherwise (migration `0005`, backfilled
   from the executions the sandbox recorded). The store takes the origin of a result as a
   parameter the caller cannot choose from the payload: the API passes `EXTERNAL`, the workflow's
   internal activity passes `SANDBOX`, and a result whose origin is not the request's executor is
   refused with `TOOL_RESULT_ORIGIN_REFUSED` before anything is stored — earlier or later than the
   sandbox's own result. A sandbox result delivered twice stays idempotent. The null-control
   scenario of the audit becomes a verification stage.
5. **Memory.** `LSN-0040` resolved in `GATE-3-CP-0003` with the repaired control; new lessons and
   guardrails for `M1-F-001` and `M1-F-002`.
6. **Closure.** Full verification; the Green Keeper; completeness; the internal Red Team with the
   new attacks; the mirror audit; a clean clone of the **remote** with the full verification and
   every sealed `M1` checkpoint validated from it; `M1-FINDINGS-CLOSURE.json`; finalize at
   `READY_FOR_REVIEW`, seal, push, synchronise; the review bundle.

## Stop conditions

`READY_FOR_REVIEW` is not declared if any preserved commit is not published, the clean clone of the
remote fails, a sealed `M1` checkpoint does not validate there, a finding stays open, the live
coding run of the configured model fails, a forged result is still accepted, a test or gate is red,
completeness is below 100%, the mirror fails, a guardrail failure is unresolved, the remote is not
synchronised or the review bundle is missing. A real external blocker yields `BLOCKED`.
