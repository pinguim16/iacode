"""Owned desktop live-proof actors. These call the real API/installed client, never domain fakes."""

from __future__ import annotations

import ast
import contextlib
import hashlib
import hmac
import http.client
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import threading
import time
import uuid
from collections import Counter
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

from compose import REPOSITORY_ROOT, StackError, compose, psql, published_port

sys.path.insert(0, str(REPOSITORY_ROOT / "packages/common/src"))
sys.path.insert(0, str(REPOSITORY_ROOT / "packages/contracts/src"))

from iacode_common.desktop_auth import response_signature, signed_headers

PROTOCOL_PATH = REPOSITORY_ROOT / "packages/contracts/src/iacode_contracts/desktop_protocol.json"
PROTOCOL = json.loads(PROTOCOL_PATH.read_bytes())


@contextlib.contextmanager
def environment(values: dict[str, str]):
    previous = {key: os.environ.get(key) for key in values}
    os.environ.update(values)
    try:
        yield
    finally:
        for key, value in previous.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def wait(description, probe, *, seconds=300):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        result = probe()
        if result:
            return result
        time.sleep(0.25)
    raise StackError(description + " did not complete before its declared deadline")


def scalar(query: str) -> int:
    result = psql(query, timeout=30)
    if not result.ok or not result.stdout.strip().isdigit():
        raise StackError("owned desktop SQL observation failed")
    return int(result.stdout.strip())


def active_session_predicate() -> str:
    """Read the canonical public tuple lazily without initializing application dependencies."""
    source = REPOSITORY_ROOT / "packages/contracts/src/iacode_contracts/sandbox.py"
    tree = ast.parse(source.read_text(encoding="utf-8"))
    values = [
        ast.literal_eval(row.value)
        for row in tree.body
        if isinstance(row, ast.AnnAssign)
        and isinstance(row.target, ast.Name)
        and row.target.id == "SANDBOX_ACTIVE_SESSION_STATES"
    ]
    if (
        len(values) != 1
        or not isinstance(values[0], tuple)
        or not values[0]
        or not all(
            isinstance(value, str) and re.fullmatch(r"[A-Z_]{1,64}", value) for value in values[0]
        )
    ):
        raise StackError("canonical active sandbox vocabulary is invalid")
    return "state IN (" + ",".join("'" + value + "'" for value in values[0]) + ")"


def object_count() -> int:
    code = (
        "import os; from minio import Minio; "
        "c=Minio(os.environ['IACODE_MINIO_ENDPOINT'],"
        "access_key=os.environ['IACODE_MINIO_ACCESS_KEY'],"
        "secret_key=os.environ['IACODE_MINIO_SECRET_KEY'],secure=False); "
        "print(sum(1 for _ in c.list_objects(os.environ['IACODE_MINIO_BUCKET'],recursive=True)))"
    )
    result = compose("exec", "-T", "api", "python", "-c", code, merge_stderr=False, timeout=30)
    if not result.ok or not result.stdout.strip().isdigit():
        raise StackError("owned desktop object-store observation failed")
    return int(result.stdout.strip())


def request(
    base: str,
    key: str,
    method: str,
    target: str,
    value: dict | None = None,
    *,
    request_id: str | None = None,
    authenticated: bool = True,
) -> tuple[int, dict]:
    data = (
        b""
        if value is None
        else json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode()
    )
    headers = {"Content-Type": "application/json"}
    signed = signed_headers(
        key,
        method,
        target,
        data,
        request_id=request_id,
        names=PROTOCOL["headers"],
        version=PROTOCOL["version"],
    )
    if authenticated:
        headers.update(signed)
    url = urlsplit(base)
    connection = http.client.HTTPConnection(url.hostname, url.port, timeout=35)
    try:
        connection.request(method, target, body=data, headers=headers)
        response = connection.getresponse()
        body = response.read(PROTOCOL["maxResponseBytes"] + 1)
        if len(body) > PROTOCOL["maxResponseBytes"]:
            raise StackError("live desktop response exceeded its byte bound")
        identity = signed[PROTOCOL["headers"]["requestId"]] if authenticated else ""
        expected = response_signature(
            key, identity, response.status, body, version=PROTOCOL["version"]
        )
        if not hmac.compare_digest(
            response.getheader(PROTOCOL["headers"]["signature"], ""), expected
        ):
            raise StackError("live response authentication failed")
        result = json.loads(body)
        if key.encode() in body:
            raise StackError("live response reflected protected authentication material")
        return response.status, result
    finally:
        connection.close()


