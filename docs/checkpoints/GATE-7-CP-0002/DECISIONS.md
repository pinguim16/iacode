# Decisions

- Audit only the sealed `GATE-7-CP-0001` subject and accumulated Gates 4-7. Findings return to a
  later implementer; no correction is made here.
- Preserve the failed original-worktree validation separately from the clean public-clone entry.
  The authorized prior reports are neither deleted nor silently absorbed into the subject baseline.
- Use a private process-scoped Git configuration whose non-target semantics and ignore bytes were
  independently compared. Do not change global configuration or suppress stderr.
- Freeze the complete audit criteria before substantive tests. A new Critical or High finding is
  blocking but does not erase safe evidence already collected or prevent consolidation of other
  non-destructive audit checks.
- Treat the omitted `--phase` from generated `cmd-0001` as confirmed `M2-F-001`, a High recurrence
  of guarded `LSN-0010`; preserve the record exactly and return it to implementation.
- Treat the two real client-test cleanup exceptions that erased their producer results as confirmed
  `M2-F-002`, a Critical recurrence of guarded `LSN-0135`; do not repair or selectively rerun them.
- Classify the dependency null-control failure as environment-confounded because the test invokes
  real client Docker scans and engine access was denied. It remains a red suite result, not a
  product PASS or a separately confirmed vulnerability finding.
- Do not write an attestation or claim any milestone PASS unless every criterion, independent
  review, Red Team, completeness and full test obligation passes. Never claim cross-tool status.

