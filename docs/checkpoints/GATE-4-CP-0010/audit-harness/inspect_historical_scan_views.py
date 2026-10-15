#!/usr/bin/env python3
"""Compare source-view interpretation without printing or retaining any matched value."""

from __future__ import annotations

import ast
import inspect
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))
from secret_scan import ALL_PATTERNS, component_digest
from ledger_common import write_json
import iacode_common.secret_scanning as scanning


class RemoveUnescapedFastPath(ast.NodeTransformer):
    def visit_If(self, node):
        if (isinstance(node.test, ast.Compare) and isinstance(node.test.left, ast.Constant)
                and node.test.left.value == "\\"):
            return None
        return self.generic_visit(node)


def main() -> int:
    tree = ast.parse(inspect.getsource(scanning.iter_secret_scan_views))
    tree = ast.fix_missing_locations(RemoveUnescapedFastPath().visit(tree))
    namespace = dict(vars(scanning))
    exec(compile(tree, "isolated-view-comparison", "exec"), namespace)
    source = subprocess.run(
        ["git", "show", "aedc17a:tests/test_development_ledger.py"], cwd=ROOT,
        capture_output=True, text=True, encoding="utf-8", check=True,
    ).stdout
    source_tree = ast.parse(source)
    parents = {child: parent for parent in ast.walk(source_tree)
               for child in ast.iter_child_nodes(parent)}
    rows = []
    for mode, function in (("current", scanning.iter_secret_scan_views),
                           ("without-unescaped-fast-path", namespace["iter_secret_scan_views"])):
        seen = set()
        for view, carrier in function(source):
            for name, pattern in ALL_PATTERNS:
                if name not in {"bearer credential", "named secret assignment"}:
                    continue
                for match in pattern.finditer(view):
                    digest = component_digest(name, match.group(0))
                    key = (name, digest, carrier)
                    if key in seen:
                        continue
                    seen.add(key)
                    redacted_view = scanning.redact_secret_patterns(view)
                    if scanning.find_secret_kinds(redacted_view):
                        raise RuntimeError("historical fixture observation is not sanitized")
                    payload = match.group(0).partition(" ")[2] if name == "bearer credential" else (
                        match.group(0).partition("=")[2])
                    literal_contexts = []
                    for node in ast.walk(source_tree):
                        if isinstance(node, ast.Constant) and node.value == view:
                            ancestor = parents.get(node)
                            while ancestor is not None and not isinstance(ancestor, ast.FunctionDef):
                                ancestor = parents.get(ancestor)
                            literal_contexts.append({"line": node.lineno,
                                                     "function": ancestor.name if ancestor else None})
                    rows.append({"mode": mode, "kind": name, "sha256": digest,
                                 "carrierLine": carrier,
                                 "redactedShape": scanning.redact_secret_patterns(match.group(0)),
                                 "viewContainsEscapes": "\\" in view,
                                 "redactedView": redacted_view,
                                 "matchingSourceLiterals": literal_contexts,
                                 "componentIsAlphabetSequence": payload.lower() in (
                                     "abcdefghijklmnopqrstuvwxyz" * 2),
                                 "viewLength": len(view)})
    contexts = sorted({literal["function"] for row in rows
                       for literal in row["matchingSourceLiterals"] if literal["function"]})
    reviewed = bool(rows) and all(
        row["componentIsAlphabetSequence"] and row["matchingSourceLiterals"]
        and all(item["function"] == "test_redactor_replaces_known_shapes"
                for item in row["matchingSourceLiterals"]) for row in rows
    )
    document = {"sourceContexts": contexts,
                "sourceReference": "aedc17a:tests/test_development_ledger.py",
                "classification": "SYNTHETIC_REDACTION_TEST_MARKERS" if reviewed else "REVIEW_REQUIRED",
                "matches": rows}
    write_json(Path(__file__).resolve().parent.parent / "HISTORICAL-SCAN-REVIEW.json", document)
    print(json.dumps(document, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
