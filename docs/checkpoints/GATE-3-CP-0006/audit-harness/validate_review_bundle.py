#!/usr/bin/env python3
"""Validate the M1 review ZIP and write the adjacent machine-readable result.

The check is deliberately independent of the bundle builder: it opens the archive, checks CRC,
rejects duplicate or unsafe member names, verifies the embedded SHA256SUMS and manifest, requires
the milestone evidence set, and applies the repository's canonical secret patterns to every text
member without ever printing a matched value.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "scripts" / "development-ledger"))

from secret_scan import load_allowlist, scan_text  # noqa: E402

CHECKPOINT = "GATE-3-CP-0006"
PREFIX = f"docs/checkpoints/{CHECKPOINT}/"
MANDATORY = {
    ".iacode/attestations/M1-CP-0006.json",
    "CHANGESET.patch",
    "GIT-LOG.txt",
    "REMOTE-STATE.txt",
    "REVIEW-BUNDLE-MANIFEST.json",
    "SHA256SUMS.txt",
    PREFIX + "PLAN.md",
    PREFIX + "AUDIT-EXECUTIONS.json",
    PREFIX + "FINDINGS.json",
    PREFIX + "TESTS.json",
    PREFIX + "DEPENDENCY-SCAN-REPORT.json",
    PREFIX + "VERIFICATION-REPORT.json",
    PREFIX + "CLEAN-CLONE-REPORT.json",
    PREFIX + "LIVE-CODING-RUN.json",
    PREFIX + "TOOL-RESULT-ORIGIN.json",
    PREFIX + "M1-INTERNAL-RED-TEAM.json",
    PREFIX + "COMPLETENESS-REPORT.json",
    PREFIX + "FINAL-M1-AUDIT-MATRIX.json",
    PREFIX + "FINAL-REPORT.md",
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def safe(name: str) -> bool:
    path = PurePosixPath(name)
    return (not path.is_absolute() and ".." not in path.parts
            and not re.match(r"^[A-Za-z]:", name) and "\\" not in name)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    arguments = parser.parse_args()
    checks: list[dict[str, object]] = []

    def record(name: str, ok: bool, observed: str) -> None:
        checks.append({"check": name, "ok": ok, "observed": observed})

    with zipfile.ZipFile(arguments.archive) as archive:
        infos = archive.infolist()
        names = [item.filename for item in infos]
        record("archive CRC", archive.testzip() is None,
               "all members readable" if archive.testzip() is None else "CRC failure")
        record("member names are unique", len(names) == len(set(names)),
               f"{len(names)} members, {len(set(names))} unique")
        unsafe = [name for name in names if not safe(name)]
        record("member paths are safe", not unsafe,
               "no absolute, parent, drive or backslash path" if not unsafe else str(unsafe))
        missing = sorted(MANDATORY - set(names))
        record("mandatory evidence is present", not missing,
               f"{len(MANDATORY)} required members" if not missing else f"missing {missing}")

        payload = {name: archive.read(name) for name in names if not name.endswith("/")}
        sums: dict[str, str] = {}
        malformed: list[str] = []
        for line in payload.get("SHA256SUMS.txt", b"").decode("utf-8", "replace").splitlines():
            value, separator, name = line.partition("  ")
            if not separator or not re.fullmatch(r"[0-9a-f]{64}", value):
                malformed.append(line[:120])
            else:
                sums[name] = value
        bad_sums = [name for name, value in sums.items()
                    if name not in payload or digest(payload[name]) != value]
        expected_sums = set(payload) - {"SHA256SUMS.txt"}
        record("embedded checksums", not malformed and not bad_sums
               and set(sums) == expected_sums,
               f"{len(sums)}/{len(expected_sums)} verified; malformed={len(malformed)}; "
               f"mismatch={bad_sums}")

        try:
            manifest = json.loads(payload["REVIEW-BUNDLE-MANIFEST.json"])
        except (KeyError, json.JSONDecodeError) as error:
            manifest = {}
            record("manifest parses", False, type(error).__name__)
        else:
            record("manifest parses", True,
                   f"checkpoint={manifest.get('checkpoint')} finalCommit={manifest.get('finalCommit')}")
        declared = manifest.get("filesIncluded") or []
        bad_manifest = [item.get("path") for item in declared
                        if item.get("path") not in payload
                        or digest(payload[item["path"]]) != item.get("sha256")
                        or len(payload[item["path"]]) != item.get("bytes")]
        record("manifest file hashes", bool(declared) and not bad_manifest,
               f"{len(declared)} declared; mismatches={bad_manifest}")
        record("manifest identity", manifest.get("checkpoint") == CHECKPOINT
               and manifest.get("milestone") == "M1"
               and manifest.get("tag") == f"refs/tags/iacode-checkpoints/{CHECKPOINT}",
               f"checkpoint={manifest.get('checkpoint')} milestone={manifest.get('milestone')} "
               f"tag={manifest.get('tag')}")

        allowlist = load_allowlist(ROOT)
        blocking: list[dict[str, object]] = []
        allowed = 0
        for name, data in payload.items():
            if b"\0" in data[:8192]:
                continue
            for kind, line, is_allowed in scan_text(data.decode("utf-8", "replace"), allowlist):
                if is_allowed:
                    allowed += 1
                else:
                    blocking.append({"path": name, "line": line, "kind": kind})
        record("secret scan", not blocking,
               f"blocking={len(blocking)} allowlisted={allowed}; values are never recorded")

    failed = [item for item in checks if not item["ok"]]
    report = {
        "schemaVersion": "1.0.0",
        "artifact": "REVIEW-BUNDLE-VALIDATION",
        "checkpoint": CHECKPOINT,
        "archive": str(arguments.archive.resolve()),
        "archiveSha256": digest(arguments.archive.read_bytes()),
        "checks": checks,
        "passed": len(checks) - len(failed),
        "total": len(checks),
        "result": "PASS" if not failed else "FAIL",
    }
    arguments.report.parent.mkdir(parents=True, exist_ok=True)
    arguments.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n",
                                encoding="utf-8", newline="\n")
    print(f"REVIEW_BUNDLE_VALIDATION={report['result']} {report['passed']}/{report['total']}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
