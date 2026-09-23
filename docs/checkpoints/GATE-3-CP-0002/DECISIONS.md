# Decisions

Checkpoint-local decisions of the M1 fresh-session audit, `GATE-3-CP-0002`. This run implemented
none of the audited Gates and changed no product code: every file it wrote is inside this
checkpoint, the attestation it authored, the integrity anchor it owed its subject and `LATEST.md`.

## D-01 — The owner's local archive is excluded, not committed and not deleted

The working tree held `docs/checkpoints/GATE-3-CP-0001.rar`, the owner's backup of the sealed
subject. It is not repository content and deleting it is not this run's decision. Following the
precedent of `GATE-3-CP-0001` D-01, `/docs/checkpoints/*.rar` was added to `.git/info/exclude`
(local, unversioned). Validation then saw a clean tree (`CHECKPOINT_VALID`) and the file stayed where
the owner put it.

## D-02 — The audit checkpoint belongs to GATE-3 and anchors its subject

The audit judges `M1`, whose last Gate is `GATE 3`, so the checkpoint is `GATE-3-CP-0002`, exactly as
the `M0` audits were `SETUP-00` checkpoints. It opened at `BASELINING`, anchored the sealed
`GATE-3-CP-0001` (18 anchors, `cmd-0002`, `cmd-0003`) and derived its requirement set from the
`GATE 3` checklist and a preflight scoped `independent-audit` (`LSN-0030`): 139 + 54 = 193 rows.

## D-03 — Sealed checkpoints are judged by the current validator

`sealed_subjects.py` first ran each checkpoint's own revision of the validator, and two failed:
`GATE-0-CP-0001` names inputs under the ignored `var/` (`G1-F-007`) and `GATE-2-CP-0001` was sealed at
`BLOCKED` with the symbolic `HEAD` (`G2-F-013`). Both defects were found and repaired in the tooling by
the Gates that followed, and the repository's rule is that the current validator applies the rules of
the schema version a checkpoint declares — the property
`test_every_sealed_checkpoint_validates_from_its_own_tag` asserts. The verdict is therefore the
current validator run with `--root` on a detached checkout of each tag (5/5, `cmd-0010`); the own
revision's result is kept in `SEALED-SUBJECTS.json` as an observation (`M1-O-001`) rather than
dropped.

## D-04 — The live cross-gate run took four attempts, and every one is kept

`cmd-0013`: the verification's `fresh-install` stage had just recreated the stack with an empty model
catalog, and the planner's call was refused (`GATEWAY_ERROR`); the harness now synchronises the
catalog first, as the gateway smoke does, and accepts the API's `202` (`M1-O-003`). `cmd-0014` and
`cmd-0015`: the operator's configured model (`openai:gpt-4o-mini`) never produced a valid tool
request (`CROSS-GATE-LIVE-ATTEMPT-2.json`, `-3.json`). `cmd-0016`: an explicitly chosen catalogued
model (`openai:gpt-4.1-mini`), named in the request and recorded as a choice, crossed every Gate —
seven model calls through the gateway, tool requests executed in a sandbox session, results delivered
back, the model called again after a sandbox result, the host sentinel untouched — and then failed the
same way. The crossing criterion (AM-10) is judged on `cmd-0016`; the failure of all four to finish
the task is finding `M1-F-001`. Choosing another model was an audit probe, not a substitution: the
operator's configuration was not changed and the smoke model is still the configured one.

## D-05 — M1-F-001 is MEDIUM, and carried as mandatory work

The severity was weighed against the owner's rule that a real Critical or High stops the night. It is
MEDIUM: the crossing it concerns was executed, the refusal is bounded and classified, nothing
malformed was executed, and the correction is to the instructions the runtime sends. The
counter-argument is in `FINDINGS.json` beside the verdict. It is not left as backlog: it goes with
`M1-F-003` to the corrective delivery, which cannot close while any finding of this audit is open.

## D-06 — The forged-result probe needed three runs, and all three are kept

