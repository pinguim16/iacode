# Risks — GATE-0-CP-0001

What could go wrong, what would make it a defect rather than a risk, and what is already in place.

## R1 — The stack is heavy for one machine

Nine long-running containers, plus two one-shot jobs. On a laptop already running other work this
is a real cost, and the machine this Gate was delivered on had seventeen unrelated containers up.

**Becomes a defect when:** a contributor cannot run the verification because the stack will not fit,
and the Gate's success criterion stops being reachable.

**In place:** every published port binds to loopback and comes from configuration, so the stack
cannot collide with another; `verify.py --fast` skips the stages that restart the stack; images are
two-stage and small.

**Accepted because:** the alternative is substituting components, and a foundation that exercises
substitutes has not established the foundation.

## R2 — Docker is now a hard requirement of the repository

Every service, every image build and four of the nine mandatory gates need it. A contributor without
Docker cannot run the mandatory gate set at all.

**Becomes a defect when:** an environment that must deliver this repository cannot run Docker, and
the mandatory set becomes unmeasurable there.

**In place:** stated in `docs/VERSIONS.md` and `docs/DEVELOPMENT.md` as a requirement rather than as
tooling; the gates fail with an actionable message rather than a traceback when it is absent.

**Carried into M1:** if a Gate 1–3 environment cannot run Docker, the gate registry has to grow a
way to express that, and the answer is not to weaken the set.

## R3 — The mandatory gate set now takes minutes

Nine gates, four of which build or run containers. The control-plane suite alone takes about eleven
minutes on this machine; the full verification is longer.

**Becomes a defect when:** the cycle is slow enough that the Green Keeper is run less often, which
is how a red gate survives.

**In place:** `--fast`, layer caching, the frontend toolchain built once and reused between the test
and lint gates.

**Carried into M1:** if Gate 1 adds more, the set needs a fast subset that is still closed — not a
smaller mandatory set.

## R4 — Stopping PostgreSQL stops Temporal

Temporal persists into the same PostgreSQL server. It is declared in `ADR-0014`, asserted by the
dependency-failure scenario and by Red Team attack `G0-Y`, and documented in the runbook.

**Becomes a defect when:** the coupling grows beyond what is declared — for example if Temporal's
load started affecting the system of record's availability.

**In place:** separate databases, so a backup of `iacode` is clean; the blast radius is a declared
set the scenario compares exactly, so a widening is a test failure rather than a surprise.

**Reversal:** a dedicated `temporal-postgres` service, described in the ADR. Temporal rebuilds its
schema on first boot, so no data migrates.

## R5 — The frontend suite is outside the derived TESTS denominator

Its cases are TypeScript, collected by Vitest inside the toolchain container. The Python count
derivation cannot recompute that number, so the suite is declared `counted: false` with a reason and
is evidenced by its recorded execution.

**Becomes a defect when:** "not counted" starts being used for a suite that *could* be counted,
which would be exactly the denominator escape the `M0` audit found.

**In place:** `test-suites.json` refuses an uncounted suite that records no reason;
`test_an_uncounted_suite_declares_why` asserts it; the suite runs in a mandatory gate, so it cannot
silently stop running.

**Carried into M1:** the honest repair is a countable frontend derivation, not a wider exception.

## R6 — Four control-plane controls were generalised by this Gate

The expected-set derivation, the assurance scope, the count derivation and the mirror's scope check
were all coupled to SETUP-00 and had to change before any product code could be delivered. Changing
a control is how a control gets weakened.

**Becomes a defect when:** one of the four turns out to be weaker rather than more general.

**In place:** each change makes the control apply to *more* deliveries, not fewer; each is covered
by tests in `tests/test_gate0_foundation.py`; the scope change is attacked directly by `G0-O` and
`G0-P`; the sealed history still validates, which `MIR-016` checks by running the current validator
against every sealed checkpoint.

**The one to watch:** `MIR-018`. The old assertion ("no Gate 0 runtime exists") was concrete and
easy to check. The new one ("no capability reserved for a later Gate is implemented") is broader and
depends on the reservation registry being kept honest. A path nobody reserves is a path nobody
protects.

## R7 — The pgvector extension is created and unused until Gate 7

It could rot unnoticed, or be removed by someone swapping the image back to plain `postgres`.

**In place:** `test_pgvector_extension_is_available` reads `pg_extension` against the running
database and fails the moment it is not there.

## R8 — The smoke workflow is the only thing exercising Temporal

Durable execution is a large dependency carrying one workflow. Its failure modes under real load are
untested, because there is no real load.

**Becomes a defect when:** Gate 2 discovers a property of Temporal that makes it unsuitable, after
the Foundation has been built around it.

**Accepted because:** the alternative is a task queue that Gate 2 would have to replace, and this
Gate's job is to establish the boundary rather than to exercise it.

## R9 — The verification's own runtime depends on an image build succeeding

Several gates build an image before running. A registry outage or a base-image change makes them
fail for reasons unrelated to the delivery.

**In place:** every base image and every dependency is pinned exactly, so the only failure of this
kind is a registry that cannot serve a pinned artefact; the lock files mean a resolution never
changes silently between two builds of the same commit.
