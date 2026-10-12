#!/usr/bin/env python3
"""Audit the sealed Gate 4 subject and its review bundle from published transport."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import zipfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
SUBJECT = "GATE-4-CP-0005"
TAG = f"iacode-checkpoints/{SUBJECT}"
TAG_REF = f"refs/tags/{TAG}"
SEALED_COMMIT = "c631270e49c095a9777825c0bc18818694c07ffb"
CONTENT_COMMIT = "cac77ddef9c351ce828442d9312db69083aab81e"
REMOTE = "https://github.com/pinguim16/iacode.git"
EXPECTED_BUNDLE = "bb130be4e4e871af158bb71b0bc4c0f0a1da73af50a5db74df49f870b2d14d59"
sys.path.insert(0, str(ROOT / "scripts" / "development-ledger"))

from ledger_common import use_utf8_stdout  # noqa: E402


def run(argv: list[str], cwd: Path, timeout: int = 1800) -> dict[str, Any]:
    completed = subprocess.run(
        argv,
        cwd=cwd,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
        timeout=timeout,
    )
    return {
        "command": argv,
        "exitCode": completed.returncode,
        "tail": completed.stdout.strip()[-1600:],
    }


def git(cwd: Path, *arguments: str) -> str:
    completed = subprocess.run(
        ["git", *arguments], cwd=cwd, text=True, encoding="utf-8", errors="replace",
        capture_output=True, check=True, timeout=900,
    )
    return completed.stdout.strip()


def categories(names: list[str]) -> dict[str, bool]:
    return {
        "tests": any("/tests/" in name or name.startswith("repository/tests/") for name in names),
        "migrations": any("/migrations/" in name for name in names),
        "schemas": any("/.iacode/schemas/" in name for name in names),
        "policies": any("/.iacode/policies/" in name for name in names),
        "documentation": any(name.startswith("repository/docs/") for name in names),
        "changeset": "bundle/CHANGESET.diff" in names,
        "gitState": "bundle/REVIEW-STATE.json" in names,
        "manifest": "bundle/MANIFEST.json" in names,
    }


def inspect_archive(path: Path) -> dict[str, Any]:
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        bad_crc = archive.testzip()
        manifest = json.loads(archive.read("bundle/MANIFEST.json"))
        review_state = json.loads(archive.read("bundle/REVIEW-STATE.json"))
        entries = manifest.get("entries") or []
        manifest_names = {str(item.get("path")) for item in entries}
        payload_names = set(names) - {"bundle/MANIFEST.json"}
        mismatches = []
        for item in entries:
            name = str(item.get("path"))
            content = archive.read(name)
            if len(content) != item.get("sizeBytes"):
                mismatches.append(f"size:{name}")
            if hashlib.sha256(content).hexdigest() != item.get("sha256"):
                mismatches.append(f"digest:{name}")
        return {
            "entries": len(names),
            "uniqueEntries": len(set(names)),
            "crcFailure": bad_crc,
            "manifestEntries": len(entries),
            "manifestMatchesPayload": manifest_names == payload_names,
            "hashMismatches": mismatches,
            "categories": categories(names),
            "reviewState": review_state,
        }


def main() -> int:
    use_utf8_stdout()
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path, required=True)
    arguments = parser.parse_args()
    steps: list[dict[str, Any]] = []
    original = ROOT / "artifacts" / "review" / f"{SUBJECT}.zip"
    declared = json.loads(
        (ROOT / "docs" / "checkpoints" / SUBJECT / "REVIEW-BUNDLE-VALIDATION.json")
        .read_text(encoding="utf-8")
    )
    original_digest = hashlib.sha256(original.read_bytes()).hexdigest() if original.is_file() else None
    original_inspection = inspect_archive(original) if original.is_file() else None

    scratch = Path(tempfile.mkdtemp(prefix="iacode-g4-bundle-audit-"))
    clone = scratch / "iacode"
    original_validation: dict[str, Any] = {"result": "FAIL", "findings": ["not executed"]}
    rebuilt_validations: list[dict[str, Any]] = []
    rebuilt_digests: list[str] = []
    identity: dict[str, Any] = {}
    try:
        steps.append(run(["git", "clone", "--quiet", REMOTE, str(clone)], scratch))
        if steps[-1]["exitCode"] != 0:
            raise RuntimeError("published transport clone failed")
        remote_head = git(clone, "rev-parse", "origin/main")
        remote_tag = git(clone, "rev-parse", f"{TAG}^{{commit}}")
        remote_parent = git(clone, "rev-parse", f"{TAG}^")
        remote_tree = git(clone, "rev-parse", f"{TAG}^{{tree}}")
        identity = {
            "originMain": remote_head,
            "tagCommit": remote_tag,
            "contentCommit": remote_parent,
            "tree": remote_tree,
            "matchesExpected": (
                remote_head == SEALED_COMMIT
                and remote_tag == SEALED_COMMIT
                and remote_parent == CONTENT_COMMIT
            ),
        }
        steps.append(run([
            sys.executable,
            "scripts/development-ledger/remote_sync.py",
            "--authorised-url",
            REMOTE,
            "--tag",
            TAG,
        ], clone))
        steps.append(run(["git", "checkout", "--detach", "--quiet", TAG], clone))
        steps.append(run([
            sys.executable, "scripts/development-ledger/validate_checkpoint.py"
        ], clone, 3600))
        steps.append(run([
            sys.executable, "scripts/development-ledger/verify_integrity.py"
        ], clone, 1800))
        steps.append(run([
            sys.executable, "scripts/development-ledger/validate_lessons.py"
        ], clone, 1800))

        sys.path.insert(0, str(clone / "scripts" / "development-ledger"))
        from review_bundle import create, validate  # type: ignore[import-not-found]

        portable_original = clone / "artifacts" / "review" / original.name
        portable_original.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(original, portable_original)
        subject_path = clone / "docs" / "checkpoints" / SUBJECT
        original_validation = validate(clone, subject_path, portable_original)

        for name in ("rebuilt-a.zip", "rebuilt-b.zip"):
            target = clone / "artifacts" / "review" / name
            rebuilt_digests.append(create(clone, subject_path, target))
            rebuilt_validations.append(validate(clone, subject_path, target))
    finally:
        shutil.rmtree(scratch, ignore_errors=True)

    checks = {
        "subjectIdentity": bool(identity.get("matchesExpected")),
        "publishedCommands": all(item.get("exitCode") == 0 for item in steps),
        "declaredBundleIdentity": (
            declared.get("sha256") == EXPECTED_BUNDLE
            and original_digest == EXPECTED_BUNDLE
            and declared.get("sizeBytes") == (original.stat().st_size if original.is_file() else None)
        ),
        "originalArchiveStructure": bool(
            original_inspection
            and original_inspection["crcFailure"] is None
            and original_inspection["entries"] == original_inspection["uniqueEntries"]
            and original_inspection["manifestMatchesPayload"]
            and not original_inspection["hashMismatches"]
            and all(original_inspection["categories"].values())
        ),
        "originalPortableValidation": (
            original_validation.get("result") == "PASS"
            and not original_validation.get("findings")
            and not original_validation.get("secretFindings")
        ),
        "deterministicRebuild": (
            len(rebuilt_digests) == 2 and rebuilt_digests[0] == rebuilt_digests[1]
        ),
        "rebuiltPortableValidation": bool(rebuilt_validations) and all(
            item.get("result") == "PASS"
            and not item.get("findings")
            and not item.get("secretFindings")
            for item in rebuilt_validations
        ),
    }
    report = {
        "schemaVersion": "1.0.0",
        "artifact": "GATE-4-SUBJECT-AND-BUNDLE-AUDIT",
        "checkpoint": CHECKPOINT.name,
        "subjectCheckpoint": SUBJECT,
        "subjectCommit": SEALED_COMMIT,
        "contentCommit": CONTENT_COMMIT,
        "generatedAt": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "identity": identity,
        "publishedValidationSteps": steps,
        "declaredBundleValidation": declared,
        "originalBundleSha256": original_digest,
        "originalInspection": original_inspection,
        "originalPortableValidation": original_validation,
        "rebuiltSha256": rebuilt_digests,
        "rebuiltValidations": rebuilt_validations,
        "checks": checks,
        "result": "PASS" if all(checks.values()) else "FAIL",
    }
    arguments.report.resolve().write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        f"SUBJECT_BUNDLE_AUDIT={report['result']} "
        f"checks={sum(1 for value in checks.values() if value)}/{len(checks)} "
        f"original={original_digest} rebuilt={','.join(rebuilt_digests)}"
    )
    return 0 if report["result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
