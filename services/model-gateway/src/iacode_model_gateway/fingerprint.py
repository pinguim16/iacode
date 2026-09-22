"""A stable fingerprint of a request, for correlating calls without storing what they said.

The problem it solves is ordinary: two identical requests a minute apart, one slow and one fast, and
an operator who needs to know they were the same request. Storing the prompt would answer that and
would also put the prompt in the database, which `docs/GATE-1-CHECKLIST.md` row 10.4 forbids by
default. A digest answers the narrower question and carries none of the text.

**A hash is not anonymization, and this module does not pretend otherwise.** Anyone holding a
candidate prompt can hash it and compare, so a fingerprint confirms a guess even though it reveals
nothing on its own. That is acceptable for operational correlation and is not a privacy control; the
runbook says so in the same words, because a property people believe a hash has is more dangerous
than one it visibly lacks.

The digest covers the parts of a request that decide what the model was asked, and excludes the
parts that decide how the answer is delivered: two calls that differ only in ``stream`` are the same
question, and an operator comparing them wants to see that.
"""

from __future__ import annotations

import hashlib
import json

from iacode_model_gateway.contracts import GatewayRequest

__all__ = ["request_fingerprint"]


def request_fingerprint(request: GatewayRequest) -> str:
    """A hex digest of what was asked, stable across processes and across runs.

    ``sort_keys`` and a fixed separator set make the serialisation canonical: without them the
    digest would depend on dictionary insertion order, and the same request would fingerprint
    differently in two processes.
    """
    material = {
        "messages": [
            {
                "role": str(message.role),
                "content": message.content,
                "name": message.name,
                "toolCallId": message.tool_call_id,
                "toolCalls": [
                    {"name": call.name, "arguments": call.arguments}
                    for call in message.tool_calls
                ],
            }
            for message in request.messages
        ],
        "tools": [
            {"name": tool.name, "description": tool.description, "parameters": tool.parameters}
            for tool in request.tools
        ],
        "responseFormat": (request.response_format.model_dump(mode="json")
                           if request.response_format else None),
        "temperature": request.temperature,
        "topP": request.top_p,
        "reasoningEffort": str(request.reasoning_effort) if request.reasoning_effort else None,
        "maxOutputTokens": request.max_output_tokens,
    }
    canonical = json.dumps(material, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
