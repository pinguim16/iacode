# Cold-start and subject validation

The audit began on `main` at `3ef2bf77ddbddd378d35f5c4d32f2d90d42fc97d`, with a clean
worktree. `STATE.json` in the sealed subject named the same base, branch and canonical tag. The tag
`refs/tags/iacode-checkpoints/GATE-3-CP-0005`, local `HEAD` and `origin/main` all resolved to that
commit before the audit wrote anything.

The initial checkpoint validator, lesson validator and integrity validator passed. The successor
anchor was then added for `GATE-3-CP-0005`; the chain contains twenty-two anchors.

`SEALED-SUBJECTS.json` validates every M1 checkpoint detached at its canonical local tag.
`SEALED-SUBJECTS-PUBLISHED.json` repeats the validation from a transport clone of
`https://github.com/pinguim16/iacode.git`. `REMOTE-PUBLISHED-OBJECTS.json` proves that objects named
by historical evidence are absent when their preserved published references are removed and become
reachable when those exact references are fetched.

The clean-clone full verification used the authorised remote and the sealed subject commit. It
passed all 32 non-fast stages. The working copy was never used to change the audited product.