def operation(
    base: str,
    key: str,
    name: str,
    args: dict | None = None,
    *,
    request_id: str | None = None,
    authenticated: bool = True,
):
    identity = request_id or str(uuid.uuid4())
    envelope = {
        "version": PROTOCOL["version"],
        "requestId": identity,
        "operation": name,
        "arguments": args or {},
    }
    return request(
        base,
        key,
        "POST",
        PROTOCOL["path"],
        envelope,
        request_id=identity,
        authenticated=authenticated,
    )


def restarted_api_endpoint(key: str) -> str:
    """A daemon-allocated host port is a new identity after restart, not a stable endpoint."""
    base = f"http://127.0.0.1:{published_port('api', 8000)}"

    def probe():
        try:
            status, value = operation(base, key, "hello")
        except (OSError, http.client.RemoteDisconnected):
            return None
        if status != 200:
            raise StackError(
                "restarted runtime refused actual host authentication: "
                + str(value.get("code", "UNKNOWN"))
            )
        return True

    wait("restarted API real host-published authenticated endpoint", probe, seconds=30)
    return base


def manifest(files: list[dict]) -> str:
    digest = hashlib.sha256()
    for file in sorted(files, key=lambda item: item["path"].encode()):
        data = file["content"].encode()
        digest.update(
            file["path"].encode()
            + b"\0"
            + str(len(data)).encode()
            + b":"
            + hashlib.sha256(data).hexdigest().encode()
            + b"\n"
        )
    return digest.hexdigest()


def node_executable(configured: Path | None) -> Path:
    value = configured or os.environ.get("IACODE_NODE_EXECUTABLE") or shutil.which("node")
    if not value or not Path(value).is_file():
        raise StackError(
            "a supported actual Node executable is required for fresh CLI installation"
        )
    executable = Path(value).resolve()
    version = subprocess.run(
        [str(executable), "--version"],
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=True,
    ).stdout.strip()
    numbers = tuple(map(int, version.removeprefix("v").split(".")))
    if not (
        (numbers[0] == 22 and numbers >= (22, 23, 2))
        or (numbers[0] == 24 and numbers >= (24, 19, 0))
    ):
        raise StackError(
            "configure IACODE_NODE_EXECUTABLE with supported Node 22.23.2+ or 24.19.0+"
        )
    return executable


def synchronize_authorized_model(base: str, key: str, model: str) -> dict:
    """Explicit fresh-runtime operator bootstrap, never a new client IPC operation or fallback."""
    provider, separator, identifier = model.partition(":")
    if not separator or not identifier or not re.fullmatch(r"[a-z][a-z0-9_-]{0,63}", provider):
        raise StackError("an explicit provider-qualified authorized model is required")
    status, synced = request(
        base, key, "POST", "/api/v1/gateway/models/sync", {"provider": provider}
    )
    outcomes = [row for row in synced.get("outcomes", []) if row.get("provider") == provider]
    if status != 200 or len(outcomes) != 1 or outcomes[0].get("errors"):
        raise StackError(
            "actual authorized provider catalog synchronization failed; no model substituted"
        )
    status, catalog = request(
        base, key, "GET", f"/api/v1/gateway/models?provider={provider}&active=true"
    )
    models = catalog.get("models", [])
    if status != 200 or not any(
        row.get("provider") == provider
        and row.get("model") == identifier
        and row.get("active") is True
        for row in models
    ):
        raise StackError(
            "the exact authorized model is absent from the fresh catalog; no model substituted"
        )
    return {
        "authorizedModel": model,
        "provider": provider,
        "catalogModels": len(models),
        "discovered": sum(outcomes[0].get(name, 0) for name in ("added", "updated", "unchanged")),
    }


