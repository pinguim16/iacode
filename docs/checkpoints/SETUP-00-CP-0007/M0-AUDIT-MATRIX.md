# M0 Audit Matrix

Checkpoint: `SETUP-00-CP-0007`  
Milestone: `M0`  
Verdict: `REWORK_REQUIRED`  
Audit execution coverage: `71/71 = 100.00%`  
Evidence coverage: `71/71 = 100.00%`

`COMPLETE` means that the audit activity was fully executed and evidenced. `Outcome` records whether the audited control passed; it does not hide product failures.

| ID | Section | Dimension | Audit status | Outcome | Evidence |
|---|---|---|---|---|---|
| AUD-001 | 1,45 | Execution profile and model usage | COMPLETE | PASS | file:MILESTONE-REPORT.md<br>file:REVIEW-REPORT.md |
| AUD-002 | 2 | Auditor independence | COMPLETE | PASS | file:MILESTONE-REPORT.md<br>file:REVIEW-REPORT.md |
| AUD-003 | 3 | Cold start | COMPLETE | PASS | file:MILESTONE-REPORT.md<br>file:REVIEW-REPORT.md |
| AUD-004 | 4 | Baseline | COMPLETE | PASS | file:MILESTONE-REPORT.md<br>file:REVIEW-REPORT.md |
| AUD-005 | 5,41 | Audit control plane | COMPLETE | PASS | file:MILESTONE-REPORT.md<br>file:REVIEW-REPORT.md |
| AUD-006 | 6 | Independent audit roles | COMPLETE | PASS | file:AUDIT-EXECUTIONS.md |
| AUD-007 | 7 | M0 traceability and completeness | COMPLETE | FAIL | file:MILESTONE-REPORT.md<br>file:REVIEW-REPORT.md |
| AUD-008 | 8 | CP-0005 controls | COMPLETE | PASS | file:MILESTONE-REPORT.md<br>file:REVIEW-REPORT.md |
| AUD-009 | 9 | Inherited R3.1 | COMPLETE | FAIL | file:MILESTONE-REPORT.md<br>file:REVIEW-REPORT.md |
| AUD-010 | 9 | Inherited R3.2 | COMPLETE | FAIL | file:MILESTONE-REPORT.md<br>file:REVIEW-REPORT.md |
| AUD-011 | 9 | Inherited RT-01 | COMPLETE | PASS | file:MILESTONE-REPORT.md<br>file:REVIEW-REPORT.md |
| AUD-012 | 9,26 | Inherited RT-02 and finalization audit | COMPLETE | PASS | file:MILESTONE-REPORT.md<br>file:REVIEW-REPORT.md |
| AUD-013 | 10 | Green Keeper enforcement | COMPLETE | FAIL | file:MILESTONE-REPORT.md<br>file:REVIEW-REPORT.md |
| AUD-014 | 11 | CP-0005 completeness recomputation | COMPLETE | PASS | file:MILESTONE-REPORT.md<br>file:REVIEW-REPORT.md |
| AUD-015 | 11 | CP-0006 completeness recomputation | COMPLETE | FAIL | file:MILESTONE-REPORT.md<br>file:REVIEW-REPORT.md |
| AUD-016 | 12 | Engineering Memory structure and policy | COMPLETE | FAIL | file:MILESTONE-REPORT.md<br>file:REVIEW-REPORT.md |
| AUD-017 | 13 | Lesson schema | COMPLETE | FAIL | file:MILESTONE-REPORT.md<br>file:REVIEW-REPORT.md |
| AUD-018 | 14 | Initial lesson audit | COMPLETE | FAIL | file:MILESTONE-REPORT.md<br>file:REVIEW-REPORT.md |
| AUD-019 | 15 | Lesson preflight | COMPLETE | FAIL | file:MILESTONE-REPORT.md<br>file:REVIEW-REPORT.md |
| AUD-020 | 16 | Lesson to guardrail principle | COMPLETE | FAIL | file:MILESTONE-REPORT.md<br>file:REVIEW-REPORT.md |
| AUD-021 | 17 | Recurrence | COMPLETE | PASS | file:MILESTONE-REPORT.md<br>file:REVIEW-REPORT.md |
| AUD-022 | 18 | Retrospective | COMPLETE | PASS | file:MILESTONE-REPORT.md<br>file:REVIEW-REPORT.md |
| AUD-023 | 19 | Milestone mapping | COMPLETE | PASS | file:MILESTONE-REPORT.md<br>file:REVIEW-REPORT.md |
| AUD-024 | 20 | Internal versus external pass | COMPLETE | FAIL | file:MILESTONE-REPORT.md<br>file:REVIEW-REPORT.md |
| AUD-025 | 21 | Codex cadence | COMPLETE | PASS | file:MILESTONE-REPORT.md<br>file:REVIEW-REPORT.md |
| AUD-026 | 22 | Extraordinary external audit | COMPLETE | PASS | file:MILESTONE-REPORT.md<br>file:REVIEW-REPORT.md |
| AUD-027 | 23 | Historical integrity and compatibility | COMPLETE | FAIL | file:MILESTONE-REPORT.md<br>file:REVIEW-REPORT.md |
| AUD-028 | 24 | Detached tag validation | COMPLETE | FAIL | file:MILESTONE-REPORT.md<br>file:REVIEW-REPORT.md |
| AUD-029 | 25 | FILES inventory | COMPLETE | PASS | file:MILESTONE-REPORT.md<br>file:REVIEW-REPORT.md |
| AUD-030 | 27 | Quality evidence integrity | COMPLETE | PASS | file:MILESTONE-REPORT.md<br>file:REVIEW-REPORT.md |
| AUD-031 | 28 | Command reproducibility sampling | COMPLETE | FAIL | file:MILESTONE-REPORT.md<br>file:REVIEW-REPORT.md |
| AUD-032 | 29 | Secret safety | COMPLETE | PASS | file:MILESTONE-REPORT.md<br>file:REVIEW-REPORT.md |
| AUD-033 | 30 | Self-contained repository | COMPLETE | PASS | file:MILESTONE-REPORT.md<br>file:REVIEW-REPORT.md |
| AUD-034 | 31 | Documentation integrity | COMPLETE | FAIL | file:MILESTONE-REPORT.md<br>file:REVIEW-REPORT.md |
| AUD-035 | 32 | Full validation suite | COMPLETE | PASS | file:AUDIT-EXECUTIONS.md |
| AUD-036 | 33 | Clean-clone validation | COMPLETE | PASS | file:AUDIT-EXECUTIONS.md |
| RT-A | 34.A | READY_FOR_REVIEW with blocker | COMPLETE | DEFENDED | file:RED-TEAM-REPORT.md#attack-a |
| RT-B | 34.B | READY_FOR_REVIEW with red quality | COMPLETE | DEFENDED | file:RED-TEAM-REPORT.md#attack-b |
| RT-C | 34.C | READY_FOR_REVIEW with missing requirement | COMPLETE | ESCAPED | file:RED-TEAM-REPORT.md#attack-c |
| RT-D | 34.D | Forged completeness 100% | COMPLETE | DEFENDED | file:RED-TEAM-REPORT.md#attack-d |
| RT-E | 34.E | Lesson requirement removed | COMPLETE | DEFENDED | file:RED-TEAM-REPORT.md#attack-e |
| RT-F | 34.F | Documentation-only GUARDED lesson | COMPLETE | DEFENDED | file:RED-TEAM-REPORT.md#attack-f |
| RT-G | 34.G | Duplicate lesson IDs | COMPLETE | DEFENDED | file:RED-TEAM-REPORT.md#attack-g |
| RT-H | 34.H | Secret inserted into lesson | COMPLETE | DEFENDED | file:RED-TEAM-REPORT.md#attack-h |
| RT-I | 34.I | Historical checkpoint modified | COMPLETE | ESCAPED | file:RED-TEAM-REPORT.md#attack-i |
| RT-J | 34.J | Historical tag moved | COMPLETE | ESCAPED | file:RED-TEAM-REPORT.md#attack-j |
| RT-K | 34.K | FILES entry removed | COMPLETE | DEFENDED | file:RED-TEAM-REPORT.md#attack-k |
| RT-L | 34.L | Tracked file silently modified | COMPLETE | DEFENDED | file:RED-TEAM-REPORT.md#attack-l |
| RT-M | 34.M | Wrong hashBefore | COMPLETE | DEFENDED | file:RED-TEAM-REPORT.md#attack-m |
| RT-N | 34.N | Wrong hashAfter | COMPLETE | DEFENDED | file:RED-TEAM-REPORT.md#attack-n |
| RT-O | 34.O | Quality PASS without evidence | COMPLETE | DEFENDED | file:RED-TEAM-REPORT.md#attack-o |
| RT-P | 34.P | Nonexistent evidence reference | COMPLETE | DEFENDED | file:RED-TEAM-REPORT.md#attack-p |
| RT-Q | 34.Q | Forged second-tool validation | COMPLETE | ESCAPED | file:RED-TEAM-REPORT.md#attack-q |
| RT-R | 34.R | Internal pass forged as external | COMPLETE | ESCAPED | file:RED-TEAM-REPORT.md#attack-r |
| RT-S | 34.S | External pass without independent validation | COMPLETE | ESCAPED | file:RED-TEAM-REPORT.md#attack-s |
| RT-T | 34.T | Extraordinary audit without valid reason | COMPLETE | DEFENDED | file:RED-TEAM-REPORT.md#attack-t |
| RT-U | 34.U | Retired lesson in active preflight | COMPLETE | ESCAPED | file:RED-TEAM-REPORT.md#attack-u |
| RT-V | 34.V | Green Keeper green with red mandatory gate | COMPLETE | ESCAPED | file:RED-TEAM-REPORT.md#attack-v |
| RT-W | 34.W | Completeness PASS with PARTIAL | COMPLETE | DEFENDED | file:RED-TEAM-REPORT.md#attack-w |
| RT-X | 34.X | Malformed command or audit record | COMPLETE | DEFENDED | file:RED-TEAM-REPORT.md#attack-x |
| RT-Y | 34.Y | LATEST points to wrong checkpoint | COMPLETE | DEFENDED | file:RED-TEAM-REPORT.md#attack-y |
| RT-Z | 34.Z | Path traversal or invalid checkpoint path | COMPLETE | DEFENDED | file:RED-TEAM-REPORT.md#attack-z |
| AUD-037 | 35 | Per-attack evidence | COMPLETE | PASS | file:MILESTONE-REPORT.md<br>file:REVIEW-REPORT.md |
| AUD-038 | 36 | Audit completeness | COMPLETE | PASS | file:MILESTONE-REPORT.md<br>file:REVIEW-REPORT.md |
| AUD-039 | 37 | Failure classification | COMPLETE | PASS | file:AUDIT-EXECUTIONS.md |
| AUD-040 | 38 | Lesson candidates | COMPLETE | PASS | file:LESSON-CANDIDATES.json<br>file:LESSON-CANDIDATES.md |
| AUD-041 | 39,40 | Binary milestone verdict | COMPLETE | PASS | file:MILESTONE-REPORT.md<br>file:REVIEW-REPORT.md |
| AUD-042 | 42 | Pass transition | COMPLETE | PASS | file:MILESTONE-REPORT.md<br>file:REVIEW-REPORT.md |
| AUD-043 | 43 | Failure transition | COMPLETE | PASS | file:MILESTONE-REPORT.md<br>file:REVIEW-REPORT.md |
| AUD-044 | 44 | Engineering Memory effectiveness | COMPLETE | PASS | file:MILESTONE-REPORT.md#engineering-memory-effectiveness |
| AUD-045 | 46 | Final user response | COMPLETE | PASS | file:FINAL-REPORT.md#execution-profile |

## Recomputed summary

- Audit rows complete: 71
- Audit rows partial: 0
- Audit rows missing: 0
- Red Team defenses: 18/26
- Red Team escapes: 8/26 (`C`, `I`, `J`, `Q`, `R`, `S`, `U`, `V`)
- Product verdict: `REWORK_REQUIRED`
- Gate 0: `BLOCKED`
