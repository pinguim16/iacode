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
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any

from ledger_common import LedgerError, find_root, load_json, resolve_latest, use_utf8_stdout, utc_now
from secret_scan import load_allowlist, scan_text

ZIP_TIME = (1980, 1, 1, 0, 0, 0)
DECLARATION_SCHEMA_VERSION = "2.0.0"
DECLARATION_FILE = "REVIEW-BUNDLE-VALIDATION.json"
# The declaration cannot be a member of the byte stream whose digest it declares. Schema 3.4 makes
# that mathematical boundary explicit, while every other checkpoint file comes from the immutable
# content commit named by the declaration.
SUBJECT_EXCLUDED_CHECKPOINT_FILES = (DECLARATION_FILE,)
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
REVIEW_CONTEXT_PATTERNS = (
    ".iacode/policies/**",
    ".iacode/schemas/**",
    ":(glob)**/migrations/**",
    ":(glob)**/tests/**",
)


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


def _review_context_paths(root: Path) -> set[Path]:
    """Return tracked canonical inputs a reviewer needs even when this Gate did not change them."""

    listing = str(git(root, "ls-files", "--", *REVIEW_CONTEXT_PATTERNS))
    return {
        Path(line)
        for line in listing.splitlines()
        if line.strip() and (root / Path(line)).is_file()
    }


def resolve_subject(root: Path, subject: str) -> str:
    """Resolve an immutable commit used as the canonical review transport subject."""

    resolved = str(git(root, "rev-parse", "--verify", f"{subject}^{{commit}}"))
    if len(resolved) != 40 or any(character not in "0123456789abcdef" for character in resolved):
        raise LedgerError(f"review bundle subject did not resolve to a commit: {subject}")
    return resolved


def _subject_paths(root: Path, subject: str, *patterns: str) -> set[Path]:
    arguments = ["ls-tree", "-r", "--name-only", subject]
    if patterns:
        arguments += ["--", *patterns]
    listing = str(git(root, *arguments))
    return {Path(line) for line in listing.splitlines() if line.strip()}


def _subject_bytes(root: Path, subject: str, path: Path) -> bytes:
    return bytes(git(root, "show", f"{subject}:{path.as_posix()}", binary=True))


def collect_subject(root: Path, checkpoint: Path, subject: str) -> dict[str, bytes]:
    """Collect a bundle solely from immutable Git objects.

    No working-tree file, live remote ref, observation timestamp or ignored output contributes to
    this payload. The declaration sidecar is excluded because embedding a digest declaration in the
    bytes it hashes is self-referential; schema 3.4 validators enforce that exact one-file boundary.
    """

    commit = resolve_subject(root, subject)
    relative_checkpoint = checkpoint.relative_to(root)
    state_path = relative_checkpoint / "STATE.json"
    try:
        state = json.loads(_subject_bytes(root, commit, state_path).decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError, subprocess.CalledProcessError) as error:
        raise LedgerError(f"review bundle subject has no valid checkpoint state: {error}") from error
    base = str(state.get("baseCommit") or "")
    if not base:
        raise LedgerError("review bundle subject STATE.json has no baseCommit")

    changed = str(git(root, "diff", "--name-only", "--diff-filter=ACMR", base, commit))
    paths = {Path(line) for line in changed.splitlines() if line.strip()}
    tracked = _subject_paths(root, commit)
    paths.update(
        path for path in tracked
        if path.parts[:2] in ((".iacode", "policies"), (".iacode", "schemas"))
        or "migrations" in path.parts
        or "tests" in path.parts
    )
    paths.update(
        path for path in tracked if path == relative_checkpoint or relative_checkpoint in path.parents
    )
    excluded = {
        relative_checkpoint / name for name in SUBJECT_EXCLUDED_CHECKPOINT_FILES
    }
    paths.difference_update(excluded)
    paths.intersection_update(tracked)
    payload = {
        f"repository/{path.as_posix()}": _subject_bytes(root, commit, path)
        for path in sorted(paths, key=lambda item: item.as_posix())
    }

    tree = str(git(root, "rev-parse", f"{commit}^{{tree}}"))
    review_state = {
        "schemaVersion": "2.0.0",
        "checkpoint": checkpoint.name,
        "baseCommit": base,
        "subjectCommit": commit,
        "subjectTree": tree,
        "branch": state.get("branch"),
        "declaredCommit": state.get("currentCommit"),
        "source": "immutable-git-objects",
        "excludedCheckpointFiles": list(SUBJECT_EXCLUDED_CHECKPOINT_FILES),
    }
    payload["bundle/REVIEW-STATE.json"] = (
        json.dumps(review_state, sort_keys=True, separators=(",", ":")) + "\n"
    ).encode("utf-8")
    payload["bundle/CHANGESET.diff"] = bytes(
        git(root, "diff", "--binary", base, commit, binary=True)
    )
    checkpoint_prefix = f"repository/{relative_checkpoint.as_posix()}/"
    missing = sorted(
        name for name in REQUIRED_CHECKPOINT_FILES if checkpoint_prefix + name not in payload
    )
    if missing:
        raise LedgerError("review bundle checkpoint is incomplete: " + ", ".join(missing))
    return payload


