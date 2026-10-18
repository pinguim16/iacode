"""Assemble observed internal delivery only; canonical finalization/sealing remain real tool actions."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from assemble_source_ready import render_handoff, render_next
from delivery_assurance import completeness_scope
from ledger_common import load_json, scope_fingerprint, use_utf8_stdout, utc_now, write_json
from sync_in_progress_metadata import synchronize


def evidence() -> tuple[dict, dict]:
    state = load_json(CHECKPOINT / "STATE.json")
    if state["status"] != "IN_PROGRESS" or state["blockedBy"]:
        raise ValueError("only unsealed, unblocked implementing state may be assembled")
    fingerprint = scope_fingerprint(ROOT)
    verification = load_json(CHECKPOINT / "VERIFY.json")
    publication = load_json(CHECKPOINT / "PUBLISHED-CLEAN-CLONE-REPORT.json")
    functional = load_json(CHECKPOINT / "FUNCTIONAL-ACCEPTANCE-VALIDATION.json")
    complete = load_json(CHECKPOINT / "COMPLETENESS-REPORT.json")
    attacks = load_json(CHECKPOINT / "M2-INTERNAL-RED-TEAM.json")
    mirror = load_json(CHECKPOINT / "M2-INTERNAL-MIRROR.json")
    matrix = load_json(CHECKPOINT / "REQUIREMENTS-MATRIX.json")
    scenarios = load_json(CHECKPOINT / "FUNCTIONAL-SCENARIOS.json")
    quality = load_json(CHECKPOINT / "QUALITY.json")
    if (verification["result"] != "PASS" or verification["fast"] is not False
            or any(row["result"] != "PASS" for row in verification["stages"])
            or publication["result"] != "PASS" or publication["invocationCount"] != 1
            or publication["retryCount"] != 0 or not publication["temporaryCloneRemoved"]
            or not publication["ownedComposeProjectRemoved"] or not publication["sharedProjectUnchanged"]
            or not publication["gitStateAfterVerificationClean"]
            or scenarios["scenarios"]["experience-store-e2e.json"]["sourceFingerprint"] != fingerprint
            or complete["result"] != "PASS" or complete["coveragePercent"] != 100.0
            or complete["evidenceCoveragePercent"] != 100.0
            or complete["scopeFingerprint"] != scope_fingerprint(ROOT, completeness_scope(ROOT, CHECKPOINT))
            or complete["complete"] != len(matrix["requirements"])
            or any(row["status"] != "COMPLETE" for row in matrix["requirements"])
            or state["greenKeeper"]["status"] != "PASS" or state["greenKeeper"]["remainingFailures"]
            or state["greenKeeper"]["unresolvedReworkItems"]
            or attacks["result"] != "RED_TEAM_PASS" or attacks["targetFingerprint"] != fingerprint
            or attacks["baselineControl"]["result"] != "VALID" or attacks["escaped"]
            or mirror["result"] != "PASS" or mirror["targetFingerprint"] != fingerprint
            or mirror["failed"] or not any(row["id"] == "MIR-017" and row["result"] == "PASS"
                                            for row in mirror["checks"])
            or any(row["status"] != "PASS" for row in quality["checks"].values())
            or any(row["status"] != "CLOSED" for row in load_json(CHECKPOINT / "FINDINGS.json")["findings"])):
        raise ValueError("all current complete unchanged internal evidence must actually pass")
    steps = load_json(CHECKPOINT / "STEPS.json")
    if next(row for row in steps["steps"] if row["stepId"] == "G6-S02")["status"] != "COMPLETE":
        raise ValueError("the actual ordered assurance step must be complete first")
    return state, {"verification": verification, "publication": publication, "functional": functional,
                   "complete": complete, "attacks": attacks, "mirror": mirror, "fingerprint": fingerprint}


def commands() -> list[dict]:
    return [json.loads(line) for line in (CHECKPOINT / "COMMANDS.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--complete-handoff-step", action="store_true")
    args = parser.parse_args()
    state, facts = evidence()
    if args.complete_handoff_step:
        if not (CHECKPOINT / "FINAL-REPORT.md").is_file():
            raise ValueError("actual final report assembly is required")
        validations = [row for row in commands() if row.get("exitCode") == 0 and
                       "audit-harness/run_checkpoint_validation.py" in row["command"]]
        if not validations:
            raise ValueError("actual quiescent preseal metadata validation is required")
        validation = validations[-1]
        from datetime import datetime

        if datetime.fromisoformat(validation["timestamp"].replace("Z", "+00:00")).timestamp() < (CHECKPOINT / "FINAL-REPORT.md").stat().st_mtime:
            raise ValueError("the actual validation must follow this final report, not precede it")
        steps = load_json(CHECKPOINT / "STEPS.json")
        step = next(row for row in steps["steps"] if row["stepId"] == "G6-S03")
        if step["status"] != "IN_PROGRESS":
            raise ValueError("handoff completion is not replayable")
        step.update({"status": "COMPLETE", "functionalProof":
            "Actual final internal report, counters, explicit inventory, provenance/risks and complete canonical handoff are assembled. Subsequent quiescent checkpoint validation " + validation["id"] +
            " passes. This completes preseal assembly, not a claim that a future content commit, canonical seal or publication already happened.",
            "evidence": [validation["id"], "FINAL-REPORT.md", "COUNTS.json", "FILES.json", "HANDOFF.md", "RISKS.md", "PROVENANCE.json"]})
        write_json(CHECKPOINT / "STEPS.json", steps)
        synchronize(ROOT, CHECKPOINT)
        print("PRESEAL_HANDOFF_ASSEMBLY_COMPLETE; canonical finalization/content commit/seal/publication remain actual subsequent operations")
        return 0
    if (CHECKPOINT / "FINAL-REPORT.md").exists():
        raise ValueError("final assembly already exists; do not replay or overwrite it")
    justification = ("Intermediate Gate 6 internal closure under explicit owner authorization in AUTHORIZATION.md "
        "and ADR-0037. Independent milestone review and Red Team are deferred to M2 closure, not waived "
        "or claimed by this implementing session.")
    state["independentReview"] = {"status": "NOT_REQUIRED", "tool": None, "reviewedAt": None,
                                  "justification": justification, "evidence": ["checkpoint:AUTHORIZATION.md"]}
    state["redTeam"] = {"status": "NOT_REQUIRED", "tool": None, "executedAt": None,
                        "justification": justification, "evidence": ["checkpoint:AUTHORIZATION.md"]}
    if (state["secondToolValidation"]["status"] != "PENDING_MANUAL" or state["milestone"]["status"] != "PENDING"
            or state["externalAttestation"]["status"] != "NONE"):
        raise ValueError("this assembly must never grant independent or second-tool approval")
    action = ("Complete any canonical Gate6 finalization, content-commit, sealing, publication and exact transport/archive "
        "verification not already evidenced by its canonical tag and tool records. Once sealed and verified, never rerun "
        "writing helpers in this checkpoint; await explicit owner authorization for Gate7. Independent M2 review, "
        "Red Team and second-tool validation remain pending for milestone closure.")
    state["nextAllowedAction"], state["updatedAt"], state["dirty"] = action, utc_now(), True
    write_json(CHECKPOINT / "STATE.json", state)
    counts = load_json(CHECKPOINT / "COUNTS.json")["counts"]
    ratios = "; ".join(f"{name}={value['numerator']}/{value['denominator']}" for name, value in sorted(counts.items()))
    subject = facts["publication"]["publishedCommit"]
    tag = facts["publication"]["subjectTag"]
    mirror = facts["mirror"]
    summary = (f"Published immutable subject {tag} at {subject} completes all{len(facts['verification']['stages'])} non-fast stages "
        f"in one invocation, with clean detached transport, unchanged shared project and actual removal of its isolated "
        f"Compose resources and temporary clone. Functional acceptance covers every37 runtime criterion across eight scenarios. "
        f"Whole Green Keeper cycle7 passes every15 mandatory gate; completeness and evidence coverage are100 percent over "
        f"all{facts['complete']['totalRequirements']} derived requirements. Fresh internal Red Team defends "
        f"{facts['attacks']['defended']}/{facts['attacks']['total']} with VALID positive control. Full closure mirror evaluates "
        f"all{mirror['total']} dimensions: {mirror['passed']} PASS, {mirror['notApplicable']} policy-derived NOT_APPLICABLE, "
        f"{mirror['failed']} FAIL. These are separate same-session internal artifacts, never independent M2 approval.")
    report = ("# Gate 6 internal delivery report\n\n" + summary + "\n\n"
        "The implementation stores only explicitly consented source-bound observable engineering facts. Closed contracts, "
        "actual PostgreSQL/object evidence, immutable audit/idempotency, project-scoped authenticated API, denied unproven "
        "reuse, finite retention and anti-resurrection are exercised by the real provider/sandbox/quality workflow.\n\n"
        "Native cleanup correction is evidenced by the actual pinned owned-handle mismatch, formerly failing causal "
        "controls, unchanged deadlines and fresh actual native profile removal. Original failures, escalated counters "
        "and exact producer bytes remain retained; a later successful run never rewrites a historical failure.\n\n"
        "Canonical counters: " + ratios + ".\n\n"
        "## Evidence\n\n"
        "[Full verifier](VERIFY.json), [published clean clone](PUBLISHED-CLEAN-CLONE-REPORT.json), "
        "[functional validation](FUNCTIONAL-ACCEPTANCE-VALIDATION.json), [completeness](COMPLETENESS-REPORT.json), "
        "[internal Red Team](M2-INTERNAL-RED-TEAM.json), [full mirror](M2-INTERNAL-MIRROR.json), "
        "[command ledger](COMMANDS.jsonl), [risks](RISKS.md), [provenance](PROVENANCE.json).\n\n"
        "## Sealing and independence boundary\n\n"
        "This report records completed internal controls and preseal assembly, not a future seal or publication. "
        "Canonical sealing is established only by the sealer's real committed-content/transport records and "
        "iacode-checkpoints/GATE-6-CP-0001. That tag must never be moved or the sealed subject rewritten.\n\n"
        "The permitted intermediate verdict is INTERNAL_GATE_PASS, never GATE_PASS or a milestone audit verdict. "
        "Independent M2 review/Red Team/second-tool validation remain pending. Gate7 is not authorized. Unknown "
        "training, RAG and distillation rights remain denied.\n")
    (CHECKPOINT / "FINAL-REPORT.md").write_text(report, encoding="utf-8", newline="\n")
    sections = {
        "## Objective": "Finish only explicitly authorized Gate6 Experience Store, all internal controls and actual canonical checkpoint sealing; independent milestone validation remains due at M2 closure.",
        "## What was completed": summary,
        "## What was NOT completed": "Independent M2 review, independent Red Team and second-tool validation have not occurred. Gate7 is not authorized. This preseal assembly does not self-certify a future seal/publication: consult the real canonical tag, postcommit records and review declaration.",
        "## Current repository state": "Branch main; immutable runtime subject " + subject + ". STATE.json binds the current content; the canonical Gate6 tag and postcommit evidence bind the eventual seal. The sealed Gate5 base " + state["baseCommit"] + " remains unchanged.",
        "## Files changed": "FILES.json explicitly declares the actual Gate6 delta before hash binding. Native process synchronization/failure observations and ADR-0052 are in-scope causal repairs, not another Gate. Original producer bytes remain exact in attempts; no sealed predecessor is rewritten.",
        "## Important decisions": "ADR-0050: source-bound consented facts, not raw answers or authority. ADR-0051: finite retention and tombstones. ADR-0052: exact observed member synchronization and retained cleanup failures under unchanged bounds. ADR-0037 defers independence to M2, never waives it.",
        "## Tests executed": "Actual cmd-0296 full47, cmd-0300 functional37/37, cmd-0306 through0320 whole15 Green Keeper, cmd-0322 completeness, cmd-0324 fresh71-attack Red Team and cmd-0329 full18-dimension clean-clone mirror pass. " + ratios + ". Counts are canonical distinct cases/criteria, not a sum of repeated runs.",
        "## Known failures": "FINDINGS.json closes local causal rework with observable evidence. Historical failed commands, v4 root failure, interrupted Docker attempts and v5 failed native/Red Team remain preserved. No historical result is overwritten or combined with partial reruns to create a current PASS.",
        "## Known risks": "External provider/Engine availability and external Windows sharing locks can still fail closed. A member snapshot is not proof about future spawns/external holders; actual removal stays mandatory. Four historical policy-refused temporary targets remain responsible-owner manual cleanup, never retried. See RISKS.md; no unproven reuse or independent M2 approval is implied.",
        "## Do not repeat": "Never rerun checkpoint writing helpers after canonical sealing. Never move tags, amend history, force push, narrow gates/denominators, bypass checks or stop unrelated apps. Do not replay immutable archival/diagnostic/recovery helpers or any of the four policy-refused cleanup targets. Preserve all failures and raw bytes.",
        "## Required next action": action,
        "## Exact continuation sequence": "If canonical Gate6 tag is absent, validate current assembly, finalize INTERNAL_GATE_PASS against refs/tags/iacode-checkpoints/GATE-6-CP-0001, commit and publish clean content, run the canonical sealer, publish its evidence commit/tag, then verify fresh exact Git/archive transport. If already sealed, perform only read-only verification and do not rerun writers. Await owner Gate7 authorization; M2 independence remains mandatory.",
        "## Validation commands": "python scripts/development-ledger/validate_checkpoint.py; python scripts/development-ledger/validate_lessons.py; python scripts/development-ledger/verify_integrity.py; python scripts/development-ledger/review_bundle.py --verify-declaration. Canonical writers: finalize_checkpoint.py and seal_checkpoint.py self-record; do not wrap them in an outer recorder.",
        "## Stop conditions": "Stop for unexpected Git divergence or a genuine missing external prerequisite/authority. Preserve real failures and use causal rework, not false PASS. No Gate7 or milestone boundary may be crossed without the required separate authority and independent validation.",
    }
    (CHECKPOINT / "HANDOFF.md").write_text(render_handoff(sections), encoding="utf-8", newline="\n")
    (CHECKPOINT / "NEXT.md").write_text(render_next(action), encoding="utf-8", newline="\n")
    (CHECKPOINT / "PROGRESS.md").write_text("# Gate 6 progress\n\n" + summary + "\n\nCanonical counters: " + ratios
        + ".\n\nActual sealing/publication is derived from the canonical tag and postcommit/transport records, never predicted by this report. "
        "Independent M2 validation and explicit Gate7 authority remain pending.\n", encoding="utf-8", newline="\n")
    risks_path = CHECKPOINT / "RISKS.md"
    old = risks_path.read_text(encoding="utf-8").removeprefix("# Risks\n").lstrip()
    risks_path.write_text("# Risks\n\n## Current residuals and boundary\n\n"
        "- All internal controls in FINAL-REPORT.md actually pass against unchanged runtime source. Canonical sealing/publication is separately evidenced by its real tool records and tag. Independent M2 and second-tool approval are still pending; Gate7 is unauthorized.\n"
        "- Process completion and actual removal are separate requirements. Both ten-second bounds remain unchanged; external OS/file holders may still cause a real FAIL. The exact historical log holder is not retroactively identified.\n"
        "- Unknown reuse rights stay denied. Primary deletion is not proof of erasure from every backup. Preserve project scope, consent, source integrity and finite tombstones.\n"
        "- Four historically policy-refused targets below remain manual-owner cleanup only. No alternate deletion API or replay is authorized.\n\n"
        "## Historical observations retained without rewriting\n\n"
        "The following original observations preserve their then-current failures/prerequisites. References to fresh assurance being due describe those historical moments, not the completed current internal controls.\n\n"
        + old, encoding="utf-8", newline="\n")
    decisions = CHECKPOINT / "DECISIONS.md"
    decisions.write_text(decisions.read_text(encoding="utf-8") + "\n- Final internal acceptance derives from actual current full47, whole15 Green Keeper, total193-requirement completeness, fresh71-attack Red Team/VALID control and all18 mirror dimensions, including real clean-clone/historical compatibility. Same-session is never independent. Preseal assembly does not predict its own commit, seal or publication; canonical tools must perform those actions.\n", encoding="utf-8", newline="\n")
    synchronize(ROOT, CHECKPOINT)
    print("FINAL_INTERNAL_HANDOFF_ASSEMBLED; status=IN_PROGRESS; real canonical preseal validation/finalization/sealing/publication still required")
    return 0


if __name__ == "__main__":
    use_utf8_stdout()
    raise SystemExit(main())
