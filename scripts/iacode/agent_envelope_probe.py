#!/usr/bin/env python3
"""Show the shape of one planner envelope, as the deployed runtime would parse it.

A diagnostic, not a check. It exists because a live planner-reviewer run can fail
`INVALID_AGENT_OUTPUT` for a reason that no recorded artifact shows: the runtime stores no model
output, by design, so the envelope that was refused is gone by the time anybody looks. This makes
exactly one call through the Model Gateway, with the context the runtime itself assembles for the
planner stage of the live smoke, and reports the **shape** of the answer — its field names and the
JSON type of each value — and the parser's verdict. It never prints the answer's text.

It runs inside the worker container, because that is where the runtime and its dependencies are,
and it reuses the smoke's task, output cap and configured model so it describes the same call the
smoke makes:

    python scripts/iacode/agent_envelope_probe.py

Exit codes: `0` the probe ran (whatever the verdict), `1` it could not run, `2` BLOCKED because the
smoke model is not configured.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from agent_runtime_smoke import BLOCKED_EXIT, MAX_OUTPUT_TOKENS, TEAM_TASK, setting
from compose import StackError, compose, log, main_guard

#: Runs inside the worker. Kept as one program passed with ``-c`` so nothing is copied into a
#: container and the command that ran is the command the ledger records.
IN_CONTAINER = r'''
import json, sys, urllib.request
from pathlib import Path
from iacode_agent_runtime.context import assemble
from iacode_agent_runtime.errors import InvalidAgentOutputError
from iacode_agent_runtime.prompts import load_template
from iacode_agent_runtime.protocol import parse_envelope

root, base, model, task, limit = sys.argv[1:6]
profile = json.loads((Path(root) / "agents/profiles/planner.json").read_text(encoding="utf-8"))
role = load_template(Path(root), profile["promptTemplate"]).render(
    role=profile["role"], description=profile["description"])
context = assemble(role_instructions=role, task=task)
body = {"model": model, "maxOutputTokens": int(limit), "messages": [
    {"role": "system", "content": context.instruction_text},
    {"role": "user", "content": context.data_text}]}
request = urllib.request.Request(
    base + "/api/v1/gateway/infer", data=json.dumps(body).encode("utf-8"),
    headers={"Content-Type": "application/json"}, method="POST")
with urllib.request.urlopen(request, timeout=120) as response:
    answer = json.loads(response.read().decode("utf-8"))

def kind_of(value):
    if isinstance(value, bool): return "boolean"
    if isinstance(value, (int, float)): return "number"
    if isinstance(value, list): return "array[%d]" % len(value)
    if isinstance(value, dict): return "object[%d]" % len(value)
    if value is None: return "null"
    return "string[%d]" % len(value)

text = answer.get("content") or ""
report = {"servedBy": "%s:%s" % (answer.get("provider"), answer.get("model")),
          "endpoint": answer.get("endpoint"), "finishReason": answer.get("finishReason")}
try:
    decoded = json.loads(text.strip().removeprefix("```json").removesuffix("```").strip())
    report["shape"] = ({key: kind_of(value) for key, value in decoded.items()}
                       if isinstance(decoded, dict) else kind_of(decoded))
except json.JSONDecodeError as error:
    report["shape"] = "not-json: " + error.msg
try:
    parse_envelope(text)
    report["verdict"] = "ACCEPTED"
except InvalidAgentOutputError as error:
    report["verdict"] = "REFUSED"
    report["reason"] = error.details.get("reason")
    report["refusal"] = str(error)
print(json.dumps(report, sort_keys=True))
'''


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, help="write the shape report here as JSON")
    arguments = parser.parse_args()

    model = setting("IACODE_GATEWAY_SMOKE_MODEL")
    if not model:
        log("AGENT_ENVELOPE_PROBE=BLOCKED")
        log("IACODE_GATEWAY_SMOKE_MODEL is not set; the probe spends only on the smoke's model")
        return BLOCKED_EXIT

    result = compose("exec", "-T", "worker", "python", "-c", IN_CONTAINER,
                     "/app", "http://api:8000", model, TEAM_TASK, str(MAX_OUTPUT_TOKENS),
                     merge_stderr=False, timeout=180)
    if not result.ok:
        raise StackError(f"the probe did not run in the worker: {result.stdout.strip()[-500:]}")
    report = json.loads(result.stdout.strip().splitlines()[-1])
    for key in ("servedBy", "endpoint", "finishReason", "shape", "verdict", "reason", "refusal"):
        if key in report:
            log(f"{key}: {report[key]}")
    if arguments.report:
        arguments.report.parent.mkdir(parents=True, exist_ok=True)
        arguments.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8",
                                    newline="\n")
        log(f"wrote {arguments.report}")
    log(f"AGENT_ENVELOPE_PROBE={report['verdict']}")
    return 0


if __name__ == "__main__":
    main_guard(main)
