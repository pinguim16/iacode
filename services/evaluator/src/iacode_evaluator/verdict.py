"""Pure, fail-closed verdict derivation from a frozen plan and resolved evidence."""

from __future__ import annotations

from datetime import UTC, datetime

from iacode_contracts.quality import QualityPlan, QualityResult, QualityVerdict

from iacode_evaluator.canonical import digest


def result_digest(result: QualityResult) -> str:
    return digest(result.model_dump(mode="json"))


def derive_verdict(
    *,
    run_id: str,
    plan: QualityPlan,
    results: tuple[QualityResult, ...],
    resolved_evidence_digests: set[str],
    derived_at: datetime | None = None,
) -> QualityVerdict:
    reasons: list[str] = []
    expected = {
        check.checkId: check for check in plan.checks if check.applicable and check.mandatory
    }
    by_check: dict[str, QualityResult] = {}
    for result in results:
        if result.runId != run_id:
            reasons.append(f"result {result.resultId} belongs to another run")
            continue
        if result.checkId not in expected:
            reasons.append(f"unexpected result for {result.checkId}")
            continue
        if result.checkId in by_check:
            reasons.append(f"duplicate result for {result.checkId}")
            continue
        by_check[result.checkId] = result
    for check_id, check in expected.items():
        result = by_check.get(check_id)
        if result is None:
            reasons.append(f"missing result for {check_id}")
            continue
        if result.status != "PASSED":
            reasons.append(f"{check_id} ended {result.status}")
        kinds = {item.kind for item in result.evidence}
        missing_kinds = sorted(set(check.requiredEvidenceKinds) - kinds)
        if missing_kinds:
            reasons.append(f"{check_id} lacks evidence kinds: {', '.join(missing_kinds)}")
        for item in result.evidence:
            if item.digest not in resolved_evidence_digests:
                reasons.append(f"{check_id} has unresolved evidence {item.evidenceId}")
    if not expected:
        reasons.append("the required check set is missing")
    verdict = "FAIL" if reasons else "PASS"
    if not reasons:
        reasons.append("every applicable mandatory check passed with resolved required evidence")
    result_digests = tuple(result_digest(result) for result in results)
    evidence_digests = tuple(
        sorted({item.digest for result in results for item in result.evidence})
    )
    instant = derived_at or datetime.now(UTC)
    content = {
        "contractVersion": "1.0.0",
        "runId": run_id,
        "planId": plan.planId,
        "verdict": verdict,
        "reasons": reasons,
        "resultDigests": result_digests,
        "evidenceDigests": evidence_digests,
        "derivedAt": instant.isoformat(),
    }
    return QualityVerdict(**content, digest=digest(content))
