#!/usr/bin/env python3
"""Derive whether a milestone passed its independent audit, from the repository alone.

A milestone verdict is never read from a status field. It is computed from the attestations that
completed audits left behind, each re-verified against the sealed subject it names, the audit
checkpoint that wrote it, and the four results that make a milestone pass.

    python scripts/development-ledger/milestone_status.py --milestone M0

Exit code 0 means the milestone has a valid attestation and passed. Exit code 1 means it did not,
and every reason is printed. The subject checkpoint is never modified, re-tagged or re-sealed by
this derivation: an audit is something recorded *about* a sealed checkpoint, in a later one.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from attestation import derive_milestone_verdict, statuses_for_mechanism
from ledger_common import LedgerError, find_root


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path)
    parser.add_argument("--milestone", required=True, help="milestone identifier, such as M0")
    parser.add_argument("--subject", default=None,
                        help="restrict the derivation to one subject checkpoint")
    parser.add_argument("--json", action="store_true", help="print the full derivation as JSON")
    args = parser.parse_args()

    root = find_root(args.root) if args.root else find_root()
    verdict = derive_milestone_verdict(root, args.milestone, args.subject)

    if args.json:
        print(json.dumps(verdict, indent=2, ensure_ascii=False))
    else:
        print(f"MILESTONE_{verdict['status']} milestone={verdict['milestone']} "
              f"attestations={len(verdict['attestations'])} accepted={len(verdict['accepted'])}")
        for item in verdict["accepted"]:
            statuses = statuses_for_mechanism(item["validationMechanism"])
            print(f"- {item['auditId']}: {item['subjectCheckpoint']} at {item['subjectCommit']} "
                  f"audited by {item['auditCheckpoint']} "
                  f"({item['validationMechanism']}); authorises "
                  + (", ".join(statuses) if statuses else "no milestone status"))
        for item in verdict["attestations"]:
            for reason in item["reasons"]:
                print(f"- REJECTED {reason}")
        for reason in verdict["reasons"]:
            if not any(reason in item["reasons"] for item in verdict["attestations"]):
                print(f"- {reason}")
    return 0 if verdict["status"] == "PASSED" else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except LedgerError as exc:
        print(f"LEDGER_ERROR: {exc}")
        sys.exit(2)
