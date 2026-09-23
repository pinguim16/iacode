# Decisions

Checkpoint-local decisions of `GATE-3-CP-0003`, the corrective delivery of the `M1` audit
`GATE-3-CP-0002`.

## D-01 — Three preserved references, not one, by the owner's decision

The owner's mandate authorised one new published reference, for
`b59d66f9f3f9add2ae9dcd1cd4609fb4a1bf0b55`, and asked for `M1-F-003` to be corrected as a property:
every object sealed evidence references is reachable from the published history. Measured over the
whole ledger before anything changed (`SEALED-EVIDENCE-COMMITS-BASELINE.json`, `cmd-0009`), the
property fails on three commits, not one: `b59d66f9f3f9` (`GATE-1-CP-0001` `cmd-0086`, `cmd-0087`),
`13ab172fcc06` (`SETUP-00-CP-0009` `cmd-0011`) and `643e721ee519` (`GATE-2-CP-0001` `cmd-0057`).
All three are the same class — the first version of a closure commit, replaced before the seal —
and differ from their published siblings only in that checkpoint's `COMMANDS.jsonl`, `FILES.json`,
`STATE.json` and `RUN-METADATA.json`. Only the first breaks validation today, because only its
record claims a clean tree and binds inputs to the commit; the other two are named by records of a
dirty tree.

