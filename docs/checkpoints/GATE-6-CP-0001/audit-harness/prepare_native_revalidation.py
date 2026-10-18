"""Bind actual local native repair evidence and require a fresh whole immutable assurance cycle."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from assemble_source_ready import local_handoff_sections, render_handoff, render_next
from derive_requirements import render_closure, render_matrix
from ledger_common import load_json, use_utf8_stdout, utc_now, write_json
from sync_in_progress_metadata import synchronize


def main() -> int:
    state = load_json(CHECKPOINT / "STATE.json")
    if state["status"] != "IN_PROGRESS" or (CHECKPOINT / "VERIFY.json").exists():
        raise ValueError("unsealed archived rework state required")
    manifest = load_json(CHECKPOINT / "attempts/RUNTIME-V5-ASSURANCE-ARCHIVE.json")
    if manifest["result"] != "PASS" or len(manifest["records"]) != 19:
        raise ValueError("the complete exact historical archive is required")
    for row in manifest["records"]:
        raw = (ROOT / row["archive"]).read_bytes()
        if len(raw) != row["bytes"] or hashlib.sha256(raw).hexdigest() != row["sha256"]:
            raise ValueError("historical archive changed")
    observation = load_json(CHECKPOINT / "attempts/NATIVE-JOB-COMPLETION-0001.json")
    if not observation["zeroAccountingWithUnsignaledOwnedMemberObserved"]:
        raise ValueError("the actual old completion predicate must be disproved")
    for sequence in (1, 2):
        proof = load_json(CHECKPOINT / f"attempts/NATIVE-COMPLETION-PROOF-{sequence:04d}-RECEIPT.json")
        raw = (ROOT / proof["producerArchive"]).read_bytes()
        if (proof["result"] != "PASS" or not proof["allObservedOwnedMembersSignaled"]
                or not proof["ownedTemporaryDirectoryRemoved"]
                or hashlib.sha256(raw).hexdigest() != proof["producerSha256"]):
            raise ValueError("fresh actual native proof missing or changed")
    commands = {row["id"]: row for row in (json.loads(line) for line in
                (CHECKPOINT / "COMMANDS.jsonl").read_text(encoding="utf-8").splitlines() if line.strip())}
    for identifier in ("cmd-0276", "cmd-0279", "cmd-0281", "cmd-0282", "cmd-0283"):
        if commands[identifier]["exitCode"] != 0:
            raise ValueError("local corrective command must actually succeed")

    findings = load_json(CHECKPOINT / "FINDINGS.json")
    finding = next(row for row in findings["findings"] if row["findingId"] == "G6-INT-019")
    finding["status"] = "CLOSED"
    finding["rootCause"] = ("Actual cmd-0274 pins a current owned job member and observes WAIT_TIMEOUT258 "
        "after the old close routine reports zero active members. Accounting was incorrectly treated as "
        "completed asynchronous termination. A separate pre-fix control cmd-0265 proves lost failure "
        "observations. Cmd-0269 proves the lock persisted through the entire existing removal budget, "
        "not budget consumed by traversal. The exact historical log owner is not retroactively known.")
    finding["evidence"] = ["command:cmd-0258", "command:cmd-0265", "command:cmd-0269", "command:cmd-0274",
        "checkpoint:attempts/RUNTIME-V5-ASSURANCE-RED-TEAM-NATIVE.json",
        "checkpoint:attempts/RUNTIME-V5-ASSURANCE-RED-TEAM-EXECUTIONS.json",
        "checkpoint:attempts/RUNTIME-V5-ASSURANCE-M2-INTERNAL-RED-TEAM.json"]
    finding["resolution"] = ("Pin a complete bounded job-member snapshot, verify exact handle membership, "
        "require zero accounting plus signaled observed members, and close acquired handles on all paths. "
        "Keep both ten-second bounds and mandatory physical directory removal. Preserve/rethrow typed "
        "cleanup failure observations. Formerly failing controls pass cmd-0276; all77 Gate5/Gate6 root "
        "cases pass canonical discovery cmd-0279, including snapshot/identity refusal. Two actual fresh "
        "uninstrumented native proofs pass cmd-0281. LSN-0125 recurrence2 remains CRITICAL, locally GUARDED. "
        "This closes causal rework only: a new immutable full subject and every ordered assurance step remain due.")
    finding["resolutionEvidence"] = ["command:cmd-0267", "command:cmd-0276", "command:cmd-0279", "command:cmd-0281",
        "command:cmd-0282", "checkpoint:attempts/NATIVE-JOB-COMPLETION-0001.json",
        "checkpoint:attempts/NATIVE-COMPLETION-PROOF-0001-RECEIPT.json",
        "checkpoint:attempts/NATIVE-COMPLETION-PROOF-0002-RECEIPT.json",
        "checkpoint:attempts/RUNTIME-V5-ASSURANCE-ARCHIVE.json"]
    if not any(row["findingId"] == "G6-INT-020" for row in findings["findings"]):
        findings["findings"].append({"findingId": "G6-INT-020", "severity": "LOW", "status": "CLOSED",
            "title": "Ad hoc qualified unittest invocation omits canonical discovery import context",
            "observed": "Cmd-0277 runs77 cases but two inherited adapter imports fail because tests is not the discovery root. Cmd-0278 is a recorder precondition refusal for a glob ending in .py, not a test result.",
            "rootCause": "Incorrect ad hoc invocation; no production or inherited test defect is established.",
            "resolution": "Use the existing canonical discover -s tests context and supported non-script glob. Cmd-0279 executes the same complete77 cases PASS; assertions and source imports are unchanged.",
            "evidence": ["command:cmd-0277", "command:cmd-0278"], "resolutionEvidence": ["command:cmd-0279"]})
    write_json(CHECKPOINT / "FINDINGS.json", findings)
    for name in ("REQUIREMENTS-MATRIX.json", "CLOSURE-REQUIREMENTS.json"):
        document = load_json(CHECKPOINT / name)
        for row in document["requirements"]:
            row["status" if name.startswith("REQUIREMENTS") else "finalStatus"] = "PARTIAL"
            row["validationEvidence"] = []
            row["notes"] = "Historical v5 assurance is archived byte-for-byte. Current causal native correction passes local controls; complete fresh immutable verification and ordered assurance remain mandatory for every original derived requirement."
        write_json(CHECKPOINT / name, document)
        renderer = render_matrix if name.startswith("REQUIREMENTS") else render_closure
        (CHECKPOINT / name.replace(".json", ".md")).write_text(renderer(document), encoding="utf-8", newline="\n")
    quality = load_json(CHECKPOINT / "QUALITY.json")
    quality["checks"]["redTeam"].update({"status": "FAIL", "evidence": [
        "file:attempts/RUNTIME-V5-ASSURANCE-M2-INTERNAL-RED-TEAM.json",
        "file:attempts/RUNTIME-V5-ASSURANCE-RED-TEAM-NATIVE.json"],
        "justification": "Historical cmd-0258 remains FAIL with INVALID baseline. Local causal correction passes; no current fresh Red Team or complete Gate verdict exists yet."})
    write_json(CHECKPOINT / "QUALITY.json", quality)
    state["nextAllowedAction"] = ("Freeze and publish a new Gate6-only immutable runtime subject after local native "
        "completion repair, current lesson/preflight derivation, full lint and valid serialized bookkeeping. "
        "Execute all47 non-fast stages, whole15 Green Keeper, total completeness, fresh internal Red Team/null "
        "control, full18-dimension clean-clone mirror, then actual canonical seal/publication/archive checks. "
        "Historical v5 successes and failed Red Team remain archived. Independent M2 remains pending; Gate7 is not authorized.")
    total = len(load_json(CHECKPOINT / "REQUIREMENTS-MATRIX.json")["requirements"])
    state["requirementsMatrix"].update({"complete": 0, "partial": total, "coveragePercent": 0})
    state["greenKeeper"]["evidence"] = ["checkpoint:REWORK-LOG.jsonl",
        "checkpoint:attempts/RUNTIME-V5-ASSURANCE-M2-INTERNAL-RED-TEAM.json"]
    state["deliveryCompleteness"]["evidence"] = []
    state["updatedAt"] = utc_now()
    write_json(CHECKPOINT / "STATE.json", state)
    steps = load_json(CHECKPOINT / "STEPS.json")
    steps["steps"][1]["functionalProof"] += " Native completion rework is causally accepted locally by cmd-0274/0276/0279/0281 without extending deadlines or claiming whole-Gate acceptance."
    steps["steps"][1]["evidence"] += ["cmd-0274", "cmd-0276", "cmd-0279", "cmd-0281"]
    steps["steps"][2].update({"status": "IN_PROGRESS", "functionalProof":
        "Historical v5 full47, functional37/37, whole Green Keeper cycle5 and completeness pass, then fresh Red Team fails native cleanup. All19 original assurance/producer reports are archived byte-for-byte by cmd-0282. Local corrective proofs pass; complete fresh immutable verification, every ordered internal control and actual seal remain pending.",
        "evidence": ["cmd-0232", "cmd-0256", "cmd-0258", "cmd-0282", "attempts/RUNTIME-V5-ASSURANCE-ARCHIVE.json"]})
    write_json(CHECKPOINT / "STEPS.json", steps)
    preflight = load_json(CHECKPOINT / "LESSON-PREFLIGHT.json")
    marker = "\n<!-- BEGIN DERIVED LESSON COMMITMENTS -->\n"
    plan_path = CHECKPOINT / "PLAN.md"
    plan = plan_path.read_text(encoding="utf-8").split(marker, 1)[0].rstrip()
    commitments = []
    for row in preflight["applicable"]:
        commitments.extend(["", "### " + row["derivedRequirementId"] + " — " + row["lessonId"], "",
                            "- Required check: " + row["requiredCheck"],
                            "- Required evidence: " + row["requiredEvidence"]])
    plan_path.write_text(plan + marker + "\n".join(commitments) + "\n", encoding="utf-8", newline="\n")
    sections = local_handoff_sections()
    sections["## What was completed"] += " Historical v5 full47/47, functional37/37, Green Keeper15 and completeness PASS are exact archives, not current approval. The later failed Red Team is retained. Current native causal repair passes formerly failing controls, complete77 Gate5/Gate6 root cases and two actual fresh native removal proofs."
    sections["## Important decisions"] += " ADR-0052 requires observed exact-owned-member synchronization and retained typed cleanup facts under unchanged deadlines; actual directory removal remains mandatory."
    sections["## Tests executed"] += " Cmd-0274 disproves the old job completion predicate with a real pinned handle; cmd-0276/0279/0281 accept local corrective controls and real native removal. Cmd-0277/0278 are retained wrong-invocation/precondition failures, not edited tests."
    sections["## Known failures"] = "Historical Red Team cmd-0258 remains FAIL/INVALID in attempts/RUNTIME-V5-ASSURANCE-ARCHIVE.json. Local G6-INT-019 causal repair is closed, but the fresh whole assurance cycle is pending. Non-reproducing diagnostics do not constitute repair; historical exact log-holder identity remains unknown."
    sections["## Do not repeat"] = "Never overlap ledger/inventory/validation writers, narrow denominators or replace failures with later successes. Do not replay immutable diagnostic/capture/recovery helpers. Never retry the four policy-refused targets named in earlier recovery evidence. Never stop unrelated applications, alter global profiles or move published tags."
    (CHECKPOINT / "HANDOFF.md").write_text(render_handoff(sections), encoding="utf-8", newline="\n")
    (CHECKPOINT / "NEXT.md").write_text(render_next(state["nextAllowedAction"]), encoding="utf-8", newline="\n")
    (CHECKPOINT / "STATUS.md").write_text("# Status\n\nIN_PROGRESS — local native repair accepted; complete fresh immutable verification and ordered assurance/seal pending.\n", encoding="utf-8", newline="\n")
    (CHECKPOINT / "PROGRESS.md").write_text("# Gate 6 progress\n\n" + sections["## What was completed"]
        + "\n\n" + sections["## Known failures"] + "\n\nNext: " + state["nextAllowedAction"] + "\n", encoding="utf-8", newline="\n")
    synchronize(ROOT, CHECKPOINT)
    print(f"LOCAL_NATIVE_REWORK_BOUND; all{total} requirements retained PARTIAL pending fresh whole assurance; no Gate or independent verdict")
    return 0


if __name__ == "__main__":
    use_utf8_stdout()
    raise SystemExit(main())
