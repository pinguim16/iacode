# Final Report — GATE-0-CP-0001

## Gate

`GATE 0 — FOUNDATION`, milestone `M1` (Gates 0 to 3).

## Status

`INTERNAL_GATE_PASS`.

The project's own controls passed. That is not an independent verdict and is not recorded as one:
`independentReview` and `redTeam` are `NOT_REQUIRED` with the reason, because `M1` is audited after
Gate 3, and the adversarial battery this run executed is filed as `M1-INTERNAL-RED-TEAM.json`
rather than as a Red Team verdict. An implementing run may not grant itself an independent status.

## Authorization

Derived, not assumed. `docs/checkpoints/SETUP-00-CP-0013` is sealed with `M0` at `PASSED` and
`SETUP-00` closed, `.iacode/anchors/checkpoint-chain.json` verifies thirteen anchors, and
`docs/MASTER-PLAN.md` places `GATE 0` next. `BASELINE.md` records the check, including the one
baseline finding it started from.

## Environment

Windows 11 Pro 10.0.26200, Python 3.13.15, Docker 29.6.1, Git. Branch `main`, base commit
`b5b594660584092c74738bdda3d8bca9b210b406`. The stack runs locally and needs no cloud account: one
PostgreSQL server, Redis, MinIO, Temporal, Prometheus and Grafana, all from
`infra/compose/docker-compose.yml`. Every adversarial scenario that mutates a repository runs in a
disposable clone under the system temporary directory, never here.

## Tool / Model / Effort

Claude Code 2.1.195, Anthropic, `claude-opus-5`. Effort is not exposed by the runtime and is
recorded as `not-exposed` rather than guessed.

This is the implementing run: a single session with full memory of its own work, which is exactly
why it may not record an independent verdict about itself. `crossToolValidation` is `NOT_AVAILABLE`
and no attestation mechanism is claimed.

## Deliverables

- `docs/GATE-0-CHECKLIST.md` - the Gate's canonical specification, 84 rows, mirrored row for row by
  `.iacode/policies/canonical-requirements.json`, and the source the expected requirement set is
  derived from.
- The backend: FastAPI with typed configuration, an explicit dependency lifecycle, `/health`,
  `/ready`, `/version`, `/metrics`, structured JSON logging, request correlation and an error
  contract that leaks no traceback.
- Persistence: PostgreSQL 17 with pgvector, SQLAlchemy 2 with `asyncpg`, Alembic from the first
  commit, UUIDv7 identifiers and twelve structural tables.
- Redis, MinIO with an idempotent bucket bootstrap, and Temporal with the worker as its own process
  running a smoke workflow that actually executes.
- The Angular web shell, built and tested in a container, reading its backend address at run time.
- The Compose stack with real health conditions and no fixed sleeps, named volumes, loopback-bound
  configurable ports and non-root images.
- Prometheus, and Grafana with a provisioned datasource and a Foundation dashboard.
- Backup and restore, where a backup is not accepted without a verified restore and read-back.
- One verification command, `python scripts/iacode/verify.py`, and `verify.ps1` for Windows.
- Documentation: `README.md`, `docs/ARCHITECTURE.md`, `docs/DEVELOPMENT.md`, `docs/VERSIONS.md`,
  two runbooks and four ADRs.

## Files Created

196 paths. `FILES.json` declares each one with the reason it exists, and `finalize_checkpoint.py`
binds the hashes rather than the author typing them.

## Files Modified

27 paths: the control-plane tooling generalised so a Gate other than SETUP-00 can be delivered, the
policies and schemas this Gate introduces or extends, the engineering memory, the entry
documentation, and the integrity chain, which gains the thirteenth anchor.

No sealed checkpoint was modified and no historical tag was moved.

## Validation

`CHECKPOINT_VALID`. `LESSONS_VALID`. `INTEGRITY_VALID` with thirteen anchors.
`DELIVERY_COMPLETENESS_GATE=PASS` at total coverage and total evidence coverage.
`GREEN_KEEPER_GATE=PASS`. `INTERNAL_MIRROR=PASS`. The final validation runs after the commit, so it
describes the sealed content rather than a working tree.

## Derived values

