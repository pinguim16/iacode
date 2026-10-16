# Gate 5 baseline

## Immutable entry

Before this checkpoint existed, Gate 4 CP0010 was canonically sealed and published at
44f6da5b092b5f3243331253ca4fc2bf7c45d603. Its exact remote detached checkout passed its own
validator, current integrity validation and reproducible review-bundle declaration. The clone
was clean before and after and was removed. The final regenerated ZIP SHA-256 is
a76ab2cf0382b75fe40d2c9b16d073c64076a14f364e057833f7c696be71ba78 (1,758,438 bytes, 332 entries).
These are earlier same-session observations, not independent validation or new Gate 5 commands.

Gate 5 began on clean main at that SHA. Cmd-0001 created the separate checkpoint. Cmd-0002
anchored the predecessor and validated all 33 anchors. No sealed predecessor was edited. The
canonical rebuilder recomputed successor hash links in its existing name order; historical tag,
commit and tree identities are unchanged. Cmd-0003 selected 115 of 116 lessons. Cmd-0004 derived
50 canonical plus 115 lesson obligations, all initially NOT_STARTED. Cmd-0005/0006 observed and
validated G5-S00 against actual local/remote Git.

## Executed pre-implementation regression baseline

Cmd-0007 was refused before execution: the recorder interpreted the bare test filename in
unittest's pattern argument as a missing repository-relative script. The refusal is preserved;
it is not a test execution or a PASS. Cmd-0008 used an executable portable discovery pattern:

`python -m unittest discover -s tests -p test_gate4_*`

Actual result: exit 1, 343,907 ms; 49 tests in 343.524 seconds, 6 failures and 1 error. The
reservation subtests account for two reported failure traces within one failing test method.

The six affected methods (seven failure/error records) share one cause:
`GATE = delivered_gate(PROJECT_ROOT)` selected Gate 5
while SPECIFICATION, expected functional identifiers, reservation ownership and the comparison
fixture remained explicitly historical Gate 4. The dropped-row negative fixture copied only the
Gate 4 specification but selected Gate 5's registry entry. The timestamp comparison fixture also
compared Gate 5 to itself. This is G5-INT-001, a recurrence of LSN-0084 / GRD-0085, not a failure of
Gate 4's immutable delivered product. The lesson is reopened and escalated before correction.

## Initial feature boundary

Both client directories still contain only reserved READMEs. No extension or CLI runtime has
been implemented, installed or functionally accepted in this checkpoint. No Green Keeper,
completeness, internal Red Team, mirror or independent verdict is claimed.
