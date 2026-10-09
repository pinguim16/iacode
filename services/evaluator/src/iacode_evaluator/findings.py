"""Stable finding fingerprints and deterministic recurrence-preserving deduplication."""

from __future__ import annotations

from iacode_contracts.quality import QualityFinding

from iacode_evaluator.canonical import digest


def finding_fingerprint(*, check_id: str, category: str, message: str, location: str | None) -> str:
    return digest(
        {
            "checkId": check_id,
            "category": category,
            "message": " ".join(message.split()),
            "location": location,
        }
    )


def deduplicate(findings: tuple[QualityFinding, ...]) -> tuple[QualityFinding, ...]:
    grouped: dict[str, QualityFinding] = {}
    for finding in findings:
        previous = grouped.get(finding.fingerprint)
        if previous is None:
            grouped[finding.fingerprint] = finding
            continue
        grouped[finding.fingerprint] = previous.model_copy(
            update={
                "recurrenceCount": previous.recurrenceCount + finding.recurrenceCount,
                "evidenceIds": tuple(sorted(set(previous.evidenceIds) | set(finding.evidenceIds))),
            }
        )
    return tuple(grouped[key] for key in sorted(grouped))
