# Plan — GATE-2-CP-0002

The closure of GATE 2 from `GATE-2-CP-0001`, sealed `BLOCKED`. The Gate's plan is that checkpoint's
`PLAN.md`; this one covers only what the closure does, in order, and what makes each step
verifiable.

1. Validate the sealed state: `validate_checkpoint.py`, `validate_lessons.py`,
   `verify_integrity.py`, and Git against `STATE.json`.
2. Obtain the live evidence against the model the operator configures, never a substituted one:
   `gateway_smoke.py` and `agent_runtime_smoke.py` report `PASS`, and the persisted provenance of
   the live call names provider, model, endpoint and model call with no content.
3. Repair every defect a live run exposes, with a test that fails on the code it replaces, and
   record each as a lesson with a guardrail. Never retry a live run until it is green.
4. Anchor `GATE-2-CP-0001`, refresh the lesson preflight, derive the requirement set and declare it
   with this checkpoint's evidence; the completeness audit reaches 100%.
5. Execute every counted suite, the internal Red Team battery unchanged, the Green Keeper over every
   mandatory gate, the full verification, and the internal mirror.
6. Finalize at `INTERNAL_GATE_PASS`, commit, seal, and validate from the sealed content.

Stop conditions: the configured model does not answer (the Gate stays `BLOCKED`), a mandatory gate is
red (repair it), or anything of GATE 3.
