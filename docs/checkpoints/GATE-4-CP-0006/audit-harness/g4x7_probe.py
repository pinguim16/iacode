#!/usr/bin/env python3
"""Independent Gate 4 credential-containment probe executed in the evaluator image.

The synthetic marker is assembled only in memory. This source and its report contain only the
construction recipe, booleans, stable reason codes, operation names and a one-way digest.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from iacode_common.secret_scanning import find_secret_kinds as canonical_find_secret_kinds
from iacode_contracts.quality import QualityCheck, QualityPlan, QualityPolicy, QualityResult
from iacode_evaluator import activities as activities_module
from iacode_evaluator import evidence as evidence_module
from iacode_evaluator.activities import derive_run_verdict, record_execution, set_runtime
from iacode_evaluator.evidence import (
    MemoryEvidenceRepository,
    MemoryObjectStore,
    QualityEvidenceStore,
)
from iacode_evaluator.store import MemoryQualityStore
from iacode_evaluator.telemetry import QualityMetrics
from iacode_evaluator.verdict import derive_verdict
from prometheus_client import CollectorRegistry


NOW = datetime(2026, 10, 11, 12, tzinfo=UTC)
PLAN_DIGEST = "a" * 64
SNAPSHOT_DIGEST = "b" * 64


class LogCapture:
    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    def info(self, message: str, *args: Any, **kwargs: Any) -> None:
        self.calls.append({"message": message, "args": args, "kwargs": kwargs})


class TracingRepository(MemoryEvidenceRepository):
    def __init__(self, timeline: list[str]) -> None:
        super().__init__()
        self.timeline = timeline

    async def by_digest(self, run_id: str, digest: str):  # type: ignore[no-untyped-def]
        self.timeline.append("repository.by_digest")
        return await super().by_digest(run_id, digest)

    async def by_evidence_id(self, evidence_id: str):  # type: ignore[no-untyped-def]
        self.timeline.append("repository.by_evidence_id")
        return await super().by_evidence_id(evidence_id)

    async def record(self, record):  # type: ignore[no-untyped-def]
        self.timeline.append("repository.record")
        return await super().record(record)


class TracingObjectStore(MemoryObjectStore):
    def __init__(self, timeline: list[str]) -> None:
        super().__init__()
        self.timeline = timeline

    def stat_object(self, bucket: str, key: str) -> object:
        self.timeline.append("object.stat")
        return super().stat_object(bucket, key)

    def put_object(self, bucket: str, key: str, data, length: int, **options: Any) -> None:  # type: ignore[no-untyped-def]
        self.timeline.append("object.put")
        super().put_object(bucket, key, data, length, **options)

    def get_object(self, bucket: str, key: str):  # type: ignore[no-untyped-def]
        self.timeline.append("object.get")
        return super().get_object(bucket, key)


def plan() -> QualityPlan:
    return QualityPlan(
        planId=PLAN_DIGEST,
        snapshotId="independent-g4x7-snapshot",
        snapshotDigest=SNAPSHOT_DIGEST,
        projectProfile="python",
        projectProfileDigest="c" * 64,
        policy=QualityPolicy(
            policyId="default",
            version="1.0.0",
            digest="d" * 64,
            profile="python",
            mandatoryCheckKinds=("unit",),
            maxRunSeconds=60,
            maxCheckSeconds=30,
            maxOutputBytes=4096,
        ),
        checks=(
            QualityCheck(
                checkId="q001-unit",
                kind="unit",
                runner="python.unit",
                command=("python", "-m", "unittest"),
                applicabilityReason="mandatory independent containment control",
                timeoutSeconds=30,
                requiredEvidenceKinds=("report",),
            ),
        ),
        createdAt=NOW,
    )


async def runtime(timeline: list[str], key: str):  # type: ignore[no-untyped-def]
    quality_store = MemoryQualityStore(now=lambda: NOW)
    frozen = plan()
    await quality_store.create_plan(frozen)
    run = await quality_store.create_run(
        plan_id=frozen.planId,
        owner_run_id=None,
        idempotency_key=key,
    )
    for state, event in (("PLANNED", "PLANNED"), ("QUEUED", "QUEUED"), ("RUNNING", "STARTED")):
        await quality_store.transition(
            run.run_id,
            state=state,
            event_type=event,
            dedupe_key=f"{key}:{state}",
            payload={},
        )
    objects = TracingObjectStore(timeline)
    repository = TracingRepository(timeline)
    evidence = QualityEvidenceStore(
        client=objects,
        bucket="independent-audit",
        repository=repository,
        now=lambda: NOW,
    )
    return quality_store, run, objects, repository, evidence


async def record_case(output: str, key: str, scanner):  # type: ignore[no-untyped-def]
    timeline: list[str] = []
    quality_store, run, objects, repository, evidence = await runtime(timeline, key)
    capture = LogCapture()
    original_scanner = evidence_module.find_secret_kinds
    original_logger = activities_module.logger

    def traced(text: str) -> list[str]:
        timeline.append("scanner.scan")
        return scanner(text)

    evidence_module.find_secret_kinds = traced
    activities_module.logger = capture
    set_runtime(
        SimpleNamespace(
            store=quality_store,
            evidence=evidence,
            metrics=QualityMetrics(CollectorRegistry()),
        )
    )
    try:
        result = await record_execution(
            {
                "runId": run.run_id,
                "checkId": "q001-unit",
                "finishedAt": NOW.isoformat(),
                "execution": {
                    "status": "SUCCEEDED",
                    "exitCode": 0,
                    "durationMs": 1,
                    "output": {"stdout": output, "stderr": ""},
                },
            }
        )
        verdict = await derive_run_verdict(
            {"runId": run.run_id, "derivedAt": NOW.isoformat()}
        )
    finally:
        set_runtime(None)
        evidence_module.find_secret_kinds = original_scanner
        activities_module.logger = original_logger
    return result, verdict, objects, repository, timeline, capture.calls


async def execute() -> dict[str, Any]:
    marker = "gh" + "p_" + ("q" * 24)
    marker_digest = hashlib.sha256(marker.encode("utf-8")).hexdigest()
    kinds = canonical_find_secret_kinds(marker)

    clean_result, clean_verdict, clean_objects, clean_repository, clean_timeline, _clean_logs = (
        await record_case("ordinary clean output", "null-control", canonical_find_secret_kinds)
    )
    clean_contract = clean_result["evidence"][0]
    null_control = {
        "status": "VALID" if (
            clean_result["status"] == "PASSED"
            and clean_verdict["verdict"] == "PASS"
            and len(clean_objects.objects) == 1
            and len(clean_repository.records) == 1
            and clean_contract
        ) else "INVALID",
        "resultStatus": clean_result["status"],
        "verdict": clean_verdict["verdict"],
        "objects": len(clean_objects.objects),
        "records": len(clean_repository.records),
        "timeline": clean_timeline,
    }

    result, verdict, objects, repository, timeline, logs = await record_case(
        marker, "canonical-marker", canonical_find_secret_kinds
    )
    serialized = json.dumps(
        {"result": result, "verdict": verdict, "logs": logs},
        sort_keys=True,
        default=str,
    )
    marker_case = {
        "scannerKinds": kinds,
        "scanPrecededDurableOperation": timeline == ["scanner.scan"],
        "timeline": timeline,
        "resultStatus": result["status"],
        "resultExitCode": result["exitCode"],
        "resultSummary": result["summary"],
        "evidenceCount": len(result["evidence"]),
        "findingCount": len(result["findings"]),
        "verdict": verdict["verdict"],
        "objectCount": len(objects.objects),
        "metadataCount": len(repository.records),
        "resolvableEvidenceCount": 0,
        "serializedOutputContainsMarker": marker in serialized,
        "capturedLogsContainMarker": marker in json.dumps(logs, default=str),
    }

    def unavailable(_text: str) -> list[str]:
        raise RuntimeError("synthetic scanner unavailable")

    failed_result, failed_verdict, failed_objects, failed_repository, failed_timeline, failed_logs = (
        await record_case("otherwise clean output", "scanner-failure", unavailable)
    )
    scanner_failure = {
        "scanPrecededDurableOperation": failed_timeline == ["scanner.scan"],
        "timeline": failed_timeline,
        "resultStatus": failed_result["status"],
        "resultSummary": failed_result["summary"],
        "evidenceCount": len(failed_result["evidence"]),
        "findingCount": len(failed_result["findings"]),
        "verdict": failed_verdict["verdict"],
        "objectCount": len(failed_objects.objects),
        "metadataCount": len(failed_repository.records),
        "capturedLogsContainInput": "otherwise clean output" in json.dumps(failed_logs, default=str),
    }

    legacy_timeline: list[str] = []
    legacy_objects = TracingObjectStore(legacy_timeline)
    legacy_repository = TracingRepository(legacy_timeline)
    legacy_store = QualityEvidenceStore(
        client=legacy_objects,
        bucket="independent-audit",
        repository=legacy_repository,
        now=lambda: NOW,
    )
    legacy_contract = await legacy_store.put(
        run_id="legacy-run",
        result_id="legacy-result",
        kind="report",
        content=b"clean legacy object",
        media_type="text/plain",
        producer="independent-audit",
    )
    object_key = next(iter(legacy_objects.objects))
    legacy_objects.objects[object_key] = marker.encode("utf-8")
    legacy_timeline.clear()
    original_legacy_scanner = evidence_module.find_secret_kinds

    def trace_legacy_scan(text: str) -> list[str]:
        legacy_timeline.append("scanner.scan")
        return canonical_find_secret_kinds(text)

    evidence_module.find_secret_kinds = trace_legacy_scan
    try:
        resolved = await legacy_store.resolve(legacy_contract)
    finally:
        evidence_module.find_secret_kinds = original_legacy_scanner
    legacy_result = QualityResult(
        resultId="legacy-result",
        runId="legacy-run",
        checkId="q001-unit",
        status="PASSED",
        exitCode=0,
        durationMs=1,
        timedOut=False,
        truncated=False,
        summary="legacy result",
        evidence=(legacy_contract,),
        findings=(),
        finishedAt=NOW,
    )
    legacy_verdict = derive_verdict(
        run_id="legacy-run",
        plan=plan(),
        results=(legacy_result,),
        resolved_evidence_digests=set() if not resolved else {legacy_contract.digest},
        derived_at=NOW,
    )
    legacy = {
        "resolutionAccepted": resolved,
        "verdict": legacy_verdict.verdict,
        "timeline": legacy_timeline,
        "rescannedAfterRead": (
            "object.get" in legacy_timeline
            and legacy_timeline[-1] == "scanner.scan"
        ),
    }

    marker_ok = (
        "GitHub credential" in kinds
        and marker_case["scanPrecededDurableOperation"]
        and marker_case["resultStatus"] == "ERROR"
        and marker_case["resultExitCode"] is None
        and marker_case["evidenceCount"] == 0
        and marker_case["findingCount"] == 0
        and marker_case["verdict"] == "FAIL"
        and marker_case["objectCount"] == 0
        and marker_case["metadataCount"] == 0
        and not marker_case["serializedOutputContainsMarker"]
        and not marker_case["capturedLogsContainMarker"]
    )
    failure_ok = (
        scanner_failure["scanPrecededDurableOperation"]
        and scanner_failure["resultStatus"] == "ERROR"
        and scanner_failure["evidenceCount"] == 0
        and scanner_failure["findingCount"] == 0
        and scanner_failure["verdict"] == "FAIL"
        and scanner_failure["objectCount"] == 0
        and scanner_failure["metadataCount"] == 0
    )
    legacy_ok = (
        legacy["resolutionAccepted"] is False
        and legacy["verdict"] == "FAIL"
        and legacy["rescannedAfterRead"] is True
    )
    return {
        "schemaVersion": "1.0.0",
        "artifact": "GATE-4-INDEPENDENT-G4-X7-PROBE",
        "checkpoint": "GATE-4-CP-0006",
        "subjectCheckpoint": "GATE-4-CP-0005",
        "subjectCommit": "c631270e49c095a9777825c0bc18818694c07ffb",
        "generatedAt": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "syntheticMarkerSha256": marker_digest,
        "nullControl": null_control,
        "canonicalMarker": marker_case,
        "scannerFailure": scanner_failure,
        "legacyObject": legacy,
        "safety": (
            "The synthetic value was assembled only in memory and never emitted. This report "
            "contains only its SHA-256 digest, canonical finding kind and non-secret observations."
        ),
        "result": "PASS" if (
            null_control["status"] == "VALID" and marker_ok and failure_ok and legacy_ok
        ) else "FAIL",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path, required=True)
    arguments = parser.parse_args()
    report = asyncio.run(execute())
    arguments.report.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        "G4_X7_INDEPENDENT_PROBE=" + str(report["result"])
        + " control=" + str(report["nullControl"]["status"])
        + " marker=" + str(report["canonicalMarker"]["resultStatus"])
        + " scannerFailure=" + str(report["scannerFailure"]["resultStatus"])
        + " legacyResolved=" + str(report["legacyObject"]["resolutionAccepted"])
    )
    return 0 if report["result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
