# Risks

- A declaration embedded in the bytes it hashes is recursively unstable; the sidecar exclusion must
  remain explicit and validator-enforced.
- Live remote refs, working-tree dirt and observation timestamps would reintroduce nondeterminism if
  they enter the canonical payload.
- Seal evidence is necessarily written after the immutable content commit. The declaration must bind
  that content commit exactly and the canonical tag may differ only by permitted append-only seal
  evidence.
- Same-session reconstruction and Red Team evidence are not independent approval.
- The post-dispatch cancellation boundary depends on Temporal's deterministic event ordering. The
  structural guardrail fixes the vulnerable interval, the rebuilt evaluator suite exercises the
  shipped workflow, and only a new complete verifier may close the preserved red cycle.
- A transport probe run while CP0009 is still in progress could accidentally treat missing handoff
  artifacts as a producer defect. The resolver now selects a complete immutable checkpoint and the
  final seal still targets CP0009 itself; tests cover both boundaries.
- A pre-seal exact-subject tag could pollute the preserved-evidence denominator. Namespace separation
  and the published-clone mapping test keep `iacode-preserved/` load-bearing only for sealed ledgers.
