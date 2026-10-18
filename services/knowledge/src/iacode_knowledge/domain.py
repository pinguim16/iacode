"""Permitted sources, exact deterministic spans and persistent source/store ports."""

from __future__ import annotations

import hashlib
import re
import unicodedata
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Protocol

from iacode_contracts.knowledge import (
    CuratedArtifact,
    IngestKnowledge,
    KnowledgeChunk,
    KnowledgeCitation,
    KnowledgeDocument,
    KnowledgeHit,
    KnowledgePolicy,
    KnowledgeProvenance,
    SearchKnowledge,
    SourceEntry,
    SourceGrant,
)
from iacode_experience import domain as content
from pydantic import BaseModel, ValidationError


class KnowledgeError(Exception):
    """Only fixed reason codes cross adapters; never source/query/driver exception text."""

    def __init__(self, code: str) -> None:
        super().__init__("knowledge operation refused")
        self.code = code


def canonical(value: object) -> bytes:
    try:
        return content.canonical(value)
    except content.ExperienceError as error:
        raise KnowledgeError(error.code) from error


def digest(value: object) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def index_fingerprint(policy: KnowledgePolicy) -> str:
    return digest(
        {
            "policy": policy.model_dump(mode="json"),
            "unicodeDataVersion": unicodedata.unidata_version,
        }
    )


def require_safe(raw: bytes, known_credentials: tuple[str, ...] = ()) -> None:
    try:
        content.require_safe(raw, known_credentials)
    except content.ExperienceError as error:
        raise KnowledgeError(error.code) from error


def decode[Model: BaseModel](
    raw: bytes, model: type[Model], maximum: int, known_credentials: tuple[str, ...] = ()
) -> Model:
    try:
        value = content.parse_json(raw, maximum)
        require_safe(raw, known_credentials)
        normalized = canonical(value)
        require_safe(normalized, known_credentials)
        return model.model_validate_json(normalized)
    except content.ExperienceError as error:
        raise KnowledgeError(error.code) from error
    except ValidationError as error:
        raise KnowledgeError("KNOWLEDGE_CONTRACT_INVALID") from error


def load_policy(path: Path) -> KnowledgePolicy:
    return decode(path.read_bytes(), KnowledgePolicy, 4096)


def parse_ingest(
    raw: bytes, policy: KnowledgePolicy, known_credentials: tuple[str, ...] = ()
) -> IngestKnowledge:
    try:
        value = content.parse_json(raw, policy.maxRequestBytes)
    except content.ExperienceError as error:
        raise KnowledgeError(error.code) from error
    require_safe(raw, known_credentials)
    if "storageConsent" not in value:
        raise KnowledgeError("CONSENT_MISSING")
    if type(value["storageConsent"]) is not bool:
        raise KnowledgeError("CONSENT_TYPE_INVALID")
    if value["storageConsent"] is not True:
        raise KnowledgeError("CONSENT_DENIED")
    request = decode(canonical(value), IngestKnowledge, policy.maxRequestBytes, known_credentials)
    if (
        request.retentionSeconds is not None
        and request.retentionSeconds > policy.maxRetentionSeconds
    ):
        raise KnowledgeError("RETENTION_LIMIT_EXCEEDED")
    return request


def tokens(text: str, maximum: int, max_token_chars: int) -> tuple[str, ...]:
    normalized = unicodedata.normalize("NFKC", text).casefold()
    values = tuple(sorted(set(re.findall(r"\w+", normalized, flags=re.UNICODE))))
    if len(values) > maximum or any(len(value) > max_token_chars for value in values):
        raise KnowledgeError("TOKEN_LIMIT_EXCEEDED")
    return values


def parse_search(
    raw: bytes, policy: KnowledgePolicy, known_credentials: tuple[str, ...] = ()
) -> tuple[SearchKnowledge, tuple[str, ...]]:
    try:
        value = content.parse_json(raw, policy.maxRequestBytes)
    except content.ExperienceError as error:
        raise KnowledgeError(error.code) from error
    require_safe(raw, known_credentials)
    if "query" not in value:
        raise KnowledgeError("QUERY_MISSING")
    if not isinstance(value["query"], str):
        raise KnowledgeError("QUERY_TYPE_INVALID")
    if not value["query"].strip():
        raise KnowledgeError("QUERY_EMPTY")
    if len(value["query"]) > policy.maxQueryChars:
        raise KnowledgeError("QUERY_LIMIT_EXCEEDED")
    request = decode(canonical(value), SearchKnowledge, policy.maxRequestBytes, known_credentials)
    if request.limit > policy.maxResults:
        raise KnowledgeError("RESULT_LIMIT_EXCEEDED")
    query_tokens = tokens(request.query, policy.maxQueryTokens, policy.maxTokenChars)
    if not query_tokens:
        raise KnowledgeError("QUERY_EMPTY")
    return request, query_tokens