`cmd-0017` read the run's result, which is the reviewer's and cannot show what the developer was
told; `cmd-0018` read the developer stage for the mutation but not for the null control; `cmd-0019`
reads both from the developer stage and is the evidence: control `TIMEOUT-SEEN`, forged
`TIMEOUT-NOT-SEEN`, API `200`, sandbox record `TIMED_OUT`. Finding `M1-F-002`, MEDIUM.

## D-07 — The clean clone is given the machine's configuration and nothing else

A clone of the public remote cannot carry `infra/compose/.env`, which holds the database passwords
and the provider credential and which Git deliberately never publishes. `clean_clone.py` copies that
one file into the disposable clone for the full verification and deletes it with the clone; no other
file comes from the working tree. The verification of the clone recreates the local stack from the
clone's own images, as a fresh installation does.

## D-08 — The mechanism is a fresh session of the same tool

This session is Claude Code, Anthropic, `claude-opus-5-5` — the tool, provider and model of the runs
that implemented `GATE 0` to `GATE 3`. It has no memory of them. That is session independence, not
cross-tool validation: the attestation records `FRESH_SESSION_INDEPENDENT_AUDIT`, and the derivation
refuses `MILESTONE_EXTERNAL_PASS` from it. The owner's mandate names this mechanism; a cross-tool
audit was not performed and is not claimed. Cross-tool execution *is* available on this machine — a
one-line probe of a GPT model through the session's routing answered — so the attestation records
`crossToolValidation: AVAILABLE` rather than implying it was not: the mechanism was the mandate's
choice, and a later cross-tool audit of the same sealed subject remains possible.

## D-09 — The clean clone of the remote found what no local control could (finding M1-F-003)

The full verification of a fresh clone of the public remote failed one stage, `gate:tests`
(`cmd-0023`). The clone was deleted with its report, so the failing case was reproduced in a second
fresh clone, outside the ledger, and then made decisive inside it: `sealed_subjects.py --remote`
validates every sealed M1 checkpoint from a clone of the remote (`cmd-0029`, 4/5) and names the
cause — `GATE-1-CP-0001`'s record `cmd-0086` binds its inputs to commit `b59d66f9f3f9`, a closure
commit replaced before publication that no published reference reaches. Three clones settled why
the repository's own controls never saw it: the remote and `git clone --no-local` do not carry the
object, and `git clone --no-hardlinks` of the local path — the method of
`test_every_sealed_checkpoint_validates_from_its_own_tag` and of `MIR-016` — does. The finding is
HIGH by the repository's own precedent (`G1-F-007`, `G2-F-013`) and fails AM-01, AM-05, AM-17 and
AM-18.

## D-10 — The only copy of the commit is protected, not published

`b59d66f9f3f9` exists only as an unreachable object on this machine, and Git's garbage collection
removes unreachable objects after two weeks. A local reference, `refs/iacode-preserved/b59d66f9f3f9`,
now keeps it from being pruned. It is not pushed, it changes no published reference and it does not
correct the finding — a clone of the remote still lacks the commit. Publishing it, or any other
correction, belongs to the corrective delivery.

## D-11 — The night stops at the audit, as the owner's rule requires

The owner's mandate stops the execution when the `M1` audit finds a real Critical or High: a
consolidated finding, the audit's review bundle, and no `GATE 4`. That is what happened. The audit
checkpoint is sealed at `REWORK_REQUIRED`, pushed with its tag, and bundled. Design notes and
library modules drafted for `GATE 4` while the verification ran were kept out of the repository and
out of every checkpoint; they are not a delivery and nothing here depends on them.

## D-12 — AM-01 and AM-18 are judged from the published history as well

`PLAN.md` froze AM-01 and AM-18 to be judged by `sealed_subjects.py`, which validated from worktrees
of this repository. After the clean clone showed that a worktree of this repository carries objects
no published reference reaches, the same script was run against a clone of the remote as well
(`--remote`), and both rows now require both sources. That changes the evidence of two rows, not
the criteria: the criterion is that the sealed Gates are valid, and what was published is what a
reviewer receives. Judged from this repository alone, AM-01 and AM-18 would pass; the verdict would
still be `REWORK_REQUIRED`, on AM-05 (the clean clone) and AM-17 (an unresolved HIGH), which are
judged exactly as frozen.
