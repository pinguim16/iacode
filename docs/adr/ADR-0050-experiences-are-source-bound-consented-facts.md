# ADR-0050 — Experiences are source-bound consented facts

Status: Accepted
Date: 2026-10-17
Owners: GATE 6 — Experience Store

## Context

Gate5 is sealed and the owner explicitly authorized Gate6, with independent M2 audit deferred.
The Foundation already has an experiences envelope/JSONB body. Runtime and quality records hold
observable identities, outcomes, tools and immutable evidence, while prompts/private reasoning are
not legitimate reusable experiences. An arbitrary JSON upload would turn privacy into caller discipline.

## Decision

services/experience is a provider-neutral in-process domain library with closed shared contracts,
consumed versioned policy and source/store ports. apps/api supplies real PostgreSQL/source adapters
and authenticated project-scoped endpoints. It does not add another deployment, host execution,
provider invocation, vector index, retrieval system or quality-verdict authority.

Capture selects exact completed source IDs and explicit storage-only consent. Trusted adapters
project only allowlisted observable columns and immutable quality references. No caller-supplied
experience body, raw transcript, arbitrary annotation, private reasoning, provider response, verdict
or rights grant is accepted. Unobserved metadata stays unknown. Existing quality verification owns
the source verdict/evidence; experience capture references and verifies it rather than submitting one.

New documents use a closed versioned schema covering every canonical experience category; empty or
unknown categories state the observation limit rather than fabricate an event. Canonical normalized
bytes/digest bind content and provenance. Full payload secret/known-authorization checks precede
durable writes and delivery; errors/audit/log records contain only bounded safe identifiers/codes.

Extend the existing experiences table and add only its minimal audit facts. Legacy rows retain
their historical envelope/permissions but remain quarantined from the current API until a separately
governed valid capture; migration never promotes unvalidated legacy JSON. A transaction binds the
new immutable payload, lineage, rights, request identity and capture audit fact. Database constraints,
uniqueness and immutability guards supplement application validation. Reads verify schema, digest,
lineage, source evidence, rights and retention before data leaves storage.

## Evidence and verification

The derived Gate6 requirements include closed/privacy input, actual migration up/down/check,
source-bound real PostgreSQL/HTTP round-trip, concurrent retry, corrupt recovery, auth/project/rights
refusal, actual provider/sandbox/quality lineage, current full verification and all internal controls.
This ADR records a decision, not an executed PASS. Evidence belongs in GATE-6-CP-0001.

## Alternatives considered

- Arbitrary experience/transcript ingestion was rejected: exclusion of private content cannot rest
  on undocumented free-form payload conventions.
- A second experience database/object body was rejected: JSONB is bounded and permits one atomic
  capture/audit transaction without a new cross-store commit protocol.
- A new network microservice was rejected: it adds deployment/auth/availability boundaries without
  a present independent consumer. Ports preserve future separation without a production fake.
- Automatic capture of every run was rejected: operational presence is not informed storage consent.

## Consequences and risks

Capture is intentionally factual and conservative. Free-form narratives, source code, raw tool
output and model text are not copied. Actual command/file references and hashes are retained, not
private source bodies. Catalog/provider/effort observations are never inferred from configuration.
No positive reuse grant is introduced without a separate proven governance mechanism. RAG/training/
distillation stay denied; Gate6 stores metadata, not a learning pipeline. A trusted local OS and
database administrator remain within the existing trust model; digests are not anonymization or signatures.

## Reversal strategy and related artifacts

Ports permit extracting a separate service later with versioned contracts/migrations. A broader
ingestion/grant model requires a new ADR, rights evidence, adverse tests and owner-scoped authority.
See MASTER-PLAN.md, GATE-6-CHECKLIST.md, ADR-0037, the provenance/training policies and ADR-0051.
