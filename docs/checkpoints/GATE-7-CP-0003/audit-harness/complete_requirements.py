"""Bind reviewed corrective obligations to actual complete current assurance, not predictions."""

from __future__ import annotations

import hashlib
import json
import subprocess
from copy import deepcopy

from acceptance_evidence import BASELINE, CHECKPOINT, ROOT, current_execution, current_greenkeeper

DIRECT = {
    "LSN-0154": (
        [
            "scripts/iacode/self_qualification_source.py",
            "scripts/iacode/scenarios/quality_engine_e2e.py",
        ],
        ["tests/test_m2_self_snapshot.py"],
        ["FULL-VERIFICATION-FAILURE-0001.json", "FULL-REWORK-REGISTRATION-0001.json"],
    ),
    "LSN-0153": (
        ["scripts/development-ledger/derive_counts.py"],
        ["tests/test_m2_discovery_isolation.py"],
        [
            "IMPORT-ISOLATION-001.json",
            "IMPORT-ISOLATION-LOCAL-PREVENTION.json",
            "causal-attempts/discovery-isolation/run-0003.json",
        ],
    ),
    "LSN-0010": (
        ["scripts/development-ledger/new_checkpoint.py"],
        ["tests/test_m2_audit_corrections.py"],
        ["causal-attempts/run-0009.json"],
    ),
    "LSN-0035": (
        ["scripts/development-ledger/new_checkpoint.py", "audit-harness/publish_progress.py"],
        ["tests/test_m2_current_stream_bootstrap.py", "tests/test_m2_progress_publication.py"],
        ["causal-attempts/inherited-streams/run-0003.json"],
    ),
    "LSN-0054": (
        ["audit-harness/publish_progress.py", "audit-harness/authored_python_quality.py"],
        ["tests/test_m2_progress_publication.py"],
        ["causal-attempts/publication-policy/run-0007.json", "RUNTIME-V4-PUBLICATION.json"],
    ),
    "LSN-0083": (
        ["audit-harness/run_causal.py", "audit-harness/run_full_verification.py"],
        ["tests/test_m2_current_stream_bootstrap.py"],
        ["causal-attempts/current-streams/run-0001.json"],
    ),
    "LSN-0105": (
        ["audit-harness/authored_python_quality.py", "audit-harness/publish_progress.py"],
        ["tests/test_m2_progress_publication.py"],
        ["quality-attempts/lint/run-0014.json", "AUTHORED-STYLE-LOCAL-RESTORATION.json"],
    ),
    "LSN-0125": (
        ["audit-harness/current_resources.py", "scripts/iacode/native_process.py"],
        ["tests/test_m2_bootstrap_ownership.py", "tests/test_m2_cleanup_operator.py"],
        [
            "causal-attempts/bootstrap-ownership/run-0004.json",
            "resource-phases/phase-0002/BUILDER-BOOTSTRAP-RETRY-0001.json",
        ],
    ),
    "LSN-0131": (
        [".gitattributes", "audit-harness/probe_index_byte_preservation.py"],
        ["tests/test_m2_observation_transport.py"],
        [
            "byte-transport-attempts/controls/run-0012.json",
            "byte-transport-attempts/index-0010.json",
        ],
    ),
    "LSN-0135": (
        ["scripts/iacode/client_checks.py", "scripts/iacode/native_execution.py"],
        ["tests/test_m2_audit_corrections.py", "tests/test_m2_native_observation.py"],
        ["causal-attempts/run-0009.json", "causal-attempts/native-observation/run-0004.json"],
    ),
    "LSN-0140": (
        [
            ".iacode/memory/retrospectives/GATE-7-CP-0003.md",
            "audit-harness/probe_current_continuation.py",
        ],
        ["tests/test_m2_continuation.py"],
        ["CONTINUATION-LOCAL-RESTORATION.json"],
    ),
    "LSN-0151": (
        [
            "scripts/development-ledger/review_bundle.py",
            "scripts/development-ledger/gate4_red_team.py",
            "audit-harness/post_quality_diagnostics.py",
        ],
        [
            "tests/test_m2_history_transport.py",
            "tests/test_gate7_git_transport.py",
            "tests/test_m2_host_transport.py",
        ],
        [
            "causal-attempts/history-transport/run-0006.json",
            "history-diagnostics/run-0006/RECEIPT.json",
            "history-diagnostics/run-0007/RECEIPT.json",
            "history-diagnostics/run-0008/RECEIPT.json",
            "causal-attempts/review-reconstruction/run-0001.json",
            "causal-attempts/full-host-transport/run-0001/RECEIPT.json",
            "causal-attempts/full-host-transport/run-0002/RECEIPT.json",
        ],
    ),
    "LSN-0152": (
        ["scripts/development-ledger/audit_runner_bridge.py"],
        ["tests/test_m2_bridge_physical_bounds.py", "tests/test_m2_closed_runner_bridge.py"],
        ["causal-attempts/bridge-physical-bounds/run-0002.json"],
    ),
}

