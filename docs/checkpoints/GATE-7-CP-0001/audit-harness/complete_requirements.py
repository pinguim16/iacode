"""Assemble reviewed Gate7 evidence; never substitute implementation status for ordered closure."""

from __future__ import annotations

import json
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]
BASELINE = "GATE-6-CP-0001"
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))

CP = "docs/checkpoints/GATE-7-CP-0001/"
CONTRACT = "packages/contracts/src/iacode_contracts/knowledge.py"
DOMAIN = "services/knowledge/src/iacode_knowledge/domain.py"
SOURCES = "apps/api/src/iacode_api/knowledge/sources.py"
STORE = "apps/api/src/iacode_api/knowledge/store.py"
RUNTIME = "apps/api/src/iacode_api/knowledge/runtime.py"
API = "apps/api/src/iacode_api/routes/knowledge.py"
MODELS = "packages/persistence/src/iacode_persistence/models.py"
MIGRATION = "apps/api/migrations/versions/0008_knowledge_engine.py"
POLICY = ".iacode/policies/knowledge-policy.json"
SCHEMA = ".iacode/schemas/knowledge.schema.json"
ROOT_TESTS = "tests/test_gate7_knowledge.py"
ASSURANCE_TESTS = "tests/test_gate7_assurance.py"
DOMAIN_TESTS = "services/knowledge/tests/test_domain.py"
API_TESTS = "apps/api/tests/unit/test_knowledge_api.py"
SQL_TESTS = "apps/api/tests/integration/test_knowledge_engine.py"
STRUCTURE_TESTS = "apps/api/tests/unit/test_knowledge_structure.py"
LIVE = "scripts/iacode/scenarios/knowledge_engine_e2e.py"
CORPUS = "services/knowledge/tests/fixtures/retrieval-corpus.json"
RUNBOOK = "docs/runbooks/KNOWLEDGE-ENGINE.md"
PUBLISHER = CP + "audit-harness/run_full_verification.py"
CANONICAL = {}


def mapped(artifacts, tests, docs=None):
    return {
        "implementationEvidence": ["file:" + path for path in artifacts],
        "testEvidence": ["file:" + path for path in tests],
        "negativeTestEvidence": ["file:" + path for path in tests] + ["checkpoint:FINDINGS.json"],
        "documentationEvidence": ["file:" + path for path in (docs or [RUNBOOK])],
        "validationEvidence": [
            "checkpoint:VERIFY.json",
            "checkpoint:PUBLISHED-CLEAN-CLONE-REPORT.json",
        ],
        "guardrailEvidence": ["file:.iacode/memory/guardrails/registry.json"],
    }


def bind(keys, artifacts, tests, docs=None):
    for key in keys.split():
        if key in CANONICAL:
            raise ValueError("duplicate authored requirement mapping")
        CANONICAL[key] = mapped(artifacts, tests, docs)


