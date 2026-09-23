#!/usr/bin/env python3
"""Build FINAL-M1-AUDIT-MATRIX from the frozen criteria and the artifacts this audit produced.

The rows are the twenty criteria frozen in PLAN.md before execution. Every verdict is computed from
an artifact the audit wrote by executing something — never typed — and a row whose artifact is
missing is UNVERIFIED, which fails the matrix.

    python build_matrix.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "development-ledger"))

from ledger_common import utc_now, write_json  # noqa: E402


def load(name: str) -> dict:
    path = CHECKPOINT / name
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}


def main() -> int:
    sealed = load("SEALED-SUBJECTS.json")
    published = load("SEALED-SUBJECTS-PUBLISHED.json")
    verification = load("VERIFICATION-REPORT.json")
    clone = load("CLEAN-CLONE-REPORT.json")
    live = load("CROSS-GATE-LIVE.json")
    red = load("M1-INTERNAL-RED-TEAM.json")
    review = load("R-G3-001-REVIEW.json")
    findings = load("FINDINGS.json") if (CHECKPOINT / "FINDINGS.json").is_file() else None
    executions = {item["id"]: item for item in load("AUDIT-EXECUTIONS.json").get("executions", [])}

    stages = {item["name"]: item for item in verification.get("stages") or []}
    attacks = {item["attackId"]: item for item in red.get("attacks") or []}

    def stages_ok(*names: str) -> tuple[bool | None, str]:
        if not stages:
            return None, "no verification report"
        seen = {name: (stages.get(name) or {}).get("result") for name in names}
        return all(value == "PASS" for value in seen.values()), ", ".join(
            f"{name}={value}" for name, value in seen.items())

    def attack(identifier: str) -> tuple[bool | None, str]:
        item = attacks.get(identifier)
        if item is None:
            return None, f"{identifier} not executed"
        control = (red.get("baselineControl") or {}).get("result")
        return (item["result"] == "DEFENDED" and control == "VALID",
                f"{identifier} {item['result']} (control {control}): {item['observed'][:200]}")

    subjects = sealed.get("subjects") or []
    final = [item for item in subjects if item.get("finalOfGate")]
    remote_subjects = published.get("subjects") or []
    remote_failed = [item["checkpoint"] for item in remote_subjects if not item["ok"]]
    live_checks = {item["name"]: item for item in live.get("checks") or []}
    clone_steps = clone.get("steps") or []
    controls = review.get("controls") or []

    rows = []

    def row(identifier: str, dimension: str, expectation: str, outcome: tuple[bool | None, str],
            evidence: list[str]) -> None:
        ok, observed = outcome
        rows.append({
            "id": identifier, "dimension": dimension, "expectation": expectation,
            "mandatory": True,
            "status": "COMPLETE" if ok is not None else "UNVERIFIED",
            "observed": observed, "evidence": evidence,
            "verdict": "PASS" if ok else ("FAIL" if ok is False else "UNVERIFIED"),
        })

    row("AM-01", "Four Gates sealed and valid",
        "Every sealed M1 checkpoint validates detached at its own canonical tag, from this "
        "repository and from a clone of the published remote.",
        ((bool(subjects) and all(item["ok"] for item in subjects) and len(final) == 4
          and bool(remote_subjects) and not remote_failed) if subjects else None,
         f"this repository: {sum(item['ok'] for item in subjects)}/{len(subjects)}; published "
         f"remote: {len(remote_subjects) - len(remote_failed)}/{len(remote_subjects)}"
         + (f", invalid there: {remote_failed}" if remote_failed else "")),
        ["checkpoint:SEALED-SUBJECTS.json", "checkpoint:SEALED-SUBJECTS-PUBLISHED.json"])
    row("AM-02", "Integrity and tags",
        "The anchored chain verifies and a moved tag or a rewritten commit is refused.",
        ((bool(subjects) and all(item["checks"]["anchoredAtTheTagCommit"] for item in subjects)
          and attack("M1-M")[0] is True),
         f"{sealed.get('anchors')} anchors; every M1 tag at its anchored commit; "
         + attack("M1-M")[1]),
        ["checkpoint:SEALED-SUBJECTS.json", "checkpoint:M1-INTERNAL-RED-TEAM.json",
         "command:cmd-0003"])
    row("AM-03", "Remote synchronised",
        "origin/main and every subject tag are on the authorised remote; drift is detected.",
        (attack("M1-N")[0] is True and "EX-003" in executions
         and executions["EX-003"]["exitCode"] == 0,
         (executions.get("EX-003") or {}).get("observed", "not executed") + "; "
         + attack("M1-N")[1]),
        ["command:cmd-0007", "checkpoint:M1-INTERNAL-RED-TEAM.json"])
    row("AM-04", "Full verification",
        "Every stage of the full verification passes in this session.",
        ((verification.get("result") == "PASS" and not verification.get("fast"))
         if verification else None,
         f"{verification.get('result')} {sum(1 for s in stages.values() if s.get('result') == 'PASS')}"
         f"/{len(stages)} stages, fast={verification.get('fast')}"),
        ["checkpoint:VERIFICATION-REPORT.json"])
    row("AM-05", "Clean clone",
        "A fresh clone of the remote validates, verifies its integrity and passes the full "
        "verification.",
        ((clone.get("result") == "PASS" and len(clone_steps) >= 4) if clone else None,
         "; ".join(f"{item['step']} exit {item['exitCode']}" for item in clone_steps)
         or "not executed"),
        ["checkpoint:CLEAN-CLONE-REPORT.json"])
    row("AM-06", "Foundation operational",
        "The stack, its integration suite, infrastructure, smoke, backup, restart and fresh "
        "installation pass.",
        stages_ok("stack", "integration", "infra", "smoke", "backup", "restart",
                  "dependency-failure", "fresh-install", "gate:apiTests", "gate:webTests"),
        ["checkpoint:VERIFICATION-REPORT.json"])
    row("AM-07", "Gateway functional",
        "The gateway suite and the live gateway smoke pass.",
        stages_ok("gate:gatewayTests", "gateway-smoke"), ["checkpoint:VERIFICATION-REPORT.json"])
    row("AM-08", "Agent Runtime functional",
        "The runtime suite, the live runtime smoke, durability, cancellation and deadline pass.",
        stages_ok("gate:agentRuntimeTests", "agent-runtime-smoke", "agent-durability",
                  "agent-cancellation", "agent-deadline"),
        ["checkpoint:VERIFICATION-REPORT.json"])
    row("AM-09", "Sandbox functional",
        "The sandbox suite, its integration and its four scenarios pass.",
        stages_ok("gate:sandboxTests", "sandbox-integration", "sandbox-coding", "sandbox-timeout",
                  "sandbox-cancellation", "sandbox-recovery"),
        ["checkpoint:VERIFICATION-REPORT.json"])
    crossing = ["model calls through the gateway", "tool requests executed in a sandbox",
                "tool results delivered to the runtime",
                "the runtime called the model again after a sandbox result"]
    row("AM-10", "Cross-gate flow",
        "Task → Agent Runtime → Model Gateway → ToolRequest → Sandbox → ToolResult → Agent Runtime "
        "in one live run.",
        ((live.get("result") == "PASS" and all((live_checks.get(name) or {}).get("ok")
                                               for name in crossing)) if live else None,
         "; ".join(f"{name}: {(live_checks.get(name) or {}).get('detail')}" for name in crossing)
         if live else "not executed"),
        ["checkpoint:CROSS-GATE-LIVE.json"])
    host_ok = (live_checks.get("host sentinel untouched") or {}).get("ok")
    a_ok, a_seen = attack("M1-A")
    row("AM-11", "No tool runs on the host",
        "The live run leaves the host sentinel untouched and a command reports the sandbox as its "
        "host.",
        ((bool(host_ok) and a_ok) if (live and a_ok is not None) else None,
         f"host sentinel untouched={host_ok}; {a_seen}"),
        ["checkpoint:CROSS-GATE-LIVE.json", "checkpoint:M1-INTERNAL-RED-TEAM.json"])
    row("AM-12", "Host secrets absent from the sandbox", "Attack M1-B is defended.",
        attack("M1-B"), ["checkpoint:M1-INTERNAL-RED-TEAM.json"])
    row("AM-13", "Workspace isolation", "Attack M1-E is defended.",
        attack("M1-E"), ["checkpoint:M1-INTERNAL-RED-TEAM.json"])
    row("AM-14", "Path traversal and link escapes defended", "Attack M1-D is defended.",
        attack("M1-D"), ["checkpoint:M1-INTERNAL-RED-TEAM.json"])
    c_ok, c_seen = attack("M1-C")
    c2 = next((item for item in controls if item["id"] == "C2"), {})
    row("AM-15", "Engine socket absent from an executed sandbox",
        "Attack M1-C is defended and the builder cannot hand a sandbox a host resource.",
        ((c_ok and c2.get("result") == "PASS") if c_ok is not None and c2 else None,
         f"{c_seen}; R-G3-001 C2 {c2.get('result')}"),
        ["checkpoint:M1-INTERNAL-RED-TEAM.json", "checkpoint:R-G3-001-REVIEW.json"])
    row("AM-16", "Git remote unavailable to an agent", "Attack M1-H is defended.",
        attack("M1-H"), ["checkpoint:M1-INTERNAL-RED-TEAM.json"])
    if findings is None:
        outcome: tuple[bool | None, str] = (None, "findings not consolidated")
    else:
        blocking = [item for item in findings.get("findings") or []
                    if item.get("severity") in ("CRITICAL", "HIGH")
                    and item.get("status") != "CLOSED"]
        outcome = (not blocking, f"{len(findings.get('findings') or [])} finding(s); unresolved "
                                 f"Critical/High: {[item['id'] for item in blocking] or 'none'}")
    row("AM-17", "No unresolved Critical/High finding",
        "No finding of this review, and no open finding of the Gates, is Critical or High "
        "unresolved.", outcome, ["checkpoint:REVIEW-REPORT.md", "checkpoint:FINDINGS.json"])
    row("AM-18", "Completeness and evidence of the Gates",
        "Each Gate's matrix, recomputed by the validator from its tag, is complete with every "
        "evidence reference resolved, from this repository and from the published remote.",
        ((bool(final) and all(item["ok"] and item["coveragePercent"] == 100.0
                              and item["completeness"] == "PASS" for item in final)
          and bool(remote_subjects) and not remote_failed) if final else None,
         "; ".join(f"{item['checkpoint']} {item['requirements']} requirements "
                   f"{item['coveragePercent']}% completeness {item['completeness']}"
                   for item in final)
         + (f"; from the published remote the evidence of {remote_failed} does not resolve"
            if remote_failed else "")),
        ["checkpoint:SEALED-SUBJECTS.json", "checkpoint:SEALED-SUBJECTS-PUBLISHED.json"])
    g_ok, g_seen = attack("M1-G")
    row("AM-19", "R-G3-001 dispositioned from proof",
        "Ten controls proved and no untrusted input reaches an engine operation.",
        ((review.get("result") == "PASS" and g_ok) if review and g_ok is not None else None,
         f"{review.get('passed')}/{review.get('total')} controls, disposition "
         f"{review.get('disposition')}; {g_seen}"),
        ["checkpoint:R-G3-001-REVIEW.json", "checkpoint:M1-INTERNAL-RED-TEAM.json"])
    row("AM-20", "The audit's Red Team",
        "Every attack of the cross-gate battery is defended over a valid null-mutation control.",
        ((red.get("result") == "RED_TEAM_PASS") if red else None,
         f"{red.get('result')} {red.get('defended')}/{red.get('total')} control "
         f"{(red.get('baselineControl') or {}).get('result')}"),
        ["checkpoint:M1-INTERNAL-RED-TEAM.json", "checkpoint:RED-TEAM-REPORT.md"])

    failed = [item for item in rows if item["verdict"] != "PASS"]
    document = {
        "schemaVersion": "1.0.0", "artifact": "FINAL-M1-AUDIT-MATRIX", "checkpoint": CHECKPOINT.name,
        "milestone": "M1", "gate": "GATE-3", "subjectCheckpoint": "GATE-3-CP-0001",
        "subjectCommit": "3bc8e9d8a94d44163d1af9325ad5b2272f71f8ed",
        "auditMechanism": "FRESH_SESSION_INDEPENDENT_AUDIT", "sameToolAsImplementer": True,
        "createdAt": utc_now(),
        "note": ("The rows are the criteria frozen in PLAN.md before execution. Each verdict is "
                 "computed from an artifact this audit wrote by executing something."),
        "rows": rows, "passed": len(rows) - len(failed), "total": len(rows),
        "result": "PASS" if not failed else "FAIL",
    }
    write_json(CHECKPOINT / "FINAL-M1-AUDIT-MATRIX.json", document)
    lines = ["# Final M1 audit matrix", "", f"Result: `{document['result']}` — "
             f"{document['passed']}/{document['total']} criteria", "",
             "| Criterion | Dimension | Verdict | Observed |", "|---|---|---|---|"]
    for item in rows:
        observed = item["observed"].replace("|", "/").replace("\n", " ")[:400]
        lines.append(f"| {item['id']} | {item['dimension']} | `{item['verdict']}` | {observed} |")
    (CHECKPOINT / "FINAL-M1-AUDIT-MATRIX.md").write_text("\n".join(lines) + "\n",
                                                         encoding="utf-8", newline="\n")
    print(f"M1_AUDIT_MATRIX={document['result']} {document['passed']}/{document['total']}")
    for item in failed:
        print(f"- {item['id']} {item['verdict']}: {item['observed'][:200]}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
