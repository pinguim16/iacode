"""Closed policy, pre-effect validation and source/store ports (ADR-0050/0051)."""

from __future__ import annotations

import base64
import binascii
import hashlib
import json
import re
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Literal, Protocol

from iacode_common.secret_scanning import find_secret_kinds, iter_secret_scan_views
from iacode_contracts.experience import CaptureExperience, ExperienceDocument, ExperienceModel
from pydantic import Field, ValidationError, model_validator


class ExperienceError(Exception):
    """Only fixed codes cross the adapter boundary; never exception/input text."""

    def __init__(self, code: str) -> None:
        super().__init__("experience operation refused")
        self.code = code


class ExperiencePolicy(ExperienceModel):
    schemaVersion: Literal["1.0.0"]
    defaultRetentionSeconds: int = Field(ge=1, le=7776000)
    maxRetentionSeconds: int = Field(ge=1, le=7776000)
    captureMaxAgeSeconds: int = Field(ge=1, le=7776000)
    tombstoneRetentionSeconds: int = Field(ge=1, le=31536000)
    sweepIntervalSeconds: int = Field(ge=1, le=3600)
    batchSize: int = Field(ge=1, le=1000)
    maxFacts: int = Field(ge=1, le=1000)
    maxBodyBytes: int = Field(ge=1024, le=262144)
    maxRequestBytes: int = Field(ge=256, le=4096)
    maxPageSize: int = Field(ge=1, le=50)

    @model_validator(mode="after")
    def finite_window(self) -> ExperiencePolicy:
        if self.defaultRetentionSeconds > self.maxRetentionSeconds:
            raise ValueError("default retention exceeds the maximum")
        if self.tombstoneRetentionSeconds < self.captureMaxAgeSeconds:
            raise ValueError("tombstones must cover the recapture window")
        return self


def _pairs(pairs: list[tuple[str, object]]) -> dict:
    result: dict = {}
    for key, value in pairs:
        if key in result:
            raise ExperienceError("JSON_DUPLICATE_KEY")
        result[key] = value
    return result


def _constant(_value: str) -> None:
    raise ExperienceError("JSON_NONFINITE")


def canonical(value: object) -> bytes:
    try:
        return json.dumps(
            value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
        ).encode("utf-8", errors="strict")
    except (UnicodeError, ValueError, TypeError, RecursionError) as error:
        raise ExperienceError("CONTENT_ENCODING_INVALID") from error


def digest(value: object) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def parse_json(raw: bytes, maximum: int) -> dict:
    if len(raw) > maximum:
        raise ExperienceError("CONTENT_TOO_LARGE")
    try:
        value = json.loads(
            raw.decode("utf-8", errors="strict"), object_pairs_hook=_pairs, parse_constant=_constant
        )
        if not isinstance(value, dict):
            raise ExperienceError("CONTENT_TYPE_INVALID")
        # Surrogate and depth checks precede Pydantic and every effect.
        stack = [(value, 0)]
        while stack:
            item, depth = stack.pop()
            if depth > 12:
                raise ExperienceError("CONTENT_DEPTH_INVALID")
            if isinstance(item, dict):
                stack.extend((x, depth + 1) for pair in item.items() for x in pair)
            elif isinstance(item, list):
                stack.extend((x, depth + 1) for x in item)
            elif isinstance(item, str):
                item.encode("utf-8", errors="strict")
        return value
    except (UnicodeError, ValueError, RecursionError) as error:
        raise ExperienceError("JSON_INVALID") from error


def load_policy(path: Path) -> ExperiencePolicy:
    raw = path.read_bytes()
    value = parse_json(raw, 4096)
    return ExperiencePolicy.model_validate_json(canonical(value))


def require_safe(raw: bytes, known_credentials: tuple[str, ...] = ()) -> None:
    try:
        text = raw.decode("utf-8", errors="strict")
        if find_secret_kinds(text):
            raise ExperienceError("SECRET_MATERIAL_REFUSED")
        # One declared base64 text layer is additionally inspected using the SAME taxonomy.
        # Arbitrary encryption/encoding is not claimed to be detectable. Decode work is linear
        # in the bounded body; binary/non-UTF8 blocks are not invented text observations.
        for candidate in re.finditer(r"[A-Za-z0-9+/_-]{24,}={0,2}", text):
            encoded_text = candidate.group(0)
            try:
                decoded = base64.b64decode(
                    encoded_text + "=" * (-len(encoded_text) % 4), altchars=b"-_", validate=True
                ).decode("utf-8", "strict")
            except (binascii.Error, UnicodeError):
                continue
            if find_secret_kinds(decoded):
                raise ExperienceError("SECRET_MATERIAL_REFUSED")
        forms: set[str] = set()
        for credential in known_credentials:
            if not credential:
                continue
            for spelling in (credential, credential.upper()):
                encoded = spelling.encode("utf-8")
                forms.update(
                    (
                        spelling.casefold(),
                        encoded.hex(),
                        base64.b64encode(encoded).decode().casefold(),
                        base64.urlsafe_b64encode(encoded).decode().rstrip("=").casefold(),
                        "".join(f"%{value:02x}" for value in encoded),
                        "".join(f"\\u{value:04x}" for value in encoded),
                    )
                )
        if any(
            any(form in view.casefold() for form in forms)
            for view, _ in iter_secret_scan_views(text)
        ):
            raise ExperienceError("AUTHORIZATION_MATERIAL_REFUSED")
    except ExperienceError:
        raise
    except Exception as error:
        raise ExperienceError("SECRET_SCAN_UNAVAILABLE") from error


