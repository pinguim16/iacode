# Plan

1. Reproduce the reported installation discrepancy without changing machine configuration: inspect PATH resolution, locate executable candidates, and run each candidate directly.
2. Verify Claude Code project integration mechanisms against local CLI help and official documentation; do not infer unsupported formats.
3. Preserve `SETUP-00-CP-0001` as immutable history, create this correction checkpoint, and update only current canonical documentation.
4. Add one Claude Code project-subagent adapter for each canonical role in `.iacode/agents/`, with tests for name parity, supported frontmatter, and canonical-contract delegation.
5. Attempt genuine repository-only cold-start validation from a clean clone using the detected Claude Code executable. Record authentication or execution failure truthfully.
6. Run the complete test suite, checkpoint validation, independent review, and Red Team review. Finalize and tag the correction checkpoint only when evidence is consistent.

Stop on unexpected Git divergence, an unsupported Claude adapter format, test failure, secret exposure, or any request to advance beyond SETUP-00.