class Cli:
    def __init__(self, directory: Path, tarball: Path, node: Path, base: str, key: str) -> None:
        candidates = [
            node.parent / "node_modules/npm/bin/npm-cli.js",
            node.parent.parent / "node_modules/npm/bin/npm-cli.js",
        ]
        npm = shutil.which("npm")
        if npm:
            candidates.append(Path(npm).parent / "node_modules/npm/bin/npm-cli.js")
        npm_cli = next((path for path in candidates if path.is_file()), None)
        if npm_cli is None:
            raise StackError(
                "the supported Node installation needs an actual npm CLI for fresh installation"
            )
        directory.mkdir(parents=True)
        userconfig = directory / "empty.npmrc"
        userconfig.write_text("", encoding="utf-8")
        prefix = directory / "installed"
        installed = subprocess.run(
            [
                str(node),
                str(npm_cli),
                "install",
                "--offline",
                "--ignore-scripts",
                "--no-audit",
                "--no-fund",
                "--prefix",
                str(prefix),
                "--cache",
                str(directory / "cache"),
                "--userconfig",
                str(userconfig),
                str(tarball),
            ],
            cwd=directory,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            timeout=120,
            check=False,
        )
        self.entry = prefix / "node_modules/@iacode/cli/bin/iacode.cjs"
        if installed.returncode or not self.entry.is_file():
            raise StackError(
                "actual offline npm CLI installation failed: " + installed.stderr[-800:]
            )
        self.node = node
        self.env = {**os.environ, "IACODE_DESKTOP_ENDPOINT": base, "IACODE_DESKTOP_TOKEN": key}
        self.calls: list[dict] = []

    def call(self, *args: str, expected: int = 0, timeout: int = 180) -> dict:
        completed = subprocess.run(
            [str(self.node), str(self.entry), *args],
            env=self.env,
            cwd=self.entry.parent,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            timeout=timeout,
            check=False,
        )
        self.calls.append({"command": args[0], "exitCode": completed.returncode})
        if completed.returncode != expected:
            # The CLI emits sanitized typed JSON, never a raw server response.
            raise StackError(
                f"installed CLI {args[0]} exit {completed.returncode}, "
                f"expected {expected}: {completed.stderr[-1000:]}"
            )
        text = completed.stdout if expected == 0 or args[0].endswith("follow") else completed.stderr
        lines = [json.loads(line) for line in text.splitlines() if line.strip()]
        if not lines:
            raise StackError("installed CLI returned no JSON observation")
        return lines[-1]


