# Audit Executions

## Baseline and isolation

- Baseline commit/tag: `994bab402873bc4d221c02d8c94bdebeb2b0f3cb` / CP-0006.
- Shared tree was clean before CP-0007 creation.
- All destructive mutations ran in disposable clones; only CP-0007 and `LATEST.md` changed in the shared repository.
- Gate 0 work was not started.

## Independent roles

| Role | Isolation | Result |
|---|---|---|
| Completeness auditor | clean clone at CP-0006 | 59 checklist rows inspected; 55 COMPLETE after this audit, 4 PARTIAL |
| Test/evidence validator | clean clone and detached replays | nominal suite green; count and reproducibility defects found |
| Red Team | isolated mutation clones | 18 defended, 8 escaped |
| Primary auditor | shared audit-only checkpoint plus isolated fixtures | evidence verified; verdict REWORK_REQUIRED |

## Canonical executions

| Check | Result |
|---|---|
| Baseline full suite | 181 tests, 0 failures, 163.963s |
| Independent clean-clone full suite | 181 tests, 0 failures, 123.486s |
| Test/evidence role full suite | 181 tests, 0 failures, 144.030s |
| Python compileall | exit 0 |
| Current checkpoint validator on sealed CP-0006 | `CHECKPOINT_VALID` |
| Lesson validator | `LESSONS_VALID total=14 active=14 guarded=12` |
| CP-0005 completeness | PASS, 38/38, evidence 100% |
| CP-0006 completeness | PASS, 47/47, evidence 100%; independently 45 mandatory |
| Secret scan | 222 tracked/readable files, 0 findings |
| Markdown links | 142 tracked Markdown files, 37 relative links, 0 missing |
| Detached historical tags | CP-0001 through CP-0006 all `CHECKPOINT_VALID` with current tooling |
| Diff whitespace check | exit 0 |

## Historical anchors

`CP1 0cb4f246`, `CP2 ae563f860`, `CP3 5780b0f8`, `CP4 c2eea150`, `CP5 276645b4`, `CP6 994bab40`. Current tooling accepted all six in clean detached validation. Red Team nevertheless proved that coordinated tag/content movement is not anchored against an immutable external expected value.

## Deterministic command sampling

Seed: `20260920`.

- CP-0005 selected: `cmd-0008`, `cmd-0028`, `cmd-0015`.
- CP-0006 selected: `cmd-0013`, `cmd-0012`, `cmd-0003`.
- At final sealed tags, all six sampled commands replayed with exit 0; CP-0005 `cmd-0008` ran 131 tests.
- At the commands' own declared commits, CP-0006 `cmd-0012` exited 2 because its declared input did not exist, and CP-0005 `cmd-0028` exited 1 because the referenced tag was not at that commit.
- Finding: command syntax is valid, but dirty working-tree inputs are not content-bound, so recorded commit context is not reproducible.

The sample inspection covered runtime, working directory, literal command/arguments, commit, purpose, inputs, recorded result, exit code, duration, and repository dirty state.

## Mutation evidence summary

Every mandatory A–Z mutation has a per-attack record in `RED-TEAM-REPORT.md`. Every failing gate was reproduced and classified as deterministic `PRODUCT_DEFECT`; there were no environment or flaky classifications.

