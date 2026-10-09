# Baseline — GATE-4-CP-0001

## Proven predecessor

- `GATE-3-CP-0006` is sealed at `92020769ffd19adeb78d432141da5b1fd492f969`.
- `milestone_status.py --milestone M1` derives `MILESTONE_INDEPENDENT_AUDIT_PASS`.
- The checkpoint chain, canonical tag, authorised remote branch, and remote tag were verified before
  this checkpoint was created.
- The predecessor reports 1,551 passing counted tests, 32/32 verification stages, 198/198
  requirements complete, and 19/19 final audit attacks defended.

## Gate 4 starting condition

- `services/evaluator/` contains only its reservation README; no quality engine is implemented.
- No quality contracts, policy registry, planner, runner registry, verdict derivation, evidence
  store, persistence schema, service API, worker, or Gate 4 functional scenario exists.
- The sandbox is available as the only authorised execution boundary and already supports
  content-addressed images, immutable workspace snapshots, bounded commands, artifact storage,
  cancellation, recovery, and origin-checked tool results.
- PostgreSQL, MinIO, Temporal, the API, the Agent Runtime, Prometheus, and the verification driver
  are available integration points.
- `docs/GATE-4-CHECKLIST.md` now fixes 105 mandatory Gate requirements; the lesson preflight adds
  58 requirements, for a derived denominator of 163 before implementation.
- The full control-plane baseline was started through `record_command.py`; its result remains
  whatever the ledger records and is not presumed green while it runs.

## Known gaps to close

1. Stable, versioned quality-domain contracts and closed policy vocabularies.
2. Project-agnostic detection and stack-specific plans for Python, Node, TypeScript, Angular,
   Maven, and Gradle.
3. Sandbox-only runners and extensible content-addressed toolchain images.
4. Immutable evidence, append-only lifecycle persistence, and pure verdict derivation.
5. Durable workflow, API, Agent Runtime integration, health, telemetry, and operational docs.
6. Permanent functional acceptance, program-state, review-bundle, and false-PASS controls.
7. Live passing, failing, IACode, reproduction, recovery, cancellation, and timeout proofs.

## Stop conditions

- Any command path outside the sandbox.
- Any verdict accepted from a caller or stored without re-derivation.
- Any evidence that can be replaced, cannot be resolved, or is not bound to its inputs.
- Any required stack represented only by a mock, assertion, or documentation.
- Any attempt to start Gate 5 or Gate 20 capability.
- Any divergence from the sealed predecessor, canonical requirement set, or authorised remote.