class InterruptedResponseProxy:
    """Drop exactly one accepted create response, without inventing domain data."""

    def __init__(
        self,
        base: str,
        *,
        drop_operation: str = "start",
        experience_project: str | None = None,
        knowledge_project: str | None = None,
    ) -> None:
        if drop_operation not in {
            "start",
            "quality-start",
            "experience-capture",
            "knowledge-ingest",
        }:
            raise ValueError("unsupported closed interruption operation")
        experience = drop_operation == "experience-capture"
        knowledge = drop_operation == "knowledge-ingest"
        if experience:
            if knowledge_project is not None:
                raise ValueError("an experience interruption cannot select a knowledge project")
            if (
                not isinstance(experience_project, str)
                or str(uuid.UUID(experience_project)) != experience_project
            ):
                raise ValueError("an exact canonical experience project is required")
            path = "/api/v1/experiences/projects/" + experience_project
            maximum = json.loads(
                (REPOSITORY_ROOT / ".iacode/policies/experience-policy.json").read_bytes()
            )["maxRequestBytes"]
            if type(maximum) is not int or not 1 <= maximum <= 4096:
                raise ValueError("the canonical experience request limit is invalid")
        elif knowledge:
            if (
                experience_project is not None
                or not isinstance(knowledge_project, str)
                or str(uuid.UUID(knowledge_project)) != knowledge_project
            ):
                raise ValueError("an exact canonical knowledge project alone is required")
            path = "/api/v1/knowledge/projects/" + knowledge_project + "/ingestions"
            maximum = json.loads(
                (REPOSITORY_ROOT / ".iacode/policies/knowledge-policy.json").read_bytes()
            )["maxRequestBytes"]
            if type(maximum) is not int or not 1 <= maximum <= 16384:
                raise ValueError("the canonical knowledge request limit is invalid")
        else:
            if experience_project is not None or knowledge_project is not None:
                raise ValueError("a desktop interruption does not select an experience project")
            path, maximum = PROTOCOL["path"], PROTOCOL["maxRequestBytes"]
        target = urlsplit(base)
        self.counts: Counter = Counter()
        self.accepted_run: str | None = None
        self.accepted_experience: str | None = None
        self.accepted_document: str | None = None
        self.accepted_status: int | None = None
        self.accepted_expires_at: str | None = None
        self.accepted_content_digest: str | None = None
        self.upstream_statuses: list[int] = []
        self.upstream_code: str | None = None
        self.dropped = False
        owner = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *_args):
                # This owned actor deliberately never logs HTTP payloads, headers or tasks.
                return

            def do_POST(self):
                length = int(self.headers.get("Content-Length", "-1"))
                if not 0 <= length <= maximum or self.path != path:
                    self.send_error(400)
                    return
                body = self.rfile.read(length)
                name = (
                    drop_operation
                    if experience or knowledge
                    else json.loads(body).get("operation", "unknown")
                )
                owner.counts[name] += 1
                upstream = http.client.HTTPConnection(target.hostname, target.port, timeout=35)
                try:
                    headers = {
                        name: value
                        for name, value in self.headers.items()
                        if name.lower() not in {"host", "connection", "proxy-connection"}
                    }
                    upstream.request("POST", self.path, body=body, headers=headers)
                    response = upstream.getresponse()
                    result = response.read(PROTOCOL["maxResponseBytes"] + 1)
                    owner.upstream_statuses.append(response.status)
                    if (experience or knowledge) and response.status >= 400:
                        code = json.loads(result).get("code")
                        safe_codes = {
                            "AUTHORIZATION_MATERIAL_REFUSED",
                            "SECRET_MATERIAL_REFUSED",
                            "STORED_CONTRACT_INVALID",
                            "QUALITY_PLAN_CORRUPT",
                            "QUALITY_VERDICT_CORRUPT",
                            "SOURCE_OBJECT_UNAVAILABLE",
                            "SOURCE_PERMISSION_REFUSED",
                            "SOURCE_OBJECT_CORRUPT",
                            "EXPERIENCE_DEPENDENCY_UNAVAILABLE",
                            "PROVENANCE_DIGEST_INVALID",
                            "KNOWLEDGE_DEPENDENCY_UNAVAILABLE",
                            "SOURCE_CHANGED",
                            "REUSE_PERMISSION_DENIED",
                        }
                        owner.upstream_code = code if code in safe_codes else "OTHER_REFUSAL"
                    if (
                        name == drop_operation
                        and not owner.dropped
                        and 200 <= response.status < 300
                    ):
                        accepted = json.loads(result)
                        if experience or knowledge:
                            if knowledge:
                                owner.accepted_document = accepted["documentId"]
                            else:
                                owner.accepted_experience = accepted["experienceId"]
                            owner.accepted_expires_at = accepted["expiresAt"]
                            owner.accepted_content_digest = accepted["contentDigest"]
                        else:
                            owner.accepted_run = accepted["data"]["runId"]
                        owner.accepted_status = response.status
                        owner.dropped = True
                        self.close_connection = True
                        self.connection.shutdown(socket.SHUT_RDWR)
                        self.connection.close()
                        return
                    self.send_response(response.status)
                    for name, value in response.getheaders():
                        if name.lower() not in {
                            "connection",
                            "transfer-encoding",
                            "content-length",
                        }:
                            self.send_header(name, value)
                    self.send_header("Content-Length", str(len(result)))
                    self.end_headers()
                    self.wfile.write(result)
                finally:
                    upstream.close()

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.server.daemon_threads = True
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.base = f"http://127.0.0.1:{self.server.server_port}"

    def close(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=5)
        if self.thread.is_alive():
            raise StackError("owned response proxy did not stop")
