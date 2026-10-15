from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))

from delivery_assurance import collect_test_ids
from derive_counts import count_pytest_cases
from ledger_common import LedgerError
from policies import counted_test_suites, test_suite_source_files


class TestSuiteInputRepositoriesTests(unittest.TestCase):
    def test_policy_count_matches_collected_suite_not_live_input_projects(self) -> None:
        suite = next(s for s in counted_test_suites(ROOT) if s["id"] == "evaluator")
        self.assertEqual(count_pytest_cases(ROOT, suite["root"], suite=suite), 89)
        self.assertEqual(count_pytest_cases(ROOT, suite["root"]), 94)
        self.assertEqual(count_pytest_cases(ROOT, suite["root"] + "/fixtures"), 5)

    def test_only_declared_runner_exclusions_leave_both_count_and_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            directory = root / "suite"
            (directory / "fixtures").mkdir(parents=True)
            (directory / "test_real.py").write_text("def test_real(): pass\n")
            (directory / "fixtures/test_input.py").write_text("def test_input(): pass\n")
            (directory / "conftest.py").write_text('collect_ignore_glob = ["fixtures/**"]\n')
            suite = {"id": "proof", "root": "suite", "framework": "python-pytest",
                     "counted": True, "inputRepositories": [{"root": "fixtures",
                     "collectionIgnoreGlob": "fixtures/**", "notCountedReason": "live input"}]}
            policy = root / ".iacode/policies"
            policy.mkdir(parents=True)
            (policy / "test-suites.json").write_text(json.dumps({"suites": [suite]}))
            self.assertEqual(count_pytest_cases(root, "suite", suite=suite), 1)
            self.assertIn("test_real", collect_test_ids(root))
            self.assertNotIn("test_input", collect_test_ids(root))
            suite["inputRepositories"] = []
            with self.assertRaisesRegex(LedgerError, "disagree"):
                test_suite_source_files(root, suite)
            suite["inputRepositories"] = [{"root": "..", "collectionIgnoreGlob": "../**",
                                           "notCountedReason": "not authorized"}]
            with self.assertRaises(LedgerError):
                test_suite_source_files(root, suite)

    def test_a_registry_exclusion_cannot_remove_a_runner_collected_test(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "suite/fixtures").mkdir(parents=True)
            suite = {"root": "suite", "framework": "python-pytest",
                     "inputRepositories": [{"root": "fixtures",
                     "collectionIgnoreGlob": "fixtures/**", "notCountedReason": "input"}]}
            with self.assertRaisesRegex(LedgerError, "disagree"):
                test_suite_source_files(root, suite)