@dataclass(frozen=True)
class AdmittedSource:
    entry: SourceEntry
    artifact: CuratedArtifact
    grant: SourceGrant


def validate_grant(
    entry: SourceEntry, grant: SourceGrant, project: str, policy: KnowledgePolicy, now: datetime
) -> None:
    if (project, entry.sourceId, entry.revision, entry.sourceDigest) != (
        grant.projectId,
        grant.sourceId,
        grant.revision,
        grant.sourceDigest,
    ) or entry.projectId != project:
        raise KnowledgeError("SOURCE_SCOPE_MISMATCH")
    if not grant.reviewed or not grant.storageAllowed or not grant.ragAllowed:
        raise KnowledgeError("REUSE_PERMISSION_DENIED")
    unknown = {"unknown", "unverified", "unspecified", "none", "n/a"}
    if any(
        not value.strip() or value.strip().casefold() in unknown
        for value in (grant.ownership, grant.license, grant.authority, grant.evidence)
    ):
        raise KnowledgeError("RIGHTS_EVIDENCE_UNVERIFIED")
    if grant.status != "ACTIVE":
        raise KnowledgeError("SOURCE_REVOKED")
    if not grant.validFrom <= now < grant.validUntil:
        raise KnowledgeError("SOURCE_GRANT_EXPIRED")
    if (grant.validUntil - grant.validFrom).total_seconds() > policy.maxGrantValiditySeconds:
        raise KnowledgeError("SOURCE_GRANT_LIMIT_EXCEEDED")


def validate_source(
    source: AdmittedSource, project: str, policy: KnowledgePolicy, now: datetime, *, capture: bool
) -> None:
    artifact = source.artifact
    validate_grant(source.entry, source.grant, project, policy, now)
    if artifact.createdAt > now:
        raise KnowledgeError("SOURCE_TIME_INVALID")
    if capture and (now - artifact.createdAt).total_seconds() > policy.sourceCaptureMaxAgeSeconds:
        raise KnowledgeError("SOURCE_TOO_OLD")
    if len(artifact.text) > policy.maxSourceChars:
        raise KnowledgeError("SOURCE_LIMIT_EXCEEDED")


def derive(
    source: AdmittedSource,
    project: str,
    retention: int,
    policy: KnowledgePolicy,
    known_credentials: tuple[str, ...] = (),
) -> KnowledgeDocument:
    artifact, entry = source.artifact, source.entry
    if retention < 1 or retention > policy.maxRetentionSeconds:
        raise KnowledgeError("RETENTION_LIMIT_EXCEEDED")
    policy_digest = index_fingerprint(policy)
    chunks = []
    start = 0
    while start < len(artifact.text):
        end = min(start + policy.maxChunkChars, len(artifact.text))
        if end < len(artifact.text):
            boundary = max(
                artifact.text.rfind("\n", start, end), artifact.text.rfind(" ", start, end)
            )
            if boundary >= start:
                end = boundary + 1
        excerpt = artifact.text[start:end]
        excerpt_digest = hashlib.sha256(excerpt.encode("utf-8")).hexdigest()
        identity = {
            "projectId": project,
            "sourceId": entry.sourceId,
            "revision": entry.revision,
            "sourceDigest": entry.sourceDigest,
            "grantDigest": entry.grantDigest,
            "policyDigest": policy_digest,
            "ordinal": len(chunks),
            "start": start,
            "end": end,
            "digest": excerpt_digest,
        }
        chunks.append(
            KnowledgeChunk(
                chunkId=digest(identity),
                ordinal=len(chunks),
                start=start,
                end=end,
                text=excerpt,
                digest=excerpt_digest,
                tokens=tokens(excerpt, policy.maxChunkTokens, policy.maxTokenChars),
            )
        )
        if len(chunks) > policy.maxChunks:
            raise KnowledgeError("CHUNK_LIMIT_EXCEEDED")
        start = end
    if not chunks or not any(chunk.tokens for chunk in chunks):
        raise KnowledgeError("SOURCE_EMPTY")
    document = KnowledgeDocument(
        schemaVersion="1.0.0",
        projectId=project,
        title=artifact.title,
        indexVersion=policy.indexVersion,
        policyDigest=policy_digest,
        unicodeDataVersion=unicodedata.unidata_version,
        retentionSeconds=retention,
        provenance=KnowledgeProvenance(
            sourceKind="curated",
            sourceId=entry.sourceId,
            revision=entry.revision,
            sourceDigest=entry.sourceDigest,
            artifactCreatedAt=artifact.createdAt,
            grantDigest=entry.grantDigest,
            grant=source.grant,
        ),
        chunks=tuple(chunks),
    )
    decode(
        canonical(document.model_dump(mode="json")),
        KnowledgeDocument,
        policy.maxBodyBytes,
        known_credentials,
    )
    return document