bind(
    "1.1",
    [CP + "AUTHORIZATION.md", ".iacode/anchors/checkpoint-chain.json"],
    [ROOT_TESTS, "tests/test_gate0_foundation.py"],
    ["docs/DEVELOPMENT-CONTRACT.md"],
)
bind(
    "1.2",
    [
        "docs/GATE-7-CHECKLIST.md",
        ".iacode/policies/canonical-requirements.json",
        "scripts/development-ledger/derive_requirements.py",
    ],
    [ROOT_TESTS],
)
bind(
    "1.3",
    [
        "docs/adr/ADR-0053-knowledge-requires-content-bound-source-permission.md",
        "docs/adr/ADR-0054-knowledge-indexes-are-rebuildable-cited-projections.md",
        "docs/adr/ADR-0055-code-graph-remains-an-explicit-future-reservation.md",
        "docs/adr/ADR-0056-minimal-protocol-fixtures-inherit-only-control-contracts.md",
        "docs/adr/ADR-0057-build-and-verification-root-inputs-follow-subject-versioned-assurance.md",
        "docs/adr/ADR-0058-immutable-review-git-reads-use-child-scoped-long-path-handling.md",
        "docs/adr/ADR-0059-full-verifier-consumers-use-complete-canonical-archived-producers.md",
        "docs/adr/ADR-0060-native-drain-allows-natural-exit-within-the-existing-deadline.md",
    ],
    [ROOT_TESTS],
    ["docs/ARCHITECTURE.md"],
)
bind("1.4", [CONTRACT, DOMAIN], [ROOT_TESTS, DOMAIN_TESTS])
bind(
    "1.5",
    [
        ".iacode/policies/quality-gates.json",
        ".iacode/policies/test-suites.json",
        "scripts/iacode/verify.py",
        "scripts/iacode/gates/knowledge_tests.py",
    ],
    [ROOT_TESTS, "tests/test_test_suite_input_repositories.py"],
)
bind(
    "2.1 2.2 2.3 2.5",
    [CONTRACT, SOURCES, DOMAIN, POLICY, SCHEMA],
    [DOMAIN_TESTS, API_TESTS, SQL_TESTS],
)
bind(
    "2.4",
    [
        SOURCES,
        "apps/api/src/iacode_api/experience/sources.py",
        "services/experience/src/iacode_experience/domain.py",
        LIVE,
    ],
    [SQL_TESTS, DOMAIN_TESTS, "apps/api/tests/integration/test_experience_store.py"],
)
bind("2.6", [SOURCES, POLICY], [API_TESTS, SQL_TESTS, DOMAIN_TESTS])
bind(
    "2.7 2.8",
    [DOMAIN, CONTRACT, SOURCES, API, "packages/common/src/iacode_common/secret_scanning.py"],
    [DOMAIN_TESTS, API_TESTS, SQL_TESTS],
)
bind("3.1 3.2 3.3", [CONTRACT, DOMAIN, POLICY, SCHEMA], [DOMAIN_TESTS, ROOT_TESTS, SQL_TESTS])
bind("3.4", [DOMAIN, STORE, MIGRATION, MODELS], [DOMAIN_TESTS, SQL_TESTS])
bind("3.5 3.6", [STORE, DOMAIN, MIGRATION, CORPUS, LIVE], [DOMAIN_TESTS, SQL_TESTS])
bind(
    "4.1",
    [MIGRATION, MODELS],
    [
        SQL_TESTS,
        STRUCTURE_TESTS,
        "apps/api/tests/unit/test_domain_model.py",
        "apps/api/tests/integration/test_migrations.py",
    ],
)
bind("4.2 4.3", [STORE, MIGRATION, MODELS, LIVE], [SQL_TESTS, DOMAIN_TESTS])
bind("4.4 4.5", [STORE, DOMAIN, SOURCES, LIVE], [SQL_TESTS, DOMAIN_TESTS, API_TESTS])
bind(
    "5.1",
    [API, RUNTIME, "apps/api/src/iacode_api/middleware/desktop_auth.py"],
    [API_TESTS, SQL_TESTS, "apps/api/tests/unit/test_desktop_api.py"],
)
bind("5.2 5.3 5.4", [API, STORE, DOMAIN, CORPUS, LIVE], [SQL_TESTS, DOMAIN_TESTS, API_TESTS])
bind(
    "5.5",
    [
        API,
        "packages/telemetry/src/iacode_telemetry/logging.py",
        "apps/api/src/iacode_api/middleware/correlation.py",
    ],
    [API_TESTS, SQL_TESTS],
)
bind("5.6", [DOMAIN, API, SOURCES, LIVE], [ROOT_TESTS, SQL_TESTS, DOMAIN_TESTS])
bind("6.1 6.2 6.4", [DOMAIN, STORE, API, SOURCES, LIVE], [SQL_TESTS, API_TESTS, DOMAIN_TESTS])
bind("6.3 6.5", [RUNTIME, STORE, MIGRATION, POLICY, RUNBOOK], [SQL_TESTS, API_TESTS, DOMAIN_TESTS])
bind(
    "7.1 7.2 7.3",
    [
        LIVE,
        CORPUS,
        "scripts/iacode/scenarios/knowledge_corpus_actor.py",
        "scripts/iacode/desktop_test_support.py",
    ],
    [ROOT_TESTS, SQL_TESTS, API_TESTS],
)
bind(
    "7.4 7.5",
    [
        PUBLISHER,
        "scripts/iacode/verify.py",
        CP + "audit-harness/execute_live_knowledge.py",
        ".gitattributes",
    ],
    [ROOT_TESTS],
)
bind("8.1", [RUNBOOK, "services/knowledge/README.md", "docs/ARCHITECTURE.md"], [ROOT_TESTS])
bind(
    "8.2 8.6",
    [
        "scripts/development-ledger/derive_requirements.py",
        "scripts/development-ledger/check_completeness.py",
        "scripts/development-ledger/derive_counts.py",
        CP + "audit-harness/declare_inventory.py",
    ],
    [ROOT_TESTS, "tests/test_development_ledger.py"],
    ["docs/DEVELOPMENT-CONTRACT.md", "docs/ENGINEERING-MEMORY.md"],
)
bind(
    "8.3",
    [
        "scripts/development-ledger/green_keeper.py",
        "scripts/development-ledger/m0_mirror_audit.py",
        PUBLISHER,
        CP + "audit-harness/run_internal_red_team.py",
    ],
    [ROOT_TESTS, "tests/test_development_ledger.py", "tests/test_gate4_quality_engine.py"],
)
bind(
    "8.4 8.7",
    [
        "scripts/development-ledger/validate_checkpoint.py",
        "scripts/development-ledger/seal_checkpoint.py",
        "scripts/development-ledger/review_bundle.py",
        CP + "audit-harness/publish_progress.py",
    ],
    [ROOT_TESTS, "tests/test_development_ledger.py", "tests/test_gate5_clients.py"],
    ["docs/CHECKPOINT-PROTOCOL.md"],
)
bind(
    "8.5",
    ["docs/checkpoints/M2-CONSOLIDATION.md", ".iacode/memory/retrospectives/GATE-7-CP-0001.md"],
    [ROOT_TESTS, "tests/test_development_ledger.py"],
    ["docs/checkpoints/M2-CONSOLIDATION.md", "docs/MILESTONE-VALIDATION.md"],
)
bind(
    "8.8",
    [
        CP + "AUTHORIZATION.md",
        CP + "STATE.json",
        "scripts/development-ledger/validate_checkpoint.py",
    ],
    ["tests/test_gate4_quality_engine.py", "tests/test_development_ledger.py"],
    [
        "docs/MILESTONE-VALIDATION.md",
        "docs/adr/ADR-0037-intermediate-gates-use-internal-closure.md",
    ],
)

