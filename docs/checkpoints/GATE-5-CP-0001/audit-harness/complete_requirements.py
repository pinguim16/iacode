"""Assemble reviewed evidence mappings after complete immutable functional verification."""

from __future__ import annotations

import json
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
BASELINE = "GATE-4-CP-0010"
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))

from delivery_assurance import collect_test_ids, load_command_results, resolve_evidence
from derive_requirements import EVIDENCE_FIELDS, render_closure, render_matrix
from ledger_common import LedgerError, load_json, scope_fingerprint, write_json

CORE = "apps/cli/src/client.cjs"
SNAPSHOT = "apps/cli/src/snapshot.cjs"
CLI = "apps/cli/bin/iacode.cjs"
EDITOR = "apps/vscode-extension/src/extension.cjs"
API = "apps/api/src/iacode_api/routes/desktop.py"
AUTH = "apps/api/src/iacode_api/middleware/desktop_auth.py"
API_TESTS = "apps/api/tests/unit/test_desktop_api.py"
CORE_TESTS = "apps/cli/tests/core.test.cjs"
EDITOR_TESTS = "apps/vscode-extension/tests/extension.test.cjs"
ROOT_TESTS = "tests/test_gate5_clients.py"
RUNBOOK = "docs/runbooks/DESKTOP-CLIENTS.md"
LIVE = "scripts/iacode/scenarios/desktop_e2e.py"
NATIVE = "scripts/iacode/native_editor.py"


def mapped(artifacts: list[str], tests: list[str], docs: list[str] | None = None) -> dict:
    return {
        "implementationEvidence": ["file:" + path for path in artifacts],
        "testEvidence": ["file:" + path for path in tests],
        "negativeTestEvidence": ["file:" + path for path in tests] + ["checkpoint:FINDINGS.json"],
        "documentationEvidence": ["file:" + path for path in (docs or [RUNBOOK])],
        "validationEvidence": ["checkpoint:VERIFY.json", "checkpoint:PUBLISHED-CLEAN-CLONE-REPORT.json"],
        "guardrailEvidence": ["file:.iacode/memory/guardrails/registry.json"],
    }


CANONICAL: dict[str, dict] = {}


def bind(keys: str, artifacts: list[str], tests: list[str], docs: list[str] | None = None) -> None:
    for key in keys.split():
        if key in CANONICAL:
            raise ValueError("duplicate authored requirement mapping " + key)
        CANONICAL[key] = mapped(artifacts, tests, docs)


