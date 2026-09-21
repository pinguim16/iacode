#!/usr/bin/env python3
"""Independent CP11-F-001 probe. Written by the CP-0013 audit, not by the delivery.

Every scenario runs the real m0_mirror_audit.py inside a disposable clone of the repository.
Nothing here reads the delivery's own MIRROR-SEMANTICS-VALIDATION.json.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve()
CP = "SETUP-00-CP-0012"
RESULTS = []


def clone(dst: Path) -> None:
    subprocess.run(["git", "clone", "--quiet", "--no-hardlinks", str(ROOT), str(dst)],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def mirror(root: Path, checkpoint: str = CP):
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    proc = subprocess.run(
        [sys.executable, "scripts/development-ledger/m0_mirror_audit.py",
         "--checkpoint", f"docs/checkpoints/{checkpoint}"],
        cwd=root, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        check=False, env=env)
    return proc.returncode, proc.stdout


def parse(out: str) -> dict:
    res = {}
    for line in out.splitlines():
        line = line.strip()
        if line.startswith("[MIR-"):
            ident = line[1:line.index("]")]
            rest = line[line.index("]") + 2:]
            res[ident] = rest.split(" ", 1)[0]
        if line.startswith("INTERNAL_MIRROR="):
            res["overall"] = line.split("=", 1)[1].split(" ")[0]
            res["summary"] = line
    return res


def scenario(name: str, mutate, expect: dict) -> None:
    with tempfile.TemporaryDirectory(prefix="cp13-probe-") as tmp:
        work = Path(tmp) / "clone"
        clone(work)
        note = mutate(work) if mutate else "unmutated"
        code, out = mirror(work)
        got = parse(out)
        ok = all(got.get(k) == v for k, v in expect.items())
        RESULTS.append({
            "scenario": name, "mutation": note, "expected": expect,
            "observed": {k: got.get(k) for k in expect},
            "exitCode": code, "summary": got.get("summary", ""),
            "verdict": "PASS" if ok else "FAIL",
            "mirOO2Reason": next((l for l in out.splitlines()
                                  if l.startswith("- NOT_APPLICABLE MIR-002")), None),
            "failLines": [l for l in out.splitlines() if l.startswith("- FAIL")],
        })
        print(f"[{'PASS' if ok else 'FAIL'}] {name}: {got.get('summary','(no summary)')}")
        for k, v in expect.items():
            print(f"      {k}: expected={v} observed={got.get(k)}")


# --- P1: closed set. CP-0012 is the registered corrective delivery of M0-CP-0011.
scenario("P1-closed-set", None, {"MIR-002": "PASS", "MIR-003": "PASS"})


# --- P2: one applicable finding left OPEN.
def open_one(work: Path) -> str:
    path = work / "docs" / "checkpoints" / CP / "CP11-FINDINGS-CLOSURE.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    doc["findings"][0]["status"] = "OPEN"
    path.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    return f"set {doc['findings'][0]['findingId']} to OPEN"


scenario("P2-open-finding", open_one, {"MIR-002": "FAIL", "overall": "FAIL"})


# --- P3: required closure artifact removed.
def drop_closure(work: Path) -> str:
    (work / "docs" / "checkpoints" / CP / "CP11-FINDINGS-CLOSURE.json").unlink()
    return "deleted CP11-FINDINGS-CLOSURE.json"


scenario("P3-missing-required-artifact", drop_closure, {"MIR-002": "FAIL", "overall": "FAIL"})


# --- P4: delivery forges an empty expected set inside its own artifacts.
def forge_in_checkpoint(work: Path) -> str:
    path = work / "docs" / "checkpoints" / CP / "CP11-FINDINGS-CLOSURE.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    doc["findings"] = []
    doc["expectedFindings"] = 0
    doc["notApplicable"] = True
    path.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    return "emptied the checkpoint's own closure record and declared it inapplicable"


scenario("P4-forged-empty-set-in-delivery", forge_in_checkpoint,
         {"MIR-002": "FAIL", "overall": "FAIL"})


# --- P5: registry repointed at a report with no findings (parse must raise, not empty).
def repoint_report(work: Path) -> str:
    empty = work / "docs" / "checkpoints" / CP / "EMPTY-REPORT.md"
    empty.write_text("# Nothing here\n", encoding="utf-8")
    reg = work / ".iacode" / "policies" / "audit-registry.json"
    doc = json.loads(reg.read_text(encoding="utf-8"))
    for audit in doc["audits"]:
        if audit["auditId"] == "M0-CP-0011":
            audit["reviewReport"] = f"docs/checkpoints/{CP}/EMPTY-REPORT.md"
    reg.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    return "repointed M0-CP-0011.reviewReport at a report with no parseable finding"


scenario("P5-unparseable-report-is-not-empty", repoint_report,
         {"MIR-002": "FAIL", "overall": "FAIL"})


# --- P6: delivery deletes its own audit from the registry to make the set empty.
def delete_registry_entry(work: Path) -> str:
    reg = work / ".iacode" / "policies" / "audit-registry.json"
    doc = json.loads(reg.read_text(encoding="utf-8"))
    doc["audits"] = [a for a in doc["audits"] if a["auditId"] != "M0-CP-0011"]
    reg.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    return "removed the M0-CP-0011 entry from the audit registry"


scenario("P6-registry-entry-deleted", delete_registry_entry,
         {"MIR-002": "NOT_APPLICABLE", "overall": "FAIL"})

out = Path(sys.argv[2])
out.write_text(json.dumps(RESULTS, indent=2), encoding="utf-8")
failed = [r for r in RESULTS if r["verdict"] == "FAIL"]
print(f"\nPROBE_RESULT={'PASS' if not failed else 'FAIL'} "
      f"{len(RESULTS) - len(failed)}/{len(RESULTS)}")
sys.exit(0 if not failed else 1)
