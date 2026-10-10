"""Deterministic quality plan construction."""

from __future__ import annotations

from datetime import UTC, datetime

from iacode_contracts.quality import QualityCheck, QualityPlan

from iacode_evaluator.canonical import digest
from iacode_evaluator.errors import QualityError
from iacode_evaluator.policy import PolicyRegistry
from iacode_evaluator.projects import ProjectProfile
from iacode_evaluator.runners import get_runner


def _has_unit_tests(project: ProjectProfile, root: str, stack: str) -> bool:
    """Derive unit-check applicability from the frozen inventory, without executing content."""
    prefix = "" if root == "." else f"{root.rstrip('/')}/"
    paths = tuple(path[len(prefix) :] for path in project.source_paths if path.startswith(prefix))
    if stack == "python":
        return any(
            path.endswith(".py")
            and (
                path.rsplit("/", 1)[-1].startswith("test_")
                or path.rsplit("/", 1)[-1].endswith("_test.py")
            )
            for path in paths
        )
    if stack in {"node", "typescript", "angular"}:
        suffixes = (".spec.ts", ".test.ts", ".spec.js", ".test.js")
        return any(path.endswith(suffixes) for path in paths)
    return True


def select_profile(project: ProjectProfile, registry: PolicyRegistry) -> str:
    if project.confidence == "UNSUPPORTED":
        raise QualityError("PROJECT_UNSUPPORTED", "no supported toolchain was detected")
    candidates = [
        profile.name
        for profile in registry.profiles.values()
        if set(profile.stacks) == set(project.stacks)
    ]
    if len(candidates) != 1:
        reason = (
            "no exact policy profile" if not candidates else "more than one exact policy profile"
        )
        raise QualityError("PROJECT_PROFILE_AMBIGUOUS", f"{reason} for {project.profile_id}")
    return candidates[0]


def _identity(
    snapshot_id: str,
    snapshot_digest: str,
    project: ProjectProfile,
    policy_digest: str,
    checks: tuple[QualityCheck, ...],
) -> str:
    return digest(
        {
            "contractVersion": "1.0.0",
            "snapshotId": snapshot_id,
            "snapshotDigest": snapshot_digest,
            "projectProfile": project.profile_id,
            "projectProfileDigest": project.digest,
            "policyDigest": policy_digest,
            "checks": [check.model_dump(mode="json") for check in checks],
        }
    )


def build_plan(
    *,
    snapshot_id: str,
    snapshot_digest: str,
    project: ProjectProfile,
    registry: PolicyRegistry,
    configuration: dict | None = None,
    created_at: datetime | None = None,
) -> QualityPlan:
    profile = registry.profile(select_profile(project, registry))
    policy = registry.contract(profile, configuration)
    checks: list[QualityCheck] = []
    selected = profile.runners + tuple((configuration or {}).get("additionalRunners") or ())
    index = 0
    for identifier in selected:
        runner = get_runner(identifier)
        roots = (
            (".",)
            if runner.stack == "common"
            else tuple(
                root for stack, root in project.workspace_roots if stack == runner.stack
            )
        )
        for root in roots:
            index += 1
            timeout = min(runner.timeout_seconds, policy.maxCheckSeconds)
            applicable = runner.kind != "unit" or _has_unit_tests(project, root, runner.stack)
            checks.append(
                QualityCheck(
                    checkId=f"q{index:03d}-{runner.kind}",
                    kind=runner.kind,
                    runner=runner.identifier,
                    command=runner.command,
                    workingDirectory=root,
                    mandatory=applicable,
                    applicable=applicable,
                    applicabilityReason=(
                        f"profile {profile.name} requires {runner.kind} in {root}"
                        if applicable
                        else f"no {runner.stack} unit-test source was found in {root}"
                    ),
                    timeoutSeconds=timeout,
                    requiredEvidenceKinds=runner.evidence_kinds,
                )
            )
    frozen = tuple(checks)
    return QualityPlan(
        planId=_identity(snapshot_id, snapshot_digest, project, policy.digest, frozen),
        snapshotId=snapshot_id,
        snapshotDigest=snapshot_digest,
        projectProfile=project.profile_id,
        projectProfileDigest=project.digest,
        policy=policy,
        checks=frozen,
        createdAt=created_at or datetime.now(UTC),
    )
