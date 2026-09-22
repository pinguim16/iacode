"""Estimating how much context a request needs, and saying that it is an estimate.

The gateway must not knowingly send a request larger than a model's context window. "Knowingly" is
the operative word: we have no tokenizer for models we did not train, and pretending otherwise would
be worse than having no check at all — a number presented as exact gets trusted, and a wrong exact
number is acted on.

So the estimate is a heuristic, it is labelled a heuristic in :class:`TokenEstimate`, and it is used
with a margin. Four characters per token is the well-known rule of thumb for English; it
underestimates for code and for scripts that are not Latin, which is why the safety margin is
applied on top rather than instead.

The check is deliberately one-sided. A model whose context window is unknown is **not** filtered
out: the catalog says we were told nothing, and inventing a limit in order to enforce it would
exclude every model a terse provider lists. The router's capability policy is where "unknown is not
good enough" is decided, and it decides it for capabilities, not for a number nobody stated.
"""

from __future__ import annotations

import json

from iacode_model_gateway.contracts import GatewayRequest, ModelDescriptor, TokenEstimate

__all__ = ["CHARACTERS_PER_TOKEN", "SAFETY_MARGIN", "estimate_request_tokens", "fits_context"]

#: The conventional rule of thumb. Stated as a constant so the assumption is visible and reviewable
#: rather than buried in an expression.
CHARACTERS_PER_TOKEN = 4.0

#: Every message costs a few tokens of framing beyond its text, in every protocol here.
TOKENS_PER_MESSAGE = 4

#: How much of the window the estimate is allowed to claim. The estimate is low for code and for
#: non-Latin scripts, and a preflight that only rejected requests already over the line would let
#: exactly the requests it exists to catch through.
SAFETY_MARGIN = 0.95


def estimate_request_tokens(request: GatewayRequest) -> TokenEstimate:
    """Estimate the input size of a request, labelled as an estimate."""
    characters = 0
    for message in request.messages:
        characters += len(message.content)
        for call in message.tool_calls:
            characters += len(call.name)
            characters += len(json.dumps(call.arguments, ensure_ascii=False))
    for tool in request.tools:
        characters += len(tool.name) + len(tool.description)
        characters += len(json.dumps(tool.parameters, ensure_ascii=False))
    if request.response_format is not None:
        characters += len(json.dumps(request.response_format.json_schema, ensure_ascii=False))

    tokens = int(characters / CHARACTERS_PER_TOKEN) + TOKENS_PER_MESSAGE * len(request.messages)
    return TokenEstimate(
        tokens=tokens, exact=False,
        method=f"heuristic: {CHARACTERS_PER_TOKEN:g} characters per token plus "
               f"{TOKENS_PER_MESSAGE} per message")


def fits_context(estimate: TokenEstimate, model: ModelDescriptor,
                 output_tokens: int) -> tuple[bool, str]:
    """Whether the request plus its output cap plausibly fits, and why not when it does not.

    A model with no declared window passes: the catalog recorded that the provider said nothing, and
    a filter that treated silence as a small window would exclude most of a terse provider's models.
    """
    if model.context_window is None:
        return True, "the model declares no context window, so no preflight is possible"
    needed = estimate.tokens + output_tokens
    budget = int(model.context_window * SAFETY_MARGIN)
    if needed <= budget:
        return True, ""
    return False, (
        f"an estimated {estimate.tokens} input tokens plus {output_tokens} output tokens exceed "
        f"the usable part of a {model.context_window} token window")