NEW_LESSONS = {
    "LSN-0151": (
        [
            "scripts/development-ledger/review_bundle.py",
            "docs/adr/ADR-0058-immutable-review-git-reads-use-child-scoped-long-path-handling.md",
        ],
        ["tests/test_gate7_git_transport.py", "tests/test_gate4_quality_engine.py"],
    ),
    "LSN-0077": (
        ["scripts/iacode/scenarios/quality_engine_e2e.py", ".iacode/policies/quality-policy.json"],
        ["tests/test_gate7_quality_observation.py", "tests/test_gate4_quality_engine.py"],
    ),
    "LSN-0110": (
        [
            "scripts/iacode/scenarios/quality_engine_e2e.py",
            "scripts/iacode/native_process.py",
            "scripts/iacode/native_editor.py",
            CP + "NATIVE-REWORK-CONTEXT-02.json",
        ],
        [
            "tests/test_gate7_quality_observation.py",
            "tests/test_gate4_quality_engine.py",
            "tests/test_gate7_native_cleanup.py",
        ],
    ),
    "LSN-0128": (
        [
            "scripts/iacode/scenarios/desktop_e2e.py",
            "tests/test_gate7_quality_observation.py",
            CP + "NATIVE-REWORK-CONTEXT.json",
            "tests/test_gate7_native_cleanup.py",
        ],
        [
            "tests/test_gate5_clients.py",
            "tests/test_gate7_quality_observation.py",
            "tests/test_gate7_native_cleanup.py",
        ],
    ),
    "LSN-0125": (
        [
            "scripts/iacode/native_process.py",
            "scripts/iacode/native_editor.py",
            "docs/adr/ADR-0060-native-drain-allows-natural-exit-within-the-existing-deadline.md",
            CP + "NATIVE-REWORK-CONTEXT.json",
            CP + "NATIVE-REWORK-CONTEXT-02.json",
        ],
        [
            "tests/test_gate7_native_cleanup.py",
            "tests/test_gate6_experience.py",
            "tests/test_gate5_clients.py",
        ],
    ),
    "LSN-0150": (
        [
            ".iacode/policies/assurance-scope.json",
            "scripts/development-ledger/ledger_common.py",
            "docs/adr/ADR-0057-build-and-verification-root-inputs-follow-subject-versioned-assurance.md",
        ],
        [ASSURANCE_TESTS, "tests/test_gate5_clients.py", "tests/test_development_ledger.py"],
    ),
    "LSN-0145": (
        [MODELS, MIGRATION, STRUCTURE_TESTS],
        [STRUCTURE_TESTS, SQL_TESTS, "apps/api/tests/unit/test_domain_model.py"],
    ),
    "LSN-0146": (
        [CP + "audit-harness/publish_progress.py", CP + "audit-harness/verify_original_bytes.py"],
        [ROOT_TESTS, ASSURANCE_TESTS, "tests/test_gate7_publication_paths.py"],
    ),
    "LSN-0147": (["scripts/iacode/verify.py"], [ASSURANCE_TESTS]),
    "LSN-0148": (
        ["scripts/development-ledger/promotion_fixture.py"],
        [ASSURANCE_TESTS, "tests/test_development_ledger.py"],
    ),
    "LSN-0149": ([CP + "audit-harness/verify_original_bytes.py"], [ASSURANCE_TESTS]),
    "LSN-0029": (
        [".iacode/policies/gate-scope.json", "services/code-graph/README.md"],
        [ASSURANCE_TESTS, "tests/test_gate3_sandbox.py"],
    ),
    "LSN-0083": (
        [
            CP + "audit-harness/publish_progress.py",
            CP + "audit-harness/run_knowledge_integration.py",
        ],
        [ASSURANCE_TESTS, "tests/test_gate0_foundation.py"],
    ),
    "LSN-0102": (
        ["tests/test_gate5_clients.py", ROOT_TESTS, ".iacode/policies/quality-gates.json"],
        [ROOT_TESTS, "tests/test_gate6_experience.py", "tests/test_gate5_clients.py"],
    ),
    "LSN-0018": (
        ["scripts/development-ledger/lessons.py", ".iacode/memory/guardrails/registry.json"],
        ["tests/test_development_ledger.py", ROOT_TESTS],
    ),
    "LSN-0011": (
        [
            "scripts/development-ledger/sync_in_progress_metadata.py",
            CP + "audit-harness/run_checkpoint_validation.py",
            CP + "audit-harness/publish_progress.py",
        ],
        ["tests/test_in_progress_metadata.py", ROOT_TESTS],
    ),
    "LSN-0105": (
        ["scripts/iacode/gates/lint.py", CP + "audit-harness/format_current_python.py"],
        [ROOT_TESTS, ASSURANCE_TESTS, "tests/test_gate5_clients.py"],
    ),
    "LSN-0117": (
        ["README.md", "docs/ARCHITECTURE.md", ROOT_TESTS],
        [ROOT_TESTS, "tests/test_gate5_clients.py"],
    ),
    "LSN-0119": (
        [
            CONTRACT,
            "scripts/development-ledger/validate_checkpoint.py",
            "packages/common/src/iacode_common/secret_scanning.py",
        ],
        [DOMAIN_TESTS, "tests/test_gate5_clients.py"],
    ),
    "LSN-0131": ([".gitattributes", PUBLISHER], [ROOT_TESTS, "tests/test_gate5_clients.py"]),
    "LSN-0135": (
        [
            PUBLISHER,
            CP + "audit-harness/execute_live_knowledge.py",
            CP + "audit-harness/diagnose_promotion_producer.py",
            CP + "audit-harness/import_rework_contexts.py",
            CP + "REWORK-CONTEXT-ARCHIVE.json",
        ],
        [ROOT_TESTS, ASSURANCE_TESTS, "tests/test_gate5_clients.py"],
    ),
    "LSN-0136": ([CONTRACT, DOMAIN], [DOMAIN_TESTS, SQL_TESTS]),
    "LSN-0137": ([STORE, SQL_TESTS], [SQL_TESTS]),
    "LSN-0138": ([RUNTIME, API, SOURCES], [API_TESTS, SQL_TESTS]),
    "LSN-0139": ([STORE, SOURCES], [SQL_TESTS]),
    "LSN-0140": (
        [
            CP + "audit-harness/assemble_final_handoff.py",
            CP + "audit-harness/write_progress_handoff.py",
            "scripts/development-ledger/validate_checkpoint.py",
        ],
        [
            ROOT_TESTS,
            ASSURANCE_TESTS,
            "tests/test_gate5_clients.py",
            "tests/test_gate6_experience.py",
            "tests/test_gate7_continuation.py",
        ],
    ),
    "LSN-0008": (
        [
            CP + "audit-harness/assemble_final_handoff.py",
            "scripts/development-ledger/validate_checkpoint.py",
        ],
        ["tests/test_development_ledger.py", ROOT_TESTS],
    ),
}


