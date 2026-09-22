# ADR-0016 — The Model Gateway is an in-process library with its dependencies pointing inward

Status: Accepted
Date: 2026-09-22
Owners: GATE 1 — Model Gateway

## Context

`docs/GATE-1-CHECKLIST.md` row 2.1 requires the gateway to live in the directory the Foundation
reserved for it, to be consumed in process, and for the boundary decision to be recorded rather
than implied.

Gate 0 reserved `services/model-gateway/` and left it as a README saying `Status: RESERVED`. The
name `services/` invites the assumption that this is a network service. It is not, and the reason
matters more than the convention.

Three questions had to be answered together: does the gateway run in its own process; which
direction does the dependency point between it and the API; and where does I/O happen inside it.

## Decision

**A library in `services/model-gateway/`, composed by the API in process. The gateway declares
storage as ports and the application implements them. Protocol adapters perform no I/O.**

Concretely:

- `iacode_model_gateway` is a Python package with its own `pyproject.toml`, installed into the API
  image. It has no process, no port and no database of its own.
- It depends on `iacode-common`, `iacode-telemetry`, `httpx`, `pydantic` and `prometheus-client`.
  It does **not** depend on `iacode-api`. The application composes the gateway; never the reverse.
- It declares four ports in `ports.py` — `CatalogStore`, `ModelCallStore`, `Clock`, `Jitter` — and
  `apps/api/src/iacode_api/gateway/store.py` implements the first two in SQLAlchemy. The gateway
  has no idea a database exists.
- The three protocol adapters translate between the gateway's contracts and one provider protocol
  each. They build an `HttpCall`, parse a completion, decode a stream chunk, parse a catalog entry
  and classify an error body. **None of them opens a socket.** `HttpModelProvider` is the only
  thing in the package that does.

## Evidence

- `services/model-gateway/pyproject.toml` lists no IACode dependency beyond the two cross-cutting
  packages.
- `services/model-gateway/tests/test_package.py::test_gateway_package_is_importable` and the
  boundary scan in `tests/test_gate1_model_gateway.py::GatewayBoundaryTests`, which fails if any
  gateway module imports `iacode_api` or names a provider in a provider-neutral module. The scan
  carries a negative control, so a scan that has stopped scanning is itself detected.
- `services/model-gateway/tests/test_provider_contract.py` runs the same scenarios against all
  three adapters with `httpx.MockTransport` and no network.
- `apps/api/src/iacode_api/lifespan.py` builds the runtime; `services/model-gateway/README.md`
  records the reservation as consumed.

## Alternatives Considered

**A separate HTTP service.** It would make the boundary physical and unmistakable. It also adds a
container, a network hop on every inference, a second deployment unit, an authentication scheme
between our own components, and a serialisation format for streaming that would have to be invented
and then kept in step with the one we already expose. Nothing in Gate 1 needs independent scaling of
the gateway, and the boundary is already enforceable statically. The library can become a service
later without its consumers changing, because they already talk to an interface rather than to
`httpx`.

**A module inside `apps/api`.** Simplest, and it makes the dependency direction unenforceable: the
first `from iacode_api.db import ...` inside the gateway would pass review as an obvious
convenience, and the second consumer would inherit a web application to use a model.

**Adapters that make their own HTTP calls.** The usual shape, and it means timeout handling, retry
classification, frame-size limits and cancellation are re-implemented — differently — in each
adapter, and every adapter test needs a network double. One `HttpModelProvider` means one place
where a transport bug can live.

## Consequences

- A second consumer (the Gate 2 agent runtime) can use the gateway by implementing the same ports,
  without the API.
- Adapters are testable as pure functions. Adding one means translation plus a row in the contract
  suite, not a new I/O path.
- The gateway cannot be scaled or deployed independently of the API. That is acceptable now and is
  the thing this decision trades away.
- `services/` now contains one thing that is not a service. The README says so in its first line.

## Risks

- **The directory name misleads a future reader.** Mitigated by the README and by this ADR;
  renaming the reserved directory would break the Gate 0 scope registry for no functional gain.
- **The boundary erodes through a convenient import.** Mitigated by the static scan being a
  mandatory test rather than a review habit.

## Reversal Strategy

Wrap the package in a FastAPI application of its own, implement the ports against a database it
owns, and replace the in-process composition in `lifespan.py` with an HTTP client that satisfies
the same interface. No consumer code changes, because no consumer knows how the gateway is reached.

## Related Artifacts

- [ADR-0012](ADR-0012-foundation-runtime-stack.md)
- [ADR-0017](ADR-0017-capabilities-are-tri-state.md)
- `docs/GATE-1-CHECKLIST.md` rows 2.1, 2.5, 4.x
- `.iacode/policies/gate-scope.json`
