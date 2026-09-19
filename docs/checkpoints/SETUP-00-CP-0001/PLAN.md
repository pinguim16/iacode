# SETUP-00 Execution Plan

## Objective

Establish the tool-neutral development control plane and Engineering Ledger for IACode without implementing any Gate 0 runtime functionality.

## Baseline

- Baseline classification: `EMPTY_PROJECT`.
- Initial Git state: no repository and no files.
- Repository initialized on branch `main` after baseline inspection.
- Existing build and tests: none.
- Codex CLI: `0.155.0-alpha.9`.
- Claude Code: not installed.
- Python: `3.13.15`.
- Git: `2.52.0.windows.1`.
- Operating system: Windows 11 Pro 64-bit, version 10.0.26200.

## Steps

1. Define canonical agent contracts, policies, protocols, schemas, and templates.
   - Likely paths: `.iacode/`, `docs/`, `prompts/`.
   - Success: every required artifact exists and cross-references the canonical layer.
   - Risk: tool-specific adapters could contradict canonical contracts.
2. Implement the cross-platform Development Ledger scripts.
   - Likely paths: `scripts/development-ledger/`.
   - Dependencies: Python standard library; optional `jsonschema` is not required.
   - Success: checkpoint creation, finalization, validation, and secret redaction work on Windows and Unix-like systems.
   - Risk: Git commit self-reference and unborn repositories require explicit semantics.
3. Add automated tests covering every required validator failure mode.
   - Likely paths: `tests/`.
   - Success: valid checkpoint passes; all specified corruptions fail.
   - Risk: fixture tests must not modify the real checkpoint.
4. Create and populate `SETUP-00-CP-0001`.
   - Success: complete reconstructible evidence, handoff, provenance, quality, and next action.
   - Risk: metadata must remain truthful when a check is not executable.
5. Run validation, automated tests, independent review, and adversarial red-team checks.
   - Success: reproducible commands exit zero and tampering cases are detected.
   - Risk: Claude Code is unavailable, so genuine cross-tool validation may remain manual.
6. Finalize documentation, commit the completed setup, and report only the requested summary.

## Stop Conditions

- A mandatory artifact cannot be created or validated.
- A secret is detected and cannot be safely redacted.
- Git state diverges unexpectedly from the recorded baseline.
- A future Gate implementation would be required to satisfy a SETUP-00 item.

## Out of Scope

- Any functional implementation of Gate 0 or later Gates.
- Model training, inference runtime, sandbox runtime, or IDE integration.
