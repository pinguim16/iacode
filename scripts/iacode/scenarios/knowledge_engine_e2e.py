#!/usr/bin/env python3
"""Governed knowledge through an exclusively owned real authenticated runtime stack.

The permitted corpus is synthetic validation data. Real provider/sandbox/quality/experience
integration proves the upstream chain without treating storage consent as permission for RAG.
"""

from __future__ import annotations

import argparse
import hashlib
import http.client
import json
import os
import re
import secrets
import subprocess
import sys
import uuid
from datetime import UTC, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts/iacode"))
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))

from compose import StackError, compose, published_port, read_env_file, wait_for_health
from desktop_test_support import (
    InterruptedResponseProxy,
    environment,
    manifest,
    request,
    restarted_api_endpoint,
    scalar,
    synchronize_authorized_model,
    wait,
)
from experience_store_e2e import TASK, adverse_transport, operation, terminal
from iacode_common.secret_scanning import find_secret_kinds
from ledger_common import git_snapshot, scope_fingerprint, use_utf8_stdout
from verify import VERIFICATION_PORT_VARIABLES

OWNER = re.compile(r"iacode-knowledge-[0-9a-f]{12}")
CORPUS = ROOT / "services/knowledge/tests/fixtures/retrieval-corpus.json"


def report_path(value: Path) -> Path:
    candidate = value if value.is_absolute() else ROOT / value
    runtime = ROOT / "var"
    if runtime.is_symlink() or runtime.is_junction() or candidate.is_symlink():
        raise ValueError("redirected knowledge proof report refused")
    resolved = candidate.resolve()
    if not resolved.is_relative_to(runtime.resolve()) or resolved.suffix != ".json":
        raise ValueError("knowledge report must remain under this checkout's var directory")
    return resolved


