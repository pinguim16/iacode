"""Closed knowledge wire contracts: permitted source projections, never executable instructions."""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import AwareDatetime, Field, field_validator, model_validator

from iacode_contracts.experience import Code, Digest, ExperienceModel, Identity

Lexeme = Annotated[str, Field(min_length=1, max_length=128)]
SourceKind = Literal["curated", "experience"]
KnowledgeState = Literal["ACTIVE", "INVALIDATED", "EXPIRED", "DELETED"]
KNOWLEDGE_STATES = ("ACTIVE", "INVALIDATED", "EXPIRED", "DELETED")
KNOWLEDGE_EVENTS = ("INDEXED", "INVALIDATED", "EXPIRED", "DELETED")


class KnowledgePolicy(ExperienceModel):
    schemaVersion: Literal["1.0.0"]
    indexVersion: Literal["unicode-lexical-v1"]
    maxRequestBytes: int = Field(ge=256, le=16384)
    maxRegistryBytes: int = Field(ge=1024, le=1048576)
    maxSourceBytes: int = Field(ge=256, le=262144)
    maxSourceChars: int = Field(ge=1, le=65536)
    maxBodyBytes: int = Field(ge=1024, le=524288)
    maxSources: int = Field(ge=1, le=256)
    maxChunks: int = Field(ge=1, le=128)
    maxChunkChars: int = Field(ge=1, le=2048)
    maxChunkTokens: int = Field(ge=1, le=512)
    maxTokenChars: int = Field(ge=1, le=128)
    maxQueryChars: int = Field(ge=1, le=512)
    maxQueryTokens: int = Field(ge=1, le=32)
    maxCandidates: int = Field(ge=1, le=512)
    maxResults: int = Field(ge=1, le=20)
    maxResponseBytes: int = Field(ge=2048, le=1048576)
    maxPageSize: int = Field(ge=1, le=50)
    defaultRetentionSeconds: int = Field(ge=1, le=7776000)
    maxRetentionSeconds: int = Field(ge=1, le=7776000)
    sourceCaptureMaxAgeSeconds: int = Field(ge=1, le=7776000)
    maxGrantValiditySeconds: int = Field(ge=1, le=7776000)
    tombstoneRetentionSeconds: int = Field(ge=1, le=31536000)
    sweepIntervalSeconds: int = Field(ge=1, le=3600)
    batchSize: int = Field(ge=1, le=1000)
    operationTimeoutSeconds: int = Field(ge=1, le=60)

    @model_validator(mode="after")
    def coherent_windows(self) -> KnowledgePolicy:
        if self.defaultRetentionSeconds > self.maxRetentionSeconds:
            raise ValueError("default retention exceeds policy maximum")
        if self.tombstoneRetentionSeconds < self.sourceCaptureMaxAgeSeconds:
            raise ValueError("tombstones must cover source recapture age")
        if self.maxResponseBytes < self.maxBodyBytes * 2:
            raise ValueError("response bound must cover the complete document envelope")
        return self


class CuratedArtifact(ExperienceModel):
    schemaVersion: Literal["1.0.0"]
    classification: Literal["curated-project-knowledge"]
    createdAt: AwareDatetime
    title: str = Field(min_length=1, max_length=256)
    text: str = Field(min_length=1, max_length=65536)

    @field_validator("title", "text")
    @classmethod
    def meaningful_text(cls, value: str) -> str:
        if not value.strip() or any(ord(char) < 32 and char not in "\r\n\t" for char in value):
            raise ValueError("blank or control-bearing source text")
        return value


class SourceEntry(ExperienceModel):
    projectId: Identity
    sourceId: Identity
    revision: Code
    artifactPath: str = Field(min_length=1, max_length=256)
    sourceDigest: Digest
    grantPath: str = Field(min_length=1, max_length=256)
    grantDigest: Digest


class SourceRegistry(ExperienceModel):
    schemaVersion: Literal["1.0.0"]
    sources: tuple[SourceEntry, ...] = Field(max_length=256)

    @model_validator(mode="after")
    def one_current_revision(self) -> SourceRegistry:
        keys = [(entry.projectId, entry.sourceId) for entry in self.sources]
        if len(keys) != len(set(keys)):
            raise ValueError("ambiguous current source registry")
        return self


class SourceGrant(ExperienceModel):
    schemaVersion: Literal["1.0.0"]
    kind: Literal["operator-reviewed-source-grant"]
    grantId: Identity
    projectId: Identity
    sourceId: Identity
    revision: Code
    sourceDigest: Digest
    ownership: str = Field(min_length=1, max_length=128)
    license: str = Field(min_length=1, max_length=128)
    authority: str = Field(min_length=1, max_length=256)
    evidence: str = Field(min_length=1, max_length=1024)
    reviewed: bool
    status: Literal["ACTIVE", "REVOKED"]
    storageAllowed: bool
    ragAllowed: bool
    trainingAllowed: Literal[False]
    distillationAllowed: Literal[False]
    validFrom: AwareDatetime
    validUntil: AwareDatetime

    @model_validator(mode="after")
    def ordered_validity(self) -> SourceGrant:
        if self.validUntil <= self.validFrom:
            raise ValueError("grant validity must be ordered")
        return self


