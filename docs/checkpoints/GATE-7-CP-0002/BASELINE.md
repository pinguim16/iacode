# Baseline — M2 fresh-session independent audit

## Immutable subject

- Subject checkpoint: `GATE-7-CP-0001`.
- Canonical tag: `refs/tags/iacode-checkpoints/GATE-7-CP-0001`.
- Sealed commit: `823cf164c6931dab7f957c92721ded7a916655bd`.
- Offered status: `READY_FOR_REVIEW`; M2 remains `PENDING` in the subject.
- Public remote: `https://github.com/pinguim16/iacode.git`.

## Entry observations

- Direct Git stdout resolved branch `main`, HEAD and the canonical tag to the declared commit.
  Stderr independently reproduced malformed inherited `safe.directory` entries and denial of the
  sandbox user's read of the original global ignore file.
- The owner-provided byte copy of that ignore file existed, was readable, and matched declared
  SHA-256 `744e3b6c0e736af11840443f60f3f4b38176d214e026a54763628d8a6c317cbb`.
- A process-scoped private Git configuration preserved all six non-target records, all includes
  and the exact ignore bytes, removed only four malformed/wildcard trust records, and added only
  exact trust for `E:/iacode`. No global configuration or ACL changed.
- The original worktree contains the authorized prior untracked reports under
  `docs/audits/M2-ENTRY-BLOCKED-2026-10-21/`. Its required validator therefore exited 1 on dirty
  state, inventory/freshness and strict secret-pattern findings. This is retained as an entry
  observation, not a verdict over the sealed subject.
- A new public HTTPS clone, with credential helpers and prompting disabled, resolved remote `main`
  and the canonical tag to the declared commit. Detached checkout was clean. The subject returned
  `CHECKPOINT_VALID`, `LESSONS_VALID total=151 active=151 guarded=148`,
  `INTEGRITY_VALID anchors=35`, and `REVIEW_BUNDLE_DECLARATION=PASS`.
- Every one of the subject checkpoint's 610 files was read byte-for-byte: 9,202,580 bytes, with
  aggregate path/content SHA-256
  `74638eb4c285d05ca11dcf5164731c7002bd15625800de42cae4a365bae118ef`.

## Frozen denominator

The canonical registry/checklist agreement exposes 105 Gate 4, 50 Gate 5, 51 Gate 6 and 48 Gate 7
requirements: 254 accumulated Gate rows. The lesson preflight considered 151 lessons, selected 150
as applicable and derived 150 mandatory `LESSON-REQ-` rows. The accumulated M2 audit denominator is
therefore 404 rows, independently generated in `M2-AUDIT-REQUIREMENTS.json`. The ordinary Gate 7
audit-checkpoint matrix contains 198 rows and remains a separate mandatory control.

## Pre-test finding

Creating this audit checkpoint with an explicit `--phase` produced `cmd-0001` without that option
or its value in both `command` and `arguments`, although `STATE.json.phase` proves it was consumed.
The current `new_checkpoint.py` hard-codes only Gate and status into the record. This independently
reproduces the failure class documented by guarded `LSN-0010`; it is recorded as `M2-F-001`, a High
`GUARDRAIL_FAILURE`. The record is preserved unchanged and no correction is made by this auditor.

## Environment boundaries

- PowerShell 7.6.5; Python 3.13.15; Git 2.52.0.windows.1; Docker CLI 29.8.1.
- The Docker CLI reports it cannot read the user's global Docker configuration under sandbox
  permissions. No replacement configuration, restart or permission change has been authorized.
- The four prohibited historical temporary targets and the two retained Gate 7 diagnostic owners
  listed in the subject `RISKS.md` are outside cleanup authority and remain untouched.
- No separately identified second tool/provider/model is exposed. Cross-tool validation is
  `NOT_AVAILABLE`; `trainingAllowed` remains `false`.
