#!/usr/bin/env python3
"""The adversarial battery of this audit, independent of ``m0_red_team.py``.

Every scenario runs against its own disposable clone of the repository, detached at the sealed
subject tag, so no scenario inherits another's leftover state. A **null-mutation control** runs
first through the identical path and must be accepted before any refusal is attributed to a
mutation: the second ``M0`` audit's first harness reported every attack as defended while the
refusals came from leftover state.

Mutating a sealed checkout necessarily makes the worktree dirty, and the validator says so. A
scenario is therefore judged by whether the *attack-specific* refusal appears, not merely by a
non-zero exit code, which any dirty tree would produce.

    python attack_battery.py --json <out.json>
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

HARNESS = Path(__file__).resolve().parent
CHECKPOINT = HARNESS.parent
ROOT = CHECKPOINT.parents[2]
SUBJECT = "SETUP-00-CP-0012"
TAG = f"refs/tags/iacode-checkpoints/{SUBJECT}"


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


VALIDATOR = "scripts/development-ledger/validate_checkpoint.py"
MIRROR = "scripts/development-ledger/m0_mirror_audit.py"
INTEGRITY = "scripts/development-ledger/verify_integrity.py"
LESSONS = "scripts/development-ledger/validate_lessons.py"
MILESTONE = "scripts/development-ledger/milestone_status.py"


def validate(clone: Path) -> tuple[int, str]:
    return _run(clone, VALIDATOR)


def mirror(clone: Path) -> tuple[int, str]:
    return _run(clone, MIRROR, "--checkpoint", f"docs/checkpoints/{SUBJECT}")


def integrity(clone: Path) -> tuple[int, str]:
    return _run(clone, INTEGRITY)


def lessons(clone: Path) -> tuple[int, str]:
    return _run(clone, LESSONS)


def milestone(clone: Path) -> tuple[int, str]:
    return _run(clone, MILESTONE, "--milestone", "M0")


@dataclass(frozen=True)
class Attack:
    identifier: str
    category: str
    target: str
    description: str
    mutation_text: str
    expected: str
    control: Callable[[Path], tuple[int, str]]
    mutate: Callable[[Path], str]
    must_match: str
    mandatory: bool = True
    evidence: tuple[str, ...] = field(default=())


# ---------------------------------------------------------------------------------------------
# mutations
# ---------------------------------------------------------------------------------------------


def _mirror_path(clone: Path) -> Path:
    return clone / "docs" / "checkpoints" / SUBJECT / "M0-INTERNAL-MIRROR.json"


def _closure_path(clone: Path) -> Path:
    return clone / "docs" / "checkpoints" / SUBJECT / "CP11-FINDINGS-CLOSURE.json"


def _registry_path(clone: Path) -> Path:
    return clone / ".iacode" / "policies" / "audit-registry.json"


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _store(path: Path, document: Any) -> None:
    path.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8", newline="\n")


def _recount(document: dict[str, Any]) -> None:
    document["passed"] = sum(1 for c in document["checks"] if c["result"] == "PASS")
    document["failed"] = sum(1 for c in document["checks"] if c["result"] == "FAIL")
    document["notApplicable"] = sum(
        1 for c in document["checks"] if c["result"] == "NOT_APPLICABLE")


def _set_na(document: dict[str, Any], check_id: str, **fields: Any) -> None:
    for check in document["checks"]:
        if check["id"] == check_id:
            check["result"] = "NOT_APPLICABLE"
            check.update(fields)
    _recount(document)


def na_unjustified(clone: Path) -> str:
    document = _load(_mirror_path(clone))
    _set_na(document, "MIR-002")
    _store(_mirror_path(clone), document)
    return "MIR-002 declared NOT_APPLICABLE with no reason and no derivation source"


def na_over_named_work(clone: Path) -> str:
    document = _load(_mirror_path(clone))
    _set_na(document, "MIR-002", reason="nothing to close", expectedCount=0,
            derivationSource=".iacode/policies/audit-registry.json")
    _store(_mirror_path(clone), document)
    return "MIR-002 declared NOT_APPLICABLE while the registry still names CP11-F-001"


def na_with_items(clone: Path) -> str:
    document = _load(_mirror_path(clone))
    _set_na(document, "MIR-002", reason="nothing to close", expectedCount=4,
            derivationSource=".iacode/policies/audit-registry.json")
    _store(_mirror_path(clone), document)
    return "MIR-002 declared NOT_APPLICABLE while carrying four applicable items"


def na_old_report_version(clone: Path) -> str:
    document = _load(_mirror_path(clone))
    _set_na(document, "MIR-002", reason="nothing to close", expectedCount=0,
            derivationSource=".iacode/policies/audit-registry.json")
    document["schemaVersion"] = "1.0.0"
    _store(_mirror_path(clone), document)
    return "an inapplicable dimension recorded under mirror report schemaVersion 1.0.0"


def na_counted_as_pass(clone: Path) -> str:
    document = _load(_mirror_path(clone))
    _set_na(document, "MIR-002", reason="nothing to close", expectedCount=0,
            derivationSource=".iacode/policies/audit-registry.json")
    document["passed"] += document["notApplicable"]
    document["notApplicable"] = 0
    _store(_mirror_path(clone), document)
    return "the inapplicable dimension counted as a passing one"


def na_every_dimension(clone: Path) -> str:
    document = _load(_mirror_path(clone))
    for check in document["checks"]:
        check["result"] = "NOT_APPLICABLE"
        check["reason"] = "declared inapplicable by this attack"
        check["expectedCount"] = 0
        check["derivationSource"] = ".iacode/policies/audit-registry.json"
    _recount(document)
    _store(_mirror_path(clone), document)
    return "every mirror dimension declared inapplicable at once"


def mirror_fail_reported_as_pass(clone: Path) -> str:
    document = _load(_mirror_path(clone))
    document["checks"][0]["result"] = "FAIL"
    document["result"] = "PASS"
    _recount(document)
    _store(_mirror_path(clone), document)
    return "a failing dimension kept while the overall result claims PASS"


def finding_reopened(clone: Path) -> str:
    document = _load(_closure_path(clone))
    document["findings"][0]["status"] = "OPEN"
    _store(_closure_path(clone), document)
    return "the closed audit finding set back to OPEN"


def closure_record_removed(clone: Path) -> str:
    _closure_path(clone).unlink()
    return "the closure record the audit registry requires deleted"


def closure_emptied(clone: Path) -> str:
    document = _load(_closure_path(clone))
    document["findings"] = []
    document["total"] = 0
    document["closed"] = 0
    _store(_closure_path(clone), document)
    return "the delivery declaring that it has no finding to close"


def registry_entry_removed(clone: Path) -> str:
    document = _load(_registry_path(clone))
    document["audits"] = [a for a in document["audits"] if a["auditId"] != "M0-CP-0011"]
    _store(_registry_path(clone), document)
    return "the audit removed from the registry so its findings stop being applicable"


def report_repointed(clone: Path) -> str:
    empty = clone / "docs" / "checkpoints" / SUBJECT / "NO-FINDINGS.md"
    empty.write_text("# Nothing\n", encoding="utf-8")
    document = _load(_registry_path(clone))
    for audit in document["audits"]:
        if audit["auditId"] == "M0-CP-0011":
            audit["reviewReport"] = f"docs/checkpoints/{SUBJECT}/NO-FINDINGS.md"
    _store(_registry_path(clone), document)
    return "the registry repointed at a report from which no finding can be parsed"


def anchor_removed(clone: Path) -> str:
    path = clone / ".iacode" / "anchors" / "checkpoint-chain.json"
    document = _load(path)
    document["anchors"] = document["anchors"][:-1]
    _store(path, document)
    return "the anchor of a sealed checkpoint removed from the chain"


def anchor_commit_forged(clone: Path) -> str:
    path = clone / ".iacode" / "anchors" / "checkpoint-chain.json"
    document = _load(path)
    document["anchors"][-1]["commit"] = "0" * 40
    _store(path, document)
    return "an anchored commit replaced with one the tag does not resolve to"


def tag_moved(clone: Path) -> str:
    subprocess.run(["git", "tag", "-f", "iacode-checkpoints/SETUP-00-CP-0010",
                    "refs/tags/iacode-checkpoints/SETUP-00-CP-0009"],
                   cwd=clone, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return "a historical checkpoint tag moved onto another commit"


def counts_forged(clone: Path) -> str:
    path = clone / "docs" / "checkpoints" / SUBJECT / "COUNTS.json"
    document = _load(path)
    document["counts"]["TESTS"]["numerator"] = 9999
    document["counts"]["TESTS"]["denominator"] = 9999
    _store(path, document)
    return "the derived test count replaced with a larger one"


def blocker_with_readiness(clone: Path) -> str:
    path = clone / "docs" / "checkpoints" / SUBJECT / "STATE.json"
    document = _load(path)
    document["blockedBy"] = ["INVENTED-BLOCKER"]
    _store(path, document)
    return "a blocker carried while the checkpoint claims READY_FOR_REVIEW"


def self_asserted_milestone(clone: Path) -> str:
    path = clone / "docs" / "checkpoints" / SUBJECT / "STATE.json"
    document = _load(path)
    document["status"] = "MILESTONE_EXTERNAL_PASS"
    document["milestone"]["status"] = "PASSED"
    document["secondToolValidation"]["status"] = "PASSED"
    document["secondToolValidation"]["tool"] = "invented"
    document["secondToolValidation"]["provider"] = "invented"
    document["secondToolValidation"]["validatedAt"] = "2026-09-21T00:00:00Z"
    _store(path, document)
    return "the delivery promoting itself to a cross-tool milestone status"


def attestation_mechanism_upgraded(clone: Path) -> str:
    path = clone / ".iacode" / "attestations" / "M0-CP-0011.json"
    document = _load(path)
    document["validationMechanism"] = "CROSS_TOOL_INDEPENDENT_AUDIT"
    document["reviewResult"] = "APPROVED"
    _store(path, document)
    return "a fresh-session attestation relabelled as a cross-tool one while it records that "\
           "cross-tool execution was unavailable"


def attestation_review_upgraded(clone: Path) -> str:
    path = clone / ".iacode" / "attestations" / "M0-CP-0011.json"
    document = _load(path)
    document["reviewResult"] = "APPROVED"
    document["subjectCommit"] = "0" * 40
    _store(path, document)
    return "an attestation approved for a commit the subject tag does not resolve to"


def guarded_lesson_unguarded(clone: Path) -> str:
    path = clone / ".iacode" / "memory" / "lessons.jsonl"
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()]
    for row in rows:
        if row.get("status") == "GUARDED":
            row["guardrails"] = []
            break
    path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
                    encoding="utf-8", newline="\n")
    return "a GUARDED lesson stripped of the guardrail it names"


def secret_planted(clone: Path) -> str:
    path = clone / ".iacode" / "memory" / "lessons.jsonl"
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()]
    rows[0]["notes"] = "credential " + "sk-" + ("z" * 20)
    path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
                    encoding="utf-8", newline="\n")
    return "a credential-shaped value planted in the engineering memory"


def inventory_entry_removed(clone: Path) -> str:
    path = clone / "docs" / "checkpoints" / SUBJECT / "FILES.json"
    document = _load(path)
    for key in ("filesCreated", "filesModified"):
        if document.get(key):
            document[key] = document[key][1:]
            break
    _store(path, document)
    return "an entry removed from the declared change set"


ATTACKS: tuple[Attack, ...] = (
    Attack("NA-01", "mirror applicability", "inapplicable dimension",
           "An inapplicable dimension with no justification.",
           "declare MIR-002 NOT_APPLICABLE without a reason", "reject",
           validate, na_unjustified, "NOT_APPLICABLE without a reason"),
    Attack("NA-02", "mirror applicability", "inapplicable dimension",
           "A fully justified inapplicable dimension over work the registry still names.",
           "declare MIR-002 NOT_APPLICABLE while CP11-F-001 is applicable", "reject",
           validate, na_over_named_work,
           "NOT_APPLICABLE while the canonical sources name 1 applicable audit finding"),
    Attack("NA-03", "mirror applicability", "inapplicable dimension",
           "An inapplicable dimension that admits it has items.",
           "declare MIR-002 NOT_APPLICABLE with expectedCount=4", "reject",
           validate, na_with_items, "expectedCount=4"),
    Attack("NA-04", "mirror applicability", "report version",
           "An inapplicable dimension under the report version that cannot justify one.",
           "record a NOT_APPLICABLE check under schemaVersion 1.0.0", "reject",
           validate, na_old_report_version,
           "requires the justification fields of report schemaVersion 1.1.0"),
    Attack("NA-05", "mirror applicability", "counting",
           "An inapplicable dimension counted as a passing one.",
           "add the inapplicable count to passed", "reject",
           validate, na_counted_as_pass, "passed does not match the recorded checks"),
    Attack("NA-06", "mirror applicability", "whole report",
           "Every dimension declared inapplicable at once.",
           "declare all eighteen checks NOT_APPLICABLE", "reject",
           validate, na_every_dimension,
           "NOT_APPLICABLE while the canonical sources name"),
    Attack("MIR-A1", "mirror integrity", "overall result",
           "A failing dimension kept while the report claims a pass.",
           "set one check to FAIL and the result to PASS", "reject",
           validate, mirror_fail_reported_as_pass, "a failed check cannot produce a PASS"),
    Attack("FND-01", "audit findings", "closure record",
           "A closed finding reopened.",
           "set CP11-F-001 back to OPEN", "reject",
           mirror, finding_reopened, "FAIL MIR-002"),
    Attack("FND-02", "audit findings", "closure record",
           "The required closure record deleted.",
           "delete CP11-FINDINGS-CLOSURE.json", "reject",
           mirror, closure_record_removed, "FAIL MIR-002"),
    Attack("FND-03", "audit findings", "expected set",
           "The delivery declaring it has nothing to close.",
           "empty the closure record's finding list", "reject",
           mirror, closure_emptied, "FAIL MIR-002"),
    Attack("FND-04", "audit findings", "audit registry",
           "The audit deleted from the registry so its findings stop applying.",
           "remove the M0-CP-0011 entry", "reject",
           mirror, registry_entry_removed, "FAIL MIR-009"),
    Attack("FND-05", "audit findings", "sealed report",
           "The registry repointed at a report with no parseable finding.",
           "repoint reviewReport at an empty document", "reject",
           mirror, report_repointed, "no finding could be parsed"),
    Attack("INT-01", "integrity", "anchor chain",
           "The anchor of a sealed checkpoint removed.",
           "drop the last anchor", "reject",
           integrity, anchor_removed, "INTEGRITY_INVALID"),
    Attack("INT-02", "integrity", "anchor chain",
           "An anchored commit replaced with one the tag does not resolve to.",
           "forge the anchored commit", "reject",
           integrity, anchor_commit_forged, "INTEGRITY_INVALID"),
    Attack("INT-03", "integrity", "sealed history",
           "A historical checkpoint tag moved onto another commit.",
           "force-move the SETUP-00-CP-0010 tag", "reject",
           integrity, tag_moved, "INTEGRITY_INVALID"),
    Attack("CNT-01", "derived counts", "COUNTS.json",
           "The derived test count replaced with a larger one.",
           "set TESTS to 9999/9999", "reject",
           validate, counts_forged, "COUNTS.json"),
    Attack("RDY-01", "readiness invariant", "STATE.json",
           "A blocker carried while claiming readiness.",
           "add an entry to blockedBy", "reject",
           validate, blocker_with_readiness, "blockedBy"),
    Attack("PRM-01", "promotion", "STATE.json",
           "The delivery promoting itself to a cross-tool milestone status.",
           "set MILESTONE_EXTERNAL_PASS and fill secondToolValidation", "reject",
           validate, self_asserted_milestone, "MILESTONE_EXTERNAL_PASS"),
    Attack("ATT-01", "attestation", "mechanism",
           "A fresh-session attestation relabelled as cross-tool.",
           "set validationMechanism to CROSS_TOOL_INDEPENDENT_AUDIT", "reject",
           milestone, attestation_mechanism_upgraded, "crossToolValidation"),
    Attack("ATT-02", "attestation", "subject",
           "An approved attestation for a commit the subject tag does not resolve to.",
           "approve the review and forge subjectCommit", "reject",
           milestone, attestation_review_upgraded, "REJECTED"),
    Attack("MEM-01", "engineering memory", "guarded semantics",
           "A GUARDED lesson stripped of its guardrail.",
           "empty the guardrails list of a GUARDED lesson", "reject",
           lessons, guarded_lesson_unguarded, "LESSONS_INVALID"),
    Attack("SEC-01", "secret handling", "engineering memory",
           "A credential-shaped value planted in the memory.",
           "write a credential into a lesson note", "reject",
           lessons, secret_planted, "LESSONS_INVALID"),
    Attack("STL-01", "file inventory", "FILES.json",
           "An entry removed from the declared change set.",
           "drop one declared path", "reject",
           validate, inventory_entry_removed, "FILES.json"),
)


def baseline_control() -> dict[str, Any]:
    """The unmutated subject through the identical path. It must be accepted."""
    with tempfile.TemporaryDirectory(prefix="cp13-control-") as workdir:
        clone = Path(workdir) / "clone"
        _clone(clone)
        code, output = validate(clone)
        accepted = code == 0 and "CHECKPOINT_VALID" in output
        return {
            "result": "VALID" if accepted else "INVALID",
            "detail": (
                f"the unmutated {SUBJECT} checkout, detached at its canonical tag, run through the "
                f"identical validation path: exit={code} {output.strip().splitlines()[0] if output.strip() else 'no output'}"),
            "evidence": [f"file:docs/checkpoints/{SUBJECT}/STATE.json"],
        }


def run_attack(attack: Attack) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix=f"cp13-{attack.identifier.lower()}-") as workdir:
        clone = Path(workdir) / "clone"
        _clone(clone)
        applied = attack.mutate(clone)
        code, output = attack.control(clone)
        matched = bool(re.search(re.escape(attack.must_match), output))
        defended = code != 0 and matched
        first = next((line.strip() for line in output.splitlines() if line.strip()), "no output")
        detail = next(
            (line.strip() for line in output.splitlines() if attack.must_match in line), first)
        return {
            "attackId": attack.identifier,
            "description": attack.description,
            "target": f"{attack.category}: {attack.target}",
            "mutation": applied,
            "expectedDefense": attack.expected,
            "observed": f"exit={code}; {detail[:240]}",
            "result": "DEFENDED" if defended else "ESCAPED",
            "evidence": list(attack.evidence) or [f"checkpoint:{HARNESS.name}/attack_battery.py"],
            "mandatory": attack.mandatory,
            "origin": "authored by the CP-0013 fresh-session independent audit",
        }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", type=Path, required=True)
    parser.add_argument("--only", default=None)
    args = parser.parse_args()

    control = baseline_control()
    print(f"CONTROL {control['result']}: {control['detail'][:160]}")
    if control["result"] != "VALID":
        print("BATTERY_REFUSED: the null-mutation control was not accepted")
        args.json.write_text(json.dumps({"baselineControl": control}, indent=2) + "\n",
                             encoding="utf-8", newline="\n")
        return 3

    selected = set((args.only or "").split(",")) if args.only else None
    results = []
    for attack in ATTACKS:
        if selected and attack.identifier not in selected:
            continue
        record = run_attack(attack)
        results.append(record)
        print(f"[{record['result']}] {record['attackId']} {record['observed'][:150]}")

    escaped = [item for item in results if item["result"] == "ESCAPED"]
    mandatory = [item for item in results if item["mandatory"]]
    payload = {
        "baselineControl": control,
        "attacks": results,
        "total": len(results),
        "defended": len(results) - len(escaped),
        "escaped": len(escaped),
        "mandatoryTotal": len(mandatory),
        "mandatoryDefended": len([i for i in mandatory if i["result"] == "DEFENDED"]),
        "result": "RED_TEAM_FAIL" if escaped else "RED_TEAM_PASS",
    }
    args.json.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
                         encoding="utf-8", newline="\n")
    print(f"BATTERY={payload['result']} defended={payload['defended']}/{payload['total']}")
    return 0 if not escaped else 1


if __name__ == "__main__":
    raise SystemExit(main())
