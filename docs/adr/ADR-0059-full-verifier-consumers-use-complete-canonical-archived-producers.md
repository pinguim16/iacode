# ADR-0059 — Full verifier consumers use complete canonical archived producers

Status: Accepted
Date: 2026-10-19
Owners: GATE 7 — original evidence retention and current internal-audit inputs

## Context

The actual runtime-v2 publisher retains selected quality/client reports but omits nine available
canonical agent/gateway/sandbox lifecycle producers. Its later forwarding loop repeats the same
incomplete membership, so parent-workspace audit inputs may be missing or historical even though
the fresh verifier executed the owning stages. The omission is reproduced by actual capture,
canonical-growth and post-consumer-error cleanup controls.

Eighteen available canonical originals were rescued before the active clone's cleanup. All28
rescued and actual legacy-capture copies have verified nonempty original bytes/digests and no
secret refusal. These are failed-runtime observations, not current or independent acceptance.

## Decision

Derive current report names from the canonical full verifier's declared var report arguments,
retaining every previously supported legacy output and quality namespace. Callers cannot select
a smaller report set. Do not indiscriminately ingest unrelated files from the operational var
directory; excluded private extras remain excluded.

Capture every available matching original plus the verifier report before interpretation or
temporary-owner cleanup. A successful complete verification must not lack any canonically named
producer. Failed executions preserve their available originals without inventing missing reports
or promoting neutral capture into acceptance.

Consumers and parent-workspace forwarding read the same durable archived originals. Before any
forwarding effect, validate name/path containment, exact nonempty bytes/digests, safe content and
JSON-object shape for every selected report. Forward exact raw bytes and derive semantic scenario
objects from those same bytes. Refused, missing, corrupt or private input never falls back to a
historical parent report, and a retained FAIL remains FAIL.

## Evidence

G7-INT-029 and LSN-0135 recurrence2 preserve the actual omission and all earlier recurrence history.
The canonical causal tests keep legacy support, private-extra exclusion, real consumer failure
and actual owner cleanup while testing registered report growth. Fresh whole immutable execution
and every ordered internal control remain separately mandatory.

## Alternatives Considered

- Expand another hand-maintained partial list: rejected; it can omit the next registered producer.
- Capture every var JSON without ownership membership: rejected; unrelated operational input is
  not automatically an authorized producer.
- Parse the temporary original again after durable capture: rejected; downstream semantics must
  describe the retained original rather than a second mutable read.
- Trust parent files or prior stage PASS fragments: rejected as a substitute for current evidence.

## Consequences

Canonical lifecycle reports survive failure/cleanup and the later internal audit receives current
copies from the same completed invocation. Existing archive/report schemas and promotion rules
remain authoritative; no new Gate, independent verdict or source-reuse permission is introduced.

## Risks

Archive ownership, filesystem and local operator remain trusted boundaries. All report strings
are data, never execution instructions. Capture is neutral provenance, not proof that a scenario
passed; the full/functional validators still require actual complete successful execution.

## Reversal Strategy

A later authorized pipeline may supersede this boundary only with equivalent complete canonical
membership, privacy, exact-byte, consumer-failure and cleanup controls. Historical originals and
their context remain immutable; no shortened denominator or manufactured report is acceptable.

## Related Artifacts

[Full verifier publisher](../checkpoints/GATE-7-CP-0001/audit-harness/run_full_verification.py);
[assurance controls](../../tests/test_gate7_assurance.py);
[context originals](../checkpoints/GATE-7-CP-0001/REWORK-CONTEXT-ARCHIVE.json);
[findings](../checkpoints/GATE-7-CP-0001/FINDINGS.json).
