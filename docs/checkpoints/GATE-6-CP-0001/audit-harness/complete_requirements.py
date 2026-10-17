"""Assemble reviewed evidence mappings after complete immutable functional verification."""

from __future__ import annotations

import json
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
BASELINE = "GATE-5-CP-0001"
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))

from delivery_assurance import collect_test_ids, load_command_results, resolve_evidence
from derive_requirements import EVIDENCE_FIELDS, render_closure, render_matrix
from ledger_common import LedgerError, load_json, scope_fingerprint, write_json


CONTRACT = "packages/contracts/src/iacode_contracts/experience.py"
DOMAIN = "services/experience/src/iacode_experience/domain.py"
SOURCES = "apps/api/src/iacode_api/experience/sources.py"
STORE = "apps/api/src/iacode_api/experience/store.py"
RUNTIME = "apps/api/src/iacode_api/experience/runtime.py"
API = "apps/api/src/iacode_api/routes/experiences.py"
MODELS = "packages/persistence/src/iacode_persistence/models.py"
MIGRATION = "apps/api/migrations/versions/0007_experience_store.py"
POLICY = ".iacode/policies/experience-policy.json"
SCHEMA = ".iacode/schemas/experience.schema.json"
ROOT_TESTS = "tests/test_gate6_experience.py"
DOMAIN_TESTS = "services/experience/tests/test_contract.py"
SQL_TESTS = "apps/api/tests/integration/test_experience_store.py"
API_TESTS = "apps/api/tests/unit/test_experience_api.py"
MIGRATION_TESTS = "apps/api/tests/integration/test_migrations.py"
LIVE = "scripts/iacode/scenarios/experience_store_e2e.py"
RUNBOOK = "docs/runbooks/experience-store.md"
CP = "docs/checkpoints/GATE-6-CP-0001/"
PUBLISHER = CP + "audit-harness/run_full_verification.py"


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


bind("1.1", [CP + "AUTHORIZATION.md", ".iacode/anchors/checkpoint-chain.json"],
     [ROOT_TESTS, "tests/test_gate0_foundation.py"], ["docs/DEVELOPMENT-CONTRACT.md"])
bind("1.2", ["docs/GATE-6-CHECKLIST.md", ".iacode/policies/canonical-requirements.json",
            "scripts/development-ledger/derive_requirements.py"], [ROOT_TESTS])
bind("1.3", ["docs/adr/ADR-0050-experiences-are-source-bound-consented-facts.md",
            "docs/adr/ADR-0051-retention-tombstones-prevent-experience-resurrection.md"],
     [ROOT_TESTS], ["docs/ARCHITECTURE.md"])
bind("1.4", [DOMAIN, CONTRACT], [ROOT_TESTS, DOMAIN_TESTS])
bind("1.5", [".iacode/policies/quality-gates.json", ".iacode/policies/test-suites.json",
            "scripts/iacode/gates/experience_tests.py"], [ROOT_TESTS, "tests/test_test_suite_input_repositories.py"])
bind("1.6 8.8", [".iacode/policies/gate-scope.json", CP + "AUTHORIZATION.md"],
     [ROOT_TESTS, "tests/test_gate0_foundation.py"], ["docs/MASTER-PLAN.md", "docs/MILESTONE-VALIDATION.md"])
bind("2.1 2.3", [CONTRACT, SOURCES, SCHEMA], [DOMAIN_TESTS, SQL_TESTS, API_TESTS])
bind("2.2 2.4 3.5 3.6", [DOMAIN, CONTRACT, SOURCES, API, RUNTIME],
     [DOMAIN_TESTS, API_TESTS, SQL_TESTS])