| Item | Value |
|---|---|
| Requirements | 118 of 118 `COMPLETE` (84 from the Gate specification, 34 from the lesson preflight) |
| Mandatory requirements | 117; the one non-mandatory row is `LESSON-REQ-0013`, which the preflight derives as advisory |
| Coverage | 100.00% |
| Evidence coverage | 100.00% |
| Backend | PASS |
| Frontend | PASS |
| Docker Compose | PASS |
| PostgreSQL | PASS |
| Redis | PASS |
| MinIO | PASS |
| Temporal | PASS |
| Prometheus | PASS |
| Grafana | PASS |
| Migrations | PASS |
| Fresh install | PASS |
| Restart | PASS |
| Backup | PASS |
| Restore | PASS |
| Health | PASS |
| Readiness | PASS |
| Tests | 579 of 579 PASS (438 control plane, 93 backend, 48 infrastructure) |
| Frontend tests | 14 of 14 PASS, inside the `webTests` gate (Vitest, 3 files) |
| Builds | PASS |
| Static analysis | PASS |
| Lint | PASS |
| Green Keeper | PASS, cycle 2, measured against 9 of 9 mandatory gates |
| Completeness | PASS |
| Red Team (internal, Gate 0) | 28 of 28 defended, null-mutation control `VALID` |
| Internal mirror audit | PASS, 16 of 18, 2 `NOT_APPLICABLE` with a derivation source |
| Critical findings | 0 |
| High findings | 0 |
| Medium backlog | 0 |
| Low backlog | 0 |
| Blockers | 0 |
| Integrity | 13 anchors verified, 13 tags resolve |

Every number above is derived: `COUNTS.json` holds the count derivation, `COMPLETENESS-REPORT.json`
the coverage, `REWORK-LOG.jsonl` the Green Keeper cycles, `M1-INTERNAL-RED-TEAM.json` the battery
and `VERIFICATION-REPORT.json` the executions.

## Tests

`python scripts/iacode/verify.py` runs eighteen stages and reads the mandatory gate set from
`.iacode/policies/quality-gates.json` rather than carrying a copy, so a gate added to the registry
is covered without editing the command.

Nine mandatory gates: `tests`, `staticAnalysis`, `lessons`, `integrity`, `checkpointValidation`,
`apiTests`, `webTests`, `lint`, `infraDefinition`. Then the stack with real health conditions, the
backend suite against the running services, the infrastructure suite against the live stack, the
smoke check including a Temporal workflow that actually executes, a backup with a verified restore
and read-back, a dependency scan, and the three scenarios: restart with data intact, dependency
failure with recovery, and a fresh installation from no volumes at all.

## Red Team

`scripts/development-ledger/gate0_red_team.py` executes 28 attacks scoped to this Gate: a fresh
installation, a restart, each of PostgreSQL, Redis, MinIO and Temporal taken down, invalid
configuration, a missing environment variable, a secret pushed through the logger, a migration
failure, a corrupted backup, a failed restore, a corrupted readiness state, and the control-plane
escapes this Gate's own changes could have opened. All 28 defended, over a null-mutation control
that is `VALID`: the battery is shown to fail when nothing is broken, which is what makes a defence
mean anything.

It is filed as `M1-INTERNAL-RED-TEAM.json` and `RED-TEAM-REPORT.md`, and `STATE.json` records
`redTeam` as `NOT_REQUIRED` rather than `RED_TEAM_PASS`. An internal battery is not an independent
Red Team and is not recorded as one.

## Engineering memory

Four lessons added, each `GUARDED` by an automated control rather than by prose:

| Lesson | Guardrail |
|---|---|
| `LSN-0032` a control written while one Gate was the only Gate stops being a control when the next one starts | `GRD-0034` |
| `LSN-0033` a value bound in middleware is absent in the handlers that run outside it | `GRD-0035` |
| `LSN-0034` re-deriving what the framework already computed diverges from the framework | `GRD-0036` |
| `LSN-0035` captured subprocess output decoded or re-emitted with the platform codepage crashes the tool, not the work | `GRD-0037` |

`LSN-0028` recurred twice against a guardrail that was already `GUARDED`, which is a
`GUARDRAIL_FAILURE`: the control was scoped to one document while the class was general. Recorded
as a failure of the control, investigated as one, and closed by `GRD-0033`, which checks the
application's declared configuration against the source that must read it.

Guardrail effectiveness: 37 of 37 effective, resolved and verified by a test. No unresolved
guardrail failure.

## Rework

Two Green Keeper cycles, and the red attempts are in the log rather than hidden.

- **Cycle 1 — `STILL_RED` at `checkpointValidation`.** `QUALITY.json` used an evidence kind the
  checkpoint schema does not define and pointed at a repository path, where that document resolves
  evidence against the checkpoint directory; `STATE.json` still carried the preflight counts from
  before the newest lesson.
- **Cycle 2 — `GREEN`,** 9 of 9 mandatory gates, `remainingFailures=0`.

