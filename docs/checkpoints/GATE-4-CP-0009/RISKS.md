# Risks

- A declaration embedded in the bytes it hashes is recursively unstable; the sidecar exclusion must
  remain explicit and validator-enforced.
- Live remote refs, working-tree dirt and observation timestamps would reintroduce nondeterminism if
  they enter the canonical payload.
- Seal evidence is necessarily written after the immutable content commit. The declaration must bind
  that content commit exactly and the canonical tag may differ only by permitted append-only seal
  evidence.
- Same-session reconstruction and Red Team evidence are not independent approval.
- The first post-dispatch signal-only guard recurred in cmd-0060 and is formally recorded as a
  `GUARDRAIL_FAILURE`. The replacement treats persisted `CANCELLING` state as authoritative both
  before activity creation and throughout a long activity, cancels a handle assigned after the flag
  is set, and gives cancellation precedence over a racing normal response. Cmd-0071 resolved the
  recorded guardrail failure in a live checkout-owned stack, but only the next complete verifier can
  prove the repair holds in the full 42-stage order.
- A transport probe run while CP0009 is still in progress could accidentally treat missing handoff
  artifacts as a producer defect. The resolver now selects a complete immutable checkpoint and the
  final seal still targets CP0009 itself; tests cover both boundaries.
- A pre-seal exact-subject tag could pollute the preserved-evidence denominator. Namespace separation
  and the published-clone mapping test keep `iacode-preserved/` load-bearing only for sealed ledgers.
- Detached subject validation must never become an alternate seal path. It is restricted to clean
  `IN_PROGRESS` checkpoints whose symbolic HEAD is reached by a checkpoint-named
  `iacode-subjects/` tag; all later statuses still require the canonical checkpoint tag.
