#!/usr/bin/env python3
"""Record and resolve the GRD-0042 failure exposed after anchoring GATE-3-CP-0003."""

from __future__ import annotations

import argparse
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

LESSON = "LSN-0040"
GUARDRAIL = "GRD-0042"
TEST = "test_a_preserved_commit_maps_to_the_checkpoint_whose_evidence_names_it"
MARKER = "GATE-3-CP-0005 preserved-checkpoint association"
DETAIL = (
    "GUARDRAIL_FAILURE: GATE-3-CP-0005 anchored GATE-3-CP-0003, whose tag-creation command "
    "mentions the preserved SETUP-00 commit only as an argument. GRD-0042's load-bearing-reference "
    "test selected a checkpoint by raw SHA substring, associated the commit with GATE-3-CP-0003 "
    "instead of SETUP-00-CP-0009, and therefore expected the wrong checkpoint to fail. The Git "
    "property and validator were correct; the guardrail could no longer identify its subject."
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=("record", "resolve"), required=True)
    args = parser.parse_args()
    lessons = load_lessons(ROOT)
    index = next(i for i, item in enumerate(lessons) if item.get("lessonId") == LESSON)
    item = lessons[index]

    if args.phase == "record":
        if not any(MARKER in str(failure.get("detail"))
                   for failure in item.get("guardrailFailures") or []):
            item = register_recurrence(item, CHECKPOINT.name, f"{MARKER}: {DETAIL}")
            lessons[index] = item
            save_lessons(ROOT, lessons)
        print(f"{LESSON} status={item['status']} recurrenceCount={item['recurrenceCount']} "
              f"openFailures={sum(not f.get('resolvedIn') for f in item['guardrailFailures'])}")
        return 0

    failures = item.get("guardrailFailures") or []
    open_failures = [failure for failure in failures
                     if MARKER in str(failure.get("detail")) and not failure.get("resolvedIn")]
    if not open_failures:
        raise RuntimeError(f"{LESSON} has no open {MARKER!r} failure")
    for failure in open_failures:
        failure["resolvedIn"] = CHECKPOINT.name
    item["status"] = "GUARDED"
    item["updatedAt"] = utc_now()
    if not any(control.get("reference") == TEST for control in item["prevention"]):
        item["prevention"].append({
            "kind": "test",
            "reference": TEST,
            "description": (
                "Every preserved commit is associated only with a checkpoint whose canonical "
                "command evidence fields name it; a SHA appearing merely in an argument cannot "
                "capture the guardrail's subject."
            ),
        })
    evidence = list(item.get("evidence") or [])
    for reference in (
        "file:docs/checkpoints/GATE-3-CP-0005/PRESERVED-REFERENCE-PROBE.json",
        "file:tests/test_gate3_sandbox.py",
    ):
        if reference not in evidence:
            evidence.append(reference)
    item["evidence"] = evidence
    item["notes"] = (
        (item.get("notes") or "").rstrip()
        + " The GATE-3-CP-0005 recurrence was in subject selection: checkpoint_naming now reads "
          "exactly the evidence fields the validator judges, and a regression test prevents a SHA "
          "used only as a tag argument from capturing the association."
    )
    lessons[index] = item
    save_lessons(ROOT, lessons)

    path = guardrail_registry_path(ROOT)
    registry = json.loads(path.read_text(encoding="utf-8"))
    entry = next(row for row in registry["guardrails"] if row["guardrailId"] == GUARDRAIL)
    if TEST not in entry["verifiedBy"]:
        entry["verifiedBy"].append(TEST)
    write_json(path, registry)
    print(f"{LESSON} status={item['status']} resolved={len(open_failures)} "
          f"{GUARDRAIL}Tests={len(entry['verifiedBy'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
