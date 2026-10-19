# ADR-0058 — Immutable review Git reads use child-scoped long-path handling

Status: Accepted
Date: 2026-10-19
Owners: GATE 7 — immutable M2 review transport and Windows portability

## Context

The published runtime-v2 completes49 stages but fails its two owning immutable review tests and
Red Team portability attackT. In a fresh Windows checkout, Git interprets a full SHA:path
expression through a filesystem probe longer than the platform's default path boundary, although
the real tracked file is valid. Renaming or omitting published evidence would break its identity.

An actual isolated Git repository reproduces this with a240-character binary source and a
281-character object-expression probe. The current reader and bare Git fail; an explicit
child-scoped core.longpaths=true returns the same28 bytes. Owned/local and global configuration
remain unchanged, and the diagnostic owner is actually removed.

## Decision

Pass core.longpaths=true with Git's per-command -c option through the immutable review reader's
Git adapter. The override belongs only to that child invocation. Do not write repository/global
configuration, change parent environment, rename evidence, move tags, omit archive members or
weaken an existing reconstruction/declaration assertion.

Preserve exact binary output and current text/error semantics. A nonzero Git exit still raises
the original explicit failure. Execute real long-path object/premise, child-argument scope,
unchanged local/global settings and genuine bad-reference controls, followed by unchanged owning
reconstruction/declaration tests and complete current immutable assurance.

## Evidence

G7-INT-024/028, LSN-0151, failed runtime-v2 cmd-0143 and the exact archived real diagnosis own
the observations. The diagnosis is not an independent audit or a corrected current full run.
A new immutable source subject and every ordered internal control remain required.

## Alternatives Considered

- Change global or shared repository settings: rejected; other applications and users are outside
  this correction's authority.
- Shorten only the author's current checkout: rejected; independent transported checkouts may
  have legitimate longer prefixes.
- Rename/delete published observations or skip the failing archive member: rejected; neither
  preserves the subject or complete transport denominator.
- Replace the reader with a new batching protocol: deferred; the observed defect has a narrower
  proven child-scoped correction and does not require that structural expansion.

## Consequences

Legitimate long immutable object paths remain readable without persistent host configuration.
Existing archive names, bytes, sidecar exclusion, deterministic ZIP construction and independent
milestone boundaries remain unchanged. Same-session tests never grant M2 approval.

## Risks

The installed Git must support its existing command-line configuration contract. Windows path
handling and archive path-safety are distinct boundaries; this override does not authorize unsafe
ZIP names, external paths or arbitrary source execution. Real failures must remain observable.

## Reversal Strategy

A later authorized transport decision may replace this adapter only with equivalent real
positive/adverse byte, configuration and reconstruction proof. Never rewrite historical subjects
or accept a declaration without rebuilding its original immutable bytes.

## Related Artifacts

[Git reader](../../scripts/development-ledger/review_bundle.py);
[unchanged reconstruction owners](../../tests/test_gate4_quality_engine.py);
[Gate7 findings](../checkpoints/GATE-7-CP-0001/FINDINGS.json);
[exact contextual originals](../checkpoints/GATE-7-CP-0001/REWORK-CONTEXT-ARCHIVE.json).
