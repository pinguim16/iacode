# ADR-0052 — Native cleanup failures retain observed diagnostics

Status: Accepted
Date: 2026-10-18
Owners: GATE 6 — Experience Store internal acceptance

## Context

Fresh internal Red Team cmd-0258 records both native functional/trust cases and zero owned job
members, then fails to remove an owned agenthost log with WinError32. The original report remains
FAIL; all other fresh executions cannot turn its invalid baseline into acceptance. Read-only
inspection cmd-0264 later observes the file unlocked, and exact recovery cmd-0266 removes only the
generated test owner without stopping any application. The historical lock holder is not known.
Actual cmd-0274 later pins a current process with verified membership in the owned native job:
the old close routine returns zero members while that process handle is still nonsignaled (258).
It signals only later. This directly disproves the old completion predicate; it does not identify
the historical failed log owner retroactively. Cmd-0275 reproduces false drainage in causal controls.

The pre-fix causal counterexample cmd-0265 demonstrates a separate reporting defect: context cleanup
throws before retry/attempt/elapsed observations reach the native result. Parent/job exit is not
file-removal evidence, and a failure string cannot explain which part of the cleanup budget elapsed.

## Decision

The existing exact-target checks, ten-second removal retry deadline, allowed WinError5/32 retries,
original exception propagation, owned Job Objects and mandatory observed removal remain unchanged.
Before terminating the owned job, pin read/synchronization handles for its complete bounded member
snapshot and verify each handle still belongs to that exact job. Reject truncation, unknown states
or reused/foreign identities. Within the existing ten-second job-drain deadline, require both zero
active accounting and signaled completion of every observed member. Close every acquired handle,
including failure paths. Never obtain termination authority from a filename or an unverified PID.
Actual profile removal remains mandatory: a snapshot cannot certify every future spawn or an
external file holder, and signaled observed handles alone never establish native acceptance.
The cleanup context retains attempts, retries, elapsed duration, first sharing-lock timing and the
terminal typed error on both success and failure. The native reporter publishes these observations
even when context exit raises. Functional success never overrides failed cleanup.

Read-only handle inspection may identify current PID/creation identities with positive/released
controls; it does not identify a historical holder retroactively and never stops another application.
Generated-owner recovery is separately recorded and never rewrites the original failed result.

## Evidence and verification

Require the original negative report, the pre-fix failing counterexample, positive actual removal,
deadline/error propagation and false-PASS reporting controls, a real held/released Win32 file control,
fresh actual native host/profile cleanup and the complete fresh ordered assurance cycle. An added
diagnostic field or this ADR is not proof of runtime acceptance or independent M2 approval.

Cmd-0276 accepts the same formerly failing positive/deadline controls; cmd-0279 runs all77 Gate5/
Gate6 root cases in canonical discovery context, including truncation and identity refusal.
After normal source formatting, cmd-0281 retains both fresh uninstrumented actual native producers:
installation/trust pass, every observed owned member signals, and both owned directories are removed.
These are local corrective proofs, not a substitute for the complete new immutable assurance cycle.

Microsoft documents asynchronous termination and waiting for completion:
https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-terminateprocess
https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_basic_process_id_list

## Alternatives considered

- Increasing a timeout, ignoring removal or equating zero job members with deletion is rejected.
- Killing global Code, security or indexing processes is outside ownership and is rejected.
- Blind reruns presented as a causal software fix are rejected: use the actual pinned-handle mismatch
  and formerly failing controls; the historical holder still remains unknown.
- Losing failed cleanup observations is rejected: the original error still propagates with evidence.

## Consequences and risks

An external/transient Windows sharing lock may still produce a real FAIL within the unchanged bound.
The control guarantees fail-closed observed cleanup, not perpetual operating-system availability.
Source/memory changes require a new immutable full subject; old successful and failed observations
remain historical rather than being mixed into current approval. ADR-0048 and ADR-0037 still apply.
