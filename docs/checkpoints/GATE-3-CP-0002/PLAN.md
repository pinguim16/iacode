# Plan — M1 fresh-session milestone audit

Audit checkpoint `GATE-3-CP-0002`. Subject: the sealed `GATE-3-CP-0001`, the last Gate of `M1`,
together with the sealed Gates it builds on — `GATE-0-CP-0001`, `GATE-1-CP-0001`, `GATE-2-CP-0002`
(and the superseded `GATE-2-CP-0001`). This session implemented none of them. It changes no product
code: every file it writes is inside this checkpoint, its attestation, the integrity anchor it owes
its subject and `LATEST.md`.

The mechanism is `FRESH_SESSION_INDEPENDENT_AUDIT`: the same tool, provider and model as the
implementing runs, in a session with no memory of them. It is not cross-tool validation and is never
recorded as one.

## Frozen criteria

Written before any substantive execution, from the owner's mandate. No criterion is added, removed
or weakened after execution starts; a result is merged into the matrix from the execution record.

| # | Criterion | How it is judged |
|---|---|---|
| AM-01 | The four Gates are sealed and valid | every sealed M1 checkpoint validates detached at its own tag (`sealed_subjects.py`) |
| AM-02 | Integrity and tags are valid | `verify_integrity.py`; tags resolve to anchored commits; history attacks M1-M |
| AM-03 | The remote is synchronised | `remote_sync.py --tag` against the authorised remote; attack M1-N |
| AM-04 | Full verification is green | `verify.py` full, every stage, run by this session |
| AM-05 | A clean clone is green | a fresh clone of the remote: validation, integrity, full verification |
| AM-06 | The Foundation works | verification stages `stack`, `integration`, `infra`, `smoke`, `backup`, `restart`, `fresh-install` |
| AM-07 | The Gateway works | stages `gate:gatewayTests`, `gateway-smoke` (live provider) |
| AM-08 | The Agent Runtime works | stages `gate:agentRuntimeTests`, `agent-runtime-smoke`, `agent-durability`, `agent-cancellation`, `agent-deadline` |
| AM-09 | The Sandbox works | stages `gate:sandboxTests`, `sandbox-integration`, `sandbox-coding`, `sandbox-timeout`, `sandbox-cancellation`, `sandbox-recovery` |
| AM-10 | The cross-gate flow works | one live run: Task → Agent Runtime → Model Gateway → ToolRequest → Sandbox → ToolResult → Agent Runtime (`cross_gate_live.py`) |
| AM-11 | No tool runs on the host | host sentinel of the live run; attack M1-A |
| AM-12 | Host secrets are absent from a sandbox | attack M1-B |
| AM-13 | Workspaces are isolated | attack M1-E |
| AM-14 | Path traversal and link escapes are defended | attack M1-D |
| AM-15 | The engine socket is absent from an executed sandbox | attack M1-C; `R-G3-001-REVIEW.json` C2 |
| AM-16 | Git remote is not available to an agent | attack M1-H |
| AM-17 | No unresolved Critical/High finding | this review's findings, the Gates' open findings and risks |
| AM-18 | Completeness and evidence of the Gates are valid | each Gate's matrix recomputed from its tag: coverage and evidence 100% |
| AM-19 | `R-G3-001` is dispositioned from proof | `r_g3_001.py` ten controls and attack M1-G |
| AM-20 | The audit's own Red Team passes | fourteen cross-gate attacks over a valid null-mutation control |

## Order

1. Cold start, subject validation, anchor `GATE-3-CP-0001`, preflight (`independent-audit`), derived
   requirements.
2. Full verification of the audited tree (`cmd` recorded).
3. Sealed-subject validation, R-G3-001 probe, cross-gate live run.
4. The audit's Red Team (in-image and host halves) with its null-mutation control.
5. Clean clone of the remote: validation, integrity, full verification.
6. Review: findings with severity and disposition. Critical/High stops the audit at
   `REWORK_REQUIRED` and nothing of `GATE 4` starts.
7. Requirement matrix completed from evidence this audit resolved itself; Green Keeper;
   completeness; counts; internal mirror.
8. Attestation, milestone report, finalize at `MILESTONE_INDEPENDENT_AUDIT_PASS`, commit, seal, push
   the commit and the tag, remote synchronisation.
9. Review bundle ZIP.

## Stop conditions

- A Critical or High finding that is real: `REWORK_REQUIRED`, consolidated finding, review ZIP, stop.
- An untrusted input that reaches an arbitrary engine operation (`R-G3-001`): CRITICAL, stop.
- Divergence between the local history and `origin/main`, or a push that would need force: stop.
