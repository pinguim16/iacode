"""Fresh same-session Red Team, strictly after complete Green Keeper and audit-only DCV.

Every producer uses a previously absent unique output path. Safe exact bytes are retained in a
finally block before JSON interpretation. Inherited attack membership is preserved, not its
historical verdict. This is never independent M2 review or cross-tool validation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import uuid
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))

DESKTOP_ATTACKS = [
    ("G5-AUTH", "unauthenticated-domain-refused-before-effects"),
    ("G5-TOOL-IPC", "closed-ipc-refuses-tool-result"),
    ("G5-VERDICT-IPC", "closed-ipc-refuses-quality-verdict"),
    ("G5-HOST-IPC", "closed-ipc-refuses-shell.exec"),
    ("G5-SECRET", "secret-upload-refused-before-sql-or-object-persistence"),
    ("G5-REPLAY", "redis-replay-refusal-survives-api-restart"),
    ("G5-CONSENT", "cli-changed-or-wrong-consent-refused-locally"),
    ("G5-TASK-LOSS", "lost-response-has-one-real-persisted-run"),
    ("G5-TOOL-FORGERY", "authenticated-external-sandbox-result-forgery-refused"),
    ("G5-QUALITY-LOSS", "actual-quality-response-loss-reconciles-once-without-replay"),
    ("G5-SIGINT", "actual-cli-sigint-stops-only-local-observation"),
    ("G5-TAMPER", "actual-object-tamper-refused-before-task-persistence"),
]
EXPERIENCE_ATTACKS = [
    "unauthenticated-capture-refused-before-effects",
    "invalid-signature-refused",
    "stale-authentication-refused",
    "consent-missing-refused-before-persistence",
    "consent-denied-refused-before-persistence",
    "consent-type-refused-before-persistence",
    "private-transcript-refused-before-persistence",
    "forged-verdict-refused-before-persistence",
    "forged-rights-refused-before-persistence",
    "secret-ingress-refused-before-persistence",
    *[f"known-capability-form-{index}-refused-before-persistence" for index in range(6)],
    "cross-project-source-capture-refused",
    "actual-redis-authentication-replay-refused",
    "actual-accepted-experience-response-loss-one-durable-effect",
    "actual-concurrent-retry-one-row-one-capture-audit",
    "cross-project-cursor-refused",
    "cross-project-get-refused",
    "cross-project-delete-refused",
    *[f"denied-{use}-use-no-data" for use in ("rag", "training", "distillation", "unknown")],
    "conflicting-stable-request-refused",
    "authentication-replay-survives-real-restart",
    "actual-source-object-corrupt-fails-closed",
    "actual-source-object-remove-fails-closed",
    "new-key-cannot-resurrect-withdrawn-source",
    "expired-read-denied-without-manual-sweep",
    "actual-owned-background-sweeper-physically-purged",
    "expired-request-retry-cannot-renew",
    "expired-source-new-key-cannot-resurrect",
    "actual-production-logs-retain-observability-not-ingress",
    "actual-expired-capability-refuses-experience-access",
]
KNOWLEDGE_ATTACKS = [
    "owning-validated-storage-only-experience-cannot-be-laundered",
    "unauthenticated-ingestions-refused",
    "unauthenticated-search-refused",
    "unauthenticated-documents-refused",
    "invalid-authentication-refused",
    "stale-authentication-refused",
    "consent-missing-refused-before-effects",
    "consent-denied-refused-before-effects",
    "consent-coerced-refused-before-effects",
    "caller-text-refused-before-effects",
    "caller-path-refused-before-effects",
    "caller-rights-refused-before-effects",
    "caller-verdict-refused-before-effects",
    "secret-refused-before-effects",
    "actual-capability-refused-before-effects",
    "cross-project-ingestion-refused",
    "actual-redis-authentication-replay-refused",
    "actual-accepted-response-loss-one-publication",
    "stable-exact-request-recovers-original-publication",
    "cross-project-cursor-refused",
    "cross-project-document-get-refused",
    "cross-project-document-delete-refused",
    "actual-persistent-source-index-after-restart",
    "actual-corrupt-body-is-not-empty-success",
    "actual-missing-index-is-not-empty-success",
    "revoked-grant-immediately-denies-delivery",
    "superseded-source-immediately-denies-old-citation",
    "actual-rebuild-publishes-current-revision",
    "rebuilt-retrieval-selects-new-citation",
    "actual-withdrawal",
    "same-key-cannot-resurrect-withdrawn-revision",
    "new-key-cannot-resurrect-withdrawn-revision",
    "expiry-denial-does-not-require-manual-sweep",
    "owned-background-retention-physically-purges-primary-index",
    "changed-raw-source-immediately-denies-delivery",
    "missing-current-source-is-unavailable-not-empty-success",
    "actual-logs-retain-observability-not-private-ingress",
    "knowledge-never-executes-or-mutates-upstream-evidence",
    "upstream-experience-and-rights-remain-unchanged",
    "owned-resources-actually-removed",
    "unrelated-container-identities-and-running-states-preserved",
    "measured-source-inputs-unchanged",
]
DOMAIN_ATTACKS = [
    "test_ingestion_cannot_submit_text_paths_rights_or_verdicts",
    "test_missing_denied_and_wrong_type_consent_are_distinct",
    "test_permission_booleans_never_coerce",
    "test_ambiguous_nonfinite_nested_and_invalid_unicode_json_refused",
    "test_source_grants_deny_unknown_ownership_license_authority",
    "test_source_denial_revocation_and_expiry_fail_closed",
    "test_project_source_revision_and_digest_must_match_grant",
    "test_source_age_and_future_time_cannot_reset_capture_window",
    "test_chunk_token_and_body_bounds_do_not_silently_truncate",
    "test_query_defects_are_distinct_and_input_is_closed",
    "test_scanner_failure_is_sanitized_and_fails_closed",
]
API_ATTACKS = [
    "test_denied_grant_is_checked_before_actual_source_body_read",
    "test_wrong_project_never_opens_another_projects_grant_or_artifact",
    "test_actual_path_confinement_refuses_traversal_absolute_alias_and_symlink",
    "test_actual_nonregular_hardlinked_and_oversized_files_refused",
    "test_actual_secret_and_private_source_fields_refused",
    "test_source_grant_mismatch_expiry_unknown_fields_and_invalid_utf8_refused",
    "test_runtime_unexpected_task_failure_is_not_hidden",
    "test_dependency_failure_has_sanitized_observable_code_not_empty_success",
    "test_operation_timeout_is_a_real_bound_not_empty_success",
]
SQL_ATTACKS = [
    "test_concurrent_stable_retry_and_accepted_response_loss_keep_one_fact",
    "test_conflicting_key_and_new_key_cannot_renew_same_material",
    "test_expiry_denies_before_sweep_and_bounded_purge_then_finite_gc",
    "test_policy_drift_requires_real_reindex_and_cannot_extend_original_ceiling",
    "test_grant_reindex_cannot_reset_original_retention_or_accept_changed_same_revision",
    "test_missing_indexed_audit_fails_even_with_valid_index_and_digest",
    "test_capacity_is_explicit_failure_not_silently_truncated_success",
    "test_audit_failure_rolls_back_document_and_all_index_rows",
    "test_real_immutable_guards_and_admin_corruption_are_refused",
    "test_real_source_permission_denial_and_cross_project_have_zero_sql_effects",
    "test_actual_query_projection_excludes_open_metadata_and_private_runtime_columns",
    "test_migration_zero_parity_reversible_preserves_existing_experience_identity",
]


def archive_original(source: Path, label: str):
    from ledger_common import find_secrets, utc_now, write_json

    if source.is_symlink() or source.is_junction() or not source.is_file():
        raise ValueError("a regular current original producer is required")
    resolved = source.resolve(strict=True)
    if not resolved.is_relative_to(ROOT.resolve()):
        raise ValueError("producer escaped the exact owned workspace")
    raw = source.read_bytes()
    if find_secrets(raw.decode("utf-8", errors="strict")):
        raise ValueError("unsafe original producer cannot be transported")
    directory = CHECKPOINT / "attempts"
    if directory.is_symlink() or directory.is_junction():
        raise ValueError("redirected raw producer archive refused")
    destination = directory / ("RT-" + label + "-" + uuid.uuid4().hex + ".json")
    with destination.open("xb") as output:
        output.write(raw)
    if destination.read_bytes() != raw:
        raise ValueError("original Red Team byte equality failed")
    receipt = {
        "kind": "UNINTERPRETED_ORIGINAL_RED_TEAM_PRODUCER_NOT_ACCEPTANCE",
        "observedAt": utc_now(),
        "source": source.relative_to(ROOT).as_posix(),
        "artifact": destination.relative_to(CHECKPOINT).as_posix(),
        "sizeBytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "acceptanceGranted": False,
    }
    write_json(destination.with_name(destination.stem + "-RECEIPT.json"), receipt)
    return destination, receipt


def execute(arguments, label, source=None):
    from execute_gate import preserve_execution

    before = set((CHECKPOINT / "suite-attempts").glob("RT-" + label + "-*.json"))
    original = None
    try:
        code = preserve_execution(
            ["python", *arguments],
            "RT-" + label,
            "FRESH_POST_GREENKEEPER_DCV_INTERNAL_RED_TEAM",
            label,
        )
    finally:
        if source is not None and source.is_file():
            original, _ = archive_original(source, label)
    after = set((CHECKPOINT / "suite-attempts").glob("RT-" + label + "-*.json"))
    created = after - before
    if len(created) != 1:
        raise ValueError("one actual process receipt must resolve")
    receipt_path = created.pop()
    receipt = json.loads(receipt_path.read_bytes())
    return {
        "exitCode": code,
        "receipt": receipt_path.relative_to(CHECKPOINT).as_posix(),
        "original": original.relative_to(CHECKPOINT).as_posix() if original else None,
        "result": receipt["result"],
        "sourceUnchanged": receipt["sourceUnchanged"],
    }


def main() -> int:
    from ledger_common import use_utf8_stdout

    use_utf8_stdout()
    from delivery_assurance import collect_test_ids, completeness_scope
    from ledger_common import (
        LedgerError,
        load_json,
        scope_fingerprint,
        utc_now,
        validate_schema,
        write_json,
    )
    from validate_checkpoint import _validate_green_keeper_cycle

    if load_json(CHECKPOINT / "STATE.json")["status"] != "IN_PROGRESS":
        raise LedgerError("never write Red Team into a terminal or sealed subject")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--node", required=True, type=Path)
    options = parser.parse_args()
    destination = CHECKPOINT / "M2-INTERNAL-RED-TEAM.json"
    if destination.exists():
        raise LedgerError("preserve an existing Red Team before another execution")
    fingerprint = scope_fingerprint(ROOT)
    cycles = [
        json.loads(line)
        for line in (CHECKPOINT / "REWORK-LOG.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    errors = []
    if not cycles or cycles[-1].get("result") != "GREEN":
        raise LedgerError("the actual whole mandatory Green Keeper must pass first")
    _validate_green_keeper_cycle(ROOT, {}, cycles[-1], errors, closure=True)
    complete = load_json(CHECKPOINT / "COMPLETENESS-REPORT.json")
    if (
        errors
        or complete.get("result") != "PASS"
        or complete.get("scopeFingerprint")
        != scope_fingerprint(ROOT, completeness_scope(ROOT, CHECKPOINT))
    ):
        raise LedgerError("current audit-only DCV must pass after the complete Green Keeper")
    if (ROOT / "var").is_symlink() or (ROOT / "var").is_junction():
        raise LedgerError("redirected fresh producer parent refused")
    nonce = uuid.uuid4().hex
    paths = {
        key: ROOT / "var" / ("gate7-red-team-" + nonce + "-" + key + ".json")
        for key in ("native", "desktop", "experience", "knowledge")
    }
    if any(path.exists() or path.is_symlink() for path in paths.values()):
        raise LedgerError("a fresh unique absent producer destination is required")
    receipts = []
    inherited_run = execute(
        ["scripts/development-ledger/gate4_red_team.py", "--write"], "INHERITED", destination
    )
    receipts.append(inherited_run)
    if not inherited_run["original"]:
        write_json(CHECKPOINT / "RED-TEAM-EXECUTIONS.json", receipts)
        raise LedgerError("fresh inherited producer is absent; no stale PASS is accepted")
    base = load_json(CHECKPOINT / inherited_run["original"])
    write_json(CHECKPOINT / "M2-INHERITED-RED-TEAM.json", base)
    destination.unlink()
    # The escaped corrective obligations are policy-derived additions, never replacements
    # for the complete inherited/runtime battery below. Execute the canonical fixture and
    # its actual validator/null control; do not credit a targeted unit run as this Red Team.
    from policies import audit_attacks, open_audits
    from m0_red_team import build_attacks
    registered = {row["id"]: row for audit in open_audits(ROOT, "GATE-7", CHECKPOINT.name)
                  for row in audit_attacks(ROOT, audit) if row["mandatory"] == "true"}
    implementations = {row["attackId"]: row for row in build_attacks()}
    if not registered or set(registered) - set(implementations):
        raise LedgerError("complete registered corrective attack implementations required")
    corrective_run = execute(["scripts/development-ledger/m0_red_team.py", "--only",
                              ",".join(sorted(registered))], "CORRECTIVE")
    receipts.append(corrective_run)
    corrective_receipt = load_json(CHECKPOINT / corrective_run["receipt"])
    artifact = corrective_receipt.get("safeOutputArtifact")
    if not artifact:
        raise LedgerError("original canonical corrective Red Team output required")
    raw = (ROOT / artifact).read_bytes()
    if (len(raw) != corrective_receipt["outputBytes"]
            or hashlib.sha256(raw).hexdigest() != corrective_receipt["outputSha256"]):
        raise LedgerError("corrective Red Team original bytes mismatch")
    text = raw.decode("utf-8", errors="strict")
    observations = re.findall(r"^\[([^\]]+)\] (DEFENDED|ESCAPED) (.*)$", text, flags=re.M)
    observed_ids = [row[0] for row in observations]
    if set(observed_ids) != set(registered) or len(observed_ids) != len(set(observed_ids)):
        raise LedgerError("canonical corrective attack execution membership differs from policy")
    corrective_attacks = [{key: implementations[identifier][key]
                           for key in ("attackId", "target", "mutation", "expectedDefense", "origin")}
                          | {"description": implementations[identifier]["mutation"],
                             "mandatory": True, "observed": observed, "result": result,
                             "evidence": ["checkpoint:" + corrective_run["receipt"],
                                          "file:" + artifact]}
                          for identifier, result, observed in observations]
    for arguments, label in (
        (["scripts/iacode/gates/client_tests.py"], "CLIENT"),
        (["scripts/iacode/gates/knowledge_tests.py"], "DOMAIN"),
        (["scripts/iacode/gates/api_tests.py"], "API"),
        (
            [
                CHECKPOINT.relative_to(ROOT).as_posix()
                + "/audit-harness/run_knowledge_integration.py"
            ],
            "SQL",
        ),
    ):
        receipts.append(execute(arguments, label))
    for key, arguments in (
        ("native", ["scripts/iacode/native_editor.py"]),
        (
            "desktop",
            [
                "scripts/iacode/scenarios/desktop_e2e.py",
                "--node",
                str(options.node.resolve(strict=True)),
            ],
        ),
        ("experience", ["scripts/iacode/scenarios/experience_store_e2e.py"]),
        ("knowledge", ["scripts/iacode/scenarios/knowledge_engine_e2e.py"]),
    ):
        receipts.append(
            execute(
                [*arguments, "--report", paths[key].relative_to(ROOT).as_posix()],
                key.upper(),
                paths[key],
            )
        )
    write_json(CHECKPOINT / "RED-TEAM-EXECUTIONS.json", receipts)
    producers = {}
    for key, receipt in zip(
        ("native", "desktop", "experience", "knowledge"), receipts[-4:], strict=True
    ):
        producers[key] = load_json(CHECKPOINT / receipt["original"]) if receipt["original"] else {}
        write_json(CHECKPOINT / ("RED-TEAM-" + key.upper() + ".json"), producers[key])
    desktop, native = producers["desktop"], producers["native"]
    experience, knowledge = producers["experience"], producers["knowledge"]
    desktop_steps = {row["name"]: row for row in desktop.get("steps", [])}
    experience_steps = {row["name"]: row for row in experience.get("steps", [])}
    knowledge_steps = {row["name"]: row for row in knowledge.get("steps", [])}
    corpus = load_json(ROOT / "services/knowledge/tests/fixtures/retrieval-corpus.json")
    measurements = knowledge.get("retrievalMeasurements", [])
    measured = len(measurements) == len(corpus["queries"]) and all(
        row.get("result") == "PASS"
        and row.get("queryOrdinal") == index
        and row.get("expectedSources") == query["expectedSources"]
        and row.get("observedHits") == len(query["expectedSources"])
        for index, (row, query) in enumerate(zip(measurements, corpus["queries"], strict=True))
    )
    clean = (
        all(
            row["exitCode"] == 0 and row["result"] == "PASS" and row["sourceUnchanged"]
            for row in receipts
        )
        and base.get("baselineControl", {}).get("result") == "VALID"
        and base.get("result") == "RED_TEAM_PASS"
        and all(producer.get("result") == "PASS" for producer in producers.values())
        and desktop.get("sourceFingerprint") == fingerprint
        and experience.get("sourceFingerprint") == fingerprint
        and knowledge.get("sourceFingerprint") == fingerprint
        and desktop.get("ownedTemporaryDirectoryRemoved") is True
        and native.get("ownedTemporaryDirectoryRemoved") is True
        and all(row.get("result") == "PASS" for row in experience.get("steps", []))
        and all(row.get("result") == "PASS" for row in knowledge.get("steps", []))
        and desktop_steps.get(
            "actual-new-host-secretstorage-recovery-provider-sandbox-quality", {}
        ).get("result")
        == "PASS"
        and experience_steps.get("authentication-null-control", {}).get("result") == "PASS"
        and experience_steps.get("actual-source-bound-experience-captured", {}).get("result")
        == "PASS"
        and knowledge_steps.get("actual-body-restoration-null-control", {}).get("result") == "PASS"
        and knowledge_steps.get("actual-content-bound-synthetic-source-grants-deployed", {}).get(
            "result"
        )
        == "PASS"
        and measured
    )
    attacks = [*base["attacks"], *corrective_attacks]

    def append_attack(identifier, name, passed, target, evidence):
        attacks.append(
            {
                "attackId": identifier,
                "description": name,
                "target": target,
                "mutation": name,
                "expectedDefense": (
                    "Refuse unsafe effects or disclosure beside an actual "
                    "successful clean control; "
                    "preserve bounded scoped facts and truthful failures."
                ),
                "observed": name + ": " + ("PASS" if passed else "NOT_PASSED"),
                "result": "DEFENDED" if clean and passed else "ESCAPED",
                "mandatory": True,
                "origin": "Fresh same-session Gate7 internal Red Team after whole Green Keeper/DCV",
                "evidence": evidence,
            }
        )

    for identifier, name in DESKTOP_ATTACKS:
        append_attack(
            identifier,
            name,
            desktop_steps.get(name, {}).get("result") == "PASS",
            "Actual authenticated desktop runtime; no client execution/verdict authority",
            ["checkpoint:RED-TEAM-DESKTOP.json", "checkpoint:RED-TEAM-EXECUTIONS.json"],
        )
    trust = [
        row
        for run in native.get("runs", [])
        for row in run["steps"]
        if row["name"] == "actual-untrusted-workspace-refuses-every-mutation-before-connection"
    ]
    append_attack(
        "G5-NATIVE-TRUST",
        "Actual untrusted native workspace refuses every mutation",
        len(trust) == 1 and trust[0]["result"] == "PASS",
        "Real isolated installed VS Code Extension Host, not an editor API double",
        ["checkpoint:RED-TEAM-NATIVE.json", "checkpoint:RED-TEAM-DESKTOP.json"],
    )
    for index, name in enumerate(EXPERIENCE_ATTACKS, 1):
        append_attack(
            f"G6-EXPERIENCE-{index:02d}",
            name,
            experience_steps.get(name, {}).get("result") == "PASS",
            "Actual authenticated Experience Store/source objects/finite retention",
            ["checkpoint:RED-TEAM-EXPERIENCE.json", "checkpoint:RED-TEAM-EXECUTIONS.json"],
        )
    for index, name in enumerate(KNOWLEDGE_ATTACKS, 1):
        append_attack(
            f"G7-KNOWLEDGE-{index:02d}",
            name,
            knowledge_steps.get(name, {}).get("result") == "PASS",
            "Actual authenticated knowledge, real source/grant/SQL/retrieval/citation/lifecycle",
            ["checkpoint:RED-TEAM-KNOWLEDGE.json", "checkpoint:RED-TEAM-EXECUTIONS.json"],
        )
    discovered = collect_test_ids(ROOT)
    for family, names, path in (
        ("DOMAIN", DOMAIN_ATTACKS, "services/knowledge/tests/test_domain.py"),
        ("API", API_ATTACKS, "apps/api/tests/unit/test_knowledge_api.py"),
        ("SQL", SQL_ATTACKS, "apps/api/tests/integration/test_knowledge_engine.py"),
    ):
        for index, name in enumerate(names, 1):
            # The complete owning collection actually ran above. The static resolver separately
            # refuses a misspelled/nonexistent case; it does not substitute for that execution.
            exists = name in discovered
            append_attack(
                f"G7-{family}-{index:02d}",
                name,
                exists,
                (
                    "Complete fresh owning " + family + " suite. Domain/unit doubles prove only "
                    "their declared decisions/filesystem boundary; SQL is actual PostgreSQL."
                ),
                ["file:" + path, "checkpoint:RED-TEAM-EXECUTIONS.json"],
            )
    inherited_ids = {
        row["attackId"]
        for row in load_json(ROOT / "docs/checkpoints/GATE-6-CP-0001/M2-INTERNAL-RED-TEAM.json")[
            "attacks"
        ]
    }
    actual_ids = [row["attackId"] for row in attacks]
    if not inherited_ids.issubset(actual_ids) or len(set(actual_ids)) != len(actual_ids):
        raise LedgerError("an inherited attack disappeared or a current attack identifier repeats")
    unchanged = scope_fingerprint(ROOT) == fingerprint
    escaped = sum(row["result"] != "DEFENDED" for row in attacks)
    report = {
        "schemaVersion": "1.1.0",
        "checkpoint": CHECKPOINT.name,
        "generatedAt": utc_now(),
        "targetFingerprint": fingerprint,
        "source": (
            "Fresh inherited false-PASS battery, whole client/domain/API and real knowledge SQL "
            "suites, actual installed native/desktop, Experience Store and measured Knowledge "
            "Engine adversaries. Same-session internal only; not independent M2 attestation."
        ),
        "baselineControl": {
            "result": "VALID" if clean and unchanged else "INVALID",
            "detail": (
                "Fresh inherited null mutation, trusted native/provider/sandbox/quality, owning "
                "Experience capture, positive rights-qualified corpus with all exact predefined "
                "queries/citations, actual body restoration and unchanged measured source."
            ),
            "evidence": [
                "checkpoint:M2-INHERITED-RED-TEAM.json",
                "checkpoint:RED-TEAM-DESKTOP.json",
                "checkpoint:RED-TEAM-EXPERIENCE.json",
                "checkpoint:RED-TEAM-KNOWLEDGE.json",
            ],
        },
        "attacks": attacks,
        "total": len(attacks),
        "defended": len(attacks) - escaped,
        "escaped": escaped,
        "mandatoryTotal": len(attacks),
        "mandatoryDefended": len(attacks) - escaped,
        "result": "RED_TEAM_PASS" if not escaped and clean and unchanged else "RED_TEAM_FAIL",
    }
    errors = validate_schema(
        report, load_json(ROOT / ".iacode/schemas/red-team-report.schema.json")
    )
    if errors:
        raise LedgerError("actual Red Team report schema refused: " + str(errors))
    write_json(destination, report)
    lines = [
        "# Gate 7 internal Red Team",
        "",
        "Same-session only; independent M2 audit stays pending.",
        "",
        "Result: " + report["result"],
        "",
        "| Attack | Observed | Result |",
        "|---|---|---|",
    ]
    lines.extend(
        f"| {row['attackId']} | {row['observed'].replace('|', '/')} | {row['result']} |"
        for row in attacks
    )
    (CHECKPOINT / "RED-TEAM-REPORT.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8", newline="\n"
    )
    print(
        f"INTERNAL_RED_TEAM={report['result']} defended={report['defended']}/{report['total']} "
        f"control={report['baselineControl']['result']}"
    )
    return 0 if report["result"] == "RED_TEAM_PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
