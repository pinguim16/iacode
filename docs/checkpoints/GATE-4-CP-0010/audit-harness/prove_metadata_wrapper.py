#!/usr/bin/env python3
"""Exercise old/new metadata wrappers with real validation in a complete disposable copy."""

from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
RELATIVE = CHECKPOINT.relative_to(ROOT)
WRAPPER = RELATIVE / "audit-harness/run_checkpoint_validation.py"
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))

from ledger_common import (
    LedgerError, clone_with_worktree, load_json, scope_fingerprint, utc_now,
    use_utf8_stdout, write_json,
)

LEGACY = "4c53e4f788adc24e1b9cd9f581a7dc0d0f3c1340"


def execute(root: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, *arguments], cwd=root, capture_output=True,
                          text=True, encoding="utf-8", errors="replace", check=False)


def observation(checkpoint: Path) -> dict:
    state = load_json(checkpoint / "STATE.json")
    return {"status": state["status"], "dirty": state["dirty"],
            "lessonPreflight": {key: state["lessonPreflight"].get(key) for key in
                                ("lessonsConsidered", "lessonsApplicable", "derivedRequirements")}}


def main() -> int:
    destination = CHECKPOINT / "METADATA-WRAPPER-REAL-VALIDATION.json"
    if destination.exists():
        raise LedgerError("preserve every previous real-validation observation")
    report = {"schemaVersion": "1.0.0", "generatedAt": utc_now(),
              "kind": "SAME_SESSION_BOOKKEEPING_COPY_PROOF_ONLY",
              "promotionEvidence": False, "steps": [], "result": "NOT_EXECUTED"}
    temporary = None
    try:
        fingerprint = scope_fingerprint(ROOT)
        current = (ROOT / WRAPPER).read_bytes()
        legacy = subprocess.run(
            ["git", "show", f"{LEGACY}:{WRAPPER.as_posix()}"], cwd=ROOT,
            capture_output=True, check=True,
        ).stdout
        report.update(sourceFingerprint=fingerprint,
                      currentWrapperSha256=hashlib.sha256(current).hexdigest(),
                      legacyWrapperCommit=LEGACY,
                      legacyWrapperSha256=hashlib.sha256(legacy).hexdigest())
        with tempfile.TemporaryDirectory(prefix="iacode-cp0010-bookkeeping-proof-") as temporary:
            clone = Path(temporary) / "repository"
            if not clone_with_worktree(ROOT, clone):
                raise LedgerError("the complete transported working copy could not be created")
            checkpoint = clone / RELATIVE
            initial = load_json(checkpoint / "STATE.json")
            initial["dirty"] = False
            initial["lessonPreflight"].update({"lessonsConsidered": 1,
                                               "lessonsApplicable": 0, "derivedRequirements": 0})
            expected = load_json(checkpoint / "LESSON-PREFLIGHT.json")
            for label, source in (("legacy-negative", legacy), ("current-positive", current)):
                # Generated diagnostic fixture bytes, never a modification of the source checkout.
                (clone / WRAPPER).write_bytes(source)
                write_json(checkpoint / "STATE.json", copy.deepcopy(initial))
                declared = execute(clone, str(RELATIVE / "audit-harness/declare_inventory.py"))
                if declared.returncode:
                    raise LedgerError(f"{label}: declaration failed with {declared.returncode}")
                before = observation(checkpoint)
                result = execute(clone, str(WRAPPER))
                after = observation(checkpoint)
                metadata_refusal = ("lessonPreflight" in result.stdout
                                    or "preflight" in result.stdout.lower())
                report["steps"].append({"control": label, "before": before, "after": after,
                                        "exitCode": result.returncode,
                                        "metadataRefusalObserved": metadata_refusal})
                if label == "legacy-negative":
                    if result.returncode == 0 or not metadata_refusal:
                        raise LedgerError("the old wrapper did not produce the expected metadata refusal")
                elif (result.returncode != 0 or not after["dirty"]
                      or after["status"] != "IN_PROGRESS"
                      or after["lessonPreflight"]["lessonsConsidered"] != expected["lessonsConsidered"]
                      or after["lessonPreflight"]["derivedRequirements"] != len(expected["derivedRequirements"])):
                    raise LedgerError("the real current wrapper did not preserve valid derived metadata")
            report["sourceFingerprintUnchanged"] = scope_fingerprint(ROOT) == fingerprint
            report["result"] = ("BOOKKEEPING_CONTROLS_OBSERVED"
                                if report["sourceFingerprintUnchanged"] else "FAIL")
    except Exception as error:
        report.update(result="FAIL", failureType=type(error).__name__)
    report["temporaryCloneRemoved"] = temporary is None or not Path(temporary).exists()
    if not report["temporaryCloneRemoved"]:
        report["result"] = "FAIL"
    write_json(destination, report)
    print(json.dumps({key: report[key] for key in
                      ("kind", "result", "promotionEvidence", "temporaryCloneRemoved", "steps")}))
    return 0 if report["result"] == "BOOKKEEPING_CONTROLS_OBSERVED" else 1


if __name__ == "__main__":
    use_utf8_stdout()
    raise SystemExit(main())
