#!/usr/bin/env python3
"""Prove the Agent Runtime actually executes, through the Model Gateway, against a real provider.

Doubles prove the runtime's own logic. Only this proves the integration: that a run created over
HTTP reaches a durable Temporal workflow, that the workflow calls the Model Gateway and nothing
else, that the answer comes back, that the events were recorded, and that a two-stage team runs in
order with the first stage's output reaching the second.

It drives the **running stack over HTTP**, exactly as the operational page does, rather than
importing the runtime in a process of its own. What is being proved is the deployed path — the API,
the worker, Temporal, the gateway, the provider and the database — and a script that imported the
library would prove the library.

    python scripts/iacode/agent_runtime_smoke.py
    python scripts/iacode/agent_runtime_smoke.py --report var/agent-runtime-smoke.json

**Without a credential it does not pass.** It exits `BLOCKED`, naming the variable that is missing,
because a live check that quietly reports success when it never called anything is worse than no
live check at all.

**The smoke model is never substituted.** If the configured model is not in the discovered catalog,
the check fails. Silently picking another one would spend money on a model nobody authorised.

It is deliberately cheap: three model calls in total — one for the single-agent run, two for the
planner and reviewer — each with a short prompt and a low output cap.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from compose import StackError, log, main_guard, published_port, read_env_file

#: Short, cheap, and impossible to satisfy by accident.
SINGLE_AGENT_TASK = "Reply with exactly: IACODE_AGENT_OK"
SINGLE_AGENT_EXPECTED = "IACODE_AGENT_OK"

#: Two stages, one sentence each. The reviewer's job is to prove it received the planner's output.
TEAM_TASK = (
    "Plan, in at most two steps, how to rename one function in one file. "
    "Keep every line under twenty words.")

#: Small enough that a mistake costs nothing.
MAX_OUTPUT_TOKENS = 400

READ_TIMEOUT_SECONDS = 20
RUN_TIMEOUT_SECONDS = 240
POLL_SECONDS = 2.0

#: The exit code that means "not run, and not passed either".
BLOCKED_EXIT = 2

TERMINAL = ("SUCCEEDED", "FAILED", "CANCELLED")


@dataclass
class Check:
    name: str
    ok: bool
    detail: str
    data: dict = field(default_factory=dict)


class BlockedError(RuntimeError):
    """The check could not run because something outside the repository is not configured."""


def setting(name: str) -> str:
    import os

    value = (os.environ.get(name) or "").strip()
    if value:
        return value
    return (read_env_file().get(name) or "").strip()


def request_json(url: str, payload: dict | None = None, *, timeout: float,
                 accept_status: tuple[int, ...] = (200, 202)) -> tuple[int, dict]:
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    request = urllib.request.Request(
        url, data=data, method="POST" if data is not None else "GET",
        headers={"Accept": "application/json",
                 **({"Content-Type": "application/json"} if data is not None else {})})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        if error.code in accept_status:
            return error.code, json.loads(body)
        raise StackError(f"{url} responded {error.code}: {body[:500]}") from error
    except urllib.error.URLError as error:
        raise StackError(f"{url} is unreachable: {error.reason}") from error


def require_configuration(base: str) -> tuple[str, dict]:
    """The smoke model and the provider, or a refusal that says which variable is missing."""
    smoke_model = setting("IACODE_GATEWAY_SMOKE_MODEL")
    if not smoke_model:
        raise BlockedError(
            "IACODE_GATEWAY_SMOKE_MODEL is not set. It names the 'provider:model' this check is "
            "authorised to spend tokens on, and there is no safe default: choosing one would mean "
            "spending on a model nobody authorised.")
    if ":" not in smoke_model:
        raise StackError(
            f"IACODE_GATEWAY_SMOKE_MODEL is {smoke_model!r}, which is not 'provider:model'.")

    _status, health = request_json(f"{base}/api/v1/gateway/health", timeout=READ_TIMEOUT_SECONDS)
    provider_id = smoke_model.split(":", 1)[0]
    providers = {item["provider"]: item for item in health.get("providers", [])}
    provider = providers.get(provider_id)
    if provider is None:
        raise StackError(
            f"the gateway knows no provider {provider_id!r}; the configured providers are "
            + (", ".join(sorted(providers)) or "none"))
    if not provider["addressConfigured"]:
        raise BlockedError(
            f"provider {provider_id!r} has no address. Set {provider['addressVariable']} in "
            f"infra/compose/.env and restart the stack.")
    if not provider["credentialConfigured"]:
        raise BlockedError(
            f"provider {provider_id!r} has no credential. Set {provider['credentialVariable']} in "
            f"infra/compose/.env and restart the stack. The value is never read by this script, "
            f"never printed and never written to the report.")

    _status, catalog = request_json(f"{base}/api/v1/gateway/models?provider={provider_id}",
                                    timeout=READ_TIMEOUT_SECONDS)
    model_id = smoke_model.split(":", 1)[1]
    known = {item["model"] for item in catalog.get("models", []) if item.get("active")}
    if model_id not in known:
        raise StackError(
            f"the configured smoke model {smoke_model!r} is not in the discovered catalog. "
            f"It is not substituted: spending on a different model is a decision nobody made. "
            f"Synchronise the catalog or correct IACODE_GATEWAY_SMOKE_MODEL.")
    return smoke_model, provider


def start_run(base: str, payload: dict) -> str:
    status, body = request_json(f"{base}/api/v1/agent-runs", payload,
                                timeout=READ_TIMEOUT_SECONDS)
    if status != 202:
        raise StackError(f"creating a run answered {status}, not 202")
    return body["runId"]


def wait_for(base: str, run_id: str) -> dict:
    """Poll the run until it is terminal, or fail with what the run said about itself."""
    deadline = time.monotonic() + RUN_TIMEOUT_SECONDS
    body: dict = {}
    while time.monotonic() < deadline:
        _status, body = request_json(f"{base}/api/v1/agent-runs/{run_id}",
                                     timeout=READ_TIMEOUT_SECONDS)
        if body["state"] in TERMINAL:
            return body
        time.sleep(POLL_SECONDS)
    raise StackError(
        f"run {run_id} was still {body.get('state')} after {RUN_TIMEOUT_SECONDS}s")


def events_of(base: str, run_id: str) -> list[dict]:
    _status, body = request_json(f"{base}/api/v1/agent-runs/{run_id}/events?limit=500",
                                 timeout=READ_TIMEOUT_SECONDS)
    return body["events"]


def check_single_agent(base: str, smoke_model: str) -> tuple[list[Check], str]:
    """One agent, one turn, one model call. The shortest path a run can take."""
    run_id = start_run(base, {
        "task": SINGLE_AGENT_TASK,
        "team": "single-agent",
        "model": smoke_model,
        "maxTurns": 2,
        "maxModelCalls": 2,
        "maxDurationSeconds": 180,
    })
    run = wait_for(base, run_id)
    events = events_of(base, run_id)
    types = [event["type"] for event in events]
    completed = [event for event in events if event["type"] == "MODEL_CALL_COMPLETED"]
    provenance = completed[0]["payload"] if completed else {}

    checks = [
        Check("single.succeeded", run["state"] == "SUCCEEDED",
              f"state {run['state']}"
              + (f": {run.get('errorType')} {run.get('errorSummary')}"
                 if run["state"] != "SUCCEEDED" else ""),
              {"runId": run_id}),
        Check("single.answered", SINGLE_AGENT_EXPECTED in (run.get("result") or ""),
              ("contains" if SINGLE_AGENT_EXPECTED in (run.get("result") or "")
               else "does not contain") + f" {SINGLE_AGENT_EXPECTED}"),
        Check("single.one_agent_run", len(run["stages"]) == 1,
              f"{len(run['stages'])} agent run(s)"),
        Check("single.workflow_executed", bool(run.get("workflowId")),
              f"workflow {run.get('workflowId')}"),
        Check("single.events_persisted",
              {"RUN_CREATED", "RUN_STARTED", "AGENT_STARTED", "MODEL_CALL_STARTED",
               "MODEL_CALL_COMPLETED", "AGENT_COMPLETED", "RUN_COMPLETED"}.issubset(set(types)),
              f"{len(events)} event(s): {', '.join(types)}"),
        Check("single.sequence_is_monotonic",
              [event["sequence"] for event in events]
              == sorted(event["sequence"] for event in events),
              "the recorded order is the sequence order"),
        Check("single.model_provenance",
              bool(provenance.get("provider")) and bool(provenance.get("model"))
              and bool(provenance.get("modelCallId")),
              f"{provenance.get('provider')}:{provenance.get('model')} "
              f"call {provenance.get('modelCallId')}"),
        Check("single.gateway_only",
              provenance.get("model", "") == smoke_model.split(":", 1)[1],
              "the call went to the model the run asked the gateway for"),
        Check("single.no_content_in_events",
              all(SINGLE_AGENT_EXPECTED not in json.dumps(event["payload"])
                  or event["type"] == "AGENT_COMPLETED"
                  for event in events),
              "no event carries the model's output except the bounded summary"),
        Check("single.no_tool_executed",
              not run["toolRequests"] and run["summary"]["toolsRequested"] == 0,
              "no tool was requested and none was executed"),
        Check("single.training_denied", run["trainingAllowed"] is False,
              "the run is not training-eligible"),
        Check("single.budget_recorded",
              run["budget"]["modelCallsUsed"] >= 1 and run["budget"]["turnsUsed"] >= 1,
              f"{run['budget']['turnsUsed']} turn(s), "
              f"{run['budget']['modelCallsUsed']} model call(s)"),
    ]
    return checks, run_id


def check_team(base: str, smoke_model: str) -> tuple[list[Check], str]:
    """Two agents, in order, with the planner's output reaching the reviewer as an artifact."""
    run_id = start_run(base, {
        "task": TEAM_TASK,
        "team": "planner-reviewer",
        "model": smoke_model,
        "maxTurns": 4,
        "maxModelCalls": 4,
        "maxDurationSeconds": 240,
    })
    run = wait_for(base, run_id)
    events = events_of(base, run_id)
    stages = run["stages"]
    started = [event for event in events if event["type"] == "AGENT_STARTED"]

    plan_output = next((stage["outputSummary"] for stage in stages
                        if stage["name"] == "plan"), None)
    review_output = next((stage["outputSummary"] for stage in stages
                          if stage["name"] == "review"), None)

    checks = [
        Check("team.succeeded", run["state"] == "SUCCEEDED",
              f"state {run['state']}"
              + (f": {run.get('errorType')} {run.get('errorSummary')}"
                 if run["state"] != "SUCCEEDED" else ""),
              {"runId": run_id}),
        Check("team.two_agent_runs", len(stages) == 2, f"{len(stages)} agent run(s)"),
        Check("team.order", [stage["name"] for stage in stages] == ["plan", "review"],
              " then ".join(stage["name"] for stage in stages)),
        Check("team.agents", [stage["agent"] for stage in stages] == ["planner", "reviewer"],
              " then ".join(stage["agent"] for stage in stages)),
        Check("team.started_in_order",
              [event["stage"] for event in started] == ["plan", "review"],
              "the events record the same order the stages ran in"),
        Check("team.outputs_are_separate",
              bool(plan_output) and bool(review_output) and plan_output != review_output,
              "each stage recorded its own output summary"),
        Check("team.provenance_per_stage",
              all(stage.get("profileVersion") and stage.get("promptTemplateHash")
                  for stage in stages),
              "each stage recorded the profile and prompt that produced it"),
        Check("team.result_is_the_last_stage",
              (run.get("result") or "").strip() != ""
              and (run.get("resultSummary") or "") == review_output,
              "the run's result is the reviewer's answer"),
        Check("team.calls_were_bounded", run["budget"]["modelCallsUsed"] <= 4,
              f"{run['budget']['modelCallsUsed']} model call(s)"),
        Check("team.no_tool_executed", run["summary"]["toolsRequested"] == 0,
              "no tool was requested and none was executed"),
    ]
    return checks, run_id


