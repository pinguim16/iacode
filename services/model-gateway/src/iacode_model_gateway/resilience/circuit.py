"""A circuit breaker over provider calls.

The failure it prevents is specific: a provider that is down does not merely fail requests, it fails
them *slowly*. Every caller waits out the full timeout before learning what the previous caller
already knew, so an outage at the provider becomes an outage of everything that depends on the
gateway. The breaker converts "wait thirty seconds, then fail" into "fail now, and consider a
different candidate", which is the difference between a degraded gateway and a hung one.

Three states, and one deliberate asymmetry between them:

``CLOSED``     calls go through. Consecutive failures accumulate; any success clears the count,
              because scattered failures are normal and only a *run* of them is a signal.
``OPEN``      calls fail immediately with ``CIRCUIT_OPEN``, which is a fallback-eligible class, so
              the router moves on instead of stopping.
``HALF_OPEN``  after the cooldown, one probe at a time is admitted. A success closes the circuit; a
              failure reopens it and restarts the cooldown, so a provider that is still broken is
              not hammered by every caller that happened to arrive after the timer expired.

The scope is the pair. A provider that is entirely down trips its provider-level breaker; a single
model that is unavailable while the rest of the provider works trips only its own. Keeping only the
first would let one bad model take a healthy provider offline; keeping only the second would make
a total outage cost one timeout per model in the catalog.

Time is injected. The suite exercises a thirty-second cooldown in microseconds through the same
code path production runs.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum

from iacode_model_gateway.ports import Clock

__all__ = ["CircuitBreaker", "CircuitState", "CircuitSettings"]


class CircuitState(StrEnum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


@dataclass(frozen=True)
class CircuitSettings:
    """Externally configured thresholds."""

    failure_threshold: int = 5
    cooldown_seconds: float = 30.0
    half_open_successes: int = 1


@dataclass
class _Circuit:
    state: CircuitState = CircuitState.CLOSED
    failures: int = 0
    successes: int = 0
    opened_at: float = 0.0
    probe_in_flight: bool = False


@dataclass
class CircuitBreaker:
    """One breaker per scope key, with the scopes created on first use."""

    settings: CircuitSettings
    clock: Clock
    _circuits: dict[str, _Circuit] = field(default_factory=dict)

    def state(self, key: str) -> CircuitState:
        """The state of one scope, after applying any cooldown that has expired."""
        circuit = self._circuits.get(key)
        if circuit is None:
            return CircuitState.CLOSED
        if circuit.state is CircuitState.OPEN and self._cooled_down(circuit):
            circuit.state = CircuitState.HALF_OPEN
            circuit.successes = 0
            circuit.probe_in_flight = False
        return circuit.state

    def allow(self, key: str) -> bool:
        """Whether a call on this scope may proceed now.

        In ``HALF_OPEN`` exactly one probe is admitted at a time. Admitting all of them would send
        the whole queued load at a provider that has given no evidence of having recovered.
        """
        state = self.state(key)
        if state is CircuitState.CLOSED:
            return True
        if state is CircuitState.OPEN:
            return False
        circuit = self._circuits[key]
        if circuit.probe_in_flight:
            return False
        circuit.probe_in_flight = True
        return True

    def record_success(self, key: str) -> None:
        circuit = self._circuits.setdefault(key, _Circuit())
        circuit.probe_in_flight = False
        if circuit.state is CircuitState.HALF_OPEN:
            circuit.successes += 1
            if circuit.successes >= self.settings.half_open_successes:
                circuit.state = CircuitState.CLOSED
                circuit.failures = 0
                circuit.successes = 0
            return
        circuit.failures = 0
        circuit.state = CircuitState.CLOSED

    def record_failure(self, key: str) -> None:
        circuit = self._circuits.setdefault(key, _Circuit())
        circuit.probe_in_flight = False
        if circuit.state is CircuitState.HALF_OPEN:
            # The probe failed. Reopening restarts the cooldown rather than continuing the old one,
            # so a provider that is still broken gets the full interval again.
            circuit.state = CircuitState.OPEN
            circuit.opened_at = self.clock.monotonic()
            circuit.successes = 0
            return
        circuit.failures += 1
        if circuit.failures >= self.settings.failure_threshold:
            circuit.state = CircuitState.OPEN
            circuit.opened_at = self.clock.monotonic()

    def snapshot(self) -> dict[str, CircuitState]:
        """Every known scope and its current state, for the metrics and the health endpoint."""
        return {key: self.state(key) for key in sorted(self._circuits)}

    def _cooled_down(self, circuit: _Circuit) -> bool:
        return (self.clock.monotonic() - circuit.opened_at) >= self.settings.cooldown_seconds


def scope_keys(provider_id: str, model_id: str | None) -> tuple[str, ...]:
    """The breaker scopes one call belongs to, widest first.

    Checking the provider scope first means a total outage is refused after one lookup instead of
    after one lookup per model.
    """
    if model_id is None:
        return (f"provider:{provider_id}",)
    return (f"provider:{provider_id}", f"model:{provider_id}:{model_id}")
