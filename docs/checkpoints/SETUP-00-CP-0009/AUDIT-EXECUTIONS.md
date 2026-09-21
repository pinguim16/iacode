# Audit Executions — SETUP-00-CP-0009

Everything this audit claims was executed. The machine-readable record is
`AUDIT-EXECUTIONS.json`; the scripts that produced it are in `audit-harness/`, copied into this
checkpoint so the audit reproduces from a clean clone. They resolve the repository from their own
location, or from `IACODE_ROOT`, and write their output to the directory given as the first
argument.

## Safety

Every negative scenario ran inside a disposable clone, a temporary Git repository or an in-memory
copy. No tag, commit, sealed checkpoint or canonical memory file of the real repository was written
to by any attack. The two writes this audit made to the repository outside its own checkpoint are
`docs/checkpoints/LATEST.md`, which every checkpoint updates, and
`.iacode/anchors/checkpoint-chain.json`, which the checkpoint protocol requires a successor to
extend for its sealed predecessor.

## Cold start

Read from the repository, in this order: `START-HERE.md`, `AGENTS.md`, `CLAUDE.md`,
`docs/DEVELOPMENT-CONTRACT.md`, `docs/MASTER-PLAN.md`, `docs/ROADMAP.md`,
`docs/DEFINITION-OF-DONE.md`, `docs/QUALITY-GATES.md`, `docs/HANDOFF-PROTOCOL.md`,
`docs/CHECKPOINT-PROTOCOL.md`, `docs/SETUP-00-CHECKLIST.md`, `docs/ENGINEERING-MEMORY.md`,
`docs/MILESTONE-VALIDATION.md`, `docs/checkpoints/LATEST.md`, then `SETUP-00-CP-0007` and
`SETUP-00-CP-0008` in full, then `ADR-0010`, the policies, the schemas that matter to the controls
under audit, the engineering memory, the guardrail registry and the anchor chain. No external
summary was used as evidence anywhere in this audit.

## Baseline

The working tree carried an unsealed, uncommitted `SETUP-00-CP-0009` scaffold from an earlier
interrupted attempt at this audit: a 98-row matrix with every row `NOT_STARTED` and no evidence. It
was copied to the session scratchpad, removed, and `docs/checkpoints/LATEST.md` restored, so the
audit started from a clean worktree at `c53f4c59a77870414324efa6b5f61b35d26c5090`. That is recorded
in `DECISIONS.md` rather than passed over.

With the worktree clean, `validate_checkpoint.py` returned `CHECKPOINT_VALID` for
`SETUP-00-CP-0008` on the branch, and again from a clone detached at
`refs/tags/iacode-checkpoints/SETUP-00-CP-0008`.

## Harness design, and the two things it got wrong first

A rejection only means something if it is attributable to the mutation under test. The first
revision of the attack harness failed that standard twice, and both are recorded here because an
audit that hides its own corrections is not evidence:

1. It committed each mutation as a new commit, which broke the seal-chronology control
   independently of the mutation. Every attack still reported `DEFENDED`, for the wrong reason.
   The harness now performs a faithful two-commit re-seal, exactly as `seal_checkpoint.py` does.
2. Its reset restored only the checkpoint's own tag, so an attack that moved a historical tag
   poisoned every later attack. The harness now captures and restores every namespaced tag.

Both are classified `AUDIT_ENVIRONMENT` and were repaired in the audit harness only. Nothing in the
product was changed. The control that makes the corrected results checkable is a null mutation
through the identical path, which validates: `CHECKPOINT_VALID`. Every result reported in
`RED-TEAM-REPORT.md` comes from the corrected harness.

The assurance-scenario harness carries the same kind of control: `BASE-001`, an unmutated
consistent copy of the delivery, is accepted by the delivery-assurance, memory, internal-assurance
and quality-evidence validators.

## What was executed

| Area | Harness | Result |
|---|---|---|
| Expected requirement set, re-derived without `policies.py` | `derive_expected.py` | 131 expected, 131 declared, 0 missing, 0 unexpected, 0 duplicated |
| Mandatory and additional attack battery | `attacks.py`, `fixture.py` | 52 attacks defended, 1 positive control refused |
| External PASS reachability | `ext_reachability.py` | no reachable state; finding `CP9-F-001` |
| Attestation rules, one at a time | `run_attestation.py` | 14 refusals correct, 1 positive control accepted |
| Delivery assurance, completeness, evidence, staleness | `run_scenarios.py`, `scenarios.py` | 33 refusals correct over an accepted baseline |
| Preflight freshness | `run_preflight.py` | 6 mutations, stored preflight stale and regenerated preflight fresh in each |
| The four previously bypassed guardrails | `run_guardrails.py` | 4 originals and 4 variations blocked |
| Engineering memory and guardrail effectiveness | `run_memory.py` | 22/22/22/22, 0 unresolved failures, agreeing with the product and the state |
| History and tag integrity | `run_history.py` | 7 mutations refused; 7 sealed checkpoints intact read-only |
| Semantic counts, commands, documentation | `run_counts_docs.py` | 18 comparisons, 0 mismatches; 39 links, 0 broken |
| Command auditability and replay | `run_commands.py` | 60 records complete, 6/6 safe replays reproduce |
| Successor suite simulation | recorded in `AUDIT-EXECUTIONS.json` | finding `CP9-F-002` |

## The subject's own handoff commands

All fifteen validation commands in `SETUP-00-CP-0008`'s `HANDOFF.md` were executed in a clean clone
detached at the sealed tag. `derive_requirements.py` reported 131, `m0_mirror_audit.py
--clean-clone` reported `INTERNAL_MIRROR=PASS passed=18/18`, and `m0_red_team.py` reported
`INTERNAL_RED_TEAM=RED_TEAM_PASS defended=46/46 mandatory=26/26`. Those are the delivery's own
tools; they corroborate this audit's independent battery rather than substituting for it.

## The eleven findings of SETUP-00-CP-0007

For each finding the audit read the closure record, read the named regression and negative tests in
their source rather than by name, confirmed that the test reproduces the original defect, and
executed it. The 53 distinct tests named by `CP7-FINDINGS-CLOSURE.json` ran together in a clean
clone: 53 of 53 passed in 76.3 s. The corresponding attacks were then re-run independently by this
audit's own harness.

## Test failure policy

- `PRODUCT_DEFECT`: the suite regression that anchoring the sealed predecessor produced. Left red.
  Recorded as `FAIL` in `QUALITY.json` and as finding `CP9-F-002`. No test was edited.
- `AUDIT_ENVIRONMENT`: the two harness defects described above. Repaired in the harness only.
- `FLAKY_OR_NONDETERMINISTIC`: none observed. No command was re-run until it turned green.

## Residual limits of this audit

- Same tool and same provider as the implementing run. `crossToolValidation` is `NOT_AVAILABLE`.
- The attack battery is large but finite; a defended attack is evidence about that attack.
- The integrity anchors and the attestation are tamper-evident inside the local trust model, not
  cryptographic. An actor controlling the repository can recompute both. This audit reproduces that
  limit rather than disproving it.
