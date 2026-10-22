"""Reconstruct the G4-F-004 red/green subjects and final M2 review transport from public clones."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from typing import Any
import zipfile


REMOTE = "https://github.com/pinguim16/iacode.git"
CASES = (
    {
        "id": "g4-cp0007-historical-red",
        "checkpoint": "GATE-4-CP-0007",
        "tag": "refs/tags/iacode-checkpoints/GATE-4-CP-0007",
        "tagCommit": "e21d30fde473f302d0f8f60b59acf008fa52e250",
        "expectedDeclarationMatch": False,
        "expectedRebuiltSha256": "07bb328a4316297d0b6bd2df986c7b5f5fb41b30c8b2fb58cd99a8d96c24c168",
        "expectedRebuiltSize": 751518,
    },
    {
        "id": "g4-cp0009-corrective-green",
        "checkpoint": "GATE-4-CP-0009",
        "tag": "refs/tags/iacode-checkpoints/GATE-4-CP-0009",
        "tagCommit": "ff2814f7d7bf06fa8a99858b958daf3f22197496",
        "expectedDeclarationMatch": True,
    },
    {
        "id": "g7-cp0001-final-green",
        "checkpoint": "GATE-7-CP-0001",
        "tag": "refs/tags/iacode-checkpoints/GATE-7-CP-0001",
        "tagCommit": "823cf164c6931dab7f957c92721ded7a916655bd",
        "expectedDeclarationMatch": True,
    },
)


def _run(argv: list[str], cwd: Path, env: dict[str, str]) -> dict[str, Any]:
    started = time.monotonic()
    completed = subprocess.run(
        argv,
        cwd=cwd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return {
        "arguments": argv,
        "workingDirectory": str(cwd),
        "durationMs": int((time.monotonic() - started) * 1000),
        "exitCode": completed.returncode,
        "stdout": completed.stdout.decode("utf-8", errors="replace")[-32768:],
        "stderr": completed.stderr.decode("utf-8", errors="replace")[-32768:],
    }


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--owner-root", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--case", choices=[item["id"] for item in CASES], action="append")
    args = parser.parse_args()

    owner_root = args.owner_root.resolve()
    if owner_root.exists():
        raise RuntimeError(f"exclusive owner root already exists: {owner_root}")
    owner_root.mkdir(parents=True)
    env = os.environ.copy()
    env.update({
        "GIT_TERMINAL_PROMPT": "0",
        "GCM_INTERACTIVE": "Never",
        "GIT_CONFIG_COUNT": "3",
        "GIT_CONFIG_KEY_0": "core.longpaths",
        "GIT_CONFIG_VALUE_0": "true",
        "GIT_CONFIG_KEY_1": "http.sslBackend",
        "GIT_CONFIG_VALUE_1": "openssl",
        "GIT_CONFIG_KEY_2": "credential.helper",
        "GIT_CONFIG_VALUE_2": "",
    })
    case_reports: list[dict[str, Any]] = []
    overall = True

    selected_cases = tuple(
        case for case in CASES if not args.case or case["id"] in set(args.case)
    )
    for case in selected_cases:
        builds: list[dict[str, Any]] = []
        for suffix in ("a", "b"):
            repository = owner_root / case["id"] / suffix / "repository"
            repository.parent.mkdir(parents=True)
            steps: list[dict[str, Any]] = []
            clone = _run([
                "git", "-c", "core.longpaths=true", "-c", "http.sslBackend=openssl",
                "-c", "credential.helper=",
                "clone", "--quiet", "--no-local", REMOTE, str(repository),
            ], owner_root, env)
            steps.append(clone)
            if clone["exitCode"] != 0:
                builds.append({"clone": str(repository), "steps": steps, "result": "FAIL"})
                overall = False
                continue
            checkout = _run([
                "git", "checkout", "--quiet", "--detach", case["tag"],
            ], repository, env)
            steps.append(checkout)
            head = _run(["git", "rev-parse", "HEAD"], repository, env)
            steps.append(head)
            head_value = head["stdout"].strip()
            identity_ok = checkout["exitCode"] == 0 and head_value == case["tagCommit"]

            validation = _run([
                sys.executable, "scripts/development-ledger/validate_checkpoint.py",
            ], repository, env)
            steps.append(validation)
            integrity = _run([
                sys.executable, "scripts/development-ledger/verify_integrity.py",
            ], repository, env)
            steps.append(integrity)

            checkpoint_path = repository / "docs" / "checkpoints" / case["checkpoint"]
            declaration_path = checkpoint_path / "REVIEW-BUNDLE-VALIDATION.json"
            declaration = json.loads(declaration_path.read_text(encoding="utf-8"))
            bundle = repository / "artifacts" / "review" / "independent-rebuild.zip"
            producer = [
                sys.executable,
                "scripts/development-ledger/review_bundle.py",
                "--checkpoint", f"docs/checkpoints/{case['checkpoint']}",
                "--bundle", "artifacts/review/independent-rebuild.zip",
            ]
            subject = declaration.get("subject")
            if isinstance(subject, dict) and subject.get("commit"):
                producer.extend(["--subject", str(subject["commit"])])
            production = _run(producer, repository, env)
            steps.append(production)

            if bundle.is_file():
                with zipfile.ZipFile(bundle, "r") as archive:
                    entries = len(archive.infolist())
                    crc_failure = archive.testzip()
                digest = _sha256(bundle)
                size = bundle.stat().st_size
            else:
                entries = None
                crc_failure = "bundle absent"
                digest = None
                size = None
            build_ok = (
                identity_ok
                and validation["exitCode"] == 0
                and integrity["exitCode"] == 0
                and production["exitCode"] == 0
                and crc_failure is None
            )
            overall = overall and build_ok
            builds.append({
                "clone": str(repository),
                "tag": case["tag"],
                "head": head_value,
                "declaration": {
                    "schemaVersion": declaration.get("schemaVersion"),
                    "sha256": declaration.get("sha256"),
                    "sizeBytes": declaration.get("sizeBytes"),
                    "entries": declaration.get("entries"),
                    "subject": declaration.get("subject"),
                },
                "bundle": str(bundle),
                "sha256": digest,
                "sizeBytes": size,
                "entries": entries,
                "crcFailure": crc_failure,
                "steps": steps,
                "result": "PASS" if build_ok else "FAIL",
            })

        complete = len(builds) == 2 and all(build.get("result") == "PASS" for build in builds)
        byte_identical = complete and builds[0]["sha256"] == builds[1]["sha256"]
        declarations = [build.get("declaration", {}) for build in builds]
        declaration_match = complete and all(
            build["sha256"] == build["declaration"].get("sha256")
            and build["sizeBytes"] == build["declaration"].get("sizeBytes")
            and build["entries"] == build["declaration"].get("entries")
            for build in builds
        )
        expectations = byte_identical and declaration_match == case["expectedDeclarationMatch"]
        if "expectedRebuiltSha256" in case:
            expectations = expectations and all(
                build.get("sha256") == case["expectedRebuiltSha256"]
                and build.get("sizeBytes") == case["expectedRebuiltSize"]
                for build in builds
            )
        overall = overall and bool(expectations)
        case_reports.append({
            "id": case["id"],
            "checkpoint": case["checkpoint"],
            "tag": case["tag"],
            "tagCommit": case["tagCommit"],
            "expectedDeclarationMatch": case["expectedDeclarationMatch"],
            "builds": builds,
            "byteIdentical": bool(byte_identical),
            "declarationMatchesRebuilds": bool(declaration_match),
            "expectationsSatisfied": bool(expectations),
            "result": "PASS" if expectations else "FAIL",
        })

    report = {
        "schemaVersion": "1.0.0",
        "artifact": "M2_INDEPENDENT_REVIEW_TRANSPORT_RECONSTRUCTION",
        "remote": REMOTE,
        "credentialsDisabled": True,
        "ownerRoot": str(owner_root),
        "retained": True,
        "cases": case_reports,
        "result": "PASS" if overall else "FAIL",
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    for case in case_reports:
        digest = case["builds"][0].get("sha256") if case["builds"] else None
        print(
            f"{case['id']} result={case['result']} byte_identical={case['byteIdentical']} "
            f"declaration_match={case['declarationMatchesRebuilds']} sha256={digest}"
        )
    print(f"M2_REVIEW_TRANSPORT_RECONSTRUCTION={'PASS' if overall else 'FAIL'}")
    return 0 if overall else 1


if __name__ == "__main__":
    raise SystemExit(main())
