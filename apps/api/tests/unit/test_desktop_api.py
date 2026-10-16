"""Real ASGI boundary tests; Redis is a decision double here, never a live-state proof."""

from __future__ import annotations

import asyncio
import base64
import hashlib
import io
import json
import tarfile
import time
import uuid
from contextlib import contextmanager
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from unittest import mock

import pytest
from fastapi.testclient import TestClient
from iacode_api.config import settings_for_tests
from iacode_api.desktop_snapshots import snapshot_bytes, store_snapshot
from iacode_api.main import create_app
from iacode_common.desktop_auth import response_signature, signed_headers
from iacode_common.secret_scanning import find_secret_kinds
from iacode_contracts.desktop import PROTOCOL, PROTOCOL_DIGEST, DesktopError, parse_request

KEY = hashlib.sha256(b"explicit deterministic desktop unit-test fixture").hexdigest()


def envelope(operation: str = "hello", arguments: dict | None = None) -> dict:
    return {
        "version": PROTOCOL["version"],
        "requestId": str(uuid.uuid4()),
        "operation": operation,
        "arguments": {} if arguments is None else arguments,
    }


def encoded(value: dict) -> bytes:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


@contextmanager
def authenticated_client(*, expired: bool = False):
    expiry = datetime.now(UTC) + timedelta(seconds=-60 if expired else 3600)
    app = create_app(settings_for_tests(desktop_token=KEY, desktop_token_expires_at=expiry))
    with TestClient(app) as client:
        resources = app.state.resources
        original = resources.redis
        decision = mock.AsyncMock()
        decision.set.return_value = True
        resources.redis = decision
        try:
            yield client, decision
        finally:
            resources.redis = original


def send(
    client: TestClient,
    value: dict,
    *,
    key: str = KEY,
    timestamp: int | None = None,
    extra: dict | None = None,
):
    body = encoded(value)
    headers = signed_headers(
        key,
        "POST",
        PROTOCOL["path"],
        body,
        request_id=value["requestId"],
        timestamp=timestamp,
        names=PROTOCOL["headers"],
        version=PROTOCOL["version"],
    )
    return client.post(
        PROTOCOL["path"],
        content=body,
        headers={**headers, "Content-Type": "application/json", **(extra or {})},
    )


def manifest(files: list[dict[str, str]]) -> str:
    parts = []
    for item in sorted(files, key=lambda row: row["path"].encode("utf-8")):
        content = item["content"].encode("utf-8")
        parts.append(
            item["path"].encode("utf-8")
            + b"\0"
            + str(len(content)).encode("ascii")
            + b":"
            + hashlib.sha256(content).hexdigest().encode("ascii")
            + b"\n"
        )
    return hashlib.sha256(b"".join(parts)).hexdigest()


