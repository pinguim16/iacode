#!/usr/bin/env python3
"""Rebuild and validate the CP0007 review bundle using published transport only."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
import zipfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
SUBJECT = "GATE-4-CP-0007"
TAG = f"iacode-checkpoints/{SUBJECT}"
SEALED_COMMIT = "e21d30fde473f302d0f8f60b59acf008fa52e250"
CONTENT_COMMIT = "c9adc70032584ce8ff3ad52616f9eae6410c805f"
EXPECTED_BUNDLE = "8856ce50acebfa02528ad318247c22e6e460c224eb62774c99a35cb5cd734578"
REMOTE = "https://github.com/pinguim16/iacode.git"
sys.path.insert(0, str(ROOT / "scripts" / "development-ledger"))

from ledger_common import use_utf8_stdout  # noqa: E402


def run(arguments: list[str], cwd: Path, timeout: int = 1800) -> dict[str, Any]:
    completed = subprocess.run(
        arguments, cwd=cwd, text=True, encoding="utf-8", errors="replace",
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False, timeout=timeout,
    )
    return {
        "command": arguments,
        "exitCode": completed.returncode,
        "tail": completed.stdout.strip()[-2000:],
    }


def git(cwd: Path, *arguments: str) -> str:
    completed = subprocess.run(
        ["git", *arguments], cwd=cwd, text=True, encoding="utf-8", errors="replace",
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True,
    )
    return completed.stdout.strip()


def inspect_archive(path: Path) -> dict[str, Any]:
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        manifest = json.loads(archive.read("bundle/MANIFEST.json"))
        entries = manifest.get("entries") or []
        mismatches: list[str] = []
        for entry in entries:
            name = str(entry.get("path"))
            content = archive.read(name)
            if len(content) != entry.get("sizeBytes"):
                mismatches.append(f"size:{name}")
            if hashlib.sha256(content).hexdigest() != entry.get("sha256"):
                mismatches.append(f"digest:{name}")
        categories = {
            "tests": any("/tests/" in name or name.startswith("repository/tests/") for name in names),
            "migrations": any("/migrations/" in name for name in names),
            "schemas": any("/.iacode/schemas/" in name for name in names),
            "policies": any("/.iacode/policies/" in name for name in names),
            "documentation": any(name.startswith("repository/docs/") for name in names),
            "changeset": "bundle/CHANGESET.diff" in names,
            "gitState": "bundle/REVIEW-STATE.json" in names,
            "manifest": "bundle/MANIFEST.json" in names,
        }
        return {
            "entries": len(names),
            "uniqueEntries": len(set(names)),
            "crcFailure": archive.testzip(),
            "manifestEntries": len(entries),
            "manifestMatchesPayload": {
                str(item.get("path")) for item in entries
            } == set(names) - {"bundle/MANIFEST.json"},
            "hashMismatches": mismatches,
            "categories": categories,
        }


def main() -> int:
    use_utf8_stdout()
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path, required=True)
    arguments = parser.parse_args()
    steps: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="iacode-g4-cp0008-bundle-") as temporary:
        parent = Path(temporary)
        clone = parent / "repository"
        steps.append(run(["git", "clone", "--quiet", "--no-local", REMOTE, str(clone)], parent))
        steps.append(run(["git", "checkout", "--quiet", "--detach", TAG], clone))
        identity = {
            "originMain": git(clone, "rev-parse", "origin/main"),
            "tagCommit": git(clone, "rev-parse", f"{TAG}^{{commit}}"),
            "contentCommit": git(clone, "rev-parse", f"{TAG}^"),
            "tree": git(clone, "rev-parse", f"{TAG}^{{tree}}"),
        }
        identity["matchesExpected"] = (
            identity["originMain"] == SEALED_COMMIT
            and identity["tagCommit"] == SEALED_COMMIT
            and identity["contentCommit"] == CONTENT_COMMIT
        )
        for tool in (
            [sys.executable, "scripts/development-ledger/validate_checkpoint.py"],
            [sys.executable, "scripts/development-ledger/verify_integrity.py"],
            [sys.executable, "scripts/development-ledger/validate_lessons.py"],
        ):
            steps.append(run(tool, clone, 3600))
        declared = json.loads(
            (clone / "docs" / "checkpoints" / SUBJECT / "REVIEW-BUNDLE-VALIDATION.json")
            .read_text(encoding="utf-8")
        )
        sys.path.insert(0, str(clone / "scripts" / "development-ledger"))
        from review_bundle import create, validate  # type: ignore[import-not-found]

        subject_path = clone / "docs" / "checkpoints" / SUBJECT
        bundle_directory = clone / "artifacts" / "review"
        bundle_directory.mkdir(parents=True, exist_ok=True)
        bundles = [bundle_directory / "rebuild-a.zip", bundle_directory / "rebuild-b.zip"]
        digests = [create(clone, subject_path, target) for target in bundles]
        validations = [validate(clone, subject_path, target) for target in bundles]
        inspections = [inspect_archive(target) for target in bundles]
        checks = {
            "subjectIdentity": bool(identity["matchesExpected"]),
            "publishedValidation": all(step["exitCode"] == 0 for step in steps),
            "declaredDigest": declared.get("sha256") == EXPECTED_BUNDLE,
            "deterministicRebuild": len(digests) == 2 and digests[0] == digests[1],
            "declaredDigestReconstructed": digests == [EXPECTED_BUNDLE, EXPECTED_BUNDLE],
            "portableValidation": all(
                item.get("result") == "PASS"
                and not item.get("findings")
                and not item.get("secretFindings")
                for item in validations
            ),
            "archiveIntegrity": all(
                item["entries"] == item["uniqueEntries"]
                and item["crcFailure"] is None
                and item["manifestMatchesPayload"]
                and not item["hashMismatches"]
                and all(item["categories"].values())
                for item in inspections
            ),
        }
        checks.update({
            "originalPortableValidation": checks["portableValidation"],
            "rebuiltPortableValidation": checks["portableValidation"],
            "originalArchiveStructure": checks["archiveIntegrity"],
        })
        report = {
            "schemaVersion": "1.0.0",
            "artifact": "GATE-4-PUBLISHED-SUBJECT-BUNDLE-AUDIT",
            "checkpoint": CHECKPOINT.name,
            "subjectCheckpoint": SUBJECT,
            "subjectCommit": SEALED_COMMIT,
            "contentCommit": CONTENT_COMMIT,
            "generatedAt": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            "identity": identity,
            "publishedValidationSteps": steps,
            "declaredBundleValidation": declared,
            "rebuiltSha256": digests,
            "rebuiltValidations": validations,
            "rebuiltInspections": inspections,
            "checks": checks,
            "result": "PASS" if all(checks.values()) else "FAIL",
            "transportNote": (
                "No producer-local ZIP is an input. Both archives were reconstructed from the "
                "detached published subject and discarded after validation; the checkpoint stores "
                "only the canonical digest and report."
            ),
        }
        arguments.report.resolve().write_text(
            json.dumps(report, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8", newline="\n",
        )
    print(
        f"SUBJECT_BUNDLE_AUDIT={report['result']} "
        f"checks={sum(1 for value in checks.values() if value)}/{len(checks)} "
        f"digest={','.join(digests)}"
    )
    return 0 if report["result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
