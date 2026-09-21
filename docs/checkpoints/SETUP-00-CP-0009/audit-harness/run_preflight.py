#!/usr/bin/env python3
"""Section 15: preflight freshness, measured by mutating the inputs in a disposable clone.

The preflight under test is the one sealed in SETUP-00-CP-0008. For each mutation the
experiment asks two questions:

  1. does the stored preflight become STALE or INVALID?
  2. does a preflight regenerated after the mutation pass?

A control that only answers the first would be a control that can never be satisfied.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
import os as _os
from pathlib import Path as _Path
_DEFAULT_ROOT = _Path(__file__).resolve().parents[4]

ROOT = Path(_os.environ.get("IACODE_ROOT") or _DEFAULT_ROOT)
PROBE = r'''
import json, sys
from pathlib import Path
sys.path.insert(0, "scripts/development-ledger")
from lessons import preflight_staleness, build_preflight, preflight_fingerprint
root = Path(".").resolve()
stored = json.loads(Path("docs/checkpoints/SETUP-00-CP-0008/LESSON-PREFLIGHT.json").read_text(encoding="utf-8"))
before = preflight_staleness(root, stored, "SETUP-00")
fresh = build_preflight(root, stored.get("gate"), stored.get("scope"),
                        stored.get("technologies") or [], stored.get("modules") or [])
fresh["inputsFingerprint"] = preflight_fingerprint(
    root, stored.get("gate"), stored.get("scope"),
    stored.get("technologies") or [], stored.get("modules") or [])
fresh.setdefault("schemaVersion", stored.get("schemaVersion"))
fresh.setdefault("policyVersion", stored.get("policyVersion"))
after = preflight_staleness(root, fresh, "SETUP-00")
print(json.dumps({"stored": before, "regenerated": after,
                  "storedApplicable": len(stored.get("applicable") or []),
                  "freshApplicable": len(fresh.get("applicable") or [])}))
'''


def rmtree(path: Path) -> None:
    def force(func, target, _info):
        try:
            os.chmod(target, 0o700)
            func(target)
        except Exception:
            pass
    if path.exists():
        shutil.rmtree(path, onerror=force)
        if path.exists():
            time.sleep(0.5)
            shutil.rmtree(path, onerror=force)


def clone(workdir: Path) -> Path:
    target = workdir / "clone"
    rmtree(target)
    subprocess.run(["git", "clone", "--quiet", "--no-hardlinks", str(ROOT), str(target)],
                   check=True, capture_output=True)
    subprocess.run(["git", "checkout", "--quiet", "-B", "main",
                    "iacode-checkpoints/SETUP-00-CP-0008"], cwd=target, check=True,
                   capture_output=True)
    return target


def lessons_of(root: Path):
    path = root / ".iacode" / "memory" / "lessons.jsonl"
    return path, [json.loads(line) for line in
                  path.read_text(encoding="utf-8").splitlines() if line.strip()]


def save_lessons(path: Path, lessons) -> None:
    path.write_text("\n".join(json.dumps(item, ensure_ascii=False) for item in lessons) + "\n",
                    encoding="utf-8", newline="\n")


def probe(root: Path):
    proc = subprocess.run([sys.executable, "-c", PROBE], cwd=root,
                          capture_output=True, text=True)
    if proc.returncode != 0:
        return {"error": (proc.stdout + proc.stderr)[-800:]}
    return json.loads(proc.stdout.strip().splitlines()[-1])


def change_active_lesson(root: Path) -> None:
    path, lessons = lessons_of(root)
    for lesson in lessons:
        if lesson["status"] == "GUARDED":
            lesson["severity"] = "LOW"
            break
    save_lessons(path, lessons)


def retire_lesson(root: Path) -> None:
    path, lessons = lessons_of(root)
    for lesson in lessons:
        if lesson["status"] == "GUARDED":
            lesson["status"] = "RETIRED"
            break
    save_lessons(path, lessons)


def change_applicability(root: Path) -> None:
    path, lessons = lessons_of(root)
    for lesson in lessons:
        if lesson["applicability"].get("gates") == ["*"]:
            lesson["applicability"]["gates"] = ["GATE 3"]
            break
    save_lessons(path, lessons)


def change_registry(root: Path) -> None:
    path = root / ".iacode" / "memory" / "guardrails" / "registry.json"
    document = json.loads(path.read_text(encoding="utf-8"))
    document["guardrails"][0]["title"] = document["guardrails"][0]["title"] + " (audit mutation)"
    path.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8", newline="\n")


def change_policy(root: Path) -> None:
    path = root / ".iacode" / "memory" / "POLICY.json"
    document = json.loads(path.read_text(encoding="utf-8"))
    document["auditNote"] = "mutated by the CP-0009 preflight freshness experiment"
    path.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8", newline="\n")


def change_schema(root: Path) -> None:
    path = root / ".iacode" / "schemas" / "lesson.schema.json"
    document = json.loads(path.read_text(encoding="utf-8"))
    document["description"] = "mutated by the CP-0009 preflight freshness experiment"
    path.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8", newline="\n")


GATE_PROBE = r'''
import json, sys
from pathlib import Path
sys.path.insert(0, "scripts/development-ledger")
from lessons import preflight_staleness
stored = json.loads(Path("docs/checkpoints/SETUP-00-CP-0008/LESSON-PREFLIGHT.json").read_text(encoding="utf-8"))
print(json.dumps({"otherGate": preflight_staleness(Path(".").resolve(), stored, "GATE 1")}))
'''


def main() -> int:
    workdir = Path(sys.argv[1])
    workdir.mkdir(parents=True, exist_ok=True)
    results = []

    baseline = clone(workdir)
    observed = probe(baseline)
    results.append({"id": "PRE-000", "mutation": "none (control)",
                    "storedStale": bool(observed.get("stored")),
                    "regeneratedFresh": not observed.get("regenerated"),
                    "observed": observed,
                    "result": "OK" if not observed.get("stored") and not observed.get("regenerated")
                    else "UNEXPECTED"})

    cases = [
        ("PRE-001", "an active lesson changed", change_active_lesson),
        ("PRE-002", "a lesson retired", retire_lesson),
        ("PRE-003", "applicability changed", change_applicability),
        ("PRE-004", "the guardrail registry changed", change_registry),
        ("PRE-005a", "the memory policy changed", change_policy),
        ("PRE-005b", "the lesson schema changed", change_schema),
    ]
    for scenario_id, description, mutate in cases:
        root = clone(workdir)
        mutate(root)
        observed = probe(root)
        stale = bool(observed.get("stored"))
        regenerated_ok = not observed.get("regenerated")
        results.append({"id": scenario_id, "mutation": description,
                        "storedStale": stale, "regeneratedFresh": regenerated_ok,
                        "observed": observed,
                        "result": "DEFENDED" if stale and regenerated_ok else "ESCAPED"})

    root = clone(workdir)
    proc = subprocess.run([sys.executable, "-c", GATE_PROBE], cwd=root,
                          capture_output=True, text=True)
    payload = json.loads(proc.stdout.strip().splitlines()[-1]) if proc.returncode == 0 else {}
    results.append({"id": "PRE-006", "mutation": "the Gate changed",
                    "storedStale": bool(payload.get("otherGate")),
                    "regeneratedFresh": True, "observed": payload,
                    "result": "DEFENDED" if payload.get("otherGate") else "ESCAPED"})

    for item in results:
        print("[" + item["id"] + "] " + item["result"] + " :: " + item["mutation"])
        print("      " + json.dumps(item["observed"])[:400])
    (workdir / "preflight-results.json").write_text(
        json.dumps(results, indent=2) + "\n", encoding="utf-8", newline="\n")
    bad = [item for item in results if item["result"] in ("ESCAPED", "UNEXPECTED")]
    print("TOTAL=" + str(len(results)) + " PROBLEMS=" + str(len(bad)))
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