Publishing only the authorised reference would have left the property false and two sealed
records pointing at objects that garbage collection will eventually delete from the only machine
that holds them. The question was put to the owner, who chose to publish all three. Before that,
the two new commits were protected locally (`refs/iacode-preserved/13ab172fcc06`,
`refs/iacode-preserved/643e721ee519`, beside the audit's `refs/iacode-preserved/b59d66f9f3f9`), and
the full-history scan, which reads every local reference, found no credential in any of them
(`cmd-0010`).

The references are lightweight tags in a namespace of their own, so each names exactly its commit
and `git ls-remote` shows that commit: `iacode-preserved/gate1-ledger-b59d66f9f3f9`,
`iacode-preserved/setup00-ledger-13ab172fcc06`, `iacode-preserved/gate2-ledger-643e721ee519`. No
existing reference was changed and nothing was pushed with force (`cmd-0011` to `cmd-0015`). The
local `refs/iacode-preserved/*` references stay until the correction is validated from the remote.

## D-02 — The audit is registered exactly as its NEXT.md states

`M1-CP-0002` is registered with the fields `GATE-3-CP-0002/NEXT.md` lists — `auditId`, `milestone`,
`gate`, `auditor`, `auditCheckpoint`, `subjectCheckpoint`, `subjectCommit`, `verdict`,
`reviewReport`, `correctiveCheckpoint`, `findingsClosureFile` — plus the descriptive `notes` every
entry carries. It has no `redTeamReport`: the audit's battery uses identifiers the registry's attack
parser does not read, none of its attacks escaped, and inventing a report path would make the
derivation read a table that is not a battery. It has no `auditCommit`, which the schema leaves
optional and `NEXT.md` does not list; the audit checkpoint's commit is bound by its canonical tag
and by the anchor this delivery adds.

## D-03 — M1-F-003 is recorded as a guardrail failure of GRD-0042

`LSN-0040` is the lesson of the class — a sealed checkpoint that does not validate from its own
tag, found late by a control over sealed history — and `GRD-0042`,
`test_every_sealed_checkpoint_validates_from_its_own_tag`, is its guardrail. `M1-F-003` is the same
class and the guardrail stayed green, because it cloned the local path. It is recorded with the
memory's own `register_recurrence` (`cmd-0019`): recurrence count 1, one `GUARDRAIL_FAILURE`,
severity HIGH to CRITICAL, status `CONFIRMED` until the repaired control is named.

## D-04 — The recurrence travels with the commit that repairs the control

The first targeted run after recording the recurrence failed (`cmd-0025`):
`test_guardrail_effectiveness_is_measured_not_asserted` found 54 of 55 guardrails effective,
because `GRD-0042` carried an unresolved `GUARDRAIL_FAILURE`. That is the control working — a
guardrail that let its failure through is red until the repaired control is named. The memory
change was therefore kept out of the first commit (the same tests green without it, `cmd-0026`)
and committed with the correction that repairs the control and resolves the failure (`15dfaf7`).
The ledger keeps the moment it was recorded (`cmd-0019`) and the moment it was resolved
(`cmd-0032`).

## D-05 — The property applies to every schema version and to the metadata commits

A sealed checkpoint is judged by the rules of the schema version it declares, so a new rule could
invalidate history. This one is different in kind: it is not about a checkpoint's format but about
what was published, and it was measured before it was made a rule — every one of the 62 commits
the ledger names is reachable once the three preserved tags exist (`cmd-0016`). It covers the
record fields that name a commit (`commit`, `subjectCommit`, `repositoryState.head`) and the
checkpoint's own (`baseCommit`, `currentCommit`, `initialCommit`, `finalCommit`), because each is
evidence a reviewer must be able to resolve. "Published" means a branch, a tag or a
remote-tracking branch of the repository validating: a private namespace such as
`refs/iacode-preserved/` keeps an object alive and publishes nothing, and a test says so.

## D-06 — The old-code evidence is behavioural as well as structural

The new tests fail against the tooling of `0e60b96` (`OLD-CODE-M1-F-003.json`, `cmd-0029`), but
mostly because a helper does not exist there. `validator_blind_spot.py` measures the behaviour: the
old validator, unchanged, accepts each sealed checkpoint whose preserved tag was removed and the
corrected one refuses it (`cmd-0031`). Its first run picked this checkpoint as a subject, because
this ledger names the preserved commits in the commands that tagged them (`cmd-0030`); subjects are
now the anchored checkpoints only. Both runs are kept.

## D-07 — The contract is stated on every turn, not only when structured output is off

The mandate asks for the exact shape whenever native structured output is not requested. The
engine requests it on every turn and the gateway client honours it only for a model whose
capability is known, so the text is written before anyone knows which will happen — which is how
`M1-F-001` arose. The contract is therefore always in the instructions; with native structured
output it restates what the schema already enforces. It is rendered from `envelope_schema()` and
the parser's kind table, and a test changes the schema and watches the text change.

## D-08 — The executor is recorded when the request is created, and the origin is never data

Deriving the executor at resolution time from the stage's profile would depend on a profile that
may have changed or been disabled since. It is written with the request instead (`0005`), and the
store's `origin` parameter has no default, so every caller declares it and a scan asserts that
each declares a constant. The refusal is a typed `403 TOOL_RESULT_ORIGIN_REFUSED`, distinct from
the `409` refusals of a wrong run or a finished run, and it is checked before the idempotent answer
so a forger never learns what the stored result says. The old behaviour is evidenced by the audit's
own probe (`GATE-3-CP-0002/FORGED-RESULT-PROBE.json`); the old images were not rebuilt to repeat it.

## D-09 — What the snapshot suite and the lint gate found before the pushes

The control-plane suite over a snapshot of the corrected tree (`cmd-0040`, 704 cases) failed two:
the preflight was stale because the memory had changed after it, and three captures in the new
tests relied on the platform codepage (`LSN-0035`). Both were repaired and the preflight re-run
(`cmd-0042`) before the M1-F-003 commit, whose exact content was then tested in a worktree of its
own (`cmd-0045`). The lint gate was not run before `3101d31` was pushed, and it was red
(`cmd-0052`): recorded as a recurrence of `LSN-0054`, repaired by `369f084` (`cmd-0053`), and
every later push ran it first.

## D-10 — The live run is the configured model's, and its verdict is the mandate's

The live coding run used `IACODE_GATEWAY_SMOKE_MODEL` (`openai:gpt-4o-mini`) and no other; the
harness has no option to choose one. The mandate's requirement is that this model makes a valid
tool request and that at least one tool executes in the sandbox. It made eleven, all executed, with
no repair (`cmd-0041`). The run then ended `BUDGET_EXCEEDED` at twelve turns without finishing the
task: recorded as an observation and as risk `R-G3-009`, not hidden and not counted as a failure
of the correction.

## D-11 — The findings are attacked by the Gate's own battery

`G3-Y` runs the forged-result scenario through the real API with its own null control, and
`G3-AA` removes a preserved tag in a transport clone and requires the validator's refusal, with the
unmutated validation as its control. The audit registered no `redTeamReport` (D-02), so no
mandatory attack is derived; these are the Gate battery's own.

## D-12 — GitGuardian's report on 7d57721 is checked against the real credentials

During this delivery the owner relayed a GitGuardian "Generic Password" incident on `7d57721`, the
M1 audit's closing commit. A pattern scanner cannot say whether a match is a credential, so two
questions were asked separately. What in that commit looks like one: the audit harness exports a
value it generates at run time with `uuid4` under a provider-credential name (`m1_sandbox_attacks.py`,
attack M1-B, which proves a sandbox cannot see the controller's environment), and it sends a
deliberately fake `apiKey` phrase to the API to prove the API refuses a provider field with `422`
(`red_team.py`, attack M1-J); neither is a credential. And whether any credential this machine
really uses is in the history: every secret value of `infra/compose/.env` — the database, Grafana
and MinIO passwords and keys, the provider keys — was searched for in all 1,898 blobs reachable
from every local ref, every commit message and every annotated tag message, recording names and
never values (`SECRET-EXPOSURE-CHECK.json`, `cmd-0072`): none is present. An access key ID is an
identifier and was not searched for. The repository's own history scan agreed (`cmd-0010`). The
incident is a false positive to be closed in GitGuardian by the owner; the provider credential of
`R-G2-009` still needs rotating for its own reason.
