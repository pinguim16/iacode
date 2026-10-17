# Gate 6 baseline

## Entry

Clean main, HEAD and the canonical Gate 5 tag matched bcfe297278d25ee5a1db70a32b8c4ba0731941ea.
The actual predecessor checkpoint, memory, integrity and remote synchronization checks passed
before this checkpoint was created. No sealed predecessor or refused cleanup target was changed.

Cmd-0001 creates this separate Gate 6 checkpoint. Cmd-0002 registers51 authored canonical rows,
preserving every earlier Gate row. Cmd-0003 anchors the predecessor and validates34 anchors.
Cmd-0004 selects134 of135 active lessons; cmd-0005 derives185 requirements, all initially
NOT_STARTED. These are scope/entry observations, not implementation or a Gate verdict.

## Executed pre-implementation regression baseline

Cmd-0006 executes:

`python -m unittest discover -s tests -p test_gate[45]_*`

Actual result:91 tests in374.645 seconds, OK, exit0, recorded duration374995ms. The fixture's
printed FAIL is an intentionally adverse diagnostic control inside this successful suite, not
a failed baseline. No test or runtime implementation was edited to obtain this result.

## Feature boundary

services/experience still has only its reserved README. The original structural experiences table
has no Gate6 body behavior/API/retention implementation. No new experience unit/integration,
migration, live acceptance, full verifier, Green Keeper, completeness, Red Team or mirror has run.
Implementation and all acceptance obligations remain ahead; no independent M2 approval is claimed.
