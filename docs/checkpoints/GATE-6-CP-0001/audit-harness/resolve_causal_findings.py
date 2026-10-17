"""Restore causal guards only after completed current local executions, never a Gate verdict."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))
from ledger_common import load_json, scope_fingerprint, utc_now, use_utf8_stdout, write_json
from lessons import load_lessons, save_lessons


def main() -> int:
    if load_json(CHECKPOINT / "STATE.json")["status"] != "IN_PROGRESS" or (CHECKPOINT / "CHECKSUMS.sha256").exists():
        raise ValueError("an unsealed current implementing checkpoint is required")
    records = [json.loads(line) for line in (CHECKPOINT / "COMMANDS.jsonl").read_text(
        encoding="utf-8").splitlines() if line.strip()]
    sequences = [row for row in records if row.get("exitCode") == 0
                 and "audit-harness/run_pre_live_sequence.py" in row["command"]]
    if not sequences:
        raise ValueError("completed complete current pre-live command required")
    sequence = sequences[-1]
    progress = load_json(CHECKPOINT / "PRE-LIVE-PROGRESS.json")
    expected = ["mechanical-format", "whole-mandatory-lint", "complete-domain-and-api-unit",
                "whole-mandatory-client-tests", "complete-gate6-root", "actual-owned-provider-sandbox-experience"]
    fingerprint = scope_fingerprint(ROOT)
    if (progress["status"] != "PASS" or [row["name"] for row in progress["phases"]] != expected
            or any(row["exitCode"] != 0 for row in progress["phases"])
            or progress["sourceFingerprintAfter"] != fingerprint):
        raise ValueError("every complete local phase must pass against unchanged current source")
    for suite in ("DOMAIN", "API-UNIT", "INTEGRATION"):
        path = sorted((CHECKPOINT / "suite-attempts").glob(suite + "-*.json"))[-1]
        report = load_json(path)
        if report["result"] != "PASS" or not report["sourceUnchanged"] or report["sourceFingerprint"] != fingerprint:
            raise ValueError("actual complete unchanged local suite missing: " + suite)
        if suite == "INTEGRATION" and (not report["operationalContainerIdentitiesPreserved"]
                or report["missingOriginalContainerIdentities"]):
            raise ValueError("unchanged original operational identities must be observed")
    receipt = load_json(sorted((CHECKPOINT / "attempts").glob("EXPERIENCE-LIVE-*-RECEIPT.json"))[-1])
    raw = (ROOT / receipt["producerArchive"]).read_bytes()
    if (receipt["result"] != "PASS" or receipt["sourceFingerprint"] != fingerprint
            or receipt["failedControls"] or hashlib.sha256(raw).hexdigest() != receipt["producerSha256"]):
        raise ValueError("fresh exact successful actual live source capture is required")
    registry = load_json(ROOT / ".iacode/memory/guardrails/registry.json")
    fresh = (
        ("GRD-0138", "LSN-0136", "Strict JSON context survives exact permission validation",
         ["test_exact_closed_roundtrip", "test_permissions_require_exact_boolean", "test_numeric_observations_are_not_coerced"],
         "A model-level prevalidator to destroy valid JSON collection/date semantics while checking unrelated booleans."),
        ("GRD-0139", "LSN-0137", "Structured SQL fixtures bind JSON as data",
         ["test_legacy_migration_preserves_identity_body_and_rights_without_promotion",
          "test_database_immutability_and_direct_corruption_fail_closed"],
         "A SQL text parser to reinterpret JSON colons before substantive legacy/corruption assertions execute."),
        ("GRD-0140", "LSN-0138", "Actual secret projection distinguishes public identities",
         ["test_public_minio_identity_is_not_a_bearer_secret_but_storage_password_stays_protected",
          "test_known_opaque_capability_refused_in_declared_forms"],
         "A public account identity to block valid source facts or a broad word exemption to bypass actual password/authorization refusal."),
        ("GRD-0141", "LSN-0139", "Actual source SQL is private-column minimal and byte bounded",
         ["test_actual_sql_projection_does_not_fetch_unneeded_private_source_columns",
          "test_oversized_required_source_json_is_refused_before_materialization_and_writes"],
         "A safe output projection to conceal unbounded private source reads into adapter memory."),
    )
    additions = {
        "GRD-0044": ["test_experience_constraint_names_respect_their_actual_kind"],
        "GRD-0128": ["test_known_opaque_capability_refused_in_declared_forms"],
        "GRD-0137": ["test_current_producer_bytes_survive_actual_consumer_failure_and_owned_cleanup",
                     "test_current_producer_capture_refuses_unsafe_bytes_without_losing_neutral_inventory"],
    }
    for guard in registry["guardrails"]:
        if guard["guardrailId"] in additions:
            guard["verifiedBy"] = list(dict.fromkeys(
                guard.get("verifiedBy", [guard["reference"]]) + additions[guard["guardrailId"]]))
    for identifier, lesson_id, title, controls, consequence in fresh:
        existing = next((row for row in registry["guardrails"] if row["guardrailId"] == identifier), None)
        if existing is not None and existing["lessons"] != [lesson_id]:
            raise ValueError("guard identity already belongs to another lesson")
        if existing is None:
            registry["guardrails"].append({"guardrailId": identifier, "title": title, "kind": "test",
                "reference": controls[0], "verifiedBy": controls, "lessons": [lesson_id],
                "removingItWouldAllow": consequence})
    write_json(ROOT / ".iacode/memory/guardrails/registry.json", registry)
    new = {lesson: (guard, controls) for guard, lesson, _, controls, _ in fresh}
    selected = {"LSN-0042", "LSN-0105", "LSN-0126", "LSN-0135"} | set(new)
    lessons = load_lessons(ROOT)
    references = ["file:docs/checkpoints/GATE-6-CP-0001/COMMANDS.jsonl",
                  "file:docs/checkpoints/GATE-6-CP-0001/PRE-LIVE-PROGRESS.json",
                  "file:docs/checkpoints/GATE-6-CP-0001/suite-attempts/INTEGRATION-0004.json"]
    for lesson in lessons:
        identifier = lesson["lessonId"]
        if identifier not in selected:
            continue
        if identifier in new:
            guard, controls = new[identifier]
            lesson["guardrails"] = [guard]
            lesson["prevention"] = [{"kind": "test", "reference": name,
                "description": "Executed causal positive/adverse regression in the actual owning runtime."}
                for name in controls]
        else:
            for failure in lesson["guardrailFailures"]:
                if failure["checkpoint"] == CHECKPOINT.name:
                    failure["resolvedIn"] = CHECKPOINT.name
            for guard in lesson["guardrails"]:
                for control in additions.get(guard, []):
                    if not any(row["reference"] == control for row in lesson["prevention"]):
                        lesson["prevention"].append({"kind": "test", "reference": control,
                            "description": "Current strengthened causal boundary; every original control remains."})
        lesson["status"] = "GUARDED"
        lesson["updatedAt"] = utc_now()
        lesson["evidence"] = list(dict.fromkeys(lesson["evidence"] + references))
        lesson["notes"] = ("All original failures, recurrence counts and escalated severities remain. "
            "Causal acceptance: actual complete pre-live " + sequence["id"] + "; actual PostgreSQL/HTTP/migrations36 "
            "cmd-0050 and exact fresh real provider/sandbox/quality experience producer. The prior integration "
            "attempt's false identity flag is retained without inventing its cause. Guards restored, not "
            "whole-Gate readiness: immutable full verification and ordered assurance remain pending.")
    save_lessons(ROOT, lessons)
    findings = load_json(CHECKPOINT / "FINDINGS.json")
    for finding in findings["findings"]:
        if finding["findingId"] in {f"G6-INT-{i:03d}" for i in range(1, 8)}:
            finding["status"] = "CLOSED"
            finding["resolutionEvidence"] = ["command:" + sequence["id"], "command:cmd-0050",
                "file:docs/checkpoints/GATE-6-CP-0001/PRE-LIVE-PROGRESS.json",
                "file:" + receipt["producerArchive"]]
            finding["resolution"] = "Actual complete causal local suites, clean/adverse controls and fresh real source capture pass; original failures remain. No whole-Gate or independent verdict is inferred."
    write_json(CHECKPOINT / "FINDINGS.json", findings)
    print("CAUSAL_GUARDS_RESTORED new=4 recurrences=3 fullImmutable=PENDING independentM2=PENDING")
    return 0


if __name__ == "__main__":
    use_utf8_stdout()
    raise SystemExit(main())
