#!/usr/bin/env python3
"""Build the post-seal review bundle for GATE-3-CP-0006.

Only public repository artifacts required to reproduce or review the audit are included. Ignored
configuration, provider credentials, prompts, completions, runtime databases and backup data are
excluded by construction.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path

CHECKPOINT_ID = "GATE-3-CP-0006"
BASE_COMMIT = "3ef2bf77ddbddd378d35f5c4d32f2d90d42fc97d"
ROOT = Path(__file__).resolve().parents[4]

SAFE_FILES = [
    ".iacode/anchors/checkpoint-chain.json",
    ".iacode/attestations/M1-CP-0006.json",
    ".iacode/memory/LESSONS.md",
    ".iacode/memory/guardrails/registry.json",
    ".iacode/memory/lessons.jsonl",
    ".iacode/policies/audit-registry.json",
    ".iacode/policies/quality-gates.json",
    ".iacode/policies/test-suites.json",
    "AGENTS.md",
    "START-HERE.md",
    "apps/web/package.json",
    "apps/web/package-lock.json",
    "docs/DEVELOPMENT-CONTRACT.md",
    "docs/MASTER-PLAN.md",
    "docs/MILESTONE-VALIDATION.md",
    "scripts/iacode/dependency_scan.py",
    "scripts/iacode/verify.py",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git(*arguments: str) -> str:
    return subprocess.run(
        ["git", *arguments], cwd=ROOT, check=True, capture_output=True,
        text=True, encoding="utf-8", errors="replace",
    ).stdout


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--final-commit", required=True)
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args()

    checkpoint = ROOT / "docs" / "checkpoints" / CHECKPOINT_ID
    paths = [ROOT / item for item in SAFE_FILES]
    paths.extend(sorted(path for path in checkpoint.rglob("*") if path.is_file()
                        and "__pycache__" not in path.parts))
    missing = [str(path.relative_to(ROOT)) for path in paths if not path.is_file()]
    if missing:
        raise SystemExit(f"missing required review artifact(s): {missing}")

    output = arguments.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="iacode-review-") as temporary:
        staging = Path(temporary)
        for source in paths:
            relative = source.relative_to(ROOT)
            destination = staging / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(source.read_bytes())

        generated = {
            "CHANGESET.patch": git("diff", "--binary", BASE_COMMIT, arguments.final_commit),
            "GIT-LOG.txt": git("log", "--decorate", "--oneline", "--graph", "--all", "-80"),
            "REMOTE-STATE.txt": (
                f"generatedAt: {utc_now()}\n"
                f"origin: {git('remote', 'get-url', 'origin').strip()}\n"
                f"local HEAD: {git('rev-parse', 'HEAD').strip()}\n"
                f"local branch: {git('branch', '--show-current').strip()}\n"
                "remote refs:\n"
                + git("ls-remote", "--heads", "--tags", "origin",
                      "main", f"refs/tags/iacode-checkpoints/{CHECKPOINT_ID}")
            ),
        }
        for name, content in generated.items():
            (staging / name).write_text(content, encoding="utf-8", newline="\n")

        included = []
        payload_files = sorted(path for path in staging.rglob("*") if path.is_file())
        for path in payload_files:
            relative = str(path.relative_to(staging)).replace("\\", "/")
            included.append({"path": relative, "sha256": sha256(path),
                             "bytes": path.stat().st_size})

        tests = json.loads((checkpoint / "TESTS.json").read_text(encoding="utf-8"))
        quality = json.loads((checkpoint / "QUALITY.json").read_text(encoding="utf-8"))
        manifest = {
            "schemaVersion": "1.0.0",
            "artifact": "REVIEW-BUNDLE-MANIFEST",
            "generatedAt": utc_now(),
            "checkpoint": CHECKPOINT_ID,
            "gate": "GATE-3",
            "milestone": "M1",
            "status": json.loads((checkpoint / "STATE.json").read_text(encoding="utf-8"))["status"],
            "baseCommit": BASE_COMMIT,
            "finalCommit": arguments.final_commit,
            "tag": f"refs/tags/iacode-checkpoints/{CHECKPOINT_ID}",
            "branch": "main",
            "remote": git("remote", "get-url", "origin").strip(),
            "requirementsCount": json.loads((checkpoint / "STATE.json").read_text(encoding="utf-8"))["requirementsMatrix"]["total"],
            "testsSummary": tests,
            "qualitySummary": {key: value["status"]
                               for key, value in quality["checks"].items()},
            "summaries": [
                "STATE.json", "TESTS.json", "QUALITY.json", "COUNTS.json",
                "COMPLETENESS-REPORT.json", "VERIFICATION-REPORT.json",
                "DEPENDENCY-SCAN-REPORT.json", "FINDINGS.json", "FINAL-REPORT.md",
            ],
            "filesIncluded": included,
            "filesExcluded": [
                "infra/compose/.env", "var/", "artifacts/backups/", "provider prompts and completions",
            ],
            "exclusionReasons": {
                "infra/compose/.env": "ignored runtime configuration may contain credentials",
                "var/": "runtime and transient evidence is not part of the sealed checkpoint",
                "artifacts/backups/": "operational data is outside review scope",
                "provider prompts and completions": "the audit stores neither",
            },
        }
        (staging / "REVIEW-BUNDLE-MANIFEST.json").write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8", newline="\n")

        sum_paths = sorted(path for path in staging.rglob("*") if path.is_file()
                           and path.name != "SHA256SUMS.txt")
        sums = "".join(
            f"{sha256(path)}  {str(path.relative_to(staging)).replace(chr(92), '/')}\n"
            for path in sum_paths
        )
        (staging / "SHA256SUMS.txt").write_text(sums, encoding="utf-8", newline="\n")

        with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED,
                             compresslevel=9) as archive:
            for path in sorted(path for path in staging.rglob("*") if path.is_file()):
                archive.write(path, str(path.relative_to(staging)).replace("\\", "/"))

    digest = sha256(output)
    sidecar = Path(str(output) + ".sha256")
    sidecar.write_text(f"{digest}  {output.name}\n", encoding="utf-8", newline="\n")
    print(f"REVIEW_BUNDLE={output} sha256={digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
