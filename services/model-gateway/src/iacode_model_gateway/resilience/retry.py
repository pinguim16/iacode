"""Retrying, bounded and classified.

A retry is only ever correct for a failure that could go the other way next time. The classification
lives in :mod:`iacode_model_gateway.errors`, declared once per error class, and this module applies
it. Nothing here decides *per call site* whether something is worth retrying, because that is how a
retry on an authentication error gets written: at one call site, in isolation, it looks sensible.

**Full jitter, not fixed sleeps.** The delay is ``uniform(0, min(cap, base * 2 ** attempt))``. The
alternative most codebases reach for — a fixed multiplier with no randomness — synchronises every
client that failed at the same moment, so they all come back at the same moment, which is how a
provider recovering from an incident is knocked over by its own clients.

**The provider's ``Retry-After`` wins, up to a bound.** A provider that says "wait 12 seconds" knows
something we do not, and ignoring it wastes a request that is certain to fail. A provider that says
"wait four hours" is not a hint the gateway can honour inside a request, so the wait is capped and
the error is returned instead. Obeying it would turn a rate limit into an indefinitely hung caller.

Time and randomness are injected, so the suite exercises a thirty-second cooldown without spending
thirty seconds. A test that has to wait is a test that gets marked slow and then gets skipped.
"""

from __future__ import annotations

from dataclasses import dataclass

from iacode_model_gateway.errors import GatewayError
from iacode_model_gateway.ports import Clock, Jitter

__all__ = ["RetryDecision", "RetryPolicy"]


@dataclass(frozen=True)
class RetryDecision:
    """Whether to try again, after how long, and why not when the answer is no."""

    retry: bool
    delay_seconds: float = 0.0
    reason: str = ""


@dataclass(frozen=True)
class RetryPolicy:
    """The bounds within which the gateway will try the same candidate again."""

    max_attempts: int = 3
    initial_backoff_seconds: float = 0.25
    max_backoff_seconds: float = 8.0
    max_retry_after_seconds: float = 30.0

    def decide(self, error: GatewayError, attempt: int, jitter: Jitter) -> RetryDecision:
        """Decide whether attempt ``attempt`` may be followed by another one.

        ``attempt`` is one-based: the first call is attempt 1, so ``max_attempts = 3`` allows two
        retries.
        """
        if attempt >= self.max_attempts:
            return RetryDecision(
                retry=False,
                reason=f"the attempt budget of {self.max_attempts} is exhausted")
        if not error.retryable:
            return RetryDecision(
                retry=False,
                reason=f"{error.error_type!s} cannot be resolved by sending the same request again")

        if error.retry_after_seconds is not None:
            if error.retry_after_seconds > self.max_retry_after_seconds:
                return RetryDecision(
                    retry=False,
                    reason=(f"the provider asked for {error.retry_after_seconds:g}s, beyond the "
                            f"{self.max_retry_after_seconds:g}s this gateway will hold a caller"))
            return RetryDecision(
                retry=True, delay_seconds=max(error.retry_after_seconds, 0.0),
                reason="honouring the provider's retry hint")

        ceiling = min(self.max_backoff_seconds,
                      self.initial_backoff_seconds * (2 ** (attempt - 1)))
        delay = jitter.uniform(0.0, ceiling)
        return RetryDecision(retry=True, delay_seconds=delay,
                             reason=f"transient failure, attempt {attempt + 1}")

    async def wait(self, decision: RetryDecision, clock: Clock) -> None:
        """Sleep for a decided delay, through the injected clock."""
        if decision.delay_seconds > 0:
            await clock.sleep(decision.delay_seconds)