bind("1.1", ["docs/GATE-5-CHECKLIST.md", ".iacode/policies/canonical-requirements.json"], [ROOT_TESTS], ["docs/DEVELOPMENT-CONTRACT.md"])
bind("1.2 1.6 9.8", [".iacode/policies/gate-scope.json", "docs/checkpoints/GATE-5-CP-0001/PROVENANCE.json"], [ROOT_TESTS, "tests/test_gate0_foundation.py"], ["docs/MASTER-PLAN.md", "docs/checkpoints/GATE-5-CP-0001/AUTHORIZATION.md"])
bind("1.3 1.4", [".iacode/policies/quality-gates.json", ".iacode/policies/test-suites.json"], [ROOT_TESTS, "tests/test_test_suite_input_repositories.py"], ["docs/adr/ADR-0047-native-client-suites-and-packages-are-explicit.md"])
bind("1.5", [CLI, CORE, EDITOR, API], [CORE_TESTS, EDITOR_TESTS, API_TESTS])
bind("2.1 2.3", [AUTH, "packages/common/src/iacode_common/desktop_auth.py"], [API_TESTS, CORE_TESTS])
bind("2.2", [CORE, EDITOR], [CORE_TESTS, EDITOR_TESTS])
bind("2.4", [CORE, CLI, EDITOR, "apps/api/src/iacode_api/config.py"], [API_TESTS, CORE_TESTS, EDITOR_TESTS])
bind("2.5", ["packages/contracts/src/iacode_contracts/desktop.py", "packages/contracts/src/iacode_contracts/desktop_protocol.json", CORE], [API_TESTS, CORE_TESTS])
bind("2.6", [CORE, CLI, EDITOR], [CORE_TESTS, EDITOR_TESTS, ROOT_TESTS])
bind("3.1 3.2 3.3 3.4", [SNAPSHOT, "apps/api/src/iacode_api/desktop_snapshots.py", API], [API_TESTS, CORE_TESTS, EDITOR_TESTS])
bind("3.5", [EDITOR], [EDITOR_TESTS, ROOT_TESTS])
bind("4.1 4.3 4.4 4.7", [CORE, CLI, EDITOR, API], [CORE_TESTS, EDITOR_TESTS])
bind("4.2", [CORE, CLI, EDITOR], [CORE_TESTS, "apps/cli/tests/cli.test.cjs", EDITOR_TESTS])
bind("4.5", [CLI, EDITOR, "services/agent-runtime/src/iacode_agent_runtime/persistence.py", LIVE], [EDITOR_TESTS, "services/agent-runtime/tests/test_cancellation_store.py", ROOT_TESTS])
bind("4.6", [CORE, CLI, EDITOR, API], [EDITOR_TESTS, "services/evaluator/tests/test_core.py"])
bind("5.1 5.2 5.3 5.4", [CLI, CORE], ["apps/cli/tests/cli.test.cjs", CORE_TESTS])
bind("6.1", ["scripts/iacode/build_clients.py", "apps/vscode-extension/package.json", NATIVE], [ROOT_TESTS, EDITOR_TESTS])
bind("6.2 6.3 6.4 6.5", [EDITOR], [EDITOR_TESTS, ROOT_TESTS])
bind("7.1 7.2", ["scripts/iacode/build_clients.py", "scripts/iacode/client_checks.py", "scripts/iacode/dependency_scan.py", ".gitattributes"], [ROOT_TESTS, CORE_TESTS, EDITOR_TESTS], ["docs/adr/ADR-0047-native-client-suites-and-packages-are-explicit.md", RUNBOOK])
bind("7.3", ["scripts/iacode/gates/lint.py", "services/evaluator/src/iacode_evaluator/planner.py", ".iacode/policies/test-suites.json"], [ROOT_TESTS, "services/evaluator/tests/test_core.py"])
bind("7.4", ["scripts/development-ledger/ledger_common.py", "scripts/development-ledger/validate_checkpoint.py", ".iacode/policies/assurance-scope.json"], [ROOT_TESTS, "tests/test_gate4_quality_engine.py"], ["docs/adr/ADR-0049-root-assurance-inputs-follow-subject-policy.md"])
bind("8.1 8.2 8.3 8.4 8.5", [LIVE, NATIVE, "scripts/iacode/desktop_test_support.py", "scripts/iacode/native_process.py"], [ROOT_TESTS, CORE_TESTS, EDITOR_TESTS])
bind("9.1", [RUNBOOK, "apps/cli/README.md", "apps/vscode-extension/README.md"], [ROOT_TESTS])
bind("9.2 9.5", ["scripts/development-ledger/derive_requirements.py", "scripts/development-ledger/check_completeness.py", "scripts/development-ledger/derive_counts.py"], ["tests/test_development_ledger.py", ROOT_TESTS], ["docs/DEVELOPMENT-CONTRACT.md", "docs/ENGINEERING-MEMORY.md"])
bind("9.3", ["scripts/iacode/verify.py"], [ROOT_TESTS], ["docs/DEVELOPMENT.md"])
bind("9.4", ["scripts/development-ledger/green_keeper.py", "scripts/development-ledger/check_completeness.py", "scripts/development-ledger/m0_mirror_audit.py"], ["tests/test_development_ledger.py", ROOT_TESTS], ["docs/DEVELOPMENT-CONTRACT.md", "docs/QUALITY-GATES.md"])
bind("9.6", ["scripts/development-ledger/seal_checkpoint.py", "scripts/development-ledger/review_bundle.py"], ["tests/test_development_ledger.py"], ["docs/CHECKPOINT-PROTOCOL.md"])
bind("9.7", ["scripts/development-ledger/validate_checkpoint.py", "docs/checkpoints/GATE-5-CP-0001/STATE.json"], ["tests/test_gate4_quality_engine.py"], ["docs/MILESTONE-VALIDATION.md", "docs/adr/ADR-0037-intermediate-gates-use-internal-closure.md"])

