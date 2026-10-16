#!/usr/bin/env python3
"""Fresh installed clients against a separately owned authenticated real runtime/provider stack."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import secrets
import shutil
import subprocess
import sys
import uuid
from datetime import UTC, datetime, timedelta
from pathlib import Path


def checked_report_path(value: Path) -> Path:
    root = Path(__file__).resolve().parents[3]
    runtime = root / "var"
    candidate = value if value.is_absolute() else root / value
    if runtime.is_symlink() or runtime.is_junction() or candidate.is_symlink():
        raise ValueError("refusing a redirected desktop proof report")
    resolved = candidate.resolve()
    if not resolved.is_relative_to(runtime.resolve()) or resolved.suffix != ".json":
        raise ValueError("desktop proof reports must remain under this checkout's var directory")
    return resolved


def retire_before_imports(arguments: list[str]) -> None:
    # This standard-library bootstrap must run before any project import can fail. The external
    # full verifier additionally retires the report before launching even this Python source.
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--report", type=Path, default=Path("var/desktop-e2e.json"))
    options, _ = parser.parse_known_args(arguments)
    checked_report_path(options.report).unlink(missing_ok=True)


if __name__ == "__main__" and not {"-h", "--help"}.intersection(sys.argv[1:]):
    retire_before_imports(sys.argv[1:])

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "development-ledger"))

from build_clients import build
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
    Cli,
    InterruptedResponseProxy,
    active_session_predicate,
    environment,
    manifest,
    node_executable,
    object_count,
    operation,
    request,
    restarted_api_endpoint,
    scalar,
    synchronize_authorized_model,
    wait,
)
from iacode_common.secret_scanning import find_secret_kinds
from ledger_common import git_snapshot, scope_fingerprint
from native_editor import NativeEditor
from native_process import owned_directory
from verify import VERIFICATION_PORT_VARIABLES

TASK = (
    "Use the provided immutable workspace. Inspect calculator.py and test_calculator.py. "
    "In the run sandbox execute python -m unittest -v and report its actual result. "
    "Source is already correct: do not change files or dependencies, contact a network, or open "
    "an external path. Finish with a concise result. Never claim tests ran without executing them."
)
TERMINAL = {"SUCCEEDED", "FAILED", "CANCELLED"}
QUALITY_TERMINAL = TERMINAL | {"TIMED_OUT", "INVALID"}


def docker(*arguments: str) -> str:
    result = subprocess.run(
        ["docker", *arguments],
        cwd=REPOSITORY_ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        timeout=60,
        check=False,
    )
    if result.returncode:
        raise StackError("owned desktop Docker observation failed: " + result.stderr[-500:])
    return result.stdout.strip()


def record(report: dict, name: str, ok: bool, **facts) -> None:
    report["steps"].append({"name": name, "result": "PASS" if ok else "FAIL", **facts})
    log(f"DESKTOP {'PASS' if ok else 'FAIL'} {name}")
    if not ok:
        raise StackError("live desktop control failed: " + name)


def cleanup_owned_sandboxes(project: str) -> dict:
    if not re.fullmatch(r"iacode-desktop-[0-9a-f]{12}", project):
        raise ValueError("refusing an unowned sandbox namespace")
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
                raise StackError("invalid owned engine identity")
            observed = json.loads(docker(kind, "inspect", identifier))[0]
            actual = (
                observed.get("Config", {}).get("Labels", {})
                if kind == "container"
                else observed.get("Labels", {})
            )
            if (
                actual.get("org.iacode.sandbox") != "1"
                or actual.get("org.iacode.sandbox.owner") != project
            ):
                raise StackError("sandbox cleanup ownership changed")
            docker(kind, "rm", *(["--force"] if kind == "container" else []), identifier)
    return {
        "remainingContainers": len(docker("container", "ls", "-aq", *labels).splitlines()),
        "remainingNetworks": len(docker("network", "ls", "-q", *labels).splitlines()),
    }


def quality_terminal(cli: Cli, identifier: str) -> dict:
    def probe():
        detail = cli.call("quality-read", "--run-id", identifier)
        return detail if detail["run"]["state"] in QUALITY_TERMINAL else None

    return wait("actual quality terminal", probe, seconds=600)


def executed_sandbox_request(detail: dict) -> dict:
    executed = {
        row["toolRequestId"]
        for row in detail["toolExecutions"]
        if row.get("status") == "SUCCEEDED" and row.get("sandboxSession")
    }
    matches = [row for row in detail["toolRequests"] if row["toolRequestId"] in executed]
    if not matches:
        raise StackError(
            "an actual successful sandbox execution is required for the forgery premise"
        )
    return matches[0]


def interrupt_local_quality_observer(cli: Cli, quality_id: str, report: dict) -> None:
    project = os.environ["COMPOSE_PROJECT_NAME"]
    if not re.fullmatch(r"iacode-desktop-[0-9a-f]{12}", project):
        raise StackError("local observer requires an owned desktop namespace")
    api = compose("ps", "-q", "api")
    identifier = api.stdout.strip()
    if not api.ok or not re.fullmatch(r"[0-9a-f]{64}", identifier):
        raise StackError("owned observer API network identity is unavailable")
    name = project + "-observer"
    package_root = cli.entry.parents[1]
    from client_checks import NODE_IMAGE

    def log_rows():
        # Docker preserves stdout/stderr streams; the CLI's interruption receipt is on stderr.
        observed = subprocess.run(
            ["docker", "logs", "--tail", "50", name],
            cwd=REPOSITORY_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
            check=False,
        )
        if observed.returncode or len(observed.stdout.encode("utf-8")) > 1048576:
            raise StackError("owned observer log receipt is unavailable or oversized")
        return [json.loads(line) for line in observed.stdout.splitlines() if line.strip()]

    try:
        # Actual installed CLI, pinned supported Node, own PID namespace and the API's loopback.
        # Credential values are inherited by name only, never command arguments or logs.
        docker(
            "run",
            "--detach",
            "--name",
            name,
            "--read-only",
            "--user",
            "1000:1000",
            "--cap-drop",
            "ALL",
            "--security-opt",
            "no-new-privileges:true",
            "--network",
            "container:" + identifier,
            "--env",
            "IACODE_DESKTOP_TOKEN",
            "--env",
            "IACODE_DESKTOP_ENDPOINT=http://127.0.0.1:8000",
            "--volume",
            f"{package_root}:/client:ro",
            NODE_IMAGE,
            "node",
            "/client/bin/iacode.cjs",
            "quality-follow",
            "--run-id",
            quality_id,
            "--wait-seconds",
            "300",
        )

        def observing():
            if docker("inspect", "--format", "{{.State.Running}}", name) != "true":
                raise StackError("local quality observer exited before interruption premise")
            rows = log_rows()
            return rows if any(row.get("type") == "events" for row in rows) else None

        observed = wait("actual installed CLI quality observation", observing, seconds=30)
        docker("kill", "--signal", "SIGINT", name)
        code = docker("wait", name)
        rows = log_rows()
        last = rows[-1]
        detail = cli.call("quality-read", "--run-id", quality_id)
        record(
            report,
            "actual-cli-sigint-stops-only-local-observation",
            code == "130"
            and last.get("code") == "OBSERVATION_CANCELLED"
            and last.get("remoteCancellationRequested") is False
            and last.get("lastCursor", -1) >= max(row.get("nextCursor", 0) for row in observed)
            and detail["run"]["state"] not in QUALITY_TERMINAL,
            exitCode=code,
            lastCursor=last.get("lastCursor"),
            remoteState=detail["run"]["state"],
        )
    finally:
        docker("rm", "--force", name)


def tamper_owned_snapshot(base: str, key: str, snapshot: dict, report: dict) -> None:
    if not re.fullmatch(r"iacode-desktop-[0-9a-f]{12}", os.environ["COMPOSE_PROJECT_NAME"]):
        raise StackError("snapshot corruption premise requires a disposable owned namespace")
    digest = snapshot["snapshotDigest"]
    if not re.fullmatch(r"[0-9a-f]{64}", digest):
        raise StackError("invalid owned snapshot identity")
    code = (
        "import io,os,sys; from minio import Minio; "
        "c=Minio(os.environ['IACODE_MINIO_ENDPOINT'],access_key=os.environ['IACODE_MINIO_ACCESS_KEY'],"
        "secret_key=os.environ['IACODE_MINIO_SECRET_KEY'],secure=False); "
        "p='sandbox/snapshots/desktop/'+sys.argv[1]+'.tar.gz'; "
        "b=os.environ['IACODE_MINIO_BUCKET']; "
        "r=c.get_object(b,p); original=r.read(); r.close(); r.release_conn(); "
        "changed=original+b'owned-negative-control'; "
        "c.put_object(b,p,io.BytesIO(changed),len(changed)); "
        "print('OWNED_SNAPSHOT_BYTES_CHANGED')"
    )
    changed = compose("exec", "-T", "api", "python", "-c", code, digest)
    if not changed.ok or changed.stdout.strip() != "OWNED_SNAPSHOT_BYTES_CHANGED":
        raise StackError("actual owned object corruption premise failed")
    before = scalar("SELECT count(*) FROM task_runs;")
    status, refused = operation(
        base,
        key,
        "start",
        {
            "snapshotId": snapshot["snapshotId"],
            "task": TASK,
            "team": "coding",
            "idempotencyKey": str(uuid.uuid4()),
        },
    )
    record(
        report,
        "actual-object-tamper-refused-before-task-persistence",
        status >= 400
        and refused.get("code") == "SNAPSHOT_CORRUPT"
        and scalar("SELECT count(*) FROM task_runs;") == before,
    )


def exercise(directory: Path, node: Path, key: str, model: str, report: dict) -> None:
    packages = build(directory / "packages")
    report["packages"] = packages
    base = f"http://127.0.0.1:{published_port('api', 8000)}"
    source = directory / "workspace"
    shutil.copytree(
        REPOSITORY_ROOT / "services/evaluator/tests/fixtures/python-pass",
        source,
        ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache"),
    )
    (source / ".env").write_text("excluded synthetic local fixture\n", encoding="utf-8")
    sentinel = directory / "host-sentinel.txt"
    sentinel.write_text("owned-host-sentinel-" + uuid.uuid4().hex, encoding="utf-8")
    before_sentinel = hashlib.sha256(sentinel.read_bytes()).hexdigest()
    original_sources = {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in source.iterdir()
        if path.is_file()
    }
    cli = Cli(directory / "cli", directory / "packages/iacode-cli-0.1.0.tgz", node, base, key)
    report["cliCommands"] = cli.calls  # Retain observed commands even when a later premise fails.
    report["cliRuntime"] = subprocess.run(
        [str(node), "--version"], capture_output=True, text=True, check=True
    ).stdout.strip()
    doctor = cli.call("doctor")
    record(
        report,
        "fresh-offline-cli-install-and-authenticated-contract",
        doctor["authenticated"] is True,
    )
    catalog = synchronize_authorized_model(base, key, model)
    record(
        report, "fresh-provider-catalog-synced-and-exact-authorized-model-present", True, **catalog
    )

    # Adversarial premises use the real authenticated ASGI boundary and real persistence.
    before_runs = scalar("SELECT count(*) FROM task_runs;")
    status, rejected = operation(base, key, "start", authenticated=False)
    record(
        report,
        "unauthenticated-domain-refused-before-effects",
        status == 401
        and rejected["code"] == "AUTHENTICATION_REQUIRED"
        and scalar("SELECT count(*) FROM task_runs;") == before_runs,
    )
    for forbidden in ("tool-result", "quality-verdict", "shell.exec"):
        status, rejected = operation(base, key, forbidden)
        record(
            report,
            "closed-ipc-refuses-" + forbidden,
            status == 400 and rejected["code"] == "OPERATION_UNKNOWN",
        )
    marker = "gh" + "p_" + "q" * 24
    record(report, "secret-adverse-premise", bool(find_secret_kinds(marker)))
    before_artifacts, before_objects = scalar("SELECT count(*) FROM artifacts;"), object_count()
    files = [{"path": "main.py", "content": marker}]
    status, rejected = operation(
        base, key, "snapshot", {"files": files, "manifestDigest": manifest(files)}
    )
    record(
        report,
        "secret-upload-refused-before-sql-or-object-persistence",
        status == 400
        and rejected["code"] == "SNAPSHOT_SECRET_REFUSED"
        and scalar("SELECT count(*) FROM artifacts;") == before_artifacts
        and object_count() == before_objects,
    )
    identity = str(uuid.uuid4())
    status, _ = operation(base, key, "hello", request_id=identity)
    record(report, "replay-clean-control", status == 200)
    restarted = compose("restart", "api", timeout=90)
    if not restarted.ok:
        raise StackError("owned API restart failed")
    wait_for_health(["api"], timeout=120)
    base = restarted_api_endpoint(key)
    # Explicit owned test-operator reconfiguration, before any approved client mutation.
    # Production clients never infer a replacement endpoint from workspace data.
    cli.env["IACODE_DESKTOP_ENDPOINT"] = base
    status, rejected = operation(base, key, "hello", request_id=identity)
    record(
        report,
        "redis-replay-refusal-survives-api-restart",
        status == 409 and rejected["code"] == "AUTHENTICATION_REPLAY",
    )

    inventory = cli.call("preview", "--root", str(source))
    record(
        report,
        "cli-preview-is-bounded-and-excludes-private-path",
        "files" not in inventory
        and ".env" not in [item["path"] for item in inventory["inventory"]]
        and inventory["excludedCount"] >= 1,
    )
    refused = cli.call("snapshot", "--root", str(source), "--approve", "0" * 64, expected=2)
    record(
        report,
        "cli-changed-or-wrong-consent-refused-locally",
        refused["code"] == "SNAPSHOT_CONSENT_MISMATCH",
    )
    stored = cli.call("snapshot", "--root", str(source), "--approve", inventory["manifestDigest"])
    retried = cli.call("snapshot", "--root", str(source), "--approve", inventory["manifestDigest"])
    record(
        report,
        "real-snapshot-persistence-stable-retry-and-rights",
        stored["snapshotId"] == retried["snapshotId"]
        and stored["snapshotDigest"] == retried["snapshotDigest"]
        and stored["trainingAllowed"] is False,
    )
    lookup = cli.call("snapshot-lookup", "--digest", inventory["manifestDigest"])
    record(
        report,
        "read-only-snapshot-reconciliation",
        lookup["found"] and lookup["snapshotId"] == stored["snapshotId"],
    )

    # Native commands make every approval through actual Workbench QuickInput controls. The
    # forwarding proxy drops only the first real accepted create response, not its domain effect.
    proxy = InterruptedResponseProxy(base)
    try:
        native = NativeEditor(
            directory / "editor",
            source,
            directory / "packages/iacode-0.1.0.vsix",
            packages["protocolDigest"],
        )
        first = native.run(
            "start",
            extra_env={
                "IACODE_DESKTOP_ENDPOINT": proxy.base,
                "IACODE_DESKTOP_TOKEN": key,
                "IACODE_EDITOR_TASK": TASK,
            },
        )
        report["nativeStart"] = first
        record(
            report,
            "actual-native-snapshot-and-uncertain-accepted-create",
            first["result"] == "PASS",
        )
        pending = first["pending"]
        recovered = cli.call("lookup", "--request-id", pending["idempotencyKey"])
        report["acceptedRunId"] = recovered.get("runId")
        record(
            report,
            "lost-response-has-one-real-persisted-run",
            recovered["found"]
            and recovered["runId"] == proxy.accepted_run
            and scalar(
                "SELECT count(*) FROM task_runs "
                f"WHERE idempotency_key='{pending['idempotencyKey']}';"
            )
            == 1
            and proxy.counts["start"] == 1
            and proxy.counts["snapshot"] == 1,
        )
        second = native.run("resume")
        report["nativeResume"] = second
        record(
            report,
            "actual-new-host-secretstorage-recovery-provider-sandbox-quality",
            second["result"] == "PASS"
            and second["processId"] != first["processId"]
            and second["runId"] == recovered["runId"]
            and proxy.counts["start"] == 1
            and proxy.counts["lookup"] == 1,
        )
        report["proxyOperationCounts"] = dict(proxy.counts)
        detail = cli.call("read", "--run-id", recovered["runId"])
        record(
            report,
            "both-clients-observe-identical-server-task-truth",
            detail["state"] == "SUCCEEDED"
            and detail["budget"]["modelCallsUsed"] > 0
            and bool(detail["toolExecutions"]),
        )
        # A completed sandbox-owned tool is still not writable by an external client.
        tool = executed_sandbox_request(detail)
        status, rejected = request(
            base,
            key,
            "POST",
            f"/api/v1/agent-runs/{recovered['runId']}/tool-results",
            {
                "toolRequestId": tool["toolRequestId"],
                "status": "SUCCEEDED",
                "output": {"forged": True},
            },
        )
        record(
            report,
            "authenticated-external-sandbox-result-forgery-refused",
            status == 403 and rejected["code"] == "TOOL_RESULT_ORIGIN_REFUSED",
        )
        quality_id = second["qualityRunId"]
        quality = cli.call("quality-read", "--run-id", quality_id)
        record(
            report,
            "both-clients-observe-identical-derived-verdict-and-evidence",
            quality["verdict"]["verdict"] == "PASS"
            and bool(quality["results"])
            and all(item["trainingAllowed"] is False for item in quality["evidence"]),
        )
        reproduction = cli.call(
            "quality-reproduce",
            "--run-id",
            quality_id,
            "--request-id",
            str(uuid.uuid4()),
            "--approve",
        )
        repeated = quality_terminal(cli, reproduction["runId"])
        record(
            report,
            "installed-cli-reproduces-real-quality-inputs",
            repeated["run"]["state"] == "SUCCEEDED" and repeated["verdict"]["verdict"] == "PASS",
        )
        quality_proxy = InterruptedResponseProxy(base, drop_operation="quality-start")
        original_endpoint = cli.env["IACODE_DESKTOP_ENDPOINT"]
        try:
            cli.env["IACODE_DESKTOP_ENDPOINT"] = quality_proxy.base
            identity = str(uuid.uuid4())
            uncertain = cli.call(
                "quality-start",
                "--snapshot",
                stored["snapshotId"],
                "--digest",
                stored["snapshotDigest"],
                "--request-id",
                identity,
                "--approve",
                expected=4,
            )
            recovered_quality = cli.call("quality-lookup", "--request-id", identity)
            record(
                report,
                "actual-quality-response-loss-reconciles-once-without-replay",
                uncertain.get("uncertain") is True
                and uncertain.get("idempotencyKey") == identity
                and recovered_quality.get("found") is True
                and recovered_quality["runId"] == quality_proxy.accepted_run
                and quality_proxy.counts["quality-start"] == 1
                and scalar(f"SELECT count(*) FROM quality_runs WHERE idempotency_key='{identity}';")
                == 1,
            )
            record(
                report,
                "reconciled-quality-completes-with-real-pass-evidence",
                quality_terminal(cli, recovered_quality["runId"])["verdict"]["verdict"] == "PASS",
            )
        finally:
            cli.env["IACODE_DESKTOP_ENDPOINT"] = original_endpoint
            quality_proxy.close()
    finally:
        proxy.close()

    # Real running agent cancellation, not merely stopping a local observer or an unstarted row.
    create_id = str(uuid.uuid4())
    run = cli.call(
        "start",
        "--snapshot",
        stored["snapshotId"],
        "--task",
        TASK,
        "--team",
        "coding",
        "--model",
        model,
        "--request-id",
        create_id,
        "--approve",
    )

    def running():
        observed = cli.call("read", "--run-id", run["runId"])
        if observed["state"] in TERMINAL:
            raise StackError("agent reached terminal before running-cancellation premise")
        return observed if observed["state"] == "RUNNING" else None

    report["taskCancellation"] = {"runId": run["runId"], "phase": "WAIT_RUNNING"}
    wait("actual agent RUNNING premise", running, seconds=60)
    report["taskCancellation"]["phase"] = "REQUEST_CANCEL"
    requested = cli.call("cancel", "--run-id", run["runId"], "--approve")
    report["taskCancellation"].update(
        {"phase": "FOLLOW_TERMINAL", "requestedState": requested["state"]}
    )
    terminal = cli.call(
        "follow", "--run-id", run["runId"], "--wait-seconds", "300", expected=3, timeout=330
    )
    report["taskCancellation"].update(
        {"phase": "REPEAT_CANCEL", "terminalState": terminal["data"]["state"]}
    )
    cli.call("cancel", "--run-id", run["runId"], "--approve")
    report["taskCancellation"]["phase"] = "COMPLETE"
    record(
        report,
        "installed-cli-running-task-cancel-request-terminal-and-repeat",
        requested["state"] != "SUCCEEDED"
        and terminal["data"]["state"] == "CANCELLED"
        and scalar(
            f"SELECT count(*) FROM sandbox_sessions WHERE task_run_id='{run['runId']}' "
            "AND " + active_session_predicate() + ";"
        )
        == 0,
    )

    slow = directory / "slow"
    shutil.copytree(
        REPOSITORY_ROOT / "services/evaluator/tests/fixtures/python-slow",
        slow,
        ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache"),
    )
    slow_inventory = cli.call("preview", "--root", str(slow))
    slow_snapshot = cli.call(
        "snapshot", "--root", str(slow), "--approve", slow_inventory["manifestDigest"]
    )
    quality_id = cli.call(
        "quality-start",
        "--snapshot",
        slow_snapshot["snapshotId"],
        "--digest",
        slow_snapshot["snapshotDigest"],
        "--request-id",
        str(uuid.uuid4()),
        "--approve",
    )["runId"]
    wait(
        "actual quality sandbox RUNNING premise",
        lambda: scalar(
            f"SELECT count(*) FROM sandbox_sessions WHERE quality_run_id='{quality_id}' "
            "AND state='RUNNING';"
        ),
        seconds=120,
    )
    interrupt_local_quality_observer(cli, quality_id, report)
    cli.call("quality-cancel", "--run-id", quality_id, "--approve")
    terminal = cli.call(
        "quality-follow", "--run-id", quality_id, "--wait-seconds", "300", expected=3, timeout=330
    )
    cli.call("quality-cancel", "--run-id", quality_id, "--approve")
    record(
        report,
        "installed-cli-running-quality-cancel-waits-for-cleanup",
        terminal["data"]["run"]["state"] == "CANCELLED"
        and terminal["data"]["verdict"]["verdict"] == "FAIL"
        and scalar(
            f"SELECT count(*) FROM sandbox_sessions WHERE quality_run_id='{quality_id}' "
            "AND " + active_session_predicate() + ";"
        )
        == 0,
    )
    record(
        report,
        "host-source-and-sentinel-unchanged",
        hashlib.sha256(sentinel.read_bytes()).hexdigest() == before_sentinel
        and original_sources
        == {
            path.name: hashlib.sha256(path.read_bytes()).hexdigest()
            for path in source.iterdir()
            if path.is_file()
        },
    )
    report["cliCommands"] = cli.calls
    tamper_owned_snapshot(base, key, stored, report)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--node", type=Path)
    parser.add_argument("--report", type=Path, default=REPOSITORY_ROOT / "var/desktop-e2e.json")
    args = parser.parse_args()
    args.report = checked_report_path(args.report)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.unlink(missing_ok=True)
    report = {
        "schemaVersion": "1.0.0",
        "scenario": "desktop-e2e",
        "result": "FAIL",
        "environment": "fresh-installed-cli-and-native-vscode-real-authenticated-compose-"
        "provider-postgresql-redis-minio-temporal-sandbox-quality",
        "subjectCommit": git_snapshot(REPOSITORY_ROOT)["head"],
        "sourceDirty": git_snapshot(REPOSITORY_ROOT)["dirty"],
        "sourceFingerprint": scope_fingerprint(REPOSITORY_ROOT),
        "steps": [],
    }
    project = "iacode-desktop-" + uuid.uuid4().hex[:12]
    report["composeProject"] = project
    before_containers = set(docker("ps", "-aq", "--no-trunc").splitlines())
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
        node = node_executable(args.node)
        if not model:
            raise StackError(
                "IACODE_GATEWAY_SMOKE_MODEL must name the actual authorized provider model; "
                "it is never substituted"
            )
        with (
            environment(owned),
            owned_directory("iacode-desktop-live-") as temporary,
        ):
            directory = temporary["path"]
            log("building and starting separate owned authenticated desktop stack")
            images = subprocess.run(
                [sys.executable, str(REPOSITORY_ROOT / "scripts/iacode/sandbox_image.py")],
                cwd=REPOSITORY_ROOT,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
            )
            if images.returncode:
                raise StackError(
                    "current sandbox/quality image build failed: " + images.stdout[-800:]
                )
            started = compose("up", "-d", "--build", timeout=600)
            if not started.ok:
                raise StackError("owned desktop stack startup failed: " + started.output[-1600:])
            wait_for_health(timeout=300)
            record(report, "fresh-owned-authenticated-stack-healthy", True, authorizedModel=model)
            try:
                exercise(directory, node, key, model, report)
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
                }
        report["ownedTemporaryDirectoryRemoved"] = not directory.exists()
        report["directoryCleanupRetries"] = temporary["cleanupRetries"]
        after_containers = set(docker("ps", "-aq", "--no-trunc").splitlines())
        record(
            report,
            "operational-container-identities-preserved",
            before_containers <= after_containers,
        )
        record(
            report,
            "owned-services-volumes-profiles-removed",
            report["cleanup"]
            == {"composeExitCode": 0, "remainingContainers": 0, "remainingVolumes": 0}
            and report["ownedTemporaryDirectoryRemoved"],
        )
        record(
            report,
            "owned-sandbox-children-and-networks-removed",
            report["sandboxCleanup"] == {"remainingContainers": 0, "remainingNetworks": 0},
        )
        record(
            report,
            "measured-source-inputs-unchanged",
            scope_fingerprint(REPOSITORY_ROOT) == report["sourceFingerprint"],
        )
        report["result"] = "PASS"
    except Exception as error:
        report["failure"] = {"type": type(error).__name__, "message": str(error)[:1800]}
        # A failed build/start also owns its partial namespace; no operational project is touched.
        with environment(owned):
            removed = compose("down", "--volumes", "--remove-orphans", timeout=180)
            report["failureCleanupExitCode"] = removed.exit_code
            report["failureSandboxCleanup"] = cleanup_owned_sandboxes(project)
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
