# ADR-0032 — Quality evidence is scanned before durable commit

Status: Accepted
Date: 2026-10-10
Owners: GATE 4 — Quality Engine

## Context

Quality evidence contains complete serialized runner output. Key-aware redaction keeps ordinary
logs readable, but it cannot prove that an innocuously named field does not contain a
credential-shaped value. The independent `G4-X7` attack demonstrated the gap: a value recognized by
the canonical repository scanner crossed the activity boundary, was stored in MinIO, received
immutable metadata, and resolved successfully.

Content addressing makes the ordering significant. Scanning after digest lookup permits an
existing object to bypass containment; scanning after object upload creates prohibited durable
bytes even if metadata is later refused. A scanner failure cannot be treated as a clean result.

## Decision

`packages/common` owns the canonical credential-shape taxonomy used by both repository controls and
runtime evidence containment. The evidence store decodes the exact serialized bytes with a
replacement-safe UTF-8 view and scans them before digest calculation, repository lookup, object
stat, object upload, or metadata commit.

A match raises `EVIDENCE_SECRET_DETECTED`; inability to scan raises
`EVIDENCE_SECRET_SCAN_FAILED`. Both contain only stable non-secret text. The recording activity
catches only these containment codes and writes an immutable sanitized `ERROR` result with no
evidence or finding payload. Normal verdict derivation therefore returns `FAIL` for the failed
check and missing required evidence. Other storage failures retain their existing error behavior.

Resolution downloads and scans stored bytes again before accepting size and digest. This prevents
legacy, externally injected, or otherwise pre-existing secret-bearing objects from supporting a
verdict. Redaction remains defense in depth but is not the persistence authorization decision.

## Consequences

Credential-shaped output is unavailable as quality evidence and must be diagnosed through the
stable containment code. A false positive fails the run closed and requires changing or explicitly
sanitizing the producer; operators cannot override the decision by editing evidence metadata. A
scanner taxonomy change affects both runtime containment and repository delivery controls, so one
regression suite can prove they do not drift.

The workflow remains terminal and auditable even when evidence is rejected: the sanitized result
is durable, metrics count the failed check but not an evidence write, and no prohibited value is
copied into summaries, findings, logs, or verdicts.

## Alternatives considered

Relying only on recursive redaction was rejected because arbitrary field names cannot classify
their values. Scanning after upload was rejected because quarantine would still begin with a
durable prohibited object. Deleting a rejected object was rejected because deletion is not atomic
with every object-store observer and contradicts immutable evidence semantics. Letting the
activity fail and retry forever was rejected because it could strand the workflow without a
terminal quality result.
