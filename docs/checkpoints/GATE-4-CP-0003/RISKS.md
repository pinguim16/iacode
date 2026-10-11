# Risks

## Residual risks

- Credential-shape taxonomy changes remain security-sensitive: a future runtime must not fork or
  weaken the canonical scanner without equivalent containment and regression coverage.
- The sandbox cleanup is bounded. A process that remains uninterruptible beyond the configured
  deadline still produces an explicit failure instead of silently claiming a clean sandbox.
- Docker-backed and live-service scenarios depend on host capabilities and external package or
  advisory availability. The final verification observed all required scenarios green, but future
  reproduction still needs the documented environment.
- This session's Red Team, completeness audit, and mirror are internal assurance only. They do not
  satisfy the repository's independent-review or second-tool promotion rules.

## Closed risks and preserved failures

- The initial copied-runtime dependency failure (`cmd-0022`), invalid completeness evidence
  (`cmd-0046`), Green Keeper cycle-2 failures, and transient agent-runtime stage failure
  (`cmd-0077`) remain recorded. Each was followed by a targeted repair or isolated green replay and
  a final complete green run; none is erased or represented as an independent pass.
