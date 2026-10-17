#!/usr/bin/env python3
"""Declare this checkpoint's actual delta using authored, closed path reasons."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))

from ledger_common import canonical_hash_bytes, canonical_hash_path, use_utf8_stdout, write_json  # noqa: E402


def git(*arguments: str, binary: bool = False) -> bytes | str:
    result = subprocess.run(["git", *arguments], cwd=ROOT, check=True,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            text=not binary, encoding=None if binary else "utf-8")
    return result.stdout


def reason(path: str) -> str:
    if path == ".iacode/anchors/checkpoint-chain.json":
        return "Anchor sealed Gate 4 CP0010 with the canonical chain rebuilder, preserving every historical tag, commit and tree identity."
    if path.startswith(".iacode/memory/"):
        return "Preserve and resolve the observed historical/current Gate recurrence and causal architecture-rollup failure with executable guards."
    if path in {"docs/GATE-5-CHECKLIST.md", ".iacode/policies/canonical-requirements.json"}:
        return "Establish the complete Gate 5 canonical requirement set before implementation; preserve every predecessor row."
    if path == ".iacode/policies/secret-scan-allowlist.json":
        return "Review only exact observed code-reference component digests; preserve all scanner rules and blocking behavior for every other value."
    if path.startswith("docs/checkpoints/GATE-5-CP-0001/"):
        return "Record truthful in-progress Gate 5 authorization, requirements, baseline, plan, implementation observations and executable continuation."
    if path == "docs/checkpoints/LATEST.md":
        return "Advance the live pointer to the separately authorized Gate 5 checkpoint."
    if path.startswith("docs/adr/"):
        return "Record and atomically index the authenticated runtime-adapter architecture before structural changes."
    if path in {"START-HERE.md", "docs/ARCHITECTURE.md", "docs/DEVELOPMENT.md"}:
        return "Align current entry and architecture with sealed Gate 4 and truthful Gate 5 work in progress, without claiming client acceptance."
    if path.startswith("apps/api/"):
        return "Implement and test authenticated desktop ingress, closed governed adapters and consent-bound scanned snapshots without host tool execution."
    if path.startswith("infra/tests/"):
        return "Classify decoded committed environment literals through the unchanged canonical taxonomy; retain full infrastructure and backup secrecy assertions after actual Compose disagreement."
    if path in {"tests/test_gate1_model_gateway.py", "tests/test_gate3_sandbox.py"}:
        return "Repair demonstrated serialized-value and historical pre-owner test premises using canonical literal decoding and policy-derived scope lifecycle; retain every correct boundary assertion."
    if path.startswith("packages/common/") or path.startswith("packages/contracts/"):
        return "Define one byte-exact authenticated desktop protocol, shared contracts and strict request validation."
    if path.startswith("services/orchestrator/") or path in {"infra/compose/docker-compose.yml", "infra/compose/.env.example"}:
        return "Supply infrastructure API authentication outside the provider-neutral agent domain and preserve explicit legacy development mode."
    if path.startswith("apps/cli/"):
        return "Implement and test the bounded authenticated shared core, consent preview and standalone CLI; actual installation/runtime acceptance remains separate evidence."
    if path.startswith("apps/vscode-extension/"):
        return "Implement and test native editor commands, trust and exact consent, SecretStorage, plaintext results and stable recovery without host execution."
    if path.startswith("scripts/iacode/"):
        return "Build closed deterministic client packages, execute complete client tests, lint and graph checks, and extend mandatory live verification without dropping inherited controls."
    if path.startswith("docs/runbooks/"):
        return "Document authenticated desktop installation, limits, exact approvals, truthful status/recovery, failure and removal procedures."
    if path in {".gitattributes", ".gitignore", "ruff.toml", ".iacode/policies/quality-gates.json", ".iacode/policies/quality-policy.json",
                ".iacode/policies/test-suites.json", ".iacode/schemas/test-suites.schema.json",
                "scripts/development-ledger/policies.py", "scripts/development-ledger/ledger_common.py",
                "scripts/development-ledger/validate_checkpoint.py", ".iacode/policies/assurance-scope.json",
                "tests/test_test_suite_input_repositories.py"}:
        return "Version explicit native suite declarations and preserve historical collection semantics, all counted suites and every inherited mandatory gate; ignore generated client artifacts only."
    if path.startswith("services/evaluator/"):
        return "Include CommonJS/ESM tests and plain Node client roots in real mixed-project quality planning, preserving Angular and inherited checks."
    if path.startswith("services/agent-runtime/"):
        return "Repair the observed Gate5 repeated-cancellation integration by preserving an already cancelled terminal result, while retaining refusal of successful/failed terminals and requested-versus-completed semantics."
    if path in {"tests/test_gate4_quality_engine.py", "tests/test_gate5_clients.py"}:
        return "Separate historical fixture ownership from live scope, prove a future Gate transition and guard the observed documentation contradiction."
    raise RuntimeError(f"no authored Gate 5 inventory reason for {path!r}")


def main() -> int:
    use_utf8_stdout()
    state = json.loads((CHECKPOINT / "STATE.json").read_text(encoding="utf-8"))
    base = state["baseCommit"]
    changed = set(str(git("diff", "--name-only", base)).splitlines())
    changed.update(str(git("ls-files", "--others", "--exclude-standard")).splitlines())
    document = {"filesRead": [
        {"path": path, "reason": why} for path, why in (
            ("START-HERE.md", "Required entry contract."),
            ("docs/DEVELOPMENT-CONTRACT.md", "Canonical delivery contract."),
            ("docs/MASTER-PLAN.md", "Authorized Gate scope and milestones."),
            ("docs/GATE-5-CHECKLIST.md", "Complete current canonical requirements."),
            ("docs/checkpoints/GATE-4-CP-0010/STATE.json", "Immutable sealed predecessor state."),
            ("docs/checkpoints/GATE-4-CP-0010/HANDOFF.md", "Predecessor handoff and entry conditions."),
        )], "filesCreated": [], "filesModified": [], "filesDeleted": []}
    for raw in sorted(changed):
        path = raw.replace("\\", "/")
        if not path:
            continue
        existed = subprocess.run(["git", "cat-file", "-e", f"{base}:{path}"], cwd=ROOT,
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                 check=False).returncode == 0
        exists = (ROOT / path).is_file()
        category = "filesModified" if existed and exists else "filesDeleted" if existed else "filesCreated"
        item = {"path": path, "reason": reason(path)}
        if path != str((CHECKPOINT / "FILES.json").relative_to(ROOT)).replace("\\", "/"):
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
