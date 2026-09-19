# Checkpoint Template

A checkpoint contains `STATUS.md`, `HANDOFF.md`, `RUN-METADATA.json`, `STATE.json`, `PLAN.md`, `DECISIONS.md`, `COMMANDS.jsonl`, `FILES.json`, `TESTS.json`, `QUALITY.json`, `PROVENANCE.json`, `DIFF-SUMMARY.md`, `RISKS.md`, and `NEXT.md`.

Create it with `new_checkpoint.py`, populate only observed evidence, finalize it with `finalize_checkpoint.py`, and accept it only after `validate_checkpoint.py` exits zero.