CURRENT_CANONICAL = {
    "1.1": ["checkpoint:AUTHORIZATION.md", "checkpoint:OWNER-DECISIONS.json"],
    "1.3": [
        "file:docs/adr/ADR-0064-unittest-discovery-restores-caller-import-bindings.md",
        "file:docs/adr/ADR-0061-client-verification-preserves-producer-and-cleanup-outcomes.md",
        "file:docs/adr/ADR-0062-isolated-audit-uses-closed-host-validation-jobs.md",
        (
            "file:docs/adr/ADR-0063-historical-review-producers-inherit-only-"
            "process-scoped-git-path-handling.md"
        ),
        (
            "file:docs/adr/ADR-0065-self-qualification-uses-immutable-product-inputs-"
            "not-checkpoint-outputs.md"
        ),
    ],
    "7.3": [
        "file:scripts/development-ledger/audit_runner_bridge.py",
        "checkpoint:audit-harness/prove_canonical_bridge.py",
        "checkpoint:ACTIVE-DOCKER-PHASE.json",
    ],
    "7.4": ["checkpoint:audit-harness/run_full_verification.py"],
    "7.5": [
        "checkpoint:audit-harness/run_full_verification.py",
        "checkpoint:audit-harness/current_resources.py",
        "file:.gitattributes",
    ],
    "8.3": ["checkpoint:audit-harness/run_internal_red_team.py"],
    "8.4": [
        "checkpoint:audit-harness/declare_inventory.py",
        "checkpoint:audit-harness/publish_progress.py",
        "file:scripts/development-ledger/review_bundle.py",
    ],
    "8.5": [
        "file:.iacode/memory/retrospectives/GATE-7-CP-0003.md",
        "checkpoint:M2-CP-0002-FINDINGS-CLOSURE.json",
    ],
    "8.7": ["checkpoint:audit-harness/run_full_verification.py"],
    "8.8": ["checkpoint:AUTHORIZATION.md", "checkpoint:STATE.json"],
}


def artifact(path):
    if path.startswith("audit-harness/"):
        path = CHECKPOINT.relative_to(ROOT).as_posix() + "/" + path
    return "file:" + path


def baseline_document(name):
    relative = f"docs/checkpoints/{BASELINE}/{name}"
    raw = subprocess.check_output(
        ["git", "-c", "core.longpaths=true", "show", f"iacode-checkpoints/{BASELINE}:{relative}"],
        cwd=ROOT,
    )
    return raw


def inherited(reference, prior_commands, bindings):
    from delivery_assurance import command_succeeded
    from ledger_common import LedgerError

    kind, _, value = reference.partition(":")
    if kind == "checkpoint":
        return f"file:docs/checkpoints/{BASELINE}/{value}"
    if kind == "command":
        command = prior_commands.get(value, {})
        if not command_succeeded(command):
            raise LedgerError("sealed inherited command did not succeed: " + value)
        translated = f"file:docs/checkpoints/{BASELINE}/COMMANDS.jsonl"
        bindings.append({"original": reference, "translated": translated, "record": command})
        return translated
    return reference


