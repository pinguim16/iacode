#!/usr/bin/env python3
"""Independent probe of the state the CP11-F-001 repair opened: NOT_APPLICABLE as a bypass.

Each scenario mutates the sealed mirror report of SETUP-00-CP-0012 inside a disposable clone and
asks validate_checkpoint whether it is refused. The tree is deliberately dirty, so a dirtiness
error is expected as well; what is probed is whether the SPECIFIC control fires.
"""
from __future__ import annotations

import json, os, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve()
CP = "SETUP-00-CP-0012"
RESULTS = []


def validate(clone: Path):
    env = dict(os.environ); env["PYTHONDONTWRITEBYTECODE"] = "1"
    p = subprocess.run([sys.executable, "scripts/development-ledger/validate_checkpoint.py"],
                       cwd=clone, text=True, stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT, check=False, env=env)
    return p.returncode, p.stdout


def scenario(name: str, mutate, must_contain: list[str]) -> None:
    with tempfile.TemporaryDirectory(prefix="cp13-na-") as tmp:
        clone = Path(tmp) / "clone"
        subprocess.run(["git", "clone", "--quiet", "--no-hardlinks", str(ROOT), str(clone)],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["git", "checkout", "--quiet", "--detach",
                        f"refs/tags/iacode-checkpoints/{CP}"], cwd=clone, check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        path = clone / "docs" / "checkpoints" / CP / "M0-INTERNAL-MIRROR.json"
        doc = json.loads(path.read_text(encoding="utf-8"))
        note = mutate(doc)
        path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
        code, out = validate(clone)
        found = {frag: any(frag in line for line in out.splitlines()) for frag in must_contain}
        ok = code != 0 and all(found.values())
        RESULTS.append({"scenario": name, "mutation": note, "exitCode": code,
                        "requiredFragments": found, "verdict": "PASS" if ok else "FAIL",
                        "output": out.strip().splitlines()})
        print(f"[{'PASS' if ok else 'FAIL'}] {name} exit={code}")
        for frag, hit in found.items():
            print(f"      {'found' if hit else 'MISSING'}: {frag!r}")
        if not ok:
            for line in out.strip().splitlines()[:25]:
                print("       |", line)


def as_na(doc, *, reason=None, source=None, count=None, check_id="MIR-002"):
    for c in doc["checks"]:
        if c["id"] == check_id:
            c["result"] = "NOT_APPLICABLE"
            if reason is not None:
                c["reason"] = reason
            if source is not None:
                c["derivationSource"] = source
            if count is not None:
                c["expectedCount"] = count
    doc["passed"] = sum(1 for c in doc["checks"] if c["result"] == "PASS")
    doc["failed"] = sum(1 for c in doc["checks"] if c["result"] == "FAIL")
    doc["notApplicable"] = sum(1 for c in doc["checks"] if c["result"] == "NOT_APPLICABLE")


scenario("N1-na-without-justification",
         lambda d: (as_na(d), "MIR-002 -> NOT_APPLICABLE with no reason and no derivationSource")[1],
         ["NOT_APPLICABLE without a reason"])

scenario("N2-na-while-registry-names-items",
         lambda d: (as_na(d, reason="nothing to close", source=".iacode/policies/audit-registry.json",
                          count=0),
                    "MIR-002 -> fully justified NOT_APPLICABLE while the registry names CP11-F-001")[1],
         ["NOT_APPLICABLE while the canonical sources name 1 applicable audit finding"])

scenario("N3-na-with-nonzero-expected-count",
         lambda d: (as_na(d, reason="nothing to close", source=".iacode/policies/audit-registry.json",
                          count=3), "MIR-002 -> NOT_APPLICABLE with expectedCount=3")[1],
         ["expectedCount=3"])


def downgrade(d):
    as_na(d, reason="nothing to close", source=".iacode/policies/audit-registry.json", count=0)
    d["schemaVersion"] = "1.0.0"
    return "MIR-002 -> NOT_APPLICABLE under report schemaVersion 1.0.0"


scenario("N4-na-under-report-version-1.0.0", downgrade,
         ["requires the justification fields of report schemaVersion 1.1.0"])


def counted_as_pass(d):
    as_na(d, reason="nothing to close", source=".iacode/policies/audit-registry.json", count=0)
    d["passed"] = d["passed"] + d["notApplicable"]
    d["notApplicable"] = 0
    return "the inapplicable dimension counted as a passing one"


scenario("N5-na-counted-as-a-pass", counted_as_pass,
         ["passed does not match the recorded checks"])

out = Path(sys.argv[2])
out.write_text(json.dumps(RESULTS, indent=2), encoding="utf-8")
failed = [r for r in RESULTS if r["verdict"] == "FAIL"]
print(f"\nNA_ESCAPE_PROBE={'PASS' if not failed else 'FAIL'} {len(RESULTS)-len(failed)}/{len(RESULTS)}")
sys.exit(0 if not failed else 1)
