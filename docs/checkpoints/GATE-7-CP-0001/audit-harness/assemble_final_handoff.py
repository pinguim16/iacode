"""Assemble actual Gate7 internal evidence without predicting its seal or M2 audit verdict."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))


def clean(text: str) -> str:
    return " ".join(text.split())


def render_handoff(sections: dict[str, str]) -> str:
    from validate_checkpoint import HANDOFF_HEADINGS

    if set(sections) != set(HANDOFF_HEADINGS):
        raise ValueError("the exact complete canonical handoff section set is required")
    if any(len(value.strip()) < 20 for value in sections.values()):
        raise ValueError("every handoff section needs substantive observed content")
    return (
        "# Handoff\n\nCurrent Gate: GATE-7\nCurrent Status: IN_PROGRESS\n\n"
        + "\n\n".join(heading + "\n\n" + sections[heading] for heading in HANDOFF_HEADINGS)
        + "\n"
    )


def render_final_report(sections: dict[str, str]) -> str:
    from validate_checkpoint import FINAL_REPORT_HEADINGS

    if set(sections) != set(FINAL_REPORT_HEADINGS):
        raise ValueError("the complete canonical final-report section set is required")
    if any(not isinstance(value, str) or len(value.strip()) < 20 for value in sections.values()):
        raise ValueError("every canonical final-report section needs substantive content")
    return (
        "# Gate 7 internal delivery report\n\n"
        + "\n\n".join(heading + "\n\n" + sections[heading] for heading in FINAL_REPORT_HEADINGS)
        + "\n"
    )


def evidence() -> tuple[dict, dict]:
    from complete_functional_acceptance import current_execution
    from delivery_assurance import completeness_scope
    from ledger_common import load_json, scope_fingerprint

    current_execution()
    state = load_json(CHECKPOINT / "STATE.json")
    if (
        state["independentReview"]["status"] != "PENDING"
        or state["redTeam"]["status"] != "PENDING"
        or state["secondToolValidation"]["status"] != "PENDING_MANUAL"
        or state["milestone"]["status"] != "PENDING"
        or state["externalAttestation"]["status"] != "NONE"
    ):
        raise ValueError("this implementing assembly must never grant M2 independence")
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
    if (
        functional.get("result") != "PASS"
        or verification["result"] != "PASS"
        or verification["fast"] is not False
        or any(row["result"] != "PASS" for row in verification["stages"])
        or publication["result"] != "PASS"
        or publication["invocationCount"] != 1
        or publication["retryCount"] != 0
        or not publication["temporaryCloneRemoved"]
        or not publication["ownedComposeProjectRemoved"]
        or not publication["sharedProjectUnchanged"]
        or not publication["gitStateAfterVerificationClean"]
        or scenarios["scenarios"]["knowledge-engine-e2e.json"]["sourceFingerprint"] != fingerprint
        or complete["result"] != "PASS"
        or complete["coveragePercent"] != 100.0
        or complete["evidenceCoveragePercent"] != 100.0
        or complete["scopeFingerprint"]
        != scope_fingerprint(ROOT, completeness_scope(ROOT, CHECKPOINT))
        or complete["complete"] != len(matrix["requirements"])
        or any(row["status"] != "COMPLETE" for row in matrix["requirements"])
        or state["greenKeeper"]["status"] != "PASS"
        or state["greenKeeper"]["remainingFailures"]
        or state["greenKeeper"]["unresolvedReworkItems"]
        or attacks["result"] != "RED_TEAM_PASS"
        or attacks["targetFingerprint"] != fingerprint
        or attacks["baselineControl"]["result"] != "VALID"
        or attacks["escaped"]
        or mirror["result"] != "PASS"
        or mirror["targetFingerprint"] != fingerprint
        or mirror["failed"]
        or not any(row["id"] == "MIR-017" and row["result"] == "PASS" for row in mirror["checks"])
        or any(row["status"] != "PASS" for row in quality["checks"].values())
        or any(
            row["status"] != "CLOSED" for row in load_json(CHECKPOINT / "FINDINGS.json")["findings"]
        )
    ):
        raise ValueError("all current complete unchanged internal evidence must actually pass")
    steps = load_json(CHECKPOINT / "STEPS.json")
    if next(row for row in steps["steps"] if row["stepId"] == "G7-S02")["status"] != "COMPLETE":
        raise ValueError("the actual ordered assurance step must be complete first")
    return state, {
        "verification": verification,
        "publication": publication,
        "functional": functional,
        "complete": complete,
        "attacks": attacks,
        "mirror": mirror,
        "fingerprint": fingerprint,
    }


def commands() -> list[dict]:
    return [
        json.loads(line)
        for line in (CHECKPOINT / "COMMANDS.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def main() -> int:
    from ledger_common import use_utf8_stdout

    use_utf8_stdout()
    from ledger_common import load_json, utc_now, write_json
    from sync_in_progress_metadata import synchronize

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--complete-handoff-step", action="store_true")
    args = parser.parse_args()
    state, facts = evidence()
    if args.complete_handoff_step:
        if not (CHECKPOINT / "FINAL-REPORT.md").is_file():
            raise ValueError("actual final report assembly is required")
        validations = [
            row
            for row in commands()
            if row.get("exitCode") == 0
            and "audit-harness/run_checkpoint_validation.py" in row["command"]
        ]
        if not validations:
            raise ValueError("actual quiescent preseal metadata validation is required")
        validation = validations[-1]
        from datetime import datetime

        if (
            datetime.fromisoformat(validation["timestamp"].replace("Z", "+00:00")).timestamp()
            < (CHECKPOINT / "FINAL-REPORT.md").stat().st_mtime
        ):
            raise ValueError("the actual validation must follow this final report, not precede it")
        steps = load_json(CHECKPOINT / "STEPS.json")
        step = next(row for row in steps["steps"] if row["stepId"] == "G7-S03")
        if step["status"] != "IN_PROGRESS":
            raise ValueError("handoff completion is not replayable")
        step.update(
            {
                "status": "COMPLETE",
                "functionalProof": "Actual final internal report, counters, explicit inventory, "
                "provenance/risks "
                "and complete canonical handoff are assembled. Subsequent quiescent "
                "checkpoint validation "
                + validation["id"]
                + " passes. This completes preseal assembly, not a claim that a future content "
                "commit, canonical seal or publication already happened.",
                "evidence": [
                    validation["id"],
                    "FINAL-REPORT.md",
                    "COUNTS.json",
                    "FILES.json",
                    "HANDOFF.md",
                    "RISKS.md",
                    "PROVENANCE.json",
                ],
            }
        )
        write_json(CHECKPOINT / "STEPS.json", steps)
        synchronize(ROOT, CHECKPOINT)
        print(
            "PRESEAL_HANDOFF_ASSEMBLY_COMPLETE; canonical finalization/content commit/"
            "seal/publication remain actual subsequent operations"
        )
        return 0
    if (CHECKPOINT / "FINAL-REPORT.md").exists():
        raise ValueError("preserve an existing final assembly before another attempt")
    counts = load_json(CHECKPOINT / "COUNTS.json")["counts"]
    ratios = "; ".join(
        f"{name}={value['numerator']}/{value['denominator']}"
        for name, value in sorted(counts.items())
    )
    summary = (
        f"One complete immutable non-fast invocation passes all "
        f"{len(facts['verification']['stages'])} mandatory stages at "
        f"{facts['publication']['subjectTag']} / {facts['publication']['publishedCommit']}. "
        f"Functional acceptance covers {len(facts['functional']['required'])} canonical criteria. "
        f"Whole Green Keeper passes all {len(state['greenKeeper']['requiredGates'])} gates; "
        f"completeness resolves {facts['complete']['totalRequirements']} requirements at "
        "100 percent implementation/evidence coverage. Fresh same-session internal Red Team "
        f"defends {facts['attacks']['defended']}/{facts['attacks']['total']} with VALID control. "
        f"The full clean-clone mirror evaluates {facts['mirror']['total']} dimensions: "
        f"{facts['mirror']['passed']} PASS, {facts['mirror']['notApplicable']} derived "
        f"NOT_APPLICABLE, {facts['mirror']['failed']} FAIL. No independent M2 approval is implied."
    )
    action = clean("""
        Complete any canonical Gate7 READY_FOR_REVIEW finalization, content commit, real seal,
        publication and exact immutable review/archive transport not already evidenced by the
        canonical tag and tool records. Once sealed, never rewrite this subject. A later separate
        independent M2 checkpoint must audit sealed Gates4-7, including independent Red Team,
        G4-F-004 reconstruction and functional proof; second-tool validation remains manual.
        Findings return to a new implementing checkpoint. Gate8 is not authorized.
    """)
    report = render_final_report(
        {
            "## Status": clean("""
            All internal controls below are actual observations. This is a preseal assembly:
            canonical tool records and the final tag, not this prose, establish READY_FOR_REVIEW
            and actual sealing. Independent M2 review, Red Team and second-tool approval remain due.
        """),
            "## Environment": clean("""
            Windows/PowerShell, actual Python and supported explicit Node, pinned owning-image
            toolchains and Docker. Real PostgreSQL, source files, provider, sandbox, quality,
            native editor and HTTP acceptance use owned isolated resources. Current exact
            producer/isolation reports establish observed cleanup and preserved unrelated states.
        """),
            "## Tool / Model / Effort": clean("""
            Codex/OpenAI implementing session. RUN-METADATA.json does not attest an exact runtime
            model or effort. Separate internal role artifacts are not independent sessions or
            cross-tool validation. No unobserved cost or token figure is invented.
        """),
            "## Deliverables": clean("""
            Governed deterministic cited lexical knowledge over explicitly reviewed, project and
            content-bound curated grants. Default admission is empty/denied. Storage-only
            experiences remain ineligible for RAG; training/distillation stay denied. Real atomic
            PostgreSQL inverted indexing, authenticated scoped APIs, exact citations, invalidation,
            immutable retries, original retention ceilings and owned finite purge are implemented.
            ADR-0053/0054 record the structural decisions; no graph/training/Gate8 scope is added.
        """),
            "## Files Created": clean("""
            FILES.json explicitly declares every new Gate7 contract/domain, actual SQL/API/source
            adapter, migration, corpus, tests, ADR/runbook and checkpoint evidence before binding.
            Exact safe original producer bytes, failed candidates and causal diagnostic logs remain
            in attempts and suite-attempts; original failures are not rewritten as successful runs.
        """),
            "## Files Modified": clean("""
            FILES.json owns the complete Gate7-only delta against sealed Gate6. Inherited controls
            are strengthened without removing mandatory gates, assertions, lineage or history.
            Every sealed predecessor and immutable candidate tag remains unchanged.
        """),
            "## Validation": summary + "\n\nMeasured source fingerprint: " + facts["fingerprint"],
            "## Tests": (
                "Canonical distinct counters: " + ratios + ". "
                "Repeated executions are not additional cases. The e2e category records an actual "
                "owned scenario, not one test per observation or per verifier stage. "
                "Complete mandatory "
                "suite process results and the canonical collection guards "
                "support the derived counts."
            ),
            "## Red Team": clean("""
            The fresh internal battery runs only after whole Green Keeper and audit-only
            completeness. All inherited mandatory attacks remain, with new domain, actual source,
            SQL and live knowledge adversaries and a valid positive/null control. Exact originals
            precede fallible interpretation. This is not independent Red Team or M2 attestation.
        """),
            "## Known Risks": clean("""
            RISKS.md retains provider/Engine/Windows availability, trusted local curator/DB/clock,
            structural rather than legal rights verification, lexical ranking limits and backup/
            restore limits. Primary purge is not proof of every backup's erasure. Four historical
            policy-refused temporary targets remain responsible-owner manual cleanup only.
        """),
            "## Remaining Work": clean("""
            Actual terminal finalization/content commit/seal/publication/transport are subsequent
            operations to this preseal assembly; consult their real records and canonical tag to
            determine completion, never infer them here. Independent accumulated M2 audit and
            second-tool validation remain pending. No Gate8 work is authorized.
        """),
            "## Handoff Readiness": clean("""
            Internal evidence is complete with no external blocker. The only offered delivery
            verdict is READY_FOR_REVIEW through canonical finalization and actual seal. Independent
            review/Red Team remain PENDING, second-tool PENDING_MANUAL, M2 PENDING and external
            attestation NONE. Same-session assurance never becomes independent approval.
        """),
            "## Next Gate": clean("""
            Gate7 closes implementation of M2, not its independent audit.
            Await the later independent
            audit of the sealed subject and explicit authority before any milestone boundary or
            Gate8 advancement. Do not rewrite a sealed subject to make it approved.
        """),
            "## Evidence": clean("""
            [Full verifier](VERIFY.json), [immutable clone](PUBLISHED-CLEAN-CLONE-REPORT.json),
            [functional acceptance](FUNCTIONAL-ACCEPTANCE-VALIDATION.json),
            [completeness](COMPLETENESS-REPORT.json),
            [internal Red Team](M2-INTERNAL-RED-TEAM.json),
            [full mirror](M2-INTERNAL-MIRROR.json), [ledger](COMMANDS.jsonl),
            [M2 consolidation](../M2-CONSOLIDATION.md), [risks](RISKS.md),
            [provenance](PROVENANCE.json), [findings](FINDINGS.json).
            The canonical sealer/tag separately establish committed-content sealing.
        """),
        }
    )
    (CHECKPOINT / "FINAL-REPORT.md").write_text(report, encoding="utf-8", newline="\n")
    sections = {
        "## Objective": clean("""
            Finish only authorized Gate7 Knowledge Engine, every internal control and actual
            canonical seal. Deliver M2 for later independent audit, without Gate8 advancement.
        """),
        "## What was completed": summary,
        "## What was NOT completed": clean("""
            Independent M2 review, independent Red Team, G4-F-004 reconstruction/functional proof
            and second-tool validation have not occurred. This preseal report does not certify
            future terminal tool operations; consult the actual canonical tag and transport proof.
        """),
        "## Current repository state": (
            "Branch "
            + state["branch"]
            + "; runtime subject "
            + facts["publication"]["publishedCommit"]
            + "; predecessor "
            + state["baseCommit"]
            + ". STATE and the canonical checkpoint tag bind actual terminal Git state."
        ),
        "## Files changed": clean("""
            FILES.json explicitly declares the complete Gate7 delta before hashes are bound.
            Exact original producer bytes and failed attempts remain. No sealed predecessor,
            immutable tag, denominator or promotion rule is rewritten.
        """),
        "## Important decisions": clean("""
            ADR-0053 requires explicit exact content-bound source grants; storage is not RAG.
            ADR-0054 defines rebuildable exact cited projections and nonrenewing lifecycle facts.
            ADR-0037 separates internal assurance from later independent milestone validation.
        """),
        "## Tests executed": summary + " Canonical distinct counters: " + ratios + ".",
        "## Known failures": clean("""
            FINDINGS.json retains every observed failure, recurrence and causal repair with
            actual evidence. Earlier full and local failures remain failed history, never
            combined with partial reruns to manufacture the current complete verification.
        """),
        "## Known risks": clean("""
            RISKS.md records external availability and Windows file holders, trusted curator/DB/
            clock, rights/privacy/ranking/backup limits and four historical policy-refused
            temporary targets. Those targets remain manual-owner cleanup; no retry is authorized.
        """),
        "## Do not repeat": clean("""
            Never run checkpoint writers after sealing or overlap writers. Await actual process
            exits, not ledger success markers. No tag movement, history rewrite, force push,
            narrowed checks, global Docker restart/prune or stopping unrelated applications.
        """),
        "## Required next action": action,
        "## Exact continuation sequence": clean("""
            If the canonical Gate7 tag is absent, validate the quiescent assembly, finalize
            READY_FOR_REVIEW with its future canonical tag reference, commit/publish Gate7-only
            content, run the self-recording canonical sealer, publish its evidence commit/tag and
            verify fresh exact public Git/archive transport. If sealed, perform read-only
            verification only. A later separate independent M2 audit must precede advancement.
        """),
        "## Validation commands": clean("""
            python scripts/development-ledger/validate_checkpoint.py;
            python scripts/development-ledger/validate_lessons.py;
            python scripts/development-ledger/verify_integrity.py;
            python scripts/development-ledger/review_bundle.py --verify-declaration.
            Canonical finalizer/sealer self-record; do not outer-wrap either.
        """),
        "## Stop conditions": clean("""
            Stop for unexpected Git divergence or genuine missing external prerequisites/authority.
            Internal red results require retained causal rework and fresh complete assurance, not
            waivers. No independent self-attestation, milestone-boundary crossing
            or Gate8 authority.
        """),
    }
    (CHECKPOINT / "HANDOFF.md").write_text(render_handoff(sections), encoding="utf-8", newline="\n")
    (CHECKPOINT / "NEXT.md").write_text(
        "# Next\n\n## Required next action\n\n" + action + "\n", encoding="utf-8", newline="\n"
    )
    (CHECKPOINT / "PROGRESS.md").write_text(
        "# Gate 7 progress\n\n"
        + summary
        + "\n\nCanonical counters: "
        + ratios
        + ".\n\nActual sealing/publication is determined only by canonical records and the tag. "
        "Independent M2 validation remains pending; Gate8 is not authorized.\n",
        encoding="utf-8",
        newline="\n",
    )
    state["nextAllowedAction"], state["updatedAt"], state["dirty"] = action, utc_now(), True
    write_json(CHECKPOINT / "STATE.json", state)
    decisions = CHECKPOINT / "DECISIONS.md"
    decisions.write_text(
        decisions.read_text(encoding="utf-8")
        + "\n- Final preseal assembly derives from actual complete current internal evidence. "
        "It predicts neither its own content commit, seal nor publication. "
        "All independent M2 statuses remain pending and Gate8 remains unauthorized.\n",
        encoding="utf-8",
        newline="\n",
    )
    synchronize(ROOT, CHECKPOINT)
    print("GATE7_INTERNAL_HANDOFF_ASSEMBLED; actual canonical terminal operations remain")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
