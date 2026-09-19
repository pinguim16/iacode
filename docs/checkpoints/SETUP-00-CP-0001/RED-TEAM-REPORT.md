# SETUP-00 Red Team Report

## Attack round 1

- Target: review commit `0dc50fae803d6e8c13258fbe808e1af4cb6f4c10` in disposable clones.
- Verdict: `RED_TEAM_FAIL`.

Required corruptions—missing handoff, invalid JSON, invalid status, wrong commit, nonexistent LATEST target, credential-shaped value, missing provenance, and missing/empty NEXT—were detected. Additional attacks found false PASS paths.

## Findings and remediation

- Cross-file Gate PASS contradictions: new hard-coded invariants connect state, status, quality, tests, reports, cold start, and Red Team evidence.
- Mutable schema/status bypass: all schemas load, canonical statuses remain hard-coded, and empty-baseline tracked files are hash-verified.
- Unanchored later commits: Gate PASS now requires a namespaced checkpoint tag that resolves to the checked-out commit.
- Secrets outside the checkpoint or encoded inside JSON: repository-wide raw and decoded scans were added.
- Incomplete authorization/private-key redaction: full-value and full-block redaction plus dedicated tests were added.
- Path traversal in checkpoint creation: Gate identifiers are allowlisted by format before path construction.
- External-path mutation in finalization: finalization is restricted to the resolved LATEST checkpoint before any write.
- Dirty-state bypass: normal validation no longer exposes a dirty-state suppression flag.
- False initial Gate PASS: checkpoint creation disallows terminal Gate statuses; validation independently enforces closure evidence.
- Empty command/status/next/file evidence and inconsistent metadata: structural and cross-file checks were added.
- Provider/cloud credential shapes requested by review were added with non-disclosing tests.

## Isolation

Destructive attacks ran only in temporary repositories. The shared checkout was not deliberately corrupted by Red Team activity.

Final Red Team verdict is pending rerun against the corrected clean commit.

## Attack round 2

The clean rework commit passed its 31-test suite but independent adversarial review found two remaining false-PASS paths: decoded JSONL values and unanchored handoff-ready states. Independent QA also found insufficient positive evidence for a PASS test category. All three now have dedicated regression tests; final rerun is pending.

## Attack round 3

- Target: clean commit `0b943d501346078bddf4d7518936c1f3abea1ae9`, anchored by the review tag.
- Verdict: `RED_TEAM_PASS`.

Independent read-only validation and the 34-case suite re-executed all required corruptions plus the false-PASS paths discovered in earlier rounds. Missing files, malformed content, status/metadata/quality contradictions, later commits, incomplete evidence, unsafe paths, external finalization, dirty bypass, raw/decoded secret shapes, incomplete redaction, schema corruption, stale hashes, and incomplete manifests were rejected. No tested value was disclosed in validator output, and no unresolved adversarial finding remains.

## Final result

`RED_TEAM_PASS`