class IngestKnowledge(ExperienceModel):
    sourceKind: SourceKind
    sourceId: Identity
    revision: Code
    storageConsent: Literal[True]
    idempotencyKey: Identity
    retentionSeconds: int | None = Field(default=None, ge=1, le=7776000)

    @field_validator("storageConsent", mode="before")
    @classmethod
    def explicit_boolean_consent(cls, value: object) -> object:
        if value is not True:
            raise ValueError("explicit boolean storage consent is required")
        return value


class SearchKnowledge(ExperienceModel):
    query: str = Field(min_length=1, max_length=512)
    limit: int = Field(default=10, ge=1, le=20)


class KnowledgeProvenance(ExperienceModel):
    sourceKind: Literal["curated"]
    sourceId: Identity
    revision: Code
    sourceDigest: Digest
    artifactCreatedAt: AwareDatetime
    grantDigest: Digest
    grant: SourceGrant


class KnowledgeChunk(ExperienceModel):
    chunkId: Digest
    ordinal: int = Field(ge=0, le=127)
    start: int = Field(ge=0, le=65535)
    end: int = Field(ge=1, le=65536)
    text: str = Field(min_length=1, max_length=2048)
    digest: Digest
    tokens: tuple[Lexeme, ...] = Field(max_length=512)

    @model_validator(mode="after")
    def exact_coordinates(self) -> KnowledgeChunk:
        if self.end - self.start != len(self.text):
            raise ValueError("chunk coordinates must describe its exact text")
        if tuple(sorted(set(self.tokens))) != self.tokens:
            raise ValueError("index tokens must be a unique ordered set")
        return self


class UntrustedKnowledge(ExperienceModel):
    untrustedContent: Literal[True] = True

    @field_validator("untrustedContent", mode="before")
    @classmethod
    def exact_untrusted_marker(cls, value: object) -> object:
        if value is not True:
            raise ValueError("the untrusted marker requires exact true")
        return value


class KnowledgeDocument(UntrustedKnowledge):
    schemaVersion: Literal["1.0.0"]
    projectId: Identity
    title: str = Field(min_length=1, max_length=256)
    indexVersion: Literal["unicode-lexical-v1"]
    policyDigest: Digest
    unicodeDataVersion: Code
    retentionSeconds: int = Field(ge=1, le=7776000)
    provenance: KnowledgeProvenance
    chunks: tuple[KnowledgeChunk, ...] = Field(min_length=1, max_length=128)

    @model_validator(mode="after")
    def coherent_source(self) -> KnowledgeDocument:
        source = self.provenance
        grant = source.grant
        if (self.projectId, source.sourceId, source.revision, source.sourceDigest) != (
            grant.projectId,
            grant.sourceId,
            grant.revision,
            grant.sourceDigest,
        ):
            raise ValueError("source and grant identity must agree")
        if not grant.storageAllowed or not grant.ragAllowed or not grant.reviewed:
            raise ValueError("a document requires explicit permitted reuse")
        if grant.status != "ACTIVE":
            raise ValueError("revoked grants cannot support a document")
        if [chunk.ordinal for chunk in self.chunks] != list(range(len(self.chunks))):
            raise ValueError("chunk order must be complete")
        if self.chunks[0].start != 0 or any(
            left.end != right.start
            for left, right in zip(self.chunks, self.chunks[1:], strict=False)
        ):
            raise ValueError("chunks must cover one contiguous source projection")
        return self


class KnowledgeCitation(ExperienceModel):
    documentId: Identity
    sourceKind: Literal["curated"]
    sourceId: Identity
    revision: Code
    sourceDigest: Digest
    grantDigest: Digest
    chunkId: Digest
    chunkDigest: Digest
    pointer: Literal["/text"] = "/text"
    coordinateSystem: Literal["unicode-codepoints-start-inclusive-end-exclusive"] = (
        "unicode-codepoints-start-inclusive-end-exclusive"
    )
    start: int = Field(ge=0, le=65535)
    end: int = Field(ge=1, le=65536)


class KnowledgeHit(UntrustedKnowledge):
    citation: KnowledgeCitation
    excerpt: str = Field(min_length=1, max_length=2048)
    score: int = Field(ge=1)
    matchedTokens: tuple[Lexeme, ...] = Field(min_length=1, max_length=32)
