#!/usr/bin/env python3
"""Resolve LSN-0040's GUARDRAIL_FAILURE by naming the checkpoint that repaired GRD-0042.

`record_guardrail_failure.py` reopened the lesson when `M1-F-003` was recorded. The control is now
repaired in this checkpoint: the validator asks whether a published reference reaches every commit
sealed evidence names, every clone that judges sealed history is a published clone, and the tests
that fail without that are registered. The memory's rule is that a guardrail failure is resolved
only by naming the checkpoint that repaired the control, which is the one way a reopened lesson
returns to `GUARDED`; the escalated severity stays.

    python resolve_guardrail_failure.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "development-ledger"))

from ledger_common import utc_now, write_json  # noqa: E402
from lessons import guardrail_registry_path, load_lessons, save_lessons  # noqa: E402

LESSON = "LSN-0040"
GUARDRAIL = "GRD-0042"

NEW_TESTS = (
    ("test_the_validator_refuses_a_record_naming_an_unpublished_commit",
     "A record naming a commit no published reference reaches is refused, as a local object in "
     "the repository that holds it and as an absent object in a published clone; the same record "
     "passes once a published reference reaches the commit."),
    ("test_every_preserved_reference_is_what_makes_its_checkpoint_valid",
     "On the real sealed history, removing each refs/tags/iacode-preserved/ reference makes the "
     "checkpoint that names its commit invalid in the repository and in a published clone."),
    ("test_a_published_clone_carries_only_what_a_published_reference_reaches",
     "A published clone does not carry an unreachable object that a copy of the object store "
     "does."),
    ("test_every_clone_in_the_tooling_and_the_suite_is_a_published_clone",
     "A syntax-tree scan refuses any git clone in the tooling or the suite that is not a "
     "transport clone."),
    ("test_a_preserved_reference_missing_from_the_remote_fails_unnamed",
     "remote_sync.py refuses a local preserved or checkpoint tag that is not on the remote."),
)


def main() -> int:
    lessons = load_lessons(ROOT)
    index = next(i for i, item in enumerate(lessons) if item.get("lessonId") == LESSON)
    lesson = lessons[index]
    failures = lesson.get("guardrailFailures") or []
    open_failures = [item for item in failures if not item.get("resolvedIn")]
    if not open_failures:
        print(f"{LESSON} has no unresolved guardrail failure; nothing to do")
        return 0
    for item in open_failures:
        item["resolvedIn"] = CHECKPOINT.name
    prevention = list(lesson.get("prevention") or [])
    named = {control.get("reference") for control in prevention}
    additions = [{
        "kind": "validator",
        "reference": "scripts/development-ledger/validate_checkpoint.py",
        "description": ("Every commit a checkpoint's evidence names must be reachable from a "
                        "published reference (a branch, a tag or a remote-tracking branch); an "
                        "object that exists only in the local store is refused, for every schema "
                        "version (ADR-0028)."),
    }] + [{"kind": "test", "reference": name, "description": description}
          for name, description in NEW_TESTS]
    for control in additions:
        if control["kind"] == "validator" and any(
                item.get("kind") == "validator" and item.get("reference") == control["reference"]
                for item in prevention):
            continue
        if control["reference"] not in named or control["kind"] == "validator":
            prevention.append(control)
    lesson["prevention"] = prevention
    evidence = list(lesson.get("evidence") or [])
    for reference in ("file:docs/checkpoints/GATE-3-CP-0002/REVIEW-REPORT.md",
                      "file:docs/adr/ADR-0028-sealed-evidence-is-judged-from-the-published-history.md",
                      "file:scripts/development-ledger/ledger_common.py",
                      "file:tests/test_gate3_sandbox.py"):
        if reference not in evidence:
            evidence.append(reference)
    lesson["evidence"] = evidence
    lesson["applicability"]["requiredCheck"] = (
        "Confirm that every sealed predecessor this Gate anchors validates from a detached checkout "
        "of its own tag in a published clone (Git's transport, never a copy of the local object "
        "store), that every commit sealed evidence names is reachable from a published reference, "
        "and that no command this Gate records declares an input the repository does not carry.")
    lesson["applicability"]["requiredEvidence"] = (
        "A validation run against each anchored checkpoint from its tag in a published clone, "
        "green, and a clone of the remote that validates every sealed checkpoint of the milestone.")
    lesson["status"] = "GUARDED"
    lesson["updatedAt"] = utc_now()
    lesson["notes"] = (
        "The residual limit is honest: a control over sealed history cannot run before the history "
        "is sealed, so the first execution is always one Gate late, and 'published' is judged "
        "locally from the branches and tags this repository holds. remote_sync.py closes the gap "
        "between a local tag and the remote. M1-F-003 showed the earlier form of the control "
        "could not tell a local object from a published one; that distinction is now the rule.")
    lessons[index] = lesson
    save_lessons(ROOT, lessons)

    path = guardrail_registry_path(ROOT)
    registry = json.loads(path.read_text(encoding="utf-8"))
    entry = next(item for item in registry["guardrails"] if item["guardrailId"] == GUARDRAIL)
    entry["title"] = ("Every anchored checkpoint validates from its own tag in a clone of the "
                      "published history")
    for name, _description in NEW_TESTS:
        if name not in entry["verifiedBy"]:
            entry["verifiedBy"].append(name)
    entry["removingItWouldAllow"] = (
        "A sealed checkpoint to stop validating from its own tag, or to validate only on the "
        "machine whose object store still holds a commit no published reference reaches, without "
        "anything noticing until a clone of the remote is verified (M1-F-003).")
    write_json(path, registry)
    print(f"{LESSON}: {len(open_failures)} guardrail failure(s) resolved in {CHECKPOINT.name}; "
          f"status {lesson['status']}, severity {lesson['severity']}; {GUARDRAIL} verified by "
          f"{len(entry['verifiedBy'])} test(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
