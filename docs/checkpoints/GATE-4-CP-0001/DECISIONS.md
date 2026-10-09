# Decisions

## D-01 — The Gate 4 denominator is fixed before product code

The owner mandate, master plan, inherited architecture, and engineering lessons were consolidated
into `docs/GATE-4-CHECKLIST.md`. The canonical parser derives 105 Gate rows. The lesson preflight
originally derived 58 more; three observed implementation failures added three applicable
requirements, so implementation is now measured against 166 requirements. The registry is only a
row-for-row mirror and cannot shrink the source document.

## D-02 — The baseline is focused; the complete suite belongs to Green Keeper

An attempted pre-implementation run of the complete control-plane suite was manually stopped after
roughly nine minutes when historical ledger evidence showed that this suite normally takes 37–72
minutes. The recorder process was also stopped, so it emitted no command record; this paragraph is
the explicit record rather than a fabricated result. The baseline was replaced by focused checks of
the sealed Gate 3 sandbox boundary and the exact Gate 4 derivation (`cmd-0005`, `cmd-0006`). The
complete suite remains mandatory and will run through Green Keeper before handoff.

## D-03 — A normalized identifier is compared with a normalized identifier

The first Gate 4 test run (`cmd-0007`) failed because the new test compared the normal form
`GATE4` with the documentary spelling `GATE-4`. The repository policy was correct; the test mixed
representations. The repair normalizes both operands, and `cmd-0008` passes all seven kickoff tests.

## D-04 — A pre-commit chain must stop explicitly on every failed command

The kickoff commit `f0b18f3` was pushed after `git diff --cached --check` reported one trailing blank
line in `BASELINE.md`. PowerShell continued because the commands were separated by semicolons and
the later commit and push succeeded. No secret or behavioral defect was involved, but a reported
quality failure reached the remote. This corrective commit removes the whitespace, and subsequent
delivery chains inspect `$LASTEXITCODE` after every check before commit or push.

## D-05 — Quality contract casing is a bounded wire-format exception

Quality plans, runs, results, findings, evidence and verdicts cross the API, Temporal and sandbox
boundaries and are persisted as versioned JSON. Their camelCase fields therefore remain literal
wire names, matching the existing gateway, agent-runtime and sandbox contracts. `ruff.toml` exempts
only `quality.py` from N815; implementation modules retain normal Python naming rules. The first
repository lint run (`cmd-0018`) exposed 105 issues in the new slice, and the repaired full run
(`cmd-0019`) is green without disabling any behavioral or security check.

## D-06 — Quality toolchains extend the Gate 3 boundary

ADR-0029 records the structural choice: the evaluator never runs project processes. Three
stack-specific image profiles map Python, Node/TypeScript/Angular and Maven/Gradle plans onto
shell-only, `network=none` sandbox policies. The images pin their base digests and tool versions;
Node dependency installation consumes a prebuilt offline cache, and Java resolution consumes an
immutable local repository. `image-inputs.json` extends the image fingerprint to source files such
as the Node lockfile that live outside an image context, refusing unsafe or missing paths.

## D-07 — A stripped environment must still expose every declared tool

The first complete sandbox run (`cmd-0022`) passed 147 tests and failed the Java toolchain smoke
test because Gate 3 correctly strips the image's inherited `PATH`; the JDK lived only under
`/opt/java`. The repair links the pinned JDK executables into `/usr/local/bin`, which is part of the
helper's fixed environment. The next full run (`cmd-0023`) passed all 148 tests with network and
privilege isolation unchanged.

## D-08 — Constraint names are table-qualified

PostgreSQL exposes unique-constraint backing indexes in a schema-wide namespace. The first live
migration attempt found collisions when generic names such as `idempotency_key` were repeated
across quality tables. Migration 0006 therefore uses table-qualified names. This preserves the
closed uniqueness rules without relying on database-specific implicit names.

## D-09 — Artifact bytes are shared; evidence references are run-scoped

Immutable evidence bytes are content-addressed in MinIO and may be shared when an exact reproduction
emits identical content. Each run still receives its own immutable evidence reference in PostgreSQL,
including producer, result association and provenance. Reproduction can therefore compare digests
without pretending that two executions are the same event.

## D-10 — Raw foreign keys require an explicit persistence boundary

The first real PostgreSQL lifecycle run attempted to insert child checks before their new plan
because the objects were connected only by UUID values, not an ORM relationship. The store now
flushes a new plan before its checks and a new run before its first event. LSN-0060 and GRD-0061
make the real-database lifecycle test a permanent guardrail against this ordering failure.

## D-11 — Early and late results are different refusal classes

The first repaired evaluator rerun (`cmd-0030`) showed that the terminal callback was refused with
the right code but the generic message used for a run that had not started. The store now reports
`EARLY_RESULT` for CREATED, PLANNED or QUEUED runs and `LATE_RESULT` for CANCELLING or terminal runs.
This preserves fail-closed behavior while giving callers an actionable and truthful reason.
