"""Real discovery must count the inspected suite without replacing its caller's imports."""

from __future__ import annotations

import importlib
import sys
import tempfile
import unittest
import uuid
from pathlib import Path
from typing import override

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts/development-ledger"))

from derive_counts import count_unittest_cases
from ledger_common import LedgerError

ROOT = Path(__file__).resolve().parents[1]


class M2DiscoveryIsolationTests(unittest.TestCase):
    @override
    def setUp(self):
        self.owner = tempfile.TemporaryDirectory(prefix="iacode-discovery-control-")
        self.addCleanup(self.owner.cleanup)
        self.root = Path(self.owner.name)
        self.saved_path = list(sys.path)
        self.saved_modules = dict(sys.modules)
        self.addCleanup(self.restore_imports)
        self.name = "test_iacode_discovery_" + uuid.uuid4().hex

    def restore_imports(self):
        sys.path[:] = self.saved_path
        for name in set(sys.modules) - self.saved_modules.keys():
            del sys.modules[name]
        sys.modules.update(self.saved_modules)

    def suite(self, name, body):
        root = self.root / name
        directory = root / "tests"
        directory.mkdir(parents=True)
        (directory / (self.name + ".py")).write_text("import unittest\n" + body, encoding="utf-8")
        return root

    def test_actual_valid_null_counts_inherited_and_skipped_cases_without_running_them(self):
        root = self.suite(
            "null",
            """
class Parent(unittest.TestCase):
    def test_inherited(self):
        raise AssertionError('discovery must not execute a case')
class Child(Parent):
    @unittest.skip('still a discovered physical case')
    def test_own(self):
        raise AssertionError('discovery must not execute a case')
""",
        )
        self.assertEqual(count_unittest_cases(root, "tests"), 3)

    def test_actual_inspected_import_cannot_replace_the_late_current_consumer(self):
        name = "_iacode_discovery_consumer_" + uuid.uuid4().hex
        current = self.root / "current"
        current.mkdir()
        (current / (name + ".py")).write_text("ORIGIN = 'current'\n", encoding="utf-8")
        foreign = self.root / "foreign"
        foreign.mkdir()
        (foreign / (name + ".py")).write_text("ORIGIN = 'inspected'\n", encoding="utf-8")
        root = self.suite(
            "adverse",
            f"""
import sys
sys.path.insert(0, {str(foreign)!r})
import {name}
assert {name}.ORIGIN == 'inspected'
class Case(unittest.TestCase):
    def test_case(self):
        raise AssertionError('not executed')
""",
        )
        sys.path.insert(0, str(current))
        before = list(sys.path)
        self.assertEqual(count_unittest_cases(root, "tests"), 1)
        self.assertEqual(sys.path, before)
        self.assertNotIn(name, sys.modules)
        self.assertEqual(importlib.import_module(name).ORIGIN, "current")

    def test_same_named_preloaded_test_is_restored_but_never_counted_for_another_root(self):
        first = self.suite(
            "first", ("class Case(unittest.TestCase):\n    def test_one(self): pass\n")
        )
        second = self.suite(
            "second",
            """
class Case(unittest.TestCase):
    def test_one(self): pass
    def test_two(self): pass
""",
        )
        sys.path.insert(0, str(first / "tests"))
        original = importlib.import_module(self.name)
        self.assertEqual(count_unittest_cases(second, "tests"), 2)
        self.assertIs(sys.modules[self.name], original)

    def test_repeated_real_roots_keep_their_own_exact_discovery_counts(self):
        first = self.suite("one", "class Case(unittest.TestCase):\n    def test_one(self): pass\n")
        second = self.suite(
            "two",
            """
class Case(unittest.TestCase):
    def test_one(self): pass
    def test_two(self): pass
""",
        )
        self.assertEqual(count_unittest_cases(first, "tests"), 1)
        self.assertEqual(count_unittest_cases(second, "tests"), 2)
        self.assertEqual(count_unittest_cases(first, "tests"), 1)

    def test_a_real_load_tests_error_is_refused_instead_of_counted_as_one_case(self):
        root = self.suite(
            "error",
            """
import sys
sys.path.insert(0, 'iacode-owned-discovery-error-marker')
def load_tests(loader, tests, pattern):
    raise RuntimeError('intentional owned collection failure')
""",
        )
        before = list(sys.path)
        with self.assertRaises(LedgerError):
            count_unittest_cases(root, "tests")
        self.assertEqual(sys.path, before)
        self.assertNotIn(self.name, sys.modules)

    def test_an_actual_uncaught_import_failure_also_restores_caller_state(self):
        root = self.suite(
            "interrupt",
            """
import sys
sys.path.insert(0, 'iacode-owned-discovery-interrupt-marker')
__file__ = __file__.replace('tests', 'intentionally-wrong-owned-origin')
""",
        )
        before = list(sys.path)
        with self.assertRaises(ImportError):
            count_unittest_cases(root, "tests")
        self.assertEqual(sys.path, before)

    def test_the_shared_default_loader_is_not_mutated_by_counting(self):
        root = self.suite(
            "loader", ("class Case(unittest.TestCase):\n    def test_one(self): pass\n")
        )
        loader = unittest.defaultTestLoader
        before = loader.testNamePatterns
        try:
            loader.testNamePatterns = ["*intentionally_not_a_current_case*"]
            self.assertEqual(count_unittest_cases(root, "tests"), 1)
            self.assertEqual(loader.testNamePatterns, ["*intentionally_not_a_current_case*"])
        finally:
            loader.testNamePatterns = before

    def test_missing_suite_remains_zero_without_changing_import_state(self):
        before = list(sys.path)
        self.assertEqual(count_unittest_cases(self.root, "absent"), 0)
        self.assertEqual(sys.path, before)


if __name__ == "__main__":
    unittest.main()
