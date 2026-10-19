# ADR-0060 — Native drain allows natural exit within the existing deadline

Status: Accepted
Date: 2026-10-19
Owners: GATE 7 — inherited native acceptance and observed cleanup

## Context

Completed runtime-v3 cmd-0180 passes48 of49 stages and fails native installation/trust cleanup.
The exact failed invocation and all available original producers remain archived. A real
instrumented reproduction pins three owned members: accounting becomes zero, but two handles
remain nonsignaled at ten seconds. Closing the Job earlier also fails with two observed members;
that hypothesis is rejected. Exit codes alone do not establish physical completion.

A controlled natural-exit variant exercises two actual pending members. Both signal in about
52ms without forced termination, and the real package/trust run and owned directory removal pass.
This supports avoiding a force-termination race with exiting descendants; it does not identify
an operating-system internal deadlock or the exact historical thread/resource holder.

Contrary current observation: uninstrumented cmd-0195 still fails, now in package mode with3
pending handles after the one-second natural budget and ten-second total limit. The bounded
diagnostic survives correctly, but one green experiment is not a completed lifecycle correction.
At that point G7-INT-030 remained open; no candidate was published from the incomplete proof.

Further real observations reject installed-CLI `--wait` as a fix: two handles remain nonsignaled
after ten seconds, with both ctypes and Python's Win32 binding agreeing, including after Job
release. An external crash/telemetry bootstrap opt-out then observes a real pending member signal
in868ms without force. This supports a bounded owned-only privacy/teardown improvement, not a
claim that Crashpad or a specific Windows component caused the historical failure.

## Decision

Keep exact unnamed owned Job assignment before suspended-child resume, read/synchronization-only
member handles, complete bounded snapshots and exact membership validation. Preserve the same
ten-second total drain deadline and physical-signaling predicate. Allow at most one second of
natural exit inside that deadline. Finish immediately when accounting is zero and all pinned
members signal. Otherwise pin the current complete snapshot as well, then terminate only the
owned Job and require both zero accounting and every observed handle signaled before success.
Sample the clock before success as well: a signal observed after the original deadline remains
FAIL. Cmd-0210 reproduces the old late-success branch in a causal unit fixture; no inherited
assertion, deadline or physical predicate is relaxed.
Do not close the Job early, widen deadlines, replay historical PIDs or touch unrelated processes.
Actual owned profile removal remains required and independently observed under ADR-0052.

Opt out of crash reporting and telemetry at the owned native host's bootstrap with the installed
editor's supported `--disable-crash-reporter` and `--disable-telemetry` arguments, in addition to
the existing per-profile telemetry setting. This affects only generated acceptance processes;
it does not alter the user's editor settings, disable a test/security control, disable extension
activation or relax workspace trust. Keep the actual direct native host launch; the rejected
CLI-wait experiment is not adopted. Verify the launch arguments and repeat real uninstrumented
package/trust/profile-removal before considering local restoration.

A failed drain retains a bounded closed phase/count/time observation on its raised exception.
The native reporter records it as FAIL with the actual mode before temporary cleanup, even when
an inner child report might say PASS. No PID, path, raw kernel error text or child input enters
the bounded diagnostic projection. Other failures still propagate and fail closed.

## Verification

Retain the original negative and rejected/inconclusive experiments as inert context. Require
causal unit controls for natural drainage without force, forced fallback, late-member pinning,
zero-accounting/nonsignaled refusal, unchanged deadline, foreign/truncated snapshot refusal,
and red bounded reporting. A real owned parent/child plus independent outside sentinel proves
scope and physical exit; its premise uses observed membership, never a guessed exact count.
Then require repeated fresh uninstrumented native package/trust/removal, all inherited owners,
the complete immutable49-stage verifier and every ordered internal delivery control.

Local outcomes: causal cmd-0188/0210 failures remain; cmd-0211 passes10 current native controls,
cmd-0213 all152 owning Gate5/6/7 cases, cmd-0214 helper quality and cmd-0215 whole unchanged lint.
Final strict source passes two fresh uninstrumented installation/trust/removal runs at cmd-0217,
with exact originals retained before interpretation. This supports local guard restoration only;
failed runtime-v3 stays FAIL and the complete new immutable/ordered cycle remains due.

## Alternatives Considered

- Treat zero accounting or a non-STILL_ACTIVE exit code as success: rejected; physical signals
  and actual profile deletion remain mandatory.
- Close the Job before waiting: rejected by a real nonempty-boundary failed experiment.
- Accept an empty-snapshot green rerun as causal proof: rejected as inconclusive.
- Increase a timeout or kill global Code processes: rejected; ownership and budgets are unchanged.

## Consequences and Risks

Natural shutdown may finish before forced cleanup is necessary. Persistent children still face
the same owned force-termination and ten-second bound. A genuine kernel/cleanup failure remains
FAIL with retained observations, not acceptance. This session does not grant independent M2
approval; a fresh sealed subject and later independent review remain mandatory.

Microsoft documents process signaling and termination behavior in
[Terminating a Process](https://learn.microsoft.com/en-us/windows/win32/procthread/terminating-a-process)
and [WaitForSingleObject](https://learn.microsoft.com/en-us/windows/win32/api/synchapi/nf-synchapi-waitforsingleobject).
The supported bootstrap switches are declared by the
[VS Code argument contract](https://github.com/microsoft/vscode/blob/main/src/vs/platform/environment/node/argv.ts).
