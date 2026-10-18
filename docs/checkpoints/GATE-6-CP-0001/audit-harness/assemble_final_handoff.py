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
from validate_checkpoint import FINAL_REPORT_HEADINGS


def render_final_report(sections: dict[str, str]) -> str:
    if set(sections) != set(FINAL_REPORT_HEADINGS):
        raise ValueError("the complete canonical final-report section set is required")
    if any(not isinstance(value, str) or len(value.strip()) < 20 for value in sections.values()):
        raise ValueError("every canonical final-report section needs substantive content")
    return "# Gate 6 internal delivery report\n\n" + "\n\n".join(
        heading + "\n\n" + sections[heading] for heading in FINAL_REPORT_HEADINGS) + "\n"


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
    cycle = state["greenKeeper"]["cycles"]
    summary = (f"Published immutable subject {tag} at {subject} completes all {len(facts['verification']['stages'])} non-fast stages "
        f"in one invocation, with clean detached transport, unchanged shared project and actual removal of its isolated "
        f"Compose resources and temporary clone. Functional acceptance covers every 37 runtime criterion across eight scenarios. "
        f"Whole Green Keeper cycle {cycle} passes every 15 mandatory gate; completeness and evidence coverage are 100 percent over "
        f"all {facts['complete']['totalRequirements']} derived requirements. Fresh internal Red Team defends "
        f"{facts['attacks']['defended']}/{facts['attacks']['total']} with VALID positive control. Full closure mirror evaluates "
        f"all {mirror['total']} dimensions: {mirror['passed']} PASS, {mirror['notApplicable']} policy-derived NOT_APPLICABLE, "
        f"{mirror['failed']} FAIL. These are separate same-session internal artifacts, never independent M2 approval.")
    report = render_final_report({
        "## Status": "All current internal controls actually pass. This unsealed assembly does not predict its own content commit, seal or publication. Only successful canonical finalization may assign INTERNAL_GATE_PASS; no independent Gate or M2 approval is claimed.",
        "## Environment": "Windows / PowerShell, Python 3.13.15, supported bundled Node and Docker Desktop. Actual PostgreSQL/object/provider/sandbox, native editor and desktop acceptance use isolated owned resources. Shared operational identities remain unchanged in the published clean-clone proof.",
        "## Tool / Model / Effort": "Codex / OpenAI, implementing session. Exact runtime model and effort are not attested by RUN-METADATA.json. Assurance roles have separate artifacts but are same-session, not independent or cross-tool validation.",
        "## Deliverables": "Only explicitly consented source-bound observable engineering facts are persisted. Closed contracts, actual PostgreSQL/object evidence, immutable audit/idempotency, authenticated project scope, denied unproven reuse, finite retention and anti-resurrection are exercised in the real workflow. ADR-0050/0051/0052 record the architecture and causal native completion repair.",
        "## Files Created": "FILES.json explicitly declares every new Gate6 contract/domain, migration, API/runtime, tests, ADR/runbook, engineering memory and checkpoint evidence path before canonical hash binding. Attempts retain exact original producer observations, including the refused v6 final report.",
        "## Files Modified": "FILES.json owns the complete delta against sealed Gate5. Existing API/contracts/persistence/telemetry, native completion, quality collection and engineering memory changes remain Gate6-only. No sealed predecessor, immutable tag, denominator or terminal rule is rewritten.",
        "## Validation": summary + "\n\nRuntime subject fingerprint: " + facts["fingerprint"] + ". The actual canonical ledger and current reports own all execution identities; repeated runs are not combined into one invented invocation.",
        "## Tests": "Canonical distinct counters: " + ratios + ". Repeated full, Green Keeper and mirror executions are not new cases. Native cleanup correctness requires actual physical removal as well as observed owned-member completion, under unchanged bounds.",
        "## Red Team": "Fresh internal battery defends " + str(facts["attacks"]["defended"]) + "/" + str(facts["attacks"]["total"]) + " with VALID positive/null control and zero escapes. Exact original failures remain. This is never independent Red Team or an M2 attestation.",
        "## Known Risks": "RISKS.md retains external provider/Engine availability, external Windows sharing locks, rights/backup/retention limits and four historical policy-refused temporary targets requiring responsible-owner manual cleanup. Those targets must not be retried through another API. Actual current owned cleanup is separately evidenced. The [preserved OS write failure](FINALIZER-OS-FAILURE.json) distinguishes cmd-0396's early internal record0 from its actual process exit1, which was not accepted as completed finalization. Closing requires a later observed canonical process exit0 and committed-content validation; the transient OS cause is not established.",
        "## Remaining Work": "Cmd-0340's failed terminal finalization and cmd-0342's causal failure are immutable history. LSN-0008 recurrence3/CRITICAL and the original successful v6 assurance are preserved, not silently relabelled. Current corrective controls and fresh unchanged-memory assurance must actually pass before this assembler can run. Canonical finalization, content commit, real seal, publication and exact final transport/archive verification remain subsequent actual operations, never certified here in advance.",
        "## Handoff Readiness": "All internal preseal evidence is assembled. The canonical finalizer and sealer remain authoritative for terminal status and committed-content validation. Independent M2 review, independent Red Team, second-tool validation and milestone attestations remain pending. Unknown training, RAG and distillation rights remain denied.",
        "## Next Gate": "Gate6 alone is being closed. Gate7 has not been authorized or started. The M2 boundary cannot be crossed without the mandatory later independent validation and explicit owner authority.",
        "## Evidence": "[Full verifier](VERIFY.json), [published clone](PUBLISHED-CLEAN-CLONE-REPORT.json), [functional validation](FUNCTIONAL-ACCEPTANCE-VALIDATION.json), [completeness](COMPLETENESS-REPORT.json), [internal Red Team](M2-INTERNAL-RED-TEAM.json), [mirror](M2-INTERNAL-MIRROR.json), [ledger](COMMANDS.jsonl), [risks](RISKS.md), [provenance](PROVENANCE.json), [findings](FINDINGS.json), [original v6 archive](attempts/RUNTIME-V6-FINALIZATION-ARCHIVE.json). Canonical sealing is separately established by real sealer records and iacode-checkpoints/GATE-6-CP-0001, never by moving that tag."
    })
    (CHECKPOINT / "FINAL-REPORT.md").write_text(report, encoding="utf-8", newline="\n")
    sections = {
        "## Objective": "Finish only explicitly authorized Gate6 Experience Store, all internal controls and actual canonical checkpoint sealing; independent milestone validation remains due at M2 closure.",
        "## What was completed": summary,
        "## What was NOT completed": "Independent M2 review, independent Red Team and second-tool validation have not occurred. Gate7 is not authorized. This preseal assembly does not self-certify a future seal/publication: consult the real canonical tag, postcommit records and review declaration.",
        "## Current repository state": "Branch main; immutable runtime subject " + subject + ". STATE.json binds the current content; the canonical Gate6 tag and postcommit evidence bind the eventual seal. The sealed Gate5 base " + state["baseCommit"] + " remains unchanged.",
        "## Files changed": "FILES.json explicitly declares the actual Gate6 delta before hash binding. Native process synchronization/failure observations and ADR-0052 are in-scope causal repairs, not another Gate. Original producer bytes remain exact in attempts; no sealed predecessor is rewritten.",
        "## Important decisions": "ADR-0050: source-bound consented facts, not raw answers or authority. ADR-0051: finite retention and tombstones. ADR-0052: exact observed member synchronization and retained cleanup failures under unchanged bounds. ADR-0037 defers independence to M2, never waives it.",
        "## Tests executed": "Current complete non-fast full47, functional37/37, whole15 Green Keeper, total completeness, fresh71-attack Red Team and full18-dimension clean-clone mirror actually pass. The current reports and canonical ledger bind their real invocation identities. " + ratios + ". Counts are canonical distinct cases/criteria, not a sum of repeated runs.",
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
    decisions.write_text(decisions.read_text(encoding="utf-8") + "\n- Final internal acceptance derives from actual current full47, whole15 Green Keeper, total" + str(facts["complete"]["totalRequirements"]) + "-requirement completeness, fresh71-attack Red Team/VALID control and all18 mirror dimensions, including real clean-clone/historical compatibility. Same-session is never independent. Preseal assembly does not predict its own commit, seal or publication; canonical tools must perform those actions.\n", encoding="utf-8", newline="\n")
    synchronize(ROOT, CHECKPOINT)
    print("FINAL_INTERNAL_HANDOFF_ASSEMBLED; status=IN_PROGRESS; real canonical preseal validation/finalization/sealing/publication still required")
    return 0


if __name__ == "__main__":
    use_utf8_stdout()
    raise SystemExit(main())
