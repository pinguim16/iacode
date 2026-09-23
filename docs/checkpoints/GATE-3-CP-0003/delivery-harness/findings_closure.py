#!/usr/bin/env python3
"""Write M1-FINDINGS-CLOSURE.json and .md: the closure of the three findings of audit M1-CP-0002.

Every finding of the registered audit is accounted for, re-parsed from the sealed review report by
the registry's own parser, so a finding cannot be forgotten here without validation refusing the
checkpoint. For each one the file records what the audit expected and observed, the root cause,
what changed, the regression and negative tests, the command that verifies it and the evidence.

    python findings_closure.py --verification cmd-0070 --clean-clone cmd-0080 ...
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "development-ledger"))

from ledger_common import load_json, write_json  # noqa: E402
from policies import audit_findings, open_audits  # noqa: E402

AUDIT = "M1-CP-0002"


def closures(arguments: argparse.Namespace) -> dict[str, dict]:
    sealed = load_json(ROOT / "docs" / "checkpoints" / "GATE-3-CP-0002" / "FINDINGS.json")
    audit = {item["id"]: item for item in sealed["findings"]}
    return {
        "M1-F-003": {
            "originalExpected": audit["M1-F-003"]["requiredCorrection"],
            "originalObserved": audit["M1-F-003"]["observed"],
            "rootCause": audit["M1-F-003"]["rootCause"] + (
                " Measured over the whole ledger before any change, the same class held for two "
                "more sealed records: SETUP-00-CP-0009 cmd-0011 (13ab172fcc06) and GATE-2-CP-0001 "
                "cmd-0057 (643e721ee519), each a replaced closure commit named by a record of a "
                "dirty tree, so validation never read them."),
            "implementation": [
                "Three lightweight tags under refs/tags/iacode-preserved/, each naming exactly its "
                "commit (gate1-ledger-b59d66f9f3f9, setup00-ledger-13ab172fcc06, "
                "gate2-ledger-643e721ee519), pushed without force after a clean history scan; no "
                "existing reference moved (owner-authorised, DECISIONS.md D-01).",
                "scripts/development-ledger/ledger_common.py: one definition of the published "
                "history — PUBLISHED_REFERENCE_NAMESPACES, published_reachability (PUBLISHED, "
                "UNPUBLISHED_LOCAL_OBJECT, ABSENT_OBJECT) and published_clone, a --no-local "
                "transport clone; clone_with_worktree clones through it.",
                "scripts/development-ledger/validate_checkpoint.py: every commit a checkpoint's "
                "evidence names (a record's commit, subjectCommit and repositoryState.head; the "
                "state's and run metadata's commits) must be reachable from a published reference, "
                "for every schema version.",
                "test_every_sealed_checkpoint_validates_from_its_own_tag, MIR-016 and the Red Team "
                "fixture clone the published history; remote_sync.py requires every local "
                "checkpoint and preserved tag on the remote.",
                "ADR-0028; LSN-0040 records the GUARDRAIL_FAILURE of GRD-0042 and its resolution "
                "in GATE-3-CP-0003.",
            ],
            "regressionTest": [
                "tests/test_gate3_sandbox.py PublishedHistoryTests",
                "tests/test_gate3_sandbox.py PreservedReferenceTests",
                "tests/test_gate3_sandbox.py CloneMethodTests",
                "tests/test_gate1_model_gateway.py "
                "test_every_sealed_checkpoint_validates_from_its_own_tag",
                "tests/test_git_policy.py test_a_preserved_reference_missing_from_the_remote_fails"
                "_unnamed",
            ],
            "negativeTest": [
                "OLD-CODE-M1-F-003.json: the new tests run against the tooling of 0e60b96 fail (9 "
                "failures and errors) and pass against the corrected tooling (cmd-0029).",
                "VALIDATOR-BLIND-SPOT.json: with each preserved tag removed from a transport "
                "clone, the old validator accepts the sealed checkpoint and the corrected one "
                "refuses it as naming a local-only object; with the tag both accept (cmd-0031).",
                "PreservedReferenceTests: without each reference the checkpoint is refused in the "
                "repository that holds the object and, as absent, in a published clone of it.",
            ],
            "verificationCommand": (
                "python docs/checkpoints/GATE-3-CP-0003/delivery-harness/clean_clone.py --report "
                "docs/checkpoints/GATE-3-CP-0003/CLEAN-CLONE-REPORT.json"),
            "evidence": [
                "command:cmd-0015", "command:cmd-0016", "checkpoint:REMOTE-PUBLISHED-OBJECTS.json",
                "command:cmd-0029", "checkpoint:OLD-CODE-M1-F-003.json", "command:cmd-0031",
                "checkpoint:VALIDATOR-BLIND-SPOT.json", f"command:{arguments.clean_clone}",
                "checkpoint:CLEAN-CLONE-REPORT.json", f"command:{arguments.sealed_subjects}",
                "checkpoint:SEALED-SUBJECTS-PUBLISHED.json", f"command:{arguments.verification}"],
            "lesson": "LSN-0040",
            "guardrail": "GRD-0042",
        },
        "M1-F-001": {
            "originalExpected": audit["M1-F-001"]["requiredCorrection"],
            "originalObserved": audit["M1-F-001"]["observed"],
            "rootCause": audit["M1-F-001"]["rootCause"] + (
                " The parser also dropped a stray key in the tool object, so arguments sent "
                "under 'args' or 'parameters' were lost silently and refused later by the sandbox "
                "as missing."),
            "implementation": [
                "services/agent-runtime/src/iacode_agent_runtime/protocol.py: envelope_contract "
                "and envelope_examples render, from envelope_schema() and the kind table the "
                "parser enforces, the version, every kind, one minimal valid envelope per kind "
                "with tool.name and tool.arguments, and where the arguments go.",
                "context.runtime_instructions carries the contract on every turn, whether or not "
                "the gateway honours a structured-output request; repair_instruction restates it "
                "verbatim with the stage's tools (engine.py passes them).",
                "The parser refuses a key beside name and arguments in the tool object "
                "(tool-unknown-field) and says where the arguments go; a TOOL_REQUEST with "
                "arguments at the top level is refused with the same hint.",
                "ADR-0022 amendment; LSN-0055 guarded by GRD-0056.",
            ],
            "regressionTest": [
                "services/agent-runtime/tests/test_context.py "
                "test_the_runtime_instructions_show_the_exact_envelope_of_every_kind (A)",
                "services/agent-runtime/tests/test_protocol.py "
                "test_the_tool_request_example_carries_a_name_and_arguments (B)",
                "services/agent-runtime/tests/test_protocol.py "
                "test_the_repair_restates_the_same_shape (C)",
                "services/agent-runtime/tests/test_protocol.py "
                "test_the_rendered_contract_follows_the_schema and test_context.py "
                "test_the_instructions_follow_a_change_of_the_canonical_schema (D)",
                "services/agent-runtime/tests/test_context.py "
                "test_no_second_envelope_contract_is_written_by_hand (E)",
                "services/agent-runtime/tests/test_engine.py "
                "test_the_repair_carries_the_shape_with_the_stage_tools",
            ],
            "negativeTest": [
                "services/agent-runtime/tests/test_protocol.py "
                "test_arguments_outside_tool_arguments_are_refused_by_their_real_defect: the "
                "audit's top-level arguments and 'args', plus 'parameters' and a bare argument, "
                "each refused by its own reason; the correct shape accepted.",
                "The audit's live attempts with the same model before the correction "
                "(GATE-3-CP-0002 CROSS-GATE-LIVE-ATTEMPT-2.json, -3.json): no valid tool request.",
            ],
            "verificationCommand": (
                "python docs/checkpoints/GATE-3-CP-0003/delivery-harness/live_coding_run.py "
                "--report docs/checkpoints/GATE-3-CP-0003/LIVE-CODING-RUN.json"),
            "evidence": ["command:cmd-0035", "command:cmd-0041", "checkpoint:LIVE-CODING-RUN.json",
                         f"command:{arguments.verification}"],
            "lesson": "LSN-0055",
            "guardrail": "GRD-0056",
        },
        "M1-F-002": {
            "originalExpected": audit["M1-F-002"]["requiredCorrection"],
            "originalObserved": audit["M1-F-002"]["observed"],
            "rootCause": audit["M1-F-002"]["rootCause"],
            "implementation": [
                "packages/contracts: TOOL_REQUEST_EXECUTORS (EXTERNAL, SANDBOX), written once; "
                "tool_requests.executor with its constraint (migration 0005, backfilled from the "
                "executions the sandbox recorded).",
                "The workflow records the executor from the stage's sandbox policy when the "
                "request is created.",
                "SqlAgentRunStore.resolve_tool_request(run, result, *, origin): a result whose "
                "origin is not the request's executor is refused with "
                "ToolResultOriginRefusedError before the idempotent answer and the terminal "
                "check, so nothing is stored and nothing is signalled.",
                "The API's service passes origin EXTERNAL; the workflow's internal activity "
                "iacode_agent_runtime_resolve_tool_request passes SANDBOX; the submission "
                "contract cannot carry an origin. The API answers 403 "
                "TOOL_RESULT_ORIGIN_REFUSED with the executor in its safe details.",
                "The verification stage sandbox-tool-result-origin runs the audit's null control "
                "and mutation; LSN-0056 guarded by GRD-0057; Red Team attack G3-Y.",
            ],
            "regressionTest": [
                "apps/api/tests/integration/test_agent_runtime_persistence.py "
                "test_a_forged_result_cannot_displace_the_sandbox_result",
                "apps/api/tests/integration/test_agent_runtime_persistence.py "
                "test_a_manual_result_for_a_manual_request_is_accepted",
                "apps/api/tests/integration/test_agent_runtime_persistence.py "
                "test_a_duplicate_sandbox_result_is_idempotent",
                "apps/api/tests/unit/test_agent_runtime_api.py "
                "test_a_result_for_a_request_the_sandbox_owns_is_refused_and_never_signalled",
                "apps/api/tests/integration/test_migrations.py ToolRequestExecutorMigrationTests",
                "tests/test_gate3_sandbox.py ToolResultOriginTests",
            ],
            "negativeTest": [
                "test_a_manual_result_for_a_sandbox_request_is_refused",
                "test_a_forged_result_after_the_run_ended_is_refused",
                "test_a_sandbox_request_of_another_run_is_refused_as_another_run",
                "test_a_sandbox_result_for_a_manual_request_is_refused",
                "test_the_submission_cannot_claim_an_origin",
                "scripts/iacode/scenarios/sandbox_coding_e2e.py --scenario forged-result: control "
                "TIMEOUT-SEEN; forgery during execution 403; stored TIMED_OUT; agent "
                "TIMEOUT-SEEN; forgery after the run 403.",
            ],
            "verificationCommand": (
                "python scripts/iacode/scenarios/sandbox_coding_e2e.py --scenario forged-result "
                "--report var/sandbox-tool-result-origin.json"),
            "evidence": ["command:cmd-0038", "command:cmd-0039", "command:cmd-0055",
                         "checkpoint:TOOL-RESULT-ORIGIN.json", f"command:{arguments.red_team}",
                         f"command:{arguments.verification}"],
            "lesson": "LSN-0056",
            "guardrail": "GRD-0057",
        },
    }


def render(document: dict) -> str:
    lines = [f"# M1 Findings Closure — {document['checkpoint']}", "",
             f"Audit `{document['auditId']}` (`{document['source']}`): "
             f"**{document['closed']}/{document['total']} CLOSED** — result "
             f"`{document['result']}`.", ""]
    for item in document["findings"]:
        lines += [f"## {item['findingId']} — {item['severity']} — {item['title']}", "",
                  f"Status: `{item['status']}` · lesson `{item['lesson']}` · guardrail "
                  f"`{item['guardrail']}`", "",
                  "**What the audit required.** " + item["originalExpected"], "",
                  "**What the audit observed.** " + item["originalObserved"], "",
                  "**Root cause.** " + item["rootCause"], "", "**Implementation.**", ""]
        lines += [f"- {entry}" for entry in item["implementation"]]
        lines += ["", "**Regression tests.**", ""]
        lines += [f"- {entry}" for entry in item["regressionTest"]]
        lines += ["", "**Negative tests and the old behaviour.**", ""]
        lines += [f"- {entry}" for entry in item.get("negativeTest") or []]
        lines += ["", f"**Verification.** `{item['verificationCommand']}`", "",
                  "**Evidence.** " + ", ".join(f"`{entry}`" for entry in item["evidence"]), ""]
    while lines and not lines[-1]:
        lines.pop()
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    for name in ("--verification", "--clean-clone", "--sealed-subjects", "--red-team"):
        parser.add_argument(name, required=True)
    arguments = parser.parse_args()
    audit = next(item for item in open_audits(ROOT, "GATE-3", CHECKPOINT.name)
                 if item["auditId"] == AUDIT)
    parsed = audit_findings(ROOT, audit)
    written = closures(arguments)
    rows = []
    for finding in parsed:
        closure = written[finding["id"]]
        rows.append({"findingId": finding["id"], "severity": finding["severity"],
                     "title": finding["title"], **closure, "status": "CLOSED"})
    document = {"schemaVersion": "1.0.0", "checkpoint": CHECKPOINT.name, "auditId": AUDIT,
                "source": audit["reviewReport"], "findings": rows, "total": len(rows),
                "closed": sum(1 for row in rows if row["status"] == "CLOSED"),
                "result": "CLOSED" if all(row["status"] == "CLOSED" for row in rows) else "OPEN"}
    write_json(CHECKPOINT / "M1-FINDINGS-CLOSURE.json", document)
    (CHECKPOINT / "M1-FINDINGS-CLOSURE.md").write_text(render(document), encoding="utf-8",
                                                        newline="\n")
    print(f"M1_FINDINGS_CLOSURE={document['result']} {document['closed']}/{document['total']}")
    return 0 if document["result"] == "CLOSED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
