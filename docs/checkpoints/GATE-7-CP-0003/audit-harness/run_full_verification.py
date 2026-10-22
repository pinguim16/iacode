#!/usr/bin/env python3
"""Execute one full internal verifier from an exact published subject in a fresh clone."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import shutil
import subprocess
import sys
import tempfile
import uuid
from contextlib import contextmanager
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
REMOTE = "https://github.com/pinguim16/iacode.git"
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))
sys.path.insert(0, str(ROOT / "scripts/iacode"))


def build_stages(fast: bool):
    from verify import build_stages as canonical_stages

    return canonical_stages(fast)


def canonical_producer_names() -> set[str]:
    names = {
        "sandbox-tool-result-origin.json",
        "desktop-e2e.json",
        "native-editor-package.json",
        "experience-store-e2e.json",
        "knowledge-engine-e2e.json",
    }
    for stage in build_stages(False):
        for index, argument in enumerate(stage.argv[:-1]):
            if argument == "--report":
                path = Path(stage.argv[index + 1])
                if path.parent.name == "var" and path.suffix == ".json":
                    names.add(path.name)
    return names


def functional_producer_name(name: str, canonical: set[str]) -> bool:
    return name.startswith("quality-") or name in canonical


def available_producer_paths(clone: Path) -> list[Path]:
    names = canonical_producer_names()
    return [
        path
        for path in sorted((clone / "var").glob("*.json"))
        if functional_producer_name(path.name, names)
    ]


def captured_manifest(path: Path) -> dict:
    if path.is_symlink() or path.is_junction() or not path.is_file():
        raise RuntimeError("a regular original capture manifest is required")
    document = json.loads(path.read_bytes())
    if (
        type(document) is not dict
        or document.get("kind") != "RAW_PRODUCER_CAPTURE_NOT_ACCEPTANCE"
        or document.get("gateVerdictIssued") is not False
        or document.get("refusedReports") != []
        or type(document.get("reports")) is not list
        or any(type(row) is not dict for row in document["reports"])
    ):
        raise RuntimeError("safe neutral original capture is required")
    return document


def captured_original_bytes(directory: Path, row: dict) -> bytes:
    from ledger_common import find_secrets

    name = row.get("archive")
    if (
        type(name) is not str
        or not name
        or Path(name).name != name
        or any(character in name for character in ("/", "\\", ":"))
        or any(ord(character) < 32 for character in name)
    ):
        raise RuntimeError("unsafe archived producer path")
    path = directory / name
    if (
        path.is_symlink()
        or path.is_junction()
        or not path.is_file()
        or not path.resolve().is_relative_to(directory.resolve())
    ):
        raise RuntimeError("redirected or missing original producer")
    raw = path.read_bytes()
    if (
        type(row.get("bytes")) is not int
        or row["bytes"] <= 0
        or type(row.get("sha256")) is not str
        or re.fullmatch(r"[0-9a-f]{64}", row["sha256"]) is None
        or len(raw) != row["bytes"]
        or hashlib.sha256(raw).hexdigest() != row["sha256"]
        or find_secrets(raw.decode("utf-8", errors="strict"))
    ):
        raise RuntimeError("archived producer bytes or privacy do not match")
    return raw


def forward_functional_producers(manifest: Path, target: Path) -> dict:
    names = canonical_producer_names()
    document = captured_manifest(manifest)
    pending = {}
    for row in document["reports"]:
        name = row.get("producerName")
        if type(name) is not str or not functional_producer_name(name, names):
            continue
        if (
            Path(name).name != name
            or any(value in name for value in ("/", "\\", ":"))
            or any(ord(character) < 32 for character in name)
            or name in pending
        ):
            raise RuntimeError("unsafe or duplicated functional producer identity")
        raw = captured_original_bytes(manifest.parent, row)
        value = json.loads(raw)
        if type(value) is not dict:
            raise RuntimeError("a functional producer must be a JSON object")
        pending[name] = (raw, value)
    if target.is_symlink() or target.is_junction():
        raise RuntimeError("redirected forwarding destination")
    target.mkdir(parents=True, exist_ok=True)
    for name in pending:
        path = target / name
        if path.is_symlink() or path.is_junction():
            raise RuntimeError("redirected functional output")
        if path.exists() and (not path.is_file() or path.stat().st_nlink != 1):
            raise RuntimeError("functional output must be an owned regular unlinked file")
    # Validate every source before the first effect; never consult a previous target report.
    for name, (raw, _value) in pending.items():
        path = target / name
        path.write_bytes(raw)
        if path.read_bytes() != raw:
            raise RuntimeError("forwarded original byte equality failed")
    return {name: value for name, (_raw, value) in pending.items()}


def container_states() -> dict[str, bool]:
    identities = command(["docker", "ps", "-aq", "--no-trunc"], ROOT).splitlines()
    if not identities:
        return {}
    rows = command(
        ["docker", "inspect", "--format", "{{.Id}} {{.State.Running}}", *identities], ROOT
    )
    return {
        identifier: state == "true"
        for identifier, state in (line.split() for line in rows.splitlines())
    }


@contextmanager
def verification_directory():
    # Git pack files can be read-only on Windows. TemporaryDirectory's standard cleanup
    # handles that attribute; native profile sharing-lock retries are a different boundary.
    facts = {"path": None, "removed": False, "cleanupRetries": None}
    directory = None
    try:
        with tempfile.TemporaryDirectory(prefix="iacode-gate7-full-verification-") as raw:
            directory = Path(raw)
            if (
                directory.resolve().parent != Path(tempfile.gettempdir()).resolve()
                or not directory.name.startswith("iacode-gate7-full-verification-")
                or directory.is_symlink()
                or directory.is_junction()
            ):
                raise ValueError("unexpected freshly created Git clone directory")
            facts["path"] = directory
            yield facts
    finally:
        if directory is not None:
            facts["removed"] = not directory.exists()


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8", newline="\n")


def summarize_stages(verification: dict) -> tuple[int, int, int]:
    """Consume the current producer vocabulary and result field, never a sealed denominator."""
    expected = [stage.name for stage in build_stages(False)]
    stages = verification.get("stages", [])
    if [row.get("name") for row in stages] != expected:
        raise RuntimeError(
            "verification stage vocabulary is incomplete, duplicated or out of order"
        )
    if any(row.get("result") not in {"PASS", "FAIL"} for row in stages):
        raise RuntimeError("verification stage result is missing or unknown")
    passed = sum(row["result"] == "PASS" for row in stages)
    failed = len(stages) - passed
    if verification.get("result") not in {"PASS", "FAIL"} or (
        verification["result"] == "PASS" and failed
    ):
        raise RuntimeError("verification top-level result contradicts its stage results")
    return len(expected), passed, failed


def capture_producer_reports(
    clone: Path,
    verifier_report: Path,
    archive: Path,
    subject: str,
) -> Path:
    """Retain safe original bytes before fallible interpretation and temporary-owner cleanup."""
    from ledger_common import find_secrets

    archive.mkdir(parents=True, exist_ok=True)
    if archive.is_symlink() or archive.is_junction():
        raise RuntimeError("refusing redirected producer archive")
    prefix = "FULL-PRODUCER-" + uuid.uuid4().hex[:12]
    candidates = [verifier_report, *available_producer_paths(clone)]
    reports, refused = [], []
    for path in candidates:
        if not path.is_file():
            continue
        if path.is_symlink() or not path.resolve().is_relative_to(clone.resolve()):
            raise RuntimeError("refusing redirected producer report")
        content = path.read_bytes()
        identity = {
            "producerName": path.name,
            "bytes": len(content),
            "sha256": hashlib.sha256(content).hexdigest(),
        }
        try:
            unsafe = bool(find_secrets(content.decode("utf-8")))
        except (UnicodeError, ValueError):
            refused.append({**identity, "reason": "UNSCANNABLE"})
            continue
        if unsafe:
            refused.append({**identity, "reason": "SECRET_MATERIAL"})
            continue
        destination = archive / (prefix + "-" + path.name)
        with destination.open("xb") as output:
            output.write(content)
        if destination.read_bytes() != content:
            raise RuntimeError("producer archive byte equality failed")
        reports.append({**identity, "archive": destination.name})
    manifest = archive / (prefix + "-MANIFEST.json")
    write_json(
        manifest,
        {
            "kind": "RAW_PRODUCER_CAPTURE_NOT_ACCEPTANCE",
            "subjectCommit": subject,
            "gateVerdictIssued": False,
            "reports": reports,
            "refusedReports": refused,
        },
    )
    if refused:
        raise RuntimeError(
            "producer capture refused unsafe artifact(s); neutral inventory retained"
        )
    return manifest


def command(arguments: list[str], cwd: Path) -> str:
    from current_resources import child_environment

    environment = child_environment()
    environment.update(
        GIT_TERMINAL_PROMPT="0", GCM_INTERACTIVE="Never", GIT_ASKPASS="", SSH_ASKPASS=""
    )
    if arguments[0] == "git" and "clone" in arguments:
        arguments = ["git", "-c", "credential.helper=", "-c", "core.askPass=", *arguments[1:]]
    result = subprocess.run(
        arguments,
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
        env=environment,
    )
    if result.returncode:
        raise RuntimeError(f"verification setup failed: {arguments[0]} exit={result.returncode}")
    return result.stdout.strip()


def collect_producer_observations(
    clone: Path,
    verifier_report: Path,
    archive: Path,
    subject: str,
) -> tuple[dict, tuple[int, int, int], Path]:
    """The actual publisher boundary preserves originals before any interpretation can fail."""
    manifest = capture_producer_reports(clone, verifier_report, archive, subject)
    document = captured_manifest(manifest)
    originals = [
        row for row in document["reports"] if row.get("producerName") == verifier_report.name
    ]
    if len(originals) != 1:
        raise RuntimeError("the complete verifier produced no report; available originals retained")
    verification = json.loads(captured_original_bytes(manifest.parent, originals[0]))
    summary = summarize_stages(verification)
    if verification["result"] == "PASS":
        captured = {row.get("producerName") for row in document["reports"]}
        if canonical_producer_names() - captured:
            raise RuntimeError(
                "successful verification lacks a canonical producer; originals retained"
            )
    return verification, summary, manifest


def main() -> int:
    from audit_runner_bridge import Job, run_owned
    from current_resources import child_environment, current_scope_path
    from ledger_common import find_secrets, load_json, scope_fingerprint
    from native_process import WindowsJob
    from verify import verification_environment

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--tag", required=True)
    parser.add_argument("--node", type=Path, required=True)
    args = parser.parse_args()
    if not re.fullmatch(r"[0-9a-f]{40}", args.commit) or not re.fullmatch(
        r"iacode-subjects/GATE-7-CP-0003-runtime-v[1-9][0-9]*", args.tag
    ):
        raise RuntimeError("an exact current Gate7 immutable subject commit/tag is required")
    if not args.node.is_file():
        raise RuntimeError("explicit supported Node executable required")
    destination = CHECKPOINT / "VERIFY.json"
    if destination.exists():
        raise RuntimeError("preserve the previous complete verification before another attempt")
    source = ROOT / "docs/checkpoints/GATE-4-CP-0006/RUN-INDEPENDENT-FULL-VERIFICATION.py"
    spec = importlib.util.spec_from_file_location("gate7_isolation", source)
    if spec is None or spec.loader is None:
        raise RuntimeError("the canonical isolation probe cannot be loaded")
    probe = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(probe)
    before = probe.snapshot_project("iacode")
    unrelated_before = container_states()
    fingerprint = scope_fingerprint(ROOT)
    with verification_directory() as owner:
        directory = owner["path"]
        clone = Path(directory) / "repository"
        command(
            ["git", "-c", "core.longpaths=true", "clone", "--no-local", REMOTE, str(clone)],
            Path(directory),
        )
        command(["git", "checkout", "--detach", args.tag], clone)
        observed = command(["git", "rev-parse", "HEAD"], clone)
        if (
            observed != args.commit
            or command(["git", "rev-parse", "origin/main"], clone) != args.commit
        ):
            raise RuntimeError("the published subject is not the requested remote main/tag commit")
        if command(["git", "status", "--porcelain"], clone):
            raise RuntimeError("the fresh transported subject is not clean")
        if scope_fingerprint(clone) != fingerprint:
            raise RuntimeError(
                "the exact transported canonical sources differ from the current source"
            )
        environment = child_environment()
        temporary_children = Path(directory) / "temporary"
        temporary_children.mkdir()
        environment.update(TMP=str(temporary_children), TEMP=str(temporary_children))
        project = verification_environment(clone, environment)["COMPOSE_PROJECT_NAME"]
        scope_path = current_scope_path()
        scope = load_json(scope_path)
        if project in scope["registeredProjects"]:
            raise RuntimeError("fresh verifier namespace already registered")
        scope["registeredProjects"].append(project)
        scope.setdefault("projectOwners", []).append(
            {
                "project": project,
                "checkout": str(clone),
                "subjectCommit": observed,
                "source": "canonical verification_environment before producer launch",
            }
        )
        write_json(scope_path, scope)
        shutil.copy2(ROOT / "infra/compose/.env", clone / "infra/compose/.env")
        if command(["git", "status", "--porcelain"], clone):
            raise RuntimeError("ignored workstation configuration changed the transported tree")
        report_path = clone / "artifacts/review/INTERNAL-FULL-VERIFY.json"
        arguments = [
            sys.executable,
            "scripts/iacode/verify.py",
            "--keep-going",
            "--quiet",
            "--node",
            str(args.node.resolve()),
            "--report",
            report_path.relative_to(clone).as_posix(),
        ]
        execution = None
        try:
            # The real complete verifier owns an exact suspended/attached process tree.
            # Snapshot the actual producer before fallible report parsing or clone cleanup.
            execution, streams = run_owned(
                Job(tuple(arguments), 43200), clone, environment, find_secrets, WindowsJob
            )
            archive = CHECKPOINT / "full-verifier-executions" / uuid.uuid4().hex
            archive.mkdir(parents=True)
            for name, raw in streams.items():
                with (archive / name).open("xb") as output:
                    output.write(raw)
            execution.update(
                subjectCommit=observed,
                subjectTag=args.tag,
                sourceFingerprint=fingerprint,
                composeProject=project,
                sourceUnchanged=scope_fingerprint(ROOT) == fingerprint,
            )
            write_json(archive / "EXECUTION.json", execution)
            exit_code = execution["producer"]["exitCode"]
        finally:
            verification, summary, manifest = collect_producer_observations(
                clone, report_path, CHECKPOINT / "attempts", observed
            )
            write_json(
                CHECKPOINT / "PRODUCER-REPORTS.json",
                {
                    "subjectCommit": observed,
                    "manifest": manifest.relative_to(CHECKPOINT).as_posix(),
                    "gateVerdictIssued": False,
                },
            )
        write_json(destination, verification)
        scenarios = forward_functional_producers(manifest, ROOT / "var")
        write_json(
            CHECKPOINT / "FUNCTIONAL-SCENARIOS.json",
            {
                "subjectCommit": observed,
                "source": "single full verifier invocation",
                "scenarios": scenarios,
            },
        )
        stage_count, passed, failed = summary
        isolation = verification.get("isolation") or {}
        after = probe.snapshot_project("iacode")
        unrelated_after = container_states()
        unrelated_preserved = all(
            unrelated_after.get(identifier) == state
            for identifier, state in unrelated_before.items()
        )
        project = isolation.get("composeProject")
        owned = probe.snapshot_project(str(project)) if project else None
        removed = bool(
            owned and not any(owned[kind] for kind in ("containers", "volumes", "networks"))
        )
        clean = not command(["git", "status", "--porcelain"], clone)
        write_json(
            CHECKPOINT / "COMPOSE-ISOLATION-AUDIT.json",
            {
                "sharedBefore": before,
                "sharedAfter": after,
                "sharedUnchanged": before == after,
                "ownedAfter": owned,
                "ownedRemoved": removed,
                "unrelatedBefore": unrelated_before,
                "unrelatedAfter": unrelated_after,
                "unrelatedContainerIdentitiesAndStatesPreserved": unrelated_preserved,
                "result": "PASS" if before == after and removed and unrelated_preserved else "FAIL",
            },
        )
        report = {
            "schemaVersion": "1.0.0",
            "reviewKind": "SAME_SESSION_INTERNAL_REVIEW",
            "publishedCommit": observed,
            "subjectTag": args.tag,
            "remoteMainEqualsCommit": True,
            "checkoutMode": "detached-subject-tag",
            "configuration": "ignored workstation environment copied without recording values",
            "cloneCredentialHelperDisabled": True,
            "cloneInteractivePromptsDisabled": True,
            "invocationCount": 1,
            "retryCount": 0,
            "verifierRerun": False,
            "stageDenominator": stage_count,
            "stagesPassed": passed,
            "stagesFailed": failed,
            "exitCode": exit_code,
            "sharedProjectUnchanged": before == after,
            "ownedComposeProjectRemoved": removed,
            "gitStateAfterVerificationClean": clean,
            "unrelatedContainerIdentitiesAndStatesPreserved": unrelated_preserved,
            "result": "PASS"
            if (
                exit_code == 0
                and execution is not None
                and execution["producer"]["status"] == "COMPLETED"
                and execution["cleanup"]["result"] == "PASS"
                and execution["sourceUnchanged"]
                and not any(execution["producer"][name]["refusal"] for name in ("stdout", "stderr"))
                and verification.get("result") == "PASS"
                and not failed
                and isolation.get("postRunCleanup") == "PASS"
                and before == after
                and removed
                and clean
                and unrelated_preserved
            )
            else "FAIL",
        }
    report["temporaryCloneRemoved"] = owner["removed"]
    report["directoryCleanupRetries"] = owner["cleanupRetries"]
    if not report["temporaryCloneRemoved"]:
        report["result"] = "FAIL"
    write_json(CHECKPOINT / "PUBLISHED-CLEAN-CLONE-REPORT.json", report)
    print(f"INTERNAL_PUBLISHED_FULL_VERIFICATION={report['result']} stages={passed}/{stage_count}")
    return 0 if report["result"] == "PASS" else 1


if __name__ == "__main__":
    sys.path.insert(0, str(ROOT / "scripts/development-ledger"))
    sys.path.insert(0, str(ROOT / "scripts/iacode"))
    from ledger_common import use_utf8_stdout

    use_utf8_stdout()
    raise SystemExit(main())
