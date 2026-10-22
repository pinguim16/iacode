"""Bind observed local progress without closing findings or asserting integral acceptance."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))
from ledger_common import load_json, write_json
from sync_in_progress_metadata import synchronize


def main() -> int:
    transcript = CHECKPOINT / "causal-attempts/run-0009.stderr.log"
    matches = re.findall(r"Ran (\d+) tests in [0-9.]+s\s+OK", transcript.read_text(encoding="utf-8"))
    if len(matches) != 1 or load_json(transcript.with_name("run-0009.json"))["exitCode"] != 0:
        raise ValueError("actual current causal observation is required")
    closure_path = CHECKPOINT / "CLOSURE-REQUIREMENTS.json"
    closure = load_json(closure_path)
    references = {"finding:M2-F-001", "finding:M2-F-002", "attack:M2-RT-01",
                  "lesson:LSN-0010", "lesson:LSN-0135"}
    observed = set()
    for row in closure["requirements"]:
        if row["sourceRef"] not in references:
            continue
        observed.add(row["sourceRef"])
        row["implementationStatus"] = "COMPLETE"
        row["finalStatus"] = "PARTIAL"
        row["implementationEvidence"] = ["file:scripts/development-ledger/new_checkpoint.py",
                                         "file:scripts/iacode/client_checks.py"]
        row["testEvidence"] = ["file:docs/checkpoints/GATE-7-CP-0003/causal-attempts/run-0009.json"]
        row["negativeTestEvidence"] = ["file:docs/checkpoints/GATE-7-CP-0003/causal-attempts/run-0005.json"]
        row["documentationEvidence"] = ["file:docs/adr/ADR-0061-client-verification-preserves-producer-and-cleanup-outcomes.md"]
        row["justification"] = "Local causal correction is demonstrated; integral corrective acceptance and immutable assurance remain pending."
    if observed != references:
        raise ValueError("canonical finding/attack/lesson obligations changed; do not silently omit one")
    write_json(closure_path, closure)
    tests = load_json(CHECKPOINT / "TESTS.json")
    tests["unit"].update({"executed": True, "passed": int(matches[0]), "failed": 0,
                          "command": "python docs/checkpoints/GATE-7-CP-0003/audit-harness/run_causal.py",
                          "evidence": "file:docs/checkpoints/GATE-7-CP-0003/causal-attempts/run-0009.json",
                          "runId": "targeted-causal-not-whole-root-suite"})
    write_json(CHECKPOINT / "TESTS.json", tests)
    quality = load_json(CHECKPOINT / "QUALITY.json")
    for name in ("staticAnalysis", "lint"):
        path = CHECKPOINT / "quality-attempts" / name / "run-0001.json"
        receipt = load_json(path)
        if receipt["exitCode"] != 0 or any(item["refused"] for item in receipt["streams"].values()):
            raise ValueError("cannot mark a failed or unscannable canonical gate PASS")
        quality["checks"][name].update({"status": "PASS", "evidence": ["file:" + path.relative_to(CHECKPOINT).as_posix()],
                                        "justification": "Complete canonical gate, not the targeted source check."})
    write_json(CHECKPOINT / "QUALITY.json", quality)
    metadata = load_json(CHECKPOINT / "RUN-METADATA.json")
    metadata.update({"tool": "Codex desktop", "toolVersion": "not-exposed", "provider": "OpenAI",
                     "model": "not-exposed", "effort": "not-exposed", "operatingSystem": "Windows / PowerShell"})
    write_json(CHECKPOINT / "RUN-METADATA.json", metadata)
    state = load_json(CHECKPOINT / "STATE.json")
    state["nextAllowedAction"] = "Resolve the two explicit pending scope approvals; complete canonical integral assurance before sealing or a new independent audit. No Gate8."
    state["requirementsMatrix"].update({"total": len(closure["requirements"]),
        "mandatory": sum(item["mandatory"] for item in closure["requirements"]),
        "complete": 0, "partial": len(references), "missing": 0, "notApplicable": 0,
        "coveragePercent": 0.0})
    state["greenKeeper"]["unresolvedReworkItems"] = 2
    write_json(CHECKPOINT / "STATE.json", state)
    synchronize(ROOT, CHECKPOINT)
    print(json.dumps({"requirements": len(closure["requirements"]), "partial": len(references),
                      "causalTestsPassed": int(matches[0]), "integralAcceptance": "PENDING"}))
    return 0


if __name__ == "__main__":
    from ledger_common import use_utf8_stdout
    use_utf8_stdout()
    raise SystemExit(main())
