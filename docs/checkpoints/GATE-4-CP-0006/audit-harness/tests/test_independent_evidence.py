#!/usr/bin/env python3
"""Executable consistency checks for the Gate 4 independent audit evidence."""

from __future__ import annotations

import json
import unittest
from pathlib import Path


CHECKPOINT = Path(__file__).resolve().parents[2]


def load(name: str) -> dict:
    return json.loads((CHECKPOINT / name).read_text(encoding="utf-8"))


class IndependentEvidenceTests(unittest.TestCase):
    def test_single_published_verifier_passed_the_exact_denominator(self) -> None:
        publication = load("PUBLISHED-CLEAN-CLONE-REPORT.json")
        verification = load("VERIFICATION-REPORT.json")
        self.assertEqual(publication["invocationCount"], 1)
        self.assertEqual(publication["retryCount"], 0)
        self.assertFalse(publication["verifierRerun"])
        self.assertEqual(publication["result"], "PASS")
        self.assertEqual(publication["stagesPassed"], 42)
        self.assertEqual(publication["stagesFailed"], 0)
        self.assertEqual(len(verification["stages"]), 42)
        self.assertTrue(all(stage["result"] == "PASS" for stage in verification["stages"]))

    def test_independent_red_team_defended_the_exact_a_to_t_set(self) -> None:
        report = load("GATE-4-INDEPENDENT-RED-TEAM.json")
        self.assertEqual(report["result"], "RED_TEAM_PASS")
        self.assertEqual(report["defended"], 20)
        self.assertEqual(report["escaped"], 0)
        self.assertEqual(
            [attack["attackId"] for attack in report["attacks"]],
            list("ABCDEFGHIJKLMNOPQRST"),
        )

    def test_g4x7_failed_closed_before_persistence(self) -> None:
        report = load("G4-X7-INDEPENDENT-PROBE.json")
        marker = report["canonicalMarker"]
        self.assertEqual(report["result"], "PASS")
        self.assertEqual(marker["resultStatus"], "ERROR")
        self.assertEqual(marker["verdict"], "FAIL")
        self.assertEqual(marker["objectCount"], 0)
        self.assertEqual(marker["metadataCount"], 0)
        self.assertTrue(marker["scanPrecededDurableOperation"])


if __name__ == "__main__":
    unittest.main()
