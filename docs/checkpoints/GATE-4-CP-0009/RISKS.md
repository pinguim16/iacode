# Risks

- A declaration embedded in the bytes it hashes is recursively unstable; the sidecar exclusion must
  remain explicit and validator-enforced.
- Live remote refs, working-tree dirt and observation timestamps would reintroduce nondeterminism if
  they enter the canonical payload.
- Seal evidence is necessarily written after the immutable content commit. The declaration must bind
  that content commit exactly and the canonical tag may differ only by permitted append-only seal
  evidence.
- Same-session reconstruction and Red Team evidence are not independent approval.
- The first post-dispatch signal-only guard recurred in cmd-0060 and remains permanently recorded as
  a `GUARDRAIL_FAILURE`. The replacement treats persisted `CANCELLING` as authoritative before and
  during activity execution, and cmd-0109 subsequently proved the repair in the full 42-stage order.
- A transport probe run while CP0009 is still in progress could accidentally treat missing handoff
  artifacts as a producer defect. The resolver now selects a complete immutable checkpoint and the
  final seal still targets CP0009 itself; tests cover both boundaries.
- A pre-seal exact-subject tag could pollute the preserved-evidence denominator. Namespace separation
  and the published-clone mapping test keep `iacode-preserved/` load-bearing only for sealed ledgers.
- Detached subject validation must never become an alternate seal path. It is restricted to clean
  `IN_PROGRESS` checkpoints whose symbolic HEAD is reached by a checkpoint-named
  `iacode-subjects/` tag; all later statuses still require the canonical checkpoint tag.
- A structural decision can be technically valid yet undiscoverable when its canonical index is not
  updated atomically. Cmd-0083 caught ADR-0036's missing index row; both complete enumeration and a
  missing-row mutation control now pass and remain mandatory.
- Assurance bookkeeping can fail even after product verification. Cmd-0112 caught a duplicated
  corrective-row literal and cmd-0121 caught an unintended lesson selector; LSN-0102/GRD-0103 and
  the existing LSN-0059 guardrail now prevent both classes, while the failed runs remain preserved.
- The internal A-T battery and the 18-dimension closure mirror were authored in this implementing
  session. Their PASS results reduce handoff risk but cannot substitute for later independent review.
- The latest Engineering Memory changes make the earlier Green Keeper, completeness, internal Red
  Team and closure-mirror results stale for promotion. The user-requested restart interrupted the
  replacement Green Keeper attempt before its first gate completed; a fresh cycle 18 must start from
  the beginning and no partial result from that attempt may be reused.
- A host restart could expose repository divergence or leave external services in a different state.
  Resume only after repeating the AGENTS.md entry checks and comparing branch, HEAD and working-tree
  state with `STATE.json`; stop and create `DIVERGENCE.md` if they differ unexpectedly.
