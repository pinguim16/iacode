"""Cost, when cost is known.

`docs/GATE-1-CHECKLIST.md` row 10.2 is short and absolute: **an unknown cost is absent, never zero.**
Zero is a number with a meaning — the call was free — and writing it where "we do not know" belongs
produces a spend report that is confidently wrong and silently useless.

So pricing is configuration the repository does not ship. This project has not agreed a price list
with anyone, prices change without notice, and a table of numbers compiled into the gateway would be
out of date the week after it was written. A provider's rates are set by whoever operates the
deployment, in the same policy file the provider is declared in, and until they are, every call
records ``None``.

The arithmetic is deliberately trivial and deliberately conservative: a cost is computed only when
**both** the token count and the rate for that token kind exist. Half a price is not a price.
"""

from __future__ import annotations

from dataclasses import dataclass

from iacode_model_gateway.contracts import Usage

__all__ = ["ModelPricing", "PricingTable", "estimate_cost"]


@dataclass(frozen=True)
class ModelPricing:
    """Rates for one model, in currency units per million tokens.

    Per million rather than per token because that is how every provider publishes them, and a
    conversion done once here is a conversion nobody has to do again when reading the configuration.
    """

    input_per_million: float | None = None
    output_per_million: float | None = None
    cached_input_per_million: float | None = None
    currency: str = "USD"


class PricingTable:
    """Configured rates, keyed by ``provider:model``. Empty unless an operator fills it."""

    def __init__(self, rates: dict[str, ModelPricing] | None = None) -> None:
        self._rates = dict(rates or {})

    def __len__(self) -> int:
        return len(self._rates)

    def for_model(self, qualified: str) -> ModelPricing | None:
        return self._rates.get(qualified)


def estimate_cost(usage: Usage, pricing: ModelPricing | None) -> float | None:
    """The cost of a call, or ``None`` when it cannot be computed.

    ``None`` is returned whenever any input is missing: no pricing, no token counts, or a rate for a
    kind of token the provider did report. A partial sum would understate the cost while looking
    exactly like a complete one.
    """
    if pricing is None:
        return None

    total = 0.0
    contributed = False

    billable_input = usage.input_tokens
    if billable_input is not None and usage.cached_input_tokens is not None:
        # Cached input is normally billed at a lower rate and is reported *inside* the input count,
        # so charging both would bill it twice.
        billable_input = max(billable_input - usage.cached_input_tokens, 0)

    if billable_input is not None and pricing.input_per_million is not None:
        total += billable_input * pricing.input_per_million / 1_000_000
        contributed = True
    elif usage.input_tokens is not None:
        return None

    if usage.cached_input_tokens:
        if pricing.cached_input_per_million is None:
            return None
        total += usage.cached_input_tokens * pricing.cached_input_per_million / 1_000_000
        contributed = True

    if usage.output_tokens is not None and pricing.output_per_million is not None:
        total += usage.output_tokens * pricing.output_per_million / 1_000_000
        contributed = True
    elif usage.output_tokens is not None:
        return None

    return round(total, 8) if contributed else None