@dataclass(frozen=True)
class StoredKnowledge:
    document_id: str
    project_id: str
    source_kind: str
    source_id: str
    revision: str
    source_digest: str
    grant_digest: str
    policy_digest: str
    request_digest: str
    content_digest: str
    state: str
    created_at: datetime
    expires_at: datetime
    retention_ceiling: datetime
    purged_at: datetime | None
    source_created_at: datetime
    body: dict
    replay: bool = False


class SourcePort(Protocol):
    async def load(
        self, project: str, kind: str, source: str, revision: str, now: datetime, *, capture: bool
    ) -> AdmittedSource: ...


class StorePort(Protocol):
    async def publish(
        self, request: IngestKnowledge, document: KnowledgeDocument, now: datetime
    ) -> StoredKnowledge: ...

    async def get(self, project: str, document: str) -> StoredKnowledge: ...

    async def inventory(self, project: str, now: datetime) -> list[StoredKnowledge]: ...

    async def index_rows(
        self, project: str, document: str
    ) -> tuple[tuple[int, str, tuple[str, ...]], ...]: ...

    async def candidates(
        self, project: str, query: tuple[str, ...], policy_digest: str, now: datetime
    ) -> list[tuple[str, int]]: ...


INVALID_SOURCE_CODES = frozenset(
    {
        "REUSE_PERMISSION_DENIED",
        "RIGHTS_EVIDENCE_UNVERIFIED",
        "SOURCE_REVOKED",
        "SOURCE_GRANT_EXPIRED",
        "SOURCE_CHANGED",
        "SOURCE_NOT_FOUND",
        "SOURCE_TOO_OLD",
    }
)


