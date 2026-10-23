"""Archive exact failed mutable projections before an explicitly newer complete verification."""

from __future__ import annotations

import argparse
import hashlib
import json
import re

from acceptance_evidence import CHECKPOINT, current_greenkeeper, current_publication
from audit_runner_bridge import regular
from ledger_common import load_json, utc_now, write_json

NAMES = (
    "VERIFY.json",
    "PUBLISHED-CLEAN-CLONE-REPORT.json",
    "COMPOSE-ISOLATION-AUDIT.json",
    "FUNCTIONAL-SCENARIOS.json",
    "PRODUCER-REPORTS.json",
)


def checked_archive(version):
    if re.fullmatch(r"[1-9][0-9]*", version) is None:
        raise ValueError("NUMERIC_IMMUTABLE_SUBJECT_VERSION_REQUIRED")
    folder = CHECKPOINT / "attempts" / ("RUNTIME-V" + version + "-DERIVED-VIEWS")
    if folder.resolve() != folder or any(
        path.is_symlink() or path.is_junction() for path in (folder, *folder.parents)
    ):
        raise ValueError("UNREDIRECTED_EXACT_ARCHIVE_REQUIRED")
    return folder


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("archive", "retire"))
    parser.add_argument("--version", required=True)
    args = parser.parse_args()
    folder = checked_archive(args.version)
    manifest = folder / "MANIFEST.json"
    if args.action == "archive":
        originals = {}
        for name in NAMES:
            path = CHECKPOINT / name
            regular(path, CHECKPOINT)
            originals[name] = path.read_bytes()
        publication = json.loads(originals["PUBLISHED-CLEAN-CLONE-REPORT.json"])
        expected_tag = "iacode-subjects/GATE-7-CP-0003-runtime-v" + args.version
        if publication["subjectTag"] != expected_tag or publication["result"] != "FAIL":
            raise ValueError("EXACT_FAILED_OLD_FULL_EXECUTION_REQUIRED")
        if folder.exists():
            raise ValueError("DO_NOT_REPLACE_OR_RECREATE_A_PRIOR_ARCHIVE")
        folder.mkdir()
        for name, raw in originals.items():
            with (folder / name).open("xb") as stream:
                stream.write(raw)
            if (folder / name).read_bytes() != raw:
                raise ValueError("ARCHIVED_ORIGINAL_BYTES_CHANGED")
        write_json(
            manifest,
            {
                "recordedAt": utc_now(),
                "kind": "EXACT_FAILED_DERIVED_PROJECTIONS_NOT_REPLACEMENT_VERDICT",
                "subjectTag": expected_tag,
                "subjectCommit": publication["publishedCommit"],
                "originalResult": "FAIL",
                "files": {
                    name: {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}
                    for name, raw in originals.items()
                },
                "rawProducerManifest": json.loads(originals["PRODUCER-REPORTS.json"])["manifest"],
                "activeProjectionsRetired": False,
            },
        )
        print("EXACT_OLD_FAILED_FULL_VIEWS_ARCHIVED_ACTIVE_UNCHANGED")
        return 0
    regular(manifest, CHECKPOINT)
    old = load_json(manifest)
    current = current_publication()
    current_greenkeeper()
    if (
        set(old["files"]) != set(NAMES)
        or old["originalResult"] != "FAIL"
        or old["activeProjectionsRetired"] is not False
        or current["commit"] == old["subjectCommit"]
        or int(current["tag"].rsplit("-v", 1)[1]) <= int(args.version)
    ):
        raise ValueError("ACTUAL_NEWER_PUBLISHED_COMPLETE_QUALITY_REQUIRED")
    for name, fact in old["files"].items():
        source, archive = CHECKPOINT / name, folder / name
        for path in (source, archive):
            regular(path, CHECKPOINT)
            raw = path.read_bytes()
            if len(raw) != fact["bytes"] or hashlib.sha256(raw).hexdigest() != fact["sha256"]:
                raise ValueError("ORIGINAL_PROJECTION_OR_ARCHIVE_CHANGED")
    receipt = folder / "ACTIVE-PROJECTION-RETIREMENT.json"
    if receipt.exists():
        raise ValueError("DO_NOT_REPLAY_PARTIAL_OR_COMPLETED_RETIREMENT")
    facts = {
        "startedAt": utc_now(),
        "action": "RETIRE_ONLY_EXACT_ARCHIVED_MUTABLE_PROJECTIONS",
        "newSubject": current["commit"],
        "removed": [],
        "allOriginalFailuresPreserved": True,
        "result": "IN_PROGRESS",
    }
    write_json(receipt, facts)
    for name in NAMES:
        (CHECKPOINT / name).unlink()
        facts["removed"].append(name)
        write_json(receipt, facts)
    facts.update(finishedAt=utc_now(), result="PASS")
    write_json(receipt, facts)
    print("ARCHIVED_OLD_PROJECTIONS_RETIRED_NEW_FULL_EXECUTION_STILL_REQUIRED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
