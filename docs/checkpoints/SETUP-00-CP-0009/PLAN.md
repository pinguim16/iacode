# Plan — SETUP-00-CP-0009

Role: milestone independent auditor. Mechanism: `FRESH_SESSION_INDEPENDENT_AUDIT`.
Subject: `SETUP-00-CP-0008`. No product code, test, policy, schema, canonical memory, sealed
checkpoint or historical tag may be changed by this run.

1. Cold start from the repository alone: the canonical documents, `SETUP-00-CP-0007` in full, and
   `SETUP-00-CP-0008` in full.
2. Baseline: Git state, checkpoint validation on the branch and from a detached clone of the
   subject's tag, and the full suite in a clean clone.
3. Write the audit matrix before any substantive step, with every row `NOT_STARTED`.
4. Re-derive the expected requirement set independently and compare it with the declared set.
5. Re-verify all eleven `SETUP-00-CP-0007` findings by reading and executing their regression tests.
6. Execute the twenty-six mandatory attacks and the additional attacks with the auditor's own
   harness, against a faithfully re-sealed disposable clone, with a null-mutation control.
7. Audit the surfaces this delivery introduced, including the positive path of each control.
8. Recompute the engineering memory, the guardrail effectiveness, the semantic counts, the command
   ledger, the history integrity and the documentation links.
9. Reproduce the four previously bypassed guardrails and a variation of each.
10. Execute every mandatory validator, and the subject's own handoff commands, in a clean clone.
11. Anchor the sealed predecessor, which this checkpoint owes it.
12. Record a consolidated finding package, lesson candidates, and a binary verdict.
13. Seal, then validate the sealed content from a clean detached checkout.

Stop conditions: unexpected Git divergence, a need to modify a sealed checkpoint or move a
historical tag, secret exposure, or any request to begin Gate 0.
