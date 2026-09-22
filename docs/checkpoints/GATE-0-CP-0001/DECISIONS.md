# Decisions — GATE-0-CP-0001

The decisions of this delivery, with what they cost and what was given up. Structural ones have
ADRs; this records the rest, and the reasoning behind the ones that were not obvious.

## The architectural decisions have ADRs

| Decision | Where |
|---|---|
| The runtime stack and the boundaries inside it | `docs/adr/ADR-0012-foundation-runtime-stack.md` |
| pgvector prepared, not used | `docs/adr/ADR-0013-pgvector-prepared-not-used.md` |
| One PostgreSQL server, separate databases for Temporal | `docs/adr/ADR-0014-one-postgresql-server-for-the-foundation.md` |
| OpenTelemetry deferred | `docs/adr/ADR-0015-opentelemetry-deferred.md` |

Nothing already recorded was duplicated. FastAPI, PostgreSQL, Temporal and MinIO were named by the
Gate authorization, so `ADR-0012` records the choices *inside* that stack rather than re-deciding it.

## Generalising four controls before implementing anything

The control plane was written while SETUP-00 was the only Gate. Four things were coupled to that,
and each blocked Gate 0 outright. They were changed first, deliberately and visibly, rather than
worked around.

**The expected requirement set named one document by literal.** Every derived requirement cited
`docs/SETUP-00-CHECKLIST.md`, which is right for SETUP-00 and wrong for every other Gate: a Gate 0
requirement would point a reader at a document that does not contain the row. The specification path
now comes from the registry entry for the Gate being derived. The source kind changed from `SETUP`
to `GATE_SPECIFICATION`; sealed checkpoints keep their stored value and their own schema, so nothing
historical was invalidated.

**The delivery-assurance scope did not cover the product.** A Green Keeper `PASS`, a completeness
`PASS`, a Red Team result and a mirror audit are statements about a specific content, and the scope
that defines "changed" listed `scripts/`, `tests/`, `.iacode/`, `.claude/`, `prompts/` and `docs/`.
With the runtime outside it, editing the API, the worker, the frontend or the compose stack would
have left every gate result looking fresh while describing content that no longer existed. The
runtime prefixes were added.

**The `TESTS` denominator counted one suite.** `.iacode/policies/test-suites.json` now declares
every suite, and the count derivation and the evidence resolver both read it. A suite that is *not*
counted has to say why, because an omission from a denominator is exactly the shape of the
completeness escape the `M0` audit found. The frontend suite is the one uncounted suite: its cases
are TypeScript collected by Vitest inside the toolchain container, and a number the Python
derivation cannot recompute would be a claim rather than a measurement. It is evidenced by its
recorded execution instead.

**The internal mirror audit refused a tree containing `services/`.** `MIR-018` asserted "no Gate 0
runtime present", which was the right control while SETUP-00 was current and the wrong question the
moment Gate 0 created that directory as part of the layout it is required to deliver.

The replacement is stronger rather than weaker. `.iacode/policies/gate-scope.json` names each
reserved path and the Gate that owns it; the control fails a delivery that puts an implementation in
a path reserved for a *later* Gate. That applies to every Gate including this one, it is derived
from policy rather than from a directory name written into a tool, and the Red Team attacks it
directly (`G0-O`, `G0-P`). The alternative — leaving the literal and adding an exception for Gate 0
— would have been a control that stops applying the moment it is inconvenient.

## The Gate's own test suites, and where each runs

| Suite | Runs | Why there |
|---|---|---|
| `tests/` | host, standard library | the control plane; it must run where the ledger runs |
| `apps/api/tests/unit/` | inside the API image, no stack | the mandatory gate has to be runnable, so it needs no nine healthy containers |
| `apps/api/tests/integration/` | inside the API image, against the live stack | `docs/DEVELOPMENT-CONTRACT.md` forbids a mock where the test stack has the real service |
| `infra/tests/` | host | it shells out to Docker and reads the stack over HTTP |
| `apps/web/src/**.spec.ts` | inside the toolchain image | the host's Node is 18 and the toolchain needs 22 |

The split between the API unit and integration suites is the load-bearing one: a mandatory gate that
cannot run without the whole stack up is a gate that gets skipped rather than fixed.

## Three defects the delivery's own tests found

Recorded because a delivery that reports only its successes has not been reviewed.

**A configuration key with no reader.** `temporal_task_queue` was declared in the API's settings and
consumed by nothing: the API is a Temporal *client* in Gate 0 and starts no workflow.
`test_every_declared_key_is_read_somewhere` reads the application source and failed on it. The key
was removed, and the comment in its place says why the API does not carry one. This is the failure
class `.iacode/memory/lessons.jsonl` already records as `LSN-0028`.

**Error responses carried no correlation identifier.** The unhandled-exception handler runs in
Starlette's outermost error middleware, outside the task the correlation middleware binds its
context in, so the context variable was empty there. A caller was told to quote an identifier the
response did not contain. The handlers now read `request.state` first, which lives on the shared
scope, and set the header on the response as well.

**Every metric was labelled `<unmatched>`.** The route template was resolved by re-matching the
request against `app.routes`, and FastAPI wraps an included router in a single object, so the
top-level list does not contain the routes the routers own. The dashboard looked like it was
working. The template now comes from `scope["route"]`, which the router sets on the route it
actually matched, read after the request is handled.

## Smaller decisions worth recording

**The frontend reads its backend address at run time.** `config.json` is written by the container's
entrypoint from its environment, so one image runs against any backend. Compiling the address into
the bundle would mean an image per environment, which defeats the point of building one.

**The API is started with uvicorn's `--factory` flag.** A module-level `app = create_app()` would
read the environment as a side effect of importing the module, so every test importing `create_app`
would first build an application from the ambient configuration.

**`settings_for_tests` must supply every field.** It asserts that it does. The API test suite runs
inside a container whose environment is full of real `IACODE_*` values, and a field left out would
silently inherit one.

**The worker's healthcheck asks Temporal, not the operating system.** "The process exists" would
report a worker whose connection had dropped as healthy. `DescribeTaskQueue` returns the pollers
Temporal can see, which is the fact the healthcheck is supposed to establish.

**A `merge_stderr` parameter that did nothing.** An earlier edit added the parameter and its
documentation but not its effect — the same defect class as the unused configuration key, found in
this delivery's own tooling. It was implemented, and the docstring corrected: it helps for
`docker compose exec` and does *not* help for `docker compose run`, which narrates container
lifecycle on stdout. The scripts that need a value from a `run` exchange it through a mounted file.

**Retention is seven backups and no scheduler.** `docs/GATE-0-CHECKLIST.md` row 12.5 allows a simple
policy or a documented absence. A scheduler, offsite copies and lifecycle rules are operations
concerns this Gate has no environment to exercise, and a feature nobody can test is worse than a
documented boundary.

## What was deliberately not done

- No endpoint over the domain tables. They are a persistence contract; an endpoint returning an
  empty list would be a capability this Gate does not have.
- No queue, rate limiter or cache helper on Redis. The shape of those is decided by the component
  that needs them.
- No Artifact Service. Gate 0 proves the bytes survive a write, a read and a delete.
- No agent workflow. One smoke workflow, which stays as small as it is.
- No vector column. The embedding dimension follows from a model Gate 1 has not selected.
