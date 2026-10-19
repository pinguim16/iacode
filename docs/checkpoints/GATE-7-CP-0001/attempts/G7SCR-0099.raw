"""Unit boundaries for truthful quality observers; never live functional acceptance."""

from __future__ import annotations

import ast
import io
import json
import runpy
import subprocess
import tarfile
import tempfile
import unittest
from contextlib import contextmanager, redirect_stdout
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]


class Gate7QualityObservationTests(unittest.TestCase):
    def namespace(self):
        return runpy.run_path(str(ROOT / "scripts/iacode/scenarios/quality_engine_e2e.py"))

    @contextmanager
    def scenario(self, wait, detail):
        with tempfile.TemporaryDirectory(prefix="iacode-g7-quality-observer-") as raw:
            root = Path(raw)
            if root.resolve().parent != Path(tempfile.gettempdir()).resolve():
                raise ValueError("unexpected owned quality unit fixture")
            (root / "observer-premise.txt").write_bytes(b"actual owned archive premise\n")
            (root / ".gitattributes").write_bytes(b"* -text\n")
            for arguments in (
                ["init", "--quiet", "--initial-branch=main"],
                ["add", ".gitattributes", "observer-premise.txt"],
                [
                    "-c",
                    "user.name=IACode fixture",
                    "-c",
                    "user.email=fixture@example.invalid",
                    "-c",
                    "commit.gpgsign=false",
                    "commit",
                    "-qm",
                    "fixture",
                ],
            ):
                subprocess.run(["git", *arguments], cwd=root, check=True, capture_output=True)
            actual = subprocess.run(
                ["git", "archive", "--format=tar", "HEAD"],
                cwd=root,
                check=True,
                capture_output=True,
            ).stdout
            with tarfile.open(fileobj=io.BytesIO(actual), mode="r:") as archive:
                self.assertEqual(archive.getnames(), [".gitattributes", "observer-premise.txt"])
                member = archive.extractfile("observer-premise.txt")
                self.assertIsNotNone(member)
                self.assertEqual(member.read(), b"actual owned archive premise\n")
            scenario = self.namespace()["scenario_iacode"]
            request = mock.Mock(return_value=detail)
            start = mock.Mock(
                return_value={
                    "runId": "owned-unit-run",
                    "planId": "a" * 64,
                    "profile": "python+node+typescript+angular",
                }
            )
            with mock.patch.dict(
                scenario.__globals__,
                {
                    "REPOSITORY_ROOT": root,
                    "snapshot": mock.Mock(return_value={}),
                    "start": start,
                    "wait_terminal": wait,
                    "request": request,
                    "log": mock.Mock(),
                },
            ):
                yield scenario, request, start
        self.assertFalse(root.exists())

    def detail(self, state="RUNNING"):
        return {
            "run": {"state": state, "verdict": None, "untrusted": "private-unit-marker"},
            "checks": [{"applicable": True}, {"applicable": False}],
            "results": [{"status": "PASSED", "summary": "private-unit-marker"}],
            "privateBody": "private-unit-marker",
        }

    def test_large_repository_observer_covers_unchanged_canonical_run_deadline(self):
        namespace = self.namespace()
        policy = json.loads((ROOT / ".iacode/policies/quality-policy.json").read_bytes())
        budget = namespace["IACODE_WAIT_SECONDS"]
        self.assertEqual(budget, policy["defaults"]["maxRunSeconds"] + 60.0)
        self.assertGreaterEqual(budget, 2 * namespace["WAIT_SECONDS"])
        self.assertEqual(namespace["DURABLE_WAIT_SECONDS"], 900.0)

    def test_iacode_wait_timeout_is_red_and_captures_only_closed_runtime_facts(self):
        wait = mock.Mock(side_effect=self.namespace()["StackError"]("private-unit-marker"))
        with self.scenario(wait, self.detail()) as (scenario, request, start):
            report = scenario()
        self.assertEqual(report["result"], "FAIL")
        self.assertEqual(start.call_count, 1)
        request.assert_called_once_with("GET", "/owned-unit-run")
        observation = report["artifacts"][-1]["observation"]
        self.assertEqual(
            observation,
            {
                "observationStatus": "AVAILABLE",
                "state": "RUNNING",
                "declaredChecks": 2,
                "applicableChecks": 1,
                "completedResults": 1,
                "resultCounts": {"PASSED": 1},
            },
        )
        self.assertNotIn("private-unit-marker", json.dumps(report))

    def test_late_successful_diagnostic_never_promotes_the_expired_wait(self):
        wait = mock.Mock(side_effect=self.namespace()["StackError"]("private-unit-marker"))
        detail = self.detail("SUCCEEDED")
        detail["run"]["verdict"] = "PASS"
        with self.scenario(wait, detail) as (scenario, _request, _start):
            report = scenario()
        self.assertEqual(report["result"], "FAIL")
        self.assertEqual(report["artifacts"][-1]["observation"]["state"], "SUCCEEDED")

    def test_actual_success_keeps_the_original_assertions_and_makes_no_diagnostic_call(self):
        wait = mock.Mock(return_value={"run": {"state": "SUCCEEDED", "verdict": "PASS"}})
        with self.scenario(wait, self.detail()) as (scenario, request, start):
            report = scenario()
        self.assertEqual(report["result"], "PASS")
        request.assert_not_called()
        self.assertEqual(start.call_count, 1)
        self.assertTrue(all(row["result"] == "PASS" for row in report["steps"]))

    def test_owned_archive_premise_is_populated_before_observer_target(self):
        wait = mock.Mock()
        with self.scenario(wait, self.detail()) as (scenario, request, start):
            root = scenario.__globals__["REPOSITORY_ROOT"]
            self.assertEqual(
                (root / "observer-premise.txt").read_bytes(), b"actual owned archive premise\n"
            )
            wait.assert_not_called()
            request.assert_not_called()
            start.assert_not_called()

    def test_timeout_projection_refuses_malformed_private_and_excessive_metadata(self):
        projection = self.namespace()["quality_timeout_observation"]
        malformed = [
            None,
            [],
            {},
            {"run": []},
            {**self.detail(), "run": {"state": "private-unit-marker"}},
            {**self.detail(), "checks": "private-unit-marker"},
            {**self.detail(), "results": [{"status": "private-unit-marker"}]},
            {**self.detail(), "checks": [{"applicable": "private-unit-marker"}]},
            {**self.detail(), "results": self.detail()["results"] * 257},
        ]
        for detail in malformed:
            with (
                self.subTest(kind=type(detail).__name__),
                mock.patch.dict(
                    projection.__globals__, {"request": mock.Mock(return_value=detail)}
                ),
            ):
                observed = projection("owned-unit-run")
                self.assertEqual(observed, {"observationStatus": "MALFORMED", "state": "UNKNOWN"})
                self.assertNotIn("private-unit-marker", json.dumps(observed))
        with mock.patch.dict(
            projection.__globals__,
            {
                "request": mock.Mock(
                    side_effect=self.namespace()["StackError"]("private-unit-marker")
                ),
            },
        ):
            observed = projection("owned-unit-run")
        self.assertEqual(observed, {"observationStatus": "UNAVAILABLE", "state": "UNKNOWN"})
        self.assertNotIn("private-unit-marker", json.dumps(observed))

    def test_timeout_projection_follows_all_canonical_closed_states_and_result_statuses(self):
        source = ROOT / "packages/contracts/src/iacode_contracts/quality.py"
        wanted = {"QUALITY_RUN_STATES", "QUALITY_RESULT_STATUSES"}
        values = {
            target.id: ast.literal_eval(node.value)
            for node in ast.parse(source.read_text(encoding="utf-8")).body
            if isinstance(node, ast.Assign)
            for target in node.targets
            if isinstance(target, ast.Name) and target.id in wanted
        }
        self.assertEqual(set(values), wanted)
        projection = self.namespace()["quality_timeout_observation"]
        for state in values["QUALITY_RUN_STATES"]:
            for status in values["QUALITY_RESULT_STATUSES"]:
                detail = self.detail(state)
                detail["results"] = [{"status": status, "summary": "private-unit-marker"}]
                with (
                    self.subTest(state=state, status=status),
                    mock.patch.dict(
                        projection.__globals__, {"request": mock.Mock(return_value=detail)}
                    ),
                ):
                    observed = projection("owned-unit-run")
                self.assertEqual(observed["observationStatus"], "AVAILABLE")
                self.assertEqual(observed["state"], state)
                self.assertEqual(observed["resultCounts"], {status: 1})
                self.assertNotIn("private-unit-marker", json.dumps(observed))

    def test_iacode_timeout_remains_red_if_its_diagnostic_dependency_is_unavailable(self):
        wait = mock.Mock(side_effect=self.namespace()["StackError"]("private-unit-marker"))
        with self.scenario(wait, self.detail()) as (scenario, request, _start):
            request.side_effect = self.namespace()["StackError"]("private-unit-marker")
            report = scenario()
        self.assertEqual(report["result"], "FAIL")
        self.assertEqual(
            report["artifacts"][-1]["observation"],
            {
                "observationStatus": "UNAVAILABLE",
                "state": "UNKNOWN",
            },
        )
        self.assertNotIn("private-unit-marker", json.dumps(report))

    def test_actual_iacode_entrypoint_writes_a_red_timeout_report_before_owned_cleanup(self):
        wait = mock.Mock(side_effect=self.namespace()["StackError"]("private-unit-marker"))
        with self.scenario(wait, self.detail()) as (scenario, _request, _start):
            path = scenario.__globals__["REPOSITORY_ROOT"] / "observer-failure-report.json"
            main = scenario.__globals__["main"]
            captured = io.StringIO()
            with (
                mock.patch.dict(
                    main.__globals__,
                    {
                        "prepare": mock.Mock(),
                        "SCENARIOS": {"iacode": scenario},
                    },
                ),
                mock.patch(
                    "sys.argv",
                    [
                        "quality_engine_e2e.py",
                        "--scenario",
                        "iacode",
                        "--skip-build",
                        "--report",
                        str(path),
                    ],
                ),
                redirect_stdout(captured),
            ):
                code = main()
            self.assertEqual(code, 1)
            self.assertTrue(path.is_file())
            document = json.loads(path.read_bytes())
            self.assertEqual(document["result"], "FAIL")
            self.assertEqual(len(document["scenarios"]), 1)
            self.assertEqual(document["scenarios"][0]["result"], "FAIL")
            self.assertNotIn("private-unit-marker", json.dumps(document) + captured.getvalue())
        self.assertFalse(path.exists())


if __name__ == "__main__":
    unittest.main()
