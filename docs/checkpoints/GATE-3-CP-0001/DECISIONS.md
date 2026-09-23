# Decisions

Checkpoint-local decisions and corrections of `GATE-3-CP-0001`. Structural decisions are ADRs
(`ADR-0024` to `ADR-0027`); what is recorded here is what this run decided or corrected about its
own execution, including the places where its ledger says less, or more, than happened.

## D-01 — The owner's local archive is excluded, not committed and not deleted

The working tree held `docs/checkpoints/GATE-2-CP-0002.rar`, the owner's backup of a sealed
checkpoint. It is not repository content, and deleting it is not this run's decision. It is listed in
`.git/info/exclude` (local, unversioned), so validation sees a clean tree and the file stays where
the owner put it. Every validation that needed a pristine tree before the exclusion existed was run
from a detached worktree instead.

## D-02 — `cmd-0031` is not Phase 0 evidence

`cmd-0031` (`python -m unittest discover -s tests`) ran against a working tree that already held
uncommitted sandbox work, and exited `1`. Its failure belongs to that uncommitted work, not to the
five inherited fixes, and its success could not have been attributed to them either. The Phase 0
revalidation was repeated from a detached worktree at `e212dc4` (the commit that closes Phase 0):
618 tests, `OK`, one expected skip (the checkpoint had no preflight at that commit). That run was
executed outside the ledger, so it is reported here and not cited as a command; the recorded
evidence for the control-plane suite is the Green Keeper cycle and the full verification of this
Gate, which run over the committed content.

## D-03 — `cmd-0032` says more than it ran

The purpose of `cmd-0032` names the migration suite against PostgreSQL. The command it recorded,
`scripts/iacode/gates/api_tests.py`, runs the API's unit suite only; the migration tests
(`SandboxMigrationTests`) are integration tests and run in the verification's `integration` stage.
The record is not rewritten (the ledger is append-only). The migration requirements of this Gate
cite the integration stage of the full verification, not `cmd-0032`.

## D-04 — Commit 1 broke a guarded property, and a new commit repaired it

Commit `17d1498` added `secret_scan.py` and `remote_sync.py` without configuring their output
stream and with a subprocess capture that did not name its decoder, which the repository-wide
`LSN-0035` scan (`SubprocessDecodingTests`) refuses. It had been pushed, so it was not amended:
`5923ce1` repaired it, and `cmd-0015` records the targeted run of the scan and the Git policy suite
over the repair. The guardrail did what it exists for; the defect was running only the new suite
before the first push. From commit 3 onwards the pre-push check ran the repository-wide scans that
a change could reach.

## D-05 — The lesson-index and guardrail rules are versioned into the memory policy

Fixes B and C tightened `validate_lessons`. Applied unconditionally, the new rules would have made
the sealed `GATE-1` and `GATE-2` checkpoints invalid from their own tags, and the promotion fixtures
built on them fail. The rules are therefore bound to memory policy versions:
`RESOLVED_GUARDRAIL_MEMORY_POLICY = 2.2.0` (every guardrail entry resolved through one function) and
`DERIVED_INDEX_MEMORY_POLICY = 2.3.0` (`LESSONS.md` must be the render of the memory). The
repository's memory declares `2.3.0`, and `test_the_repository_memory_declares_the_newest_policy`
keeps it at the newest version, so the live memory can never sit under the weaker rule while sealed
history keeps validating under the rule it was sealed with.

## D-06 — The requirement artifacts keep their canonical names

The Gate prompt names `GATE-3-REQUIREMENTS.json` and `.md`. The repository already has the canonical
mechanism: `derive_requirements.py` writes `REQUIREMENTS-MATRIX.json` / `.md` (the schema-bound
matrix the completeness audit reads) and `CLOSURE-REQUIREMENTS.json` / `.md` (the closure view), and
the prompt forbids a parallel mechanism. Those four files are the Gate's requirement artifacts; no
copy under another name is created.

## D-07 — The sandbox image carries Git and Python, not Node

The prompt's example image lists Git, Python and Node, and also says the image must carry only the
toolchain the Gate's tests need. The synthetic repository and the ledger tests are Python. Node is
therefore absent from `iacode-dev`, stated in the image profile's description, and a profile that
needs it is a new entry in the image registry rather than a larger universal image.

## D-08 — What an agent receives is bounded as the runtime measures it

Writing the evidence for requirement 17.5 showed that the sandbox bounded the raw bytes a tool
produced but not the rendered result: JSON escapes a control character into six bytes, so a file
inside the 128 KiB read limit could render at 768 KiB, over the runtime's 256 KiB tool-result
limit, and fail the run that read it. The sandbox now shortens the output it hands an agent to
`SANDBOX_AGENT_RESULT_MAX_BYTES` (160 KiB), measured exactly as the runtime measures, explicitly and
never dropping the artifact references (`AgentResultBoundTests`), and a repository test reads both
limits from their sources and requires the runtime's to be the larger
(`Gate3AgentToolPolicyTests.test_the_runtime_accepts_every_result_the_sandbox_hands_over`).

## D-09 — The dependency scan covers the service's Python dependencies, not the image's system packages

The sandbox service installs the same lock as the API and the worker, which is the lock the
dependency scan audits. The sandbox image's system packages (Git on Debian) and the static container
client are pinned by version and by digest, and no vulnerability scanner for them exists in the
repository. That gap is stated in the runbook and in row 20.5 instead of being described as scanned.