def persist(report: dict) -> None:
    path = report_path(Path(report["reportFile"]))
    raw = (json.dumps(report, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    if find_secret_kinds(raw.decode("utf-8")):
        raise StackError("protected knowledge proof observation refused")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)


def record(report: dict, name: str, ok: bool, **facts) -> None:
    if {"name", "result"} & set(facts):
        raise ValueError("facts cannot replace the measured identity or result")
    report["steps"].append({"name": name, "result": "PASS" if ok else "FAIL", **facts})
    # Retain every available safe observation before later interpretation/cleanup can fail.
    persist(report)
    print(f"KNOWLEDGE {'PASS' if ok else 'FAIL'} {name}", flush=True)
    if not ok:
        raise StackError("knowledge live control failed: " + name)


def docker(*arguments: str) -> str:
    result = subprocess.run(
        ["docker", *arguments],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="strict",
        timeout=60,
        check=False,
    )
    if result.returncode:
        raise StackError("owned knowledge Docker observation failed")
    return result.stdout.strip()


def container_states() -> dict[str, bool]:
    identities = docker("ps", "-aq", "--no-trunc").splitlines()
    if not identities:
        return {}
    # Read only the identities/state, never configured container environments.
    rows = docker("inspect", "--format", "{{.Id}} {{.State.Running}}", *identities)
    return {
        identity: state == "true"
        for identity, state in (line.split() for line in rows.splitlines())
    }


def actor(project: str, mode: str, *arguments: str) -> dict:
    uuid.UUID(project)
    owner = os.environ.get("COMPOSE_PROJECT_NAME", "")
    if not OWNER.fullmatch(owner):
        raise ValueError("exact owned knowledge namespace required")
    observed = compose("ps", "-q", "api", merge_stderr=False)
    identifier = observed.stdout.strip()
    if not observed.ok or not re.fullmatch(r"[0-9a-f]{64}", identifier):
        raise StackError("owned knowledge API identity unavailable")
    labels = json.loads(docker("inspect", "--format", "{{json .Config.Labels}}", identifier))
    if labels.get("com.docker.compose.project") != owner:
        raise StackError("knowledge proof API ownership changed")
    code = (ROOT / "scripts/iacode/scenarios/knowledge_corpus_actor.py").read_text(encoding="utf-8")
    result = compose(
        "exec",
        "-T",
        "--env",
        "IACODE_KNOWLEDGE_PROOF_OWNER=" + owner,
        "api",
        "python",
        "-c",
        code,
        project,
        mode,
        *arguments,
        merge_stderr=False,
        timeout=60,
    )
    if not result.ok:
        raise StackError("owned knowledge corpus actor refused")
    value = json.loads(result.stdout)
    if value.get("result") != "APPLIED":
        raise StackError("owned knowledge corpus actor returned no applied observation")
    return value


def cleanup_sandboxes(owner: str) -> dict:
    if not OWNER.fullmatch(owner):
        raise ValueError("unowned knowledge sandbox cleanup refused")
    labels = (
        "--filter",
        "label=org.iacode.sandbox=1",
        "--filter",
        "label=org.iacode.sandbox.owner=" + owner,
    )
    for kind in ("container", "network"):
        identities = docker(
            kind, "ls", "-aq" if kind == "container" else "-q", "--no-trunc", *labels
        ).splitlines()
        for identifier in identities:
            if not re.fullmatch(r"[0-9a-f]{64}", identifier):
                raise StackError("invalid owned sandbox identity")
            field = "{{json .Config.Labels}}" if kind == "container" else "{{json .Labels}}"
            observed = json.loads(docker(kind, "inspect", "--format", field, identifier))
            if (
                observed.get("org.iacode.sandbox") != "1"
                or observed.get("org.iacode.sandbox.owner") != owner
            ):
                raise StackError("owned knowledge sandbox label changed")
            docker(kind, "rm", *(["--force"] if kind == "container" else []), identifier)
    return {
        kind: len(docker(kind, "ls", "-aq" if kind == "container" else "-q", *labels).splitlines())
        for kind in ("container", "network")
    }


def real_upstream(base: str, key: str, model: str, report: dict) -> tuple[str, dict]:
    catalog = synchronize_authorized_model(base, key, model)
    record(report, "exact-authorized-provider-model-discovered", True, **catalog)
    fixture = ROOT / "services/evaluator/tests/fixtures/python-pass"
    files = [
        {"path": name, "content": (fixture / name).read_text(encoding="utf-8")}
        for name in ("calculator.py", "test_calculator.py", "pyproject.toml")
    ]
    status, snapshot = operation(
        base, key, "snapshot", {"files": files, "manifestDigest": manifest(files)}
    )
    record(
        report, "actual-snapshot-created", status == 200 and snapshot["trainingAllowed"] is False
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
    task = terminal(base, key, created["runId"])
    record(
        report,
        "real-provider-and-sandbox-completed",
        task["state"] == "SUCCEEDED"
        and task["budget"]["modelCallsUsed"] > 0
        and bool(task["toolExecutions"]),
        sourceRunId=created["runId"],
        modelCallsUsed=task["budget"]["modelCallsUsed"],
        toolExecutions=len(task["toolExecutions"]),
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
    record(report, "actual-quality-created", status == 200 and bool(quality.get("runId")))
    measured = terminal(base, key, quality["runId"], quality=True)
    record(
        report,
        "actual-derived-quality-pass-with-evidence",
        measured["verdict"]["verdict"] == "PASS" and bool(measured["evidence"]),
        qualityRunId=quality["runId"],
    )
    status, source = request(base, key, "GET", "/api/v1/experiences/sources/" + created["runId"])
    record(
        report,
        "actual-source-project-discovered",
        status == 200
        and source["taskRunId"] == created["runId"]
        and source["storageConsentRequired"] is True,
    )
    project = source["projectId"]
    status, experience = request(
        base,
        key,
        "POST",
        "/api/v1/experiences/projects/" + project,
        {
            "taskRunId": created["runId"],
            "qualityRunId": quality["runId"],
            "storageConsent": True,
            "idempotencyKey": str(uuid.uuid4()),
            "retentionSeconds": 600,
        },
    )
    record(
        report,
        "actual-source-bound-experience-captured",
        status == 201
        and experience["state"] == "ACTIVE"
        and all(not row["ragAllowed"] for row in experience["document"]["provenance"]),
        experienceId=experience["experienceId"],
        sourceDigest=experience["contentDigest"],
    )
    return project, experience


def exercise(base: str, key: str, model: str, report: dict) -> None:
    corpus = json.loads(CORPUS.read_bytes())
    project, experience = real_upstream(base, key, model, report)
    root = "/api/v1/knowledge/projects/" + project

    def effects():
        return scalar("SELECT count(*) FROM knowledge_documents;")

    baseline = {
        table: scalar("SELECT count(*) FROM " + table + ";")
        for table in ("task_runs", "quality_runs", "tool_calls", "experiences")
    }
    denied = {
        "sourceKind": "experience",
        "sourceId": experience["experienceId"],
        "revision": experience["contentDigest"],
        "storageConsent": True,
        "idempotencyKey": str(uuid.uuid4()),
        "retentionSeconds": 600,
    }
    status, value = request(base, key, "POST", root + "/ingestions", denied)
    record(
        report,
        "owning-validated-storage-only-experience-cannot-be-laundered",
        status == 403 and value.get("code") == "REUSE_PERMISSION_DENIED" and effects() == 0,
    )
    sources = actor(project, "seed")
    record(
        report,
        "actual-content-bound-synthetic-source-grants-deployed",
        sources["corpusVersion"] == corpus["version"]
        and len(sources["sources"]) == len(corpus["documents"]),
        corpusVersion=corpus["version"],
        corpusSha256=hashlib.sha256(CORPUS.read_bytes()).hexdigest(),
    )
    sources = sources["sources"]
    first = sources["full"]["request"]
    for method, suffix in (("POST", "/ingestions"), ("POST", "/search"), ("GET", "/documents")):
        status, _ = request(base, key, method, root + suffix, authenticated=False)
        record(
            report, "unauthenticated-" + suffix[1:] + "-refused", status == 401 and effects() == 0
        )
    for name, options in (("invalid", {"invalid": True}), ("stale", {"stale": True})):
        status, _ = adverse_transport(base, key, root + "/documents", **options)
        record(report, name + "-authentication-refused", status == 401 and effects() == 0)
    marker = "gh" + "p_" + "k" * 24
    record(report, "canonical-secret-adverse-premise", bool(find_secret_kinds(marker)))
    variants = (
        ("consent-missing", {k: v for k, v in first.items() if k != "storageConsent"}),
        ("consent-denied", {**first, "storageConsent": False}),
        ("consent-coerced", {**first, "storageConsent": 1}),
        ("caller-text", {**first, "text": "not an admitted source"}),
        ("caller-path", {**first, "path": "outside/private.json"}),
        ("caller-rights", {**first, "ragAllowed": True}),
        ("caller-verdict", {**first, "verdict": "PASS"}),
        ("secret", {**first, "annotation": marker}),
        ("actual-capability", {**first, "annotation": key}),
    )
    for name, payload in variants:
        status, value = request(base, key, "POST", root + "/ingestions", payload)
        record(
            report,
            name + "-refused-before-effects",
            status == 400
            and effects() == 0
            and marker not in json.dumps(value)
            and key not in json.dumps(value),
        )
    wrong = "/api/v1/knowledge/projects/" + str(uuid.uuid4())
    status, _ = request(base, key, "POST", wrong + "/ingestions", first)
    record(report, "cross-project-ingestion-refused", status == 404 and effects() == 0)
    identity = str(uuid.uuid4())
    status, _ = request(base, key, "GET", root + "/documents", request_id=identity)
    record(report, "authentication-replay-clean-control", status == 200)
    status, _ = request(base, key, "GET", root + "/documents", request_id=identity)
    record(report, "actual-redis-authentication-replay-refused", status == 409 and effects() == 0)
    proxy = InterruptedResponseProxy(
        base, drop_operation="knowledge-ingest", knowledge_project=project
    )
    try:
        lost = False
        try:
            request(proxy.base, key, "POST", root + "/ingestions", first)
        except (http.client.RemoteDisconnected, ConnectionResetError):
            lost = True
        record(
            report,
            "actual-accepted-response-loss-one-publication",
            lost
            and proxy.dropped
            and proxy.accepted_status == 201
            and proxy.counts["knowledge-ingest"] == 1
            and effects() == 1,
        )
        status, recovered = request(base, key, "POST", root + "/ingestions", first)
        record(
            report,
            "stable-exact-request-recovers-original-publication",
            status == 200
            and recovered["idempotentReplay"] is True
            and recovered["documentId"] == proxy.accepted_document
            and recovered["expiresAt"] == proxy.accepted_expires_at
            and recovered["contentDigest"] == proxy.accepted_content_digest
            and effects() == 1,
        )
    finally:
        proxy.close()
    rows = {"full": recovered}
    for name, source in sources.items():
        if name in {"full", "retention"}:
            continue
        status, row = request(base, key, "POST", root + "/ingestions", source["request"])
        record(
            report, "actual-corpus-publication-" + name, status == 201 and row["state"] == "ACTIVE"
        )
        rows[name] = row
    documents = {row["name"]: row["text"] for row in corpus["documents"]}
    report["retrievalMeasurements"] = []
    for ordinal, expected in enumerate(corpus["queries"]):
        status, value = request(base, key, "POST", root + "/search", {"query": expected["query"]})
        hits = value.get("results", [])
        wanted = [rows[name]["documentId"] for name in expected["expectedSources"]]
        correct = status == 200 and [hit["citation"]["documentId"] for hit in hits] == wanted
        correct = correct and [hit["score"] for hit in hits] == expected["expectedScores"]
        correct = correct and value.get("outcome") == (
            "MATCHES" if wanted else "NO_PERMITTED_MATCH"
        )
        for hit in hits:
            citation = hit["citation"]
            name = next(
                name for name, row in rows.items() if row["documentId"] == citation["documentId"]
            )
            entry = sources[name]["entry"]
            correct = (
                correct and documents[name][citation["start"] : citation["end"]] == hit["excerpt"]
            )
            correct = (
                correct
                and hashlib.sha256(hit["excerpt"].encode()).hexdigest() == citation["chunkDigest"]
            )
            correct = correct and (
                citation["sourceDigest"],
                citation["grantDigest"],
                citation["revision"],
            ) == (entry["sourceDigest"], entry["grantDigest"], entry["revision"])
            target = (
                root + "/documents/" + citation["documentId"] + "/chunks/" + citation["chunkId"]
            )
            checked, resolved = request(base, key, "GET", target)
            correct = correct and checked == 200 and resolved.get("citation") == citation
            correct = (
                correct
                and resolved.get("excerpt") == hit["excerpt"]
                and hit["untrustedContent"] is True
            )
        report["retrievalMeasurements"].append(
            {
                "queryOrdinal": ordinal,
                "result": "PASS" if correct else "FAIL",
                "expectedSources": expected["expectedSources"],
                "observedHits": len(hits),
            }
        )
        record(report, f"measured-exact-retrieval-and-citations-{ordinal}", bool(correct))
    target = root + "/documents/" + rows["full"]["documentId"]
    status, inspected = request(base, key, "GET", target)
    exported, body = request(base, key, "GET", target + "/export")
    record(
        report, "actual-export-inspect-roundtrip", status == exported == 200 and inspected == body
    )
    status, page = request(base, key, "GET", root + "/documents?limit=1")
    record(
        report,
        "actual-bounded-project-pagination",
        status == 200 and len(page["documents"]) == 1 and bool(page.get("nextCursor")),
    )
    status, _ = request(base, key, "GET", wrong + "/documents?cursor=" + page["nextCursor"])
    record(report, "cross-project-cursor-refused", status == 400)
    for method in ("GET", "DELETE"):
        status, _ = request(base, key, method, wrong + "/documents/" + rows["full"]["documentId"])
        record(report, "cross-project-document-" + method.lower() + "-refused", status == 404)
    restarted = compose("restart", "api", timeout=90)
    record(report, "owned-api-restart", restarted.ok)
    base = restarted_api_endpoint(key)
    status, after = request(base, key, "GET", target)
    record(
        report, "actual-persistent-source-index-after-restart", status == 200 and after == inspected
    )
    actor(project, "corrupt-body", rows["full"]["documentId"])
    status, _ = request(base, key, "POST", root + "/search", {"query": "absent"})
    record(report, "actual-corrupt-body-is-not-empty-success", status == 503)
    actor(project, "restore-body", rows["full"]["documentId"])
    status, restored = request(base, key, "GET", target)
    record(report, "actual-body-restoration-null-control", status == 200 and restored == inspected)
    actor(project, "remove-index", rows["instruction"]["documentId"])
    status, _ = request(base, key, "POST", root + "/search", {"query": "absent"})
    record(report, "actual-missing-index-is-not-empty-success", status == 503)
    status, _ = request(
        base, key, "DELETE", root + "/documents/" + rows["instruction"]["documentId"]
    )
    record(report, "withdraw-owned-corrupt-projection", status == 200)
    actor(project, "revoke", "rights")
    status, _ = request(base, key, "GET", root + "/documents/" + rows["rights"]["documentId"])
    record(report, "revoked-grant-immediately-denies-delivery", status == 410)
    replacement = actor(project, "supersede", "partial")
    status, _ = request(base, key, "GET", root + "/documents/" + rows["partial"]["documentId"])
    record(report, "superseded-source-immediately-denies-old-citation", status == 410)
    status, rebuilt = request(base, key, "POST", root + "/ingestions", replacement["request"])
    record(
        report,
        "actual-rebuild-publishes-current-revision",
        status == 201 and rebuilt["revision"] == replacement["entry"]["revision"],
    )
    status, value = request(base, key, "POST", root + "/search", {"query": "Replacement rollback"})
    record(
        report,
        "rebuilt-retrieval-selects-new-citation",
        status == 200
        and value["results"][0]["citation"]["documentId"] == rebuilt["documentId"]
        and all(
            hit["citation"]["documentId"] != rows["partial"]["documentId"]
            for hit in value["results"]
        ),
    )
    deleted = root + "/documents/" + rows["long"]["documentId"]
    status, value = request(base, key, "DELETE", deleted)
    record(report, "actual-withdrawal", status == 200 and value["state"] == "DELETED")
    for label, payload in (
        ("same-key", sources["long"]["request"]),
        ("new-key", {**sources["long"]["request"], "idempotencyKey": str(uuid.uuid4())}),
    ):
        status, _ = request(base, key, "POST", root + "/ingestions", payload)
        record(report, label + "-cannot-resurrect-withdrawn-revision", status == 410)
    status, expiring = request(
        base,
        key,
        "POST",
        root + "/ingestions",
        {**sources["retention"]["request"], "retentionSeconds": 2},
    )
    record(report, "actual-finite-retention-created", status == 201)
    policy = json.loads((ROOT / ".iacode/policies/knowledge-policy.json").read_bytes())
    expired_target = root + "/documents/" + expiring["documentId"]
    wait(
        "actual knowledge expiry denial",
        lambda: request(base, key, "GET", expired_target)[0] == 410,
        seconds=policy["operationTimeoutSeconds"] + 7,
    )
    record(report, "expiry-denial-does-not-require-manual-sweep", True)
    expired_id = str(uuid.UUID(expiring["documentId"]))
    wait(
        "actual autonomous primary purge",
        lambda: (
            scalar(
                "SELECT count(*) FROM knowledge_documents WHERE id='" + expired_id + "' "
                "AND state='EXPIRED' AND body='{}'::jsonb AND purged_at IS NOT NULL;"
            )
            == 1
        ),
        seconds=policy["sweepIntervalSeconds"] + policy["operationTimeoutSeconds"] + 5,
    )
    record(
        report,
        "owned-background-retention-physically-purges-primary-index",
        scalar(
            "SELECT count(*) FROM knowledge_index_entries WHERE document_id='" + expired_id + "';"
        )
        == 0,
    )
    actor(project, "change", "unicode")
    status, _ = request(base, key, "GET", root + "/documents/" + rows["unicode"]["documentId"])
    record(report, "changed-raw-source-immediately-denies-delivery", status == 410)
    actor(project, "remove", "tides")
    status, _ = request(base, key, "POST", root + "/search", {"query": "absent"})
    record(report, "missing-current-source-is-unavailable-not-empty-success", status == 503)
    private_probe = "private-knowledge-query-" + uuid.uuid4().hex
    request(base, key, "POST", root + "/search", {"query": private_probe})
    request(base, key, "GET", root + "/documents/" + key + "?untrusted=" + key)
    logs = compose("logs", "--no-color", "api", merge_stderr=False, timeout=30)
    combined = logs.stdout + logs.stderr
    record(
        report,
        "actual-logs-retain-observability-not-private-ingress",
        logs.ok
        and key not in combined
        and marker not in combined
        and private_probe not in combined
        and "/api/v1/knowledge/<scoped>" in combined
        and "knowledge retention sweep completed" in combined,
    )
    after_counts = {table: scalar("SELECT count(*) FROM " + table + ";") for table in baseline}
    record(
        report, "knowledge-never-executes-or-mutates-upstream-evidence", after_counts == baseline
    )
    status, source_after = request(
        base,
        key,
        "GET",
        "/api/v1/experiences/projects/" + project + "/" + experience["experienceId"],
    )
    record(
        report,
        "upstream-experience-and-rights-remain-unchanged",
        status == 200
        and source_after["contentDigest"] == experience["contentDigest"]
        and all(not row["ragAllowed"] for row in source_after["document"]["provenance"]),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, default=Path("var/knowledge-engine-e2e.json"))
    options = parser.parse_args()
    path = report_path(options.report)
    path.unlink(missing_ok=True)
    snapshot = git_snapshot(ROOT)
    owner = "iacode-knowledge-" + uuid.uuid4().hex[:12]
    report = {
        "schemaVersion": "1.0.0",
        "scenario": "knowledge-engine-e2e",
        "result": "FAIL",
        "reportFile": path.relative_to(ROOT).as_posix(),
        "subjectCommit": snapshot["head"],
        "sourceDirty": snapshot["dirty"],
        "sourceFingerprint": scope_fingerprint(ROOT),
        "composeProject": owner,
        "steps": [],
        "cleanup": None,
    }
    persist(report)
    before = container_states()
    values = read_env_file()
    model = os.environ.get("IACODE_GATEWAY_SMOKE_MODEL") or values.get("IACODE_GATEWAY_SMOKE_MODEL")
    key = secrets.token_hex(32)
    owned = {
        "COMPOSE_PROJECT_NAME": owner,
        **dict.fromkeys(VERIFICATION_PORT_VARIABLES, "0"),
        "IACODE_DESKTOP_TOKEN": key,
        "IACODE_DESKTOP_TOKEN_EXPIRES_AT": (datetime.now(UTC) + timedelta(hours=2)).isoformat(),
        "IACODE_GATEWAY_DEFAULT_MODEL": model or "",
        "IACODE_KNOWLEDGE_SOURCE_ROOT": "/tmp/iacode-knowledge-corpus",
    }
    try:
        if not model:
            raise StackError("an explicit actual authorized smoke model is required; no substitute")
        with environment(owned):
            labels = ("--filter", "label=com.docker.compose.project=" + owner)
            if not OWNER.fullmatch(owner):
                raise StackError("fresh owned knowledge namespace invalid")
            for kind in ("container", "volume", "network"):
                if docker(kind, "ls", "-aq" if kind == "container" else "-q", *labels):
                    raise StackError("fresh owned knowledge namespace collision")
            try:
                built = subprocess.run(
                    [sys.executable, "scripts/iacode/sandbox_image.py"],
                    cwd=ROOT,
                    capture_output=True,
                    check=False,
                )
                record(report, "actual-current-sandbox-quality-images-built", built.returncode == 0)
                started = compose("up", "-d", "--build", timeout=600)
                record(report, "fresh-owned-authenticated-stack-started", started.ok)
                wait_for_health(timeout=300)
                record(report, "actual-owned-stack-healthy", True)
                exercise(f"http://127.0.0.1:{published_port('api', 8000)}", key, model, report)
            finally:
                persist(report)
                removed = compose("down", "--volumes", "--remove-orphans", timeout=180)
                report["sandboxCleanup"] = cleanup_sandboxes(owner)
                report["cleanup"] = {
                    "composeExitCode": removed.exit_code,
                    **{
                        kind: len(
                            docker(
                                kind, "ls", "-aq" if kind == "container" else "-q", *labels
                            ).splitlines()
                        )
                        for kind in ("container", "volume", "network")
                    },
                }
                persist(report)
        record(
            report,
            "owned-resources-actually-removed",
            report["cleanup"] == {"composeExitCode": 0, "container": 0, "volume": 0, "network": 0}
            and report["sandboxCleanup"] == {"container": 0, "network": 0},
        )
        after = container_states()
        record(
            report,
            "unrelated-container-identities-and-running-states-preserved",
            all(after.get(identity) == state for identity, state in before.items()),
        )
        record(
            report,
            "measured-source-inputs-unchanged",
            scope_fingerprint(ROOT) == report["sourceFingerprint"],
        )
        report["result"] = "PASS"
    except Exception as error:
        report["failure"] = {"type": type(error).__name__, "code": "KNOWLEDGE_LIVE_PROOF_FAILED"}
    persist(report)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["result"] == "PASS" else 1


if __name__ == "__main__":
    use_utf8_stdout()
    raise SystemExit(main())