NEW_LESSONS = {
    "LSN-0011": (["docs/checkpoints/GATE-5-CP-0001/audit-harness/validate_serial_bookkeeping.py", "docs/checkpoints/GATE-5-CP-0001/audit-harness/run_checkpoint_validation.py", "scripts/development-ledger/sync_in_progress_metadata.py", "scripts/development-ledger/finalize_checkpoint.py"], [ROOT_TESTS, "tests/test_in_progress_metadata.py", "tests/test_gate0_foundation.py"]),
    "LSN-0035": (["scripts/iacode/client_checks.py", "scripts/iacode/desktop_test_support.py", NATIVE, LIVE], ["tests/test_gate0_foundation.py", ROOT_TESTS]),
    "LSN-0037": (["scripts/development-ledger/policies.py", "tests/test_gate3_sandbox.py"], ["tests/test_gate3_sandbox.py", ROOT_TESTS]),
    "LSN-0074": ([API_TESTS], [API_TESTS, "services/sandbox/tests/test_quality_images.py"]),
    "LSN-0083": ([NATIVE, LIVE, "docs/checkpoints/GATE-5-CP-0001/audit-harness/run_internal_red_team.py"], ["tests/test_gate0_foundation.py", ROOT_TESTS]),
    "LSN-0102": (["docs/checkpoints/GATE-5-CP-0001/audit-harness/run_full_verification.py"], [ROOT_TESTS]),
    "LSN-0105": (["infra/tests/test_compose_definition.py", "scripts/iacode/gates/lint.py"], ["tests/test_gate4_quality_engine.py"]),
    "LSN-0117": (["docs/ARCHITECTURE.md"], [ROOT_TESTS]),
    "LSN-0118": ([CORE, EDITOR], [CORE_TESTS, ROOT_TESTS]),
    "LSN-0119": ([AUTH, "infra/compose/.env.example"], [ROOT_TESTS]),
    "LSN-0120": ([NATIVE], [ROOT_TESTS]),
    "LSN-0121": (["scripts/iacode/desktop_test_support.py"], [ROOT_TESTS]),
    "LSN-0122": (["scripts/iacode/desktop_test_support.py", LIVE], [ROOT_TESTS]),
    "LSN-0123": ([EDITOR], [EDITOR_TESTS, ROOT_TESTS]),
    "LSN-0124": ([NATIVE, "apps/vscode-extension/host-tests/driver.cjs"], [ROOT_TESTS]),
    "LSN-0125": ([NATIVE, "scripts/iacode/native_process.py"], [ROOT_TESTS]),
    "LSN-0126": ([AUTH, CORE, EDITOR], [API_TESTS, CORE_TESTS, EDITOR_TESTS]),
    "LSN-0127": ([LIVE, "scripts/iacode/desktop_test_support.py"], [ROOT_TESTS]),
    "LSN-0128": ([LIVE, "scripts/iacode/desktop_test_support.py"], [ROOT_TESTS]),
    "LSN-0129": (["services/agent-runtime/src/iacode_agent_runtime/persistence.py"], ["services/agent-runtime/tests/test_cancellation_store.py"]),
    "LSN-0130": ([".gitattributes", "scripts/iacode/build_clients.py"], [ROOT_TESTS]),
    "LSN-0131": ([".gitattributes"], [ROOT_TESTS]),
    "LSN-0132": (["docs/checkpoints/GATE-5-CP-0001/audit-harness/run_full_verification.py"], [ROOT_TESTS]),
    "LSN-0133": ([".iacode/schemas/provenance.schema.json", "docs/checkpoints/GATE-5-CP-0001/PROVENANCE.json"], [ROOT_TESTS]),
    "LSN-0134": (["scripts/iacode/compose.py"], [ROOT_TESTS, "tests/test_gate1_model_gateway.py", "infra/tests/test_compose_definition.py", "infra/tests/test_backup_tooling.py"]),
    "LSN-0135": (["docs/checkpoints/GATE-5-CP-0001/audit-harness/run_full_verification.py"], [ROOT_TESTS]),
}


def inherited(reference: str) -> str:
    kind, _, value = reference.partition(":")
    if kind == "checkpoint":
        return f"file:docs/checkpoints/{BASELINE}/{value}"
    if kind == "command":
        return f"file:docs/checkpoints/{BASELINE}/COMMANDS.jsonl"
    return reference


