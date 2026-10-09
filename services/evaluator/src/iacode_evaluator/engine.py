"""Plan execution orchestration; dispatchers execute checks, never this process."""

from __future__ import annotations

from collections.abc import Awaitable, Callable

from iacode_contracts.quality import QualityPlan, QualityResult, QualityVerdict

from iacode_evaluator.verdict import derive_verdict

Dispatcher = Callable[[str, QualityPlan, object], Awaitable[QualityResult]]
EvidenceResolver = Callable[[str], Awaitable[bool]]


async def execute_plan(
    *, run_id: str, plan: QualityPlan, dispatcher: Dispatcher, evidence_resolver: EvidenceResolver
) -> tuple[tuple[QualityResult, ...], QualityVerdict]:
    """Execute every independent applicable check and derive one fail-closed verdict."""
    results: list[QualityResult] = []
    by_check: dict[str, QualityResult] = {}
    for check in plan.checks:
        if not check.applicable:
            continue
        blocked = [
            dependency
            for dependency in check.dependsOn
            if dependency not in by_check or by_check[dependency].status != "PASSED"
        ]
        if blocked:
            # Dependency skips are represented by the dispatcher owner in the durable workflow;
            # this pure kernel simply leaves the result absent, which the verdict rejects and names.
            continue
        result = await dispatcher(run_id, plan, check)
        results.append(result)
        by_check[check.checkId] = result
    resolved: set[str] = set()
    for result in results:
        for item in result.evidence:
            if await evidence_resolver(item.digest):
                resolved.add(item.digest)
    frozen = tuple(results)
    return frozen, derive_verdict(
        run_id=run_id, plan=plan, results=frozen, resolved_evidence_digests=resolved
    )
