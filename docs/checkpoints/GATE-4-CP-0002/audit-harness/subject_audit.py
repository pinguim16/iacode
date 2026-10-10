#!/usr/bin/env python3
"""Audit identity, bundle integrity, requirements and published state of the Gate 4 subject."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
SUBJECT = "GATE-4-CP-0001"
SUBJECT_PATH = ROOT / "docs" / "checkpoints" / SUBJECT
TAG = f"refs/tags/iacode-checkpoints/{SUBJECT}"
EXPECTED_COMMIT = "70a22e824705f414e0c295bbdf89187db9b391f7"
EXPECTED_BUNDLE_SHA256 = "af98bb766d34beaf82f1d9963fc77377816a3cad9a850671313c528ea8701df7"
REMOTE = "https://github.com/pinguim16/iacode.git"
sys.path.insert(0, str(ROOT / "scripts" / "development-ledger"))

from ledger_common import load_json, utc_now  # noqa: E402
from policies import expected_requirement_refs  # noqa: E402
from review_bundle import validate as validate_bundle  # noqa: E402


def git(*arguments: str) -> tuple[int, str]:
    completed = subprocess.run(
        ["git", *arguments], cwd=ROOT, text=True, encoding="utf-8", errors="replace",
        capture_output=True, check=False, timeout=900,
    )
    return completed.returncode, (completed.stdout or completed.stderr).strip()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path, required=True)
    arguments = parser.parse_args()
    checks: list[dict[str, object]] = []

    def check(identifier: str, expectation: str, observed: object, ok: bool,
              evidence: list[str]) -> None:
        checks.append({
            "id": identifier,
            "expectation": expectation,
            "observed": observed,
            "result": "PASS" if ok else "FAIL",
            "evidence": evidence,
        })
        print(f"[{'PASS' if ok else 'FAIL'}] {identifier}: {observed}")

    _code, local_commit = git("rev-parse", f"{TAG}^{{commit}}")
    _code, local_tree = git("rev-parse", f"{TAG}^{{tree}}")
    check(
        "G4A-SUBJECT-LOCAL",
        "canonical local subject tag resolves to the expected commit",
        {"tag": TAG, "commit": local_commit, "tree": local_tree},
        local_commit == EXPECTED_COMMIT and len(local_tree) == 40,
        ["git:local-subject-tag"],
    )

    _code, remote_lines = git("ls-remote", "origin", "refs/heads/main", TAG)
    remote_refs = {}
    for line in remote_lines.splitlines():
        commit, _, ref = line.partition("\t")
        remote_refs[ref] = commit
    remote_ok = (
        remote_refs.get("refs/heads/main") == EXPECTED_COMMIT
        and remote_refs.get(TAG) == EXPECTED_COMMIT
    )
    check(
        "G4A-SUBJECT-REMOTE",
        "published main and subject tag resolve to the exact subject commit",
        remote_refs,
        remote_ok,
        ["git:ls-remote-origin"],
    )

    _code, remote_url = git("remote", "get-url", "origin")
    check(
        "G4A-REMOTE-IDENTITY",
        "origin is the authorised public remote",
        remote_url,
        remote_url == REMOTE,
        ["git:remote-origin"],
    )

    state = load_json(SUBJECT_PATH / "STATE.json")
    check(
        "G4A-SUBJECT-STATE",
        "sealed subject is READY_FOR_REVIEW with pending independent verdicts and no blocker",
        {
            "status": state.get("status"),
            "currentCommit": state.get("currentCommit"),
            "blockedBy": state.get("blockedBy"),
            "secondToolValidation": (state.get("secondToolValidation") or {}).get("status"),
            "independentReview": (state.get("independentReview") or {}).get("status"),
            "redTeam": (state.get("redTeam") or {}).get("status"),
        },
        (
            state.get("status") == "READY_FOR_REVIEW"
            and state.get("currentCommit") == TAG
            and state.get("blockedBy") == []
            and (state.get("secondToolValidation") or {}).get("status") == "PENDING_MANUAL"
            and (state.get("independentReview") or {}).get("status") == "PENDING"
            and (state.get("redTeam") or {}).get("status") == "PENDING"
        ),
        [f"file:docs/checkpoints/{SUBJECT}/STATE.json"],
    )

    bundle = ROOT / "artifacts" / "review" / f"{SUBJECT}-sealed.zip"
    observed_digest = hashlib.sha256(bundle.read_bytes()).hexdigest() if bundle.is_file() else None
    validation = validate_bundle(ROOT, SUBJECT_PATH, bundle) if bundle.is_file() else {
        "result": "FAIL", "findings": ["bundle does not exist"]}
    check(
        "G4A-SEALED-BUNDLE",
        "sealed bundle has the handed-off digest and passes independent structural validation",
        {
            "path": str(bundle),
            "sha256": observed_digest,
            "validationResult": validation.get("result"),
            "entries": validation.get("entries"),
            "findings": validation.get("findings"),
        },
        observed_digest == EXPECTED_BUNDLE_SHA256 and validation.get("result") == "PASS",
        ["artifact:artifacts/review/GATE-4-CP-0001-sealed.zip"],
    )

    matrix = load_json(SUBJECT_PATH / "REQUIREMENTS-MATRIX.json")
    requirements = matrix.get("requirements") or []
    actual_refs = {str(item.get("sourceRef")) for item in requirements}
    subject_preflight = load_json(SUBJECT_PATH / "LESSON-PREFLIGHT.json")
    expected_refs = set(expected_requirement_refs(ROOT, "GATE-4", SUBJECT, subject_preflight))
    complete = [item for item in requirements if item.get("status") == "COMPLETE"]
    evidence_shapes_ok = all(
        item.get("implementationEvidence")
        and item.get("validationEvidence")
        and item.get("documentationEvidence")
        for item in requirements
    )
    check(
        "G4A-SUBJECT-DENOMINATOR",
        "subject matrix equals the independently derived expected set and every row is complete",
        {
            "actual": len(actual_refs),
            "expected": len(expected_refs),
            "missing": sorted(expected_refs - actual_refs),
            "extra": sorted(actual_refs - expected_refs),
            "complete": len(complete),
            "rowsWithRequiredEvidenceShape": evidence_shapes_ok,
        },
        (
            len(requirements) == 194
            and actual_refs == expected_refs
            and len(complete) == len(requirements)
            and evidence_shapes_ok
        ),
        [f"file:docs/checkpoints/{SUBJECT}/REQUIREMENTS-MATRIX.json"],
    )

    counts = load_json(SUBJECT_PATH / "COUNTS.json").get("counts") or {}
    count_ok = (
        (counts.get("TESTS") or {}).get("numerator") == 1675
        and (counts.get("TESTS") or {}).get("denominator") == 1675
        and (counts.get("REQUIREMENTS") or {}).get("numerator") == 194
        and (counts.get("REQUIREMENTS") or {}).get("denominator") == 194
        and (counts.get("ATTACKS") or {}).get("numerator") == 10
        and (counts.get("ATTACKS") or {}).get("denominator") == 10
    )
    check(
        "G4A-SUBJECT-COUNTS",
        "subject counts preserve the delivered test, requirement and attack denominators",
        counts,
        count_ok,
        [f"file:docs/checkpoints/{SUBJECT}/COUNTS.json"],
    )

    verify = load_json(SUBJECT_PATH / "VERIFY.json")
    stages = verify.get("stages") or []
    check(
        "G4A-SUBJECT-VERIFICATION-CLAIM",
        "subject records a complete passing 42-stage verification for later reproduction",
        {
            "result": verify.get("result"),
            "stages": len(stages),
            "passed": sum(1 for item in stages if item.get("result") == "PASS"),
        },
        verify.get("result") == "PASS" and len(stages) == 42
        and all(item.get("result") == "PASS" for item in stages),
        [f"file:docs/checkpoints/{SUBJECT}/VERIFY.json"],
    )

    failed = [item for item in checks if item["result"] != "PASS"]
    document = {
        "schemaVersion": "1.0.0",
        "artifact": "GATE-4-SEALED-SUBJECT-AUDIT",
        "checkpoint": CHECKPOINT.name,
        "subjectCheckpoint": SUBJECT,
        "subjectTag": TAG,
        "subjectCommit": EXPECTED_COMMIT,
        "generatedAt": utc_now(),
        "checks": checks,
        "passed": len(checks) - len(failed),
        "total": len(checks),
        "result": "PASS" if not failed else "FAIL",
    }
    report = arguments.report.resolve()
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(
        json.dumps(document, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(f"SEALED_SUBJECT_AUDIT={document['result']} {document['passed']}/{document['total']}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
