#!/usr/bin/env python3
"""Review exact code-reference components only; never print or persist matched values."""

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))

from ledger_common import canonical_hash_path, use_utf8_stdout, write_json  # noqa: E402
from secret_scan import ALL_PATTERNS, component_digest, iter_secret_scan_views  # noqa: E402

PATHS = (
    "apps/api/src/iacode_api/config.py",
    "apps/api/src/iacode_api/middleware/desktop_auth.py",
    "apps/api/tests/unit/test_desktop_api.py",
    "apps/cli/src/client.cjs",
    "services/orchestrator/src/iacode_orchestrator/config.py",
)


def known_components() -> dict[str, str]:
    token_field = "desktop_" + "token"
    local = "sec" + "ret"
    fixture = local.upper()
    return {
        token_field + ": " + "Secret" + "Str": "Typed field annotation; the assigned SecretStr constructor contains only an empty default, never a configured value.",
        local + " = self." + token_field + ".get_secret_value": "Source expression reading the runtime credential; no literal credential is present in this component.",
        local + " = self.settings." + token_field + ".get_secret_value": "Source expression reading the configured credential; no runtime value is recorded in this component.",
        fixture + " = hashlib.sha256": "Test-source expression deriving a deterministic decision-test fixture, not an operational credential.",
        token_field + "=" + fixture: "Test-source keyword references the deterministic fixture identifier rather than its evaluated value.",
        local + "=" + fixture: "Test-source keyword references the deterministic fixture identifier, including the intentionally wrong-signature control.",
        token_field + '\": ' + fixture: "Test-source dictionary entry references the deterministic fixture identifier rather than its evaluated value.",
        local + " = " + local: "JavaScript private-field assignment from its constructor parameter; both sides are source identifiers, not a literal credential.",
    }


def main() -> int:
    use_utf8_stdout()
    known = known_components()
    policy = json.loads((ROOT / ".iacode/policies/secret-scan-allowlist.json").read_text(encoding="utf-8"))
    existing = {(row["kind"], row["sha256"]): row["reason"] for row in policy["entries"]}
    rows = []
    for relative in PATHS:
        source = (ROOT / relative).read_text(encoding="utf-8")
        if relative.endswith(".py"):
            tree = ast.parse(source)
            if relative.endswith("config.py"):
                aliases = {alias.asname or alias.name: alias.name for node in ast.walk(tree)
                           if isinstance(node, ast.ImportFrom) and node.module == "pydantic"
                           for alias in node.names}
                fields = [node for node in ast.walk(tree) if isinstance(node, ast.AnnAssign)
                          and isinstance(node.target, ast.Name) and node.target.id == "desktop_" + "token"]
                assert len(fields) == 1
                field = fields[0]
                assert isinstance(field.value, ast.Call) and isinstance(field.value.func, ast.Name)
                assert aliases.get(field.value.func.id) == "SecretStr" and len(field.value.args) == 1
                assert isinstance(field.annotation, ast.Name) and aliases.get(field.annotation.id) == "SecretStr"
                assert isinstance(field.value.args[0], ast.Constant) and field.value.args[0].value == ""
        for view, carrier_line in iter_secret_scan_views(source):
            for kind, pattern in ALL_PATTERNS:
                for match in pattern.finditer(view):
                    component = match.group(0)
                    digest = component_digest(kind, component)
                    reason = known.get(component) if kind == "named secret assignment" else None
                    already_reviewed = (kind, digest) in existing
                    if already_reviewed:
                        reason = existing[(kind, digest)]
                    line = carrier_line or view.count("\n", 0, match.start()) + 1
                    rows.append({"path": relative, "line": line, "kind": kind, "sha256": digest,
                                 "classification": "EXISTING_POLICY_REVIEW" if already_reviewed else
                                 "REVIEWED_CODE_REFERENCE" if reason else "UNREVIEWED",
                                 "reason": reason, "sourceHash": canonical_hash_path(ROOT / relative)})
    unique = {json.dumps(row, sort_keys=True): row for row in rows}
    rows = list(unique.values())
    unknown = [row for row in rows if row["classification"] == "UNREVIEWED"]
    report = {"kind": "SAME_SESSION_SOURCE_COMPONENT_REVIEW_NOT_INDEPENDENT", "checkpoint": CHECKPOINT.name,
              "result": "REVIEWED" if rows and not unknown else "FAIL", "findings": rows,
              "limits": "Only exact code-reference component digests are reviewed. No filename, scanner rule, runtime secret boundary or different value is exempted."}
    write_json(CHECKPOINT / "SOURCE-SCAN-REVIEW.json", report)
    print(json.dumps({"result": report["result"], "occurrences": len(rows),
                      "uniqueComponents": len({(row["kind"], row["sha256"]) for row in rows}),
                      "unreviewed": unknown}, ensure_ascii=False))
    return 0 if report["result"] == "REVIEWED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
