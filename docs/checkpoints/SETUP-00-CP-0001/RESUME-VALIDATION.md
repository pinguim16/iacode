# Resume Validation

## Result

A fresh Codex subagent received no conversation history and used only repository content. It reconstructed the checkpoint and executed the validator and Git comparison without editing files.

`SECOND_TOOL_VALIDATION = PENDING_MANUAL`

The subagent is another Codex session, not a genuinely independent provider or Claude Code. This result proves repository-only cold start within Codex but does not claim cross-tool validation.

## Reconstructed state

- Phase: `SETUP-00 — Development Control Plane`.
- Gate: `SETUP-00`.
- Status observed: `READY_FOR_REVIEW`.
- Branch: `main`, clean at the time of validation.
- Last commit observed: `0dc50fae803d6e8c13258fbe808e1af4cb6f4c10` (`setup: finalize review checkpoint`).
- Next step observed: reconcile the review handoff, complete independent review and Red Team, and perform a clean post-commit validation.
- Gate 0 status: not started and not permitted at the time of validation.

## Risks reconstructed

- Genuine validation by Claude Code or another provider remains pending.
- The review-stage `HANDOFF.md` still described the pre-commit state and required reconciliation during finalization.
- The schema validator implements the repository's used subset of JSON Schema, not the full specification.
- Secret scanning is defense in depth, not proof against every credential form.
- Tool adapters may drift from canonical contracts without review.
- No functional runtime exists.

## Validation commands executed

```text
python scripts/development-ledger/validate_checkpoint.py
git status --short --branch
git branch --show-current
git rev-parse HEAD
git show -s --format="%H%n%h %s%n%cI" HEAD
```

The checkpoint validator returned `CHECKPOINT_VALID` with exit code `0`; symbolic `HEAD`, branch, and clean state matched `STATE.json`.

## Exact manual second-tool procedure

1. Install or open an independently obtained Claude Code release in a clean clone of this repository.
2. Give it only `prompts/RESUME-WORK.md`; do not provide this conversation.
3. Require it to read `START-HERE.md`, `LATEST.md`, and the full checkpoint.
4. Require it to run the checkpoint validator and Git commands above without modifying files.
5. Compare its reconstructed phase, Gate, status, resolved commit, next action, risks, and validation commands with this document.
6. Record tool version, provider, model exposure, effort exposure, results, and any divergence in a new checkpoint. Do not silently alter this historical result.
