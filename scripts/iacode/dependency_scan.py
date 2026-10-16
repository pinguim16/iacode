#!/usr/bin/env python3
"""Scan the pinned dependencies for known vulnerabilities.

`docs/GATE-0-CHECKLIST.md` row 13.9: a scan is executed, or its absence is justified, and relevant
Critical and High findings block the Gate.

Two ecosystems, two scanners, each the one its ecosystem ships:

``frontend``  ``npm audit``, which resolves `package-lock.json` against the npm advisory database.
``backend``   ``pip-audit`` against `requirements.lock.txt`, using the Python Packaging Advisory
              Database.

Both need network access to an advisory service. That is stated rather than hidden: a scanner that
silently reports "no vulnerabilities" because it could not reach its database is worse than one that
says it could not run. When a scanner cannot reach its source this exits **non-zero** with
``UNAVAILABLE``, so an offline run is a recorded absence rather than a forged pass.

    python scripts/iacode/dependency_scan.py
    python scripts/iacode/dependency_scan.py --json
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from client_checks import NODE_IMAGE
from compose import REPOSITORY_ROOT, log, main_guard, require_docker
from gates.web_tests import BUILDER_IMAGE, build_toolchain

PYTHON_IMAGE = "python:3.13.15-slim-bookworm"
PIP_AUDIT_VERSION = "2.9.0"

# Severities that block. `docs/checkpoints/GATE-0-CP-0001/PLAN.md` and the Gate prompt agree:
# Critical and High block, Medium and Low go to the backlog.
BLOCKING = {"critical", "high"}


def scan_frontend() -> dict[str, object]:
    build_toolchain()
    completed = subprocess.run(
        [
            "docker",
            "run",
            "--rm",
            "--workdir",
            "/build",
            BUILDER_IMAGE,
            "npm",
            "audit",
            "--json",
            "--audit-level=low",
        ],
        cwd=str(REPOSITORY_ROOT),
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )
    try:
        payload = json.loads(completed.stdout or "{}")
    except json.JSONDecodeError:
        return {
            "ecosystem": "npm",
            "status": "UNAVAILABLE",
            "detail": (completed.stderr or completed.stdout).strip()[-400:],
        }
    if "error" in payload:
        return {"ecosystem": "npm", "status": "UNAVAILABLE", "detail": str(payload["error"])[:400]}

    severities: dict[str, int] = (payload.get("metadata") or {}).get("vulnerabilities") or {}
    findings = [
        {
            "name": name,
            "severity": str(item.get("severity", "unknown")).lower(),
            "via": [
                entry if isinstance(entry, str) else entry.get("title", "")
                for entry in item.get("via", [])
            ][:3],
        }
        for name, item in (payload.get("vulnerabilities") or {}).items()
    ]
    return {
        "ecosystem": "npm",
        "status": "SCANNED",
        "counts": {key: value for key, value in severities.items() if key != "total"},
        "blocking": [item for item in findings if item["severity"] in BLOCKING],
        "findings": findings,
    }


def scan_backend() -> dict[str, object]:
    lock = REPOSITORY_ROOT / "apps" / "api" / "requirements.lock.txt"
    completed = subprocess.run(
        [
            "docker",
            "run",
            "--rm",
            "--volume",
            f"{lock.parent}:/src:ro",
            PYTHON_IMAGE,
            "sh",
            "-c",
            f"pip install --no-cache-dir -q pip-audit=={PIP_AUDIT_VERSION} && "
            "pip-audit --requirement /src/requirements.lock.txt "
            "--format json --progress-spinner off",
        ],
        cwd=str(REPOSITORY_ROOT),
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )
    stdout = (completed.stdout or "").strip()
    if not stdout.startswith("{"):
        return {
            "ecosystem": "pypi",
            "status": "UNAVAILABLE",
            "detail": ((completed.stderr or "") + stdout).strip()[-400:],
        }
    payload = json.loads(stdout)

    findings = []
    for dependency in payload.get("dependencies", []):
        for vulnerability in dependency.get("vulns", []) or []:
            findings.append(
                {
                    "name": dependency.get("name"),
                    "version": dependency.get("version"),
                    "id": vulnerability.get("id"),
                    # The Python advisory database does not carry a severity for every entry, so the
                    # honest default is "unknown" — and an unknown severity is treated as blocking,
                    # because assuming the best about an advisory nobody has graded is backwards.
                    "severity": str(vulnerability.get("severity") or "unknown").lower(),
                    "fixVersions": vulnerability.get("fix_versions") or [],
                }
            )
    return {
        "ecosystem": "pypi",
        "status": "SCANNED",
        "counts": {"total": len(findings)},
        "blocking": [
            item
            for item in findings
            if item["severity"] in BLOCKING or item["severity"] == "unknown"
        ],
        "findings": findings,
    }


def scan_clients() -> list[dict[str, object]]:
    """Every delivered Node graph is inspected, including an explicitly empty graph."""
    results = []
    for name in ("cli", "vscode-extension"):
        root = REPOSITORY_ROOT / "apps" / name
        package = json.loads((root / "package.json").read_text(encoding="utf-8"))
        lock = json.loads((root / "package-lock.json").read_text(encoding="utf-8"))
        empty = (
            lock.get("lockfileVersion") == 3
            and set(lock.get("packages", {})) == {""}
            and all(
                not package.get(key)
                for key in ("dependencies", "devDependencies", "optionalDependencies")
            )
            and lock["packages"][""].get("name") == package.get("name")
            and lock["packages"][""].get("version") == package.get("version")
        )
        if not empty:
            results.append(
                {
                    "ecosystem": "npm-" + name,
                    "status": "UNAVAILABLE",
                    "detail": "dependency-free client graph changed; "
                    "explicit advisory coverage is required",
                }
            )
            continue
        checked = subprocess.run(
            [
                "docker",
                "run",
                "--rm",
                "--network",
                "none",
                "--read-only",
                "--tmpfs",
                "/tmp:rw,nosuid,nodev,size=32m",
                "--volume",
                f"{root}:/src:ro",
                "--workdir",
                "/tmp",
                NODE_IMAGE,
                "sh",
                "-c",
                "cp /src/package.json /src/package-lock.json . "
                "&& npm audit --offline --json --cache /tmp/cache",
            ],
            cwd=REPOSITORY_ROOT,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            check=False,
        )
        try:
            payload = json.loads(checked.stdout)
        except json.JSONDecodeError:
            payload = {}
        accepted = (
            checked.returncode == 0
            and payload.get("metadata", {}).get("vulnerabilities", {}).get("total") == 0
        )
        results.append(
            {
                "ecosystem": "npm-" + name,
                "status": "EMPTY_GRAPH_VALIDATED" if accepted else "UNAVAILABLE",
                "counts": {"thirdPartyDependencies": 0},
                "blocking": [],
                "findings": [],
                "detail": "No third-party advisory lookup applies to an empty graph; "
                "Node/VS Code runtime compatibility is tested separately.",
            }
        )
    return results


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--report", type=Path, default=None)
    arguments = parser.parse_args()

    require_docker()
    results = [scan_backend(), scan_frontend(), *scan_clients()]

    unavailable = [item for item in results if item["status"] == "UNAVAILABLE"]
    blocking = [finding for item in results for finding in item.get("blocking", [])]
    result = "FAIL" if blocking else ("UNAVAILABLE" if unavailable else "PASS")

    document = {
        "result": result,
        "blockingSeverities": sorted(BLOCKING),
        "scans": results,
    }
    if arguments.report:
        arguments.report.parent.mkdir(parents=True, exist_ok=True)
        arguments.report.write_text(
            json.dumps(document, indent=2) + "\n", encoding="utf-8", newline="\n"
        )
    if arguments.json:
        print(json.dumps(document, indent=2))
    else:
        for item in results:
            log(
                f"[{item['status']}] {item['ecosystem']}: "
                + (
                    str(item.get("detail"))
                    if item["status"] == "UNAVAILABLE"
                    else f"{item.get('counts')} blocking={len(item.get('blocking', []))}"
                )
            )
        for finding in blocking:
            log(
                f"  BLOCKING {finding.get('name')} {finding.get('id', '')} "
                f"severity={finding.get('severity')}"
            )
    log(f"DEPENDENCY_SCAN={result}")
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    main_guard(main)
