#!/usr/bin/env python3
"""Real consented Experience Store lifecycle against a separately owned authenticated stack."""

from __future__ import annotations

import argparse
import base64
import hashlib
import hmac
import http.client
import json
import os
import re
import secrets
import subprocess
import sys
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta
from pathlib import Path
from urllib.parse import urlsplit


def checked_report_path(value: Path) -> Path:
    root = Path(__file__).resolve().parents[3]
    runtime = root / "var"
    candidate = value if value.is_absolute() else root / value
    if runtime.is_symlink() or runtime.is_junction() or candidate.is_symlink():
        raise ValueError("redirected experience proof report refused")
    resolved = candidate.resolve()
    if not resolved.is_relative_to(runtime.resolve()) or resolved.suffix != ".json":
        raise ValueError("experience report must remain under this checkout's var directory")
    return resolved


def retire_before_imports(arguments: list[str]) -> None:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--report", type=Path, default=Path("var/experience-store-e2e.json"))
    options, _ = parser.parse_known_args(arguments)
    checked_report_path(options.report).unlink(missing_ok=True)


if __name__ == "__main__" and not {"-h", "--help"}.intersection(sys.argv[1:]):
    retire_before_imports(sys.argv[1:])

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "development-ledger"))

from compose import (
    REPOSITORY_ROOT,
    StackError,
    compose,
    log,
    published_port,
    read_env_file,
    wait_for_health,
)
from desktop_test_support import (
    PROTOCOL,
    InterruptedResponseProxy,
    environment,
    manifest,
    request,
    restarted_api_endpoint,
    scalar,
    synchronize_authorized_model,
    wait,
)
from desktop_test_support import (
    operation as protocol_operation,
)
from iacode_common.desktop_auth import response_signature, signed_headers
from iacode_common.secret_scanning import find_secret_kinds
from ledger_common import git_snapshot, scope_fingerprint, use_utf8_stdout
from verify import VERIFICATION_PORT_VARIABLES

TASK = (
    "Use the provided immutable workspace. Inspect calculator.py and test_calculator.py. "
    "In the run sandbox execute python -m unittest -v and report its actual result. "
    "Source is already correct: do not change files or dependencies, contact a network or open "
    "an external path. Finish concisely. Never claim tests ran without executing them."
)
TERMINAL = {"SUCCEEDED", "FAILED", "CANCELLED"}
QUALITY_TERMINAL = TERMINAL | {"TIMED_OUT", "INVALID"}


def docker(*arguments: str) -> str:
    result = subprocess.run(
        ["docker", *arguments],
        cwd=REPOSITORY_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=60,
        check=False,
    )
    if result.returncode:
        raise StackError("owned experience engine observation failed")
    return result.stdout.strip()


def record(report: dict, name: str, ok: bool, **facts) -> None:
    if {"name", "result"} & set(facts):
        raise ValueError("facts cannot replace a measured control identity/result")
    report["steps"].append({"name": name, "result": "PASS" if ok else "FAIL", **facts})
    log(f"EXPERIENCE {'PASS' if ok else 'FAIL'} {name}")
    if not ok:
        raise StackError("experience live control failed: " + name)


def operation(base: str, key: str, name: str, arguments: dict) -> tuple[int, dict]:
    status, envelope = protocol_operation(base, key, name, arguments)
    if status == 200:
        if (
            envelope.get("version") != PROTOCOL["version"]
            or envelope.get("operation") != name
            or not isinstance(envelope.get("data"), dict)
        ):
            raise StackError("actual desktop source response envelope is invalid")
        return status, envelope["data"]
    return status, envelope


def cleanup_owned_sandboxes(project: str) -> dict:
    if not re.fullmatch(r"iacode-experience-[0-9a-f]{12}", project):
        raise ValueError("unowned experience sandbox namespace refused")
    labels = (
        "--filter",
        "label=org.iacode.sandbox=1",
        "--filter",
        "label=org.iacode.sandbox.owner=" + project,
    )
    for kind in ("container", "network"):
        identifiers = docker(
            kind, "ls", "-aq" if kind == "container" else "-q", "--no-trunc", *labels
        ).splitlines()
        for identifier in identifiers:
            if not re.fullmatch(r"[0-9a-f]{64}", identifier):
                raise StackError("owned sandbox engine identity is invalid")
            value = json.loads(docker(kind, "inspect", identifier))[0]
            actual = (
                value.get("Config", {}).get("Labels", {})
                if kind == "container"
                else value.get("Labels", {})
            )
            if (
                actual.get("org.iacode.sandbox") != "1"
                or actual.get("org.iacode.sandbox.owner") != project
            ):
                raise StackError("owned experience sandbox label changed")
            docker(kind, "rm", *(["--force"] if kind == "container" else []), identifier)
    return {
        "remainingContainers": len(docker("container", "ls", "-aq", *labels).splitlines()),
        "remainingNetworks": len(docker("network", "ls", "-q", *labels).splitlines()),
    }


