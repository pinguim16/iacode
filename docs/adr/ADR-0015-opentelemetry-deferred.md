# ADR-0015 — OpenTelemetry is deferred to the Gate that needs traces

Status: Accepted
Date: 2026-09-21
Owners: GATE 0 — Foundation

## Context

`docs/GATE-0-CHECKLIST.md` row 11.6 requires the OpenTelemetry position to be **decided and
recorded** rather than left implicit. The Gate 0 authorization allows either: implement the
essential base if the architecture already assumes it, or document the deferral if adding it now
would inflate the scope without immediate benefit.

The question is narrower than "should the project have tracing". It is: what would tracing measure
in Gate 0?

## Decision

**Defer the instrumentation, keep the field.** No OpenTelemetry SDK, no exporter, no collector.

What Gate 0 does have is the shape tracing needs:

- the logging contract already declares `traceId` alongside `correlationId`, and the formatter emits
  it the moment something sets it (`packages/telemetry/src/iacode_telemetry/logging.py`);
- the ambient context that would carry a span is already there, per-task and isolated
  (`packages/telemetry/src/iacode_telemetry/context.py`);
- every request already carries a correlation identifier that is accepted or generated, propagated
  and returned, which is what a trace is grafted onto.

A distributed trace measures work crossing process boundaries. Gate 0 has exactly one such
boundary — the API starting a workflow the worker executes — and one workflow crosses it, a smoke
check. Instrumenting that would mean a collector container, an exporter in three processes and a
storage backend, to observe a call whose duration is already in the metrics.

The Gate that makes tracing worth its cost is **GATE 2 — Agent Runtime**, where a single task fans
out across the model gateway, the sandbox and several agent runs, and the question "where did this
go" stops having an obvious answer. That is the Gate that should choose the exporter and the
backend, because it is the Gate that will read the traces.

The field is declared and unset in the meantime, and the logging contract omits an unset field
rather than writing `"traceId": null` — a field that is always null teaches readers to ignore it
before it ever means anything.

## Evidence

- `iacode_telemetry.context.CONTEXT_FIELDS` includes `traceId`.
- `apps/api/tests/unit/test_observability.py::test_a_field_with_no_value_is_absent_rather_than_null`
  asserts that unset context fields do not appear in a record.
- `apps/api/tests/unit/test_errors_and_correlation.py` covers propagation of the identifier a trace
  would attach to.
- No `opentelemetry` package appears in `apps/api/requirements.lock.txt`.

## Alternatives Considered

**Add the SDK now with a no-op exporter.** It looks like preparation and is mostly cost: three
dependencies, an initialisation path in every process, and spans nobody reads. When Gate 2 arrives
the configuration would be reviewed from scratch anyway.

**Add the SDK and a collector container.** The full setup, exercising one smoke workflow. The stack
is already nine containers; a tenth that observes a single call is infrastructure the Foundation
does not need, which the Gate 0 authorization rules out in as many words.

**Drop `traceId` from the logging contract until it exists.** Tempting, and it would mean changing
the contract in Gate 2 — including every sealed log example — rather than filling in a field that
was always there.

## Consequences

- Gate 0 observability is metrics and structured logs. Both are real, both are scraped, and both
  are enough for the questions this Gate's stack raises.
- Gate 2 adds an SDK and an exporter to processes that already carry the correlation context, so
  the change is instrumentation rather than plumbing.
- `traceId` stays absent from every record until something sets it. That is the contract, not an
  omission.

## Risks

- **Deferral becomes indefinite.** Mitigated by this ADR naming the Gate and the condition, and by
  the field existing in the contract as a standing reminder.
- **Gate 2 discovers the context mechanism is wrong for spans.** Possible; the mechanism is
  `contextvars`, which is what the OpenTelemetry Python SDK itself uses for context propagation.

## Reversal Strategy

Add the SDK to `apps/api/requirements.txt`, initialise a tracer provider in
`iacode_telemetry`, and set `traceId` in the correlation middleware from the active span. The
logging contract, the context mechanism and the propagation path need no change.

## Related Artifacts

- [ADR-0012](ADR-0012-foundation-runtime-stack.md)
- `docs/GATE-0-CHECKLIST.md` row 11.6
- `docs/MASTER-PLAN.md`, `GATE 2 — Agent Runtime`