class KnowledgeService:
    def __init__(
        self,
        policy: KnowledgePolicy,
        sources: SourcePort,
        store: StorePort,
        known_credentials: tuple[str, ...] = (),
    ) -> None:
        self.policy = policy
        self.sources = sources
        self.store = store
        self.known_credentials = known_credentials

    async def ingest(
        self, project: str, request: IngestKnowledge, now: datetime | None = None
    ) -> StoredKnowledge:
        fixed_clock = now
        now = now or datetime.now(UTC)
        request = parse_ingest(
            canonical(request.model_dump(mode="json")), self.policy, self.known_credentials
        )
        source = await self.sources.load(
            project, request.sourceKind, request.sourceId, request.revision, now, capture=True
        )
        validate_source(source, project, self.policy, now, capture=True)
        if (source.entry.sourceId, source.entry.revision) != (request.sourceId, request.revision):
            raise KnowledgeError("SOURCE_SCOPE_MISMATCH")
        retention = request.retentionSeconds or self.policy.defaultRetentionSeconds
        document = derive(source, project, retention, self.policy, self.known_credentials)
        stored = await self.store.publish(request, document, now)
        await self.deliver(stored, fixed_clock)
        return stored

    async def deliver(
        self, stored: StoredKnowledge, now: datetime | None = None
    ) -> KnowledgeDocument:
        fixed_clock = now
        now = now or datetime.now(UTC)
        if stored.state != "ACTIVE" or stored.purged_at is not None or now >= stored.expires_at:
            raise KnowledgeError("KNOWLEDGE_UNAVAILABLE")
        body = canonical(stored.body)
        document = decode(body, KnowledgeDocument, self.policy.maxBodyBytes, self.known_credentials)
        provenance = document.provenance
        if stored.content_digest != hashlib.sha256(body).hexdigest():
            raise KnowledgeError("STORED_DIGEST_INVALID")
        if stored.policy_digest != index_fingerprint(self.policy):
            raise KnowledgeError("INDEX_STALE")
        if (
            stored.project_id,
            stored.source_kind,
            stored.source_id,
            stored.revision,
            stored.source_digest,
            stored.grant_digest,
            stored.policy_digest,
            stored.source_created_at,
        ) != (
            document.projectId,
            provenance.sourceKind,
            provenance.sourceId,
            provenance.revision,
            provenance.sourceDigest,
            provenance.grantDigest,
            document.policyDigest,
            provenance.artifactCreatedAt,
        ):
            raise KnowledgeError("STORED_IDENTITY_INVALID")
        expected_expiry = min(
            stored.created_at + timedelta(seconds=document.retentionSeconds),
            provenance.grant.validUntil,
            stored.retention_ceiling,
        )
        if stored.expires_at != expected_expiry:
            raise KnowledgeError("STORED_RETENTION_INVALID")
        source = await self.sources.load(
            stored.project_id,
            stored.source_kind,
            stored.source_id,
            stored.revision,
            now,
            capture=False,
        )
        validate_source(source, stored.project_id, self.policy, now, capture=False)
        expected = derive(
            source,
            stored.project_id,
            document.retentionSeconds,
            self.policy,
            self.known_credentials,
        )
        if document != expected:
            raise KnowledgeError("SOURCE_CHANGED")
        actual_index = await self.store.index_rows(stored.project_id, stored.document_id)
        expected_index = tuple(
            (chunk.ordinal, chunk.digest, chunk.tokens) for chunk in document.chunks
        )
        if actual_index != expected_index:
            raise KnowledgeError("INDEX_CORRUPT")
        final_now = fixed_clock or datetime.now(UTC)
        if final_now >= stored.expires_at or final_now >= provenance.grant.validUntil:
            raise KnowledgeError("KNOWLEDGE_UNAVAILABLE")
        return document

    def citation(
        self, stored: StoredKnowledge, document: KnowledgeDocument, chunk: KnowledgeChunk
    ) -> KnowledgeCitation:
        source = document.provenance
        return KnowledgeCitation(
            documentId=stored.document_id,
            sourceKind=source.sourceKind,
            sourceId=source.sourceId,
            revision=source.revision,
            sourceDigest=source.sourceDigest,
            grantDigest=source.grantDigest,
            chunkId=chunk.chunkId,
            chunkDigest=chunk.digest,
            start=chunk.start,
            end=chunk.end,
        )

    async def search(
        self,
        project: str,
        request: SearchKnowledge,
        query: tuple[str, ...],
        now: datetime | None = None,
    ) -> list[KnowledgeHit]:
        fixed_clock = now
        now = now or datetime.now(UTC)
        request, expected_query = parse_search(
            canonical(request.model_dump(mode="json")), self.policy, self.known_credentials
        )
        if query != expected_query:
            raise KnowledgeError("QUERY_CONTRACT_INVALID")
        if request.limit > self.policy.maxResults or not query:
            raise KnowledgeError("RESULT_LIMIT_EXCEEDED")
        # Validate the bounded current publication set before matching. Otherwise a deleted or
        # corrupted index entry could silently hide a relevant result behind an empty success.
        documents: dict[str, tuple[StoredKnowledge, KnowledgeDocument] | None] = {}
        for stored in await self.store.inventory(project, now):
            try:
                document = await self.deliver(stored, fixed_clock)
                documents[stored.document_id] = stored, document
            except KnowledgeError as error:
                if error.code not in INVALID_SOURCE_CODES | {"KNOWLEDGE_UNAVAILABLE"}:
                    raise
                documents[stored.document_id] = None
        candidates = await self.store.candidates(
            project, query, index_fingerprint(self.policy), now
        )
        if len(candidates) > self.policy.maxCandidates:
            raise KnowledgeError("INDEX_CAPACITY_EXCEEDED")
        ranked = []
        for identifier, ordinal in candidates:
            if identifier not in documents:
                stored = await self.store.get(project, identifier)
                try:
                    document = await self.deliver(stored, fixed_clock)
                    documents[identifier] = (stored, document)
                except KnowledgeError as error:
                    if error.code not in INVALID_SOURCE_CODES | {"KNOWLEDGE_UNAVAILABLE"}:
                        raise
                    documents[identifier] = None
            pair = documents[identifier]
            if pair is None:
                continue
            stored, document = pair
            if ordinal < 0 or ordinal >= len(document.chunks):
                raise KnowledgeError("INDEX_CORRUPT")
            chunk = document.chunks[ordinal]
            matched = tuple(sorted(set(query) & set(chunk.tokens)))
            if not matched:
                raise KnowledgeError("INDEX_CORRUPT")
            score = len(matched)
            hit = KnowledgeHit(
                citation=self.citation(stored, document, chunk),
                excerpt=chunk.text,
                score=score,
                matchedTokens=matched,
            )
            ranked.append(
                (
                    (
                        -score,
                        len(chunk.text),
                        document.provenance.sourceId,
                        ordinal,
                        stored.document_id,
                    ),
                    hit,
                )
            )
        ranked.sort(key=lambda pair: pair[0])
        hits = [pair[1] for pair in ranked[: request.limit]]
        # Recheck the exact selected publications after collection, immediately before delivery.
        for identifier in sorted({hit.citation.documentId for hit in hits}):
            pair = documents[identifier]
            if pair is None:
                raise KnowledgeError("SOURCE_CHANGED")
            await self.deliver(pair[0], fixed_clock)
        self.safe_response({"results": [hit.model_dump(mode="json") for hit in hits]})
        return hits

    def safe_response(self, value: object) -> None:
        raw = canonical(value)
        if len(raw) > self.policy.maxResponseBytes:
            raise KnowledgeError("RESPONSE_LIMIT_EXCEEDED")
        require_safe(raw, self.known_credentials)
