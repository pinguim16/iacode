# ADR-0024 — A public remote, atomic commits and a push per advance

Status: ACCEPTED
Date: 2026-09-22
Owners: GATE 3 — Sandbox

## Context

Until `GATE 3` the repository lived on one machine. Every Gate was delivered as one or two large
commits, sealed, tagged and anchored locally, and nothing left the disk. That had three costs: a
failed disk was the whole project, the history said what a Gate delivered but not how it got there,
and the evolution of a requirement into code, tests and fixes — the material a later Gate is meant
to learn from — was compressed into a single diff.

The owner authorised a remote for the development of IACode itself:
`https://github.com/pinguim16/iacode.git`, branch `main`. The repository is **public**. A
credential that reaches any commit is disclosed the moment that commit is pushed, even if a later
commit removes it, and a public history cannot be rewritten without breaking every checkpoint tag
and every integrity anchor that names a commit.

`ADR-0005` fixes the Gate-bound workflow and states that a replacement workflow is adopted only
through an ADR. This is that ADR. It extends `ADR-0005`; it does not relax it.

## Decision

1. **One remote, one branch.** `origin` is `https://github.com/pinguim16/iacode.git` and `main` is
   the only branch pushed. A different `origin` is never overwritten silently: it stops the run and
   goes to the owner.
2. **The whole history is scanned before it becomes public.** Before the first push,
   `python scripts/development-ledger/secret_scan.py --history` scans every blob reachable from
   every ref, every commit message and every annotated tag message. A finding names the commit, the
   path, the line and the kind of secret and never the value. A finding blocks the push; the history
   is never rewritten automatically to make one go away.
3. **Every later push is preceded by a staged scan.** `secret_scan.py --staged` over the content of
   the commit about to be made, the targeted tests of that advance, `git status` and
   `git diff --cached`. The history-wide scan is not repeated on every push.
4. **A commit is one logical advance, and a green one.** An advance is committed when its
   implementation is complete, its targeted tests pass, the staged content is only what the advance
   changed, and no secret is staged. A Gate is no longer one commit; the checkpoint still seals the
   Gate. A known-red state is not committed to "save progress" — failures live in the Engineering
   Ledger. The exception is a checkpoint the protocol requires to be preserved `BLOCKED`, and its
   commit says so.
5. **Every green commit is pushed.** `git push origin main` after each advance, not at the end of
   the Gate.
6. **Pushed history is immutable.** No force push, no `--force-with-lease`, no amend, rebase or
   hard reset of a pushed commit. A mistake is corrected by a new commit.
7. **Checkpoint tags are pushed and never moved.** After a checkpoint is sealed its canonical tag
   `refs/tags/iacode-checkpoints/<ID>` is pushed. A remote tag is never deleted or re-pointed.
8. **Authentication stays in the local credential store.** Git Credential Manager, `gh auth`, an
   SSH agent or an equivalent mechanism already configured on the machine. A token is never put in a
   URL, in Git configuration, in a versioned file or in the chat.
9. **A Gate that closes claims remote synchronisation only when it is true.** `INTERNAL_GATE_PASS`
   requires `git log origin/main..main` to be empty and the final checkpoint tag to be listed by
   `git ls-remote --tags origin`. A push that fails leaves the local commit in place and is recorded
   as an operational blocker.

The Git configuration an **agent** uses inside a sandbox is a different thing and is governed by
`ADR-0027`: local operations on a disposable workspace, a sandbox identity, no remote and no
credential.

## Evidence

- `scripts/development-ledger/secret_scan.py` and `.iacode/policies/secret-scan-allowlist.json`: the
  scanner and the reviewed values that are credential-shaped and are not credentials, matched by the
  digest of the secret component rather than by path.
- The first history-wide scan and the first push are recorded in `GATE-3-CP-0001`.

## Alternatives considered

- **Keep the repository local.** Rejected by the owner: no backup and no observable evolution.
- **One commit per Gate, pushed at closure.** Rejected: it is the practice this ADR replaces, and a
  failure late in a Gate would lose the whole Gate's work.
- **Rewrite history when a secret is found.** Rejected as an automatic action. Every checkpoint
  tag, every integrity anchor and every recorded command names a commit; rewriting one breaks all
  of them. It remains available to the owner, explicitly, after a checkpoint.

## Consequences

The history now records how a Gate was built, which is the material a later Gate will learn from.
`trainingAllowed` stays `false` by default: a public history is not a licence to train on it.

## Risks

A credential shape the scanner does not know reaches a public commit. Held down by the canonical
patterns plus the wider history patterns, the staged scan before every push, and the rule that
credentials live only in the ignored `infra/compose/.env`.

## Reversal strategy

Making the remote private, or stopping pushes, changes nothing in the local protocol: checkpoints,
tags and anchors are local objects first. A replacement workflow is adopted through a later ADR.

## Related artifacts

`ADR-0005`, `docs/DEVELOPMENT-CONTRACT.md`, `.iacode/policies/secret-policy.md`,
`.iacode/policies/tool-execution-policy.md`.
