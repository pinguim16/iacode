# Final M2 audit matrix

Audit execution: **BLOCKED**. Review: **REWORK_REQUIRED**. Milestone PASS: **not granted**.

Criteria: 45 — PASS 14, FAIL 8, PARTIAL 7, BLOCKED 16.

| ID | Status | Criterion | Observation |
|---|---|---|---|
| `M2A-01` | `PASS` | Subject identity, state and immutability | Local and unauthenticated public identity observations agree with the declared sealed subject. |
| `M2A-02` | `PASS` | Public publication and exact refs | Local and unauthenticated public identity observations agree with the declared sealed subject. |
| `M2A-03` | `PASS` | Integrity and successor anchor | The successor rebuild added the owed subject anchor and the chain validated with 36 anchors. |
| `M2A-04` | `PARTIAL` | Published historical compatibility | Selected historical public tags and current compatibility tests passed, but an explicit detached run for every Gate 4-7 sealed predecessor was not completed. |
| `M2A-05` | `PASS` | Declared subject review transport | Independent public detached reconstructions produced the expected historical red control and exact byte-identical corrective/final archives. |
| `M2A-06` | `PASS` | Final bundle determinism and portability | Independent public detached reconstructions produced the expected historical red control and exact byte-identical corrective/final archives. |
| `M2A-07` | `PASS` | Independent G4-F-004 reconstruction | Independent public detached reconstructions produced the expected historical red control and exact byte-identical corrective/final archives. |
| `M2A-08` | `PASS` | Accumulated canonical Gate denominator | Canonical checklist/registry derivation produced 105+50+51+48=254 Gate rows. |
| `M2A-09` | `FAIL` | Accumulated lesson denominator | Two selected GUARDED lesson classes recurred as M2-F-001 and M2-F-002. |
| `M2A-10` | `BLOCKED` | Requirement evidence completeness | The Docker-dependent functional and full-verifier evidence needed to close all 404 rows could not execute; rows remain unverified rather than inferred. |
| `M2A-11` | `PARTIAL` | Architecture and ADR consistency | ADRs and boundaries were reviewed and 980 control-plane tests passed, but live cross-Gate architecture behavior could not be observed. |
| `M2A-12` | `PASS` | Gate scope and future reservations | The audit created no Gate 8 content or transition and the frozen plan prohibits Gate 8. |
| `M2A-13` | `BLOCKED` | Complete non-fast verifier | The Docker engine named pipe was inaccessible, so scripts/iacode/verify.py was not launched and no partial result was promoted. |
| `M2A-14` | `FAIL` | Test and guardrail counts | The integral control-plane suite ended red: 984 total, 980 pass, 1 skip, 1 failure and 2 errors; guardrail recurrence is nonzero. |
| `M2A-15` | `BLOCKED` | Live dependency and secret security gates | The live dependency scanners and complete secret/security gates require Docker/network execution that could not be completed. |
| `M2A-16` | `BLOCKED` | Gate 4 quality behavior | The criterion requires a real Docker/stack/native functional or isolation proof; engine access was denied and no substitute was allowed. |
| `M2A-17` | `BLOCKED` | Gate 4 containment and isolation | The criterion requires a real Docker/stack/native functional or isolation proof; engine access was denied and no substitute was allowed. |
| `M2A-18` | `BLOCKED` | Gate 5 real installed workflow | The criterion requires a real Docker/stack/native functional or isolation proof; engine access was denied and no substitute was allowed. |
| `M2A-19` | `BLOCKED` | Gate 5 interaction boundaries | The criterion requires a real Docker/stack/native functional or isolation proof; engine access was denied and no substitute was allowed. |
| `M2A-20` | `BLOCKED` | Gate 6 real experience workflow | The criterion requires a real Docker/stack/native functional or isolation proof; engine access was denied and no substitute was allowed. |
| `M2A-21` | `BLOCKED` | Gate 6 rights and lifecycle | The criterion requires a real Docker/stack/native functional or isolation proof; engine access was denied and no substitute was allowed. |
| `M2A-22` | `BLOCKED` | Gate 7 real knowledge workflow | The criterion requires a real Docker/stack/native functional or isolation proof; engine access was denied and no substitute was allowed. |
| `M2A-23` | `BLOCKED` | Gate 7 rights and lifecycle | The criterion requires a real Docker/stack/native functional or isolation proof; engine access was denied and no substitute was allowed. |
| `M2A-24` | `BLOCKED` | Cross-Gate functional integration | The criterion requires a real Docker/stack/native functional or isolation proof; engine access was denied and no substitute was allowed. |
| `M2A-25` | `BLOCKED` | Persistence and migration compatibility | The criterion requires a real Docker/stack/native functional or isolation proof; engine access was denied and no substitute was allowed. |
| `M2A-26` | `BLOCKED` | Authentication and transport integrity | The criterion requires a real Docker/stack/native functional or isolation proof; engine access was denied and no substitute was allowed. |
| `M2A-27` | `BLOCKED` | Owned test isolation and cleanup | The criterion requires a real Docker/stack/native functional or isolation proof; engine access was denied and no substitute was allowed. |
| `M2A-28` | `PARTIAL` | Inherited regression coverage | Most control-plane regressions passed, but the integral suite was red and inherited image/stack stages were not executable. |
| `M2A-29` | `PARTIAL` | Documentation and runbooks | Documentation/link controls not among the three named failures passed in the integral suite, but behavior-dependent documentation could not be compared with live execution. |
| `M2A-30` | `PARTIAL` | Provenance, rights and training policy | The audit and subject retain trainingAllowed=false and declared provenance, but unexecuted live producers prevent complete provenance observation. |
| `M2A-31` | `FAIL` | Lessons and guardrail effectiveness | M2-F-001 and M2-F-002 are confirmed guardrail recurrences; zero recurrence failure is false. |
| `M2A-32` | `FAIL` | Reproducible command ledger | cmd-0001 omits the consumed --phase option/value, and the canonical validator accepts that non-literal record. |
| `M2A-33` | `PASS` | Internal versus independent evidence separation | Internal subject claims were not adopted; this later session generated its own public, test and Red Team observations. |
| `M2A-34` | `FAIL` | Independent code and architecture review | Independent review has one open Critical and one open High finding. |
| `M2A-35` | `FAIL` | Independent Red Team | A valid-baseline independent mutation escaped; the remaining M2 attack battery was blocked by the inaccessible engine. |
| `M2A-36` | `PARTIAL` | Adversarial premise validity | M2-RT-01 proved its marker was consumed and its clean control was VALID, but the complete battery could not execute. |
| `M2A-37` | `FAIL` | Risks, debt and prior findings | M2-F-001 (High) and M2-F-002 (Critical) remain open and require an implementing checkpoint. |
| `M2A-38` | `BLOCKED` | Fresh public no-credential proof | Fresh public no-credential validation passed, but complete verification could not start without Docker Engine access. |
| `M2A-39` | `PASS` | Exact final review transport | Independent public detached reconstructions produced the expected historical red control and exact byte-identical corrective/final archives. |
| `M2A-40` | `FAIL` | Audit checkpoint assurance | The audit checkpoint cannot pass its own assurance: command evidence is defective, Red Team failed, completeness is incomplete and Docker gates are blocked. |
| `M2A-41` | `PARTIAL` | Audit delivery completeness | The report preserves commands, findings, attempts and limitations, but mandatory live/full evidence is incomplete. |
| `M2A-42` | `PASS` | Second-tool availability truth | Codex/OpenAI/GPT-5 fresh-session attribution is explicit and cross-tool validation is truthfully NOT_AVAILABLE. |
| `M2A-43` | `PASS` | Independent attestation eligibility | Eligibility is false and no attestation was written. |
| `M2A-44` | `PASS` | Milestone verdict derivation | The evidence derives BLOCKED/REWORK_REQUIRED and grants neither independent nor external milestone PASS. |
| `M2A-45` | `PASS` | No Gate 8 advancement | No Gate 8 work or transition was created. |
