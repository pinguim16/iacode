"""Contracts, project profiles, policy, planning, and fail-closed verdict derivation."""

from __future__ import annotations

import ast
import asyncio
import json
import uuid
from datetime import UTC, datetime
from pathlib import Path

import pytest
from iacode_contracts.quality import (
    CreateQualityRunRequest,
    QualityCheck,
    QualityEvidence,
    QualityFinding,
    QualityPlan,
    QualityResult,
)
from iacode_evaluator.engine import execute_plan
from iacode_evaluator.errors import QualityError
from iacode_evaluator.executor import quality_tool_request_id, sandbox_request
from iacode_evaluator.findings import deduplicate, finding_fingerprint
from iacode_evaluator.planner import build_plan
from iacode_evaluator.policy import load_policy
from iacode_evaluator.projects import MAX_MANIFEST_BYTES, detect_project, inventory_project
from iacode_evaluator.reproduce import compare_reproduction
from iacode_evaluator.runners import RUNNERS, get_runner
from iacode_evaluator.verdict import derive_verdict
from pydantic import ValidationError

ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / ".iacode" / "policies").is_dir()
)
POLICY = ROOT / ".iacode" / "policies" / "quality-policy.json"
NOW = datetime(2026, 1, 2, 3, 4, 5, tzinfo=UTC)
SHA = "a" * 64


def python_plan() -> QualityPlan:
    registry = load_policy(POLICY)
    project = detect_project({"pyproject.toml": "[project]\nname='fixture'\n"})
    return build_plan(
        snapshot_id="snapshot-1",
        snapshot_digest=SHA,
        project=project,
        registry=registry,
        created_at=NOW,
    )


def evidence(index: int, kind: str = "report") -> QualityEvidence:
    digest = f"{index:064x}"
    return QualityEvidence(
        evidenceId=f"evidence-{index}",
        kind=kind,
        artifactId=f"artifact-{index}",
        digest=digest,
        sizeBytes=12,
        mediaType="application/json",
        producer="evaluator",
        sourceDigests=(SHA,),
        createdAt=NOW,
    )


def passing_results(plan: QualityPlan, run_id: str = "run-1") -> tuple[QualityResult, ...]:
    results = []
    for index, check in enumerate(plan.checks, start=1):
        item = evidence(index, check.requiredEvidenceKinds[0])
        results.append(
            QualityResult(
                resultId=f"result-{index}",
                runId=run_id,
                checkId=check.checkId,
                status="PASSED",
                exitCode=0,
                durationMs=10,
                summary="passed",
                sandboxId="sandbox-1",
                evidence=(item,),
                finishedAt=NOW,
            )
        )
    return tuple(results)


class QualityContractTests:
    def test_unknown_fields_and_unsupported_versions_are_refused(self) -> None:
        with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
            CreateQualityRunRequest(
                snapshotId="snapshot-1",
                snapshotDigest=SHA,
                policyId="default",
                idempotencyKey="key",
                surprise=True,
            )
        with pytest.raises(ValidationError, match=r"1\.0\.0"):
            CreateQualityRunRequest(
                contractVersion="2.0.0",
                snapshotId="snapshot-1",
                snapshotDigest=SHA,
                policyId="default",
                idempotencyKey="key",
            )

    def test_a_request_cannot_smuggle_execution_or_a_verdict(self) -> None:
        for field in (
            "command",
            "runner",
            "image",
            "mount",
            "network",
            "limits",
            "evidence",
            "result",
            "verdict",
        ):
            with pytest.raises(ValidationError, match="protected fields"):
                CreateQualityRunRequest(
                    snapshotId="snapshot-1",
                    snapshotDigest=SHA,
                    policyId="default",
                    idempotencyKey=f"key-{field}",
                    configuration={field: "owned-by-caller"},
                )

    def test_result_states_cannot_masquerade_as_success(self) -> None:
        with pytest.raises(ValidationError, match="exit code zero"):
            QualityResult(
                resultId="result-1",
                runId="run-1",
                checkId="check-1",
                status="PASSED",
                exitCode=1,
                durationMs=1,
                summary="not really",
                finishedAt=NOW,
            )
        with pytest.raises(ValidationError, match="cannot invent"):
            QualityResult(
                resultId="result-1",
                runId="run-1",
                checkId="check-1",
                status="DENIED",
                exitCode=1,
                durationMs=1,
                summary="denied",
                finishedAt=NOW,
            )
        with pytest.raises(ValidationError, match="timedOut=true"):
            QualityResult(
                resultId="result-1",
                runId="run-1",
                checkId="check-1",
                status="TIMED_OUT",
                durationMs=1,
                summary="timeout",
                finishedAt=NOW,
            )

    def test_contracts_round_trip_without_losing_the_frozen_plan(self) -> None:
        plan = python_plan()
        self.assert_equal(plan, QualityPlan.model_validate_json(plan.model_dump_json()))

    @staticmethod
    def assert_equal(left: object, right: object) -> None:
        assert left == right

    def test_rights_default_to_denial(self) -> None:
        item = evidence(1)
        assert item.trainingAllowed is False
        assert item.ragAllowed is False
        assert item.distillationAllowed is False


