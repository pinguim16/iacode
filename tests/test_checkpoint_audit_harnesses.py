from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HARNESS = (
    ROOT
    / "docs"
    / "checkpoints"
    / "GATE-4-CP-0009"
    / "audit-harness"
    / "complete_requirements.py"
)


def load_harness():
    spec = importlib.util.spec_from_file_location("cp0009_complete_requirements", HARNESS)
    if spec is None or spec.loader is None:
        raise AssertionError(f"cannot load {HARNESS}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CorrectiveRequirementDenominatorTests(unittest.TestCase):
    def test_corrective_partition_is_derived_from_the_current_reference_set(self) -> None:
        harness = load_harness()
        total = 227
        expected = harness.expected_breakdown(total)
        self.assertEqual(expected, (total - len(harness.CORRECTIVE_REFS) - 20, 10, 20))

        harness.CORRECTIVE_REFS.add("lesson:LSN-FUTURE")
        self.assertEqual(harness.expected_breakdown(total + 1), (197, 11, 20))


if __name__ == "__main__":
    unittest.main()
