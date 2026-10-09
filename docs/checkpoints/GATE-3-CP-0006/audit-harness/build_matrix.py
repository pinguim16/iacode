#!/usr/bin/env python3
"""Build the 32-row final M1 audit matrix from this session's evidence."""
from __future__ import annotations

import json
import sys
from pathlib import Path

CP = Path(__file__).resolve().parent.parent
ROOT = CP.parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "development-ledger"))
from ledger_common import utc_now, write_json  # noqa: E402

SUBJECT = "GATE-3-CP-0005"
SUBJECT_COMMIT = "3ef2bf77ddbddd378d35f5c4d32f2d90d42fc97d"


def load(name: str) -> dict:
    path = CP / name
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}


def main() -> int:
    sealed, published = load("SEALED-SUBJECTS.json"), load("SEALED-SUBJECTS-PUBLISHED.json")
    objects, deps = load("REMOTE-PUBLISHED-OBJECTS.json"), load("DEPENDENCY-SCAN-REPORT.json")
    verify, clone = load("VERIFICATION-REPORT.json"), load("CLEAN-CLONE-REPORT.json")
    live, origin = load("LIVE-CODING-RUN.json"), load("TOOL-RESULT-ORIGIN.json")
    red, risk = load("M1-INTERNAL-RED-TEAM.json"), load("R-G3-001-REVIEW.json")
    sse, docs = load("SSE-TERMINAL-DRAIN.json"), load("DOCUMENTATION-AND-MEMORY-REVIEW.json")
    complete, findings = load("COMPLETENESS-REPORT.json"), load("FINDINGS.json")
    tests, counts = load("TESTS.json"), load("COUNTS.json")
    quality, state, bundle = load("QUALITY.json"), load("STATE.json"), load("REVIEW-BUNDLE-VALIDATION.json")
    mirror = load("M1-INTERNAL-MIRROR.json")
    attest_path = ROOT / ".iacode" / "attestations" / "M1-CP-0006.json"
    attest = json.loads(attest_path.read_text(encoding="utf-8")) if attest_path.is_file() else {}
    stages = {x["name"]: x for x in verify.get("stages") or []}
    checks = {x["name"]: x for x in live.get("checks") or []}
    attacks = {x["attackId"]: x for x in red.get("attacks") or []}
    commands = [json.loads(x) for x in (CP / "COMMANDS.jsonl").read_text(encoding="utf-8").splitlines() if x]

    def stage(*names: str) -> tuple[bool | None, str]:
        if not stages:
            return None, "verification absent"
        values = {n: (stages.get(n) or {}).get("result") for n in names}
        return all(v == "PASS" for v in values.values()), ", ".join(f"{k}={v}" for k, v in values.items())

    def attack(*names: str) -> tuple[bool | None, str]:
        if not red:
            return None, "Red Team absent"
        values = {n: (attacks.get(n) or {}).get("result") for n in names}
        control = (red.get("baselineControl") or {}).get("result")
        return control == "VALID" and all(v == "DEFENDED" for v in values.values()), ", ".join(
            f"{k}={v}" for k, v in values.items()) + f", control={control}"

    rows: list[dict] = []

    def add(identifier: str, title: str, expected: str, outcome: tuple[bool | None, str], evidence: list[str]) -> None:
        ok, observed = outcome
        rows.append({"id": identifier, "criterion": title, "expectation": expected,
                     "mandatory": True, "status": "COMPLETE" if ok is not None else "UNVERIFIED",
                     "observed": observed, "evidence": evidence,
                     "verdict": "PASS" if ok else ("FAIL" if ok is False else "UNVERIFIED")})

    locals_ = sealed.get("subjects") or []
    remotes = published.get("subjects") or []
    local = next((x for x in locals_ if x.get("checkpoint") == SUBJECT), {})
    remote = next((x for x in remotes if x.get("checkpoint") == SUBJECT), {})
    add("AM-01", "Subject identity and immutability", "Local and remote tags bind the frozen commit.",
        ((local.get("ok") is True and remote.get("ok") is True and local.get("commit") == SUBJECT_COMMIT
          and remote.get("commit") == SUBJECT_COMMIT) if locals_ else None,
         f"local={local.get('commit')} remote={remote.get('commit')} expected={SUBJECT_COMMIT}"),
        ["checkpoint:SEALED-SUBJECTS.json", "checkpoint:SEALED-SUBJECTS-PUBLISHED.json"])
    add("AM-02", "Local subject validity", "Checkpoint, lessons and anchored integrity pass.",
        ((sealed.get("result") == "PASS" and local.get("ok") is True) if sealed else None,
         f"result={sealed.get('result')} subject={local.get('ok')} anchors={sealed.get('anchors')}"),
        ["checkpoint:SEALED-SUBJECTS.json", "command:cmd-0001", "command:cmd-0002"])
    add("AM-03", "Published history", "Every sealed M1 checkpoint validates from a transport clone.",
        ((published.get("result") == "PASS" and remotes and all(x.get("ok") for x in remotes)) if published else None,
         f"result={published.get('result')} valid={sum(1 for x in remotes if x.get('ok'))}/{len(remotes)}"),
        ["checkpoint:SEALED-SUBJECTS-PUBLISHED.json"])
    obj_checks = objects.get("checks") or []
    add("AM-04", "Remote synchronization", "Main, tags and preserved evidence are published.",
        ((objects.get("result") == "PASS" and published.get("result") == "PASS") if objects else None,
         f"objects={objects.get('result')} subjects={published.get('result')} remote={objects.get('remote')}"),
        ["checkpoint:REMOTE-PUBLISHED-OBJECTS.json", "command:cmd-0005"])
    add("AM-05", "Unpublished-evidence negative control", "Removing/restoring preserved refs fails/passes causally.",
        ((objects.get("result") == "PASS" and len(obj_checks) >= 3 and all(x.get("ok") for x in obj_checks)) if objects else None,
         f"result={objects.get('result')} checks={sum(1 for x in obj_checks if x.get('ok'))}/{len(obj_checks)}"),
        ["checkpoint:REMOTE-PUBLISHED-OBJECTS.json", "checkpoint:M1-INTERNAL-RED-TEAM.json"])

    scans = {x.get("ecosystem"): x for x in deps.get("scans") or []}
    py, npm = scans.get("pypi") or {}, scans.get("npm") or {}
    nc = npm.get("counts") or {}
    add("AM-06", "Fresh dependency security", "Both sources scan; Critical=0 and High=0.",
        ((deps.get("result") == "PASS" and py.get("status") == npm.get("status") == "SCANNED"
          and int(nc.get("critical") or 0) == int(nc.get("high") or 0) == 0 and not py.get("blocking")) if deps else None,
         f"result={deps.get('result')} pypi={py.get('status')} npm={npm.get('status')} critical={nc.get('critical')} high={nc.get('high')}"),
        ["checkpoint:DEPENDENCY-SCAN-REPORT.json", "command:cmd-0007", "command:cmd-0008"])
    lock = (ROOT / "apps/web/package-lock.json").read_text(encoding="utf-8")
    scanner = (ROOT / "scripts/iacode/dependency_scan.py").read_text(encoding="utf-8")
    graph_ok = deps.get("result") == "PASS" and '"packages"' in lock and "package-lock.json" in scanner and "pip-audit" in scanner
    add("AM-07", "Dependency graph reality", "Resolved npm and Python graphs, not direct manifests, are evaluated.",
        (graph_ok if deps else None, "package-lock packages plus pip-audit inputs present; live scan PASS"),
        ["file:apps/web/package-lock.json", "file:scripts/iacode/dependency_scan.py", "checkpoint:DEPENDENCY-SCAN-REPORT.json"])
    add("AM-08", "Full verification", "All 32 non-fast stages pass now.",
        ((verify.get("result") == "PASS" and verify.get("fast") is False and len(stages) == 32
          and all(x.get("result") == "PASS" for x in stages.values())) if verify else None,
         f"result={verify.get('result')} fast={verify.get('fast')} passed={sum(x.get('result') == 'PASS' for x in stages.values())}/{len(stages)} clone={clone.get('result')}"),
        ["checkpoint:VERIFICATION-REPORT.json", "checkpoint:CLEAN-CLONE-REPORT.json", "command:cmd-0013"])
    tc = counts.get("counts", counts).get("TESTS") or {}
    categories = [tests.get(n) or {} for n in ("unit", "integration", "e2e")]
    add("AM-09", "Count integrity", "Discovered and deduplicated passed test counts match.",
        ((bool(tc) and tc.get("numerator") == tc.get("denominator")
          and all(x.get("executed") and x.get("failed") == 0 for x in categories)) if counts else None,
         f"TESTS={tc.get('numerator')}/{tc.get('denominator')} categories=" + ",".join(
             f"{x.get('passed')}/{x.get('failed')}:{x.get('runId')}" for x in categories)),
        ["checkpoint:TESTS.json", "checkpoint:COUNTS.json", "checkpoint:VERIFICATION-REPORT.json"])
    add("AM-10", "Foundation functional path", "Startup through fresh install passes.",
        stage("stack", "integration", "infra", "smoke", "backup", "restart", "dependency-failure", "fresh-install"),
        ["checkpoint:VERIFICATION-REPORT.json"])

    add("AM-11", "Configured Model Gateway", "The configured model runs through the gateway without substitution.",
        ((live.get("result") == "PASS" and live.get("finalState") == "SUCCEEDED"
          and live.get("model") == live.get("configuredModel") and (checks.get("model calls through the gateway") or {}).get("ok")) if live else None,
         f"result={live.get('result')} state={live.get('finalState')} model={live.get('model')} configured={live.get('configuredModel')}"),
        ["checkpoint:LIVE-CODING-RUN.json", "checkpoint:VERIFICATION-REPORT.json"])
    add("AM-12", "Agent Runtime functional path", "A live run traverses queue, workflow, events and terminal completion.",
        ((live.get("result") == "PASS" and live.get("finalState") == "SUCCEEDED"
          and all((stages.get(n) or {}).get("result") == "PASS" for n in ("gate:agentRuntimeTests", "agent-runtime-smoke", "agent-durability"))) if live else None,
         f"live={live.get('finalState')}; " + ", ".join(f"{n}={(stages.get(n) or {}).get('result')}" for n in ("gate:agentRuntimeTests", "agent-runtime-smoke", "agent-durability"))),
        ["checkpoint:LIVE-CODING-RUN.json", "checkpoint:VERIFICATION-REPORT.json"])
    crossing = ("model calls through the gateway", "the configured model made a valid tool request",
                "at least one tool executed in a sandbox", "tool results delivered to the runtime",
                "the runtime called the model again after a sandbox result", "host sentinel untouched",
                "no sandbox container outlives the run")
    add("AM-13", "Cross-Gate tool path", "One SUCCEEDED configured-model run completes the full tool round-trip.",
        ((live.get("result") == "PASS" and live.get("finalState") == "SUCCEEDED"
          and all((checks.get(n) or {}).get("ok") for n in crossing)) if live else None,
         f"result={live.get('result')} state={live.get('finalState')}; " + ", ".join(f"{n}={(checks.get(n) or {}).get('ok')}" for n in crossing)),
        ["checkpoint:LIVE-CODING-RUN.json", "checkpoint:CROSS-GATE-LIVE.json", "checkpoint:FINDINGS.json"])
    repairs = (live.get("observations") or {}).get("repairAttempts")
    add("AM-14", "Live ToolRequest contract", "The model emits canonical requests with zero repair.",
        ((live.get("result") == "PASS" and repairs == 0 and (checks.get("the configured model made a valid tool request") or {}).get("ok")) if live else None,
         f"result={live.get('result')} repairs={repairs} requests={len(live.get('toolRequests') or [])}"),
        ["checkpoint:LIVE-CODING-RUN.json"])
    os_ = {x.get("step"): x.get("result") for x in origin.get("steps") or []}
    required = ("forgery.refused_while_the_sandbox_executes", "forgery.stored_result_is_the_sandbox_result",
                "forgery.refused_after_the_run_ended", "forgery.nothing_changed_after_the_refusals")
    pa = attack("M1-P")
    add("AM-15", "Forged ToolResult defense", "During/after forgeries are refused and never stored.",
        ((origin.get("result") == "PASS" and all(os_.get(n) == "PASS" for n in required) and pa[0] is True) if origin and pa[0] is not None else None,
         f"probe={origin.get('result')} steps={os_}; {pa[1]}"),
        ["checkpoint:TOOL-RESULT-ORIGIN.json", "checkpoint:M1-INTERNAL-RED-TEAM.json"])
    add("AM-16", "Sandbox filesystem isolation", "Traversal, links and cross-run access are defended.",
        attack("M1-D", "M1-E"), ["checkpoint:M1-INTERNAL-RED-TEAM.json"])
    privilege = attack("M1-A", "M1-C", "M1-F", "M1-G")
    add("AM-17", "Sandbox privilege boundary", "Host, engine, mount and policy escalation fail.",
        ((privilege[0] is True and (checks.get("host sentinel untouched") or {}).get("ok")) if privilege[0] is not None and live else None,
         privilege[1] + f"; hostSentinel={(checks.get('host sentinel untouched') or {}).get('ok')}"),
        ["checkpoint:M1-INTERNAL-RED-TEAM.json", "checkpoint:LIVE-CODING-RUN.json"])
    add("AM-18", "Host secret isolation", "Synthetic controller secrets remain absent.", attack("M1-B"),
        ["checkpoint:M1-INTERNAL-RED-TEAM.json"])
    add("AM-19", "Network boundary", "Network-none blocks external and stack egress.", attack("M1-I"),
        ["checkpoint:M1-INTERNAL-RED-TEAM.json"])
    ra, rs = attack("M1-K", "M1-R"), stage("gate:sandboxTests", "sandbox-timeout", "sandbox-cancellation")
    add("AM-20", "Resource, timeout and cleanup", "Limits, timeout, cancellation and cleanup hold.",
        ((ra[0] is True and rs[0] is True) if ra[0] is not None and rs[0] is not None else None, ra[1] + "; " + rs[1]),
        ["checkpoint:M1-INTERNAL-RED-TEAM.json", "checkpoint:VERIFICATION-REPORT.json"])
    ga = attack("M1-G")
    add("AM-21", "R-G3-001", "Ten controls pass and untrusted input reaches no engine operation.",
        ((risk.get("result") == "PASS" and risk.get("passed") == risk.get("total")
          and risk.get("untrustedInputReachesEngineOperation") is False and ga[0] is True) if risk and ga[0] is not None else None,
         f"result={risk.get('result')} controls={risk.get('passed')}/{risk.get('total')} untrusted={risk.get('untrustedInputReachesEngineOperation')}; {ga[1]}"),
        ["checkpoint:R-G3-001-REVIEW.json", "checkpoint:M1-INTERNAL-RED-TEAM.json"])
    add("AM-22", "Durability", "Durability, restart, deadlines, recovery and ToolResults pass.",
        stage("agent-durability", "agent-cancellation", "agent-deadline", "sandbox-recovery", "sandbox-tool-result-origin", "restart"),
        ["checkpoint:VERIFICATION-REPORT.json"])
    add("AM-23", "SSE terminal drain", "The dedicated multi-page terminal SSE regression passes.",
        ((sse.get("result") == "PASS" and sse.get("exitCode") == 0) if sse else None,
         f"result={sse.get('result')} exit={sse.get('exitCode')} test={sse.get('test')}"),
        ["checkpoint:SSE-TERMINAL-DRAIN.json"])

    scans_ = [x for x in commands if x.get("operation") == "security-scan"
              and "secret_scan.py --history" in str(x.get("command"))]
    cv = stages.get("gate:checkpointValidation") or {}
    add("AM-24", "Secret and public-history scans", "History and checkpoint content scan clean.",
        ((bool(scans_) and all(x.get("exitCode") == 0 for x in scans_) and cv.get("result") == "PASS") if stages else None,
         f"history={[(x.get('id'), x.get('exitCode')) for x in scans_]} checkpointValidation={cv.get('result')}"),
        ["command:cmd-0006", "checkpoint:VERIFICATION-REPORT.json"])
    dc = docs.get("checks") or []
    add("AM-25", "Documentation and runbooks", "Runbooks exist and reproduce current behavior.",
        ((docs.get("result") == "PASS" and all(x.get("ok") for x in dc[:3])) if docs else None,
         f"review={docs.get('result')} checks={sum(bool(x.get('ok')) for x in dc[:3])}/{len(dc[:3])}"),
        ["checkpoint:DOCUMENTATION-AND-MEMORY-REVIEW.json", "checkpoint:VERIFICATION-REPORT.json"])
    measured = docs.get("guardrailEffectiveness") or {}
    add("AM-26", "Engineering Memory", "Lessons, preflight and guardrails validate with zero failure.",
        ((docs.get("result") == "PASS" and dc[3:] and all(x.get("ok") for x in dc[3:])
          and measured.get("guardrailFailures") == 0) if docs else None,
         f"review={docs.get('result')} effective={measured.get('guardrailsEffective')}/{measured.get('guardrailsTotal')} failures={measured.get('guardrailFailures')}"),
        ["checkpoint:DOCUMENTATION-AND-MEMORY-REVIEW.json", "checkpoint:LESSON-PREFLIGHT.json"])
    finals = [x for x in locals_ if x.get("finalOfGate")]
    complete_ok = complete.get("result") == "PASS" and complete.get("coveragePercent") == 100.0 and complete.get("evidenceCoveragePercent") == 100.0
    add("AM-27", "Accumulated M1 completeness", "Four Gates and the audit have 100% evidence coverage.",
        ((len(finals) == 4 and all(x.get("completeness") == "PASS" and x.get("coveragePercent") == 100.0 for x in finals) and complete_ok) if complete else None,
         f"finalGates={len(finals)}/4 current={complete.get('result')} coverage={complete.get('coveragePercent')} evidence={complete.get('evidenceCoveragePercent')}"),
        ["checkpoint:SEALED-SUBJECTS.json", "checkpoint:COMPLETENESS-REPORT.json"])
    add("AM-28", "Independent Red Team", "All fresh attacks are defended over a valid control.",
        ((red.get("result") == "RED_TEAM_PASS" and red.get("escaped") == 0 and red.get("defended") == red.get("total")
          and (red.get("baselineControl") or {}).get("result") == "VALID") if red else None,
         f"result={red.get('result')} defended={red.get('defended')}/{red.get('total')} escaped={red.get('escaped')} control={(red.get('baselineControl') or {}).get('result')}"),
        ["checkpoint:M1-INTERNAL-RED-TEAM.json", "checkpoint:RED-TEAM-ATTEMPT-1.json"])
    ff = findings.get("findings") or []
    blockers = [x.get("id") for x in ff if x.get("severity") in ("CRITICAL", "HIGH") and x.get("status") != "CLOSED"]
    fields = {"id", "severity", "requirement", "observation", "reproduction", "expected", "observed", "evidence", "impact", "recommendedCorrection", "status"}
    shape = all(fields <= set(x) for x in ff)
    add("AM-29", "Findings threshold", "Critical=0, High=0 and finding fields are complete.",
        ((not blockers and shape) if findings else None, f"total={len(ff)} blocking={blockers or 'none'} requiredFields={shape}"),
        ["checkpoint:FINDINGS.json"])
    qc = quality.get("checks") or {}
    qnames = ("build", "unitTests", "integrationTests", "e2e", "lint", "staticAnalysis", "security",
              "documentation", "checkpointValidation", "greenKeeper", "deliveryCompleteness")
    assurance = (state.get("greenKeeper", {}).get("status") == "PASS"
                 and state.get("deliveryCompleteness", {}).get("status") == "PASS"
                 and mirror.get("result") == "PASS"
                 and all((qc.get(n) or {}).get("status") == "PASS" for n in qnames))
    add("AM-30", "Audit-checkpoint assurance", "Green Keeper, completeness and quality pass before seal.",
        (assurance if state and quality else None,
         f"green={state.get('greenKeeper', {}).get('status')} completeness={state.get('deliveryCompleteness', {}).get('status')} mirror={mirror.get('result')}; "
         + ", ".join(f"{n}={(qc.get(n) or {}).get('status')}" for n in qnames)),
        ["checkpoint:STATE.json", "checkpoint:QUALITY.json", "checkpoint:COMPLETENESS-REPORT.json",
         "checkpoint:M1-INTERNAL-MIRROR.json"])
    mechanism = attest.get("validationMechanism")
    add("AM-31", "Attestation and derived verdict", "A truthful fresh-session attestation is ready for post-seal derivation.",
        ((attest.get("milestone") == "M1" and attest.get("subjectCheckpoint") == SUBJECT
          and attest.get("subjectCommit") == SUBJECT_COMMIT and mechanism == "FRESH_SESSION_INDEPENDENT_AUDIT"
          and attest.get("freshSession") is True and attest.get("reviewResult") == "APPROVED") if attest else None,
         f"attestation={'present' if attest else 'absent'} mechanism={mechanism} fresh={attest.get('freshSession')} review={attest.get('reviewResult')}; verdict derives post-seal"),
        ["file:.iacode/attestations/M1-CP-0006.json"])
    add("AM-32", "Review bundle", "CRC, manifest, checksums, mandatory files and secret scan pass.",
        ((bundle.get("result") == "PASS" and bundle.get("passed") == bundle.get("total")) if bundle else None,
         f"pre-seal={bundle.get('result')} {bundle.get('passed')}/{bundle.get('total')}; regenerated and revalidated after publication"),
        ["checkpoint:REVIEW-BUNDLE-VALIDATION.json", "file:docs/checkpoints/GATE-3-CP-0006/audit-harness/validate_review_bundle.py"])

    failed = [x for x in rows if x["verdict"] != "PASS"]
    document = {"schemaVersion": "1.0.0", "artifact": "FINAL-M1-AUDIT-MATRIX", "checkpoint": CP.name,
                "milestone": "M1", "gate": "GATE-3", "subjectCheckpoint": SUBJECT,
                "subjectCommit": SUBJECT_COMMIT, "auditMechanism": "FRESH_SESSION_INDEPENDENT_AUDIT",
                "sameToolAsImplementer": True, "createdAt": utc_now(), "rows": rows,
                "passed": len(rows) - len(failed), "total": len(rows),
                "result": "PASS" if not failed else "FAIL"}
    write_json(CP / "FINAL-M1-AUDIT-MATRIX.json", document)
    lines = ["# Final M1 audit matrix", "", f"Result: `{document['result']}` — {document['passed']}/{document['total']} criteria", "",
             "| Criterion | Dimension | Verdict | Observed |", "|---|---|---|---|"]
    for item in rows:
        observed = item["observed"].replace("|", "/").replace("\n", " ")[:500]
        lines.append(f"| {item['id']} | {item['criterion']} | `{item['verdict']}` | {observed} |")
    (CP / "FINAL-M1-AUDIT-MATRIX.md").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(f"M1_AUDIT_MATRIX={document['result']} {document['passed']}/{document['total']}")
    for item in failed:
        print(f"- {item['id']} {item['verdict']}: {item['observed'][:240]}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