def parse_capture(
    raw: bytes, policy: ExperiencePolicy, known_credentials: tuple[str, ...] = ()
) -> CaptureExperience:
    value = parse_json(raw, policy.maxRequestBytes)
    require_safe(canonical(value), known_credentials)
    try:
        request = CaptureExperience.model_validate_json(canonical(value))
    except ValidationError as error:
        if "storageConsent" not in value:
            code = "CONSENT_MISSING"
        elif type(value["storageConsent"]) is not bool:
            code = "CONSENT_TYPE_INVALID"
        elif value["storageConsent"] is not True:
            code = "CONSENT_DENIED"
        else:
            code = "CAPTURE_CONTRACT_INVALID"
        raise ExperienceError(code) from error
    if (
        request.retentionSeconds is not None
        and request.retentionSeconds > policy.maxRetentionSeconds
    ):
        raise ExperienceError("RETENTION_LIMIT_EXCEEDED")
    return request


def validate_document(
    body: dict, policy: ExperiencePolicy, known_credentials: tuple[str, ...] = ()
) -> ExperienceDocument:
    raw = canonical(body)
    parse_json(raw, policy.maxBodyBytes)
    require_safe(raw, known_credentials)
    try:
        document = ExperienceDocument.model_validate_json(raw)
    except ValidationError as error:
        raise ExperienceError("STORED_CONTRACT_INVALID") from error
    collections = (
        document.actions,
        document.toolCalls,
        document.commands,
        document.attempts,
        document.provider,
        document.model,
        document.failures,
        document.tests.checks,
    )
    if any(len(collection) > policy.maxFacts for collection in collections):
        raise ExperienceError("SOURCE_FACT_LIMIT_EXCEEDED")
    if document.provenance[0].digest != digest(document.task.model_dump(mode="json")):
        raise ExperienceError("PROVENANCE_DIGEST_INVALID")
    return document


@dataclass(frozen=True)
class StoredExperience:
    experience_id: str
    project_id: str
    source_run_id: str
    request_digest: str
    content_digest: str
    body: dict
    state: str
    created_at: datetime
    expires_at: datetime
    storage_allowed: bool
    reuse_allowed: tuple[bool, bool, bool]
    schema_version: int = 1
    replay: bool = False
    envelope_valid: bool = True


class SourcePort(Protocol):
    async def observe(
        self, project_id: str, request: CaptureExperience, now: datetime
    ) -> ExperienceDocument: ...

    async def verify(self, document: ExperienceDocument) -> None: ...


class StorePort(Protocol):
    async def by_request(self, project_id: str, request_id: str) -> StoredExperience | None: ...

    async def capture(
        self,
        project_id: str,
        request: CaptureExperience,
        document: ExperienceDocument,
        now: datetime,
        expires_at: datetime,
    ) -> StoredExperience: ...

    async def get(self, project_id: str, experience_id: str) -> StoredExperience: ...


@dataclass(frozen=True)
class ExperienceService:
    policy: ExperiencePolicy
    sources: SourcePort
    store: StorePort
    known_credentials: tuple[str, ...] = ()

    async def capture(
        self, project_id: str, request: CaptureExperience, now: datetime | None = None
    ) -> StoredExperience:
        now = now or datetime.now(UTC)
        existing = await self.store.by_request(project_id, request.idempotencyKey)
        if existing is not None:
            if existing.request_digest != digest(request.model_dump(mode="json")):
                raise ExperienceError("REQUEST_CONFLICT")
            await self.deliver(existing, now)
            return existing
        document = await self.sources.observe(project_id, request, now)
        validate_document(document.model_dump(mode="json"), self.policy, self.known_credentials)
        age = (now - document.task.finishedAt).total_seconds()
        if age < 0 or age >= self.policy.captureMaxAgeSeconds:
            raise ExperienceError("SOURCE_AGE_REFUSED")
        seconds = request.retentionSeconds or self.policy.defaultRetentionSeconds
        if seconds > self.policy.maxRetentionSeconds:
            raise ExperienceError("RETENTION_LIMIT_EXCEEDED")
        stored = await self.store.capture(
            project_id, request, document, now, now + timedelta(seconds=seconds)
        )
        if stored.replay:
            await self.deliver(stored, now)
        return stored

    async def deliver(
        self, stored: StoredExperience, now: datetime | None = None
    ) -> ExperienceDocument:
        now = now or datetime.now(UTC)
        if stored.schema_version != 1:
            raise ExperienceError("LEGACY_QUARANTINED")
        if stored.state != "ACTIVE" or not stored.storage_allowed or now >= stored.expires_at:
            raise ExperienceError("EXPERIENCE_UNAVAILABLE")
        if (
            not stored.envelope_valid
            or any(stored.reuse_allowed)
            or digest(stored.body) != stored.content_digest
        ):
            raise ExperienceError("STORED_INTEGRITY_INVALID")
        document = validate_document(stored.body, self.policy, self.known_credentials)
        if document.model_dump(mode="json") != stored.body:
            raise ExperienceError("STORED_CANONICAL_INVALID")
        if (
            document.task.projectId != stored.project_id
            or document.task.runId != stored.source_run_id
        ):
            raise ExperienceError("STORED_LINEAGE_INVALID")
        await self.sources.verify(document)
        return document
