#!/usr/bin/env python3
"""The CP-0009 auditor's own execution of the mandatory and additional attack battery.

Every attack is written here by the auditor against the product's published
controls. The delivery's own ``m0_red_team.py`` is never imported, so a DEFENDED
verdict here is a statement about the product, not about the product's harness.

All mutations happen in a disposable clone under the session scratchpad.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
import os as _os
from pathlib import Path as _Path
_DEFAULT_ROOT = _Path(__file__).resolve().parents[4]

sys.path.insert(0, str(Path(__file__).parent))
from fixture import Fixture, git, summarize  # noqa: E402

ROOT = Path(_os.environ.get("IACODE_ROOT") or _DEFAULT_ROOT)
NAME = "SETUP-00-CP-0008"


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def seal(f: Fixture, message: str) -> None:
    """Faithful two-commit re-seal of the mutated content."""
    f.reseal(message)


def matrix_row(matrix, prefix):
    for row in matrix["requirements"]:
        if str(row.get("sourceRef", "")).startswith(prefix):
            return row
    raise AssertionError("no row with prefix " + prefix)


def lessons_lines(f: Fixture):
    path = f.path / ".iacode" / "memory" / "lessons.jsonl"
    return path, [json.loads(line) for line in
                  path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_lessons(path: Path, lessons) -> None:
    path.write_text("\n".join(json.dumps(item, ensure_ascii=False) for item in lessons) + "\n",
                    encoding="utf-8", newline="\n")


# ---------------------------------------------------------------------------
# A-Z: the mandatory battery of the sealed CP-0007 Red Team report
# ---------------------------------------------------------------------------

def a_blocker(f):
    state = f.read_json("STATE.json")
    state["blockedBy"] = ["an unresolved blocker planted by the CP-0009 audit"]
    f.write_json("STATE.json", state)
    seal(f, "attack A")
    return f.validator()


def b_red_quality(f):
    quality = f.read_json("QUALITY.json")
    quality["checks"]["unitTests"]["status"] = "FAIL"
    f.write_json("QUALITY.json", quality)
    seal(f, "attack B")
    return f.validator()


def c_denominator(f):
    matrix = f.read_json("REQUIREMENTS-MATRIX.json")
    victim = matrix_row(matrix, "canonical:SETUP-00#1.1")
    matrix["requirements"] = [r for r in matrix["requirements"] if r["id"] != victim["id"]]
    f.write_json("REQUIREMENTS-MATRIX.json", matrix)
    total = len(matrix["requirements"])
    report = f.read_json("COMPLETENESS-REPORT.json")
    report.update({"totalRequirements": total, "expectedRequirements": total,
                   "complete": total, "mandatoryRequirements": total - 1,
                   "coveragePercent": 100.0, "evidenceCoveragePercent": 100.0})
    f.write_json("COMPLETENESS-REPORT.json", report)
    state = f.read_json("STATE.json")
    state["requirementsMatrix"].update({"total": total, "complete": total,
                                        "mandatory": total - 1, "coveragePercent": 100.0})
    f.write_json("STATE.json", state)
    seal(f, "attack C")
    return f.validator()


def d_forged_counts(f):
    report = f.read_json("COMPLETENESS-REPORT.json")
    report["totalRequirements"] = 999
    report["complete"] = 999
    f.write_json("COMPLETENESS-REPORT.json", report)
    seal(f, "attack D")
    return f.validator()


def e_derived_requirement(f):
    matrix = f.read_json("REQUIREMENTS-MATRIX.json")
    victim = matrix_row(matrix, "lesson:")
    matrix["requirements"] = [r for r in matrix["requirements"] if r["id"] != victim["id"]]
    f.write_json("REQUIREMENTS-MATRIX.json", matrix)
    total = len(matrix["requirements"])
    report = f.read_json("COMPLETENESS-REPORT.json")
    report.update({"totalRequirements": total, "expectedRequirements": total,
                   "complete": total, "mandatoryRequirements": total - 1})
    f.write_json("COMPLETENESS-REPORT.json", report)
    state = f.read_json("STATE.json")
    state["requirementsMatrix"].update({"total": total, "complete": total,
                                        "mandatory": total - 1})
    f.write_json("STATE.json", state)
    seal(f, "attack E")
    return f.validator()


def f_documentation_only(f):
    path, lessons = lessons_lines(f)
    for lesson in lessons:
        if lesson["status"] == "GUARDED":
            lesson["prevention"] = [{"kind": "documentation",
                                     "reference": "docs/ENGINEERING-MEMORY.md",
                                     "description": "A written reminder."}]
            break
    write_lessons(path, lessons)
    return f.script("validate_lessons.py")


def g_duplicate_lesson(f):
    path, lessons = lessons_lines(f)
    duplicate = dict(lessons[1])
    duplicate["lessonId"] = lessons[0]["lessonId"]
    write_lessons(path, lessons + [duplicate])
    return f.script("validate_lessons.py")


def h_lesson_secret(f):
    path, lessons = lessons_lines(f)
    lessons[0]["symptom"] = "credential " + "gh" + "p_" + "A" * 36
    write_lessons(path, lessons)
    return f.script("validate_lessons.py")


def i_rewrite_predecessor(f):
    """Rewrite a sealed predecessor, declare it, refresh every hash and move its tag."""
    relative = "docs/checkpoints/SETUP-00-CP-0007/REVIEW-REPORT.md"
    target = f.path / relative
    text = target.read_text(encoding="utf-8")
    target.write_text(text.replace("Verdict: `REWORK_REQUIRED`", "Verdict: `APPROVED`"),
                      encoding="utf-8", newline="\n")
    files = f.read_json("FILES.json")
    files.setdefault("filesModified", []).append(
        {"path": relative, "reason": "rewritten by the audit fixture",
         "hashBefore": "0" * 64, "hashAfter": "0" * 64})
    f.write_json("FILES.json", files)
    content = f.reseal("attack I: rewrite a sealed predecessor and re-seal")
    code, parent = git(f.path, "rev-parse", "HEAD^")
    git(f.path, "tag", "-f", "iacode-checkpoints/SETUP-00-CP-0007", parent)
    return f.validator()


def j_move_tag(f):
    """Move a sealed tag and a HEAD that contains the rewrite, together."""
    relative = "docs/checkpoints/SETUP-00-CP-0006/NEXT.md"
    (f.path / relative).write_text(
        "# Next\n\nrewritten by the CP-0009 audit fixture\n", encoding="utf-8", newline="\n")
    files = f.read_json("FILES.json")
    files.setdefault("filesModified", []).append(
        {"path": relative, "reason": "rewritten by the audit fixture",
         "hashBefore": "0" * 64, "hashAfter": "0" * 64})
    f.write_json("FILES.json", files)
    f.reseal("attack J: move a sealed tag and HEAD together")
    code, parent = git(f.path, "rev-parse", "HEAD^")
    git(f.path, "tag", "-f", "iacode-checkpoints/SETUP-00-CP-0006", parent)
    return f.validator()


def k_remove_inventory_entry(f):
    """Remove an inventory entry after the last legitimate refresh."""
    f.reseal("attack K: re-seal before removing an inventory entry")
    files = f.read_json("FILES.json")
    files["filesCreated"] = files["filesCreated"][1:]
    f.write_json("FILES.json", files)
    f.amend()
    return f.validator()


def l_silent_modification(f):
    """Modify a tracked file without declaring it. The refresh never invents a declaration."""
    target = f.path / "docs" / "ROADMAP.md"
    target.write_text(target.read_text(encoding="utf-8") + "\nsilently appended\n",
                      encoding="utf-8", newline="\n")
    f.reseal("attack L: silently modify a tracked file")
    return f.validator()


def m_wrong_hash_before(f):
    f.reseal("attack M: re-seal before corrupting hashBefore")
    files = f.read_json("FILES.json")
    files["filesModified"][0]["hashBefore"] = "0" * 64
    f.write_json("FILES.json", files)
    f.amend()
    return f.validator()


def n_wrong_hash_after(f):
    f.reseal("attack N: re-seal before corrupting hashAfter")
    files = f.read_json("FILES.json")
    files["filesCreated"][0]["hashAfter"] = "0" * 64
    f.write_json("FILES.json", files)
    f.amend()
    return f.validator()


def o_pass_without_evidence(f):
    quality = f.read_json("QUALITY.json")
    quality["checks"]["staticAnalysis"]["evidence"] = []
    f.write_json("QUALITY.json", quality)
    seal(f, "attack O")
    return f.validator()


def p_unknown_command(f):
    quality = f.read_json("QUALITY.json")
    quality["checks"]["staticAnalysis"]["evidence"] = ["command:cmd-9999"]
    f.write_json("QUALITY.json", quality)
    seal(f, "attack P")
    return f.validator()


def q_second_tool(f):
    state = f.read_json("STATE.json")
    state["secondToolValidation"] = {
        "status": "PASSED", "tool": "Some Other Tool", "provider": "Some Provider",
        "model": "some-model", "validatedAt": "2026-09-20T23:00:00Z",
        "justification": "asserted by the delivery itself", "evidence": []}
    state["status"] = "GATE_PASS"
    f.write_json("STATE.json", state)
    (f.checkpoint / "STATUS.md").write_text("# Status\n\nGATE_PASS\n",
                                            encoding="utf-8", newline="\n")
    seal(f, "attack Q")
    return f.validator()


def r_pass_vocabulary(f):
    state = f.read_json("STATE.json")
    state["status"] = "MILESTONE_EXTERNAL_PASS"
    state["milestone"]["status"] = "PASSED"
    state["milestone"]["auditor"] = "the implementing run itself"
    state["milestone"]["auditedAt"] = "2026-09-20T23:00:00Z"
    state["secondToolValidation"] = {
        "status": "PASSED", "tool": "self", "provider": "self", "model": "self",
        "validatedAt": "2026-09-20T23:00:00Z", "justification": "internal",
        "evidence": ["file:FINAL-REPORT.md"]}
    f.write_json("STATE.json", state)
    (f.checkpoint / "STATUS.md").write_text("# Status\n\nMILESTONE_EXTERNAL_PASS\n",
                                            encoding="utf-8", newline="\n")
    seal(f, "attack R")
    return f.validator()


def s_external_pending_review(f):
    state = f.read_json("STATE.json")
    state["status"] = "MILESTONE_EXTERNAL_PASS"
    state["milestone"]["status"] = "PASSED"
    state["milestone"]["auditor"] = None
    state["milestone"]["auditedAt"] = None
    f.write_json("STATE.json", state)
    (f.checkpoint / "STATUS.md").write_text("# Status\n\nMILESTONE_EXTERNAL_PASS\n",
                                            encoding="utf-8", newline="\n")
    seal(f, "attack S")
    return f.validator()


def t_extraordinary_trigger(f):
    state = f.read_json("STATE.json")
    state["externalAuditRequired"] = True
    state["externalAuditReason"] = "the auditor felt like it"
    f.write_json("STATE.json", state)
    seal(f, "attack T")
    return f.validator()


def u_retired_lesson(f):
    path, lessons = lessons_lines(f)
    for lesson in lessons:
        if lesson["status"] == "GUARDED":
            lesson["status"] = "RETIRED"
            break
    write_lessons(path, lessons)
    seal(f, "attack U")
    return f.validator()


def v_empty_gate_set(f):
    """The original escape was a vacuous PASS from an empty selection.

    The defence is not a non-zero exit: it is that the mandatory set comes from
    policy, so an empty selection still executes every mandatory gate. This check
    therefore reads the cycle the run recorded and refuses a PASS that measured
    less than the canonical set or executed no command.
    """
    policy = f.read_repo_json(".iacode/policies/quality-gates.json")
    mandatory = sorted(g["id"] for g in policy["gates"] if g.get("mandatory"))
    code, out = f.script("green_keeper.py", "--gates", "")
    log = f.checkpoint / "REWORK-LOG.jsonl"
    cycles = [json.loads(line) for line in
              log.read_text(encoding="utf-8").splitlines() if line.strip()]
    last = cycles[-1] if cycles else {}
    measured = sorted(last.get("requiredGates") or [])
    executed = last.get("commandsExecuted") or []
    vacuous = measured != mandatory or not executed
    detail = ("recorded cycle measured " + ",".join(measured) + " against the canonical "
              + ",".join(mandatory) + "; commandsExecuted=" + str(len(executed))
              + "; green_keeper exit=" + str(code))
    # Report it in the harness's reject/accept convention: 1 means the escape was refused.
    return (1 if not vacuous else 0), detail + " | " + summarize(out, 200)


def w_partial_requirement(f):
    matrix = f.read_json("REQUIREMENTS-MATRIX.json")
    matrix["requirements"][0]["status"] = "PARTIAL"
    f.write_json("REQUIREMENTS-MATRIX.json", matrix)
    seal(f, "attack W")
    return f.validator()


def x_command_field(f):
    path = f.checkpoint / "COMMANDS.jsonl"
    records = [json.loads(line) for line in
               path.read_text(encoding="utf-8").splitlines() if line.strip()]
    records[0].pop("runtime", None)
    path.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in records) + "\n",
                    encoding="utf-8", newline="\n")
    seal(f, "attack X")
    return f.validator()


def y_latest_pointer(f):
    (f.path / "docs" / "checkpoints" / "LATEST.md").write_text(
        "# Latest Checkpoint\n\nCheckpoint: `docs/checkpoints/SETUP-00-CP-0005`\n\n"
        "Validate before use.\n", encoding="utf-8", newline="\n")
    seal(f, "attack Y")
    return f.validator("--checkpoint", "docs/checkpoints/SETUP-00-CP-0008")


def z_path_traversal(f):
    return f.script("new_checkpoint.py", "--gate", "../../ESCAPE")


# ---------------------------------------------------------------------------
# AA-AF: the additional attacks of the CP-0007 report
# ---------------------------------------------------------------------------

def aa_aggregate(f):
    state = f.read_json("STATE.json")
    state["requirementsMatrix"]["mandatory"] = 999
    f.write_json("STATE.json", state)
    seal(f, "attack AA")
    return f.validator()


def ab_nonexistent_test(f):
    path, lessons = lessons_lines(f)
    for lesson in lessons:
        if lesson["status"] == "GUARDED":
            lesson["prevention"][0] = {"kind": "test",
                                       "reference": "NoSuchTests.test_nothing",
                                       "description": "A control that does not exist."}
            break
    write_lessons(path, lessons)
    return f.script("validate_lessons.py")


def ac_nonexistent_evidence(f):
    path, lessons = lessons_lines(f)
    lessons[0]["evidence"] = ["file:docs/does-not-exist.md"]
    write_lessons(path, lessons)
    return f.script("validate_lessons.py")


def ad_nested_secret(f):
    """A secret inside the documented detector scope, hidden one level down."""
    path, lessons = lessons_lines(f)
    lessons[0]["prevention"][0]["description"] = "uses " + "gh" + "p_" + "B" * 36
    write_lessons(path, lessons)
    return f.script("validate_lessons.py")


def ae_preflight_gate(f):
    state = f.read_json("STATE.json")
    state["gate"] = "GATE 1"
    state["lessonPreflight"]["gate"] = "GATE 1"
    f.write_json("STATE.json", state)
    seal(f, "attack AE")
    return f.validator()


def af_promotion_invariant(f):
    state = f.read_json("STATE.json")
    state["status"] = "MILESTONE_EXTERNAL_PASS"
    state["greenKeeper"]["status"] = "FAIL"
    state["milestone"]["status"] = "PASSED"
    f.write_json("STATE.json", state)
    (f.checkpoint / "STATUS.md").write_text("# Status\n\nMILESTONE_EXTERNAL_PASS\n",
                                            encoding="utf-8", newline="\n")
    seal(f, "attack AF")
    return f.validator()


# ---------------------------------------------------------------------------
# AG-AT: the surfaces this delivery introduced
# ---------------------------------------------------------------------------

def ag_gate_registry(f):
    policy = f.read_repo_json(".iacode/policies/quality-gates.json")
    policy["gates"] = [g for g in policy["gates"] if g["id"] != "lessons"]
    f.write_repo_json(".iacode/policies/quality-gates.json", policy)
    seal(f, "attack AG")
    return f.validator()


def ah_gate_staleness(f):
    target = f.path / "scripts" / "development-ledger" / "validate_checkpoint.py"
    target.write_text(target.read_text(encoding="utf-8") + "\n# scope changed after the green cycle\n",
                      encoding="utf-8", newline="\n")
    seal(f, "attack AH")
    return f.validator()


def _attestation(f, review_state=None, **overrides):
    """Write a synthetic attestation, in the real schema, and promote with it."""
    state = f.read_json("STATE.json")
    document = {
        "schemaVersion": "1.0.0",
        "auditId": overrides.pop("auditId", "M0-CP-0009-FIXTURE"),
        "milestone": "M0",
        "auditorRole": "milestone independent auditor",
        "tool": "Fixture Tool",
        "provider": "Fixture Provider",
        "model": "fixture-model",
        "subjectCheckpoint": NAME,
        "subjectCommit": f.base,
        "auditCheckpoint": "SETUP-00-CP-0007",
        "auditCommit": "502c554575f717c1d57290e4f4aafa575e41170e",
        "reviewResult": "APPROVED",
        "redTeamResult": "RED_TEAM_PASS",
        "completeness": 100.0,
        "evidenceCoverage": 100.0,
        "testResult": "PASS",
        "createdAt": "2026-09-20T23:30:00Z",
        "notes": "Synthetic attestation created by the CP-0009 audit fixture.",
    }
    document.update(overrides)
    directory = f.path / ".iacode" / "attestations"
    directory.mkdir(parents=True, exist_ok=True)
    relative = ".iacode/attestations/" + document["auditId"] + ".json"
    (f.path / relative).write_text(json.dumps(document, indent=2) + "\n",
                                   encoding="utf-8", newline="\n")
    f.declare_created(relative, "Synthetic attestation planted by the audit fixture.")
    state["status"] = "MILESTONE_EXTERNAL_PASS"
    state["milestone"]["status"] = "PASSED"
    state["milestone"]["auditor"] = document["tool"]
    state["milestone"]["auditedAt"] = document["createdAt"]
    state["secondToolValidation"] = {
        "status": "PASSED", "tool": document["tool"], "provider": document["provider"],
        "model": document["model"], "validatedAt": document["createdAt"],
        "justification": "derived from the attestation", "evidence": ["file:" + relative]}
    state["externalAttestation"] = {
        "status": "VERIFIED", "path": relative, "auditId": document["auditId"],
        "evidence": ["file:" + relative]}
    state["independentReview"] = review_state or {
        "status": "APPROVED", "tool": document["tool"],
        "reviewedAt": document["createdAt"], "justification": "fixture",
        "evidence": ["file:" + relative]}
    state["redTeam"] = {
        "status": "RED_TEAM_PASS", "tool": document["tool"],
        "executedAt": document["createdAt"], "justification": "fixture",
        "evidence": ["file:" + relative]}
    f.write_json("STATE.json", state)
    (f.checkpoint / "STATUS.md").write_text("# Status\n\nMILESTONE_EXTERNAL_PASS\n",
                                            encoding="utf-8", newline="\n")
    handoff = f.checkpoint / "HANDOFF.md"
    handoff.write_text(handoff.read_text(encoding="utf-8").replace(
        "Current Status: READY_FOR_REVIEW", "Current Status: MILESTONE_EXTERNAL_PASS"),
        encoding="utf-8", newline="\n")
    seal(f, "attestation fixture " + document["auditId"])
    if document.get("subjectCommit") == f.base and "subjectCommit" not in overrides:
        # The re-seal moved the tag, so an honest attestation binds the commit the tag
        # now names. Rewriting it here is what a real auditor would record.
        code, head = git(f.path, "rev-parse", "HEAD")
        document["subjectCommit"] = head
        (f.path / relative).write_text(json.dumps(document, indent=2) + "\n",
                                       encoding="utf-8", newline="\n")
        f.refresh_inventory()
        f.amend()
    return f.validator()


def ai_self_audit(f):
    return _attestation(f, auditCheckpoint=NAME, auditCommit=f.base)


def aj_failed_review(f):
    return _attestation(f, reviewVerdict="REWORK_REQUIRED")


def ak_wrong_commit(f):
    return _attestation(f, subjectCommit="0" * 40)


def au_copied_attestation(f):
    """An attestation whose subject is a different checkpoint, reused verbatim."""
    return _attestation(f, subjectCheckpoint="SETUP-00-CP-0006")


def av_red_team_fail(f):
    return _attestation(f, redTeamResult="RED_TEAM_FAIL")


def aw_incomplete_audit(f):
    return _attestation(f, completeness=93.2, evidenceCoverage=100.0)


def ax_unsealed_audit_checkpoint(f):
    """The attesting checkpoint exists but is neither sealed nor in the integrity chain."""
    unsealed = f.path / "docs" / "checkpoints" / "SETUP-00-CP-0050"
    unsealed.mkdir(parents=True, exist_ok=True)
    (unsealed / "STATUS.md").write_text("# Status\n\nIN_PROGRESS\n",
                                        encoding="utf-8", newline="\n")
    f.declare_created("docs/checkpoints/SETUP-00-CP-0050/STATUS.md",
                      "Unsealed checkpoint planted by the audit fixture.")
    return _attestation(f, auditCheckpoint="SETUP-00-CP-0050", auditCommit=None)


def ay_missing_auditor_role(f):
    return _attestation(f, auditorRole="")


def az_failed_test_result(f):
    return _attestation(f, testResult="FAIL")


def positive_attestation(f):
    """Positive control: a structurally legitimate external PASS must be ACCEPTED.

    A control that refuses every input, including the true one, is not a control.
    """
    return _attestation(f)


def al_forged_count(f):
    counts = f.read_json("COUNTS.json")
    counts["counts"]["TESTS"]["numerator"] = 999
    counts["counts"]["TESTS"]["denominator"] = 999
    f.write_json("COUNTS.json", counts)
    seal(f, "attack AL")
    return f.validator()


def am_count_contradiction(f):
    report = f.checkpoint / "FINAL-REPORT.md"
    report.write_text(report.read_text(encoding="utf-8")
                      + "\n- Tests: 999/999 TESTS recorded by this audit fixture.\n",
                      encoding="utf-8", newline="\n")
    seal(f, "attack AM")
    return f.validator()


def an_open_finding(f):
    closure = f.read_json("CP7-FINDINGS-CLOSURE.json")
    closure["findings"][0]["status"] = "OPEN"
    f.write_json("CP7-FINDINGS-CLOSURE.json", closure)
    seal(f, "attack AN")
    return f.validator()


def ao_red_team_false_pass(f):
    report = f.read_json("M0-INTERNAL-RED-TEAM.json")
    report["attacks"][0]["result"] = "ESCAPED"
    f.write_json("M0-INTERNAL-RED-TEAM.json", report)
    seal(f, "attack AO")
    return f.validator()


def ap_mirror_false_pass(f):
    report = f.read_json("M0-INTERNAL-MIRROR.json")
    report["checks"][0]["result"] = "FAIL"
    f.write_json("M0-INTERNAL-MIRROR.json", report)
    seal(f, "attack AP")
    return f.validator()


def aq_guardrail_test(f):
    registry = f.read_repo_json(".iacode/memory/guardrails/registry.json")
    registry["guardrails"][0]["verifiedBy"] = ["NoSuchTests.test_nothing"]
    f.write_repo_json(".iacode/memory/guardrails/registry.json", registry)
    return f.script("validate_lessons.py")


def ar_anchor_link(f):
    chain = f.read_repo_json(".iacode/anchors/checkpoint-chain.json")
    chain["anchors"][3]["previousAnchorHash"] = "0" * 64
    f.write_repo_json(".iacode/anchors/checkpoint-chain.json", chain)
    return f.script("verify_integrity.py")


def as_input_binding(f):
    path = f.checkpoint / "COMMANDS.jsonl"
    records = [json.loads(line) for line in
               path.read_text(encoding="utf-8").splitlines() if line.strip()]
    for record in records:
        record.pop("inputsDigest", None)
    path.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in records) + "\n",
                    encoding="utf-8", newline="\n")
    seal(f, "attack AS")
    return f.validator()


def at_seal_chronology(f):
    path = f.checkpoint / "COMMANDS.jsonl"
    records = [json.loads(line) for line in
               path.read_text(encoding="utf-8").splitlines() if line.strip()]
    records = [r for r in records if r.get("operation") != "post-commit-validation"]
    path.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in records) + "\n",
                    encoding="utf-8", newline="\n")
    seal(f, "attack AT")
    return f.validator()


BATTERY = [
    ("A", "readiness and blocker invariant", "Add a blocker to a READY_FOR_REVIEW checkpoint", a_blocker, True),
    ("B", "mandatory quality", "Set a review-ready quality dimension red", b_red_quality, True),
    ("C", "completeness denominator", "Delete a canonical requirement and recompute every count", c_denominator, True),
    ("D", "completeness claims", "Forge the stored counts of a passing report", d_forged_counts, True),
    ("E", "lesson-derived requirement", "Remove a lesson-derived requirement from the matrix", e_derived_requirement, True),
    ("F", "GUARDED semantics", "Replace a preventive control with documentation only", f_documentation_only, True),
    ("G", "lesson identity", "Duplicate a lesson identifier", g_duplicate_lesson, True),
    ("H", "lesson secret handling", "Insert a secret-shaped value into a scanned field", h_lesson_secret, True),
    ("I", "sealed predecessor", "Rewrite a sealed predecessor, refresh hashes and move its tag", i_rewrite_predecessor, True),
    ("J", "tag immutability", "Move a checkpoint tag and HEAD together", j_move_tag, True),
    ("K", "file inventory", "Remove one inventory entry", k_remove_inventory_entry, True),
    ("L", "file inventory", "Silently modify a tracked file", l_silent_modification, True),
    ("M", "file inventory", "Set a wrong hashBefore", m_wrong_hash_before, True),
    ("N", "file inventory", "Set a wrong hashAfter", n_wrong_hash_after, True),
    ("O", "quality evidence", "Claim PASS with no evidence", o_pass_without_evidence, True),
    ("P", "evidence resolution", "Reference an unknown command", p_unknown_command, True),
    ("Q", "second-tool evidence", "Supply complete attribution with empty evidence", q_second_tool, True),
    ("R", "pass vocabulary", "Promote an internally authored result to an external status", r_pass_vocabulary, True),
    ("S", "external milestone review", "Leave review and Red Team pending with a null auditor", s_external_pending_review, True),
    ("T", "extraordinary cadence", "Request an audit without a known trigger", t_extraordinary_trigger, True),
    ("U", "preflight freshness", "Retire a canonical lesson but keep the active preflight", u_retired_lesson, True),
    ("V", "Green Keeper mandatory set", "Run the Green Keeper with an empty gate selection", v_empty_gate_set, True),
    ("W", "partial completeness", "Claim PASS with a PARTIAL requirement", w_partial_requirement, True),
    ("X", "command audit", "Remove a required field from a command record", x_command_field, True),
    ("Y", "latest pointer", "Point LATEST.md at an older checkpoint", y_latest_pointer, True),
    ("Z", "path safety", "Use path traversal as the Gate identifier", z_path_traversal, True),
    ("AA", "aggregate consistency", "Contradict the matrix in the recorded state aggregate", aa_aggregate, False),
    ("AB", "control resolution", "Point a GUARDED lesson at a nonexistent test", ab_nonexistent_test, False),
    ("AC", "evidence resolution", "Point lesson evidence at a nonexistent file", ac_nonexistent_evidence, False),
    ("AD", "nested secret scan", "Hide a secret-shaped value inside prevention.description", ad_nested_secret, False),
    ("AE", "preflight gate binding", "Reuse a SETUP-00 preflight for another Gate", ae_preflight_gate, False),
    ("AF", "promotion invariant", "External status with a red Green Keeper", af_promotion_invariant, False),
    ("AG", "gate registry", "Remove a mandatory gate from the policy after a green cycle", ag_gate_registry, False),
    ("AH", "gate staleness", "Edit the assurance scope after the last green cycle", ah_gate_staleness, False),
    ("AI", "external attestation", "Attest the subject with the subject's own checkpoint", ai_self_audit, False),
    ("AJ", "external attestation", "Claim an external PASS over a failed review", aj_failed_review, False),
    ("AK", "external attestation", "Attest a different commit than the one promoted", ak_wrong_commit, False),
    ("AL", "derived counts", "Forge a stored derived count", al_forged_count, False),
    ("AM", "count consistency", "State a contradicting count in Markdown", am_count_contradiction, False),
    ("AN", "findings closure", "Offer the delivery with an audit finding still open", an_open_finding, False),
    ("AO", "internal Red Team", "Keep a PASS verdict while an attack escaped", ao_red_team_false_pass, False),
    ("AP", "internal mirror audit", "Keep a PASS verdict while a mirror check failed", ap_mirror_false_pass, False),
    ("AQ", "guardrail registry", "Verify a guardrail with a test that does not exist", aq_guardrail_test, False),
    ("AR", "integrity anchors", "Break the link between two anchors", ar_anchor_link, False),
    ("AS", "command replay context", "Remove the content binding of recorded inputs", as_input_binding, False),
    ("AT", "seal chronology", "Remove the post-commit validation of the sealed content", at_seal_chronology, False),
    ("AU", "external attestation", "Reuse an attestation written for another checkpoint", au_copied_attestation, False),
    ("AV", "external attestation", "Claim an external PASS over a failed Red Team", av_red_team_fail, False),
    ("AW", "external attestation", "Claim an external PASS over an incomplete audit", aw_incomplete_audit, False),
    ("AX", "external attestation", "Attest from a checkpoint that is unsealed and unanchored", ax_unsealed_audit_checkpoint, False),
    ("AY", "external attestation", "Attest with no auditor role recorded", ay_missing_auditor_role, False),
    ("AZ", "external attestation", "Claim an external PASS over a failed test result", az_failed_test_result, False),
]

# The positive control is evaluated with the opposite expectation.
POSITIVE = [
    ("POS-EXT", "external attestation", "A structurally legitimate external PASS",
     positive_attestation),
]


def main() -> int:
    only = {item.strip().upper() for item in sys.argv[2:] if item.strip()} if len(sys.argv) > 2 else set()
    workdir = Path(sys.argv[1])
    workdir.mkdir(parents=True, exist_ok=True)
    fixture = Fixture(ROOT, NAME, workdir)
    code, out = fixture.validator()
    if code != 0:
        print("FIXTURE_INVALID")
        print(out)
        return 3
    results = []
    for attack_id, target, mutation, run, mandatory in BATTERY:
        if only and attack_id not in only:
            continue
        fixture.reset()
        try:
            exit_code, output = run(fixture)
            defended = exit_code != 0
            observed = "exit=" + str(exit_code) + " " + summarize(output)
        except Exception as exc:  # a broken attack is itself a finding
            defended, observed = False, "attack tooling error: " + repr(exc)
        results.append({"attackId": attack_id, "target": target, "mutation": mutation,
                        "mandatory": mandatory, "expected": "reject",
                        "observed": observed,
                        "result": "DEFENDED" if defended else "ESCAPED"})
        print("[" + attack_id + "] " + results[-1]["result"] + " " + observed[:220])
    for control_id, target, mutation, run in POSITIVE:
        if only and control_id not in only:
            continue
        fixture.reset()
        try:
            exit_code, output = run(fixture)
            accepted = exit_code == 0
            observed = "exit=" + str(exit_code) + " " + summarize(output, 1200)
        except Exception as exc:
            accepted, observed = False, "control tooling error: " + repr(exc)
        results.append({"attackId": control_id, "target": target, "mutation": mutation,
                        "mandatory": True, "expected": "accept", "observed": observed,
                        "result": "ACCEPTED" if accepted else "REFUSED"})
        print("[" + control_id + "] " + results[-1]["result"] + " " + observed[:1200])
    fixture.reset()
    (workdir / "attack-results.json").write_text(
        json.dumps(results, indent=2) + "\n", encoding="utf-8", newline="\n")
    escaped = [r for r in results if r["result"] in ("ESCAPED", "REFUSED")]
    print("TOTAL=" + str(len(results)) + " DEFENDED=" + str(len(results) - len(escaped))
          + " ESCAPED=" + str(len(escaped)))
    return 0 if not escaped else 1


if __name__ == "__main__":
    sys.exit(main())
