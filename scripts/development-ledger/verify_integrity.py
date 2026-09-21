#!/usr/bin/env python3
"""Verify the sealed checkpoint chain against its integrity anchors, and rebuild it when asked.

Exit code 0 means every anchored checkpoint still resolves to the tag, commit and tree recorded
for it, and the hash chain between anchors is unbroken. Any nonzero exit means sealed history and
its record disagree, which is the failure class the M0 audit demonstrated by moving a tag and HEAD
together.

``--rebuild`` recomputes the chain from the repository for every sealed checkpoint except the one
named by ``--exclude``. A checkpoint cannot anchor its own tag, because the anchor would have to
contain the commit that contains it, so the successor checkpoint anchors it.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from anchors import (
    anchor_path,
    load_anchors,
    pending_anchor_checkpoint,
    rebuild,
    rebuild_exclusion,
    sealed_checkpoint_ids,
    verify_chain,
)
from ledger_common import LedgerError, find_root, load_json, validate_schema


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path)
    parser.add_argument("--exclude", default=None,
                        help="checkpoint being sealed right now, which its successor anchors")
    parser.add_argument("--rebuild", action="store_true",
                        help="recompute the chain from the repository and write it")
    args = parser.parse_args()

    root = find_root(args.root) if args.root else find_root()
    # Both exclusions are semantic rules, not names. Verification forgives the newest sealed
    # checkpoint, whose anchor its successor still owes; a rebuild excludes the checkpoint being
    # delivered, because the run rebuilding the chain is that successor and cannot anchor itself.
    exclude = args.exclude if args.exclude is not None else pending_anchor_checkpoint(root)
    rebuild_skip = args.exclude if args.exclude is not None else rebuild_exclusion(root)

    if args.rebuild:
        identifiers = [item for item in sealed_checkpoint_ids(root) if item != rebuild_skip]
        document = rebuild(root, identifiers)
        schema_path = root / ".iacode" / "schemas" / "checkpoint-anchors.schema.json"
        if schema_path.is_file():
            errors = validate_schema(document, load_json(schema_path))
            if errors:
                print("ANCHORS_INVALID")
                for error in errors:
                    print(f"- {error}")
                return 2
        anchor_path(root).parent.mkdir(parents=True, exist_ok=True)
        anchor_path(root).write_text(
            json.dumps(document, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8", newline="\n")

    schema_path = root / ".iacode" / "schemas" / "checkpoint-anchors.schema.json"
    if anchor_path(root).is_file() and schema_path.is_file():
        for error in validate_schema(load_json(anchor_path(root)), load_json(schema_path)):
            print("ANCHORS_INVALID")
            print(f"- {error}")
            return 2

    errors = verify_chain(root, require_sealed=True, exclude={exclude} if exclude else set())
    if errors:
        print("INTEGRITY_INVALID")
        for error in errors:
            print(f"- {error}")
        return 1
    anchors = load_anchors(root)
    print(f"INTEGRITY_VALID anchors={len(anchors)} "
          f"latest={anchors[-1]['checkpointId'] if anchors else 'none'}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except LedgerError as exc:
        print(f"LEDGER_ERROR: {exc}")
        sys.exit(2)
