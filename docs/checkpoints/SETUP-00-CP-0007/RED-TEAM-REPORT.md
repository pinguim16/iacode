# Red Team Report — M0 / SETUP-00

Result: `RED_TEAM_FAIL`  
Defense score: `18/26`  
Escapes: `8/26` — C, I, J, Q, R, S, U, V

Every attack was run in an isolated clone of `994bab402873bc4d221c02d8c94bdebeb2b0f3cb` or against an in-memory copy. No historical tag or sealed artifact in the shared repository was changed.

| Attack | Target | Mutation | Expected | Observed | Result | Evidence |
|---|---|---|---|---|---|---|
| A | readiness/blocker invariant | Add blocker to `READY_FOR_REVIEW` | reject | rejected | DEFENDED | `StatusBlockerInvariantTests.test_ready_for_review_with_blocker_fails` |
| B | mandatory quality | Set a review-ready quality gate red | reject | rejected | DEFENDED | `DeliveryAssuranceGateTests.test_red_tests_block_review` |
| C | completeness denominator | Delete mandatory `REQ-0001` and recompute all counts | reject missing source requirement | PASS at 46/46 and `CHECKPOINT_VALID` | ESCAPED | isolated `658819d` |
| D | completeness claims | Forge stored 100% counts | reject mismatch | rejected | DEFENDED | `test_completeness_report_inconsistent_with_the_matrix_is_rejected` |
| E | lesson-derived requirement | Remove a derived requirement | reject | rejected | DEFENDED | `test_a_missing_derived_requirement_blocks_completeness` |
| F | GUARDED semantics | Replace prevention with documentation only | reject | rejected | DEFENDED | `test_documentation_alone_does_not_guard_a_lesson` |
| G | lesson identity | Duplicate lesson ID | reject | rejected | DEFENDED | `test_duplicate_lesson_id_fails` |
| H | lesson secret handling | Insert a secret-shaped value in a scanned field | reject without disclosure | rejected without disclosure | DEFENDED | `test_secret_in_a_lesson_fails` |
| I | sealed predecessor | Rewrite CP-0005, declare it in CP-0006 inventory, refresh hashes, move CP-0006 tag | reject historical rewrite | `CHECKPOINT_VALID` | ESCAPED | isolated `23bce4d` |
| J | tag immutability | Move CP-0006 tag and HEAD together to a new commit | reject moved tag | `CHECKPOINT_VALID` | ESCAPED | isolated `2adc1c5` |
| K | FILES inventory | Remove one inventory entry | reject | rejected | DEFENDED | `DeltaInventoryTests.test_removed_manifest_entry_fails` |
| L | FILES inventory | Silently modify a tracked file | reject | rejected | DEFENDED | `test_silent_tracked_modification_fails` |
| M | FILES before hash | Set a wrong `hashBefore` | reject | rejected | DEFENDED | `test_wrong_hash_before_fails` |
| N | FILES after hash | Set a wrong `hashAfter` | reject | rejected | DEFENDED | `test_wrong_hash_after_fails` |
| O | quality evidence | Claim PASS with no evidence | reject | rejected | DEFENDED | `QualityEvidenceTests.test_pass_without_evidence_fails` |
| P | evidence resolution | Reference an unknown command | reject | rejected | DEFENDED | `test_pass_referencing_an_unknown_command_fails` |
| Q | second-tool evidence | Supply arbitrary complete attribution with empty evidence | reject unauthenticated validation | `CHECKPOINT_VALID` | ESCAPED | isolated `cc5c1da` |
| R | pass vocabulary | Promote an internally authored result to external status | require independent verdict | accepted | ESCAPED | isolated `4d9bef6` |
| S | external milestone review | Leave review/Red Team pending and auditor/time null | reject | accepted | ESCAPED | isolated `4d9bef6` |
| T | extraordinary cadence | Request audit without a known trigger | reject | rejected | DEFENDED | `test_an_extraordinary_audit_requires_a_recorded_trigger` |
| U | preflight freshness | Retire canonical lesson but keep stale active preflight | reject/recompute | lessons and checkpoint both valid | ESCAPED | isolated `93a7b7a` |
| V | Green Keeper mandatory set | Run `--gates ""`, then retain PASS with an actually failing test | reject/FAIL | exit 0, PASS, empty evidence; validator passed | ESCAPED | isolated `a636876`, `f707f24` |
| W | partial completeness | Claim PASS with a PARTIAL row | reject | rejected | DEFENDED | `test_partial_requirement_fails` |
| X | command audit | Remove required runtime/record field | reject | rejected | DEFENDED | `CommandReproducibilityTests` |
| Y | latest pointer | Point `LATEST.md` at CP-0005 while validating CP-0006 | reject | rejected | DEFENDED | isolated pointer mutation |
| Z | path safety | Use path traversal as checkpoint/Gate input | reject/no external write | rejected | DEFENDED | `test_new_checkpoint_rejects_path_traversal_gate` |

## Additional attacks

| ID | Mutation | Expected | Observed | Result |
|---|---|---|---|---|
| AA | CP-0006 state mandatory=47 while matrix/report=45 | reject | `CHECKPOINT_VALID` | ESCAPED |
| AB | `GUARDED` prevention points to a nonexistent test | reject | `errors=[]` | ESCAPED |
| AC | lesson evidence points to a nonexistent file | reject | `errors=[]` | ESCAPED |
| AD | secret-shaped value only in `prevention.description` | reject | `errors=[]` | ESCAPED |
| AE | GATE 1 state reuses SETUP-00 preflight | reject | no validation error | ESCAPED |
| AF | `MILESTONE_EXTERNAL_PASS` with Green Keeper FAIL | reject | no delivery-assurance error | ESCAPED |

## Conclusion

The eight mandatory escapes are product defects. A green nominal suite cannot offset them. `RED_TEAM_FAIL`; milestone M0 is `REWORK_REQUIRED`; Gate 0 is blocked.

