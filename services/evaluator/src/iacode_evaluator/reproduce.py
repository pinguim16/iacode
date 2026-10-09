"""Comparison of a new quality run with the immutable run it reproduces."""

from __future__ import annotations

from dataclasses import dataclass

from iacode_contracts.quality import QualityPlan, QualityResult

from iacode_evaluator.errors import QualityError
from iacode_evaluator.verdict import result_digest


@dataclass(frozen=True)
class ReproductionComparison:
    original_run_id: str
    reproduced_run_id: str
    plan_id: str
    original_result_digests: tuple[str, ...]
    reproduced_result_digests: tuple[str, ...]
    original_evidence_digests: tuple[str, ...]
    reproduced_evidence_digests: tuple[str, ...]
    matches: bool


def compare_reproduction(
    *,
    original_run_id: str,
    reproduced_run_id: str,
    plan: QualityPlan,
    original_results: tuple[QualityResult, ...],
    reproduced_results: tuple[QualityResult, ...],
) -> ReproductionComparison:
    """Compare stable outcomes while excluding run identity, timing and sandbox identity."""
    if original_run_id == reproduced_run_id:
        raise QualityError(
            "REPRODUCTION_RUN_REUSED", "a reproduction must be recorded as a new quality run"
        )

    def outcomes(run_id: str, results: tuple[QualityResult, ...]) -> tuple[str, ...]:
        by_check: dict[str, str] = {}
        for result in results:
            if result.runId != run_id:
                raise QualityError(
                    "REPRODUCTION_RUN_MISMATCH", "a compared result belongs to another run"
                )
            if result.checkId in by_check:
                raise QualityError(
                    "REPRODUCTION_DUPLICATE_RESULT", "a compared run repeats a check result"
                )
            by_check[result.checkId] = result_digest(result)
        return tuple(f"{check_id}:{by_check[check_id]}" for check_id in sorted(by_check))

    def evidence(results: tuple[QualityResult, ...]) -> tuple[str, ...]:
        return tuple(sorted({item.digest for result in results for item in result.evidence}))

    original_outcomes = outcomes(original_run_id, original_results)
    reproduced_outcomes = outcomes(reproduced_run_id, reproduced_results)
    original_evidence = evidence(original_results)
    reproduced_evidence = evidence(reproduced_results)
    return ReproductionComparison(
        original_run_id=original_run_id,
        reproduced_run_id=reproduced_run_id,
        plan_id=plan.planId,
        original_result_digests=original_outcomes,
        reproduced_result_digests=reproduced_outcomes,
        original_evidence_digests=original_evidence,
        reproduced_evidence_digests=reproduced_evidence,
        matches=(
            original_outcomes == reproduced_outcomes and original_evidence == reproduced_evidence
        ),
    )