class DesktopAuthenticationTests:
    def test_authentication_material_is_refused_before_replay_and_domain_io(self):
        forms = [
            KEY,
            KEY.upper(),
            base64.b64encode(KEY.encode()).decode(),
            "".join(f"%{value:02x}" for value in KEY.encode()),
            "".join(f"\\u{ord(value):04x}" for value in KEY),
        ]
        with authenticated_client() as (client, redis):
            for index, value in enumerate(forms):
                request = envelope("start", {"task": value})
                response = send(client, request)
                assert response.status_code == 400
                assert response.json()["code"] == "AUTHENTICATION_MATERIAL_REFUSED", (
                    f"bounded form index {index}"
                )
                assert KEY not in response.text
            redis.set.assert_not_awaited()
            assert send(client, envelope()).status_code == 200

    def test_desktop_credential_remains_a_secret_type_and_safe_dump_redacts_it(self):
        from pydantic import SecretStr

        settings = settings_for_tests(
            desktop_token=KEY, desktop_token_expires_at=datetime.now(UTC) + timedelta(hours=1)
        )
        assert isinstance(settings.desktop_token, SecretStr)
        assert settings.safe_dump()["desktop_token"] == "[REDACTED]"
        assert KEY not in json.dumps(settings.safe_dump())

    def test_hardened_mode_refuses_every_unauthenticated_domain_family(self):
        with authenticated_client() as (client, redis):
            for path in (
                "/api/v1/agents",
                "/api/v1/agent-runs",
                "/api/v1/gateway/models",
                "/api/v1/quality-runs",
                PROTOCOL["path"],
                "/api/v1/unknown",
            ):
                result = client.get(path)
                assert result.status_code == 401
                assert result.json()["code"] == "AUTHENTICATION_REQUIRED"
            redis.set.assert_not_awaited()
            assert client.get("/health").status_code == 200

    def test_valid_request_authenticates_exact_response_bytes_and_contract(self):
        with authenticated_client() as (client, redis):
            value = envelope()
            response = send(client, value)
            assert response.status_code == 200
            assert response.json()["data"]["authenticated"] is True
            assert response.json()["data"]["protocolDigest"] == PROTOCOL_DIGEST
            assert response.headers[PROTOCOL["headers"]["signature"]] == response_signature(
                KEY, value["requestId"], 200, response.content, version=PROTOCOL["version"]
            )
            assert KEY not in response.text
            redis.set.assert_awaited_once()

    def test_invalid_signature_is_refused_before_replay_or_domain_io(self):
        with authenticated_client() as (client, redis):
            response = send(client, envelope(), key=KEY[::-1])
            assert response.status_code == 401
            assert response.json()["code"] == "AUTHENTICATION_INVALID"
            redis.set.assert_not_awaited()

    def test_expired_credential_and_stale_clock_are_distinct_refusals(self):
        with authenticated_client(expired=True) as (client, redis):
            assert send(client, envelope()).json()["code"] == "AUTHENTICATION_EXPIRED"
            redis.set.assert_not_awaited()
        with authenticated_client() as (client, redis):
            assert (
                send(client, envelope(), timestamp=int(time.time()) - 120).json()["code"]
                == "AUTHENTICATION_STALE"
            )
            redis.set.assert_not_awaited()

    def test_replay_requires_atomic_redis_claim_and_operational_failure_is_closed(self):
        with authenticated_client() as (client, redis):
            redis.set.side_effect = [True, False, RuntimeError("unit state boundary unavailable")]
            value = envelope()
            assert send(client, value).status_code == 200
            assert send(client, value).json()["code"] == "AUTHENTICATION_REPLAY"
            assert send(client, envelope()).json()["code"] == "AUTHENTICATION_STATE_UNAVAILABLE"
            first, second = redis.set.await_args_list[:2]
            assert first.args[0] == second.args[0]
            assert first.kwargs == {"nx": True, "ex": PROTOCOL["replaySeconds"]}
            assert KEY not in first.args[0]

    def test_browser_origin_and_duplicate_authentication_headers_are_refused(self):
        with authenticated_client() as (client, redis):
            assert (
                send(client, envelope(), extra={"Origin": "http://localhost:4200"}).json()["code"]
                == "BROWSER_ORIGIN_REFUSED"
            )
            value = envelope()
            body = encoded(value)
            headers = signed_headers(
                KEY,
                "POST",
                PROTOCOL["path"],
                body,
                request_id=value["requestId"],
                names=PROTOCOL["headers"],
                version=PROTOCOL["version"],
            )
            pairs = [*headers.items(), (PROTOCOL["headers"]["signature"], "0" * 64)]
            assert client.post(PROTOCOL["path"], content=body, headers=pairs).status_code == 401
            redis.set.assert_not_awaited()

    def test_legacy_mode_is_explicitly_unavailable_to_desktop_clients(self):
        with TestClient(create_app(settings_for_tests())) as client:
            result = client.post(PROTOCOL["path"], json=envelope())
            assert result.status_code == 503
            assert result.json()["code"] == "DESKTOP_MODE_NOT_CONFIGURED"
            assert client.get("/api/v1/agents").status_code == 200

    def test_domain_read_uses_real_registry_after_authentication(self):
        with authenticated_client() as (client, _):
            response = send(client, envelope("teams"))
            assert response.status_code == 200
            teams = response.json()["data"]
            assert teams and any(item["team"] == "coding" for item in teams)

    def test_body_identity_must_match_authenticated_identity(self):
        with authenticated_client() as (client, _):
            value = envelope()
            body = encoded(value)
            headers = signed_headers(
                KEY,
                "POST",
                PROTOCOL["path"],
                body,
                names=PROTOCOL["headers"],
                version=PROTOCOL["version"],
            )
            response = client.post(PROTOCOL["path"], content=body, headers=headers)
            assert response.status_code == 400
            assert response.json()["code"] == "REQUEST_ID_MISMATCH"

    def test_configuration_requires_explicit_secret_expiration_pair(self):
        for overrides in (
            {"desktop_token": KEY},
            {"desktop_token_expires_at": datetime.now(UTC)},
            {"desktop_token": "short", "desktop_token_expires_at": datetime.now(UTC)},
            {"desktop_token": KEY, "desktop_token_expires_at": datetime.now()},
        ):
            with pytest.raises(ValueError):
                settings_for_tests(**overrides)
        assert settings_for_tests(desktop_token_expires_at="").desktop_token_expires_at is None


class DesktopContractTests:
    def test_valid_closed_request_and_absent_wrong_type_wrong_value_are_distinct(self):
        value = envelope("events", {"runId": str(uuid.uuid4()), "after": 0})
        assert parse_request(encoded(value)) == value
        for arguments, expected in (
            ({}, "FIELD_MISSING"),
            ({"runId": 42, "after": 0}, "FIELD_TYPE_INVALID"),
            ({"runId": "bad", "after": 0}, "FIELD_VALUE_INVALID"),
            ({"runId": str(uuid.uuid4()), "after": True}, "FIELD_TYPE_INVALID"),
        ):
            with pytest.raises(DesktopError) as caught:
                parse_request(encoded(envelope("events", arguments)))
            assert caught.value.code == expected

    def test_version_operation_extra_duplicate_and_nonfinite_fields_are_refused(self):
        for value, expected in (
            ({**envelope(), "version": "future"}, "VERSION_UNSUPPORTED"),
            ({**envelope(), "operation": "execute-host"}, "OPERATION_UNKNOWN"),
            ({**envelope(), "command": "ignored"}, "FIELD_UNKNOWN"),
        ):
            with pytest.raises(DesktopError) as caught:
                parse_request(encoded(value))
            assert caught.value.code == expected
        for data in (b'{"operation":0,"operation":1}', b'{"x":NaN}', b"\xff"):
            with pytest.raises(DesktopError):
                parse_request(data)

    def test_unicode_request_byte_bound_is_enforced_before_parsing(self):
        with pytest.raises(DesktopError) as caught:
            parse_request(b" " * (PROTOCOL["maxRequestBytes"] + 1))
        assert caught.value.code == "REQUEST_TOO_LARGE"
        with pytest.raises(DesktopError):
            parse_request(encoded(envelope("snapshot", {"files": [], "manifestDigest": "0" * 64})))


