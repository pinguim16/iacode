# Risks

- The original worktree contains authorized prior audit reports; the sealed subject is therefore
  judged in fresh public detached clones. Both observations remain explicit.
- The Docker CLI cannot read the user's global Docker configuration under sandbox permissions.
  It also cannot open the engine named pipe. No substitute configuration, permission change,
  restart or further direct engine action is inferred as allowed.
- Full non-fast verification is long-running and infrastructure-dependent. Silence or a PASS marker
  before process exit is not terminal evidence.
- Fresh-session independence is not cross-tool independence. The structural attestation mechanism
  is not cryptographic.
- The four prohibited historical temporary targets and the two retained Gate 7 diagnostic owners
  remain outside this auditor's cleanup authority.
- `trainingAllowed` remains false; synthetic functional fixtures grant no rights to production or
  provider/user content.
- The canonical tests gate unexpectedly reached Docker in three cases. No resource mutation was
  observed because engine access was denied. The two cleanup errors masked producer evidence and
  are the separate Critical `M2-F-002`; the dependency null-control outcome remains confounded.
