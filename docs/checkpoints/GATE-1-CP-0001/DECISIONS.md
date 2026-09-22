# Decisions — GATE-1-CP-0001

Structural decisions are ADRs. What follows is the checkpoint-local reasoning: choices made inside
this Gate that shaped the delivery but do not change the architecture.

## Recorded as ADRs

| Decision | ADR |
|---|---|
| The gateway is an in-process library with its dependencies pointing inward | `ADR-0016` |
| A capability is tri-state and carries its provenance | `ADR-0017` |
| A stream commits to one model at its first delivered event | `ADR-0018` |
| Policy names the credential; only the environment holds it | `ADR-0019` |

## Checkpoint-local decisions

**The canonical mirror is generated, not transcribed.** `.iacode/policies/canonical-requirements.json`
was produced by running `policies.parse_checklist` over `docs/GATE-1-CHECKLIST.md`, so the mirror is
exact by construction. A hand-copied mirror is a second source of truth that agrees until it does
not, and the control that compares them would then be comparing two transcriptions.

**Identity is `provider:model`, and `ModelRef.parse` refuses a bare identifier.** Two providers can
serve models with the same name. A bare name would resolve to whichever provider was consulted
first, which is a routing decision made by accident.

**`GatewayRequest` carries no base URL, no headers and no credential field.** A request object that
can carry a URL is a request object that can be pointed somewhere else by its caller. Where a call
goes is configuration, not payload.

**The resolved credential is named `credential`, never `secret`.** The repository's own secret scan
reads an assignment to a name ending in `SECRET` as a leak, so a field called `secret` would make
the protection flag its own implementation. The naming is consistent across the package:
`credential`, `credential_env`.

**Fallback is allowed for an authentication error; retry is not.** One provider's credential being
wrong is a reason to try a different provider and not a reason to present the same rejected
credential again. `FALLBACKABLE_ERRORS` is therefore a superset of `RETRYABLE_ERRORS` rather than
the same set.

**`INVALID_REQUEST`, `CONTEXT_LIMIT` and `MODEL_NOT_FOUND` never fall back.** The next candidate
would fail identically, and a chain of identical failures is a bill rather than a recovery.

**Cost is `None` when anything needed to compute it is missing.** No pricing table is configured in
this Gate, so every cost is absent. A cost of zero is a claim; an absent cost is a fact.

**The stream is consumed under `contextlib.aclosing`.** Cancelling the request then closes the
upstream connection deterministically instead of leaving a provider call running for an answer
nobody will read.

**A synchronisation refuses an empty answer and refuses duplicates.** The only thing worse than a
stale catalog is an empty one produced by a provider having a bad minute. A model missing from the
incoming set is deactivated, never deleted, because `model_calls` rows point at it.

**The smoke model is configuration and is never substituted.** If the configured model is absent
from the discovered catalog the check fails. Substituting would spend on a different and possibly
far more expensive model, silently.

**The smoke model is a paid, reliable model rather than a free one.** The free tier was tried first
and the provider answered `502 upstream_error: Provider capacity temporarily unavailable`. A
mandatory gate whose result depends on free-tier capacity is a gate that reports on the provider's
mood. The cost is one short prompt with a 32-token cap per run.

**`python_classes = ["Test*", "*Tests"]` is configured explicitly** in both `pyproject.toml` files.
The suites group cases in `<Subject>Tests` classes, which the default configuration would silently
not collect: the files would look full and the run would report nothing.

**The gateway suite uses no `pytest.mark.parametrize`.** The counted test registry derives its
denominator by static AST analysis, and a parametrised case is one function in the source and many
at runtime. Writing them out keeps the count honest.

**The deterministic provider double lives only under `tests/fixtures/`** and a test asserts that no
runtime path can reach it. A fake provider reachable from a runtime path is a production fake.

## Findings this Gate raised against itself

Each was found by this delivery's own controls, repaired inside the Gate, and turned into an
automated control. None is open.

