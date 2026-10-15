#!/usr/bin/env python3
"""Internal Gate 4 false-PASS battery with an unmutated PASS control.

Every mandatory mutation named by the canonical checklist executes against the shipped contracts,
immutable store or verdict function inside the rebuilt evaluator image. A rejection for the wrong
reason is an escape. The host wrapper records the report as ``M2-INTERNAL-RED-TEAM.json``.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import warnings
import zipfile
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace
from typing import Any

if "--in-image" not in sys.argv:
    from ledger_common import (
        LedgerError,
        find_root,
        resolve_latest,
        scope_fingerprint,
        use_utf8_stdout,
        utc_now,
        write_json,
    )

SOURCE = "scripts/development-ledger/gate4_red_team.py — Gate 4 internal false-PASS battery"


def _in_image_battery() -> dict[str, Any]:
    from iacode_contracts.quality import (
        QualityCheck,
        QualityEvidence,
        QualityPlan,
        QualityPolicy,
        QualityResult,
    )
    from iacode_evaluator.errors import QualityError
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
    from pydantic import ValidationError

    now = datetime(2026, 10, 9, 20, tzinfo=UTC)
    run_id = "red-team-run"
    plan_sha = "a" * 64
    snapshot_sha = "b" * 64
    evidence_sha = "c" * 64

    def plan() -> QualityPlan:
        return QualityPlan(
            planId=plan_sha,
            snapshotId="snapshot-red-team",
            snapshotDigest=snapshot_sha,
            projectProfile="python",
            projectProfileDigest="d" * 64,
            policy=QualityPolicy(
                policyId="default",
                version="1.0.0",
                digest="e" * 64,
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
                    applicabilityReason="mandatory red-team control",
                    timeoutSeconds=30,
                    requiredEvidenceKinds=("report",),
                ),
            ),
            createdAt=now,
        )

    def evidence() -> QualityEvidence:
        return QualityEvidence(
            evidenceId="evidence-red-team",
            kind="report",
            artifactId="artifact-red-team",
            digest=evidence_sha,
            sizeBytes=24,
            mediaType="application/json",
            producer="iacode-evaluator",
            sourceDigests=(snapshot_sha,),
            createdAt=now,
            retentionClass="quality-evidence",
        )

    def result(status: str = "PASSED", **updates: Any) -> QualityResult:
        body: dict[str, Any] = {
            "resultId": "result-red-team",
            "runId": run_id,
            "checkId": "q001-unit",
            "status": status,
            "exitCode": 0 if status == "PASSED" else None,
            "durationMs": 1,
            "timedOut": status == "TIMED_OUT",
            "truncated": False,
            "summary": f"red-team {status}",
            "evidence": (evidence(),),
            "findings": (),
            "finishedAt": now,
        }
        body.update(updates)
        return QualityResult(**body)

    canonical_plan = plan()
    canonical_result = result()
    control = derive_verdict(
        run_id=run_id,
        plan=canonical_plan,
        results=(canonical_result,),
        resolved_evidence_digests={evidence_sha},
        derived_at=now,
    )
    attacks: list[dict[str, Any]] = []

    def attack(
        identifier: str,
        target: str,
        mutation: str,
        expected: str,
        operation: Callable[[], tuple[bool, str]],
    ) -> None:
        try:
            defended, observed = operation()
        except Exception as error:
            defended, observed = False, f"attack crashed: {type(error).__name__}"
        attacks.append(
            {
                "attackId": identifier,
                "description": target,
                "target": target,
                "mutation": mutation,
                "expectedDefense": expected,
                "observed": observed,
                "result": "DEFENDED" if defended else "ESCAPED",
                "evidence": [
                    "file:services/evaluator/src/iacode_evaluator/verdict.py",
                    "file:packages/contracts/src/iacode_contracts/quality.py",
                ],
                "mandatory": True,
                "origin": "Gate 4 internal Red Team in the rebuilt evaluator image",
            }
        )

    def verdict_mutation(mutated: QualityResult | None) -> tuple[bool, str]:
        verdict = derive_verdict(
            run_id=run_id,
            plan=canonical_plan,
            results=() if mutated is None else (mutated,),
            resolved_evidence_digests={evidence_sha},
            derived_at=now,
        )
        return verdict.verdict == "FAIL", f"verdict={verdict.verdict}; reasons={verdict.reasons}"

    attack(
        "A",
        "missing result",
        "remove the only mandatory result",
        "derived verdict FAIL names the missing check",
        lambda: verdict_mutation(None),
    )

    def flip_exit() -> tuple[bool, str]:
        try:
            result(exitCode=1)
        except ValidationError as error:
            return (
                "a passed check requires exit code zero" in str(error),
                "contract refused non-zero PASS",
            )
        return False, "contract accepted a non-zero PASS"

    attack(
        "B",
        "exit-code forgery",
        "keep PASSED and flip exitCode to 1",
        "the result contract refuses the contradictory shape",
        flip_exit,
    )

    def forged_evidence() -> tuple[bool, str]:
        verdict = derive_verdict(
            run_id=run_id,
            plan=canonical_plan,
            results=(canonical_result,),
            resolved_evidence_digests={"f" * 64},
            derived_at=now,
        )
        return verdict.verdict == "FAIL", f"verdict={verdict.verdict}; reasons={verdict.reasons}"

    attack(
        "C",
        "forged evidence",
        "replace the resolved digest set",
        "the evidence reference is unresolved and verdict is FAIL",
        forged_evidence,
    )

    async def plan_conflict(field: str) -> tuple[bool, str]:
        store = MemoryQualityStore(now=lambda: now)
        await store.create_plan(canonical_plan)
        if field == "policy":
            changed_policy = canonical_plan.policy.model_copy(update={"maxCheckSeconds": 1})
            changed = canonical_plan.model_copy(update={"policy": changed_policy})
        else:
            changed = canonical_plan.model_copy(update={"snapshotDigest": "f" * 64})
        try:
            await store.create_plan(changed)
        except QualityError as error:
            return error.code == "PLAN_ID_CONFLICT", f"store refused {error.code}"
        return False, "store accepted changed material under the frozen plan identity"

    attack(
        "D",
        "policy mutation",
        "change maxCheckSeconds under the same planId",
        "the immutable store refuses PLAN_ID_CONFLICT",
        lambda: asyncio.run(plan_conflict("policy")),
    )
    attack(
        "E",
        "snapshot mutation",
        "change snapshotDigest under the same planId",
        "the immutable store refuses PLAN_ID_CONFLICT",
        lambda: asyncio.run(plan_conflict("snapshot")),
    )

    def invalid_contract(field: str, value: Any, expected_text: str) -> tuple[bool, str]:
        body = canonical_result.model_dump(mode="python")
        body[field] = value
        try:
            QualityResult.model_validate(body)
        except ValidationError as error:
            return expected_text in str(error), f"contract refused {field}"
        return False, f"contract accepted {field}={value}"

    attack(
        "F",
        "wrong origin",
        "post a result with origin CALLER",
        "the closed origin contract refuses it",
        lambda: invalid_contract("origin", "CALLER", "EVALUATOR"),
    )
    for identifier, status, updates in (
        ("G", "TIMED_OUT", {"timedOut": True, "exitCode": 124}),
        ("H", "DENIED", {"exitCode": None}),
        ("I", "CANCELLED", {"exitCode": None}),
    ):
        attack(
            identifier,
            f"{status.lower()} result",
            f"replace PASSED with {status}",
            "the derived verdict is FAIL",
            lambda status=status, updates=updates: verdict_mutation(result(status, **updates)),
        )
    attack(
        "J",
        "unknown status",
        "submit status ASSERTED_GOOD",
        "the closed result-status contract refuses it",
        lambda: invalid_contract("status", "ASSERTED_GOOD", "unknown quality result status"),
    )

    async def secret_evidence_containment() -> tuple[bool, str]:
        store = MemoryQualityStore(now=lambda: now)
        await store.create_plan(canonical_plan)
        run = await store.create_run(
            plan_id=canonical_plan.planId,
            owner_run_id=None,
            idempotency_key="red-team-secret-containment",
        )
        for state, event_type in (
            ("PLANNED", "PLANNED"),
            ("QUEUED", "QUEUED"),
            ("RUNNING", "STARTED"),
        ):
            await store.transition(
                run.run_id,
                state=state,
                event_type=event_type,
                dedupe_key=f"secret:{state}",
                payload={},
            )
        objects = MemoryObjectStore()
        repository = MemoryEvidenceRepository()
        evidence_store = QualityEvidenceStore(
            client=objects,
            bucket="red-team",
            repository=repository,
            now=lambda: now,
        )
        set_runtime(
            SimpleNamespace(
                store=store,
                evidence=evidence_store,
                metrics=QualityMetrics(CollectorRegistry()),
            )
        )
        marker = "gh" + "p_" + "z" * 20
        try:
            recorded = await record_execution(
                {
                    "runId": run.run_id,
                    "checkId": "q001-unit",
                    "finishedAt": now.isoformat(),
                    "execution": {
                        "status": "SUCCEEDED",
                        "exitCode": 0,
                        "durationMs": 1,
                        "output": {"stdout": marker},
                    },
                }
            )
            verdict = await derive_run_verdict(
                {"runId": run.run_id, "derivedAt": now.isoformat()}
            )
        finally:
            set_runtime(None)
        serialized = json.dumps(
            {"result": recorded, "verdict": verdict},
            ensure_ascii=False,
            sort_keys=True,
        )
        defended = (
            recorded["status"] == "ERROR"
            and not recorded["evidence"]
            and verdict["verdict"] == "FAIL"
            and not objects.objects
            and not repository.records
            and marker not in serialized
        )
        observed = (
            f"status={recorded['status']}; verdict={verdict['verdict']}; "
            f"objects={len(objects.objects)}; records={len(repository.records)}; "
            f"prohibited-bytes-absent={marker not in serialized}"
        )
        return defended, observed

    attack(
        "Q",
        "pre-persistence secret containment",
        "send a canonical scanner-detected marker under an ordinary structured output key",
        "reject before object or metadata persistence and derive FAIL from a sanitized result",
        lambda: asyncio.run(secret_evidence_containment()),
    )

    class TracingEvidenceRepository(MemoryEvidenceRepository):
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

        def put_object(self, bucket, key, data, length, **options):  # type: ignore[no-untyped-def]
            self.timeline.append("object.put")
            return super().put_object(bucket, key, data, length, **options)

        def get_object(self, bucket: str, key: str):  # type: ignore[no-untyped-def]
            self.timeline.append("object.get")
            return super().get_object(bucket, key)

    async def scanner_failure_containment() -> tuple[bool, str]:
        timeline: list[str] = []
        store = MemoryQualityStore(now=lambda: now)
        await store.create_plan(canonical_plan)
        run = await store.create_run(
            plan_id=canonical_plan.planId,
            owner_run_id=None,
            idempotency_key="red-team-scanner-failure",
        )
        for state, event_type in (
            ("PLANNED", "PLANNED"),
            ("QUEUED", "QUEUED"),
            ("RUNNING", "STARTED"),
        ):
            await store.transition(
                run.run_id,
                state=state,
                event_type=event_type,
                dedupe_key=f"scanner-failure:{state}",
                payload={},
            )
        objects = TracingObjectStore(timeline)
        repository = TracingEvidenceRepository(timeline)
        evidence_store = QualityEvidenceStore(
            client=objects,
            bucket="red-team",
            repository=repository,
            now=lambda: now,
        )
        original_scanner = evidence_module.find_secret_kinds

        def unavailable(_text: str) -> list[str]:
            timeline.append("scanner.scan")
            raise RuntimeError("synthetic scanner unavailable")

        evidence_module.find_secret_kinds = unavailable
        set_runtime(
            SimpleNamespace(
                store=store,
                evidence=evidence_store,
                metrics=QualityMetrics(CollectorRegistry()),
            )
        )
        try:
            recorded = await record_execution(
                {
                    "runId": run.run_id,
                    "checkId": "q001-unit",
                    "finishedAt": now.isoformat(),
                    "execution": {
                        "status": "SUCCEEDED",
                        "exitCode": 0,
                        "durationMs": 1,
                        "output": {"stdout": "otherwise clean output"},
                    },
                }
            )
            verdict = await derive_run_verdict(
                {"runId": run.run_id, "derivedAt": now.isoformat()}
            )
        finally:
            set_runtime(None)
            evidence_module.find_secret_kinds = original_scanner
        scan_before_store = timeline == ["scanner.scan"]
        defended = (
            scan_before_store
            and recorded["status"] == "ERROR"
            and not recorded["evidence"]
            and verdict["verdict"] == "FAIL"
            and not objects.objects
            and not repository.records
        )
        observed = (
            f"scan-before-store={scan_before_store}; status={recorded['status']}; "
            f"verdict={verdict['verdict']}; objects={len(objects.objects)}; "
            f"records={len(repository.records)}"
        )
        return defended, observed

    attack(
        "R",
        "scanner availability",
        "make the canonical evidence scanner throw before it can classify clean bytes",
        "fail closed before any lookup or write and derive FAIL",
        lambda: asyncio.run(scanner_failure_containment()),
    )

    async def legacy_object_containment() -> tuple[bool, str]:
        timeline: list[str] = []
        objects = TracingObjectStore(timeline)
        repository = TracingEvidenceRepository(timeline)
        evidence_store = QualityEvidenceStore(
            client=objects,
            bucket="red-team",
            repository=repository,
            now=lambda: now,
        )
        stored = await evidence_store.put(
            run_id=run_id,
            result_id="result-red-team",
            kind="report",
            content=b"clean legacy object",
            media_type="text/plain",
            producer="iacode-evaluator",
        )
        object_key = next(iter(objects.objects))
        objects.objects[object_key] = ("gh" + "p_" + "y" * 24).encode("utf-8")
        timeline.clear()
        original_scanner = evidence_module.find_secret_kinds

        def traced_scanner(text: str) -> list[str]:
            timeline.append("scanner.scan")
            return original_scanner(text)

        evidence_module.find_secret_kinds = traced_scanner
        try:
            resolved = await evidence_store.resolve(stored)
        finally:
            evidence_module.find_secret_kinds = original_scanner
        legacy_result = result(evidence=(stored,))
        verdict = derive_verdict(
            run_id=run_id,
            plan=canonical_plan,
            results=(legacy_result,),
            resolved_evidence_digests=set() if not resolved else {stored.digest},
            derived_at=now,
        )
        rescanned_after_read = "object.get" in timeline and timeline[-1] == "scanner.scan"
        defended = not resolved and rescanned_after_read and verdict.verdict == "FAIL"
        observed = (
            f"resolved={resolved}; rescanned-after-read={rescanned_after_read}; "
            f"verdict={verdict.verdict}"
        )
        return defended, observed

    attack(
        "S",
        "legacy persisted object",
        "replace already persisted clean bytes with a canonical credential shape",
        "rescan after read, refuse resolution and derive FAIL",
        lambda: asyncio.run(legacy_object_containment()),
    )

    escaped = [item for item in attacks if item["result"] == "ESCAPED"]
    return {
        "baselineControl": {
            "result": "VALID" if control.verdict == "PASS" else "INVALID",
            "detail": f"unmutated complete result derived {control.verdict}",
            "evidence": ["file:services/evaluator/src/iacode_evaluator/verdict.py"],
        },
        "attacks": attacks,
        "escaped": len(escaped),
        "defended": len(attacks) - len(escaped),
        "total": len(attacks),
    }


def _compose(root: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    directory = root / "infra" / "compose"
    return subprocess.run(
        [
            "docker",
            "compose",
            "--project-directory",
            str(directory),
            "--file",
            str(directory / "docker-compose.yml"),
            "--env-file",
            str(directory / ".env"),
            *arguments,
        ],
        cwd=root,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
        timeout=1800,
    )


def _host_attacks(root: Path, checkpoint: Path) -> list[dict[str, Any]]:
    """Exercise the audit's host-side bundle and live-lifecycle attacks.

    The evaluator image owns A-J and Q-S.  K-O target the host review transport, P consumes the four
    current live scenario reports that precede this stage in the full verifier, and T rebuilds the
    review transport in a detached clone. Keeping those operations on their real side of the
    boundary avoids pretending that an evaluator container can inspect a Git review archive or the
    host orchestration reports.
    """
    from review_bundle import declaration_from_reconstruction
    from review_bundle import manifest as bundle_manifest
    from review_bundle import validate as validate_bundle
    from review_bundle import verify_declaration

    attacks: list[dict[str, Any]] = []

    def record(
        identifier: str,
        target: str,
        mutation: str,
        expected: str,
        defended: bool,
        observed: str,
        evidence: list[str],
    ) -> None:
        attacks.append(
            {
                "attackId": identifier,
                "description": target,
                "target": target,
                "mutation": mutation,
                "expectedDefense": expected,
                "observed": observed,
                "result": "DEFENDED" if defended else "ESCAPED",
                "evidence": evidence,
                "mandatory": True,
                "origin": "Gate 4 internal Red Team on the host review boundary",
            }
        )

    prefix = f"repository/{checkpoint.relative_to(root).as_posix()}/"
    base_payload = {
        **{prefix + name: b"{}\n" for name in (
            "STATE.json",
            "REQUIREMENTS-MATRIX.json",
            "FUNCTIONAL-ACCEPTANCE.json",
            "QUALITY.json",
            "M2-INTERNAL-RED-TEAM.json",
            "COMPLETENESS-REPORT.json",
            "FILES.json",
            "COMMANDS.jsonl",
        )},
        "repository/tests/test_control.py": b"# control\n",
        "repository/apps/api/migrations/control.py": b"# migration\n",
        "repository/.iacode/schemas/control.json": b"{}\n",
        "repository/.iacode/policies/control.json": b"{}\n",
        "repository/docs/control.md": b"# control\n",
        "bundle/CHANGESET.diff": b"",
        "bundle/REVIEW-STATE.json": b"{}\n",
    }

    with tempfile.TemporaryDirectory(dir=root / "var") as temporary:
        directory = Path(temporary)

        def write_bundle(
            name: str,
            mutate: Callable[[dict[str, bytes]], None] | None = None,
            duplicate: str | None = None,
        ) -> Path:
            payload = dict(base_payload)
            if mutate:
                mutate(payload)
            declared = bundle_manifest(payload)
            archive = directory / f"{name}.zip"
            with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
                for member, content in sorted(payload.items()):
                    bundle.writestr(member, content)
                bundle.writestr(
                    "bundle/MANIFEST.json",
                    json.dumps(declared, sort_keys=True, separators=(",", ":")) + "\n",
                )
                if duplicate:
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore", UserWarning)
                        bundle.writestr(duplicate, payload[duplicate])
            return archive

        def outcome(
            identifier: str,
            target: str,
            mutation: str,
            expected_fragment: str,
            bundle: Path,
        ) -> None:
            report = validate_bundle(root, checkpoint, bundle)
            defended = report["result"] == "FAIL" and any(
                expected_fragment in finding for finding in report["findings"]
            )
            record(
                identifier,
                target,
                mutation,
                f"validator refuses with {expected_fragment}",
                defended,
                f"result={report['result']}; expected-finding={defended}",
                ["file:scripts/development-ledger/review_bundle.py"],
            )

        altered = write_bundle("altered")
        with zipfile.ZipFile(altered, "a", compression=zipfile.ZIP_DEFLATED) as bundle:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", UserWarning)
                bundle.writestr("bundle/CHANGESET.diff", b"altered")
        outcome("K", "bundle integrity", "alter one payload byte", "digest mismatch", altered)

        missing = write_bundle(
            "missing-state",
            lambda payload: payload.pop(prefix + "STATE.json"),
        )
        outcome(
            "L",
            "mandatory bundle evidence",
            "remove subject STATE.json",
            "missing required checkpoint artifact: STATE.json",
            missing,
        )

        traversal = write_bundle(
            "traversal",
            lambda payload: payload.__setitem__("../escape", b"refused"),
        )
        outcome("M", "archive path safety", "add a traversal member", "unsafe archive member", traversal)

        probe_bundle = write_bundle(
            "secret",
            lambda payload: payload.__setitem__(
                "repository/docs/ordinary.txt",
                ("gh" + "p_" + "x" * 20).encode("utf-8"),
            ),
        )
        outcome(
            "N",
            "bundle secret scan",
            "add canonical credential-shaped bytes",
            "secret scan found",
            probe_bundle,
        )

        duplicate_name = "repository/docs/control.md"
        duplicate = write_bundle("duplicate", duplicate=duplicate_name)
        outcome("O", "archive uniqueness", "duplicate a member name", "duplicate member names", duplicate)

    reports = {
        "recovery": root / "var" / "quality-recovery.json",
        "cancellation": root / "var" / "quality-cancellation.json",
        "timeout": root / "var" / "quality-timeout.json",
        "forged-origin": root / "var" / "sandbox-tool-result-origin.json",
        "secret-output": root / "var" / "quality-secret-output.json",
    }
    observed: dict[str, str] = {}
    for name, path in reports.items():
        try:
            document = json.loads(path.read_text(encoding="utf-8"))
            observed[name] = str(document.get("result"))
        except (OSError, json.JSONDecodeError):
            observed[name] = "MISSING"
    defended = all(value == "PASS" for value in observed.values())
    record(
        "P",
        "live adverse lifecycle",
        "execute restart, cancellation, timeout and forged-origin scenarios",
        "every fail-closed invariant survives in the current verifier run",
        defended,
        "; ".join(f"{name}={value}" for name, value in observed.items()),
        [
            "file:scripts/iacode/scenarios/quality_engine_e2e.py",
            "file:scripts/iacode/scenarios/sandbox_coding_e2e.py",
            "file:scripts/iacode/verify.py",
        ],
    )

    with tempfile.TemporaryDirectory(prefix="gate4-red-team-transport-") as temporary:
        clone = Path(temporary) / "repository"
        cloned = subprocess.run(
            ["git", "clone", "--quiet", "--no-local", str(root), str(clone)],
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        detached = subprocess.run(
            ["git", "checkout", "--quiet", "--detach", "HEAD"],
            cwd=clone,
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        ) if cloned.returncode == 0 else cloned
        status = subprocess.run(
            ["git", "status", "--porcelain=v1", "--untracked-files=all"],
            cwd=root,
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        copied = cloned.returncode == 0 and detached.returncode == 0 and status.returncode == 0
        if copied:
            for line in status.stdout.splitlines():
                if len(line) < 4:
                    continue
                relative = Path(line[3:].split(" -> ")[-1])
                source = root / relative
                destination = clone / relative
                if source.is_file():
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source, destination)
                elif destination.exists():
                    destination.unlink()
        from review_bundle import resolve_complete_checkpoint

        complete_checkpoint = resolve_complete_checkpoint(root, "HEAD", checkpoint)
        checkpoint_relative = complete_checkpoint.relative_to(root)
        first_bundle = Path(".git") / "gate4-red-team-review-first.zip"
        second_bundle = Path(".git") / "gate4-red-team-review-second.zip"

        def rebuild(bundle: Path) -> subprocess.CompletedProcess[str]:
            return subprocess.run(
                [
                    sys.executable,
                    str(clone / "scripts" / "development-ledger" / "review_bundle.py"),
                    "--root",
                    str(clone),
                    "--checkpoint",
                    str(checkpoint_relative),
                    "--bundle",
                    str(bundle),
                    "--subject",
                    "HEAD",
                ],
                cwd=clone,
                text=True,
                encoding="utf-8",
                errors="replace",
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
            )

        first = rebuild(first_bundle) if copied else cloned
        second = rebuild(second_bundle) if copied else cloned
        first_path = clone / first_bundle
        second_path = clone / second_bundle
        deterministic = (
            first.returncode == 0
            and second.returncode == 0
            and first_path.is_file()
            and second_path.is_file()
            and hashlib.sha256(first_path.read_bytes()).digest()
            == hashlib.sha256(second_path.read_bytes()).digest()
        )
        portable = first.returncode == 0 and second.returncode == 0
        categories = portable and "REVIEW_BUNDLE=PASS" in first.stdout and "REVIEW_BUNDLE=PASS" in second.stdout
        declaration_valid = False
        stale_declaration_refused = False
        if deterministic and categories:
            subject_commit = subprocess.run(
                ["git", "rev-parse", "HEAD"], cwd=clone, text=True, encoding="utf-8",
                errors="replace", stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False,
            ).stdout.strip()
            subject_tree = subprocess.run(
                ["git", "rev-parse", "HEAD^{tree}"], cwd=clone, text=True, encoding="utf-8",
                errors="replace", stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False,
            ).stdout.strip()
            with zipfile.ZipFile(first_path) as archive:
                entry_count = len(archive.namelist())
            digest = hashlib.sha256(first_path.read_bytes()).hexdigest()
            reconstruction = {
                "mode": "git-clone-no-local-detached",
                "subjectCommit": subject_commit,
                "subjectTree": subject_tree,
                "sha256": [digest, digest],
                "sizeBytes": [first_path.stat().st_size, second_path.stat().st_size],
                "entries": [entry_count, entry_count],
                "validationResults": ["PASS", "PASS"],
                "byteIdentical": True,
                "result": "PASS",
            }
            declaration = declaration_from_reconstruction(
                clone, clone / checkpoint_relative, first_path, reconstruction)
            declaration_valid = verify_declaration(
                clone, clone / checkpoint_relative, declaration, reconstruction)["result"] == "PASS"
            stale = json.loads(json.dumps(declaration))
            stale["sha256"] = "0" * 64
            stale_declaration_refused = verify_declaration(
                clone, clone / checkpoint_relative, stale, reconstruction)["result"] == "FAIL"
        record(
            "T",
            "review bundle portability, determinism and declaration binding",
            "rebuild twice from a detached transport clone, validate there and mutate the declaration",
            "byte-identical secret-clean rebuilds match the declaration and a stale digest is refused",
            deterministic and portable and categories and declaration_valid and stale_declaration_refused,
            f"deterministic={deterministic}; portable={portable}; categories={categories}; "
            f"declaration={declaration_valid}; stale-refused={stale_declaration_refused}",
            ["file:scripts/development-ledger/review_bundle.py"],
        )
    return attacks


def run_in_image(root: Path, rebuild: bool) -> dict[str, Any]:
    if rebuild:
        built = _compose(root, "build", "evaluator")
        if built.returncode != 0:
            raise LedgerError("evaluator rebuild failed: " + built.stdout[-1200:])
    script = Path(__file__).resolve()
    completed = _compose(
        root,
        "run",
        "--rm",
        "--no-deps",
        "--entrypoint",
        "",
        "--volume",
        f"{script.as_posix()}:/app/gate4-red-team.py:ro",
        "evaluator",
        "python",
        "/app/gate4-red-team.py",
        "--in-image",
    )
    if completed.returncode != 0:
        raise LedgerError("Gate 4 Red Team image harness failed: " + completed.stdout[-1600:])
    for line in reversed(completed.stdout.splitlines()):
        if line.strip().startswith("{"):
            return json.loads(line)
    raise LedgerError("Gate 4 Red Team image harness returned no report")


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Internal Red Team — GATE 4 — QUALITY ENGINE",
        "",
        f"Result: `{report['result']}`",
        "",
        f"- Baseline control: `{report['baselineControl']['result']}`",
        f"- Attacks defended: {report['defended']}/{report['total']}",
        "",
        "| Attack | Target | Mutation | Expected | Observed | Result |",
        "|---|---|---|---|---|---|",
    ]
    for attack in report["attacks"]:
        observed = attack["observed"].replace("|", "\\|").replace("\n", " ")
        lines.append(
            f"| `{attack['attackId']}` | {attack['target']} | {attack['mutation']} | "
            f"{attack['expectedDefense']} | {observed} | `{attack['result']}` |"
        )
    return "\n".join(lines) + "\n"


def main() -> int:
    if "--in-image" not in sys.argv:
        use_utf8_stdout()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path)
    parser.add_argument("--checkpoint", type=Path)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--skip-gate-rebuild", action="store_true")
    parser.add_argument("--execute-output-boundary-proof", action="store_true")
    parser.add_argument("--in-image", action="store_true", help=argparse.SUPPRESS)
    arguments = parser.parse_args()
    if arguments.in_image:
        report = _in_image_battery()
        print(json.dumps(report, separators=(",", ":")))
        return 0 if report["baselineControl"]["result"] == "VALID" and not report["escaped"] else 1

    root = find_root(arguments.root) if arguments.root else find_root()
    checkpoint = arguments.checkpoint or resolve_latest(root)
    if not checkpoint.is_absolute():
        checkpoint = root / checkpoint
    if arguments.execute_output_boundary_proof:
        proof = subprocess.run(
            [sys.executable, "scripts/iacode/scenarios/quality_engine_e2e.py", "--scenario",
             "secret-output", "--skip-build", "--report", "var/quality-secret-output.json"],
            cwd=root, check=False,
        )
        if proof.returncode:
            print("RED_TEAM_FAIL: live output-boundary proof did not pass")
            return proof.returncode
    observed = run_in_image(root, rebuild=not arguments.skip_gate_rebuild)
    attacks = observed["attacks"] + _host_attacks(root, checkpoint)
    order = {identifier: index for index, identifier in enumerate("ABCDEFGHIJKLMNOPQRST")}
    attacks.sort(key=lambda item: order[str(item["attackId"])])
    escaped = [item for item in attacks if item["result"] == "ESCAPED"]
    observed = {
        **observed,
        "attacks": attacks,
        "escaped": len(escaped),
        "defended": len(attacks) - len(escaped),
        "total": len(attacks),
    }
    report = {
        "schemaVersion": "1.1.0",
        "checkpoint": checkpoint.name,
        "generatedAt": utc_now(),
        "targetFingerprint": scope_fingerprint(root),
        "source": SOURCE,
        **observed,
        "mandatoryTotal": observed["total"],
        "mandatoryDefended": observed["defended"],
        "result": (
            "RED_TEAM_PASS"
            if observed["baselineControl"]["result"] == "VALID" and not observed["escaped"]
            else "RED_TEAM_FAIL"
        ),
    }
    if arguments.write:
        write_json(checkpoint / "M2-INTERNAL-RED-TEAM.json", report)
        (checkpoint / "RED-TEAM-REPORT.md").write_text(
            render_markdown(report), encoding="utf-8", newline="\n"
        )
    for attack in report["attacks"]:
        print(f"[{attack['result']}] {attack['attackId']} {attack['target']}: {attack['observed']}")
    print(
        f"RED_TEAM={report['result']} {report['defended']}/{report['total']} "
        f"control={report['baselineControl']['result']}"
    )
    return 0 if report["result"] == "RED_TEAM_PASS" else 1


if __name__ == "__main__":
    if "--in-image" in sys.argv:
        sys.exit(main())
    try:
        sys.exit(main())
    except LedgerError as error:
        print(f"LEDGER_ERROR: {error}")
        sys.exit(2)