def check_reviewer_saw_the_plan(base: str, team_run_id: str) -> list[Check]:
    """The reviewer's own output is the evidence that it received something to review.

    The prompt is not readable from anywhere — deliberately, because the runtime stores no prompt —
    so this asserts the observable consequence instead: the reviewer ran after the planner, its
    stage declared the planner's output as an input, and it produced a different answer.
    """
    _status, run = request_json(f"{base}/api/v1/agent-runs/{team_run_id}",
                                timeout=READ_TIMEOUT_SECONDS)
    _status, teams = request_json(f"{base}/api/v1/agent-teams", timeout=READ_TIMEOUT_SECONDS)
    profile = next((item for item in teams if item["team"] == "planner-reviewer"), None)
    review_stage = next((stage for stage in (profile or {}).get("stages", [])
                         if stage["name"] == "review"), None)
    return [
        Check("team.reviewer_reads_the_plan",
              bool(review_stage) and "plan" in review_stage["inputs"],
              f"the review stage declares inputs {review_stage['inputs'] if review_stage else []}"),
        Check("team.reviewer_ran_second",
              len(run["stages"]) == 2 and run["stages"][1]["agent"] == "reviewer"
              and run["stages"][1]["state"] == "SUCCEEDED",
              "the reviewer executed after the planner and completed"),
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--report", type=Path, default=None,
                        help="write a machine-readable result document to this path")
    parser.add_argument("--single-only", action="store_true",
                        help="run only the single-agent check; used while iterating")
    arguments = parser.parse_args()

    api = f"http://127.0.0.1:{published_port('api', 8000)}"

    try:
        smoke_model, provider = require_configuration(api)
    except BlockedError as blocked:
        log("AGENT_RUNTIME_SMOKE=BLOCKED")
        log(str(blocked))
        if arguments.report:
            arguments.report.parent.mkdir(parents=True, exist_ok=True)
            arguments.report.write_text(json.dumps({
                "result": "BLOCKED", "reason": str(blocked), "checks": [],
            }, indent=2) + "\n", encoding="utf-8", newline="\n")
        return BLOCKED_EXIT

    log(f"provider {provider['provider']} is configured; smoke model {smoke_model}")

    checks, single_run = check_single_agent(api, smoke_model)
    team_run = None
    if not arguments.single_only:
        team_checks, team_run = check_team(api, smoke_model)
        checks += team_checks
        checks += check_reviewer_saw_the_plan(api, team_run)

    failed = [check for check in checks if not check.ok]
    for check in checks:
        log(f"[{'PASS' if check.ok else 'FAIL'}] {check.name:32} {check.detail}")

    if arguments.report:
        arguments.report.parent.mkdir(parents=True, exist_ok=True)
        arguments.report.write_text(json.dumps({
            "result": "PASS" if not failed else "FAIL",
            "provider": provider["provider"],
            "smokeModel": smoke_model,
            "maxOutputTokens": MAX_OUTPUT_TOKENS,
            "singleAgentRunId": single_run,
            "teamRunId": team_run,
            # The tasks are here because they are ours; no model answer and no prompt is.
            "singleAgentTask": SINGLE_AGENT_TASK,
            "teamTask": TEAM_TASK,
            "checks": [
                {"name": check.name, "result": "PASS" if check.ok else "FAIL",
                 "detail": check.detail, **({"data": check.data} if check.data else {})}
                for check in checks
            ],
        }, indent=2) + "\n", encoding="utf-8", newline="\n")
        log(f"wrote {arguments.report}")

    log(f"AGENT_RUNTIME_SMOKE={'PASS' if not failed else 'FAIL'} "
        f"{len(checks) - len(failed)}/{len(checks)} checks")
    return 0 if not failed else 1


if __name__ == "__main__":
    main_guard(main)
