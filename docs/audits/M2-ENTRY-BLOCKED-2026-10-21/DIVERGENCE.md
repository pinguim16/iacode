# M2 audit entry divergence — BLOCKED

Status: BLOCKED

## Authorization and scope

The owner authorized this separate auditor chat to audit M2 (Gates 4–7) on
2026-10-20, using only repository context. Implementation repairs, changes to
sealed checkpoints, Gate 8, global configuration changes, Docker/WSL restarts,
and interruption of unrelated applications are not authorized.

## Expected

- Subject: GATE-7-CP-0001, delivered READY_FOR_REVIEW.
- Canonical tag: refs/tags/iacode-checkpoints/GATE-7-CP-0001.
- Subject commit: 823cf164c6931dab7f957c92721ded7a916655bd.
- STATE.json declares branch main and dirty=false.
- The canonical entry observation must agree with the actual Git state before
  checkpoint creation or audit execution.

## Observed

All commands below ran from E:/iacode with the current execution permissions.

Direct `git status --short --branch` showed `## main...origin/main` and no
changed paths. Direct `git branch --show-current` printed `main`. Both
`git rev-parse HEAD` and `git rev-parse
refs/tags/iacode-checkpoints/GATE-7-CP-0001` printed the expected subject commit.
These commands also emitted Git warnings; their stdout and diagnostic streams
must not be confused.

The following read-only invocation exercised the repository's actual helper:

```text
python -c "import sys,json,pathlib; sys.path.insert(0,'scripts/development-ledger'); from ledger_common import git_snapshot; print(json.dumps(git_snapshot(pathlib.Path.cwd()),ensure_ascii=True,indent=2))"
```

The process exited 0 after 4.679 seconds. Its observed output was:

```json
{
  "branch": "warning: safe.directory ''%(prefix)///192.168.68.59/f/script-amazon-novo'' not absolute\nwarning: safe.directory ''*'' not absolute\nmain",
  "head": "warning: safe.directory ''%(prefix)///192.168.68.59/f/script-amazon-novo'' not absolute\nwarning: safe.directory ''*'' not absolute\n823cf164c6931dab7f957c92721ded7a916655bd",
  "dirty": true,
  "detached": false
}
```

Direct Git also warned that C:/Users/cesar/.config/git/ignore could not be read
because permission was denied. No permission or configuration change was made.

## Difference and supported cause

The actual helper observation cannot equal STATE.json: branch and head contain
diagnostics, and dirty is true. This is not evidence that the subject tag moved
or that implementation files changed.

Source inspection of scripts/development-ledger/ledger_common.py shows that
run_git merges stderr into stdout; git_snapshot uses that merged text as branch
and head and evaluates its status text with bool(status). The observed Git
warnings therefore explain the contaminated helper observation. The origin or
history of the external Git configuration and access restriction was not
established, and no reconciliation or repair was attempted.

## Entry validation

The required `python scripts/development-ledger/validate_checkpoint.py` was
started before any repository alteration. At this report's initial creation,
the command was still running and no terminal result had been observed.
No exit code or PASS is inferred from silence. Its eventual result must be
retained separately below before this run is handed off.

### Actual terminal observation

The process was awaited to completion without interruption. It exited 1 and
printed CHECKPOINT_INVALID. Its complete decoded tool output is preserved in
ENTRY-VALIDATION.txt, with LF normalization explicitly declared; no raw byte
identity is invented. Terminal observation was available by
2026-10-21T03:07:44Z (2026-10-21 00:07:44 America/Sao_Paulo).

The last active-process observation recorded 1404.27 elapsed seconds. The
displayed process start was 2026-10-20 23:42:35 local time, at second precision.
The start-to-final-observation interval is about 25 minutes; exact full process
duration was not independently instrumented and is not fabricated from the last
poll's wait duration.

The actual output includes a branch mismatch containing both safe.directory
warnings, dirty-state mismatch, and tag/tree comparisons contaminated by the
same warnings. It also rejects the seal chronology and the change to the root
DIVERGENCE.md. The latter change was this auditor's record, not a pre-existing
implementation difference: the record was written after the helper divergence
was proved but before the long-running read-only validator terminated. This
attempt is therefore not a validation of an unchanged tree throughout its run.
Its failure remains a failed entry attempt, never M2 acceptance evidence.

Subsequent direct git commands each exited 0. HEAD and the canonical subject
tag remain 823cf164c6931dab7f957c92721ded7a916655bd, and HEAD^ is
8357bd66431253b27cdf518ccd47506403c00951, the actual declared content commit.
This does not silently waive the failed canonical validation. The contaminated
comparisons must not be represented as independent proof of moved tags or a
broken subject history.

### Auditor recording incident and original preservation

The initial Add File operation replaced the already tracked root DIVERGENCE.md.
The initial clean Git state and the final status identified this as the
auditor's own change. The historical original was read from HEAD:DIVERGENCE.md
with stdout and diagnostics captured separately, preserved without alteration,
and restored. The new report and execution transcript were relocated to this
separate docs/audits directory. No original finding is adopted as a result of
this audit, and no sealed subject is rewritten. Final Git verification below
must confirm that no tracked path remains changed.

An auxiliary read-only Get-CimInstance diagnostic was denied access; no bypass
or permission expansion was attempted. A diagnostic read of a nonexistent
historical receipt also exited 1 and is not acceptance evidence. These failures
remain in the tool transcript; they do not inflate execution or test counts.

### Pending audit obligations

No normal auditor checkpoint was allocated: the canonical allocator consumes
the divergent Git observation, and silently replacing its values would bypass
the mandatory stop. No lesson preflight, auditor requirement derivation, full
M2 review, independent Red Team, functional verification, G4-F-004 closure
reconstruction, fresh public clone, mandatory full suite, bundle comparison,
attestation, finalization, seal or publication was completed by this run.
These remain pending, not PASS or NOT_APPLICABLE. Cross-tool availability was
not established, and no NOT_AVAILABLE claim is made.

## Disposition

The mandatory divergence stop in AGENTS.md, START-HERE.md and
docs/CHECKPOINT-PROTOCOL.md applies. Normal audit execution and checkpoint
creation are stopped. This document is the authorized divergence record; it is
not a sealed audit checkpoint or a milestone attestation.

No implementation or sealed checkpoint was changed. LATEST.md still names the
sealed subject. No approval, independent Red Team result, cross-tool
availability claim, milestone verdict, publication or Gate 8 authorization is
asserted. trainingAllowed remains false.

## Final Git and report inventory

Final `git diff --exit-code` and `git diff --cached --exit-code` both exited 0.
The tracked root DIVERGENCE.md and all other tracked content are restored to
the original subject. Final `git status --short --branch` exited 0 and showed:

```text
## main...origin/main
?? docs/audits/
```

LATEST.md still identifies docs/checkpoints/GATE-7-CP-0001. No commit, tag,
seal, push, remote synchronization or public-clone claim was produced by this
audit run. Local remote-tracking status is not a fresh public verification.

FILES.json in this report directory declares the new report paths. It is a
descriptive inventory of this blocked entry record, not a finalized checkpoint
manifest. The execution transcript preserves the actual failed validation and
does not import implementation-run results as independent evidence.

## Required next action after reconciliation

Resolve the named entry-observation impediment under separate appropriate
authority, then repeat the full entry validation and compare direct Git,
canonical Git observation, STATE.json and the subject tag. Do not silently
filter the evidence, change global Git settings, modify the sealed subject or
continue an audit on a fabricated clean baseline.