def inherited(reference):
    kind, _, value = reference.partition(":")
    if kind == "checkpoint":
        return f"file:docs/checkpoints/{BASELINE}/{value}"
    if kind == "command":
        return f"file:docs/checkpoints/{BASELINE}/COMMANDS.jsonl"
    return reference


def main() -> int:
    from ledger_common import use_utf8_stdout

    use_utf8_stdout()
    from complete_functional_acceptance import current_execution
    from delivery_assurance import collect_test_ids, load_command_results, resolve_evidence
    from derive_requirements import EVIDENCE_FIELDS, render_closure, render_matrix
    from ledger_common import LedgerError, load_json, write_json

    if load_json(CHECKPOINT / "STATE.json")["status"] != "IN_PROGRESS":
        raise LedgerError("never rewrite terminal or sealed requirement evidence")
    current_execution()
    acceptance = load_json(CHECKPOINT / "FUNCTIONAL-ACCEPTANCE-VALIDATION.json")
    if acceptance.get("result") != "PASS" or acceptance.get("missing"):
        raise LedgerError("actual canonical complete functional acceptance is required")
    raw = subprocess.check_output(
        [
            "git",
            "show",
            f"iacode-checkpoints/{BASELINE}:docs/checkpoints/{BASELINE}/CLOSURE-REQUIREMENTS.json",
        ],
        cwd=ROOT,
    )
    baseline = {row["sourceRef"]: row for row in json.loads(raw)["requirements"]}
    closure = deepcopy(load_json(CHECKPOINT / "CLOSURE-REQUIREMENTS.json"))
    matrix = deepcopy(load_json(CHECKPOINT / "REQUIREMENTS-MATRIX.json"))
    tests, commands = collect_test_ids(ROOT), load_command_results(CHECKPOINT)
    canonical_refs = {
        row["sourceRef"].split("#")[-1]
        for row in closure["requirements"]
        if row["sourceRef"].startswith("canonical:")
    }
    if canonical_refs != set(CANONICAL):
        raise LedgerError("authored mappings differ from the entire canonical derived set")
    mapped_rows = {}
    for row in closure["requirements"]:
        reference = row["sourceRef"]
        if reference.startswith("canonical:"):
            evidence = deepcopy(CANONICAL[reference.split("#")[-1]])
            evidence["validationEvidence"].append("checkpoint:FUNCTIONAL-ACCEPTANCE.json")
            row["notes"] = (
                "Reviewed Gate7 implementation/protocol mapping and one complete immutable current "
                "execution. Ordered Green Keeper/completeness/Red Team/mirror and actual terminal "
                "commit/seal/publication are separately mandatory in STATE and their real reports; "
                "COMPLETE here does not predict a future operation or grant independent approval."
            )
        elif reference.startswith("lesson:") and reference[7:] in NEW_LESSONS:
            artifacts, cases = NEW_LESSONS[reference[7:]]
            evidence = mapped(artifacts, cases, ["docs/ENGINEERING-MEMORY.md", CP + "PLAN.md"])
            evidence["validationEvidence"].append("checkpoint:FUNCTIONAL-SCENARIOS.json")
            row["notes"] = (
                "Direct current causal artifacts and executed positive/adverse controls, with "
                "original failures/recurrence retained and all mandatory suites freshly "
                "re-executed. "
                "This is not independent milestone validation."
            )
        else:
            prior = baseline.get(reference)
            if prior is None or prior.get("finalStatus") != "COMPLETE":
                raise LedgerError("no reviewed sealed baseline or direct mapping for " + reference)
            evidence = {
                field: [inherited(value) for value in prior[field]] for field in EVIDENCE_FIELDS
            }
            evidence["validationEvidence"].append("checkpoint:VERIFY.json")
            row["notes"] = (
                "Sealed Gate6 lesson implementation/guard evidence plus complete current immutable "
                "re-execution of every mandatory suite/scenario; historical verdicts remain "
                "unchanged."
            )
        for field, values in evidence.items():
            row[field] = list(dict.fromkeys(values))
            if not row[field]:
                raise LedgerError(reference + " lacks " + field)
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
        for field in (
            "implementationEvidence",
            "testEvidence",
            "documentationEvidence",
            "validationEvidence",
        ):
            row[field] = list(source[field])
    write_json(CHECKPOINT / "CLOSURE-REQUIREMENTS.json", closure)
    write_json(CHECKPOINT / "REQUIREMENTS-MATRIX.json", matrix)
    (CHECKPOINT / "CLOSURE-REQUIREMENTS.md").write_text(
        render_closure(closure), encoding="utf-8", newline="\n"
    )
    (CHECKPOINT / "REQUIREMENTS-MATRIX.md").write_text(
        render_matrix(matrix), encoding="utf-8", newline="\n"
    )
    print(f"REQUIREMENT_EVIDENCE_ASSEMBLY=PASS total={len(mapped_rows)}; closure not inferred")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