bind("2.5 2.6", [SOURCES, CONTRACT], [SQL_TESTS, DOMAIN_TESTS])
bind("3.1", [API, DOMAIN, STORE], [DOMAIN_TESTS, SQL_TESTS, API_TESTS])
bind("3.2 3.3 3.4", [CONTRACT, DOMAIN, SOURCES, MODELS], [DOMAIN_TESTS, SQL_TESTS])
bind("3.7", [API, CONTRACT], [API_TESTS, SQL_TESTS])
bind("4.1 4.2", [MODELS, MIGRATION, STORE], [SQL_TESTS, MIGRATION_TESTS])
bind("4.3 4.4", [MODELS, MIGRATION, STORE, DOMAIN], [SQL_TESTS, DOMAIN_TESTS])
bind("4.5 4.6", [STORE, DOMAIN, LIVE], [SQL_TESTS, DOMAIN_TESTS, ROOT_TESTS])
bind("5.1", [API, RUNTIME, "apps/api/src/iacode_api/middleware/desktop_auth.py"],
     [API_TESTS, SQL_TESTS, "apps/api/tests/unit/test_desktop_api.py"])
bind("5.2 5.3 5.4", [API, STORE, DOMAIN, LIVE], [SQL_TESTS, API_TESTS, DOMAIN_TESTS])
bind("5.5", [API, "packages/telemetry/src/iacode_telemetry/logging.py",
            "apps/api/src/iacode_api/middleware/correlation.py"], [API_TESTS, SQL_TESTS])
bind("5.6", [API, SOURCES, "packages/contracts/src/iacode_contracts/desktop_protocol.json"],
     [ROOT_TESTS, API_TESTS, "apps/api/tests/unit/test_desktop_api.py", "apps/cli/tests/core.test.cjs"])
bind("6.1", [POLICY, DOMAIN], [ROOT_TESTS, DOMAIN_TESTS])
bind("6.2 6.4", [DOMAIN, STORE, API], [SQL_TESTS, DOMAIN_TESTS])
bind("6.3", [RUNTIME, STORE, MIGRATION], [SQL_TESTS, API_TESTS])
bind("6.5", [STORE, DOMAIN, SOURCES, LIVE], [SQL_TESTS, DOMAIN_TESTS])
bind("6.6", [RUNTIME, API, RUNBOOK], [API_TESTS, SQL_TESTS])
bind("7.1 7.2 7.3 7.4", [LIVE, "scripts/iacode/scenarios/experience_source_adversary.py",
                       "scripts/iacode/desktop_test_support.py"], [ROOT_TESTS, SQL_TESTS, API_TESTS])
bind("7.5 7.6", ["scripts/iacode/verify.py", PUBLISHER, ".gitattributes"], [ROOT_TESTS])
bind("8.1", [RUNBOOK, "services/experience/README.md", "docs/ARCHITECTURE.md"], [ROOT_TESTS])
bind("8.2 8.5", ["scripts/development-ledger/derive_requirements.py",
                "scripts/development-ledger/check_completeness.py",
                "scripts/development-ledger/derive_counts.py", CP + "audit-harness/declare_inventory.py"],
     ["tests/test_development_ledger.py", ROOT_TESTS], ["docs/DEVELOPMENT-CONTRACT.md", "docs/ENGINEERING-MEMORY.md"])
bind("8.3 8.4", ["scripts/iacode/verify.py", "scripts/development-ledger/green_keeper.py",
                "scripts/development-ledger/m0_mirror_audit.py", PUBLISHER],
     ["tests/test_development_ledger.py", "tests/test_gate4_quality_engine.py", "tests/test_gate5_clients.py", ROOT_TESTS])
bind("8.6", ["scripts/development-ledger/seal_checkpoint.py", "scripts/development-ledger/review_bundle.py"],
     ["tests/test_development_ledger.py", ROOT_TESTS], ["docs/CHECKPOINT-PROTOCOL.md"])
bind("8.7", ["scripts/development-ledger/validate_checkpoint.py", CP + "STATE.json"],
     ["tests/test_gate4_quality_engine.py", "tests/test_development_ledger.py"],
     ["docs/MILESTONE-VALIDATION.md", "docs/adr/ADR-0037-intermediate-gates-use-internal-closure.md"])
