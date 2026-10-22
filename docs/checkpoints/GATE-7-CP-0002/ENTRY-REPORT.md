# M2 audit entry report

## Subject and publication

The local branch and direct Git observations resolved `main`, `HEAD` and the canonical checkpoint
tag to `823cf164c6931dab7f957c92721ded7a916655bd`. The only pre-existing worktree additions were the
authorized untracked reports under `docs/audits/`.

The inherited Git environment emitted malformed `safe.directory` warnings and could not read its
default global ignore. Stdout and stderr were captured separately. A private per-process global
configuration preserved all six non-target configuration records and all includes, removed only
four malformed/wildcard trust entries, added trust for exact `E:/iacode`, and pointed
`core.excludesFile` to the verified byte-identical ignore copy. Direct Git then returned clean
diagnostic streams and the real branch/head values.

The validator executed once in the original worktree and exited 1 because the authorized prior
reports are untracked, stale the subject's internal-assurance scope, are absent from its inventory,
and contain text matched by the repository secret-pattern detector. That result is retained as a
failed worktree-entry observation, not a judgment of the sealed tree.

A new unauthenticated public clone used HTTPS with credential helpers disabled, terminal prompting
disabled and the OpenSSL backend required by this sandbox. Remote `main` and
`refs/tags/iacode-checkpoints/GATE-7-CP-0001` both resolved to the declared commit. Detached checkout
was clean. In that exact clone:

- `validate_checkpoint.py` exited 0 with `CHECKPOINT_VALID`;
- `validate_lessons.py` reported 151 active lessons, 148 guarded;
- `verify_integrity.py` exited 0 with 35 valid anchors;
- `review_bundle.py --verify-declaration` exited 0 with
  `REVIEW_BUNDLE_DECLARATION=PASS`.

All 610 files in the complete subject checkpoint were read byte-for-byte (9,202,580 bytes). Every
JSON, JSONL and Python source parsed structurally. The aggregate path-and-content digest was
`74638eb4c285d05ca11dcf5164731c7002bd15625800de42cae4a365bae118ef`.

## Entry result

The sealed subject identity, clean public transport, checkpoint validity, memory, integrity and
declared immutable review reconstruction are valid entry observations. They do not approve M2.