class ProjectProfileTests:
    @pytest.mark.parametrize(
        ("files", "stacks"),
        (
            ({"pyproject.toml": ""}, ("python",)),
            ({"package.json": "{}"}, ("node",)),
            ({"package.json": "{}", "tsconfig.json": "{}"}, ("node", "typescript")),
            (
                {"package.json": "{}", "tsconfig.json": "{}", "angular.json": "{}"},
                ("node", "typescript", "angular"),
            ),
            ({"pom.xml": "<project/>"}, ("maven",)),
            ({"build.gradle": "plugins {}"}, ("gradle",)),
        ),
    )
    def test_every_initial_stack_is_detected_without_execution(self, files, stacks) -> None:
        profile = detect_project(files)
        assert profile.stacks == stacks
        assert profile.confidence == "HIGH"

    def test_unknown_and_ambiguous_projects_are_explicit(self) -> None:
        unknown = detect_project({"README.md": "not a manifest"})
        assert unknown.confidence == "UNSUPPORTED"
        assert unknown.stacks == ()
        ambiguous = detect_project({"pom.xml": "", "build.gradle": ""})
        assert ambiguous.confidence == "AMBIGUOUS"
        assert ambiguous.ambiguities

    def test_paths_and_manifest_sizes_are_bounded(self) -> None:
        with pytest.raises(QualityError, match="not relative"):
            detect_project({"../pyproject.toml": ""})
        with pytest.raises(QualityError, match="exceeds manifest limit"):
            detect_project({"pyproject.toml": b"x" * (MAX_MANIFEST_BYTES + 1)})
        profile = detect_project({"node_modules/package.json": "{}", "pyproject.toml": ""})
        assert profile.stacks == ("python",)

    def test_inventory_refuses_a_manifest_symlink(self, tmp_path: Path) -> None:
        target = tmp_path / "actual.toml"
        target.write_text("[project]\n", encoding="utf-8")
        link = tmp_path / "pyproject.toml"
        try:
            link.symlink_to(target)
        except OSError:
            pytest.skip("this platform did not permit creating the test symlink")
        with pytest.raises(QualityError, match="symlink"):
            inventory_project(tmp_path)


class QualityPolicyTests:
    def test_the_canonical_policy_loads_every_initial_profile(self) -> None:
        registry = load_policy(POLICY)
        assert set(registry.profiles) == {
            "python",
            "node",
            "node+typescript",
            "node+typescript+angular",
            "maven",
            "gradle",
        }
        assert all(
            get_runner(identifier)
            for profile in registry.profiles.values()
            for identifier in profile.runners
        )

    def test_an_unknown_key_and_runner_are_refused(self, tmp_path: Path) -> None:
        document = json.loads(POLICY.read_text(encoding="utf-8"))
        document["escape"] = True
        path = tmp_path / "unknown-key.json"
        path.write_text(json.dumps(document), encoding="utf-8")
        with pytest.raises(QualityError, match="unknown keys"):
            load_policy(path)
        document.pop("escape")
        document["profiles"]["python"]["runners"].append("shell.anything")
        path.write_text(json.dumps(document), encoding="utf-8")
        with pytest.raises(QualityError, match="unknown quality runner"):
            load_policy(path)

    def test_configuration_can_only_add_declared_checks_or_lower_a_limit(self) -> None:
        registry = load_policy(POLICY)
        profile = registry.profile("python")
        with pytest.raises(QualityError, match="outside the profile"):
            registry.contract(profile, {"additionalRunners": ["node.integration"]})
        with pytest.raises(QualityError, match="cannot be raised"):
            registry.contract(profile, {"timeoutSeconds": registry.max_check_seconds + 1})
        lowered = registry.contract(profile, {"timeoutSeconds": 12})
        assert lowered.maxCheckSeconds == 12
        coverage = registry.contract(
            profile, {"additionalRunners": ["python.coverage"], "coverageThreshold": 85}
        )
        assert coverage.coverageThreshold == 85
        assert "coverage" in coverage.mandatoryCheckKinds

    def test_configured_coverage_and_migration_become_mandatory_checks(self) -> None:
        registry = load_policy(POLICY)
        project = detect_project({"pyproject.toml": ""})
        plan = build_plan(
            snapshot_id="snapshot-1",
            snapshot_digest=SHA,
            project=project,
            registry=registry,
            configuration={
                "additionalRunners": ["python.coverage", "python.migration"],
                "coverageThreshold": 80,
            },
            created_at=NOW,
        )
        assert {"coverage", "migration"} <= {check.kind for check in plan.checks}
        assert all(check.mandatory and check.applicable for check in plan.checks)

    def test_every_policy_runner_is_closed_and_policy_owned(self) -> None:
        assert len(RUNNERS) == len(set(RUNNERS))
        assert all(
            runner.command and all(part for part in runner.command) for runner in RUNNERS.values()
        )
        with pytest.raises(QualityError, match="unknown quality runner"):
            get_runner("a project supplied this")

    def test_the_registry_supports_every_required_check_kind(self) -> None:
        assert {
            "build",
            "unit",
            "integration",
            "lint",
            "static",
            "dependency-security",
            "secret",
            "coverage",
            "migration",
            "diff-integrity",
        } == {runner.kind for runner in RUNNERS.values()}