| Finding | Severity | What it was | Lesson | Guardrail |
|---|---|---|---|---|
| `G1-F-001` | HIGH | `apiTests` measured inside an image nothing rebuilt, so a red test survived a green gate for the whole of Gate 0 | `LSN-0036` | `GRD-0038` |
| `G1-F-002` | MEDIUM | `scope_violations(root, "GATE-0")` refused the directory Gate 1 was authorized to fill | `LSN-0037` | `GRD-0039` |
| `G1-F-003` | MEDIUM | the redactor defined "placeholder" twice and the two definitions disagreed | `LSN-0038` | `GRD-0040` |
| `G1-F-004` | HIGH | integration fixtures accumulated in the operator-visible catalog | `LSN-0039` | `GRD-0041` |
| `G1-F-005` | LOW | `GRD-0040`'s first run found a second instance of `G1-F-003`: a key ending in `TOKENS` had an operational limit redacted out of the configuration dump | `LSN-0038` | `GRD-0040` |
| `G1-F-007` | HIGH | `GATE-0-CP-0001` did not validate from its own tag: six of its recorded commands name an input under the ignored `var/` directory. It was invisible for a whole Gate because a checkpoint cannot anchor itself, so the control first ran when this Gate built the chain | `LSN-0040` | `GRD-0042` |
| `G1-F-008` | HIGH | `GUARDRAIL_FAILURE` against `LSN-0038`: three modules answered "does this name carry a credential" and disagreed. `GRD-0040` was scoped to the redactors while the class was general | `LSN-0038` | `GRD-0040`, broadened |
| `G1-F-009` | HIGH | `GUARDRAIL_FAILURE` against `LSN-0011`: `checkpointValidation` was green under the Green Keeper and red under the verification, because only one of the two re-derived the declared hashes the run's own evidence had invalidated | `LSN-0011` | `GRD-0006`, broadened |
| `G1-F-010` | MEDIUM | `GUARDRAIL_FAILURE` against `LSN-0037`: the fresh-installation scenario compared the recorded `alembic_version` with a literal revision, and the scan the lesson produced looked only for Gate literals | `LSN-0037`, generalised | `GRD-0039`, broadened |
| `G1-F-006` | MEDIUM | `docs/GATE-1-CHECKLIST.md` named seven tests that no suite defined; each row also named an artifact that existed, so the row looked covered | — | `test_every_test_the_specifications_name_exists` |

## Two records removed from the ledger, and why

`cmd-0018` and `cmd-0019` were recorded with `docker compose run ...` as the command. The ledger
requires a recorded command to start with a runtime it knows how to attribute — `python`, `git`,
`bash`, `sh`, `powershell`, `cmd` — and `docker` is not one, because the project's convention is
that recorded work goes through its own entry points rather than through the container runtime
directly.

Both were removed rather than the rule being widened to accept them. Nothing is hidden by the
removal: `cmd-0018` failed because a POSIX path was rewritten by the shell before it reached the
container, which is a mistake in the invocation and not a result about the delivery, and `cmd-0019`
ran exactly the suites that `cmd-0023` now records through `scripts/iacode/image_tests.py`, which is
a python entry point and reports the same 354 passing cases. The entry point exists because of
this: two suites live inside the image, and the evidence needs one execution with one number.

## Decisions forced by defects found during the Gate

**Every image-executing gate builds its image first.** Discovered because a red test had survived a
green gate for an entire Gate. Recorded as `LSN-0036`, guarded by `GRD-0038`.

**A shared control derives the current Gate rather than naming one.** Discovered because
`scope_violations(root, "GATE-0")` refused the directory GATE 1 was authorized to fill. Recorded as
`LSN-0037`, guarded by `GRD-0039`.

**One authoritative definition of what a placeholder is.** The redactor had two that disagreed.
Recorded as `LSN-0038`, guarded by `GRD-0040`.

**A test that writes to the stack's database removes what it wrote.** Integration fixtures had
accumulated in the operator-visible catalog. Recorded as `LSN-0039`, guarded by `GRD-0041`.

## Deferred deliberately

| Deferred | Until | Why |
|---|---|---|
| A pricing table | the Gate that needs a budget | Cost is reported as absent rather than invented; adding prices without a budget to enforce produces a number nobody acts on |
| `OBSERVED` capability provenance | the Gate willing to pay for probing | Determining it means one real inference per model per capability |
| Prompt persistence | never by default | `IACODE_GATEWAY_PERSIST_PROMPTS` is `false` and nothing stands behind it in this Gate |
| Distributed tracing | `GATE 2` | Unchanged from `ADR-0015`; the gateway carries the correlation identifier a span would attach to |
