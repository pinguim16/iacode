# ADR-0061 — Client verification preserves producer and cleanup outcomes

Status: Accepted
Date: 2026-10-21
Owners: GATE 7 — M2 audit correction

## Context

Independent audit M2-F-002 observed two real client producers lose their captured result when
exact-owner Docker cleanup failed. A return from try is not an evidence boundary: finally can
replace it. LSN-0135 recurred despite its guardrail. M2-F-001 separately found that checkpoint
creation reconstructed arguments from parsed defaults and omitted a consumed custom phase.

## Decision

Snapshot the Docker producer's available exit status, literal arguments and safe streams before
attempting cleanup. Cleanup has its own observation, including timeout and launch refusal. A
ClientCheckError exposes both observations as a bounded structured FAIL. It must never return
success when cleanup fails, and only an exact no-such-container result for the generated owner may
mean no resource remains. Keep all original container restrictions and exact-owner cleanup.

Retain UTF-8 stream digests and byte counts. Do not publish unsafe, undecodable, oversized or
unscannable streams; publish a neutral refusal with the digest instead. The canonical raw and
transport-decoded secret detector remains unchanged, with no new exemptions. Ordinary complete,
safe producers keep the CompletedProcess interface. An explicit native Node runtime does not
gain a Docker cleanup obligation.

The same boundary applies to native owned processes. `native_execution.py` captures raw bytes in
an owned handle, binds a finite available prefix before cleanup, and records typed launch/timeout,
Job Object cleanup and capture-handle release separately. Safe ordinary producers retain the
CompletedProcess interface. Cleanup and privacy refusals remain failures with the primary report
attached; native callers must forward it instead of replacing the exit state with a generic error.
The exact suspended/attached ownership and existing physical-drain deadline stay unchanged.

Checkpoint creation records supplied argv in original order/spelling, without adding defaults.
The recorded working directory is the actual launch directory, not a substituted --root target.
Human replay uses CreateProcess quoting on Windows and shlex quoting on POSIX, with no shell
expansion. This changes future producers only; sealed command records are not rewritten.

## Evidence and verification

CP0003 causal attempt run-0005 has valid clean controls and actual pre-fix failures. Earlier
harness failures are retained and not accepted as causal proof. Run-0006 executes the same 12
regressions after correction with exit 0. These targeted results do not replace mandatory integral
assurance, live Docker capability or a later independent milestone audit.

The native extension has an actual pre-fix producer/null and controlled post-drain callback fault,
followed by 11 current real-producer/caller/release controls. The registered M2-RT-01 executes an
actual omitted-phase null and quoted Unicode phase, including human replay. Its owning current
suite also repeats the old immutable producer and observes a valid null beside the phase escape.
The first new attack harness attempt miscounted LATEST.md as a checkpoint directory; it remains
failed and is not causal acceptance. The corrected complete 18-case invocation passed.

## Alternatives considered

- Suppressing cleanup failure or converting it to a warning would manufacture success.
- Returning only cleanup error would preserve the original defect.
- Publishing arbitrary exception messages/streams would disclose sensitive material.
- Rewriting historical commands or approving the correction in the implementing session would
  destroy the audit boundary.

## Consequences and risks

An unavailable engine still produces FAIL with both observations. No restart, global setting,
permission/group change or other application's container is part of this correction. Restricted
auditor Docker access remains a separately authorized environment prerequisite.
