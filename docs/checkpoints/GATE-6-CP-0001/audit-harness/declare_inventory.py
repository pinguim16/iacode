"""Declare the actual Gate 6 delta through authored closed scope reasons; never promote a verdict."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))

from ledger_common import canonical_hash_bytes, canonical_hash_path, load_json, use_utf8_stdout, write_json


def git(*arguments: str, binary: bool = False) -> bytes | str:
    result = subprocess.run(["git", *arguments], cwd=ROOT, check=True, capture_output=True,
                            text=not binary, encoding=None if binary else "utf-8")
    return result.stdout


def reason(path: str) -> str:
    if path == ".iacode/anchors/checkpoint-chain.json":
        return "Canonically anchor sealed Gate 5 without changing any predecessor tag, commit or tree."
    if path.startswith("docs/checkpoints/GATE-6-CP-0001/"):
        return "Record current Gate 6 authority, derived requirements, plan, observable implementation/assurance evidence and resumable handoff."
    if path == "docs/checkpoints/LATEST.md":
        return "Point to the separate explicitly authorized Gate 6 checkpoint."
    if path in {"docs/GATE-6-CHECKLIST.md", ".iacode/policies/canonical-requirements.json"}:
        return "Define and derive the complete mandatory Gate 6 specification before implementation, preserving all predecessor requirements."
    if path in {"START-HERE.md", "docs/ARCHITECTURE.md", "docs/DEVELOPMENT.md"}:
        return "Align live entry/architecture with authorized experience persistence and checkpoint-owned acceptance, without claiming a Gate verdict."
    if path.startswith("docs/adr/"):
        return "Record and atomically index the source-bound experience and finite retention architecture."
    if path.startswith("services/experience/"):
        return "Implement and prove the closed provider-neutral source/store-port experience boundary, consumed policy, privacy, rights and retention decisions."
    if path.startswith("apps/api/"):
        return "Evolve and test actual experience persistence, migrations, source/evidence adapters, authenticated project-scoped API and owned automatic retention lifecycle."
    if path.startswith("packages/contracts/") or path.startswith("packages/persistence/"):
        return "Define the shared versioned experience wire/persistence contract, schema evolution and database integrity constraints."
    if path.startswith("packages/telemetry/"):
        return "Keep new experience request targets and rejected content out of logs while preserving bounded operational observability."
    if path in {".iacode/schemas/experience.schema.json", ".iacode/policies/experience-policy.json"}:
        return "Version the complete consumed closed experience schema and finite rights/retention policy."
    if path in {".iacode/policies/quality-gates.json", ".iacode/policies/test-suites.json", "ruff.toml", ".gitattributes"}:
        return "Register complete experience quality/collection and exact evidence transport without dropping inherited gates, suites or scanner controls."
    if path.startswith("scripts/iacode/"):
        return "Execute real experience image tests and owned live acceptance within the full canonical verifier while preserving inherited stages and producer evidence."
    if path == "scripts/development-ledger/README.md":
        return "Align the tool documentation with Gate6 ownership of the generated experience schema, without changing control logic or any sealed subject."
    if path.startswith("tests/test_gate6_"):
        return "Prove Gate 6 specification, scope, boundaries, actual integration-harness behavior, collection and causal adverse controls."
    if path.startswith(".iacode/memory/"):
        return "Record observed causal lessons/guardrails or the Gate6 retrospective truthfully, without secrets or inferred training rights."
    if path.startswith("docs/runbooks/"):
        return "Document actual experience consent, API/access, lineage/rights, retention, withdrawal/recovery and operational limits."
    raise ValueError("undeclared Gate 6 scope reason: " + path)


def main() -> int:
    use_utf8_stdout()
    base = load_json(CHECKPOINT / "STATE.json")["baseCommit"]
    changed = set(str(git("diff", "--name-only", base)).splitlines())
    changed.update(str(git("ls-files", "--others", "--exclude-standard")).splitlines())
    document = {"filesRead": [{"path": path, "reason": why} for path, why in (
        ("START-HERE.md", "Mandatory current entry contract."),
        ("docs/DEVELOPMENT-CONTRACT.md", "Canonical mandatory delivery order and safety rules."),
        ("docs/MASTER-PLAN.md", "Authorized Gate 6 objective and milestone boundary."),
        ("docs/GATE-6-CHECKLIST.md", "Complete current canonical specification."),
        ("docs/checkpoints/GATE-5-CP-0001/STATE.json", "Sealed predecessor observed before alterations."),
        ("docs/checkpoints/GATE-5-CP-0001/HANDOFF.md", "Immutable predecessor continuation and exclusions."),
    )], "filesCreated": [], "filesModified": [], "filesDeleted": []}
    for path in sorted(changed):
        existed = subprocess.run(["git", "cat-file", "-e", f"{base}:{path}"], cwd=ROOT,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False).returncode == 0
        exists = (ROOT / path).is_file()
        category = "filesModified" if existed and exists else "filesDeleted" if existed else "filesCreated"
        item = {"path": path, "reason": reason(path)}
        if path != CHECKPOINT.relative_to(ROOT).as_posix() + "/FILES.json":
            if existed:
                item["hashBefore"] = canonical_hash_bytes(git("show", f"{base}:{path}", binary=True))
            if exists:
                item["hashAfter"] = canonical_hash_path(ROOT / path)
        document[category].append(item)
    write_json(CHECKPOINT / "FILES.json", document)
    print("INVENTORY_DECLARED " + " ".join(f"{key}={len(document[key])}" for key in
        ("filesCreated", "filesModified", "filesDeleted")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
