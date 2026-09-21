#!/usr/bin/env python3
"""The adversarial battery this audit owns, executed against disposable copies of the repository.

Every scenario runs against a fresh copy of a pristine snapshot, so no attack inherits the state of
another: the second M0 audit reported every attack as defended while the refusals came from leftover
state, and that failure class is the reason the null-mutation control below is mandatory rather than
decorative.

The control runs first and must be ACCEPTED. If the unmutated snapshot is refused, nothing after it
means anything and the battery reports INVALID instead of a row of defences.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

VALIDATOR = "scripts/development-ledger/validate_checkpoint.py"
MILESTONE = "scripts/development-ledger/milestone_status.py"
LESSONS = "scripts/development-ledger/validate_lessons.py"
INTEGRITY = "scripts/development-ledger/verify_integrity.py"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def run(root: Path, *argv: str) -> tuple[int, str]:
    completed = subprocess.run(
        [sys.executable, *argv], cwd=root, capture_output=True, text=True, check=False)
    return completed.returncode, (completed.stdout + completed.stderr).strip()


def git(root: Path, *argv: str) -> tuple[int, str]:
    completed = subprocess.run(
        ["git", *argv], cwd=root, capture_output=True, text=True, check=False)
    return completed.returncode, completed.stdout.strip()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, document: Any) -> None:
    path.write_text(
        json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


class Battery:
    def __init__(self, snapshot: Path, workdir: Path, checkpoint: str, subject: str) -> None:
        self.snapshot = snapshot
        self.workdir = workdir
        self.checkpoint = checkpoint
        self.subject = subject
        self.scenarios: list[dict[str, Any]] = []
        self.control: dict[str, Any] | None = None
        self._serial = 0

    def _copy(self) -> Path:
        self._serial += 1
        target = self.workdir / f"case-{self._serial:03d}"
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(self.snapshot, target, symlinks=True)
        return target

    def attestation_path(self, root: Path) -> Path:
        directory = root / ".iacode" / "attestations"
        candidates = sorted(item for item in directory.glob("*.json"))
        if not candidates:
            raise RuntimeError("the snapshot carries no attestation to attack")
        return candidates[0]

    def scenario(self, identifier: str, target: str, mutation: str,
                 mutate: Callable[[Path], None],
                 check: Callable[[Path], tuple[str, bool]],
                 category: str = "additional") -> None:
        root = self._copy()
        try:
            mutate(root)
            observed, defended = check(root)
        finally:
            pass
        self.scenarios.append({
            "attackId": identifier,
            "category": category,
            "target": target,
            "mutation": mutation,
            "expectedDefense": "reject",
            "observed": observed[:400],
            "result": "DEFENDED" if defended else "ESCAPED",
        })
        shutil.rmtree(root, ignore_errors=True)

    def run_control(self) -> None:
        root = self._copy()
        code, output = run(root, VALIDATOR)
        milestone_code, milestone_output = run(root, MILESTONE, "--milestone", "M0")
        accepted = code == 0 and milestone_code == 0 and "PASSED" in milestone_output
        self.control = {
            "control": "null-mutation",
            "detail": "the unmutated snapshot is validated through the identical path",
            "validator": output[:300],
            "milestone": milestone_output[:300],
            "result": "VALID" if accepted else "INVALID",
        }
        shutil.rmtree(root, ignore_errors=True)


def validator_refuses(root: Path, fragment: str) -> tuple[str, bool]:
    code, output = run(root, VALIDATOR)
    return f"exit={code} {output}", code != 0 and fragment in output


def milestone_refuses(root: Path, fragment: str = "") -> tuple[str, bool]:
    code, output = run(root, MILESTONE, "--milestone", "M0")
    ok = code != 0 and "NOT_PASSED" in output and (not fragment or fragment in output)
    return f"exit={code} {output}", ok


def lessons_refuse(root: Path, fragment: str) -> tuple[str, bool]:
    code, output = run(root, LESSONS)
    return f"exit={code} {output}", code != 0 and fragment in output


def integrity_refuses(root: Path, fragment: str) -> tuple[str, bool]:
    code, output = run(root, INTEGRITY)
    return f"exit={code} {output}", code != 0 and fragment in output


def build(battery: Battery) -> None:
    subject = battery.subject
    checkpoint = battery.checkpoint

    def edit_attestation(**changes: Any) -> Callable[[Path], None]:
        def mutate(root: Path) -> None:
            path = battery.attestation_path(root)
            document = read_json(path)
            document.update(changes)
            write_json(path, document)
        return mutate

    def drop_field(field: str) -> Callable[[Path], None]:
        def mutate(root: Path) -> None:
            path = battery.attestation_path(root)
            document = read_json(path)
            document.pop(field, None)
            write_json(path, document)
        return mutate

    # -- the attestation ------------------------------------------------------------------
    battery.scenario(
        "ATT-01", "attestation subject", "Attest a checkpoint other than the sealed subject",
        edit_attestation(subjectCheckpoint="SETUP-00-CP-0001"),
        lambda root: validator_refuses(root, "not"))
    battery.scenario(
        "ATT-02", "attestation subject", "Attest a commit the subject tag does not resolve to",
        edit_attestation(subjectCommit="0" * 40),
        lambda root: validator_refuses(root, "subjectCommit"))
    battery.scenario(
        "ATT-03", "attestation author", "Name the subject as its own auditor",
        edit_attestation(auditCheckpoint=subject),
        lambda root: validator_refuses(root, "may not be authored by the delivery it judges"))
    battery.scenario(
        "ATT-04", "attestation author", "Claim a verdict another checkpoint authored",
        edit_attestation(auditCheckpoint="SETUP-00-CP-0009"),
        lambda root: validator_refuses(root, "may only carry the verdict of the audit it performed"))
    battery.scenario(
        "ATT-05", "attestation verdict", "Promote on a review that was not approved",
        edit_attestation(reviewResult="REWORK_REQUIRED"),
        lambda root: validator_refuses(root, "requires APPROVED"))
    battery.scenario(
        "ATT-06", "attestation verdict", "Promote on a failed Red Team",
        edit_attestation(redTeamResult="RED_TEAM_FAIL"),
        lambda root: validator_refuses(root, "requires RED_TEAM_PASS"))
    battery.scenario(
        "ATT-07", "attestation verdict", "Promote on incomplete coverage",
        edit_attestation(completeness=99.9),
        lambda root: validator_refuses(root, "requires 100.0"))
    battery.scenario(
        "ATT-08", "attestation verdict", "Promote on incomplete evidence coverage",
        edit_attestation(evidenceCoverage=0.0),
        lambda root: validator_refuses(root, "requires 100.0"))
    battery.scenario(
        "ATT-09", "attestation verdict", "Promote on a failing test result",
        edit_attestation(testResult="FAIL"),
        lambda root: validator_refuses(root, "requires PASS"))
    battery.scenario(
        "ATT-10", "attestation mechanism", "Declare an unrecognised validation mechanism",
        edit_attestation(validationMechanism="SELF_AUDIT"),
        lambda root: validator_refuses(root, "recognised mechanisms"))
    battery.scenario(
        "ATT-11", "attestation mechanism", "Claim a fresh-session audit without a fresh session",
        edit_attestation(freshSession=False),
        lambda root: validator_refuses(root, "requires freshSession=true"))
    battery.scenario(
        "ATT-12", "attestation mechanism",
        "Claim a cross-tool audit while recording that cross-tool execution was unavailable",
        edit_attestation(validationMechanism="CROSS_TOOL_INDEPENDENT_AUDIT",
                         crossToolValidation="NOT_AVAILABLE"),
        lambda root: validator_refuses(root, "contradicts the mechanism it claims"))
    battery.scenario(
        "ATT-13", "attestation schema", "Declare an older attestation schema version",
        edit_attestation(schemaVersion="1.0.0"),
        lambda root: validator_refuses(root, "schemaVersion"))
    battery.scenario(
        "ATT-14", "attestation schema", "Remove a required field",
        drop_field("auditorRole"),
        lambda root: validator_refuses(root, "requires auditorRole"))
    def attest_an_older_checkpoint(root: Path) -> None:
        """Point both the attestation and the claim at an older, already approved delivery.

        Mutating the attestation alone is refused for the wrong reason: the claim in STATE.json
        still names the real subject, so the lookup simply finds nothing. The attack has to move
        both, which is what an actor trying to pass an easier subject would do.
        """
        older = "SETUP-00-CP-0008"
        commit = "c53f4c59a77870414324efa6b5f61b35d26c5090"
        path = battery.attestation_path(root)
        document = read_json(path)
        document["subjectCheckpoint"] = older
        document["subjectCommit"] = commit
        write_json(path, document)
        state = root / "docs" / "checkpoints" / checkpoint / "STATE.json"
        document = read_json(state)
        document["externalAttestation"]["subjectCheckpoint"] = older
        document["externalAttestation"]["subjectCommit"] = commit
        write_json(state, document)

    battery.scenario(
        "ATT-15", "attestation subject", "Attest an older, easier checkpoint",
        attest_an_older_checkpoint,
        lambda root: validator_refuses(root, "audit judges the delivery it follows"))

    def remove_attestation(root: Path) -> None:
        for path in (root / ".iacode" / "attestations").glob("*.json"):
            path.unlink()

    battery.scenario(
        "ATT-16", "milestone derivation", "Remove the attestation and keep the claimed status",
        remove_attestation,
        lambda root: validator_refuses(root, "attestation"))
    battery.scenario(
        "ATT-17", "milestone derivation", "Derive the verdict with no attestation at all",
        remove_attestation,
        lambda root: milestone_refuses(root))

    def claim_external(root: Path) -> None:
        path = battery.attestation_path(root)
        document = read_json(path)
        write_json(path, document)
        state = root / "docs" / "checkpoints" / checkpoint / "STATE.json"
        document = read_json(state)
        document["status"] = "MILESTONE_EXTERNAL_PASS"
        write_json(state, document)
        status = root / "docs" / "checkpoints" / checkpoint / "STATUS.md"
        status.write_text("# Status\n\nMILESTONE_EXTERNAL_PASS\n",
                          encoding="utf-8", newline="\n")

    battery.scenario(
        "ATT-18", "pass vocabulary",
        "Record a cross-tool milestone status from a fresh-session audit",
        claim_external,
        lambda root: validator_refuses(root, "MILESTONE_EXTERNAL_PASS"))

    # -- the integrity chain --------------------------------------------------------------
    def move_tag(root: Path) -> None:
        git(root, "tag", "-f", "iacode-checkpoints/SETUP-00-CP-0005",
            "refs/tags/iacode-checkpoints/SETUP-00-CP-0006")

    battery.scenario(
        "INT-01", "sealed history", "Move a historical checkpoint tag onto another commit",
        move_tag, lambda root: integrity_refuses(root, "resolves to"), category="mandatory")

    def rewrite_sealed(root: Path) -> None:
        path = root / "docs" / "checkpoints" / "SETUP-00-CP-0005" / "STATUS.md"
        path.write_text("# Status\n\nGATE_PASS\n", encoding="utf-8", newline="\n")
        git(root, "add", "-A")
        git(root, "-c", "user.name=Audit", "-c", "user.email=audit@example.invalid",
            "commit", "--quiet", "-m", "tamper")
        git(root, "tag", "-f", "iacode-checkpoints/SETUP-00-CP-0005", "HEAD")

    battery.scenario(
        "INT-02", "sealed history", "Rewrite sealed content and move its tag onto the rewrite",
        rewrite_sealed, lambda root: integrity_refuses(root, "SETUP-00-CP-0005"),
        category="mandatory")

    def break_link(root: Path) -> None:
        path = root / ".iacode" / "anchors" / "checkpoint-chain.json"
        document = read_json(path)
        document["anchors"][3]["previousAnchorHash"] = "0" * 64
        write_json(path, document)

    battery.scenario(
        "INT-03", "integrity chain", "Break the link between two consecutive anchors",
        break_link, lambda root: integrity_refuses(root, "chain"), category="mandatory")

    def drop_middle_anchor(root: Path) -> None:
        path = root / ".iacode" / "anchors" / "checkpoint-chain.json"
        document = read_json(path)
        document["anchors"] = [item for item in document["anchors"]
                               if item["checkpointId"] != "SETUP-00-CP-0006"]
        write_json(path, document)

    battery.scenario(
        "INT-04", "integrity chain", "Remove the anchor of a sealed checkpoint",
        drop_middle_anchor,
        lambda root: integrity_refuses(root, "SETUP-00-CP-0006"), category="mandatory")

    def drop_owed_anchor(root: Path) -> None:
        path = root / ".iacode" / "anchors" / "checkpoint-chain.json"
        document = read_json(path)
        document["anchors"] = [item for item in document["anchors"]
                               if item["checkpointId"] != subject]
        write_json(path, document)

    battery.scenario(
        "INT-05", "successor duty",
        "Skip the anchor this checkpoint owes its sealed predecessor",
        drop_owed_anchor,
        lambda root: validator_refuses(root, subject), category="mandatory")

    def forge_anchor_hash(root: Path) -> None:
        path = root / ".iacode" / "anchors" / "checkpoint-chain.json"
        document = read_json(path)
        document["anchors"][2]["treeHash"] = "0" * 40
        write_json(path, document)

    battery.scenario(
        "INT-06", "integrity chain", "Forge an anchored tree without recomputing the digest",
        forge_anchor_hash, lambda root: integrity_refuses(root, "anchorHash"))

    # -- the engineering memory and the preflight ------------------------------------------
    def mutate_lessons(root: Path) -> None:
        path = root / ".iacode" / "memory" / "lessons.jsonl"
        rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()
                if line.strip()]
        rows[0]["title"] = rows[0]["title"] + " (edited after the preflight)"
        path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
                        encoding="utf-8", newline="\n")

    battery.scenario(
        "PRE-01", "lesson preflight", "Change the memory after the preflight was recorded",
        mutate_lessons, lambda root: validator_refuses(root, "STALE"), category="mandatory")

    def forge_preflight_fingerprint(root: Path) -> None:
        path = root / "docs" / "checkpoints" / checkpoint / "LESSON-PREFLIGHT.json"
        document = read_json(path)
        document["inputsFingerprint"] = "0" * 64
        write_json(path, document)

    battery.scenario(
        "PRE-02", "lesson preflight", "Forge the recorded preflight fingerprint",
        forge_preflight_fingerprint, lambda root: validator_refuses(root, "STALE"))

    def narrow_preflight(root: Path) -> None:
        path = root / "docs" / "checkpoints" / checkpoint / "LESSON-PREFLIGHT.json"
        document = read_json(path)
        document["derivedRequirements"] = document["derivedRequirements"][:-1]
        write_json(path, document)

    battery.scenario(
        "PRE-03", "lesson preflight", "Drop a derived lesson requirement from the preflight",
        narrow_preflight, lambda root: validator_refuses(root, "preflight"))

    def documentation_only_guardrail(root: Path) -> None:
        path = root / ".iacode" / "memory" / "lessons.jsonl"
        rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()
                if line.strip()]
        for row in rows:
            if row["status"] == "GUARDED":
                row["prevention"] = [{"kind": "documentation", "reference": "docs/ROADMAP.md",
                                      "description": "documentation only"}]
                break
        path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
                        encoding="utf-8", newline="\n")

    battery.scenario(
        "MEM-01", "guarded semantics", "Replace a preventive control with documentation only",
        documentation_only_guardrail,
        lambda root: lessons_refuse(root, "documentation alone"), category="mandatory")

    def relocate_registry(root: Path) -> None:
        path = root / ".iacode" / "memory" / "POLICY.json"
        document = read_json(path)
        document["guardrailRegistry"] = "guardrails/elsewhere.json"
        write_json(path, document)

    battery.scenario(
        "MEM-02", "memory policy", "Declare a relocatable guardrail registry the code never reads",
        relocate_registry,
        lambda root: lessons_refuse(root, "guardrailRegistry"))

    def guarded_lesson_calls_itself_unguarded(root: Path) -> None:
        path = root / ".iacode" / "memory" / "lessons.jsonl"
        rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()
                if line.strip()]
        for row in rows:
            if row["status"] == "GUARDED":
                row["notes"] = "Not guarded: nothing prevents this."
                break
        path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
                        encoding="utf-8", newline="\n")

    battery.scenario(
        "MEM-03", "memory prose", "Let a GUARDED lesson describe itself as unguarded",
        guarded_lesson_calls_itself_unguarded,
        lambda root: lessons_refuse(root, "not guarded"))

    def drop_guardrail(root: Path) -> None:
        path = root / ".iacode" / "memory" / "guardrails" / "registry.json"
        document = read_json(path)
        document["guardrails"] = document["guardrails"][:-1]
        write_json(path, document)

    battery.scenario(
        "MEM-04", "guardrail registry", "Remove a guardrail a GUARDED lesson names",
        drop_guardrail, lambda root: validator_refuses(root, "guardrail"))

    # -- evidence and staleness ------------------------------------------------------------
    def touch_scope(root: Path) -> None:
        path = root / "scripts" / "development-ledger" / "anchors.py"
        path.write_text(path.read_text(encoding="utf-8") + "\n# audit staleness probe\n",
                        encoding="utf-8", newline="\n")

    battery.scenario(
        "STL-01", "gate staleness", "Edit the assurance scope after the last green cycle",
        touch_scope, lambda root: validator_refuses(root, "STALE"), category="mandatory")

    def forge_counts(root: Path) -> None:
        path = root / "docs" / "checkpoints" / checkpoint / "COUNTS.json"
        document = read_json(path)
        document["counts"]["TESTS"]["numerator"] = 99999
        document["counts"]["TESTS"]["denominator"] = 99999
        write_json(path, document)

    battery.scenario(
        "STL-02", "derived counts", "Forge the derived test count",
        forge_counts, lambda root: validator_refuses(root, "contradicts the derived"),
        category="mandatory")

    def inflate_count(root: Path) -> None:
        path = root / "docs" / "checkpoints" / checkpoint / "COUNTS.json"
        document = read_json(path)
        document["counts"]["TESTS"]["numerator"] = (
            document["counts"]["TESTS"]["denominator"] * 2)
        write_json(path, document)

    battery.scenario(
        "STL-03", "derived counts", "Record more passing cases than the suite contains",
        inflate_count, lambda root: validator_refuses(root, "contradicts the derived"))

    def blocker_with_readiness(root: Path) -> None:
        path = root / "docs" / "checkpoints" / checkpoint / "STATE.json"
        document = read_json(path)
        document["blockedBy"] = ["an unresolved blocker"]
        write_json(path, document)

    battery.scenario(
        "STL-04", "readiness invariant", "Carry a blocker while claiming a milestone verdict",
        blocker_with_readiness, lambda root: validator_refuses(root, "blockedBy"),
        category="mandatory")

    def drop_inventory_entry(root: Path) -> None:
        path = root / "docs" / "checkpoints" / checkpoint / "FILES.json"
        document = read_json(path)
        document["filesCreated"] = document["filesCreated"][:-1]
        write_json(path, document)

    battery.scenario(
        "STL-05", "file inventory", "Remove an entry from the declared change set",
        drop_inventory_entry, lambda root: validator_refuses(root, "FILES.json"),
        category="mandatory")

    # The planted value is assembled at run time from harmless parts, which is the same convention
    # the product battery uses: the repository never stores a credential-shaped literal, because
    # the secret policy applies to this harness exactly as it applies to everything else.
    planted = "gh" + "p_" + "A" * 24

    def secret_in_memory(root: Path) -> None:
        path = root / ".iacode" / "memory" / "lessons.jsonl"
        rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()
                if line.strip()]
        rows[0]["symptom"] = f"credential {planted}"
        path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
                        encoding="utf-8", newline="\n")

    def secret_refused_without_disclosure(root: Path) -> tuple[str, bool]:
        code, output = run(root, LESSONS)
        return (f"exit={code} {output}",
                code != 0 and "secret pattern detected" in output and planted not in output)

    battery.scenario(
        "SEC-01", "secret handling",
        "Insert a credential-shaped value into the memory and require a refusal that does not "
        "repeat it",
        secret_in_memory, secret_refused_without_disclosure, category="mandatory")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", type=Path, required=True,
                        help="a pristine copy of the repository under attack")
    parser.add_argument("--workdir", type=Path, required=True)
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--subject", required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    args.workdir.mkdir(parents=True, exist_ok=True)
    battery = Battery(args.snapshot.resolve(), args.workdir.resolve(),
                      args.checkpoint, args.subject)
    battery.run_control()
    if battery.control["result"] != "VALID":
        report = {
            "schemaVersion": "1.0.0",
            "generatedAt": _now(),
            "auditCheckpoint": args.checkpoint,
            "subjectCheckpoint": args.subject,
            "baselineControl": battery.control,
            "scenarios": [],
            "result": "INVALID",
            "note": ("the unmutated snapshot was refused, so no refusal in this battery could be "
                     "attributed to a mutation; nothing is claimed as defended"),
        }
        args.out.write_text(
            json.dumps(report, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8", newline="\n")
        print("BATTERY=INVALID the null-mutation control was refused")
        return 2

    build(battery)
    defended = [item for item in battery.scenarios if item["result"] == "DEFENDED"]
    escaped = [item for item in battery.scenarios if item["result"] == "ESCAPED"]
    report = {
        "schemaVersion": "1.0.0",
        "generatedAt": _now(),
        "auditCheckpoint": args.checkpoint,
        "subjectCheckpoint": args.subject,
        "baselineControl": battery.control,
        "scenarios": battery.scenarios,
        "total": len(battery.scenarios),
        "defended": len(defended),
        "escaped": len(escaped),
        "mandatory": sum(1 for item in battery.scenarios if item["category"] == "mandatory"),
        "additional": sum(1 for item in battery.scenarios if item["category"] == "additional"),
        "result": "DEFENDED" if not escaped else "ESCAPED",
    }
    args.out.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"BATTERY={report['result']} total={report['total']} defended={report['defended']} "
          f"escaped={report['escaped']} control={battery.control['result']}")
    for item in escaped:
        print(f"- ESCAPED {item['attackId']}: {item['mutation']} :: {item['observed'][:200]}")
    return 0 if not escaped else 1


if __name__ == "__main__":
    raise SystemExit(main())