Before cycle 1, the Green Keeper itself aborted with `UnicodeDecodeError` while reading the output
of a gate that was green, and after that repair the command recorder aborted with
`UnicodeEncodeError` while printing what it had just captured — after an eighteen-minute
verification had already passed. Both are one defect with two directions, and both are in the
ledger as recorded failures: `COMMANDS.jsonl` keeps them rather than discarding them.

Three product defects were found by this delivery's own tests and repaired before any gate ran: a
configuration key nothing read, error responses that lacked the correlation identifier the contract
promises, and HTTP metrics labelled with a single bucket for every route.

## Scope

Nothing reserved for a later Gate is implemented. `.iacode/policies/gate-scope.json` declares which
path belongs to which Gate, `MIR-018` checks it, and each reserved directory carries a README
stating the reservation and nothing else. There is no model routing, no agent, no RAG, no training,
no promotion engine and no mock provider: a reservation is preferable to a fake implementation, and
this Gate has no fake feature to withdraw later.

## Security

Secrets are redacted by key, by URL userinfo and by free text, and the redaction is tested rather
than asserted. `/version` exposes build identity only. No credential is persisted by the schema.
The repository secret scan reads what Git carries rather than the working tree, which is what lets
the operator create the real `infra/compose/.env` the runbook prescribes without the control
refusing the repository. Containers run as non-root where the image allows it, published ports are
bound to loopback and are configurable, and the dependency scan reports `PASS` for both ecosystems.

## Commit and tag

Recorded in `STATE.json` and in `docs/checkpoints/LATEST.md` after sealing. The checkpoint is sealed
with `seal_checkpoint.py`, so the final validation describes the committed content rather than a
dirty working tree, and the tag is `refs/tags/iacode-checkpoints/GATE-0-CP-0001`.

## Known Risks

`RISKS.md` carries nine risks into `M1`, each with the condition that turns it into a defect rather
than a feeling. The ones that bear on the next Gate:

- One PostgreSQL server holds both IACode's schema and Temporal's, which is deliberate for a local
  foundation and recorded in `ADR-0014`. It becomes a defect the moment either needs independent
  tuning or its own backup window.
- pgvector is installed and unused (`ADR-0013`). It becomes a defect if a later Gate stores
  embeddings before deciding the dimension and the index.
- OpenTelemetry is deferred (`ADR-0015`). It becomes a defect once a request crosses more than two
  processes and correlation by log field stops being enough.
- The dependency scan needs network access to two advisory databases. Offline it reports
  `UNAVAILABLE` and exits non-zero rather than forging a pass.

## Remaining Work

None inside this Gate. Every mandatory requirement is `COMPLETE` with resolved evidence, none is
`PARTIAL` or `MISSING`, and there is no backlog item at any severity: the three product defects this
delivery found were repaired rather than deferred, and no Critical, High, Medium or Low finding is
open.

What is deliberately absent belongs to a later Gate and is declared in
`.iacode/policies/gate-scope.json`, not left as an implicit gap.

## Handoff Readiness

`HANDOFF.md` states the validation commands and the stop conditions, and `MIR-018` checks that it is
executable without this session. A new machine follows `docs/DEVELOPMENT.md`: prepare configuration,
start the stack, migrate, reach the API and the web shell, confirm Redis, MinIO, Temporal,
Prometheus and Grafana, run the tests, back up, restore, restart, confirm persistence. That path is
what the three scenarios and the backup-restore check execute, so it is verified rather than
described.

## Evidence

| Artifact | What it holds |
|---|---|
| `VERIFICATION-REPORT.json` | every execution this checkpoint relies on |
| `COMMANDS.jsonl` | the ledger, including the recorded failures, with input digests |
| `REQUIREMENTS-MATRIX.json` | the requirement set with implementation, test, documentation and validation evidence |
| `COMPLETENESS-REPORT.json` | the completeness audit and the denominator it measured |
| `REWORK-LOG.jsonl` | the Green Keeper cycles, red attempts included |
| `M1-INTERNAL-RED-TEAM.json`, `RED-TEAM-REPORT.md` | the internal battery and its null-mutation control |
| `M1-INTERNAL-MIRROR.json` | the mirror audit of this delivery against the repository |
| `COUNTS.json` | every count, derived once |
| `LESSON-PREFLIGHT.json` | the lessons considered before the Gate started, and what each required |
| `.iacode/memory/retrospectives/GATE-0-CP-0001.md` | the Gate retrospective |

## Next Gate

`GATE 1 — MODEL GATEWAY`, which requires the owner's explicit authorization and a new pre-Gate
checkpoint. No Gate 1 work exists in this change set.

`M1` is `PENDING`: audited after Gate 3.
