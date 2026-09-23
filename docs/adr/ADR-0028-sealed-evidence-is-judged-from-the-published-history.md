# ADR-0028 — Sealed evidence is judged from the published history

Status: ACCEPTED
Date: 2026-09-23
Owners: GATE 3 — Sandbox (corrective delivery `GATE-3-CP-0003`)

## Context

The fresh-session `M1` audit (`GATE-3-CP-0002`, finding `M1-F-003`) cloned the public remote and
ran the full verification: 30 of 31 stages, with `gate:tests` red on
`test_every_sealed_checkpoint_validates_from_its_own_tag`. `GATE-1-CP-0001`'s sealed record
`cmd-0086` binds its inputs to `b59d66f9f3f9`, the first version of the Gate 1 closure commit,
replaced before the history was published. The commit survived only as an unreachable object on
the machine that made it. There the checkpoint validated; in every clone of the remote it did not.

Every control that judged sealed history cloned the local path — the suite with
`--no-hardlinks`, `MIR-016` the same way, the clean-clone copy and the Red Team fixture — and a
local clone copies the object store, unreachable objects included. They all asked whether the
object *exists*. A reviewer receives the published history, where the right question is whether a
published reference *reaches* it. Measured over the whole ledger, three sealed records named such a
commit: `b59d66f9f3f9`, `13ab172fcc06` and `643e721ee519`.

`ADR-0024` forbids rewriting published history, so the records cannot change and the commits
cannot be moved into `main`.

## Decision

1. **The property.** Every commit that a checkpoint's evidence names — in a command record
   (`commit`, `subjectCommit`, `repositoryState.head`) or in its metadata (`baseCommit`,
   `currentCommit`, `initialCommit`, `finalCommit`) — must be reachable from a published reference:
   a branch, a tag or a remote-tracking branch. `validate_checkpoint.py` refuses the checkpoint
   otherwise, for every schema version, and says whether the object is absent or exists only as a
   local object. The rule is a property of what was published, not of a checkpoint's format.
2. **One definition.** `ledger_common` owns it: `PUBLISHED_REFERENCE_NAMESPACES`,
   `published_reachability` and `published_clone`. A control that clones this repository to judge
   what it publishes clones through `published_clone`, which uses Git's transport (`--no-local`)
   and carries only what published references reach. A syntax-tree test refuses any other clone in
   the tooling and the suite.
3. **Preserved references.** A commit that sealed evidence names and that was replaced before
   publication is kept reachable by a lightweight tag of its own under
   `refs/tags/iacode-preserved/`, naming exactly that commit. It is an addition: the record is not
   rewritten, no existing reference moves, nothing is pushed with force. A private reference such as
   `refs/iacode-preserved/` protects an object from garbage collection and publishes nothing.
4. **Published means pushed.** `remote_sync.py` requires every local tag under
   `refs/tags/iacode-checkpoints/` and `refs/tags/iacode-preserved/` to be on the remote at the same
   commit, named on the command line or not.

## Consequences

- A sealed checkpoint that validates here validates in any clone of the remote, and a record that
  depends on an unpublished object is refused on the machine that has it, before anything is pushed.
- The history checks see exactly what a reviewer sees, at the cost of packing objects for each clone
  (seconds for this repository).
- Replacing a commit after a record names it is still possible — amending before the first push is
  not forbidden — but it now leaves a red validation until the replaced commit is preserved, which
  is the moment to decide whether the record or the amend was the mistake.
- The residual limit: a published reference can be deleted on the remote by someone with write
  access. `remote_sync.py` then fails, and `test_every_preserved_reference_is_what_makes_its_checkpoint_valid`
  keeps asserting that each preserved reference is load-bearing.
