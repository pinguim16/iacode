#!/usr/bin/env python3
"""Create and validate a deterministic, secret-scanned Gate review bundle.

The archive is a review transport, never source control input. Its payload is the complete
checkpoint plus every path changed since the checkpoint base commit. Generated entries bind the
Git state and changeset. Validation reopens the ZIP, refuses unsafe or duplicate names, verifies
every manifest hash, checks mandatory artifact classes and scans every textual member for secrets.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any

from ledger_common import LedgerError, find_root, load_json, resolve_latest, use_utf8_stdout, utc_now
from secret_scan import load_allowlist, scan_text

ZIP_TIME = (1980, 1, 1, 0, 0, 0)
REQUIRED_CHECKPOINT_FILES = {
    "STATE.json",
    "REQUIREMENTS-MATRIX.json",
    "FUNCTIONAL-ACCEPTANCE.json",
    "QUALITY.json",
    "M2-INTERNAL-RED-TEAM.json",
    "COMPLETENESS-REPORT.json",
    "FILES.json",
    "COMMANDS.jsonl",
}


def git(root: Path, *arguments: str, binary: bool = False) -> str | bytes:
    completed = subprocess.run(["git", *arguments], cwd=root, capture_output=True, check=False)
    if completed.returncode != 0:
        raise LedgerError(
            f"git {' '.join(arguments)} failed: "
            + completed.stderr.decode("utf-8", errors="replace").strip()
        )
    if binary:
        return completed.stdout
    return completed.stdout.decode("utf-8", errors="replace").strip()


def _changed_paths(root: Path, base: str) -> set[Path]:
    names = str(git(root, "diff", "--name-only", "--diff-filter=ACMR", f"{base}..HEAD"))
    paths = {Path(line) for line in names.splitlines() if line.strip()}
    dirty = str(git(root, "status", "--porcelain=v1", "--untracked-files=all"))
    for line in dirty.splitlines():
        if len(line) >= 4:
            raw = line[3:].split(" -> ")[-1]
            paths.add(Path(raw))
    return {path for path in paths if (root / path).is_file()}


def collect(root: Path, checkpoint: Path) -> dict[str, bytes]:
    state = load_json(checkpoint / "STATE.json")
    relative_checkpoint = checkpoint.relative_to(root)
    paths = _changed_paths(root, str(state["baseCommit"]))
    paths.update(path.relative_to(root) for path in checkpoint.rglob("*") if path.is_file())
    payload = {
        f"repository/{path.as_posix()}": (root / path).read_bytes()
        for path in sorted(paths, key=lambda item: item.as_posix())
    }
    head = str(git(root, "rev-parse", "HEAD"))
    branch = str(git(root, "branch", "--show-current"))
    remote = str(git(root, "ls-remote", "--heads", "origin", f"refs/heads/{branch}"))
    review_state = {
        "schemaVersion": "1.0.0",
        "checkpoint": checkpoint.name,
        "baseCommit": state["baseCommit"],
        "headCommit": head,
        "branch": branch,
        "remoteHead": remote.split()[0] if remote else None,
        "dirty": bool(str(git(root, "status", "--porcelain=v1"))),
    }
    payload["bundle/REVIEW-STATE.json"] = (
        json.dumps(review_state, sort_keys=True, separators=(",", ":")) + "\n"
    ).encode("utf-8")
    payload["bundle/CHANGESET.diff"] = bytes(
        git(root, "diff", "--binary", str(state["baseCommit"]), "HEAD", binary=True)
    )
    checkpoint_prefix = f"repository/{relative_checkpoint.as_posix()}/"
    missing = sorted(
        name for name in REQUIRED_CHECKPOINT_FILES if checkpoint_prefix + name not in payload
    )
    if missing:
        raise LedgerError("review bundle checkpoint is incomplete: " + ", ".join(missing))
    return payload


def manifest(payload: dict[str, bytes]) -> dict[str, Any]:
    return {
        "schemaVersion": "1.0.0",
        "algorithm": "sha256",
        "entries": [
            {
                "path": name,
                "sha256": hashlib.sha256(content).hexdigest(),
                "sizeBytes": len(content),
            }
            for name, content in sorted(payload.items())
        ],
    }


def create(root: Path, checkpoint: Path, destination: Path) -> str:
    payload = collect(root, checkpoint)
    payload["bundle/MANIFEST.json"] = (
        json.dumps(manifest(payload), sort_keys=True, separators=(",", ":")) + "\n"
    ).encode("utf-8")
    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(
        destination, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
    ) as archive:
        for name, content in sorted(payload.items()):
            info = zipfile.ZipInfo(name, ZIP_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, content, compresslevel=9)
    return hashlib.sha256(destination.read_bytes()).hexdigest()


def validate(root: Path, checkpoint: Path, bundle: Path) -> dict[str, Any]:
    findings: list[str] = []
    if not bundle.is_file():
        raise LedgerError(f"review bundle does not exist: {bundle}")
    archive_digest = hashlib.sha256(bundle.read_bytes()).hexdigest()
    allowlist = load_allowlist(root)
    with zipfile.ZipFile(bundle) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)):
            findings.append("archive contains duplicate member names")
        for name in names:
            path = PurePosixPath(name)
            if path.is_absolute() or ".." in path.parts or "\\" in name:
                findings.append(f"unsafe archive member: {name}")
        try:
            declared = json.loads(archive.read("bundle/MANIFEST.json"))
        except (KeyError, json.JSONDecodeError) as error:
            raise LedgerError(f"bundle manifest is missing or invalid: {error}") from error
        entries = declared.get("entries") if isinstance(declared, dict) else None
        if not isinstance(entries, list):
            raise LedgerError("bundle manifest entries are invalid")
        expected_names = {str(item.get("path")) for item in entries}
        actual_payload = set(names) - {"bundle/MANIFEST.json"}
        if expected_names != actual_payload:
            findings.append("manifest member set differs from archive payload")
        for item in entries:
            name = str(item.get("path"))
            try:
                content = archive.read(name)
            except KeyError:
                continue
            if len(content) != item.get("sizeBytes"):
                findings.append(f"size mismatch: {name}")
            if hashlib.sha256(content).hexdigest() != item.get("sha256"):
                findings.append(f"digest mismatch: {name}")
        prefix = f"repository/{checkpoint.relative_to(root).as_posix()}/"
        for required in sorted(REQUIRED_CHECKPOINT_FILES):
            if prefix + required not in names:
                findings.append(f"missing required checkpoint artifact: {required}")
        categories = {
            "tests": any(
                "/tests/" in name or name.startswith("repository/tests/") for name in names
            ),
            "migrations": any("/migrations/" in name for name in names),
            "schemas": any("/.iacode/schemas/" in name for name in names),
            "policies": any("/.iacode/policies/" in name for name in names),
            "documentation": any(name.startswith("repository/docs/") for name in names),
            "changeset": "bundle/CHANGESET.diff" in names,
            "git-state": "bundle/REVIEW-STATE.json" in names,
        }
        for category, present in categories.items():
            if not present:
                findings.append(f"missing artifact category: {category}")
        secret_findings: list[dict[str, Any]] = []
        for name in names:
            content = archive.read(name)
            if b"\x00" in content[:8192]:
                continue
            text = content.decode("utf-8", errors="replace")
            for kind, line, allowed in scan_text(text, allowlist):
                if not allowed:
                    secret_findings.append({"path": name, "line": line, "kind": kind})
        if secret_findings:
            findings.append(f"secret scan found {len(secret_findings)} blocking match(es)")
    return {
        "schemaVersion": "1.0.0",
        "checkpoint": checkpoint.name,
        "bundle": bundle.relative_to(root).as_posix(),
        "sha256": archive_digest,
        "sizeBytes": bundle.stat().st_size,
        "entries": len(names),
        "result": "PASS" if not findings else "FAIL",
        "findings": findings,
        "secretFindings": secret_findings,
        "validatedAt": utc_now(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path)
    parser.add_argument("--checkpoint", type=Path)
    parser.add_argument("--bundle", type=Path)
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--write-report", action="store_true")
    arguments = parser.parse_args()
    root = find_root(arguments.root) if arguments.root else find_root()
    checkpoint = arguments.checkpoint or resolve_latest(root)
    if not checkpoint.is_absolute():
        checkpoint = root / checkpoint
    bundle = arguments.bundle or root / "artifacts" / "review" / f"{checkpoint.name}.zip"
    if not bundle.is_absolute():
        bundle = root / bundle
    if not arguments.validate_only:
        digest = create(root, checkpoint, bundle)
        print(f"REVIEW_BUNDLE_CREATED path={bundle.relative_to(root)} sha256={digest}")
    report = validate(root, checkpoint, bundle)
    if arguments.write_report:
        (checkpoint / "REVIEW-BUNDLE-VALIDATION.json").write_text(
            json.dumps(report, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
            newline="\n",
        )
    print(f"REVIEW_BUNDLE={report['result']} entries={report['entries']} sha256={report['sha256']}")
    for finding in report["findings"]:
        print(f"- {finding}")
    return 0 if report["result"] == "PASS" else 1


if __name__ == "__main__":
    use_utf8_stdout()
    try:
        sys.exit(main())
    except (LedgerError, OSError, zipfile.BadZipFile) as error:
        print(f"REVIEW_BUNDLE=FAIL {error}")
        sys.exit(1)
