"""Consolidate actual current observations; integral acceptance and findings remain open."""

import json
import re
import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))
from ledger_common import load_json, scope_fingerprint, utc_now, write_json
from derive_requirements import render_closure, render_matrix
from sync_in_progress_metadata import synchronize


def main():
    now = utc_now()
    state = load_json(CHECKPOINT / "STATE.json")
    if state["status"] != "IN_PROGRESS":
        raise ValueError("Never rewrite a terminal subject")
    matrix = load_json(CHECKPOINT / "REQUIREMENTS-MATRIX.json")
    closure = load_json(CHECKPOINT / "CLOSURE-REQUIREMENTS.json")
    local = {"finding:M2-F-001", "finding:M2-F-002", "attack:M2-RT-01", "lesson:LSN-0010",
             "lesson:LSN-0135", "lesson:LSN-0035", "lesson:LSN-0083", "lesson:LSN-0152",
             "lesson:LSN-0131"}
    for row in closure["requirements"]:
        if row["sourceRef"] not in local:
            continue
        row.update(implementationStatus="COMPLETE", finalStatus="PARTIAL",
                   justification="Actual local correction and automated prevention observed; current complete immutable and ordered assurance remain pending.")
        row["implementationEvidence"] = ["file:scripts/development-ledger/new_checkpoint.py",
            "file:scripts/development-ledger/m0_red_team.py", "file:scripts/iacode/client_checks.py",
            "file:scripts/iacode/native_execution.py", "file:scripts/development-ledger/audit_runner_bridge.py",
            "file:.gitattributes", "file:tests/test_m2_observation_transport.py"]
        row["testEvidence"] = ["file:docs/checkpoints/GATE-7-CP-0003/causal-attempts/run-0011.json",
            "file:docs/checkpoints/GATE-7-CP-0003/causal-attempts/native-observation/run-0004.json",
            "file:docs/checkpoints/GATE-7-CP-0003/causal-attempts/bridge-physical-bounds/run-0002.json",
            "file:docs/checkpoints/GATE-7-CP-0003/causal-attempts/current-streams/run-0001.json",
            "file:docs/checkpoints/GATE-7-CP-0003/byte-transport-attempts/controls/run-0004.json",
            "file:docs/checkpoints/GATE-7-CP-0003/byte-transport-attempts/index-0006.json"]
        row["negativeTestEvidence"] = ["file:docs/checkpoints/GATE-7-CP-0003/causal-attempts/run-0005.json",
            "file:docs/checkpoints/GATE-7-CP-0003/causal-attempts/native-cleanup-evidence/run-0001.json",
            "file:docs/checkpoints/GATE-7-CP-0003/causal-attempts/bridge-physical-bounds/run-0001.json",
            "file:docs/checkpoints/GATE-7-CP-0003/byte-transport-attempts/controls/run-0001.json",
            "file:docs/checkpoints/GATE-7-CP-0003/byte-transport-attempts/controls/run-0003.json"]
        row["documentationEvidence"] = ["file:docs/adr/ADR-0061-client-verification-preserves-producer-and-cleanup-outcomes.md",
            "file:docs/adr/ADR-0062-isolated-audit-uses-closed-host-validation-jobs.md",
            "checkpoint:ENVIRONMENT-VALIDATION-CONTEXT.md"]
    for row in matrix["requirements"]:
        if row["sourceRef"] in local:
            row.update(status="PARTIAL", justification="Local correction observed; whole current acceptance pending.")
    write_json(CHECKPOINT / "CLOSURE-REQUIREMENTS.json", closure)
    write_json(CHECKPOINT / "REQUIREMENTS-MATRIX.json", matrix)
    (CHECKPOINT / "CLOSURE-REQUIREMENTS.md").write_text(render_closure(closure), encoding="utf-8", newline="\n")
    (CHECKPOINT / "REQUIREMENTS-MATRIX.md").write_text(render_matrix(matrix), encoding="utf-8", newline="\n")
    rows = matrix["requirements"]
    state["requirementsMatrix"].update(total=len(rows), mandatory=sum(row["mandatory"] for row in rows),
                                      complete=sum(row["status"] == "COMPLETE" for row in rows),
                                      partial=sum(row["status"] == "PARTIAL" for row in rows))
    preflight = load_json(CHECKPOINT / "LESSON-PREFLIGHT.json")
    state["lessonPreflight"].update(lessonsConsidered=preflight["lessonsConsidered"],
                                    lessonsApplicable=preflight["lessonsApplicable"],
                                    derivedRequirements=len(preflight["derivedRequirements"]))
    state["updatedAt"] = now
    state["nextAllowedAction"] = ("Quiesce all writers and validate declared draft bookkeeping, publish an immutable "
                                  "IN_PROGRESS runtime subject, then execute complete canonical public-transport "
                                  "Green Keeper and full non-fast verification. Complete current evidence, DCV, "
                                  "fresh internal Red Team/mirror, exact owned cleanup and seal READY_FOR_REVIEW "
                                  "before any new fresh independent M2 auditor. No Gate8.")
    write_json(CHECKPOINT / "STATE.json", state)
    tests = load_json(CHECKPOINT / "TESTS.json")
    raw = (CHECKPOINT / "quality-attempts/tests/run-0001.stderr.log").read_text(encoding="utf-8")
    count = re.search(r"Ran (\d+) tests", raw)
    failed = re.search(r"FAILED \(failures=(\d+)\)", raw)
    if not count or not failed:
        raise ValueError("Exact completed baseline counters required")
    total, failures = int(count[1]), int(failed[1])
    tests["unit"].update(executed=True, passed=total-failures, failed=failures,
                         command="python -m unittest discover -s tests",
                         evidence="file:quality-attempts/tests/run-0001.json",
                         runId="completed-pre-extension-local-baseline-not-current-acceptance")
    write_json(CHECKPOINT / "TESTS.json", tests)
    quality = load_json(CHECKPOINT / "QUALITY.json")
    lint_path = sorted((CHECKPOINT / "quality-attempts/lint").glob("run-*.json"))[-1]
    lint = load_json(lint_path)
    if lint["exitCode"] or not lint["sourceUnchanged"] or lint["sourceFingerprint"] != scope_fingerprint(ROOT):
        raise ValueError("Actual unchanged current complete lint required")
    quality["checks"]["lint"].update(status="PASS", evidence=["file:" + lint_path.relative_to(CHECKPOINT).as_posix()],
                                      justification="Complete actual canonical current gate; earlier failures/retries preserved.")
    static_path = sorted((CHECKPOINT / "quality-attempts/staticAnalysis").glob("run-*.json"))[-1]
    static = load_json(static_path)
    if (static["exitCode"] or not static["sourceUnchanged"]
            or static["sourceFingerprint"] != scope_fingerprint(ROOT)):
        raise ValueError("Actual unchanged current complete static analysis required")
    quality["checks"]["staticAnalysis"].update(status="PASS",
        evidence=["file:" + static_path.relative_to(CHECKPOINT).as_posix()],
        justification="Actual complete current script/test compile; not full test acceptance.")
    write_json(CHECKPOINT / "QUALITY.json", quality)
    active = {"recordedAt": now, "kind": "TRANSIENT_OPERATOR_RESUME_MARKER_NOT_ACCEPTANCE",
              "sourceFingerprint": scope_fingerprint(ROOT),
              "nativeToolSessions": [{"id": 45796, "lastObservedStatus": "COMPLETED", "exitCode": 1,
                                      "evidence": "quality-attempts/tests/run-0001.json"},
                                     {"lastObservedStatus": "COMPLETED", "exitCode": 0,
                                      "evidence": lint_path.relative_to(CHECKPOINT).as_posix()}],
              "cleanup": "RETIRED_CLONE_REMOVED_DOCKER_SCOPE_STILL_ACTIVE_FOR_REMAINING_VALIDATION",
              "warning": "Transient session numbers are not success evidence; completed receipts bind actual exits.",
              "ownedBuilderReceipt": "OWNED-DOCKER-SCOPE.json", "independentAuditorStarted": False,
              "gate8Authorized": False}
    write_json(CHECKPOINT / "ACTIVE-VALIDATION.json", active)
    findings = load_json(CHECKPOINT / "M2-CP-0002-FINDINGS-CLOSURE.json")
    for finding in findings["findings"]:
        if finding["findingId"] == "M2-F-002":
            finding["implementation"] = list(dict.fromkeys([*finding["implementation"],
                "file:scripts/iacode/native_editor.py", "file:scripts/iacode/native_execution.py"]))
            finding["evidence"] = list(dict.fromkeys([*finding["evidence"],
                "file:docs/checkpoints/GATE-7-CP-0003/causal-attempts/native-observation/run-0004.json"]))
    write_json(CHECKPOINT / "M2-CP-0002-FINDINGS-CLOSURE.json", findings)
    synchronize(ROOT, CHECKPOINT)
    print(json.dumps({"derivedTotal": len(rows), "mandatory": sum(row["mandatory"] for row in rows),
                      "baseline": {"run": total, "failed": failures}, "currentCompleteLint": "PASS",
                      "findingsClosed": findings["closed"], "integralAcceptance": "PENDING"}))
    return 0


if __name__ == "__main__":
    from ledger_common import use_utf8_stdout
    use_utf8_stdout()
    raise SystemExit(main())