class DesktopSnapshotTests:
    def test_clean_snapshot_has_exact_consent_identity_and_deterministic_tar_bytes(self):
        files = [
            {"path": "src/main.py", "content": "print('olá')\r\n"},
            {"path": "README.md", "content": "A clean consented fixture.\n"},
        ]
        digest = manifest(files)
        first, observed = snapshot_bytes(files, digest)
        second, _ = snapshot_bytes(list(reversed(files)), digest)
        assert first == second and observed == digest
        with tarfile.open(fileobj=io.BytesIO(first), mode="r:gz") as archive:
            assert archive.getnames() == ["README.md", "src/main.py"]
            assert archive.extractfile("src/main.py").read() == files[0]["content"].encode("utf-8")
            assert all(member.isfile() and member.mode == 0o644 for member in archive.getmembers())

    def test_unsafe_excluded_and_case_ambiguous_paths_are_refused(self):
        for path in (
            "../escape",
            "/absolute",
            "a//b",
            "a/./b",
            "a\\b",
            "C:/file",
            "NUL.txt",
            "a/.env",
            "a/.git/config",
            "a/file.pem",
            "a/b. ",
            "a/\x00b",
            "e\u0301.txt",
            ".",
            "a/?file",
            "a/a|b",
            'a/a"b',
            "a/\u202eb.txt",
        ):
            files = [{"path": path, "content": "clean"}]
            with pytest.raises(DesktopError) as caught:
                snapshot_bytes(files, manifest(files))
            assert caught.value.code == "SNAPSHOT_PATH_REFUSED"
        files = [{"path": "A.txt", "content": "a"}, {"path": "a.txt", "content": "b"}]
        with pytest.raises(DesktopError):
            snapshot_bytes(files, manifest(files))

    def test_changed_inventory_and_decoded_size_limits_are_refused(self):
        files = [{"path": "main.py", "content": "clean"}]
        with pytest.raises(DesktopError) as caught:
            snapshot_bytes(files, "0" * 64)
        assert caught.value.code == "SNAPSHOT_CONSENT_MISMATCH"
        files = [{"path": "main.py", "content": "é" * PROTOCOL["maxFileBytes"]}]
        with pytest.raises(DesktopError) as caught:
            snapshot_bytes(files, manifest(files))
        assert caught.value.code == "SNAPSHOT_TOO_LARGE"


class DesktopSnapshotSecurityTests:
    def test_secret_and_scanner_failure_cannot_reach_lookup_or_storage(self):
        marker = "gh" + "p_" + "q" * 24
        assert find_secret_kinds(marker)
        resources = SimpleNamespace(minio=mock.Mock(), session_factory=mock.Mock())
        files = [{"path": "main.py", "content": marker}]
        with pytest.raises(DesktopError) as caught:
            asyncio.run(
                store_snapshot(resources, {"files": files, "manifestDigest": manifest(files)})
            )
        assert caught.value.code == "SNAPSHOT_SECRET_REFUSED"
        clean = [{"path": "main.py", "content": "clean"}]
        with (
            mock.patch(
                "iacode_api.desktop_snapshots.find_secret_kinds",
                side_effect=RuntimeError("unit scan unavailable"),
            ),
            pytest.raises(DesktopError) as caught,
        ):
            asyncio.run(
                store_snapshot(resources, {"files": clean, "manifestDigest": manifest(clean)})
            )
        assert caught.value.code == "SNAPSHOT_SCAN_UNAVAILABLE"
        resources.minio.put_object.assert_not_called()
        resources.session_factory.assert_not_called()

    def test_real_asgi_refusal_does_not_echo_or_store_adverse_bytes(self):
        marker = "gh" + "p_" + "q" * 24
        assert find_secret_kinds(marker)
        files = [{"path": "main.py", "content": marker}]
        with (
            authenticated_client() as (client, _),
            mock.patch.object(client.app.state.resources.minio, "put_object") as put,
        ):
            response = send(
                client, envelope("snapshot", {"files": files, "manifestDigest": manifest(files)})
            )
            assert response.status_code == 400
            assert response.json()["code"] == "SNAPSHOT_SECRET_REFUSED"
            assert marker not in response.text
            put.assert_not_called()