def main() -> int:
    verification = load_json(CHECKPOINT / "VERIFY.json")
    publication = load_json(CHECKPOINT / "PUBLISHED-CLEAN-CLONE-REPORT.json")
    acceptance = load_json(CHECKPOINT / "FUNCTIONAL-ACCEPTANCE.json")
    functional = load_json(CHECKPOINT / "FUNCTIONAL-SCENARIOS.json")
    desktop = functional["scenarios"]["desktop-e2e.json"]
    if (verification.get("result") != "PASS" or verification.get("fast") is not False
            or any(row["result"] != "PASS" for row in verification["stages"])
            or publication.get("result") != "PASS" or acceptance.get("status") != "PASS"
            or desktop.get("sourceFingerprint") != scope_fingerprint(ROOT)
            or desktop.get("subjectCommit") != publication.get("publishedCommit")):
        raise LedgerError("complete immutable functional verification is required before evidence assembly")
    raw = subprocess.check_output(["git", "show",
        f"iacode-checkpoints/{BASELINE}:docs/checkpoints/{BASELINE}/CLOSURE-REQUIREMENTS.json"], cwd=ROOT)
    baseline = {row["sourceRef"]: row for row in json.loads(raw)["requirements"]}
    closure = deepcopy(load_json(CHECKPOINT / "CLOSURE-REQUIREMENTS.json"))
    matrix = deepcopy(load_json(CHECKPOINT / "REQUIREMENTS-MATRIX.json"))
    tests, commands = collect_test_ids(ROOT), load_command_results(CHECKPOINT)
    canonical_refs = {row["sourceRef"].split("#")[-1] for row in closure["requirements"]
                      if row["sourceRef"].startswith("canonical:")}
    if canonical_refs != set(CANONICAL):
        raise LedgerError("authored canonical mapping differs from the complete derived set")
    mapped_rows = {}
    for row in closure["requirements"]:
        reference = row["sourceRef"]
        if reference.startswith("canonical:"):
            evidence = deepcopy(CANONICAL[reference.split("#")[-1]])
            evidence["validationEvidence"].append("checkpoint:FUNCTIONAL-ACCEPTANCE.json")
            row["notes"] = "Authored Gate 5 artifact/test mapping and complete immutable current-source execution. Same-session only; formal ordered closure remains separately enforced by STATE and its assurance reports."
        elif reference.startswith("lesson:") and reference[7:] in NEW_LESSONS:
            artifacts, cases = NEW_LESSONS[reference[7:]]
            evidence = mapped(artifacts, cases, ["docs/ENGINEERING-MEMORY.md", "docs/checkpoints/GATE-5-CP-0001/PLAN.md"])
            evidence["validationEvidence"].append("checkpoint:FUNCTIONAL-SCENARIOS.json")
            row["notes"] = "Direct current lesson artifacts, real positive/adverse controls, retained causal failures and complete immutable re-execution; not independent validation."
        else:
            prior = baseline.get(reference)
            if prior is None or prior.get("finalStatus") != "COMPLETE":
                raise LedgerError("no reviewed sealed baseline or direct mapping for " + reference)
            evidence = {field: [inherited(value) for value in prior[field]] for field in EVIDENCE_FIELDS}
            evidence["validationEvidence"].append("checkpoint:VERIFY.json")
            row["notes"] = "Sealed prior lesson implementation/guard evidence plus complete current immutable re-execution of every mandatory suite/scenario. No historical verdict is rewritten or presented as independent current approval."
            if reference in {"lesson:LSN-0080", "lesson:LSN-0084", "lesson:LSN-0102"}:
                evidence["testEvidence"].append("file:" + ROOT_TESTS)
                evidence["implementationEvidence"].append("file:" + LIVE if reference == "lesson:LSN-0080" else "file:" + ROOT_TESTS)
                evidence["negativeTestEvidence"].append("checkpoint:FINDINGS.json")
        for field, values in evidence.items():
            row[field] = list(dict.fromkeys(values))
            if not row[field]:
                raise LedgerError(reference + " has no " + field)
            for value in row[field]:
                error = resolve_evidence(ROOT, CHECKPOINT, value, commands, tests)
                if error:
                    raise LedgerError(reference + ": " + error)
        row["implementationStatus"] = row["finalStatus"] = "COMPLETE"
        row["justification"] = None
        mapped_rows[reference] = row
    for row in matrix["requirements"]:
        source = mapped_rows[row["sourceRef"]]
        row.update({"status": "COMPLETE", "justification": None, "notes": source["notes"]})
        for field in ("implementationEvidence", "testEvidence", "documentationEvidence", "validationEvidence"):
            row[field] = list(source[field])
    write_json(CHECKPOINT / "CLOSURE-REQUIREMENTS.json", closure)
    write_json(CHECKPOINT / "REQUIREMENTS-MATRIX.json", matrix)
    (CHECKPOINT / "CLOSURE-REQUIREMENTS.md").write_text(render_closure(closure), encoding="utf-8", newline="\n")
    (CHECKPOINT / "REQUIREMENTS-MATRIX.md").write_text(render_matrix(matrix), encoding="utf-8", newline="\n")
    print(f"REQUIREMENT_EVIDENCE_ASSEMBLY=PASS total={len(mapped_rows)}; formal closure not inferred")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