def collect(root: Path, checkpoint: Path) -> dict[str, bytes]:
    state = load_json(checkpoint / "STATE.json")
    relative_checkpoint = checkpoint.relative_to(root)
    paths = _changed_paths(root, str(state["baseCommit"]))
    paths.update(_review_context_paths(root))
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


def create(root: Path, checkpoint: Path, destination: Path, subject: str | None = None) -> str:
    payload = collect_subject(root, checkpoint, subject) if subject else collect(root, checkpoint)
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
    try:
        bundle_name = bundle.relative_to(root).as_posix()
    except ValueError:
        bundle_name = bundle.name
    return {
        "schemaVersion": "1.0.0",
        "checkpoint": checkpoint.name,
        "bundle": bundle_name,
        "sha256": archive_digest,
        "sizeBytes": bundle.stat().st_size,
        "entries": len(names),
        "result": "PASS" if not findings else "FAIL",
        "findings": findings,
        "secretFindings": secret_findings,
        "validatedAt": utc_now(),
    }


def reconstruct_twice(
    root: Path,
    checkpoint: Path,
    subject: str,
    destination: Path | None = None,
) -> dict[str, Any]:
    """Rebuild the immutable subject twice and require byte identity and portable validation."""

    commit = resolve_subject(root, subject)
    with tempfile.TemporaryDirectory(prefix="iacode-review-rebuild-") as temporary:
        directory = Path(temporary)
        bundles = [directory / "rebuild-a.zip", directory / "rebuild-b.zip"]
        digests = [create(root, checkpoint, path, commit) for path in bundles]
        validations = [validate(root, checkpoint, path) for path in bundles]
        sizes = [path.stat().st_size for path in bundles]
        identical = digests[0] == digests[1] and bundles[0].read_bytes() == bundles[1].read_bytes()
        passed = identical and all(item.get("result") == "PASS" for item in validations)
        if destination is not None and passed:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(bundles[0], destination)
        return {
            "subjectCommit": commit,
            "subjectTree": str(git(root, "rev-parse", f"{commit}^{{tree}}")),
            "sha256": digests,
            "sizeBytes": sizes,
            "entries": [item.get("entries") for item in validations],
            "validationResults": [item.get("result") for item in validations],
            "byteIdentical": identical,
            "result": "PASS" if passed else "FAIL",
        }


