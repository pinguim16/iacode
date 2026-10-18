"""Preserve complete successful v6 assurance and refused final handoff before mandatory rework."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))
from ledger_common import find_secrets, load_json, use_utf8_stdout, utc_now, write_json

NAMES = (
    "VERIFY.json", "PUBLISHED-CLEAN-CLONE-REPORT.json", "FUNCTIONAL-SCENARIOS.json",
    "COMPOSE-ISOLATION-AUDIT.json", "PRODUCER-REPORTS.json", "FULL-VERIFY-PROGRESS.json",
    "FUNCTIONAL-ACCEPTANCE.json", "FUNCTIONAL-ACCEPTANCE-VALIDATION.json",
    "COMPLETENESS-REPORT.json", "COMPLETENESS-REPORT.md", "M2-INTERNAL-RED-TEAM.json",
    "M2-INHERITED-RED-TEAM.json", "RED-TEAM-NATIVE.json", "RED-TEAM-DESKTOP.json",
    "RED-TEAM-EXPERIENCE.json", "RED-TEAM-EXECUTIONS.json", "RED-TEAM-REPORT.md",
    "M2-INTERNAL-MIRROR.json", "M2-INTERNAL-MIRROR.md", "FINAL-REPORT.md",
    "HANDOFF.md", "NEXT.md", "PROGRESS.md", "STATE.json", "QUALITY.json", "STEPS.json",
    "REQUIREMENTS-MATRIX.json", "CLOSURE-REQUIREMENTS.json", "LESSON-PREFLIGHT.json",
    "audit-harness/assemble_final_handoff.py",
)
RETIRED = ("VERIFY.json", "FUNCTIONAL-ACCEPTANCE.json", "FUNCTIONAL-ACCEPTANCE-VALIDATION.json",
           "COMPLETENESS-REPORT.json", "COMPLETENESS-REPORT.md", "M2-INTERNAL-RED-TEAM.json",
           "M2-INTERNAL-MIRROR.json", "M2-INTERNAL-MIRROR.md", "FINAL-REPORT.md")


def main() -> int:
    target = CHECKPOINT / "attempts/RUNTIME-V6-FINALIZATION-ARCHIVE.json"
    if target.exists() or load_json(CHECKPOINT / "STATE.json")["status"] != "IN_PROGRESS":
        raise ValueError("only the original unsealed v6 boundary may be archived once")
    records = [json.loads(line) for line in (CHECKPOINT / "COMMANDS.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    refusal = records[-1]
    if refusal.get("operation") != "finalize-checkpoint" or refusal.get("exitCode") != 1:
        raise ValueError("the actual latest terminal refusal is required")
    if load_json(CHECKPOINT / "M2-INTERNAL-MIRROR.json")["result"] != "PASS":
        raise ValueError("actual complete v6 mirror must be preserved")
    payloads = []
    for name in NAMES:
        source = CHECKPOINT / name
        destination = CHECKPOINT / "attempts" / ("RUNTIME-V6-FINALIZATION-" + name.replace("/", "--"))
        if source.is_symlink() or not source.is_file() or destination.exists():
            raise ValueError("missing/redirected source or preexisting archive")
        raw = source.read_bytes()
        if find_secrets(raw.decode("utf-8", "strict")):
            raise ValueError("unsafe original archive refused")
        payloads.append((source, destination, raw))
    rows = []
    for source, destination, raw in payloads:
        with destination.open("xb") as output:
            output.write(raw)
        if source.read_bytes() != raw or destination.read_bytes() != raw:
            raise ValueError("exact archival failed")
        rows.append({"source": source.relative_to(ROOT).as_posix(), "archive": destination.relative_to(ROOT).as_posix(),
                     "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(), "byteEqual": True})
    for name in RETIRED:
        source = CHECKPOINT / name
        original = next(raw for path, _, raw in payloads if path == source)
        if source.parent != CHECKPOINT or source.is_symlink() or source.read_bytes() != original:
            raise ValueError("refuse changed or redirected projection retirement")
        source.unlink()
    write_json(target, {"kind": "EXACT_V6_SUCCESSFUL_ASSURANCE_AND_FAILED_HANDOFF_ARCHIVE_NOT_CURRENT_ACCEPTANCE",
        "observedAt": utc_now(), "subjectCommit": "1442b86d38be11aee5e2ff635e576be08e52997b",
        "failedFinalizationCommand": refusal["id"], "records": rows,
        "retiredRedundantProjections": list(RETIRED), "originalProducerHistoryChanged": False, "result": "PASS"})
    print(f"V6_ORIGINALS_ARCHIVED records={len(rows)} refusal={refusal['id']}; fresh memory-bound assurance required")
    return 0


if __name__ == "__main__":
    use_utf8_stdout()
    raise SystemExit(main())
