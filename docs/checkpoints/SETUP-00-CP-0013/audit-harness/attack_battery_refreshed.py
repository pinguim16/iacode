#!/usr/bin/env python3
"""Attacks that repair their own tracks before asking the control to refuse them.

Three attacks of ``attack_battery.py`` were refused by the file-inventory binding rather than by
the control they were aimed at: any edit to a sealed checkpoint changes a declared hash, and
``FILES.json`` says so before anything else looks at the content. That is a real defence, but it
is not evidence about the control under test.

These variants therefore re-derive the declared inventory hashes with the project's own
``finalize_checkpoint._refresh_inventory_hashes`` after mutating, exactly as an attacker who knows
the tooling would, and require the *aimed* control to produce the refusal. The subject checkpoint
is never modified: every scenario works in its own disposable clone.

    python attack_battery_refreshed.py --json <out.json>
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Callable

HARNESS = Path(__file__).resolve().parent
CHECKPOINT = HARNESS.parent
ROOT = CHECKPOINT.parents[2]
SUBJECT = "SETUP-00-CP-0012"
TAG = f"refs/tags/iacode-checkpoints/{SUBJECT}"

REFRESH = r"""
import json, sys
from pathlib import Path
sys.path.insert(0, "scripts/development-ledger")
from finalize_checkpoint import _refresh_inventory_hashes
from ledger_common import load_json, write_json
root = Path(".").resolve()
checkpoint = root / "docs" / "checkpoints" / "%s"
state = load_json(checkpoint / "STATE.json")
files = load_json(checkpoint / "FILES.json")
write_json(checkpoint / "FILES.json", _refresh_inventory_hashes(root, checkpoint, state, files))
print("INVENTORY_REFRESHED")
""" % SUBJECT


def _clone(destination: Path) -> None:
    subprocess.run(["git", "clone", "--quiet", "--no-hardlinks", str(ROOT), str(destination)],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(["git", "checkout", "--quiet", "--detach", TAG], cwd=destination, check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def _run(clone: Path, *argv: str) -> tuple[int, str]:
    environment = dict(os.environ)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    completed = subprocess.run([sys.executable, *argv], cwd=clone, text=True,
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False,
                               env=environment)
    return completed.returncode, completed.stdout


def _refresh(clone: Path) -> str:
    code, output = _run(clone, "-c", REFRESH)
    return f"inventory refresh exit={code} {output.strip().splitlines()[-1:] or ['']}"


def validate(clone: Path) -> tuple[int, str]:
    return _run(clone, "scripts/development-ledger/validate_checkpoint.py")


def _path(clone: Path, name: str) -> Path:
    return clone / "docs" / "checkpoints" / SUBJECT / name


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _store(path: Path, document: Any) -> None:
    path.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8", newline="\n")


def counts_forged(clone: Path) -> str:
    path = _path(clone, "COUNTS.json")
    document = _load(path)
    document["counts"]["TESTS"]["numerator"] = 9999
    document["counts"]["TESTS"]["denominator"] = 9999
    _store(path, document)
    return "the derived test count set to 9999/9999, then the declared inventory hashes re-derived"


def self_promoted(clone: Path) -> str:
    path = _path(clone, "STATE.json")
    document = _load(path)
    document["status"] = "MILESTONE_EXTERNAL_PASS"
    document["milestone"]["status"] = "PASSED"
    document["milestone"]["auditor"] = "this delivery"
    document["milestone"]["auditedAt"] = "2026-09-21T00:00:00Z"
    document["secondToolValidation"] = {
        "status": "PASSED", "tool": "invented", "provider": "invented", "model": "invented",
        "validatedAt": "2026-09-21T00:00:00Z", "justification": "invented", "evidence": []}
    document["independentReview"] = {
        "status": "APPROVED", "tool": "invented", "reviewedAt": "2026-09-21T00:00:00Z",
        "justification": "invented", "evidence": []}
    document["redTeam"] = {
        "status": "RED_TEAM_PASS", "tool": "invented", "executedAt": "2026-09-21T00:00:00Z",
        "justification": "invented", "evidence": []}
    _store(path, document)
    _path(clone, "STATUS.md").write_text(
        "# Status\n\nMILESTONE_EXTERNAL_PASS\n", encoding="utf-8", newline="\n")
    return ("the delivery promoting itself to MILESTONE_EXTERNAL_PASS with a filled "
            "secondToolValidation, a matching STATUS.md, and the inventory hashes re-derived")


def scope_made_stale(clone: Path) -> str:
    path = clone / ".iacode" / "policies" / "quality-gates.json"
    document = _load(path)
    document["auditNote"] = "edited after the last green cycle by the CP-0013 battery"
    _store(path, document)
    return ("a policy file edited after the last green Green Keeper cycle, then the declared "
            "inventory hashes re-derived")


ATTACKS: tuple[tuple[str, str, str, str, str, Callable[[Path], str], str], ...] = (
    ("CNT-02", "derived counts", "COUNTS.json",
     "The derived test count forged by an attacker who also repairs the inventory.",
     "set TESTS to 9999/9999 and refresh FILES.json", counts_forged,
     "contradicts the derived"),
    ("PRM-02", "promotion", "STATE.json",
     "A delivery promoting itself to a cross-tool milestone status, consistently.",
     "set MILESTONE_EXTERNAL_PASS everywhere and refresh FILES.json", self_promoted,
     "the verdict belongs to the audit checkpoint"),
    ("STL-02", "staleness", "assurance scope",
     "The audited scope changed after the last green cycle.",
     "edit a policy file and refresh FILES.json", scope_made_stale,
     "STALE"),
)


def baseline_control() -> dict[str, Any]:
    """The unmutated subject, refreshed the same way, through the identical path."""
    with tempfile.TemporaryDirectory(prefix="cp13-rcontrol-") as workdir:
        clone = Path(workdir) / "clone"
        _clone(clone)
        note = _refresh(clone)
        code, output = validate(clone)
        accepted = code == 0 and "CHECKPOINT_VALID" in output
        return {
            "result": "VALID" if accepted else "INVALID",
            "detail": (
                f"the unmutated {SUBJECT} checkout with its declared inventory hashes re-derived "
                f"by the same helper the attacks use ({note}), then validated: exit={code} "
                f"{(output.strip().splitlines() or ['no output'])[0]}"),
            "evidence": [f"file:docs/checkpoints/{SUBJECT}/FILES.json"],
        }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", type=Path, required=True)
    args = parser.parse_args()

    control = baseline_control()
    print(f"CONTROL {control['result']}: {control['detail'][:200]}")
    if control["result"] != "VALID":
        args.json.write_text(json.dumps({"baselineControl": control}, indent=2) + "\n",
                             encoding="utf-8", newline="\n")
        print("BATTERY_REFUSED: the null-mutation control was not accepted")
        return 3

    results = []
    for identifier, category, target, description, mutation, mutate, must_match in ATTACKS:
        with tempfile.TemporaryDirectory(prefix=f"cp13-{identifier.lower()}-") as workdir:
            clone = Path(workdir) / "clone"
            _clone(clone)
            applied = mutate(clone)
            refreshed = _refresh(clone)
            code, output = validate(clone)
            matched = [line.strip() for line in output.splitlines() if must_match in line]
            defended = code != 0 and bool(matched)
            detail = matched[0] if matched else (
                output.strip().splitlines() or ["no output"])[0]
            record = {
                "attackId": identifier,
                "description": description,
                "target": f"{category}: {target}",
                "mutation": f"{applied}; {refreshed}",
                "expectedDefense": "reject",
                "observed": f"exit={code}; {detail[:240]}",
                "result": "DEFENDED" if defended else "ESCAPED",
                "evidence": ["checkpoint:audit-harness/attack_battery_refreshed.py"],
                "mandatory": True,
                "origin": "authored by the CP-0013 fresh-session independent audit",
            }
            results.append(record)
            print(f"[{record['result']}] {identifier} {record['observed'][:170]}")

    escaped = [item for item in results if item["result"] == "ESCAPED"]
    payload = {
        "baselineControl": control,
        "attacks": results,
        "total": len(results),
        "defended": len(results) - len(escaped),
        "escaped": len(escaped),
        "result": "RED_TEAM_FAIL" if escaped else "RED_TEAM_PASS",
    }
    args.json.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
                         encoding="utf-8", newline="\n")
    print(f"BATTERY={payload['result']} defended={payload['defended']}/{payload['total']}")
    return 0 if not escaped else 1


if __name__ == "__main__":
    raise SystemExit(main())