def adverse_transport(
    base: str, key: str, target: str, *, stale: bool = False, invalid: bool = False
) -> tuple[int, dict]:
    headers = signed_headers(
        key,
        "GET",
        target,
        names=PROTOCOL["headers"],
        version=PROTOCOL["version"],
        timestamp=int(time.time()) - 120 if stale else None,
    )
    if invalid:
        name = PROTOCOL["headers"]["signature"]
        headers[name] = ("0" if headers[name][0] != "0" else "1") + headers[name][1:]
    url = urlsplit(base)
    connection = http.client.HTTPConnection(url.hostname, url.port, timeout=30)
    try:
        connection.request("GET", target, headers=headers)
        response = connection.getresponse()
        body = response.read(65537)
        if len(body) > 65536:
            raise StackError("adverse response exceeds bound")
        expected = response_signature(
            key,
            headers[PROTOCOL["headers"]["requestId"]],
            response.status,
            body,
            version=PROTOCOL["version"],
        )
        if not hmac.compare_digest(
            expected, response.getheader(PROTOCOL["headers"]["signature"], "")
        ):
            raise StackError("adverse response authentication failed")
        return response.status, json.loads(body)
    finally:
        connection.close()


def terminal(base: str, key: str, identifier: str, *, quality: bool = False) -> dict:
    def probe():
        status, value = operation(
            base, key, "quality-read" if quality else "read", {"runId": identifier}
        )
        if status != 200:
            raise StackError("actual source observation failed")
        state = value["run"]["state"] if quality else value["state"]
        return value if state in (QUALITY_TERMINAL if quality else TERMINAL) else None

    return wait(
        "actual completed quality" if quality else "actual completed task", probe, seconds=600
    )


def source_adversary(artifact_id: str, mode: str) -> dict:
    uuid.UUID(artifact_id)
    owner = os.environ.get("COMPOSE_PROJECT_NAME", "")
    if not re.fullmatch(r"iacode-experience-[0-9a-f]{12}", owner):
        raise StackError("source adversary requires the exact owned live-proof namespace")
    api = compose("ps", "-q", "api", merge_stderr=False)
    container_id = api.stdout.strip()
    if not api.ok or not re.fullmatch(r"[0-9a-f]{64}", container_id):
        raise StackError("owned source adversary API identity is unavailable")
    labels = json.loads(docker("inspect", container_id))[0].get("Config", {}).get("Labels", {})
    if labels.get("com.docker.compose.project") != owner:
        raise StackError("source adversary ownership changed")
    source = (
        REPOSITORY_ROOT / "scripts/iacode/scenarios/experience_source_adversary.py"
    ).read_text(encoding="utf-8")
    result = compose(
        "exec",
        "-T",
        "api",
        "python",
        "-c",
        source,
        artifact_id,
        mode,
        merge_stderr=False,
        timeout=60,
    )
    if not result.ok:
        raise StackError("owned source adversary failed")
    value = json.loads(result.stdout)
    if value.get("mode") != mode or value.get("result") != "APPLIED":
        raise StackError("owned source adversary receipt is invalid")
    return value


