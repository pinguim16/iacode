# Plan — GATE-0-CP-0001

## What this Gate delivers

A local, reproducible runtime foundation: an application skeleton, a backend API, a web frontend,
persistence, cache, object storage, a durable workflow engine, observability, containers,
configuration and secret handling, backup and restore, tests, and the operational documentation
that lets a new machine reproduce all of it from this repository alone.

The success criterion is not "the code exists". It is that a compatible machine, following only
this repository, can prepare configuration, start the stack, migrate the database, reach the API and
the frontend, verify health and readiness, confirm every dependency, run the tests, back up,
restore, restart, and find its data intact.

## What this Gate does not deliver

The model gateway, the agent runtime, the sandbox, retrieval, the experience store, training and
model promotion. `.iacode/policies/gate-scope.json` records which Gate owns each reserved directory,
and the scope control fails a delivery that fills one early. A reserved directory holds a README
declaring the reservation and nothing else — an absence is better than a fake.

## Order of work

The delivery order in `docs/DEVELOPMENT-CONTRACT.md`, with the Gate's own content inside step 4:

1. **Cold start and authorization.** Read the contracts, derive the milestone verdict, confirm Git
   state. Recorded in `BASELINE.md`.
2. **Pre-Gate checkpoint.** `GATE-0-CP-0001`, milestone `M1`, status `BASELINING`.
3. **Lesson preflight.** `lesson_preflight.py --gate GATE-0 --scope foundation`, with the
   technologies and modules this Gate actually uses. Thirty applicable lessons, thirty derived
   requirements.
4. **Canonical specification.** `docs/GATE-0-CHECKLIST.md`, mirrored into
   `.iacode/policies/canonical-requirements.json`. This is the first deliverable, because until it
   exists nothing can be derived: the expected requirement set comes from it.
5. **Requirements matrix.** `derive_requirements.py --write`, before implementation.
6. **Tooling that Gate 0 needs and SETUP-00 did not.** Four couplings had to be generalised before
   any product code could be delivered; see below.
7. **Implementation**, in dependency order: shared packages, the API, persistence and migrations,
   the worker, the frontend, the containers and the stack, observability, backup and restore, the
   operational tooling.
8. **Tests**, written with the implementation rather than after it.
9. **Green Keeper** over the mandatory gate set, which this Gate extends.
10. **Delivery Completeness Validator.**
11. **Internal Red Team**, scoped to the Foundation.
12. **Milestone Closure Auditor**, the internal mirror.
13. `INTERNAL_GATE_PASS`, sealed.

## The tooling this Gate had to generalise first

The control plane was written while SETUP-00 was the only Gate, and four things were coupled to
that. Each is a change to a control, so each is recorded rather than done quietly:

| Coupling | Why it blocks Gate 0 | Change |
|---|---|---|
| The expected requirement set cited `docs/SETUP-00-CHECKLIST.md` by literal | every Gate 0 requirement would cite a document that does not contain it | derive the specification path from the registry |
| The delivery-assurance scope covered `scripts/`, `tests/`, `docs/` and the policies | editing the API, the worker or the stack would leave every gate result looking fresh | add the runtime prefixes to the scope |
| The `TESTS` denominator counted `tests/` alone | the backend and infrastructure suites would not exist to the ledger | a canonical test-suite registry the count derivation reads |
| The internal mirror audit refused a tree containing `services/` | Gate 0 creates that directory as part of the layout it is required to deliver | judge scope against the Gate under audit, using a scope registry |

The fourth is the one worth stating plainly: the old control asserted "no Gate 0 runtime exists",
which was correct while SETUP-00 was the current Gate and is the wrong question now. It is replaced
by a stronger one — no capability reserved for a *later* Gate is implemented — which applies to
every Gate including this one, and which the Red Team attacks directly.

## Stack

Adopted as authorised, with the choices inside it recorded in
`docs/adr/ADR-0012-foundation-runtime-stack.md`. Python 3.13 and FastAPI; Angular 22 built in a
container; PostgreSQL 17 with pgvector; Redis 8.2; MinIO; Temporal 1.29 with the worker as a
separate process; Prometheus and Grafana provisioned from files; Docker Compose. Every version is
pinned and recorded in `docs/VERSIONS.md`.

Three decisions inside the stack get their own ADRs because a later Gate will be constrained by
them: pgvector prepared but unused (`ADR-0013`), one PostgreSQL server with separate databases for
Temporal (`ADR-0014`), and OpenTelemetry deferred to the Gate that has something to trace
(`ADR-0015`).

## How this Gate is verified

One command, `python scripts/iacode/verify.py`, reading the mandatory gate set from policy rather
than carrying its own list. Seventeen stages: nine mandatory gates, the stack, the backend
integration suite against the real services, the live infrastructure suite, the smoke check, a
verified backup-and-restore cycle, a dependency scan, and the restart, dependency-failure and
fresh-installation scenarios.

The last stage deletes every volume and rebuilds from nothing, because that is the claim the Gate
actually makes.

## Risks carried into the work

Recorded in `RISKS.md` and revisited at the end. The ones that shaped the plan: the stack is heavy
for one machine, the host's Node is too old for the frontend toolchain, and seventeen unrelated
containers were already running on the ports a default stack would want.

## Stop conditions

- The milestone verdict does not derive as `PASSED` → `BLOCKED`, no implementation.
- A mandatory gate cannot be made green by repairing its cause → `BLOCKED` with the blocker named,
  never `READY_FOR_REVIEW`.
- Any requirement `PARTIAL` or `MISSING` at handoff → not a positive terminal status.
- An attack escapes the internal Red Team → back to implementation.
- Anything that would need a sealed checkpoint rewritten or a historical tag moved → stop.