def reconstruct_twice_from_transport(
    root: Path,
    checkpoint: Path,
    subject: str,
    destination: Path,
) -> dict[str, Any]:
    """Clone through Git transport, then execute the subject-carried producer twice detached."""

    commit = resolve_subject(root, subject)
    checkpoint_relative = checkpoint.relative_to(root)
    with tempfile.TemporaryDirectory(prefix="iacode-review-transport-") as temporary:
        parent = Path(temporary)
        clone = parent / "repository"
        cloned = subprocess.run(
            ["git", "clone", "--quiet", "--no-local", str(root), str(clone)],
            cwd=parent,
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        checked = subprocess.run(
            ["git", "checkout", "--quiet", "--detach", commit],
            cwd=clone,
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        ) if cloned.returncode == 0 else cloned
        bundle_directory = clone / "artifacts" / "review"
        bundle_directory.mkdir(parents=True, exist_ok=True)
        bundles = [bundle_directory / "rebuild-a.zip", bundle_directory / "rebuild-b.zip"]
        runs: list[subprocess.CompletedProcess[str]] = []
        for bundle in bundles:
            runs.append(subprocess.run(
                [
                    sys.executable,
                    str(clone / "scripts" / "development-ledger" / "review_bundle.py"),
                    "--root", str(clone),
                    "--checkpoint", str(checkpoint_relative),
                    "--subject", commit,
                    "--bundle", str(bundle),
                ],
                cwd=clone,
                text=True,
                encoding="utf-8",
                errors="replace",
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
            ))
        files_exist = all(path.is_file() for path in bundles)
        digests = [hashlib.sha256(path.read_bytes()).hexdigest() for path in bundles] if files_exist else []
        sizes = [path.stat().st_size for path in bundles] if files_exist else []
        validation_results = [
            "PASS" if run.returncode == 0 and "REVIEW_BUNDLE=PASS" in run.stdout else "FAIL"
            for run in runs
        ]
        entries = []
        if files_exist:
            for path in bundles:
                with zipfile.ZipFile(path) as archive:
                    entries.append(len(archive.namelist()))
        identical = (
            files_exist
            and digests[0] == digests[1]
            and bundles[0].read_bytes() == bundles[1].read_bytes()
        )
        passed = (
            cloned.returncode == 0
            and checked.returncode == 0
            and all(run.returncode == 0 for run in runs)
            and identical
            and all(item == "PASS" for item in validation_results)
        )
        if passed:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(bundles[0], destination)
        return {
            "mode": "git-clone-no-local-detached",
            "subjectCommit": commit,
            "subjectTree": str(git(root, "rev-parse", f"{commit}^{{tree}}")),
            "cloneExitCode": cloned.returncode,
            "checkoutExitCode": checked.returncode,
            "producerExitCodes": [run.returncode for run in runs],
            "producerOutput": [run.stdout.strip()[-1000:] for run in runs],
            "sha256": digests,
            "sizeBytes": sizes,
            "entries": entries,
            "validationResults": validation_results,
            "byteIdentical": identical,
            "result": "PASS" if passed else "FAIL",
        }


def declaration_from_reconstruction(
    root: Path,
    checkpoint: Path,
    destination: Path,
    reconstruction: dict[str, Any],
) -> dict[str, Any]:
    """Create the transportable sidecar declaration from a successful two-build proof."""

    digests = list(reconstruction.get("sha256") or [])
    sizes = list(reconstruction.get("sizeBytes") or [])
    entries = list(reconstruction.get("entries") or [])
    passed = (
        reconstruction.get("result") == "PASS"
        and len(set(digests)) == 1
        and len(set(sizes)) == 1
        and len(set(entries)) == 1
        and destination.is_file()
    )
    findings = [] if passed else ["transported reconstructions were not identical and valid"]
    return {
        "schemaVersion": DECLARATION_SCHEMA_VERSION,
        "checkpoint": checkpoint.name,
        "bundle": destination.relative_to(root).as_posix(),
        "subject": {
            "kind": "git-commit",
            "commit": reconstruction.get("subjectCommit"),
            "tree": reconstruction.get("subjectTree"),
        },
        "payloadPolicy": {
            "source": "immutable-git-objects",
            "excludedCheckpointFiles": list(SUBJECT_EXCLUDED_CHECKPOINT_FILES),
            "reason": "The digest declaration is a sidecar and cannot be a member of the bytes it hashes.",
        },
        "sha256": digests[0] if passed else None,
        "sizeBytes": sizes[0] if passed else None,
        "entries": entries[0] if passed else None,
        "result": "PASS" if passed else "FAIL",
        "findings": findings,
        "secretFindings": [],
        "transportReconstruction": reconstruction,
        "validatedAt": utc_now(),
    }


def verify_declaration(
    root: Path,
    checkpoint: Path,
    declaration: dict[str, Any],
    reconstruction: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Independently rebuild and compare a schema 2 review declaration."""

    findings: list[str] = []
    if declaration.get("schemaVersion") != DECLARATION_SCHEMA_VERSION:
        findings.append(
            f"declaration schemaVersion must be {DECLARATION_SCHEMA_VERSION}"
        )
    subject = declaration.get("subject") if isinstance(declaration.get("subject"), dict) else {}
    commit = subject.get("commit")
    if subject.get("kind") != "git-commit" or not isinstance(commit, str):
        findings.append("declaration subject must name an immutable git-commit")
    policy = declaration.get("payloadPolicy") if isinstance(declaration.get("payloadPolicy"), dict) else {}
    if policy.get("source") != "immutable-git-objects":
        findings.append("declaration payloadPolicy must use immutable-git-objects")
    if policy.get("excludedCheckpointFiles") != list(SUBJECT_EXCLUDED_CHECKPOINT_FILES):
        findings.append("declaration must exclude exactly its self-referential sidecar")
    if reconstruction is None and not findings and isinstance(commit, str):
        try:
            reconstruction = reconstruct_twice(root, checkpoint, commit)
        except (LedgerError, OSError, subprocess.SubprocessError, zipfile.BadZipFile) as error:
            findings.append(f"declaration reconstruction failed: {error}")
    if reconstruction is not None:
        rebuilt_digests = reconstruction.get("sha256") or []
        rebuilt_sizes = reconstruction.get("sizeBytes") or []
        rebuilt_entries = reconstruction.get("entries") or []
        if reconstruction.get("result") != "PASS":
            findings.append("declaration reconstruction was not deterministic and valid")
        if subject.get("tree") != reconstruction.get("subjectTree"):
            findings.append("declaration subject tree does not match the subject commit")
        if any(value != declaration.get("sha256") for value in rebuilt_digests):
            findings.append("declared sha256 does not match two reconstructed archives")
        if any(value != declaration.get("sizeBytes") for value in rebuilt_sizes):
            findings.append("declared sizeBytes does not match two reconstructed archives")
        if any(value != declaration.get("entries") for value in rebuilt_entries):
            findings.append("declared entries do not match two reconstructed archives")
    if declaration.get("result") != "PASS":
        findings.append("declaration result is not PASS")
    return {
        "result": "PASS" if not findings else "FAIL",
        "findings": findings,
        "reconstruction": reconstruction,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path)
    parser.add_argument("--checkpoint", type=Path)
    parser.add_argument("--bundle", type=Path)
    parser.add_argument("--subject", help="immutable commit used as the reconstruction subject")
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--verify-declaration", action="store_true")
    parser.add_argument("--write-report", action="store_true")
    arguments = parser.parse_args()
    root = find_root(arguments.root) if arguments.root else find_root()
    checkpoint = arguments.checkpoint or resolve_latest(root)
    if not checkpoint.is_absolute():
        checkpoint = root / checkpoint
    bundle = arguments.bundle or root / "artifacts" / "review" / f"{checkpoint.name}.zip"
    if not bundle.is_absolute():
        bundle = root / bundle
    if arguments.verify_declaration:
        declaration_path = checkpoint / DECLARATION_FILE
        if not declaration_path.is_file():
            raise LedgerError(f"review declaration does not exist: {declaration_path}")
        declaration = load_json(declaration_path)
        verified = verify_declaration(root, checkpoint, declaration)
        print(f"REVIEW_BUNDLE_DECLARATION={verified['result']}")
        for finding in verified["findings"]:
            print(f"- {finding}")
        return 0 if verified["result"] == "PASS" else 1
    if not arguments.validate_only:
        digest = create(root, checkpoint, bundle, arguments.subject)
        print(f"REVIEW_BUNDLE_CREATED path={bundle.relative_to(root)} sha256={digest}")
    report = validate(root, checkpoint, bundle)
    if arguments.write_report:
        if arguments.subject:
            reconstruction = reconstruct_twice(root, checkpoint, arguments.subject, bundle)
            report = declaration_from_reconstruction(
                root, checkpoint, bundle, reconstruction)
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
