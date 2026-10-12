# Risks

- CP0006 remains an immutable `GATE_PASS` record whose own tag-carried validator fails from remote
  transport. CP0007 supersedes that publication claim; it does not rewrite the predecessor.
- One full verifier retry observed a Docker API-image pre-build exit with no diagnostic output.
  The canonical lint gate passed immediately afterward and the next complete 42-stage verifier
  passed. Both the transient red run and the green run remain recorded.
- The internal Red Team, Green Keeper, completeness audit and milestone mirror are same-session
  assurance. They cannot satisfy the later independent-review requirement.
- The forward-only compatibility branch is intentionally retained for sealed schema 3.2 and older
  checkpoints; schema 3.3 is the first contract that requires transportable command inputs.
