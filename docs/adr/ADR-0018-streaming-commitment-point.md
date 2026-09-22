# ADR-0018 — A stream commits to one model at its first delivered event

Status: Accepted
Date: 2026-09-22
Owners: GATE 1 — Model Gateway

## Context

The gateway retries transient failures and falls back to the next candidate when a model cannot
serve a request. For a non-streaming call this is invisible and unambiguous: nothing has reached
the caller, so the gateway can try again and return whichever attempt succeeded.

Streaming breaks that assumption. Once the consumer has received a delta, part of one model's
answer is already on their screen. If the connection then fails and the gateway retries — or falls
back to a different model — the new answer is appended to the old fragment. The consumer receives
one stream containing two models' text, spliced at an arbitrary token, with no marker saying where.

That is worse than an error. An error is a failure the caller can handle; a spliced stream is a
plausible-looking answer that no model produced, and it will be quoted, logged and acted on.

`docs/GATE-1-CHECKLIST.md` row 15.7 requires a test proving two models' output can never be
concatenated into one stream. This ADR records the rule that test defends.

## Decision

**Retry and fallback are permitted only until the first event reaches the consumer.**

The gateway maintains a `delivered` counter for the stream. While it is zero, a failure is handled
exactly as a non-streaming failure would be: retried if the error class is retryable, moved to the
next candidate if the class is fallbackable. The moment it becomes non-zero, the stream is
committed to the model that produced that event, and any later failure is emitted as an `error`
event and terminates the stream.

The counter is the number of events actually handed to the consumer, not the number received from
the provider. An upstream chunk that fails to decode has not been delivered and does not commit
anything.

Three supporting rules follow from it:

- Every event carries a monotonic sequence number, so a consumer can detect a gap rather than
  trusting the ordering.
- The stream is consumed under `contextlib.aclosing`, so cancelling the request closes the upstream
  connection deterministically rather than leaving a provider call running for an answer nobody
  will read.
- A failure before the first delta is indistinguishable from a non-streaming failure, and is
  reported with the same taxonomy and the same route decision.

## Evidence

- `services/model-gateway/src/iacode_model_gateway/gateway.py`: the `delivered` counter and the
  `async with aclosing(upstream) as chunks:` consumption.
- `services/model-gateway/tests/test_streaming.py::test_no_two_models_are_concatenated_in_one_stream`
  is the direct control; the same file covers a normal stream, an empty stream, a failure before
  the first delta, a failure after the first delta, consumer cancellation, usage at the end and a
  tool-call delta.
- Live: `scripts/iacode/gateway_smoke.py` asserts `stream.not_duplicated` — every sequence number
  distinct and ascending, and the expected answer appearing exactly once.

## Alternatives Considered

**Buffer the whole stream, then decide.** Makes retry safe by removing streaming: the consumer sees
nothing until the model has finished, which is the entire property streaming exists to provide.

**Splice and mark the seam.** Emit a `model_changed` event and continue. It keeps the request alive
at the cost of a stream whose text nobody generated. Every consumer would then need to handle a
mid-answer model change correctly, and the ones that do not would silently produce a hybrid.

**Restart the stream from the beginning on the new model.** The consumer has already rendered the
first fragment; telling them to discard it requires a protocol for retraction that every client
must implement, to recover from a case that is rare. An `error` event is a protocol every client
already has.

**Never retry a stream at all.** Simple and needlessly strict: a connection that fails during the
provider handshake, before a single byte has been delivered, is exactly the case retry exists for.

## Consequences

- A stream that fails after its first delta ends in `error`. The caller decides whether to ask
  again; the gateway does not decide for them.
- Fallback is most useful precisely where it is cheapest — before any work is visible.
- The `delivered` counter is load-bearing. It is a one-line condition guarding a property that is
  invisible when it holds and severe when it does not, which is why the test naming it exists.

## Risks

- **A future refactor moves the counter increment.** Mitigated by the named test, which fails on
  concatenated output rather than on the implementation detail.
- **Consumers treat `error` after partial content as "nothing happened".** Documented in the
  runbook: the events before the error were real and the tokens were spent.

## Reversal Strategy

The rule is one condition in `gateway.py`. Removing it re-enables mid-stream fallback and requires
a protocol change to announce the switch, plus a client contract for handling it — which is the
work this decision avoids, not a detail it postpones.

## Related Artifacts

- [ADR-0016](ADR-0016-model-gateway-boundary.md)
- `docs/GATE-1-CHECKLIST.md` rows 9.x, 15.6, 15.7
- `docs/runbooks/MODEL-GATEWAY.md`
