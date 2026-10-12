#!/usr/bin/env python3
"""Execute canonical A-T and bind attack T to transport-input refusal evidence."""

from __future__ import annotations

import argparse
import importlib.util
import json
from datetime import UTC, datetime
from pathlib import Path


CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
SUBJECT = ROOT / "docs" / "checkpoints" / "GATE-4-CP-0007"
SUBJECT_COMMIT = "e21d30fde473f302d0f8f60b59acf008fa52e250"
SOURCE = ROOT / "docs" / "checkpoints" / "GATE-4-CP-0006" / "audit-harness" / "independent_red_team.py"


def main() -> int:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--markdown", type=Path, required=True)
    parser.add_argument("--image", required=True)
    arguments, _ = parser.parse_known_args()
    specification = importlib.util.spec_from_file_location("gate4_cp0008_red_team", SOURCE)
    if specification is None or specification.loader is None:
        raise RuntimeError("the established independent Red Team harness could not be loaded")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    module.CHECKPOINT = CHECKPOINT
    module.ROOT = ROOT
    module.SUBJECT = SUBJECT
    base_result = int(module.main())

    report = json.loads(arguments.report.resolve().read_text(encoding="utf-8"))
    transport = json.loads((CHECKPOINT / "TRANSPORT-ATTACKS.json").read_text(encoding="utf-8"))
    bundle = json.loads((CHECKPOINT / "SUBJECT-BUNDLE-AUDIT.json").read_text(encoding="utf-8"))
    attack_t = next(item for item in report["attacks"] if item.get("attackId") == "T")
    transport_passed = transport.get("result") == "PASS"
    bundle_passed = bundle.get("result") == "PASS"
    attack_t.update({
        "target": "review transport determinism and command-input portability",
        "mutation": (
            "rebuild twice from a detached published clone; reference Git metadata, an absolute "
            "temporary path, ignored output and a local-only untracked input"
        ),
        "expectedDefense": (
            "byte-identical secret-clean archives and no local-only input can support a sealed "
            "checkpoint"
        ),
        "observed": (
            f"bundle={bundle.get('result')}; digest={','.join(bundle.get('rebuiltSha256') or [])}; "
            f"git-metadata={transport.get('checks', {}).get('gitMetadataRefused')}; "
            f"absolute-temp={transport.get('checks', {}).get('absoluteTemporaryRefused')}; "
            f"ignored={transport.get('checks', {}).get('ignoredOutputRefused')}; "
            f"untracked-local-only={transport.get('checks', {}).get('untrackedCannotRemainLocalOnly')}"
        ),
        "result": "DEFENDED" if bundle_passed and transport_passed else "ESCAPED",
        "evidence": [
            "checkpoint:SUBJECT-BUNDLE-AUDIT.json",
            "checkpoint:TRANSPORT-ATTACKS.json",
        ],
        "origin": "audit-owned published-clone and disposable transport probes",
    })
    escaped = [item for item in report["attacks"] if item.get("result") != "DEFENDED"]
    report.update({
        "checkpoint": CHECKPOINT.name,
        "subjectCheckpoint": "GATE-4-CP-0007",
        "subjectCommit": SUBJECT_COMMIT,
        "generatedAt": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "mandatoryDefended": len(report["attacks"]) - len(escaped),
        "defended": len(report["attacks"]) - len(escaped),
        "escaped": len(escaped),
        "total": len(report["attacks"]),
        "result": (
            "RED_TEAM_PASS"
            if report.get("baselineControl", {}).get("result") == "VALID" and not escaped
            else "RED_TEAM_FAIL"
        ),
        "transportBoundary": transport,
    })
    arguments.report.resolve().write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8", newline="\n",
    )
    arguments.markdown.resolve().write_text(
        module.render(report), encoding="utf-8", newline="\n"
    )
    print(
        f"INDEPENDENT_RED_TEAM={report['result']} "
        f"{report['defended']}/{report['total']} transport={transport.get('result')}"
    )
    if base_result != 0 and report["result"] == "RED_TEAM_PASS":
        raise RuntimeError("the canonical base battery failed before transport augmentation")
    return 0 if report["result"] == "RED_TEAM_PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
