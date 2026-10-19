# Gate 7 internal Red Team

Same-session only; independent M2 audit stays pending.

Result: RED_TEAM_PASS

| Attack | Observed | Result |
|---|---|---|
| A | verdict=FAIL; reasons=('missing result for q001-unit',) | DEFENDED |
| B | contract refused non-zero PASS | DEFENDED |
| C | verdict=FAIL; reasons=('q001-unit has unresolved evidence evidence-red-team',) | DEFENDED |
| D | store refused PLAN_ID_CONFLICT | DEFENDED |
| E | store refused PLAN_ID_CONFLICT | DEFENDED |
| F | contract refused origin | DEFENDED |
| G | verdict=FAIL; reasons=('q001-unit ended TIMED_OUT',) | DEFENDED |
| H | verdict=FAIL; reasons=('q001-unit ended DENIED',) | DEFENDED |
| I | verdict=FAIL; reasons=('q001-unit ended CANCELLED',) | DEFENDED |
| J | contract refused status | DEFENDED |
| K | result=FAIL; expected-finding=True | DEFENDED |
| L | result=FAIL; expected-finding=True | DEFENDED |
| M | result=FAIL; expected-finding=True | DEFENDED |
| N | result=FAIL; expected-finding=True | DEFENDED |
| O | result=FAIL; expected-finding=True | DEFENDED |
| P | recovery=PASS; cancellation=PASS; timeout=PASS; forged-origin=PASS; secret-output=PASS | DEFENDED |
| Q | status=ERROR; verdict=FAIL; objects=0; records=0; prohibited-bytes-absent=True | DEFENDED |
| R | scan-before-store=True; status=ERROR; verdict=FAIL; objects=0; records=0 | DEFENDED |
| S | resolved=False; rescanned-after-read=True; verdict=FAIL | DEFENDED |
| T | deterministic=True; portable=True; categories=True; declaration=True; stale-refused=True | DEFENDED |
| G5-AUTH | unauthenticated-domain-refused-before-effects: PASS | DEFENDED |
| G5-TOOL-IPC | closed-ipc-refuses-tool-result: PASS | DEFENDED |
| G5-VERDICT-IPC | closed-ipc-refuses-quality-verdict: PASS | DEFENDED |
| G5-HOST-IPC | closed-ipc-refuses-shell.exec: PASS | DEFENDED |
| G5-SECRET | secret-upload-refused-before-sql-or-object-persistence: PASS | DEFENDED |
| G5-REPLAY | redis-replay-refusal-survives-api-restart: PASS | DEFENDED |
| G5-CONSENT | cli-changed-or-wrong-consent-refused-locally: PASS | DEFENDED |
| G5-TASK-LOSS | lost-response-has-one-real-persisted-run: PASS | DEFENDED |
| G5-TOOL-FORGERY | authenticated-external-sandbox-result-forgery-refused: PASS | DEFENDED |
| G5-QUALITY-LOSS | actual-quality-response-loss-reconciles-once-without-replay: PASS | DEFENDED |
| G5-SIGINT | actual-cli-sigint-stops-only-local-observation: PASS | DEFENDED |
| G5-TAMPER | actual-object-tamper-refused-before-task-persistence: PASS | DEFENDED |
| G5-NATIVE-TRUST | Actual untrusted native workspace refuses every mutation: PASS | DEFENDED |
| G6-EXPERIENCE-01 | unauthenticated-capture-refused-before-effects: PASS | DEFENDED |
| G6-EXPERIENCE-02 | invalid-signature-refused: PASS | DEFENDED |
| G6-EXPERIENCE-03 | stale-authentication-refused: PASS | DEFENDED |
| G6-EXPERIENCE-04 | consent-missing-refused-before-persistence: PASS | DEFENDED |
| G6-EXPERIENCE-05 | consent-denied-refused-before-persistence: PASS | DEFENDED |
| G6-EXPERIENCE-06 | consent-type-refused-before-persistence: PASS | DEFENDED |
| G6-EXPERIENCE-07 | private-transcript-refused-before-persistence: PASS | DEFENDED |
| G6-EXPERIENCE-08 | forged-verdict-refused-before-persistence: PASS | DEFENDED |
| G6-EXPERIENCE-09 | forged-rights-refused-before-persistence: PASS | DEFENDED |
| G6-EXPERIENCE-10 | secret-ingress-refused-before-persistence: PASS | DEFENDED |
| G6-EXPERIENCE-11 | known-capability-form-0-refused-before-persistence: PASS | DEFENDED |
| G6-EXPERIENCE-12 | known-capability-form-1-refused-before-persistence: PASS | DEFENDED |
| G6-EXPERIENCE-13 | known-capability-form-2-refused-before-persistence: PASS | DEFENDED |
| G6-EXPERIENCE-14 | known-capability-form-3-refused-before-persistence: PASS | DEFENDED |
| G6-EXPERIENCE-15 | known-capability-form-4-refused-before-persistence: PASS | DEFENDED |
| G6-EXPERIENCE-16 | known-capability-form-5-refused-before-persistence: PASS | DEFENDED |
| G6-EXPERIENCE-17 | cross-project-source-capture-refused: PASS | DEFENDED |
| G6-EXPERIENCE-18 | actual-redis-authentication-replay-refused: PASS | DEFENDED |
| G6-EXPERIENCE-19 | actual-accepted-experience-response-loss-one-durable-effect: PASS | DEFENDED |
| G6-EXPERIENCE-20 | actual-concurrent-retry-one-row-one-capture-audit: PASS | DEFENDED |
| G6-EXPERIENCE-21 | cross-project-cursor-refused: PASS | DEFENDED |
| G6-EXPERIENCE-22 | cross-project-get-refused: PASS | DEFENDED |
| G6-EXPERIENCE-23 | cross-project-delete-refused: PASS | DEFENDED |
| G6-EXPERIENCE-24 | denied-rag-use-no-data: PASS | DEFENDED |
| G6-EXPERIENCE-25 | denied-training-use-no-data: PASS | DEFENDED |
| G6-EXPERIENCE-26 | denied-distillation-use-no-data: PASS | DEFENDED |
| G6-EXPERIENCE-27 | denied-unknown-use-no-data: PASS | DEFENDED |
| G6-EXPERIENCE-28 | conflicting-stable-request-refused: PASS | DEFENDED |
| G6-EXPERIENCE-29 | authentication-replay-survives-real-restart: PASS | DEFENDED |
| G6-EXPERIENCE-30 | actual-source-object-corrupt-fails-closed: PASS | DEFENDED |
| G6-EXPERIENCE-31 | actual-source-object-remove-fails-closed: PASS | DEFENDED |
| G6-EXPERIENCE-32 | new-key-cannot-resurrect-withdrawn-source: PASS | DEFENDED |
| G6-EXPERIENCE-33 | expired-read-denied-without-manual-sweep: PASS | DEFENDED |
| G6-EXPERIENCE-34 | actual-owned-background-sweeper-physically-purged: PASS | DEFENDED |
| G6-EXPERIENCE-35 | expired-request-retry-cannot-renew: PASS | DEFENDED |
| G6-EXPERIENCE-36 | expired-source-new-key-cannot-resurrect: PASS | DEFENDED |
| G6-EXPERIENCE-37 | actual-production-logs-retain-observability-not-ingress: PASS | DEFENDED |
| G6-EXPERIENCE-38 | actual-expired-capability-refuses-experience-access: PASS | DEFENDED |
| G7-KNOWLEDGE-01 | owning-validated-storage-only-experience-cannot-be-laundered: PASS | DEFENDED |
| G7-KNOWLEDGE-02 | unauthenticated-ingestions-refused: PASS | DEFENDED |
| G7-KNOWLEDGE-03 | unauthenticated-search-refused: PASS | DEFENDED |
| G7-KNOWLEDGE-04 | unauthenticated-documents-refused: PASS | DEFENDED |
| G7-KNOWLEDGE-05 | invalid-authentication-refused: PASS | DEFENDED |
| G7-KNOWLEDGE-06 | stale-authentication-refused: PASS | DEFENDED |
| G7-KNOWLEDGE-07 | consent-missing-refused-before-effects: PASS | DEFENDED |
| G7-KNOWLEDGE-08 | consent-denied-refused-before-effects: PASS | DEFENDED |
| G7-KNOWLEDGE-09 | consent-coerced-refused-before-effects: PASS | DEFENDED |
| G7-KNOWLEDGE-10 | caller-text-refused-before-effects: PASS | DEFENDED |
| G7-KNOWLEDGE-11 | caller-path-refused-before-effects: PASS | DEFENDED |
| G7-KNOWLEDGE-12 | caller-rights-refused-before-effects: PASS | DEFENDED |
| G7-KNOWLEDGE-13 | caller-verdict-refused-before-effects: PASS | DEFENDED |
| G7-KNOWLEDGE-14 | secret-refused-before-effects: PASS | DEFENDED |
| G7-KNOWLEDGE-15 | actual-capability-refused-before-effects: PASS | DEFENDED |
| G7-KNOWLEDGE-16 | cross-project-ingestion-refused: PASS | DEFENDED |
| G7-KNOWLEDGE-17 | actual-redis-authentication-replay-refused: PASS | DEFENDED |
| G7-KNOWLEDGE-18 | actual-accepted-response-loss-one-publication: PASS | DEFENDED |
| G7-KNOWLEDGE-19 | stable-exact-request-recovers-original-publication: PASS | DEFENDED |
| G7-KNOWLEDGE-20 | cross-project-cursor-refused: PASS | DEFENDED |
| G7-KNOWLEDGE-21 | cross-project-document-get-refused: PASS | DEFENDED |
| G7-KNOWLEDGE-22 | cross-project-document-delete-refused: PASS | DEFENDED |
| G7-KNOWLEDGE-23 | actual-persistent-source-index-after-restart: PASS | DEFENDED |
| G7-KNOWLEDGE-24 | actual-corrupt-body-is-not-empty-success: PASS | DEFENDED |
| G7-KNOWLEDGE-25 | actual-missing-index-is-not-empty-success: PASS | DEFENDED |
| G7-KNOWLEDGE-26 | revoked-grant-immediately-denies-delivery: PASS | DEFENDED |
| G7-KNOWLEDGE-27 | superseded-source-immediately-denies-old-citation: PASS | DEFENDED |
| G7-KNOWLEDGE-28 | actual-rebuild-publishes-current-revision: PASS | DEFENDED |
| G7-KNOWLEDGE-29 | rebuilt-retrieval-selects-new-citation: PASS | DEFENDED |
| G7-KNOWLEDGE-30 | actual-withdrawal: PASS | DEFENDED |
| G7-KNOWLEDGE-31 | same-key-cannot-resurrect-withdrawn-revision: PASS | DEFENDED |
| G7-KNOWLEDGE-32 | new-key-cannot-resurrect-withdrawn-revision: PASS | DEFENDED |
| G7-KNOWLEDGE-33 | expiry-denial-does-not-require-manual-sweep: PASS | DEFENDED |
| G7-KNOWLEDGE-34 | owned-background-retention-physically-purges-primary-index: PASS | DEFENDED |
| G7-KNOWLEDGE-35 | changed-raw-source-immediately-denies-delivery: PASS | DEFENDED |
| G7-KNOWLEDGE-36 | missing-current-source-is-unavailable-not-empty-success: PASS | DEFENDED |
| G7-KNOWLEDGE-37 | actual-logs-retain-observability-not-private-ingress: PASS | DEFENDED |
| G7-KNOWLEDGE-38 | knowledge-never-executes-or-mutates-upstream-evidence: PASS | DEFENDED |
| G7-KNOWLEDGE-39 | upstream-experience-and-rights-remain-unchanged: PASS | DEFENDED |
| G7-KNOWLEDGE-40 | owned-resources-actually-removed: PASS | DEFENDED |
| G7-KNOWLEDGE-41 | unrelated-container-identities-and-running-states-preserved: PASS | DEFENDED |
| G7-KNOWLEDGE-42 | measured-source-inputs-unchanged: PASS | DEFENDED |
| G7-DOMAIN-01 | test_ingestion_cannot_submit_text_paths_rights_or_verdicts: PASS | DEFENDED |
| G7-DOMAIN-02 | test_missing_denied_and_wrong_type_consent_are_distinct: PASS | DEFENDED |
| G7-DOMAIN-03 | test_permission_booleans_never_coerce: PASS | DEFENDED |
| G7-DOMAIN-04 | test_ambiguous_nonfinite_nested_and_invalid_unicode_json_refused: PASS | DEFENDED |
| G7-DOMAIN-05 | test_source_grants_deny_unknown_ownership_license_authority: PASS | DEFENDED |
| G7-DOMAIN-06 | test_source_denial_revocation_and_expiry_fail_closed: PASS | DEFENDED |
| G7-DOMAIN-07 | test_project_source_revision_and_digest_must_match_grant: PASS | DEFENDED |
| G7-DOMAIN-08 | test_source_age_and_future_time_cannot_reset_capture_window: PASS | DEFENDED |
| G7-DOMAIN-09 | test_chunk_token_and_body_bounds_do_not_silently_truncate: PASS | DEFENDED |
| G7-DOMAIN-10 | test_query_defects_are_distinct_and_input_is_closed: PASS | DEFENDED |
| G7-DOMAIN-11 | test_scanner_failure_is_sanitized_and_fails_closed: PASS | DEFENDED |
| G7-API-01 | test_denied_grant_is_checked_before_actual_source_body_read: PASS | DEFENDED |
| G7-API-02 | test_wrong_project_never_opens_another_projects_grant_or_artifact: PASS | DEFENDED |
| G7-API-03 | test_actual_path_confinement_refuses_traversal_absolute_alias_and_symlink: PASS | DEFENDED |
| G7-API-04 | test_actual_nonregular_hardlinked_and_oversized_files_refused: PASS | DEFENDED |
| G7-API-05 | test_actual_secret_and_private_source_fields_refused: PASS | DEFENDED |
| G7-API-06 | test_source_grant_mismatch_expiry_unknown_fields_and_invalid_utf8_refused: PASS | DEFENDED |
| G7-API-07 | test_runtime_unexpected_task_failure_is_not_hidden: PASS | DEFENDED |
| G7-API-08 | test_dependency_failure_has_sanitized_observable_code_not_empty_success: PASS | DEFENDED |
| G7-API-09 | test_operation_timeout_is_a_real_bound_not_empty_success: PASS | DEFENDED |
| G7-SQL-01 | test_concurrent_stable_retry_and_accepted_response_loss_keep_one_fact: PASS | DEFENDED |
| G7-SQL-02 | test_conflicting_key_and_new_key_cannot_renew_same_material: PASS | DEFENDED |
| G7-SQL-03 | test_expiry_denies_before_sweep_and_bounded_purge_then_finite_gc: PASS | DEFENDED |
| G7-SQL-04 | test_policy_drift_requires_real_reindex_and_cannot_extend_original_ceiling: PASS | DEFENDED |
| G7-SQL-05 | test_grant_reindex_cannot_reset_original_retention_or_accept_changed_same_revision: PASS | DEFENDED |
| G7-SQL-06 | test_missing_indexed_audit_fails_even_with_valid_index_and_digest: PASS | DEFENDED |
| G7-SQL-07 | test_capacity_is_explicit_failure_not_silently_truncated_success: PASS | DEFENDED |
| G7-SQL-08 | test_audit_failure_rolls_back_document_and_all_index_rows: PASS | DEFENDED |
| G7-SQL-09 | test_real_immutable_guards_and_admin_corruption_are_refused: PASS | DEFENDED |
| G7-SQL-10 | test_real_source_permission_denial_and_cross_project_have_zero_sql_effects: PASS | DEFENDED |
| G7-SQL-11 | test_actual_query_projection_excludes_open_metadata_and_private_runtime_columns: PASS | DEFENDED |
| G7-SQL-12 | test_migration_zero_parity_reversible_preserves_existing_experience_identity: PASS | DEFENDED |
