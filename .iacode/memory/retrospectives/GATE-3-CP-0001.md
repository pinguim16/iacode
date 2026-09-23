# Retrospective — GATE 3 — SANDBOX + TOOL EXECUTION / GATE-3-CP-0001

Record observations, decisions and evidence. Never record private chain-of-thought, and never record
a secret. Every claim points at an artifact in this repository.

## What went well

**Asserting isolation on the real engine found what a double could not.** The sandbox suite runs
inside the service's image with the engine's socket, so every claim about privileges, mounts,
network, secrets, limits and process control is checked against a real container. The suite and the
Red Team together cover 21 attacks on real sandboxes. Evidence:
`services/sandbox/tests/test_sandbox_engine_isolation.py`,
`services/sandbox/tests/test_sandbox_engine_limits.py`,
`scripts/development-ledger/gate3_sandbox_attacks.py`, `ContainerIsolationTests`.

**One path resolver, reached by every path.** `iacode_sandbox.paths` is the only module that decides
a path; the controller normalises through it, the helper resolves through it, the patch applier
resolves through it, and the image copies the same file. No path escape was found by the suite, the
scenarios or the Red Team. Evidence: `SinglePathResolverTests`, `PathResolverTests`,
`SymlinkContainmentTests`, `M1-INTERNAL-RED-TEAM.json` attacks `G3-A` and `G3-B`.

**The rehearsal pattern of Gate 2 carried over with one substitution.** The coding scenario uses the
runtime's own service to create the run, the real workflow and activities, the stack's sandbox
service and real containers, and scripts only the model. It found a defect in its first run that no
suite could have (below). Evidence: `services/orchestrator/rehearsal/coding.py`,
`scripts/iacode/scenarios/sandbox_coding_e2e.py`, `SandboxScenarioTests`.

**A host sentinel turned "nothing runs on the host" into a measurement.** The coding run's shell
probes where it runs and tries to write the host's sentinel under every spelling of its path; the
host file keeps its digest and no file appears beside it. Evidence: `var/sandbox-coding.json`
steps `host.sentinel_unchanged` and `host.no_file_appeared`, `cmd-0071`.

**Atomic, pushed commits made every repair a visible commit.** Every commit of the Gate reached
`origin/main` as it was made, and each repair of an earlier pushed commit is a new commit rather
than a rewrite. Evidence: `git log origin/main`, `docs/checkpoints/GATE-3-CP-0001/DECISIONS.md`
D-04, D-08, D-10, D-11.

**The stale-image lesson held.** Every gate and scenario that runs inside an image rebuilds it first,
and the sandbox image is addressed by the digest of its inputs, so the service refuses an image
built from other source. The Red Team's `G3-X` planted a failing test and the gate rebuilt and
failed on it. Evidence: `LSN-0036`, `Gate3MandatoryGateTests`, `SandboxImageProfileTests`.

## What failed

**The sandbox and the workflow disagreed on the activity's answer (G3-F-003).** The first real run
failed its workflow task with `KeyError: 'agentResult'`. Root cause: the shape of one activity
result was spelled separately in two processes, and each side's suite used the other as a double.
Recorded in `DECISIONS.md` D-10; repaired in `b69ff22`; lesson `LSN-0052`.

**A detached fork bomb wedged a sandbox (G3-F-004).** Found by the Red Team's first run (`cmd-0079`).
Root cause: the sweep read each process's command line — which waits on a forking process — and
killed without stopping first. Recorded in D-11; repaired in `540965d`; lesson `LSN-0053`.

**The result bound disagreed with the runtime's measure (G3-F-001).** Found while writing the
evidence for requirement 17.5. Root cause: two services bounded one payload by two measures.
Recorded in D-08; repaired in `5b10139`; lesson `LSN-0051`.

**Three pushed commits left a mandatory gate red (G3-F-002).** Commit 1 broke the repository-wide
decoding scan; commits 12 and 13 the lint gate. Root cause: the pre-push check followed the
commit's subject, not its reach. Recorded in D-04; repaired in `5923ce1` and `85bbb71`; lesson
`LSN-0054`.

**Three Red Team verdicts in the first run were harness errors** (`G3-D`, `G3-L`'s criterion,
`G3-Q`): a blank line parsed as a mount, a detached bomb's exit status taken as the defence, and a
replay judged by its output instead of its flag. Recorded in D-11 rather than corrected silently.

## What repeated

`LSN-0041`'s editing path recurred twice in this session's own tooling: a shell heredoc consumed
backslashes in a patch, once leaving a real newline in a string literal and once control characters
in a test. Both were caught before staging, by a syntax error and by the control-character scan run
before every stage, and never reached the repository, so the guardrail (`SourceIntegrityTests`) was
not bypassed and this is not a `GUARDRAIL_FAILURE`. Recorded in D-13.

`LSN-0035`'s failure class — a subprocess capture without a decoder — reached commit 1 and was
caught by its guardrail before the Gate went further. The guardrail worked; the gap was the pre-push
check, which is `LSN-0054`.

## What was learned

- A payload bounded by one service and accepted by another must be measured the same way on both
  sides; a bound on raw bytes is not a bound on a rendering.
- Two processes that exchange a payload must name its shape once, and a run through the real pair is
  the only thing that proves they agree.
- A control that must end processes it did not start has to freeze before it kills, and must not
  read anything a forking process holds.
- The reach of a change, not its subject, decides the checks before its push.

## What should become a guardrail

| Item | Control | Kind | Lives in | Removing it would allow |
|---|---|---|---|---|
| Result bound agrees with the runtime | `test_the_runtime_accepts_every_result_the_sandbox_hands_over` | test | `tests/test_gate3_sandbox.py` | a result the sandbox considers deliverable to fail its run |
| Activity result named once | `test_both_sides_name_the_result_by_the_shared_key` | test | `tests/test_gate3_sandbox.py` | the workflow and the sandbox to drift apart behind green suites |
| Sweep outlasts a detached bomb | `test_a_fork_bomb_that_detaches_leaves_a_sandbox_that_still_answers` | test | `services/sandbox/tests/test_sandbox_engine_limits.py` | a command to leave its sandbox unable to start a process |
| Pre-push reach | none automated | — | `docs/DEVELOPMENT-CONTRACT.md` | a red gate to reach the public remote; stays `CONFIRMED` |

## New lessons

| Lesson | Status | Guarded by |
|---|---|---|
| `LSN-0051` A payload one service bounds for another must be bounded as the receiver measures it | `GUARDED` | `GRD-0053` |
| `LSN-0052` Two processes that meet on a queue must name what crosses it once, and a real run must exercise both | `GUARDED` | `GRD-0054` |
| `LSN-0053` A process sweep that reads what a forking process holds waits on the processes it has to kill | `GUARDED` | `GRD-0055` |
| `LSN-0054` A pre-push check narrower than the change's reach lets a red gate reach the public remote | `CONFIRMED` | — |

## Updated lessons

| Lesson | Change | Reason |
|---|---|---|

## Retired lessons

| Lesson | Superseded by | Reason |
|---|---|---|
