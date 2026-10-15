# ADR-0039 — Sandbox output is scanned before durable delivery

Status: Accepted
Date: 2026-10-15
Owners: GATE 4 — Quality Engine

## Context

G4-INT-006 reproduced inline, full-stream and error-channel credential-shaped output crossing the
sandbox service unchanged. Full streams were uploaded before the evaluator received the execution.
The activity also returns execution data to Temporal, whose activity results are durable history
([Temporal workflow documentation](https://docs.temporal.io/workflows)). Evaluator-only scanning
therefore misses the first durable boundary. The probe used synthetic markers, not credentials.

## Decision

The sandbox service scans the exact structured helper response and every decoded full stream with
the canonical common-package taxonomy before any artifact write or activity response. A match
returns a sanitized FAILED result with SANDBOX_OUTPUT_SECRET_DETECTED; scanner, serialization or
full-stream decoding failure returns SANDBOX_OUTPUT_SECRET_SCAN_FAILED. Neither response contains
the rejected bytes or the scanner's exception. Every full stream is checked before the first is
uploaded, so a clean stdout cannot commit before a prohibited stderr is discovered.

The shared detector judges both exact text and valid JSON's decoded strings and normalized keys,
including JSON transported inside another JSON string. Finite layers are decoded iteratively;
malformed plain text keeps lexical scanning, while parser/scanner failures remain fail-closed.
Mixed tool logs also admit JSON records and quoted JSON strings between ordinary messages.
Those fragments are decoded with the standard JSON decoder, including records not aligned to a
line. Fragment parsing has a content-derived work ceiling (at least one million consumed character
positions, otherwise twenty times stream length); exhaustion is an explicit scanner failure, not
a clean result. This prevents adversarial overlapping malformed fragments from unbounded work.

The publication scanner consumes the same in-memory transport views, not a separate raw-only
interpretation of the canonical patterns. It retains the wider historical taxonomy and exact
component-digest allowlist, without inferring approval of another value of the same kind. Decoded
findings identify the source carrier's line, since decoded newlines are not source-file lines.
Sensitive views and matched values are never recorded; only kind, location and allowlist status
leave the scanner.
The canonical patterns are unchanged. This closes the newline/Unicode transport escape reproduced
by cmd-0052 without introducing a weaker local scanner. The same rule protects evaluator writes
and post-read resolution of legacy JSON evidence.

Both sandbox artifact sinks independently scan exact bytes before any object or metadata operation.
The boundary applies to all sandbox output, including quality runners; a policy name or request
origin never disables it. Clean output remains byte-identical. Existing evaluator pre-write and
post-read controls stay in place as defense in depth.

## Consequences

The earlier durable transport and artifact paths cannot retain canonical credential-shaped output
merely because evaluator storage later refuses it. Legitimate data matching the prohibited taxonomy
also fails closed; this is a visible security failure, not a silent redaction that permits PASS.
The change is a Gate 4 integration correction in its sandbox dependency, not a new Gate capability.
Legacy already-persisted artifacts are not rewritten or represented as repaired by this decision.

## Alternatives considered

Scanning only evaluator MinIO writes was rejected because earlier writes and the activity response
already exist. Scanning base64 envelopes without decoding was rejected because it does not inspect
the bytes being uploaded. Masking the value and retaining success was rejected because it conceals
a failed security check. Persisting rejected bytes as quarantine evidence was rejected because it
creates the prohibited durable copy.

## Reversal

The boundary may be replaced only by an equivalent earlier fail-closed control with null-mutation,
zero-write, scanner-failure, activity-response and live-container proofs. Historical evidence remains
immutable and independent milestone validation remains pending.
