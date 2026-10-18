"""Knowledge delivery controls and causal root-level guards, not substituted live acceptance."""

from __future__ import annotations

import json
import ast
import re
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))

import ledger_common


def owned_capability_titles(root: Path) -> tuple[str, ...]:
    gate = ledger_common.delivered_gate(root)
    match = re.fullmatch(r"GATE(\d+)", ledger_common.normalize_gate(gate))
    if match is None:
        raise ValueError("the current delivery has no numbered Gate")
    current = int(match.group(1))
    plan = (root / "docs/MASTER-PLAN.md").read_text(encoding="utf-8")
    rows = re.findall(r"^\| GATE (\d+) — ([^|]+?) \|", plan, flags=re.MULTILINE)
    if not rows:
        raise ValueError("master plan produced no capability corpus")
    return tuple(title.strip() for number, title in rows if int(number) <= current)


def rollup_issues(root: Path, text: str) -> list[str]:
    titles = owned_capability_titles(root)
    normalized = re.sub(r"\s+", " ", text.replace("**", "")).casefold()
    issues = []
    if "checkpoints/latest.md" not in normalized:
        issues.append("live acceptance is not delegated to the canonical checkpoint")
    if re.search(r"current gate\s*:\s*`?gate\s*\d+", normalized):
        issues.append("live current Gate is frozen in a capability rollup")
    for title in titles:
        if title.casefold() not in normalized:
            issues.append("owned capability omitted: " + title)
        for sentence in re.split(r"[.\n]", text):
            folded = re.sub(r"\s+", " ", sentence.replace("**", "")).casefold()
            if title.casefold() in folded and any(
                marker in folded
                for marker in (
                    "what does not",
                    "belongs to later",
                    "belong to later",
                    "not implemented",
                    "no runtime",
                )
            ):
                issues.append("owned capability denied: " + title)
    return issues


class Gate7RollupTests(unittest.TestCase):
    def test_current_rollups_do_not_deny_the_owned_capabilities(self):
        documents = {
            "README.md": ("## Current boundary", "## Running it"),
            "docs/ARCHITECTURE.md": ("## Current state", "## Control plane"),
        }
        for path, (start, end) in documents.items():
            with self.subTest(document=path):
                text = (ROOT / path).read_text(encoding="utf-8").split(start, 1)[1].split(end, 1)[0]
                self.assertEqual(rollup_issues(ROOT, text), [])

    def test_rollup_guard_has_positive_and_each_missing_denied_stale_mutation(self):
        titles = owned_capability_titles(ROOT)
        valid = "Current capabilities: " + "; ".join(titles) + ".\ndocs/checkpoints/LATEST.md\n"
        self.assertEqual(rollup_issues(ROOT, valid), [])
        for title in titles:
            with self.subTest(capability=title):
                self.assertTrue(rollup_issues(ROOT, valid.replace(title, "omitted-capability")))
                self.assertTrue(
                    rollup_issues(
                        ROOT, valid + "\nWhat does not: " + title + " belongs to later Gates."
                    )
                )
        self.assertTrue(rollup_issues(ROOT, valid + "\nCurrent Gate: GATE 0"))
        self.assertTrue(
            rollup_issues(ROOT, valid.replace("docs/checkpoints/LATEST.md", "unbound-status"))
        )

    def test_original_published_readme_is_a_real_causal_negative_not_a_rewritten_fixture(self):
        checkpoint = ROOT / "docs/checkpoints/GATE-7-CP-0001"
        manifest = json.loads((checkpoint / "attempts/README-ROLLUP-0001.json").read_bytes())
        raw = (checkpoint / manifest["artifact"]).read_bytes()
        import hashlib

        self.assertEqual(hashlib.sha256(raw).hexdigest(), manifest["sha256"])
        self.assertEqual(len(raw), manifest["sizeBytes"])
        import subprocess

        published = subprocess.run(
            ["git", "show", manifest["sourceCommit"] + ":" + manifest["sourcePath"]],
            cwd=ROOT,
            capture_output=True,
            check=True,
        )
        self.assertEqual(raw, published.stdout)
        original = (
            raw.decode("utf-8").split("## Current boundary", 1)[1].split("## Running it", 1)[0]
        )
        issues = rollup_issues(ROOT, original)
        self.assertIn("owned capability denied: Experience Store", issues)
        self.assertIn("live current Gate is frozen in a capability rollup", issues)


class Gate7LintDenominatorTests(unittest.TestCase):
    def test_inherited_lint_guard_refuses_each_new_python_root_omission(self):
        import test_gate4_quality_engine as inherited

        source = (ROOT / "scripts/iacode/gates/lint.py").read_text(encoding="utf-8")
        assignment = next(
            node
            for node in ast.parse(source).body
            if isinstance(node, ast.Assign)
            and any(
                isinstance(target, ast.Name) and target.id == "PYTHON_ROOTS"
                for target in node.targets
            )
        )
        roots = ast.literal_eval(assignment.value)
        control = inherited.Gate4QualityCoverageTests(
            "test_mandatory_lint_covers_every_python_project_root"
        )
        control.test_mandatory_lint_covers_every_python_project_root()
        knowledge_roots = [value for value in roots if value.startswith("services/knowledge/")]
        self.assertTrue(knowledge_roots)
        # Removing only src or only tests still covers the project under the inherited rule;
        # remove the whole owning project to exercise its actual adverse denominator.
        narrowed = tuple(value for value in roots if value not in knowledge_roots)
        with patch.object(inherited.ast, "literal_eval", return_value=narrowed):
            with self.assertRaises(AssertionError):
                control.test_mandatory_lint_covers_every_python_project_root()
