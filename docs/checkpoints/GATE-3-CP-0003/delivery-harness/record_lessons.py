#!/usr/bin/env python3
"""Record what GATE-3-CP-0003 learned: two new lessons with their guardrails, and one recurrence.

- `LSN-0055`, from `M1-F-001`: a contract a model must follow has to reach the model, rendered from
  the definition the parser enforces. Guarded by `GRD-0056`.
- `LSN-0056`, from `M1-F-002`: a result is accepted only from the executor that owns the request,
  decided when the request is created and never read from the result. Guarded by `GRD-0057`.
- `LSN-0054` recurs: commit `3101d31` reached the public remote with the lint gate red, because the
  pre-push check was narrower than the change's reach. The lesson is `CONFIRMED`, so the memory's
  own `register_recurrence` increments it; there is no guardrail to fail.

`M1-F-003` is not a new lesson: it is `LSN-0040`'s class, recorded as a `GUARDRAIL_FAILURE` and
resolved by `record_guardrail_failure.py` and `resolve_guardrail_failure.py`.

    python record_lessons.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "development-ledger"))

from ledger_common import utc_now, write_json  # noqa: E402
from lessons import (  # noqa: E402
    guardrail_registry_path,
    load_lessons,
    register_recurrence,
    save_lessons,
)

PROVENANCE = {
    "sourceType": "repository-generated",
    "provider": "local-analysis",
    "model": None,
    "ownership": "project-generated evidence",
    "license": "not-applicable",
    "notes": ("Derived from the M1 fresh-session audit's findings and this corrective delivery's "
              "recorded executions; no content outside this repository was used."),
}
NOT_FOR_TRAINING = {"trainingAllowed": False, "ragAllowed": False, "distillationAllowed": False,
                    "justification": None}

ENVELOPE_TESTS = (
    "test_the_runtime_instructions_show_the_exact_envelope_of_every_kind",
    "test_the_repair_restates_the_same_shape",
    "test_the_rendered_contract_follows_the_schema",
    "test_no_second_envelope_contract_is_written_by_hand",
    "test_arguments_outside_tool_arguments_are_refused_by_their_real_defect",
)
ORIGIN_TESTS = (
    "test_a_forged_result_cannot_displace_the_sandbox_result",
    "test_a_manual_result_for_a_sandbox_request_is_refused",
    "test_a_result_for_a_request_the_sandbox_owns_is_refused_and_never_signalled",
    "test_every_caller_declares_a_constant_origin",
    "test_existing_requests_are_backfilled_from_what_the_sandbox_executed",
)


def lesson_055(now: str) -> dict:
    return {
        "lessonId": "LSN-0055",
        "title": "A contract a model must follow has to reach the model, rendered from the "
                 "definition the parser enforces",
        "category": "model-behavior",
        "severity": "MEDIUM",
        "source": {"gate": "GATE-3", "checkpoint": "GATE-3-CP-0002", "finding": "M1-F-001"},
        "symptom": ("With the operator's configured model the developer stage never produced a "
                    "valid tool request: the arguments were written at the top level of the "
                    "envelope, then under 'args' after the one repair, and the run failed "
                    "INVALID_AGENT_OUTPUT. A second model made two valid requests, then failed "
                    "the same way."),
        "rootCauseSummary": ("The runtime described a tool request only as a tool that 'carries "
                             "its name and arguments' and never showed the keys. The schema that "
                             "named them reached a model only as a structured-output request, "
                             "made only for a model whose capability is known, and the "
                             "configured provider declares none; the docstring said the schema "
                             "documented the prompt, and nothing checked that it did. The parser "
                             "also dropped a stray key in the tool object, so an argument sent "
                             "under 'args' was lost silently and refused later by the sandbox."),
        "resolution": ("protocol.envelope_contract renders the version, every kind, one minimal "
                       "valid envelope per kind with tool.name and tool.arguments, and where the "
                       "arguments go, from envelope_schema() and the kind table the parser "
                       "enforces. The runtime instructions carry it on every turn and the repair "
                       "restates it verbatim with the stage's tools; the parser refuses a key "
                       "beside name and arguments by its own reason. A live coding run of the "
                       "configured model then made eleven valid tool requests, all executed in "
                       "the sandbox, with no repair."),
        "prevention": [
            {"kind": "test", "reference": ENVELOPE_TESTS[0],
             "description": "The instructions carry the contract rendered from the schema, "
                            "verbatim, with the stage's tools."},
            {"kind": "test", "reference": ENVELOPE_TESTS[1],
             "description": "The repair restates the same contract."},
            {"kind": "test", "reference": ENVELOPE_TESTS[2],
             "description": "A change of the canonical schema changes the rendered text."},
            {"kind": "test", "reference": ENVELOPE_TESTS[3],
             "description": "The instructions module spells no envelope key of its own."},
            {"kind": "test", "reference": ENVELOPE_TESTS[4],
             "description": "Arguments outside tool.arguments are refused by their real defect."},
        ],
        "guardrails": ["GRD-0056"],
        "evidence": [
            "file:services/agent-runtime/src/iacode_agent_runtime/protocol.py",
            "file:services/agent-runtime/src/iacode_agent_runtime/context.py",
            "file:services/agent-runtime/tests/test_protocol.py",
            "file:services/agent-runtime/tests/test_context.py",
            "file:docs/checkpoints/GATE-3-CP-0002/FINDINGS.json",
            "file:docs/checkpoints/GATE-3-CP-0003/LIVE-CODING-RUN.json",
        ],
        "applicability": {
            "gates": ["*"], "scopes": [], "technologies": [], "modules": [],
            "requiredCheck": ("For every structured answer a model must produce, confirm that the "
                              "exact shape is in the text every model receives — rendered from "
                              "the definition the parser enforces, not written beside it — and "
                              "that a live run of the configured model produces it."),
            "requiredEvidence": ("A test that the instructions contain the rendered shape and "
                                 "follow a change of the schema, and a live run of the "
                                 "configured model that produces the shape."),
        },
        "status": "GUARDED",
        "recurrenceKey": "model-behavior/model-asked-for-a-shape-it-is-never-shown",
        "recurrenceCount": 0,
        "guardrailFailures": [],
        "createdAt": now,
        "updatedAt": now,
        "provenance": PROVENANCE,
        "trainingEligibility": NOT_FOR_TRAINING,
        "notes": ("The residual limit is the model: the shape is shown and a malformed answer is "
                  "refused, but whether a given model follows the contract, and whether it "
                  "finishes a task within its budget, is measured by live runs, not guaranteed. "
                  "The configured model's run made valid requests and exhausted its turns "
                  "without finishing the task."),
    }


def lesson_056(now: str) -> dict:
    return {
        "lessonId": "LSN-0056",
        "title": "A result is accepted only from the executor that owns the request, decided "
                 "when the request is created",
        "category": "security",
        "severity": "MEDIUM",
        "source": {"gate": "GATE-3", "checkpoint": "GATE-3-CP-0002", "finding": "M1-F-002"},
        "symptom": ("In the deterministic timeout scenario, a SUCCEEDED result posted to the API "
                    "while the sandbox executed the command was answered 200; the stored result "
                    "was the forged one, the sandbox's own execution record still said "
                    "TIMED_OUT, and the agent answered TIMEOUT-NOT-SEEN."),
        "rootCauseSummary": ("resolve_tool_request accepted any PENDING request of the run "
                             "whatever its executor, and the workflow resumed the agent with the "
                             "stored result, answering the sandbox's later delivery with the "
                             "first one. Nothing recorded that a sandboxed stage's request is "
                             "answered by the sandbox, so every door looked the same."),
        "resolution": ("A tool request records its executor when it is created: SANDBOX for a "
                       "stage with a sandbox policy, EXTERNAL otherwise (migration 0005). The "
                       "store takes the origin of a result from the caller's code path — the "
                       "API's service passes EXTERNAL, the workflow's internal activity passes "
                       "SANDBOX — and refuses a mismatch with TOOL_RESULT_ORIGIN_REFUSED (403) "
                       "before anything is stored or signalled. The audit's null control and "
                       "mutation are a verification stage."),
        "prevention": [
            {"kind": "test", "reference": ORIGIN_TESTS[0],
             "description": "A forged result before and after the sandbox's own is refused and "
                            "the stored result is the sandbox's."},
            {"kind": "test", "reference": ORIGIN_TESTS[1],
             "description": "A manual result for a sandbox request is refused and nothing is "
                            "stored."},
            {"kind": "test", "reference": ORIGIN_TESTS[2],
             "description": "The API answers 403 TOOL_RESULT_ORIGIN_REFUSED and signals nothing."},
            {"kind": "test", "reference": ORIGIN_TESTS[3],
             "description": "Every caller passes a constant origin, never one read from a "
                            "payload; the scan fires on a mutated source."},
            {"kind": "test", "reference": ORIGIN_TESTS[4],
             "description": "Existing requests keep their meaning through the migration."},
            {"kind": "automated-check",
             "reference": "scripts/iacode/scenarios/sandbox_coding_e2e.py",
             "description": "The verification stage sandbox-tool-result-origin: the audit's null "
                            "control and mutation on the real stack."},
        ],
        "guardrails": ["GRD-0057"],
        "evidence": [
            "file:services/agent-runtime/src/iacode_agent_runtime/persistence.py",
            "file:services/orchestrator/src/iacode_orchestrator/agent_runtime/activities.py",
            "file:apps/api/migrations/versions/0005_tool_request_executor.py",
            "file:apps/api/tests/integration/test_agent_runtime_persistence.py",
            "file:docs/checkpoints/GATE-3-CP-0002/FORGED-RESULT-PROBE.json",
        ],
        "applicability": {
            "gates": ["*"], "scopes": [], "technologies": [], "modules": [],
            "requiredCheck": ("For every result, verdict or callback that more than one producer "
                              "could deliver, confirm that the owner is recorded when the work "
                              "is created, that the origin of a delivery comes from the code "
                              "path and never from the delivery, and that a delivery from any "
                              "other origin is refused before it is stored."),
            "requiredEvidence": ("A test that a delivery from the wrong origin is refused before "
                                 "and after the owner's, with a null control through the same "
                                 "path, and a run on the real stack."),
        },
        "status": "GUARDED",
        "recurrenceKey": "security/result-accepted-from-a-producer-that-does-not-own-it",
        "recurrenceCount": 0,
        "guardrailFailures": [],
        "createdAt": now,
        "updatedAt": now,
        "provenance": PROVENANCE,
        "trainingEligibility": NOT_FOR_TRAINING,
        "notes": ("The residual limit is the M1 trust model: the API is unauthenticated on the "
                  "loopback interface and Temporal is internal, so a local process that can "
                  "schedule the worker's activities directly could still act as the sandbox. "
                  "The control closes the public door, which is the one the audit found open."),
    }


GUARDRAILS = [
    {
        "guardrailId": "GRD-0056",
        "title": "The envelope contract every model receives is rendered from the schema the "
                 "parser enforces",
        "kind": "test",
        "reference": ENVELOPE_TESTS[0],
        "verifiedBy": list(ENVELOPE_TESTS),
        "lessons": ["LSN-0055"],
        "removingItWouldAllow": ("A model to be asked, again, for a shape it is never shown — or "
                                 "for one written by hand beside the schema that drifts from "
                                 "what the parser accepts."),
    },
    {
        "guardrailId": "GRD-0057",
        "title": "A tool result is accepted only from the executor that owns the request",
        "kind": "test",
        "reference": ORIGIN_TESTS[0],
        "verifiedBy": list(ORIGIN_TESTS),
        "lessons": ["LSN-0056"],
        "removingItWouldAllow": ("A result posted to the API to displace the sandbox's own, so "
                                 "an agent acts on a tool outcome that never happened."),
    },
]

RECURRENCE_054 = (
    "GATE-3-CP-0003: commit 3101d31 (M1-F-001) was pushed after its targeted tests and staged scan "
    "but before the lint gate, which was red on a 101-character comment line in protocol.py "
    "(cmd-0052); the next commit restored it (cmd-0053, 369f084).")


def main() -> int:
    now = utc_now()
    lessons = load_lessons(ROOT)
    identifiers = {item.get("lessonId") for item in lessons}
    if "LSN-0055" not in identifiers:
        lessons.append(lesson_055(now))
    if "LSN-0056" not in identifiers:
        lessons.append(lesson_056(now))
    index = next(i for i, item in enumerate(lessons) if item.get("lessonId") == "LSN-0054")
    if "3101d31" not in json.dumps(lessons[index]):
        before = lessons[index]
        lessons[index] = register_recurrence(before, CHECKPOINT.name, RECURRENCE_054)
        lessons[index]["notes"] = (
            (before.get("notes") or "").rstrip()
            + (" " if before.get("notes") else "")
            + "Recurred in GATE-3-CP-0003: " + RECURRENCE_054)
    save_lessons(ROOT, lessons)

    path = guardrail_registry_path(ROOT)
    registry = json.loads(path.read_text(encoding="utf-8"))
    present = {item["guardrailId"] for item in registry["guardrails"]}
    for entry in GUARDRAILS:
        if entry["guardrailId"] not in present:
            registry["guardrails"].append(entry)
    write_json(path, registry)
    print(f"lessons={len(lessons)} guardrails={len(registry['guardrails'])} "
          f"LSN-0054 recurrenceCount={lessons[index]['recurrenceCount']} "
          f"status={lessons[index]['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
