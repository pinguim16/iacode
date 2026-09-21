# Resume Validation

How to pick this checkpoint up cold, with no memory of the session that produced it, and confirm it
rather than believe it.

## The state to expect

| Field | Value |
|---|---|
| Gate | `SETUP-00` |
| Status | `MILESTONE_INDEPENDENT_AUDIT_PASS` |
| Branch | `main` |
| Base commit | `3f730dca1a12245ee8fdf8dfad7a523ed5c1c186` (`SETUP-00-CP-0012`) |
| Final reference | `refs/tags/iacode-checkpoints/SETUP-00-CP-0013` |
| Milestone | `M0` `PASSED` |
| Attestation | `.iacode/attestations/M0-CP-0013.json` |

`SECOND_TOOL_VALIDATION = PASSED`, by a fresh session of the same tool, provider and model as the
implementing run. That is session independence, not cross-tool validation, and
`crossToolValidation` is `NOT_AVAILABLE`.

## Cold start

```
git status --short --branch
git branch --show-current
git rev-parse HEAD
git rev-parse refs/tags/iacode-checkpoints/SETUP-00-CP-0013
python scripts/development-ledger/validate_checkpoint.py
```

The worktree must be clean, the branch `main`, and the tag must resolve to `HEAD`. Any divergence
stops the run and produces `DIVERGENCE.md`; it is not repaired silently.

## Confirm the verdict by derivation, not by reading it

```
python scripts/development-ledger/milestone_status.py --milestone M0
```

This re-verifies the attestation against the subject it names, the auditor that authored it, the
ancestry between them, and the four results a milestone pass requires. Reading
`STATE.json.milestone.status` is not confirmation; this command is.

## Clean clone

```
sh docs/checkpoints/SETUP-00-CP-0013/audit-harness/clean_clone.sh . SETUP-00-CP-0013
```

A fresh clone detached at this checkpoint's canonical tag, with no workspace state, re-running every
mandatory validation and the whole suite. The same script was used against the subject's tag during
the audit.

## Re-derive what this audit claims

```
python docs/checkpoints/SETUP-00-CP-0013/audit-harness/derive_expected.py --checkpoint SETUP-00-CP-0012
python docs/checkpoints/SETUP-00-CP-0013/audit-harness/resolve_evidence.py --checkpoint SETUP-00-CP-0012
python docs/checkpoints/SETUP-00-CP-0013/audit-harness/verify_memory.py
python docs/checkpoints/SETUP-00-CP-0013/audit-harness/probe_mirror.py . /tmp/probe.json
python docs/checkpoints/SETUP-00-CP-0013/audit-harness/attack_battery.py --json /tmp/battery.json
```

None of these imports the product tooling they check. The probe and the battery work in disposable
clones and change nothing.

## Known state that is not a defect

- The suite reports one skip in a sealed checkout,
  `AuditAttestationModelTests.test_an_unsealed_subject_is_rejected`. It needs an unsealed checkpoint
  directory, so it executes during any delivery and skips only at rest. See `REVIEW-REPORT.md` and
  `RISKS.md` `R4`.
- `COMMANDS.jsonl` keeps two failed attempts: `validate_checkpoint` and `check_completeness` run
  against this checkpoint before it carried its own artifacts. A failed attempt keeps its record so
  corrections stay visible.
- `verify_integrity.py` reports this checkpoint as the pending anchor. A checkpoint cannot anchor its
  own tag; its successor owes it.

## Post-seal validation

Recorded after sealing, from a clean checkout at the canonical tag, in `COMMANDS.jsonl` as the
`post-commit-validation` record `seal_checkpoint.py` wrote and bound to the sealed commit.
