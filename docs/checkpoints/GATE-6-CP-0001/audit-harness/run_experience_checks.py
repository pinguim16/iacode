"""Preserve actual safe output before interpreting a current complete suite, fail-stop in order."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/iacode"))
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))

from compose import build_service, compose
from ledger_common import find_secrets, scope_fingerprint, utc_now, use_utf8_stdout, write_json


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--suite", choices=("domain", "api-unit", "both"), default="both")
    options = parser.parse_args()
    build_service("api")
    suites = ("domain", "api-unit") if options.suite == "both" else (options.suite,)
    for suite in suites:
        directory = CHECKPOINT / "suite-attempts"
        directory.mkdir(exist_ok=True)
        sequence = len(list(directory.glob(suite.upper() + "-*.json"))) + 1
        name = suite.upper() + f"-{sequence:04d}"
        target = "/app/experience_tests" if suite == "domain" else "/app/tests/unit"
        before = scope_fingerprint(ROOT)
        result = compose("run", "--rm", "--no-deps", "--entrypoint", "", "api", "python", "-m",
                         "pytest", target, "-p", "no:cacheprovider", "--no-header", capture=True)
        raw = result.output.encode("utf-8")
        findings = find_secrets(result.output)
        artifact = None
        if not findings:
            artifact = directory / (name + ".log")
            artifact.write_bytes(raw)
        summary = re.findall(r"(?:\d+ (?:passed|failed|errors?|skipped|warnings?))(?: in [0-9.]+s)?",
                             result.output)
        report = {"schemaVersion": "1.0.0", "suite": suite, "exitCode": result.exit_code,
                  "observedAt": utc_now(), "sourceFingerprint": before,
                  "sourceUnchanged": scope_fingerprint(ROOT) == before,
                  "outputBytes": len(raw), "outputSha256": hashlib.sha256(raw).hexdigest(),
                  "safeOutputArtifact": artifact.relative_to(ROOT).as_posix() if artifact else None,
                  "unsafeOutputOccurrences": len(findings), "summaryFragments": summary[-12:],
                  "result": "PASS" if result.ok else "FAIL"}
        write_json(directory / (name + ".json"), report)
        print(json.dumps(report, ensure_ascii=False))
        if not result.ok or not report["sourceUnchanged"]:
            return result.exit_code or 1
    return 0


if __name__ == "__main__":
    use_utf8_stdout()
    raise SystemExit(main())
