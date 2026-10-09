# Independent M1 Review Report

## Verdict

`APPROVED` for the sealed subject `GATE-3-CP-0005` at
`3ef2bf77ddbddd378d35f5c4d32f2d90d42fc97d`.

This is a fresh-session audit by Codex desktop application, OpenAI, GPT-5. It is not cross-tool
validation. The mechanism is `FRESH_SESSION_INDEPENDENT_AUDIT`, and the attestation records
`crossToolValidation=NOT_AVAILABLE`.

## Basis

- Every sealed M1 checkpoint validates locally at its canonical tag and from a transport clone of
  the authorised remote. Every commit named by sealed evidence is reachable from published refs.
- The full non-fast verification passed all 32 stages in a fresh clone. The current canonical count
  is 1,551 discovered and 1,551 passed, deduplicated by physical execution.
- Fresh npm and PyPI scans reached both mandatory sources and reported zero Critical and zero High
  findings.
- The configured model completed a real task through Agent Runtime, Model Gateway, seven canonical
  ToolRequests, Sandbox execution and authoritative ToolResults, with zero repair, no host change
  and no surviving container.
- External ToolResults were refused during and after a Sandbox-owned execution; the Sandbox timeout
  remained the stored and consumed result.
- R-G3-001 passed ten controls and a fresh engine-argument attack. No untrusted input reached an
  arbitrary engine operation.
- The dedicated terminal SSE test delivered every event across more than two pages.
- The independent milestone Red Team defended 19 of 19 attacks over a valid null control.
- The 198 derived requirements have total implementation and evidence coverage.

## Findings

Critical: zero. High: zero. Medium: zero. Low: one.

`M1-F-005` records nondeterminism in a broader audit prompt that exhausted its turn budget only
after multiple valid end-to-end tool cycles. It does not contradict the separate terminal
`SUCCEEDED` proof and is non-blocking. The auditor did not implement its recommended correction.

The first Red Team report was invalid because the audit reader looked for the null control in the
wrong JSON location. It is preserved with its hash and cause. The reader was corrected without
changing product code or the attack, and the full battery repeated successfully.

## Scope boundary

No product, test, policy, prompt, historical checkpoint or historical tag changed. Gate 4 was not
started. This checkpoint adds only the predecessor anchor, audit evidence, the audit harness and the
attestation.