class QualityPlannerTests:
    def test_equal_inputs_make_the_same_plan_identity(self) -> None:
        registry = load_policy(POLICY)
        project = detect_project({"pyproject.toml": ""})
        first = build_plan(
            snapshot_id="snapshot-1",
            snapshot_digest=SHA,
            project=project,
            registry=registry,
            created_at=NOW,
        )
        second = build_plan(
            snapshot_id="snapshot-1",
            snapshot_digest=SHA,
            project=project,
            registry=registry,
            created_at=datetime(2027, 1, 1, tzinfo=UTC),
        )
        assert first.planId == second.planId
        changed = build_plan(
            snapshot_id="snapshot-1",
            snapshot_digest="b" * 64,
            project=project,
            registry=registry,
            created_at=NOW,
        )
        assert changed.planId != first.planId

    def test_plan_freezes_commands_policy_limits_and_reasons(self) -> None:
        plan = python_plan()
        assert plan.policy.digest == load_policy(POLICY).digest
        assert all(
            check.command
            and check.timeoutSeconds <= plan.policy.maxCheckSeconds
            and check.applicabilityReason
            for check in plan.checks
        )
        assert {check.kind for check in plan.checks} == set(plan.policy.mandatoryCheckKinds)

    def test_duplicate_unknown_and_cyclic_dependencies_are_refused(self) -> None:
        base = python_plan().checks[0]
        with pytest.raises(ValidationError, match="duplicate"):
            QualityPlan(
                planId=SHA,
                snapshotId="snapshot-1",
                snapshotDigest=SHA,
                projectProfile="python",
                projectProfileDigest=SHA,
                policy=python_plan().policy,
                checks=(base, base),
                createdAt=NOW,
            )
        unknown = base.model_copy(update={"dependsOn": ("missing",)})
        with pytest.raises(ValidationError, match="unknown check dependencies"):
            QualityPlan(
                planId=SHA,
                snapshotId="snapshot-1",
                snapshotDigest=SHA,
                projectProfile="python",
                projectProfileDigest=SHA,
                policy=python_plan().policy,
                checks=(unknown,),
                createdAt=NOW,
            )