CANONICAL["8.5"]["implementationEvidence"].append("file:.iacode/memory/retrospectives/GATE-6-CP-0001.md")

NEW_LESSONS = {
    "LSN-0018": (["scripts/development-ledger/lessons.py",
                   "scripts/development-ledger/validate_checkpoint.py"],
                  ["tests/test_development_ledger.py", ROOT_TESTS]),
    "LSN-0011": ([CP + "audit-harness/validate_serial_bookkeeping.py",
                  CP + "audit-harness/run_checkpoint_validation.py"],
                 [ROOT_TESTS, "tests/test_in_progress_metadata.py"]),
    "LSN-0042": ([MODELS, MIGRATION], [SQL_TESTS, MIGRATION_TESTS, "apps/api/tests/unit/test_domain_model.py"]),
    "LSN-0102": ([PUBLISHER, "scripts/iacode/verify.py"], [ROOT_TESTS, "tests/test_gate5_clients.py"]),
    "LSN-0105": (["scripts/iacode/gates/lint.py", RUNTIME, API, MODELS], [ROOT_TESTS, API_TESTS]),
    "LSN-0119": (["scripts/development-ledger/validate_lessons.py", "scripts/development-ledger/validate_checkpoint.py",
                  "packages/common/src/iacode_common/secret_scanning.py", CP + "STRICT-MEMORY-FINDING.json"],
                 ["tests/test_gate5_clients.py", "apps/api/tests/unit/test_desktop_api.py"]),
    "LSN-0126": ([DOMAIN, "apps/api/src/iacode_api/middleware/desktop_auth.py"],
                 [DOMAIN_TESTS, API_TESTS, "apps/cli/tests/core.test.cjs"]),
    "LSN-0132": ([PUBLISHER], [ROOT_TESTS]),
    "LSN-0135": ([PUBLISHER], [ROOT_TESTS, "tests/test_gate5_clients.py"]),
    "LSN-0136": ([CONTRACT, DOMAIN], [DOMAIN_TESTS]),
    "LSN-0137": ([SQL_TESTS], [SQL_TESTS]),
    "LSN-0138": ([RUNTIME, DOMAIN, SOURCES], [API_TESTS, DOMAIN_TESTS]),
    "LSN-0139": ([SOURCES], [SQL_TESTS]),
    "LSN-0140": ([CP + "audit-harness/assemble_source_ready.py", CP + "audit-harness/render_local_handoff.py"], [ROOT_TESTS]),
    "LSN-0141": (["tests/test_development_ledger.py"], [ROOT_TESTS]),
    "LSN-0142": ([CP + "audit-harness/with_local_engine.py",
                   CP + "audit-harness/recover_owned_verification.py"], [ROOT_TESTS]),
    "LSN-0143": ([CP + "audit-harness/run_full_verification.py",
                   "scripts/iacode/gates/lint.py"], [ROOT_TESTS]),
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
    experience = functional["scenarios"]["experience-store-e2e.json"]
    if (verification.get("result") != "PASS" or verification.get("fast") is not False
            or any(row["result"] != "PASS" for row in verification["stages"])
            or publication.get("result") != "PASS" or acceptance.get("status") != "PASS"
            or experience.get("sourceFingerprint") != scope_fingerprint(ROOT)
            or experience.get("subjectCommit") != publication.get("publishedCommit")):
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
            row["notes"] = "Authored Gate 6 artifact/test mapping and complete immutable current-source execution. Same-session only; formal ordered closure remains separately enforced by STATE and its assurance reports."
        elif reference.startswith("lesson:") and reference[7:] in NEW_LESSONS:
            artifacts, cases = NEW_LESSONS[reference[7:]]
            evidence = mapped(artifacts, cases, ["docs/ENGINEERING-MEMORY.md", CP + "PLAN.md"])
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
