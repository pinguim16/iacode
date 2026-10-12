# Risks

- A declaration embedded in the bytes it hashes is recursively unstable; the sidecar exclusion must
  remain explicit and validator-enforced.
- Live remote refs, working-tree dirt and observation timestamps would reintroduce nondeterminism if
  they enter the canonical payload.
- Seal evidence is necessarily written after the immutable content commit. The declaration must bind
  that content commit exactly and the canonical tag may differ only by permitted append-only seal
  evidence.
- Same-session reconstruction and Red Team evidence are not independent approval.