def direct_evidence(row):
    from derive_requirements import EVIDENCE_FIELDS

    reference = row["sourceRef"]
    evidence = {field: list(row.get(field) or []) for field in EVIDENCE_FIELDS}
    if reference.startswith("lesson:"):
        artifacts, tests, proofs = DIRECT[reference.removeprefix("lesson:")]
    else:
        artifacts = [
            "scripts/development-ledger/new_checkpoint.py",
            "scripts/development-ledger/m0_red_team.py",
        ]
        tests = ["tests/test_m2_audit_corrections.py"]
        proofs = ["causal-attempts/run-0009.json"]
        if reference == "finding:M2-F-002":
            artifacts += ["scripts/iacode/client_checks.py", "scripts/iacode/native_execution.py"]
            tests += ["tests/test_m2_native_observation.py"]
            proofs += ["causal-attempts/native-observation/run-0004.json"]
    evidence["implementationEvidence"] += [artifact(path) for path in artifacts]
    evidence["testEvidence"] += [artifact(path) for path in tests]
    evidence["negativeTestEvidence"] += ["checkpoint:INTERNAL-ENVIRONMENT-REWORK.json"]
    evidence["documentationEvidence"] += [
        "file:docs/ENGINEERING-MEMORY.md",
        "checkpoint:PLAN.md",
        "file:.iacode/memory/retrospectives/GATE-7-CP-0003.md",
    ]
    evidence["validationEvidence"] += ["checkpoint:" + path for path in proofs]
    evidence["guardrailEvidence"] += [
        "file:.iacode/memory/guardrails/registry.json",
        *[artifact(path) for path in tests],
    ]
    return evidence


