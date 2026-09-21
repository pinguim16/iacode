#!/usr/bin/env python3
"""Independent re-derivation of the SETUP-00 expected requirement set.

Written by the CP-0009 fresh-session audit. It deliberately does NOT import
scripts/development-ledger/policies.py, so the expected set is reconstructed from
the canonical documents themselves rather than from the delivery's own tooling.
"""
from __future__ import annotations
import json, re, sys
from pathlib import Path
import os as _os
from pathlib import Path as _Path
_DEFAULT_ROOT = _Path(__file__).resolve().parents[4]

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else "E:/iacode")
CP = ROOT / "docs" / "checkpoints" / "SETUP-00-CP-0008"

def read(p): return (ROOT / p).read_text(encoding="utf-8")

# --- 1. canonical checklist rows, parsed independently from the Markdown -------------
checklist_keys = []
row = re.compile(r"^\|\s*([0-9]+[a-z]?\.[0-9]+)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*$")
for line in read("docs/SETUP-00-CHECKLIST.md").splitlines():
    m = row.match(line)
    if m and m.group(2) not in ("Requirement", "---"):
        checklist_keys.append((m.group(1), m.group(2)))

# --- 2. findings of the sealed CP-0007 review report ---------------------------------
findings = re.findall(r"^###\s+([A-Z0-9]+-F-[0-9]{3})\s", read(
    "docs/checkpoints/SETUP-00-CP-0007/REVIEW-REPORT.md"), re.M)

# --- 3. mandatory attacks of the sealed CP-0007 red team report -----------------------
rt = read("docs/checkpoints/SETUP-00-CP-0007/RED-TEAM-REPORT.md")
mandatory_attacks, additional_attacks, seen = [], [], set()
seven = re.compile(r"^\|\s*([A-Z]{1,2})\s*\|" + r"\s*(.+?)\s*\|" * 6 + r"\s*$")
five = re.compile(r"^\|\s*([A-Z]{1,2})\s*\|" + r"\s*(.+?)\s*\|" * 4 + r"\s*$")
for line in rt.splitlines():
    m = seven.match(line)
    if m and m.group(1) not in seen and m.group(1) != "Attack":
        seen.add(m.group(1)); mandatory_attacks.append(m.group(1)); continue
    m = five.match(line)
    if m and m.group(1) not in seen and m.group(1) not in ("ID",):
        seen.add(m.group(1)); additional_attacks.append(m.group(1))

# --- 4. lessons the preflight selected ------------------------------------------------
preflight = json.loads((CP / "LESSON-PREFLIGHT.json").read_text(encoding="utf-8"))
lesson_ids = [d["lessonId"] for d in preflight.get("derivedRequirements", [])]

expected = set()
expected |= {f"canonical:SETUP-00#{k}" for k, _ in checklist_keys}
expected |= {f"lesson:{lid}" for lid in lesson_ids}
expected |= {f"finding:{f}" for f in findings}
expected |= {f"attack:{a}" for a in mandatory_attacks}

# --- 5. declared set from CP-0008 -----------------------------------------------------
matrix = json.loads((CP / "REQUIREMENTS-MATRIX.json").read_text(encoding="utf-8"))
declared = {}
for item in matrix["requirements"]:
    ref = (item.get("sourceRef") or "").strip()
    if ref.split(":", 1)[0] in ("canonical", "lesson", "finding", "attack"):
        declared.setdefault(ref, []).append(item["id"])

out = {
    "checklistRows": len(checklist_keys),
    "checklistKeys": [k for k, _ in checklist_keys],
    "findings": findings,
    "mandatoryAttacks": mandatory_attacks,
    "additionalAttacks": additional_attacks,
    "lessonIds": lesson_ids,
    "expectedTotal": len(expected),
    "declaredTotal": len(declared),
    "missing": sorted(expected - set(declared)),
    "unexpected": sorted(set(declared) - expected),
    "duplicated": {r: ids for r, ids in declared.items() if len(ids) > 1},
    "matrixRows": len(matrix["requirements"]),
    "localRows": [i["id"] for i in matrix["requirements"]
                  if (i.get("sourceRef") or "").startswith("local:")],
    "statusCounts": {},
}
for item in matrix["requirements"]:
    s = item.get("status", "?")
    out["statusCounts"][s] = out["statusCounts"].get(s, 0) + 1
out["mandatoryRows"] = sum(1 for i in matrix["requirements"] if i.get("mandatory"))
print(json.dumps(out, indent=1))
