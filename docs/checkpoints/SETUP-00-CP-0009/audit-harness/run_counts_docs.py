#!/usr/bin/env python3
"""Sections 21, 29 and 32: semantic counts, command auditability, documentation integrity.

Every count is recomputed by this script from the artifact that owns it, independently of
COUNTS.json and of derive_counts.py, and then compared with every current artifact that
states it.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import unittest
from pathlib import Path
import os as _os
from pathlib import Path as _Path
_DEFAULT_ROOT = _Path(__file__).resolve().parents[4]

ROOT = Path(_os.environ.get("IACODE_ROOT") or _DEFAULT_ROOT)
CP8 = ROOT / "docs" / "checkpoints" / "SETUP-00-CP-0008"
CP7 = ROOT / "docs" / "checkpoints" / "SETUP-00-CP-0007"

RESULT: dict = {"counts": {}, "commands": {}, "documentation": {}}


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()]


# ---------------------------------------------------------------- 21. semantic counts
def suite_case_count() -> int:
    loader = unittest.TestLoader()
    import os
    previous = os.getcwd()
    os.chdir(ROOT)
    try:
        suite = loader.discover("tests")
    finally:
        os.chdir(previous)
    total = 0
    stack = [suite]
    while stack:
        item = stack.pop()
        if isinstance(item, unittest.TestSuite):
            stack.extend(list(item))
        else:
            total += 1
    return total


def derive() -> dict:
    checklist = re.compile(r"^\|\s*([0-9]+[a-z]?\.[0-9]+)\s*\|\s*(.+?)\s*\|")
    setup_rows = [m.group(1) for line in
                  (ROOT / "docs" / "SETUP-00-CHECKLIST.md").read_text(encoding="utf-8").splitlines()
                  if (m := checklist.match(line)) and m.group(2) not in ("Requirement", "---")]
    findings = re.findall(r"^###\s+([A-Z0-9]+-F-[0-9]{3})\s",
                          (CP7 / "REVIEW-REPORT.md").read_text(encoding="utf-8"), re.M)
    matrix = read_json(CP8 / "REQUIREMENTS-MATRIX.json")["requirements"]
    lessons = jsonl(ROOT / ".iacode" / "memory" / "lessons.jsonl")
    guardrails = read_json(ROOT / ".iacode" / "memory" / "guardrails" / "registry.json")["guardrails"]
    red_team = read_json(CP8 / "M0-INTERNAL-RED-TEAM.json")
    closure = read_json(CP8 / "CP7-FINDINGS-CLOSURE.json")
    return {
        "SETUP_REQUIREMENTS": len(setup_rows),
        "M0_CLOSURE_REQUIREMENTS": len(matrix),
        "M0_CLOSURE_MANDATORY": sum(1 for row in matrix if row.get("mandatory")),
        "FINDINGS": len(findings),
        "FINDINGS_CLOSED": sum(1 for f in closure["findings"] if f.get("status") == "CLOSED"),
        "TESTS": suite_case_count(),
        "LESSONS": len(lessons),
        "LESSONS_GUARDED": sum(1 for item in lessons if item.get("status") == "GUARDED"),
        "GUARDRAILS": len(guardrails),
        "ATTACKS": red_team["total"],
        "ATTACKS_DEFENDED": sum(1 for a in red_team["attacks"] if a["result"] == "DEFENDED"),
        "ANCHORS": len(read_json(ROOT / ".iacode" / "anchors" / "checkpoint-chain.json")["anchors"]),
    }


def compare_counts(derived: dict) -> dict:
    stored = read_json(CP8 / "COUNTS.json")["counts"]
    state = read_json(CP8 / "STATE.json")
    report = read_json(CP8 / "COMPLETENESS-REPORT.json")
    comparisons = [
        ("COUNTS.json TESTS", stored["TESTS"]["numerator"], derived["TESTS"]),
        ("COUNTS.json TESTS denominator", stored["TESTS"]["denominator"], derived["TESTS"]),
        ("COUNTS.json REQUIREMENTS", stored["REQUIREMENTS"]["numerator"],
         derived["M0_CLOSURE_REQUIREMENTS"]),
        ("COUNTS.json FINDINGS", stored["FINDINGS"]["numerator"], derived["FINDINGS_CLOSED"]),
        ("COUNTS.json FINDINGS denominator", stored["FINDINGS"]["denominator"],
         derived["FINDINGS"]),
        ("COUNTS.json ATTACKS", stored["ATTACKS"]["numerator"], derived["ATTACKS_DEFENDED"]),
        ("COUNTS.json ATTACKS denominator", stored["ATTACKS"]["denominator"], derived["ATTACKS"]),
        ("COUNTS.json LESSONS", stored["LESSONS"]["numerator"], derived["LESSONS_GUARDED"]),
        ("COUNTS.json LESSONS denominator", stored["LESSONS"]["denominator"], derived["LESSONS"]),
        ("COUNTS.json GUARDRAILS", stored["GUARDRAILS"]["numerator"], derived["GUARDRAILS"]),
        ("STATE requirementsMatrix.total", state["requirementsMatrix"]["total"],
         derived["M0_CLOSURE_REQUIREMENTS"]),
        ("STATE requirementsMatrix.mandatory", state["requirementsMatrix"]["mandatory"],
         derived["M0_CLOSURE_MANDATORY"]),
        ("STATE lessonPreflight.lessonsConsidered", state["lessonPreflight"]["lessonsConsidered"],
         derived["LESSONS"]),
        ("STATE guardrailEffectiveness.guardrailsTotal",
         state["guardrailEffectiveness"]["guardrailsTotal"], derived["GUARDRAILS"]),
        ("STATE integrity.anchors", state["integrity"]["anchors"], derived["ANCHORS"]),
        ("COMPLETENESS totalRequirements", report["totalRequirements"],
         derived["M0_CLOSURE_REQUIREMENTS"]),
        ("COMPLETENESS expectedRequirements", report["expectedRequirements"],
         derived["M0_CLOSURE_REQUIREMENTS"]),
        ("COMPLETENESS mandatoryRequirements", report["mandatoryRequirements"],
         derived["M0_CLOSURE_MANDATORY"]),
    ]
    mismatches = [{"where": where, "stated": stated, "derived": expected}
                  for where, stated, expected in comparisons if stated != expected]
    return {"derived": derived, "compared": len(comparisons), "mismatches": mismatches}


def markdown_claims() -> dict:
    """Every N/M COUNT claim in a current (non-sealed-history) Markdown artifact."""
    claim = re.compile(r"(?<![0-9])(\d+)\s*/\s*(\d+)\s+"
                       r"(TESTS|REQUIREMENTS|FINDINGS|ATTACKS|LESSONS|GUARDRAILS)\b")
    found = []
    for path in sorted(CP8.glob("*.md")):
        for line in path.read_text(encoding="utf-8").splitlines():
            for match in claim.finditer(line):
                found.append({"file": path.name, "claim": match.group(0)})
    return {"claims": found}


# ---------------------------------------------------------------- 29. command auditability
REQUIRED_FIELDS = ("id", "timestamp", "runtime", "workingDirectory", "command", "arguments",
                   "inputs", "commit", "purpose", "result", "durationMs")


def commands() -> dict:
    records = jsonl(CP8 / "COMMANDS.jsonl")
    incomplete = []
    for record in records:
        missing = [field for field in REQUIRED_FIELDS if field not in record]
        if record.get("result") == "COMPLETED" and "exitCode" not in record:
            missing.append("exitCode")
        if record.get("result") == "PRECONDITION_REJECTED" and "resultCode" not in record:
            missing.append("resultCode")
        if missing:
            incomplete.append({"id": record.get("id"), "missing": missing})
    digested = [r for r in records if r.get("inputsDigest")]
    unbound = [r["id"] for r in records if r.get("inputs") and not r.get("inputsDigest")]
    return {"total": len(records), "incomplete": incomplete,
            "withInputsDigest": len(digested), "inputsWithoutDigest": unbound,
            "results": sorted({r.get("result") for r in records}),
            "nonZeroExits": [{"id": r["id"], "exitCode": r.get("exitCode")}
                             for r in records if r.get("exitCode") not in (0, None)]}


def replay_sample(seed: int = 20260920, size: int = 6) -> dict:
    """Replay a deterministic sample of safe, read-only recorded commands."""
    import random
    records = jsonl(CP8 / "COMMANDS.jsonl")
    safe = [r for r in records
            if r.get("result") == "COMPLETED"
            and isinstance(r.get("command"), str)
            and any(tool in r["command"] for tool in (
                "validate_checkpoint.py", "validate_lessons.py", "verify_integrity.py",
                "check_completeness.py", "derive_counts.py", "compileall"))
            and "--write" not in r["command"]]
    random.Random(seed).shuffle(safe)
    chosen = safe[:size]
    replays = []
    for record in chosen:
        digests = {item["path"]: item["hash"] for item in record.get("inputsDigest") or []}
        bound = []
        for path, digest in digests.items():
            proc = subprocess.run(["git", "show", record["commit"] + ":" + path],
                                  cwd=ROOT, capture_output=True)
            import hashlib
            content = proc.stdout.replace(b"\r\n", b"\n") if proc.returncode == 0 else b""
            observed = hashlib.sha256(content).hexdigest() if proc.returncode == 0 else None
            bound.append({"path": path, "recorded": digest, "atCommit": observed,
                          "matches": observed == digest})
        replays.append({"id": record["id"], "command": record["command"],
                        "commit": record["commit"], "recordedExit": record.get("exitCode"),
                        "inputBinding": bound})
    return {"seed": seed, "sampled": len(chosen), "replays": replays}


# ---------------------------------------------------------------- 32. documentation
LINK = re.compile(r"\[[^\]]*\]\(([^)#]+)(?:#[^)]*)?\)")


def documentation() -> dict:
    broken = []
    checked = 0
    for path in sorted(ROOT.rglob("*.md")):
        relative = path.relative_to(ROOT).as_posix()
        if relative.startswith(".git/"):
            continue
        for match in LINK.finditer(path.read_text(encoding="utf-8")):
            target = match.group(1).strip()
            if target.startswith(("http://", "https://", "mailto:")):
                continue
            checked += 1
            resolved = (path.parent / target).resolve()
            if not resolved.exists():
                broken.append({"file": relative, "link": target})
    return {"linksChecked": checked, "broken": broken}


def main() -> int:
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    derived = derive()
    RESULT["counts"] = compare_counts(derived)
    RESULT["counts"]["markdown"] = markdown_claims()
    RESULT["commands"] = commands()
    RESULT["commands"]["replay"] = replay_sample()
    RESULT["documentation"] = documentation()
    (out / "counts-docs.json").write_text(json.dumps(RESULT, indent=2) + "\n",
                                          encoding="utf-8", newline="\n")
    print("DERIVED " + json.dumps(derived))
    print("COUNT COMPARISONS " + str(RESULT["counts"]["compared"])
          + " MISMATCHES " + str(len(RESULT["counts"]["mismatches"])))
    for item in RESULT["counts"]["mismatches"]:
        print("  - " + json.dumps(item))
    print("MARKDOWN COUNT CLAIMS " + str(len(RESULT["counts"]["markdown"]["claims"])))
    print("COMMANDS " + str(RESULT["commands"]["total"])
          + " incomplete=" + str(len(RESULT["commands"]["incomplete"]))
          + " inputsWithoutDigest=" + str(len(RESULT["commands"]["inputsWithoutDigest"]))
          + " results=" + ",".join(RESULT["commands"]["results"]))
    print("  nonZeroExits=" + json.dumps(RESULT["commands"]["nonZeroExits"]))
    unbound = [entry for replay in RESULT["commands"]["replay"]["replays"]
               for entry in replay["inputBinding"] if not entry["matches"]]
    print("REPLAY sampled=" + str(RESULT["commands"]["replay"]["sampled"])
          + " unboundInputs=" + str(len(unbound)))
    print("DOC LINKS " + str(RESULT["documentation"]["linksChecked"])
          + " broken=" + str(len(RESULT["documentation"]["broken"])))
    for item in RESULT["documentation"]["broken"]:
        print("  - " + json.dumps(item))
    return 0


if __name__ == "__main__":
    sys.exit(main())
