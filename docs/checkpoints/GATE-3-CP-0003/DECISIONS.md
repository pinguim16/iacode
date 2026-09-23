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