def exercise(base: str, key: str, model: str, project: str, report: dict) -> None:
    catalog = synchronize_authorized_model(base, key, model)
    record(report, "exact-authorized-provider-model-discovered", True, **catalog)
    fixture = REPOSITORY_ROOT / "services/evaluator/tests/fixtures/python-pass"
    files = [
        {"path": name, "content": (fixture / name).read_text(encoding="utf-8")}
        for name in ("calculator.py", "test_calculator.py", "pyproject.toml")
    ]
    status, snapshot = operation(
        base, key, "snapshot", {"files": files, "manifestDigest": manifest(files)}
    )
    record(
        report,
        "actual-authorized-snapshot-stored",
        status == 200 and snapshot.get("trainingAllowed") is False,
    )
    status, created = operation(
        base,
        key,
        "start",
        {
            "snapshotId": snapshot["snapshotId"],
            "task": TASK,
            "team": "coding",
            "model": model,
            "idempotencyKey": str(uuid.uuid4()),
        },
    )
    record(report, "actual-governed-task-created", status == 200 and bool(created.get("runId")))
    run_id = created["runId"]
    task = terminal(base, key, run_id)
    record(
        report,
        "actual-provider-sandbox-task-completed",
        task["state"] == "SUCCEEDED"
        and task["budget"]["modelCallsUsed"] > 0
        and bool(task["toolExecutions"]),
        sourceRunId=run_id,
    )
    status, quality = operation(
        base,
        key,
        "quality-start",
        {
            "snapshotId": snapshot["snapshotId"],
            "snapshotDigest": snapshot["snapshotDigest"],
            "idempotencyKey": str(uuid.uuid4()),
        },
    )
    record(report, "actual-quality-workflow-created", status == 200 and bool(quality.get("runId")))
    quality_id = quality["runId"]
    quality_result = terminal(base, key, quality_id, quality=True)
    record(
        report,
        "actual-derived-quality-pass-with-evidence",
        quality_result["verdict"]["verdict"] == "PASS" and bool(quality_result["evidence"]),
        qualityRunId=quality_id,
    )
    source_target = "/api/v1/experiences/sources/" + run_id
    status, candidate = request(base, key, "GET", source_target)
    record(
        report,
        "authenticated-project-source-discovery",
        status == 200
        and candidate["taskRunId"] == run_id
        and candidate["storageConsentRequired"] is True,
    )
    project_id = candidate["projectId"]
    root = "/api/v1/experiences/projects/" + project_id
    payload = {
        "taskRunId": run_id,
        "qualityRunId": quality_id,
        "storageConsent": True,
        "idempotencyKey": str(uuid.uuid4()),
        "retentionSeconds": 600,
    }
    record(
        report,
        "fresh-experience-store-empty-premise",
        scalar("SELECT count(*) FROM experiences;") == 0,
    )
    status, refused = request(base, key, "POST", root, payload, authenticated=False)
    record(
        report,
        "unauthenticated-capture-refused-before-effects",
        status == 401
        and refused["code"] == "AUTHENTICATION_REQUIRED"
        and scalar("SELECT count(*) FROM experiences;") == 0,
    )
    for name, options, code in (
        ("invalid-signature", {"invalid": True}, "AUTHENTICATION_INVALID"),
        ("stale-authentication", {"stale": True}, "AUTHENTICATION_STALE"),
    ):
        status, refused = adverse_transport(base, key, source_target, **options)
        record(report, name + "-refused", status == 401 and refused.get("code") == code)
    marker = "gh" + "p_" + "q" * 24
    record(report, "canonical-secret-adverse-premise", bool(find_secret_kinds(marker)))
    attacks = (
        (
            "consent-missing",
            {k: v for k, v in payload.items() if k != "storageConsent"},
            "CONSENT_MISSING",
        ),
        ("consent-denied", {**payload, "storageConsent": False}, "CONSENT_DENIED"),
        ("consent-type", {**payload, "storageConsent": 1}, "CONSENT_TYPE_INVALID"),
        (
            "private-transcript",
            {**payload, "privateReasoning": "not an observable source fact"},
            "CAPTURE_CONTRACT_INVALID",
        ),
        ("forged-verdict", {**payload, "verdict": "PASS"}, "CAPTURE_CONTRACT_INVALID"),
        ("forged-rights", {**payload, "trainingAllowed": True}, "CAPTURE_CONTRACT_INVALID"),
        ("secret-ingress", {**payload, "annotation": marker}, "SECRET_MATERIAL_REFUSED"),
    )
    for name, value, code in attacks:
        status, refused = request(base, key, "POST", root, value)
        record(
            report,
            name + "-refused-before-persistence",
            status == 400
            and refused.get("code") == code
            and scalar("SELECT count(*) FROM experiences;") == 0,
        )
    for index, form in enumerate(
        (
            key,
            key.upper(),
            base64.b64encode(key.encode()).decode(),
            key.encode().hex(),
            "".join(f"%{value:02x}" for value in key.encode()),
            "".join(f"\\u{value:04x}" for value in key.encode()),
        )
    ):
        status, refused = request(base, key, "POST", root, {**payload, "annotation": form})
        record(
            report,
            f"known-capability-form-{index}-refused-before-persistence",
            status == 400
            and refused.get("code") == "AUTHENTICATION_MATERIAL_REFUSED"
            and scalar("SELECT count(*) FROM experiences;") == 0,
        )
    wrong_root = "/api/v1/experiences/projects/" + str(uuid.uuid4())
    status, refused = request(base, key, "POST", wrong_root, payload)
    record(
        report,
        "cross-project-source-capture-refused",
        status == 404
        and refused.get("code") == "SOURCE_NOT_FOUND"
        and scalar("SELECT count(*) FROM experiences;") == 0,
    )
    replay_id = str(uuid.uuid4())
    status, _ = request(base, key, "GET", source_target, request_id=replay_id)
    record(report, "authentication-null-control", status == 200)
    status, refused = request(base, key, "GET", source_target, request_id=replay_id)
    record(
        report,
        "actual-redis-authentication-replay-refused",
        status == 409 and refused.get("code") == "AUTHENTICATION_REPLAY",
    )
    proxy = InterruptedResponseProxy(
        base, drop_operation="experience-capture", experience_project=project_id
    )
    try:
        lost = False
        try:
            request(proxy.base, key, "POST", root, payload)
        except (http.client.RemoteDisconnected, ConnectionResetError):
            lost = True
        record(
            report,
            "actual-accepted-experience-response-loss-one-durable-effect",
            lost
            and proxy.dropped
            and proxy.accepted_status == 201
            and proxy.counts["experience-capture"] == 1
            and scalar("SELECT count(*) FROM experiences;") == 1
            and scalar("SELECT count(*) FROM experience_events WHERE kind='CAPTURED';") == 1,
            responseLost=lost,
            upstreamStatuses=list(proxy.upstream_statuses),
            upstreamCode=proxy.upstream_code,
            actualExperienceRows=scalar("SELECT count(*) FROM experiences;"),
            actualCaptureAuditRows=scalar(
                "SELECT count(*) FROM experience_events WHERE kind='CAPTURED';"
            ),
        )
        accepted_id = proxy.accepted_experience
        accepted_expiry = proxy.accepted_expires_at
        accepted_digest = proxy.accepted_content_digest
    finally:
        proxy.close()
    # Explicit test-operator replay of the exact original identity, never an automatic new-key
    # client retry. Only actual persisted data can recover the response that was lost.
    status, captured = request(base, key, "POST", root, payload)
    record(
        report,
        "actual-source-bound-experience-captured",
        status == 200
        and captured["state"] == "ACTIVE"
        and captured["idempotentReplay"] is True
        and captured["experienceId"] == accepted_id
        and captured["expiresAt"] == accepted_expiry
        and captured["contentDigest"] == accepted_digest,
    )
    document = captured["document"]
    actual_digest = hashlib.sha256(
        json.dumps(document, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode(
            "utf-8"
        )
    ).hexdigest()
    record(
        report,
        "consumer-recomputed-returned-document-digest",
        actual_digest == captured["contentDigest"],
    )
    record(
        report,
        "observed-provider-tool-quality-and-denied-reuse-lineage",
        document["task"]["runId"] == run_id
        and bool(document["provider"])
        and bool(document["model"])
        and any(row["sessionId"] and row["tool"] == "shell.exec" for row in document["toolCalls"])
        and bool(document["commands"])
        and document["quality"]["runId"] == quality_id
        and document["quality"]["verdict"] == "PASS"
        and document["files"]["snapshotId"] == snapshot["snapshotId"]
        and document["effort"] is document["repository"] is document["baseCommit"] is None
        and document["humanReview"] is document["agentReview"] is None
        and all(
            row["storageAllowed"] is True
            and row["ragAllowed"] is False
            and row["trainingAllowed"] is False
            and row["distillationAllowed"] is False
            for row in document["provenance"]
        ),
    )
    report["capturedExperience"] = captured
    target = root + "/" + captured["experienceId"]
    with ThreadPoolExecutor(max_workers=4) as pool:
        retries = list(pool.map(lambda _: request(base, key, "POST", root, payload), range(4)))
    record(
        report,
        "actual-concurrent-retry-one-row-one-capture-audit",
        all(
            status == 200
            and row["experienceId"] == captured["experienceId"]
            and row["expiresAt"] == captured["expiresAt"]
            and row["idempotentReplay"] is True
            for status, row in retries
        )
        and scalar("SELECT count(*) FROM experiences;") == 1
        and scalar("SELECT count(*) FROM experience_events WHERE kind='CAPTURED';") == 1,
    )
    for suffix in ("", "/export"):
        status, viewed = request(base, key, "GET", target + suffix)
        record(
            report,
            "actual-verified-" + ("export" if suffix else "read"),
            status == 200
            and viewed["contentDigest"] == captured["contentDigest"]
            and viewed["document"] == document,
        )
    status, page = request(base, key, "GET", root + "?limit=1")
    record(
        report,
        "actual-bounded-summary-pagination",
        status == 200
        and len(page["experiences"]) == 1
        and "document" not in page["experiences"][0]
        and bool(page["nextCursor"]),
    )
    status, exhausted = request(base, key, "GET", root + "?cursor=" + page["nextCursor"])
    record(
        report, "actual-project-cursor-resumption", status == 200 and exhausted["experiences"] == []
    )
    status, _ = request(base, key, "GET", wrong_root + "?cursor=" + page["nextCursor"])
    record(report, "cross-project-cursor-refused", status == 400)
    for method in ("GET", "DELETE"):
        status, _ = request(base, key, method, wrong_root + "/" + captured["experienceId"])
        record(report, "cross-project-" + method.lower() + "-refused", status == 404)
    for use in ("rag", "training", "distillation", "unknown"):
        status, refused = request(base, key, "GET", target + "?use=" + use)
        record(
            report,
            "denied-" + use + "-use-no-data",
            status == 403
            and refused.get("code") == "REUSE_PERMISSION_DENIED"
            and "document" not in refused,
        )
    status, refused = request(base, key, "POST", root, {**payload, "retentionSeconds": 601})
    record(
        report,
        "conflicting-stable-request-refused",
        status == 409 and refused.get("code") == "REQUEST_CONFLICT",
    )
    restarted = compose("restart", "api", timeout=90)
    record(report, "actual-api-restarted", restarted.ok)
    wait_for_health(["api"], timeout=120)
    base = restarted_api_endpoint(key)
    status, resumed = request(base, key, "POST", root, payload)
    record(
        report,
        "restart-preserves-content-rights-original-expiry-and-retry",
        status == 200
        and resumed["experienceId"] == captured["experienceId"]
        and resumed["expiresAt"] == captured["expiresAt"]
        and resumed["document"] == document,
    )
    status, refused = request(base, key, "GET", source_target, request_id=replay_id)
    record(
        report,
        "authentication-replay-survives-real-restart",
        status == 409 and refused.get("code") == "AUTHENTICATION_REPLAY",
    )
    artifact_id = next(
        row["sourceId"] for row in document["provenance"] if row["sourceType"] == "quality-evidence"
    )
    for mode, expected, code in (
        ("corrupt", 400, "SOURCE_OBJECT_CORRUPT"),
        ("remove", 503, "SOURCE_OBJECT_UNAVAILABLE"),
    ):
        receipt = source_adversary(artifact_id, mode)
        try:
            status, refused = request(base, key, "GET", target + "/export")
            record(
                report,
                "actual-source-object-" + mode + "-fails-closed",
                status == expected and refused.get("code") == code and "document" not in refused,
                artifactId=receipt["artifactId"],
                sourceDigest=receipt["originalDigest"],
            )
        finally:
            source_adversary(artifact_id, "restore")
        status, clean = request(base, key, "GET", target)
        record(
            report,
            "restored-source-clean-control-after-" + mode,
            status == 200
            and clean["contentDigest"] == captured["contentDigest"]
            and clean["document"] == document,
        )
    source_counts = {
        table: scalar(f"SELECT count(*) FROM {table};")
        for table in ("task_runs", "quality_runs", "artifacts")
    }
    status, removed = request(base, key, "DELETE", target)
    record(
        report, "actual-project-bound-withdrawal", status == 200 and removed["state"] == "DELETED"
    )
    status, again = request(base, key, "DELETE", target)
    record(
        report, "repeated-withdrawal-is-terminal-observation", status == 200 and again == removed
    )
    status, refused = request(base, key, "GET", target)
    record(report, "withdrawn-read-denied-immediately", status == 410 and "document" not in refused)
    status, refused = request(
        base, key, "POST", root, {**payload, "idempotencyKey": str(uuid.uuid4())}
    )
    record(
        report,
        "new-key-cannot-resurrect-withdrawn-source",
        status == 409 and refused.get("code") == "SOURCE_CONFLICT",
    )
    record(
        report,
        "withdrawal-physically-purges-primary-and-preserves-sources",
        scalar(
            "SELECT count(*) FROM experiences WHERE state='DELETED' "
            "AND body='{}'::jsonb AND summary='' AND NOT storage_allowed;"
        )
        == 1
        and all(
            scalar(f"SELECT count(*) FROM {table};") == count
            for table, count in source_counts.items()
        ),
    )
    status, second = operation(
        base,
        key,
        "start",
        {
            "snapshotId": snapshot["snapshotId"],
            "task": TASK,
            "team": "coding",
            "model": model,
            "idempotencyKey": str(uuid.uuid4()),
        },
    )
    record(
        report, "second-real-governed-source-created", status == 200 and bool(second.get("runId"))
    )
    operation(base, key, "cancel", {"runId": second["runId"]})
    second_result = terminal(base, key, second["runId"])
    status, second_source = request(
        base, key, "GET", "/api/v1/experiences/sources/" + second["runId"]
    )
    second_root = "/api/v1/experiences/projects/" + second_source["projectId"]
    expiration_payload = {
        "taskRunId": second["runId"],
        "storageConsent": True,
        "idempotencyKey": str(uuid.uuid4()),
        "retentionSeconds": 1,
    }
    status, expiring = request(base, key, "POST", second_root, expiration_payload)
    record(
        report,
        "actual-short-retention-capture-honest-observed-outcome",
        status == 201
        and expiring["document"]["task"]["status"] == second_result["state"]
        and expiring["document"]["quality"] is None,
        observedSourceState=second_result["state"],
    )
    expiration_target = second_root + "/" + expiring["experienceId"]
    wait(
        "immediate real-clock expiry denial",
        lambda: request(base, key, "GET", expiration_target)[0] == 410,
        seconds=15,
    )
    record(report, "expired-read-denied-without-manual-sweep", True)
    wait(
        "owned automatic physical primary purge",
        lambda: (
            scalar(
                "SELECT count(*) FROM experiences WHERE id='"
                + expiring["experienceId"]
                + "' AND state='EXPIRED' AND body='{}'::jsonb "
                "AND summary='' AND NOT storage_allowed;"
            )
            == 1
        ),
        seconds=90,
    )
    record(report, "actual-owned-background-sweeper-physically-purged", True)
    status, refused = request(base, key, "POST", second_root, expiration_payload)
    record(report, "expired-request-retry-cannot-renew", status == 410)
    status, refused = request(
        base, key, "POST", second_root, {**expiration_payload, "idempotencyKey": str(uuid.uuid4())}
    )
    record(
        report,
        "expired-source-new-key-cannot-resurrect",
        status == 409 and refused.get("code") == "SOURCE_CONFLICT",
    )
    # Force untrusted path/query and correlation input through actual production access logging.
    request(base, key, "GET", root + "/" + key + "?untrusted=" + key)
    logs = compose("logs", "--no-color", "api", merge_stderr=False, timeout=30)
    combined = logs.stdout + logs.stderr
    record(
        report,
        "actual-production-logs-retain-observability-not-ingress",
        logs.ok
        and key not in combined
        and marker not in combined
        and "/api/v1/experiences/<scoped>" in combined
        and "experience retention sweep completed" in combined,
    )
    with environment(
        {"IACODE_DESKTOP_TOKEN_EXPIRES_AT": (datetime.now(UTC) - timedelta(seconds=60)).isoformat()}
    ):
        recreated = compose("up", "-d", "--no-deps", "--force-recreate", "api", timeout=90)
        record(report, "owned-capability-expiry-reconfiguration", recreated.ok)
        wait_for_health(["api"], timeout=120)
        expired_base = f"http://127.0.0.1:{published_port('api', 8000)}"
        status, refused = adverse_transport(expired_base, key, source_target)
        record(
            report,
            "actual-expired-capability-refuses-experience-access",
            status == 401 and refused.get("code") == "AUTHENTICATION_EXPIRED",
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--report", type=Path, default=REPOSITORY_ROOT / "var/experience-store-e2e.json"
    )
    args = parser.parse_args()
    args.report = checked_report_path(args.report)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.unlink(missing_ok=True)
    snapshot = git_snapshot(REPOSITORY_ROOT)
    report = {
        "schemaVersion": "1.0.0",
        "scenario": "experience-store-e2e",
        "result": "FAIL",
        "environment": "owned-authenticated-real-postgresql-redis-minio-"
        "temporal-provider-sandbox-quality",
        "subjectCommit": snapshot["head"],
        "sourceDirty": snapshot["dirty"],
        "sourceFingerprint": scope_fingerprint(REPOSITORY_ROOT),
        "steps": [],
    }
    project = "iacode-experience-" + uuid.uuid4().hex[:12]
    report["composeProject"] = project
    before = set(docker("ps", "-aq", "--no-trunc").splitlines())
    values = read_env_file()
    model = os.environ.get("IACODE_GATEWAY_SMOKE_MODEL") or values.get("IACODE_GATEWAY_SMOKE_MODEL")
    key = secrets.token_hex(32)
    owned = {
        "COMPOSE_PROJECT_NAME": project,
        **dict.fromkeys(VERIFICATION_PORT_VARIABLES, "0"),
        "IACODE_DESKTOP_TOKEN": key,
        "IACODE_DESKTOP_TOKEN_EXPIRES_AT": (datetime.now(UTC) + timedelta(hours=2)).isoformat(),
        "IACODE_GATEWAY_DEFAULT_MODEL": model or "",
    }
    try:
        if not model:
            raise StackError("an explicit actual authorized smoke model is required; no substitute")
        with environment(owned):
            if docker("ps", "-aq", "--filter", "label=com.docker.compose.project=" + project):
                raise StackError("fresh owned experience namespace collision")
            try:
                images = subprocess.run(
                    [sys.executable, "scripts/iacode/sandbox_image.py"],
                    cwd=REPOSITORY_ROOT,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    check=False,
                )
                record(report, "current-sandbox-and-quality-images-built", images.returncode == 0)
                started = compose("up", "-d", "--build", timeout=600)
                record(report, "fresh-owned-authenticated-stack-started", started.ok)
                wait_for_health(timeout=300)
                record(report, "fresh-owned-authenticated-stack-healthy", True)
                exercise(
                    f"http://127.0.0.1:{published_port('api', 8000)}", key, model, project, report
                )
            finally:
                removed = compose("down", "--volumes", "--remove-orphans", timeout=180)
                report["sandboxCleanup"] = cleanup_owned_sandboxes(project)
                report["cleanup"] = {
                    "composeExitCode": removed.exit_code,
                    "remainingContainers": len(
                        docker(
                            "ps", "-aq", "--filter", "label=com.docker.compose.project=" + project
                        ).splitlines()
                    ),
                    "remainingVolumes": len(
                        docker(
                            "volume",
                            "ls",
                            "-q",
                            "--filter",
                            "label=com.docker.compose.project=" + project,
                        ).splitlines()
                    ),
                    "remainingNetworks": len(
                        docker(
                            "network",
                            "ls",
                            "-q",
                            "--filter",
                            "label=com.docker.compose.project=" + project,
                        ).splitlines()
                    ),
                }
        record(
            report,
            "owned-resources-removed",
            report["cleanup"]
            == {
                "composeExitCode": 0,
                "remainingContainers": 0,
                "remainingVolumes": 0,
                "remainingNetworks": 0,
            }
            and report["sandboxCleanup"] == {"remainingContainers": 0, "remainingNetworks": 0},
        )
        record(
            report,
            "operational-container-identities-preserved",
            before <= set(docker("ps", "-aq", "--no-trunc").splitlines()),
        )
        record(
            report,
            "measured-source-inputs-unchanged",
            scope_fingerprint(REPOSITORY_ROOT) == report["sourceFingerprint"],
        )
        report["result"] = "PASS"
    except Exception as error:
        report["failure"] = {"type": type(error).__name__, "code": "EXPERIENCE_LIVE_PROOF_FAILED"}
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["result"] == "PASS" else 1


if __name__ == "__main__":
    use_utf8_stdout()
    raise SystemExit(main())