class FalsePassRejectionTests:
    def test_complete_resolved_success_is_the_only_pass(self) -> None:
        plan = python_plan()
        results = passing_results(plan)
        resolved = {item.digest for result in results for item in result.evidence}
        verdict = derive_verdict(
            run_id="run-1",
            plan=plan,
            results=results,
            resolved_evidence_digests=resolved,
            derived_at=NOW,
        )
        assert verdict.verdict == "PASS"
        again = derive_verdict(
            run_id="run-1",
            plan=plan,
            results=results,
            resolved_evidence_digests=resolved,
            derived_at=NOW,
        )
        assert again.digest == verdict.digest

    @pytest.mark.parametrize(
        "mutation",
        (
            "missing-result",
            "failed-result",
            "unresolved-evidence",
            "duplicate-result",
            "wrong-run",
            "unexpected-result",
        ),
    )
    def test_each_false_pass_mutation_is_rejected(self, mutation: str) -> None:
        plan = python_plan()
        results = list(passing_results(plan))
        resolved = {item.digest for result in results for item in result.evidence}
        if mutation == "missing-result":
            results.pop()
        elif mutation == "failed-result":
            results[0] = results[0].model_copy(update={"status": "FAILED", "exitCode": 1})
        elif mutation == "unresolved-evidence":
            resolved.remove(results[0].evidence[0].digest)
        elif mutation == "duplicate-result":
            results.append(results[0].model_copy(update={"resultId": "duplicate"}))
        elif mutation == "wrong-run":
            results[0] = results[0].model_copy(update={"runId": "other-run"})
        elif mutation == "unexpected-result":
            results.append(
                results[0].model_copy(update={"resultId": "unexpected", "checkId": "not-planned"})
            )
        verdict = derive_verdict(
            run_id="run-1",
            plan=plan,
            results=tuple(results),
            resolved_evidence_digests=resolved,
            derived_at=NOW,
        )
        assert verdict.verdict == "FAIL"
        assert verdict.reasons

    def test_an_empty_applicable_set_is_not_a_vacuous_pass(self) -> None:
        plan = python_plan()
        check: QualityCheck = plan.checks[0].model_copy(
            update={
                "mandatory": False,
                "applicable": False,
                "applicabilityReason": "not applicable to this fixture",
            }
        )
        plan = plan.model_copy(update={"checks": (check,)})
        verdict = derive_verdict(
            run_id="run-1", plan=plan, results=(), resolved_evidence_digests=set(), derived_at=NOW
        )
        assert verdict.verdict == "FAIL"
        assert any("required check set is missing" in reason for reason in verdict.reasons)


class CoverageVerdictTests:
    @staticmethod
    def plan() -> QualityPlan:
        base = python_plan()
        coverage = QualityCheck(
            checkId="q999-coverage",
            kind="coverage",
            runner="python.coverage",
            command=("python", "-m", "coverage", "report"),
            applicabilityReason="coverage threshold is configured",
            timeoutSeconds=600,
            requiredEvidenceKinds=("coverage",),
        )
        policy = base.policy.model_copy(
            update={
                "coverageThreshold": 80.0,
                "mandatoryCheckKinds": (*base.policy.mandatoryCheckKinds, "coverage"),
            }
        )
        return base.model_copy(update={"policy": policy, "checks": (*base.checks, coverage)})

    @pytest.mark.parametrize(
        ("coverage", "expected"),
        ((80.0, "PASS"), (79.99, "FAIL"), (None, "FAIL")),
    )
    def test_configured_coverage_is_measured_not_inferred(
        self, coverage: float | None, expected: str
    ) -> None:
        plan = self.plan()
        results = list(passing_results(plan))
        results[-1] = results[-1].model_copy(update={"coveragePercent": coverage})
        resolved = {item.digest for result in results for item in result.evidence}
        verdict = derive_verdict(
            run_id="run-1",
            plan=plan,
            results=tuple(results),
            resolved_evidence_digests=resolved,
            derived_at=NOW,
        )
        assert verdict.verdict == expected

    def test_a_threshold_without_a_coverage_check_fails_closed(self) -> None:
        base = python_plan()
        plan = base.model_copy(
            update={"policy": base.policy.model_copy(update={"coverageThreshold": 80.0})}
        )
        results = passing_results(plan)
        resolved = {item.digest for result in results for item in result.evidence}
        verdict = derive_verdict(
            run_id="run-1",
            plan=plan,
            results=results,
            resolved_evidence_digests=resolved,
            derived_at=NOW,
        )
        assert verdict.verdict == "FAIL"
        assert any("coverage check" in reason for reason in verdict.reasons)


