"""Bind completed local implementation evidence without completing a requirement or Gate.

Only the explicit positive receipts below can supply counts. This preserves the old baseline,
every failed observation, the full canonical denominator and pending independent M2 boundary.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))

from derive_requirements import build, render_closure, render_matrix
from ledger_common import load_json, utc_now, write_json
from sync_in_progress_metadata import synchronize


def observation(name: str) -> tuple[dict, str]:
    receipt = load_json(CHECKPOINT / "suite-attempts" / (name + ".json"))
    if (receipt["result"] != "PASS" or receipt["exitCode"] != 0
            or not receipt["sourceUnchanged"] or receipt["unsafeOutputOccurrences"] != 0):
        raise ValueError("a successful exact local execution is required")
    artifact = (ROOT / receipt["safeOutputArtifact"]).resolve(strict=True)
    if not artifact.is_relative_to((CHECKPOINT / "suite-attempts").resolve()):
        raise ValueError("local observation escaped its checkpoint")
    raw = artifact.read_bytes()
    if len(raw) != receipt["outputBytes"] or hashlib.sha256(raw).hexdigest() != receipt["outputSha256"]:
        raise ValueError("actual producer bytes differ from their original receipt")
    return receipt, raw.decode("utf-8", errors="strict")


def main() -> int:
    state = load_json(CHECKPOINT / "STATE.json")
    if state["status"] != "IN_PROGRESS" or state["gate"] != "GATE-7":
        raise ValueError("progress authoring is restricted to the unsealed implementing Gate")
    records = {row["id"]: row for row in (json.loads(line) for line in
        (CHECKPOINT / "COMMANDS.jsonl").read_text(encoding="utf-8").splitlines() if line.strip())}
    for name in ("cmd-0033", "cmd-0055", "cmd-0042", "cmd-0081", "cmd-0089", "cmd-0090", "cmd-0092"):
        if records[name]["exitCode"] != 0:
            raise ValueError("the bound actual command did not succeed")
    suites = {}
    for name, label in (("GATE-APITESTS-0002", "apiUnit"),
                        ("GATE-KNOWLEDGETESTS-0004", "knowledgeDomain"),
                        ("KNOWLEDGE-SQL-0003", "knowledgeSqlHttpMigration")):
        receipt, raw = observation(name)
        matches = re.findall(r"(?:^|\n)(\d+) passed(?:,| in )", raw)
        if len(matches) != 1:
            raise ValueError("one actual completed pytest count is required")
        suites[label] = {"passed": int(matches[0]), "failed": 0,
                         "receipt": "suite-attempts/" + name + ".json",
                         "sourceFingerprint": receipt["sourceFingerprint"],
                         "scope": "LOCAL_TARGETED_NOT_WHOLE_VERIFICATION"}
    root_receipt, root_output = observation("GATE7-ROOT-0005")
    root_counts = re.findall(r"Ran (\d+) tests in", root_output)
    if len(root_counts) != 1 or not root_output.rstrip().endswith("OK"):
        raise ValueError("one completed actual successful root execution is required")
    suites["gate7Root"] = {"passed": int(root_counts[0]), "failed": 0,
        "receipt": "suite-attempts/GATE7-ROOT-0005.json",
        "sourceFingerprint": root_receipt["sourceFingerprint"],
        "scope": "LOCAL_TARGETED_NOT_WHOLE_VERIFICATION"}
    live_receipt, _ = observation("KNOWLEDGE-LIVE-0001")
    live_manifest = load_json(CHECKPOINT / "attempts/KNOWLEDGE-LIVE-RAW-RECEIPT-0001.json")
    live_path = (CHECKPOINT / live_manifest["artifact"]).resolve(strict=True)
    if not live_path.is_relative_to((CHECKPOINT / "attempts").resolve()):
        raise ValueError("original live producer escaped the current checkpoint")
    live_raw = live_path.read_bytes()
    if (len(live_raw) != live_manifest["sizeBytes"]
            or hashlib.sha256(live_raw).hexdigest() != live_manifest["sha256"]):
        raise ValueError("original live producer differs from its original exact receipt")
    live = json.loads(live_raw)
    corpus = load_json(ROOT / "services/knowledge/tests/fixtures/retrieval-corpus.json")
    controls = live["steps"]
    measured = live["retrievalMeasurements"]
    if (live["result"] != "PASS" or not controls
            or len({row["name"] for row in controls}) != len(controls)
            or any(row["result"] != "PASS" for row in controls)
            or [row["queryOrdinal"] for row in measured] != list(range(len(corpus["queries"])))
            or any(row["result"] != "PASS" for row in measured)
            or live["cleanup"] != {"composeExitCode": 0, "container": 0, "volume": 0, "network": 0}
            or live["sandboxCleanup"] != {"container": 0, "network": 0}):
        raise ValueError("complete measured owned live proof and actual cleanup are required")
    suites["knowledgeOwnedLive"] = {"passed": 1, "failed": 0, "controlsPassed": len(controls),
        "queriesPassed": len(measured), "receipt": "suite-attempts/KNOWLEDGE-LIVE-0001.json",
        "originalProducer": live_manifest["artifact"],
        "sourceFingerprint": live_receipt["sourceFingerprint"],
        "scope": "ONE_TARGETED_OWNED_SCENARIO_NOT_WHOLE_VERIFICATION"}
    cleanup = load_json(CHECKPOINT / "suite-attempts/KNOWLEDGE-SQL-RECEIPT-0002.json")
    if cleanup["result"] != "PASS" or not cleanup["unrelatedContainersPreserved"]:
        raise ValueError("actual owned-resource cleanup and unrelated state must be observed")
    write_json(CHECKPOINT / "CURRENT-PROGRESS.json", {
        "schemaVersion": "1.0.0", "kind": "IMPLEMENTATION_PROGRESS_NOT_ACCEPTANCE",
        "observedAt": utc_now(), "suites": suites, "cleanup": cleanup,
        "wholeVerification": "NOT_EXECUTED", "orderedInternalAssurance": "NOT_EXECUTED",
        "independentM2": "PENDING", "gate8Authorized": False,
    })
    preflight = load_json(CHECKPOINT / "LESSON-PREFLIGHT.json")
    marker = "\n<!-- BEGIN DERIVED LESSON COMMITMENTS -->\n"
    path = CHECKPOINT / "PLAN.md"
    original = path.read_text(encoding="utf-8").split(marker, 1)[0].rstrip()
    lines = []
    for row in preflight["applicable"]:
        lines.extend(["", "### " + row["derivedRequirementId"] + " — " + row["lessonId"], "",
                      "- Required check: " + row["requiredCheck"],
                      "- Required evidence: " + row["requiredEvidence"]])
    path.write_text(original + marker + "\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    closure = load_json(CHECKPOINT / "CLOSURE-REQUIREMENTS.json")
    selected = {"lesson:" + row["lessonId"] for row in preflight["applicable"]
                if row["lessonId"] in {"LSN-0018", "LSN-0105", "LSN-0117", "LSN-0119", "LSN-0145", "LSN-0146"}}
    for row in closure["requirements"]:
        anchor = row["sourceRef"]
        key = anchor.partition("#")[2] if anchor.startswith("canonical:") else ""
        section = key.partition(".")[0]
        if (section in {"1", "2", "3", "4", "5", "6", "7"}
                or key in {"8.1", "8.2", "8.4", "8.6", "8.8"}
                or anchor in selected):
            row["implementationStatus"] = row["finalStatus"] = "PARTIAL"
            row["implementationEvidence"] = ["file:services/knowledge/src/iacode_knowledge/domain.py",
                                              "file:apps/api/src/iacode_api/knowledge/store.py"]
            row["documentationEvidence"] = ["checkpoint:PLAN.md", "checkpoint:CURRENT-PROGRESS.json"]
            row["notes"] = ("Local implementation/proof exists; the exact scope and original "
                            "fingerprints are in CURRENT-PROGRESS.json. This is not complete "
                            "whole-verifier/ordered-assurance/independent acceptance.")
            if section in {"2", "3", "4", "5", "6"}:
                row["testEvidence"] = ["command:cmd-0055", "command:cmd-0042", "command:cmd-0081"]
    write_json(CHECKPOINT / "CLOSURE-REQUIREMENTS.json", closure)
    closure, matrix = build(ROOT, CHECKPOINT, "GATE-7")
    for stem, document, renderer in (("CLOSURE-REQUIREMENTS", closure, render_closure),
                                     ("REQUIREMENTS-MATRIX", matrix, render_matrix)):
        write_json(CHECKPOINT / (stem + ".json"), document)
        (CHECKPOINT / (stem + ".md")).write_text(renderer(document), encoding="utf-8", newline="\n")
    mandatory = [row for row in matrix["requirements"] if row["mandatory"]]
    state["requirementsMatrix"].update({"total": len(matrix["requirements"]),
        "mandatory": len(mandatory), "complete": 0,
        "partial": sum(row["status"] == "PARTIAL" for row in mandatory),
        "missing": 0, "notApplicable": 0, "coveragePercent": 0.0})
    state["lessonPreflight"]["evidence"] = ["checkpoint:LESSON-PREFLIGHT.json"]
    write_json(CHECKPOINT / "STATE.json", state)
    tests = load_json(CHECKPOINT / "TESTS.json")
    for category, command, label in (("unit", "cmd-0033", "apiUnit"),
                                      ("integration", "cmd-0042", "knowledgeSqlHttpMigration"),
                                      ("e2e", "cmd-0081", "knowledgeOwnedLive")):
        tests[category].update({"executed": True, "passed": suites[label]["passed"], "failed": 0,
            "command": records[command]["command"], "evidence": "command:" + command,
            "runId": "gate7-local-targeted-not-whole-acceptance"})
    write_json(CHECKPOINT / "TESTS.json", tests)
    synchronize(ROOT, CHECKPOINT)
    print("PROGRESS_BOUND " + " ".join(f"{key}={value['passed']}" for key, value in suites.items())
          + " whole=NOT_EXECUTED independent=PENDING")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
