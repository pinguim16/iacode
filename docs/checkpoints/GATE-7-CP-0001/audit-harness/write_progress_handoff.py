"""Render only current unsealed progress through the existing complete canonical renderer."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from assemble_final_handoff import render_handoff

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))


def main() -> int:
    from ledger_common import load_json, use_utf8_stdout

    use_utf8_stdout()
    state = load_json(CHECKPOINT / "STATE.json")
    if state["status"] != "IN_PROGRESS" or state["gate"] != "GATE-7":
        raise ValueError("progress rendering cannot rewrite terminal or other Gate content")
    if (
        subprocess.run(
            ["git", "rev-parse", "--verify", "refs/tags/iacode-checkpoints/" + CHECKPOINT.name],
            cwd=ROOT,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        ).returncode
        == 0
    ):
        raise ValueError("never rewrite a sealed checkpoint")
    action = state["nextAllowedAction"]
    if not isinstance(action, str) or len(action.strip()) < 40:
        raise ValueError("a substantive current action is required")
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    sections = {
        "## Objective": "Finish only authorized Gate7, every internal control and canonical "
        "READY_FOR_REVIEW sealing. Preserve the later independent M2 audit boundary.",
        "## What was completed": "Core Knowledge Engine and local causal rework. Actual0211 "
        "passes10 native controls,0213 all152 owning cases,0214 explicit helper quality,0215 "
        "whole lint and0217 two final-strict uninstrumented native installation/trust/removal "
        "runs. These scopes overlap and never substitute for whole current acceptance.",
        "## What was NOT completed": "A new complete immutable runtime-v4 execution, whole "
        "ordered assurance and actual canonical seal remain due. Independent review/Red Team "
        "PENDING, second-tool PENDING_MANUAL, M2 PENDING, attestation NONE; Gate8 unauthorized.",
        "## Current repository state": "Branch "
        + state["branch"]
        + "; observed HEAD "
        + head
        + "; checkpoint remains unsealed IN_PROGRESS. STATE and canonical Git observations "
        "are authoritative, never a predicted future commit or tag.",
        "## Files changed": "FILES.json must explicitly declare every current Gate7 delta "
        "before canonical finalization binds its hashes. Original failed attempts and inert "
        "native/continuation contexts are retained before consumers or cleanup.",
        "## Important decisions": "ADR0053/0054 govern exact rights-qualified cited projections; "
        "0055 reserves but does not implement Gate8;0056-0059 govern fixtures and exact "
        "transport. ADR0060 keeps physical ownership/deadlines and bounded red native facts. "
        "Use canonical renderers, not unstructured replacement summaries.",
        "## Tests executed": "See COMMANDS.jsonl and exact suite receipts for0211/0213/0214/0215/"
        "0217. Full preflight225/derivation226 keep all150 applicable lessons/all198 requirements, "
        "197 mandatory. Actual native source does not widen any deadline or terminate outsiders.",
        "## Known failures": "Runtime-v1/v2/v3 remain FAIL with immutable tags and exact "
        "originals. V3 cmd0180 is48/49, only native red. G7-INT-028 awaits fresh detailed attackT. "
        "Actual continuation refusal0223 and causal0227 remain;034 is repaired only through "
        "current structural controls and unchanged canonical validation.",
        "## Known risks": "Historical Windows teardown internals remain unknown and residual "
        "kernel/cleanup failure stays red. Curator/DB/clock, lexical relevance and backup limits "
        "remain in RISKS. Four excluded historical temporary targets remain manual-owner only.",
        "## Do not repeat": "No one-time archival/import replay, historical PID/session reuse, "
        "tag movement, history rewrite, source changes during immutable proof, overlapping "
        "ledger writers, global Docker/WSL restart or stopping unrelated applications.",
        "## Required next action": action,
        "## Exact continuation sequence": "Complete current local structural rework; regenerate "
        "full memory/preflight/requirements, documentation links, FILES and quiescent validation. "
        "Publish/tag a new unused runtime-v4, run one whole49-stage public proof, then all "
        "ordered internal controls and canonical READY_FOR_REVIEW sealing/exact transport.",
        "## Validation commands": "python scripts/development-ledger/validate_checkpoint.py; "
        "python scripts/development-ledger/validate_lessons.py; python "
        "scripts/development-ledger/verify_integrity.py. Finalizer/sealer self-record; never "
        "outer-wrap them. Program state is generated explicitly after actual Git boundaries.",
        "## Stop conditions": "Stop for unexpected Git divergence, genuine unavailable external "
        "prerequisites or missing authority. Internal red requires retained causal correction "
        "and fresh complete assurance; never waivers or independent self-attestation.",
    }
    (CHECKPOINT / "HANDOFF.md").write_text(render_handoff(sections), encoding="utf-8", newline="\n")
    (CHECKPOINT / "NEXT.md").write_text(
        "# Next\n\n## Required next action\n\n" + action + "\n", encoding="utf-8", newline="\n"
    )
    print("CANONICAL_PROGRESS_CONTINUATION_RENDERED; no acceptance or independent verdict")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