class QualityExecutionBoundaryTests:
    def test_quality_tool_identity_is_a_stable_uuid(self) -> None:
        first = quality_tool_request_id("run-1", "q001-build")
        assert uuid.UUID(first)
        assert first == quality_tool_request_id("run-1", "q001-build")
        assert first != quality_tool_request_id("run-1", "q002-unit")

    def test_every_stack_maps_to_a_policy_owned_sandbox_request(self) -> None:
        registry = load_policy(POLICY)
        fixtures = {
            "python": {"pyproject.toml": ""},
            "node": {"package.json": "{}"},
            "node+typescript": {"package.json": "{}", "tsconfig.json": "{}"},
            "node+typescript+angular": {
                "package.json": "{}",
                "tsconfig.json": "{}",
                "angular.json": "{}",
            },
            "maven": {"pom.xml": ""},
            "gradle": {"build.gradle": ""},
        }
        for name, files in fixtures.items():
            plan = build_plan(
                snapshot_id="snapshot-1",
                snapshot_digest=SHA,
                project=detect_project(files),
                registry=registry,
                created_at=NOW,
            )
            request = sandbox_request(
                run_id="run-1", tool_request_id="tool-1", plan=plan, check=plan.checks[0]
            )
            assert request["policy"] in {"quality-python", "quality-node", "quality-java"}
            assert request["workspace"] == {
                "kind": "snapshot",
                "artifactId": "snapshot-1",
                "checksum": SHA,
            }
            assert request["tool"] == "shell.exec"
            assert not ({"image", "mount", "network", "resources", "verdict"} & set(request))
            assert plan.projectProfile == name

    def test_no_evaluator_module_can_start_a_process(self) -> None:
        source_root = ROOT / "services" / "evaluator" / "src"
        if not source_root.is_dir():
            source_root = ROOT / "evaluator_source"
        files = list(source_root.rglob("*.py"))
        assert len(files) >= 10
        forbidden = {"subprocess", "multiprocessing", "docker"}
        offenders = []
        for path in files:
            tree = ast.parse(path.read_text(encoding="utf-8"))
            names = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    names.update(alias.name.split(".")[0] for alias in node.names)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    names.add(node.module.split(".")[0])
            if names & forbidden:
                offenders.append((path.name, sorted(names & forbidden)))
        assert offenders == []

    def test_one_failure_does_not_hide_independent_results(self) -> None:
        plan = python_plan()
        called: list[str] = []

        async def dispatch(run_id, _plan, check):
            called.append(check.checkId)
            index = len(called)
            item = evidence(index, check.requiredEvidenceKinds[0])
            failed = index == 1
            return QualityResult(
                resultId=f"result-{index}",
                runId=run_id,
                checkId=check.checkId,
                status="FAILED" if failed else "PASSED",
                exitCode=1 if failed else 0,
                durationMs=1,
                summary="failed" if failed else "passed",
                sandboxId="sandbox-1",
                evidence=(item,),
                finishedAt=NOW,
            )

        async def resolve(_digest):
            return True

        results, verdict = asyncio.run(
            execute_plan(run_id="run-1", plan=plan, dispatcher=dispatch, evidence_resolver=resolve)
        )
        assert len(called) == len(plan.checks)
        assert len(results) == len(plan.checks)
        assert verdict.verdict == "FAIL"


class QualityFindingTests:
    def test_equal_findings_deduplicate_without_hiding_recurrence(self) -> None:
        fingerprint = finding_fingerprint(
            check_id="check-1", category="lint", message="same   issue", location="a.py:1"
        )
        first = QualityFinding(
            findingId="finding-1",
            checkId="check-1",
            severity="HIGH",
            category="lint",
            fingerprint=fingerprint,
            message="same issue",
            location="a.py:1",
            evidenceIds=("evidence-1",),
        )
        second = first.model_copy(update={"findingId": "finding-2", "evidenceIds": ("evidence-2",)})
        result = deduplicate((first, second))
        assert len(result) == 1
        assert result[0].recurrenceCount == 2
        assert result[0].evidenceIds == ("evidence-1", "evidence-2")


class QualityReproductionTests:
    def test_a_new_run_compares_stable_outcomes_without_rewriting_identity(self) -> None:
        plan = python_plan()
        original = passing_results(plan)
        reproduced = tuple(
            item.model_copy(
                update={
                    "resultId": f"reproduced-{index}",
                    "runId": "run-2",
                    "durationMs": item.durationMs + 100,
                    "sandboxId": "another-sandbox",
                }
            )
            for index, item in enumerate(original, start=1)
        )
        comparison = compare_reproduction(
            original_run_id="run-1",
            reproduced_run_id="run-2",
            plan=plan,
            original_results=original,
            reproduced_results=reproduced,
        )
        assert comparison.matches
        assert comparison.original_result_digests == comparison.reproduced_result_digests
        assert comparison.original_evidence_digests == comparison.reproduced_evidence_digests

    def test_a_changed_outcome_is_a_reproduction_mismatch(self) -> None:
        plan = python_plan()
        original = passing_results(plan)
        reproduced = tuple(
            item.model_copy(update={"resultId": f"copy-{index}", "runId": "run-2"})
            for index, item in enumerate(original, start=1)
        )
        reproduced = (
            reproduced[0].model_copy(update={"status": "FAILED", "exitCode": 1}),
            *reproduced[1:],
        )
        comparison = compare_reproduction(
            original_run_id="run-1",
            reproduced_run_id="run-2",
            plan=plan,
            original_results=original,
            reproduced_results=reproduced,
        )
        assert not comparison.matches