def main():
    from delivery_assurance import collect_test_ids, load_command_results, resolve_evidence
    from derive_requirements import EVIDENCE_FIELDS, render_closure, render_matrix
    from ledger_common import LedgerError, load_json, use_utf8_stdout, write_json

    use_utf8_stdout()
    if load_json(CHECKPOINT / "STATE.json")["status"] != "IN_PROGRESS":
        raise LedgerError("never rewrite terminal or sealed requirement evidence")
    current_execution()
    _receipt, cycle, quality_folder = current_greenkeeper()
    acceptance = load_json(CHECKPOINT / "FUNCTIONAL-ACCEPTANCE-VALIDATION.json")
    if acceptance.get("result") != "PASS" or acceptance.get("missing"):
        raise LedgerError("actual complete canonical functional acceptance must pass first")
    raw_baseline = baseline_document("CLOSURE-REQUIREMENTS.json")
    raw_commands = baseline_document("COMMANDS.jsonl")
    baseline = {row["sourceRef"]: row for row in json.loads(raw_baseline)["requirements"]}
    prior_commands = {
        row["id"]: row
        for row in (json.loads(line) for line in raw_commands.splitlines() if line.strip())
    }
    closure = deepcopy(load_json(CHECKPOINT / "CLOSURE-REQUIREMENTS.json"))
    matrix = deepcopy(load_json(CHECKPOINT / "REQUIREMENTS-MATRIX.json"))
    references = [row["sourceRef"] for row in closure["requirements"]]
    additions = {
        "lesson:LSN-0152",
        "lesson:LSN-0153",
        "lesson:LSN-0154",
        "finding:M2-F-001",
        "finding:M2-F-002",
        "attack:M2-RT-01",
    }
    if (
        len(references) != len(set(references))
        or set(references) != set(baseline) | additions
        or {row["sourceRef"] for row in matrix["requirements"]} != set(references)
    ):
        raise LedgerError("complete inherited/canonical/new obligation membership differs")
    tests, commands = collect_test_ids(ROOT), load_command_results(CHECKPOINT)
    mapped, bindings = {}, []
    common = [
        "checkpoint:VERIFY.json",
        "checkpoint:PUBLISHED-CLEAN-CLONE-REPORT.json",
        "checkpoint:FUNCTIONAL-ACCEPTANCE.json",
        "checkpoint:FUNCTIONAL-ACCEPTANCE-VALIDATION.json",
        "checkpoint:" + quality_folder + "/RECEIPT.json",
        *["command:" + value for value in cycle["commandsExecuted"]],
    ]
    for row in closure["requirements"]:
        reference = row["sourceRef"]
        direct = reference in additions or reference.removeprefix("lesson:") in DIRECT
        if direct:
            evidence = direct_evidence(row)
            note = (
                "Direct corrective implementation/causal evidence and current complete quality "
                "and immutable functional execution. Original failures, recurrence counters and "
                "lesson classifications remain unchanged. LSN-0054 remains CONFIRMED, not GUARDED."
            )
        else:
            prior = baseline.get(reference)
            if prior is None or prior.get("finalStatus") != "COMPLETE":
                raise LedgerError("no sealed complete baseline for " + reference)
            evidence = {
                field: [inherited(value, prior_commands, bindings) for value in prior[field]]
                for field in EVIDENCE_FIELDS
            }
            note = (
                "Reviewed sealed Gate7 baseline artifact/test mapping plus every current "
                "mandatory quality suite and full immutable functional execution; no historical "
                "verdict is reused as current test acceptance. Exact inherited command bindings "
                "are preserved in REQUIREMENT-INHERITANCE.json."
            )
        if reference.startswith("canonical:"):
            evidence["implementationEvidence"] += CURRENT_CANONICAL.get(
                reference.split("#")[-1], []
            )
        evidence["validationEvidence"] += common
        for field, values in evidence.items():
            row[field] = list(dict.fromkeys(values))
            if not row[field]:
                raise LedgerError(reference + " lacks " + field)
            for value in row[field]:
                error = resolve_evidence(ROOT, CHECKPOINT, value, commands, tests)
                if error:
                    raise LedgerError(reference + ": " + error)
        row.update(
            implementationStatus="COMPLETE",
            finalStatus="COMPLETE",
            justification=None,
            notes=note
            + " Ordered DCV, fresh internal Red Team/mirror and actual terminal sealing remain "
            "separately mandatory; this mapping grants no future or independent verdict.",
        )
        mapped[reference] = row
    for row in matrix["requirements"]:
        source = mapped[row["sourceRef"]]
        row.update(status="COMPLETE", justification=None, notes=source["notes"])
        for field in (
            "implementationEvidence",
            "testEvidence",
            "documentationEvidence",
            "validationEvidence",
        ):
            row[field] = list(source[field])
    write_json(
        CHECKPOINT / "REQUIREMENT-INHERITANCE.json",
        {
            "kind": "SEALED_BASELINE_REFERENCE_BINDINGS_NOT_INHERITED_TEST_ACCEPTANCE",
            "baseline": BASELINE,
            "closureSha256": hashlib.sha256(raw_baseline).hexdigest(),
            "commandsSha256": hashlib.sha256(raw_commands).hexdigest(),
            "commandBindings": list({item["original"]: item for item in bindings}.values()),
            "currentExecutionRequired": True,
            "independentVerdictGranted": False,
        },
    )
    write_json(CHECKPOINT / "CLOSURE-REQUIREMENTS.json", closure)
    write_json(CHECKPOINT / "REQUIREMENTS-MATRIX.json", matrix)
    for name, document, render in (
        ("CLOSURE-REQUIREMENTS.md", closure, render_closure),
        ("REQUIREMENTS-MATRIX.md", matrix, render_matrix),
    ):
        (CHECKPOINT / name).write_text(render(document), encoding="utf-8", newline="\n")
    print(f"CURRENT_REQUIREMENT_EVIDENCE_ASSEMBLY=PASS total={len(mapped)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
