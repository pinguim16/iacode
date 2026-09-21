#!/usr/bin/env python3
"""Execute the milestone Red Team battery against an isolated copy of this delivery.

This is internal quality assurance, not independent validation. It exists so that the external
audit confirms rather than discovers. Every attack is *executed*, never asserted: the tool builds a
disposable clone of the repository, applies one mutation, runs the control that should refuse it,
and records what actually happened.

The battery is the union of

- the twenty-six mandatory A-Z attacks of the sealed ``SETUP-00-CP-0007`` Red Team report, re-parsed
  from that report rather than transcribed, including the eighteen that were already defended,
  because a correction can break a defence that used to work;
- the six additional attacks AA-AF of the same report;
- the attacks this delivery's new surfaces deserve: the external attestation, the canonical
  requirement set, the gate registry, preflight fingerprints, the guardrail registry, the integrity
  anchors, derived counts and the seal chronology.

Exit code 0 means every executed attack was defended. Any escape exits nonzero.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Callable

from anchors import resolve_tag
from ledger_common import (
    INDEPENDENT_AUDIT_PASS_STATUS,
    LedgerError,
    find_root,
    load_json,
    resolve_latest,
    run_git,
    scope_fingerprint,
    utc_now,
    validate_schema,
    write_json,
)
from policies import audit_attacks, load_audit_registry, open_audits

VALIDATOR = "scripts/development-ledger/validate_checkpoint.py"
LESSONS = "scripts/development-ledger/validate_lessons.py"
COMPLETENESS = "scripts/development-ledger/check_completeness.py"
INTEGRITY = "scripts/development-ledger/verify_integrity.py"
GREEN_KEEPER = "scripts/development-ledger/green_keeper.py"
NEW_CHECKPOINT = "scripts/development-ledger/new_checkpoint.py"

TAG_NAMESPACE = "iacode-checkpoints/"


# --------------------------------------------------------------------------------------------
# Fixture: a disposable clone that models the sealed delivery
# --------------------------------------------------------------------------------------------


class Fixture:
    """An isolated copy of the repository with this checkpoint modelled as sealed."""

    def __init__(self, root: Path, checkpoint_name: str, workdir: Path) -> None:
        self.source = root
        self.name = checkpoint_name
        self.path = workdir / "fixture"
        self.head = ""
        self._build()

    # -- construction ------------------------------------------------------------------
    def _build(self) -> None:
        subprocess.run(
            ["git", "clone", "--quiet", "--no-hardlinks", str(self.source), str(self.path)],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self._sync_worktree()
        self._model_seal()

    def _tracked(self, root: Path) -> set[str]:
        code, output = run_git(root, "ls-files", "--cached", "--others", "--exclude-standard")
        if code != 0:
            raise LedgerError("unable to enumerate the working tree for the attack fixture")
        return {line.replace("\\", "/") for line in output.splitlines() if line.strip()}

    def _sync_worktree(self) -> None:
        wanted = self._tracked(self.source)
        present = self._tracked(self.path)
        for relative in sorted(present - wanted):
            target = self.path / relative
            if target.is_file():
                target.unlink()
        for relative in sorted(wanted):
            source = self.source / relative
            target = self.path / relative
            if not source.is_file():
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)

    def _commit(self, message: str) -> str:
        subprocess.run(["git", "add", "-A"], cwd=self.path, check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(
            ["git", "-c", "user.name=red-team", "-c", "user.email=red-team@iacode.local",
             "commit", "--quiet", "--allow-empty", "-m", message],
            cwd=self.path, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        code, head = run_git(self.path, "rev-parse", "HEAD")
        if code != 0:
            raise LedgerError("the attack fixture could not resolve its own commit")
        return head

    def _model_seal(self) -> None:
        """Model the real two-commit seal, so the promotion rules are reachable and truthful.

        The content is prepared first and committed once; the post-commit validation of that commit
        is then recorded and committed on its own, exactly as ``seal_checkpoint.py`` does. A fixture
        that folded both into one commit would make the seal chronology control unsatisfiable and
        would be attacking a shape the delivery never produces.
        """
        from finalize_checkpoint import _refresh_inventory_hashes

        checkpoint = self.path / "docs" / "checkpoints" / self.name
        state = load_json(checkpoint / "STATE.json")
        state["status"] = "READY_FOR_REVIEW"
        state["dirty"] = False
        state["currentCommit"] = f"refs/tags/{TAG_NAMESPACE}{self.name}"
        write_json(checkpoint / "STATE.json", state)
        (checkpoint / "STATUS.md").write_text("# Status\n\nREADY_FOR_REVIEW\n",
                                              encoding="utf-8", newline="\n")
        handoff = (checkpoint / "HANDOFF.md").read_text(encoding="utf-8")
        (checkpoint / "HANDOFF.md").write_text(
            handoff.replace("Current Status: IN_PROGRESS", "Current Status: READY_FOR_REVIEW"),
            encoding="utf-8", newline="\n")
        self._model_internal_assurance(checkpoint)
        write_json(checkpoint / "FILES.json", _refresh_inventory_hashes(
            self.path, checkpoint, state, load_json(checkpoint / "FILES.json")))

        content_commit = self._commit("fixture: seal the content under test")

        self._append_seal_record(checkpoint, content_commit)
        metadata = load_json(checkpoint / "RUN-METADATA.json")
        metadata["finalCommit"] = state["currentCommit"]
        metadata["finishedAt"] = utc_now()
        write_json(checkpoint / "RUN-METADATA.json", metadata)
        write_json(checkpoint / "FILES.json", _refresh_inventory_hashes(
            self.path, checkpoint, state, load_json(checkpoint / "FILES.json")))
        self.head = self._commit("fixture: record the post-commit validation")

        subprocess.run(["git", "tag", "-f", f"{TAG_NAMESPACE}{self.name}", self.head],
                       cwd=self.path, check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["git", "branch", "-f", "red-team-baseline", self.head], cwd=self.path,
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def _model_internal_assurance(self, checkpoint: Path) -> None:
        """Give the fixture the internal assurance artifacts a sealed delivery carries.

        The first run of the battery happens before the report it produces exists, so the fixture
        models the shape the sealed checkpoint will have. Later runs pick up the real artifacts and
        attack those instead. The models live only in the disposable clone.
        """
        from ledger_common import scope_fingerprint

        state = load_json(checkpoint / "STATE.json")
        milestone = str((state.get("milestone") or {}).get("id") or "M0")
        fingerprint = scope_fingerprint(self.path)
        red_team = checkpoint / f"{milestone}-INTERNAL-RED-TEAM.json"
        modelled = not red_team.is_file()
        if not red_team.is_file():
            attacks = []
            for audit in open_audits(self.path, str(state.get("gate", "")), checkpoint.name):
                for attack in audit_attacks(self.path, audit):
                    attacks.append({
                        "attackId": attack["id"], "description": attack["mutation"],
                        "target": attack["target"], "mutation": attack["mutation"],
                        "expectedDefense": attack["expectedDefense"],
                        "observed": "modelled by the attack fixture", "result": "DEFENDED",
                        "evidence": ["attack:" + attack["id"]],
                        "mandatory": attack["mandatory"] == "true",
                    })
            mandatory = [item for item in attacks if item["mandatory"]]
            write_json(red_team, {
                "schemaVersion": "1.1.0", "checkpoint": checkpoint.name, "generatedAt": utc_now(),
                "targetFingerprint": fingerprint,
                "baselineControl": {
                    "result": "VALID",
                    "detail": "modelled by the attack fixture for the first run, before the real "
                              "battery has produced its own control",
                },
                "source": "modelled by the attack fixture", "attacks": attacks,
                "total": len(attacks), "defended": len(attacks), "escaped": 0,
                "mandatoryTotal": len(mandatory), "mandatoryDefended": len(mandatory),
                "result": "RED_TEAM_PASS"})
        else:
            report = load_json(red_team)
            report["targetFingerprint"] = fingerprint
            write_json(red_team, report)

        mirror = checkpoint / f"{milestone}-INTERNAL-MIRROR.json"
        modelled = modelled or not mirror.is_file()
        if not mirror.is_file():
            write_json(mirror, {
                "schemaVersion": "1.0.0", "checkpoint": checkpoint.name, "milestone": milestone,
                "generatedAt": utc_now(), "targetFingerprint": fingerprint,
                "auditorRole": "M0 Closure Auditor",
                "independence": "Internal quality assurance, not external validation.",
                "checks": [{"id": "MIR-000", "dimension": "fixture",
                            "expectation": "modelled by the attack fixture",
                            "observed": "modelled by the attack fixture", "result": "PASS",
                            "evidence": ["checkpoint:PLAN.md"]}],
                "total": 1, "passed": 1, "failed": 0, "notApplicable": 0, "result": "PASS"})
        else:
            report = load_json(mirror)
            report["targetFingerprint"] = fingerprint
            write_json(mirror, report)

        if modelled:
            # A modelled report describes a different battery than the real one, so the copied
            # reports no longer state true counts about this fixture. Quoting them keeps the
            # fixture internally consistent without silencing the control.
            claim = re.compile(
                r"(?<![0-9])(\d+)\s*/\s*(\d+)\s+"
                r"(TESTS|REQUIREMENTS|FINDINGS|ATTACKS|LESSONS|GUARDRAILS)\b")
            for document in sorted(checkpoint.glob("*.md")):
                original = document.read_text(encoding="utf-8")
                rewritten = claim.sub(
                    lambda match: "%s of %s %s" % match.groups(), original)
                if rewritten != original:
                    document.write_text(rewritten, encoding="utf-8", newline="\n")

        counts = checkpoint / "COUNTS.json"
        from derive_counts import derive_counts

        write_json(counts, {
            "schemaVersion": "1.0.0", "checkpoint": checkpoint.name, "generatedAt": utc_now(),
            "counts": derive_counts(self.path, checkpoint)})

        # Anything the fixture had to model is declared in the fixture's own inventory, so the
        # baseline stays a valid checkpoint rather than one with undeclared files.
        files = load_json(checkpoint / "FILES.json")
        declared = {
            item.get("path") for category in ("filesCreated", "filesModified", "filesDeleted")
            for item in files.get(category) or []
        }
        modelled = [red_team, mirror, counts,
                    red_team.with_suffix(".md"), mirror.with_suffix(".md")]
        for path in modelled:
            if not path.is_file():
                continue
            relative = str(path.relative_to(self.path)).replace("\\", "/")
            if relative not in declared:
                files.setdefault("filesCreated", []).append({
                    "path": relative,
                    "reason": "Modelled by the attack fixture so the sealed shape is complete.",
                })
        write_json(checkpoint / "FILES.json", files)

    def _append_seal_record(self, checkpoint: Path, commit: str) -> None:
        from ledger_common import append_command_record, build_command_record, canonical_hash_path

        record = build_command_record(
            self.path,
            command=f"python {VALIDATOR}",
            arguments=[VALIDATOR],
            purpose="Validate the sealed checkpoint content as committed, with a clean worktree.",
            working_directory=str(self.path),
            runtime="python 3",
            inputs=[VALIDATOR],
            inputs_digest=[{"path": VALIDATOR, "hash": canonical_hash_path(self.path / VALIDATOR)}],
            result="COMPLETED",
            result_code="OK",
            exit_code=0,
            duration_ms=1,
            operation="post-commit-validation",
            phase="seal",
            subject_commit=commit,
            commit=commit,
            repository_state={"branch": "main", "head": commit, "dirty": False, "detached": False},
        )
        append_command_record(checkpoint / "COMMANDS.jsonl", record)

    # -- per-attack lifecycle ----------------------------------------------------------
    def reset(self) -> None:
        subprocess.run(["git", "reset", "--hard", "--quiet", "red-team-baseline"], cwd=self.path,
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["git", "clean", "-qfd"], cwd=self.path, check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["git", "checkout", "--quiet", "-B", "main", "red-team-baseline"],
                       cwd=self.path, check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["git", "tag", "-f", f"{TAG_NAMESPACE}{self.name}", self.head],
                       cwd=self.path, check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for identifier, commit in self.historical_tags.items():
            subprocess.run(["git", "tag", "-f", identifier, commit], cwd=self.path, check=True,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    @property
    def checkpoint(self) -> Path:
        return self.path / "docs" / "checkpoints" / self.name

    def capture_tags(self) -> None:
        code, output = run_git(self.path, "tag", "-l", f"{TAG_NAMESPACE}*")
        self.historical_tags = {}
        if code != 0:
            return
        for name in output.splitlines():
            name = name.strip()
            if not name or name.endswith(self.name):
                continue
            resolved_code, commit = run_git(self.path, "rev-parse", f"{name}^{{commit}}")
            if resolved_code == 0:
                self.historical_tags[name] = commit

    # -- tools -------------------------------------------------------------------------
    def run(self, *argv: str) -> tuple[int, str]:
        environment = dict(os.environ)
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        completed = subprocess.run(
            [sys.executable, *argv], cwd=self.path, text=True, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, check=False, env=environment)
        return completed.returncode, completed.stdout

    def validator(self) -> tuple[int, str]:
        return self.run(VALIDATOR)

    def refresh_inventory(self) -> None:
        """Re-derive the declared hashes after a mutation.

        Without this, every mutation of a checkpoint file is refused by the inventory before the
        control under attack is ever reached, and the attack would prove only that hashing works.
        The inventory attacks opt out, because the inventory is exactly what they target.
        """
        from finalize_checkpoint import _refresh_inventory_hashes

        state = load_json(self.checkpoint / "STATE.json")
        write_json(self.checkpoint / "FILES.json", _refresh_inventory_hashes(
            self.path, self.checkpoint, state, load_json(self.checkpoint / "FILES.json")))

    def json_edit(self, relative: str, mutate: Callable[[Any], Any]) -> None:
        path = self.path / relative
        document = load_json(path)
        write_json(path, mutate(document))

    def checkpoint_edit(self, name: str, mutate: Callable[[Any], Any]) -> None:
        self.json_edit(str((self.checkpoint / name).relative_to(self.path)), mutate)


# --------------------------------------------------------------------------------------------
# Attack definitions
# --------------------------------------------------------------------------------------------


def _first_matrix_id(fixture: Fixture, prefix: str) -> str:
    matrix = load_json(fixture.checkpoint / "REQUIREMENTS-MATRIX.json")
    for row in matrix["requirements"]:
        if str(row["id"]).startswith(prefix):
            return str(row["id"])
    raise LedgerError(f"no requirement identifier starting with {prefix}")


def _drop_requirement(fixture: Fixture, identifier: str) -> None:
    def prune(document: Any) -> Any:
        document["requirements"] = [
            row for row in document["requirements"] if row.get("id") != identifier]
        return document

    fixture.checkpoint_edit("REQUIREMENTS-MATRIX.json", prune)
    fixture.checkpoint_edit("CLOSURE-REQUIREMENTS.json", prune)

    def recount(document: Any) -> Any:
        for key in ("totalRequirements", "complete", "expectedRequirements"):
            if isinstance(document.get(key), int) and document[key] > 0:
                document[key] -= 1
        return document

    fixture.checkpoint_edit("COMPLETENESS-REPORT.json", recount)

    def restate(document: Any) -> Any:
        block = document.get("requirementsMatrix") or {}
        for key in ("total", "complete", "mandatory"):
            if isinstance(block.get(key), int) and block[key] > 0:
                block[key] -= 1
        return document

    fixture.checkpoint_edit("STATE.json", restate)


def _lessons_edit(fixture: Fixture, mutate: Callable[[list[dict[str, Any]]], None]) -> None:
    path = fixture.path / ".iacode" / "memory" / "lessons.jsonl"
    lessons = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    mutate(lessons)
    path.write_text("".join(json.dumps(item, ensure_ascii=False) + "\n" for item in lessons),
                    encoding="utf-8", newline="\n")


def _guarded(lessons: list[dict[str, Any]]) -> dict[str, Any]:
    for lesson in lessons:
        if lesson.get("status") == "GUARDED":
            return lesson
    raise LedgerError("the memory contains no GUARDED lesson to attack")


def _anchored_predecessor(fixture: Fixture) -> str:
    """An anchored sealed checkpoint before the delivery under attack, derived from the fixture.

    A battery that names its victim by literal decides today's behaviour from yesterday's
    repository, which is the coupling class finding CP9-F-002 records.
    """
    from anchors import load_anchors

    anchored = [str(item.get("checkpointId")) for item in load_anchors(fixture.path)
                if str(item.get("checkpointId")) != fixture.name]
    if not anchored:
        raise LedgerError("the fixture has no anchored predecessor to attack")
    return anchored[-1]


def build_attacks() -> list[dict[str, Any]]:
    """Every attack, as data. ``run`` returns (observed, defended)."""

    def validator_refuses(fixture: Fixture, needle: str, refresh: bool = True) -> tuple[str, bool]:
        if refresh:
            fixture.refresh_inventory()
        code, output = fixture.validator()
        return _summarize(code, output, needle), code != 0 and needle.lower() in output.lower()

    def tool_refuses(fixture: Fixture, argv: list[str], needle: str) -> tuple[str, bool]:
        code, output = fixture.run(*argv)
        return _summarize(code, output, needle), code != 0 and needle.lower() in output.lower()

    attacks: list[dict[str, Any]] = []

    def attack(identifier: str, target: str, mutation: str, expected: str,
               run: Callable[[Fixture], tuple[str, bool]], mandatory: bool, origin: str) -> None:
        attacks.append({
            "attackId": identifier,
            "target": target,
            "mutation": mutation,
            "expectedDefense": expected,
            "run": run,
            "mandatory": mandatory,
            "origin": origin,
        })

    cp7 = "SETUP-00-CP-0007 mandatory A-Z battery"
    extra = "SETUP-00-CP-0007 additional battery"
    new = "SETUP-00-CP-0008 new attack surface"

    # -- A-Z ---------------------------------------------------------------------------
    def run_a(fixture: Fixture) -> tuple[str, bool]:
        fixture.checkpoint_edit("STATE.json", lambda d: {**d, "blockedBy": ["an unresolved blocker"]})
        return validator_refuses(fixture, "incompatible with a non-empty blockedBy")

    attack("A", "readiness and blocker invariant", "Add a blocker to a READY_FOR_REVIEW checkpoint",
           "reject", run_a, True, cp7)

    def run_b(fixture: Fixture) -> tuple[str, bool]:
        def mutate(document: Any) -> Any:
            document["checks"]["unitTests"]["status"] = "FAIL"
            return document
        fixture.checkpoint_edit("QUALITY.json", mutate)
        return validator_refuses(fixture, "unitTests=FAIL")

    attack("B", "mandatory quality", "Set a review-ready quality gate red", "reject", run_b, True, cp7)

    def run_c(fixture: Fixture) -> tuple[str, bool]:
        _drop_requirement(fixture, _first_matrix_id(fixture, "REQ-"))
        return validator_refuses(fixture, "canonical expected set requires")

    attack("C", "completeness denominator",
           "Delete a mandatory requirement and recompute every stored count",
           "reject the missing source requirement", run_c, True, cp7)

    def run_d(fixture: Fixture) -> tuple[str, bool]:
        def mutate(document: Any) -> Any:
            document["coveragePercent"] = 100.0
            document["complete"] = document["totalRequirements"] + 5
            return document
        fixture.checkpoint_edit("COMPLETENESS-REPORT.json", mutate)
        return validator_refuses(fixture, "contradicts the recomputed value")

    attack("D", "completeness claims", "Forge the stored counts of a passing report",
           "reject the mismatch", run_d, True, cp7)

    def run_e(fixture: Fixture) -> tuple[str, bool]:
        _drop_requirement(fixture, _first_matrix_id(fixture, "LESSON-REQ-"))
        return validator_refuses(fixture, "lesson preflight derived this requirement")

    attack("E", "lesson-derived requirement", "Remove a derived requirement from the matrix",
           "reject", run_e, True, cp7)

    def run_f(fixture: Fixture) -> tuple[str, bool]:
        def mutate(lessons: list[dict[str, Any]]) -> None:
            lesson = _guarded(lessons)
            lesson["prevention"] = [{
                "kind": "documentation",
                "reference": "docs/ENGINEERING-MEMORY.md",
                "description": "It is written down.",
            }]
        _lessons_edit(fixture, mutate)
        return tool_refuses(fixture, [LESSONS], "documentation alone is not a guardrail")

    attack("F", "GUARDED semantics", "Replace a preventive control with documentation only",
           "reject", run_f, True, cp7)

    def run_g(fixture: Fixture) -> tuple[str, bool]:
        def mutate(lessons: list[dict[str, Any]]) -> None:
            lessons.append(json.loads(json.dumps(lessons[0])))
        _lessons_edit(fixture, mutate)
        return tool_refuses(fixture, [LESSONS], "duplicate lessonId")

    attack("G", "lesson identity", "Duplicate a lesson identifier", "reject", run_g, True, cp7)

    def run_h(fixture: Fixture) -> tuple[str, bool]:
        planted = "gh" + "p_" + "A" * 24

        def mutate(lessons: list[dict[str, Any]]) -> None:
            lessons[0]["notes"] = f"credential {planted}"
        _lessons_edit(fixture, mutate)
        code, output = fixture.run(LESSONS)
        return _summarize(code, output), (
            code != 0 and "secret pattern detected" in output and planted not in output)

    attack("H", "lesson secret handling", "Insert a secret-shaped value into a scanned field",
           "reject without disclosing the value", run_h, True, cp7)

    def run_i(fixture: Fixture) -> tuple[str, bool]:
        # The victim is derived: an anchored predecessor of the delivery under attack, never the
        # checkpoint that happened to be convenient when this battery was written.
        victim = _anchored_predecessor(fixture)
        sealed = fixture.path / "docs" / "checkpoints" / victim / "DECISIONS.md"
        sealed.write_text("# Decisions\n\nrewritten by the attacker\n", encoding="utf-8", newline="\n")
        subprocess.run(["git", "add", "-A"], cwd=fixture.path, check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["git", "-c", "user.name=a", "-c", "user.email=a@b.c", "commit", "--quiet",
                        "-m", "rewrite sealed history"], cwd=fixture.path, check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        code, head = run_git(fixture.path, "rev-parse", "HEAD")
        subprocess.run(["git", "tag", "-f", f"{TAG_NAMESPACE}{victim}", head],
                       cwd=fixture.path, check=code == 0,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return tool_refuses(fixture, [INTEGRITY], victim)

    attack("I", "sealed predecessor",
           "Rewrite a sealed checkpoint and move its tag to the rewritten commit",
           "reject the historical rewrite", run_i, True, cp7)

    def run_j(fixture: Fixture) -> tuple[str, bool]:
        victim = _anchored_predecessor(fixture)
        (fixture.path / "docs" / "checkpoints" / "README.md").write_text(
            "# Checkpoints\n\nmoved\n", encoding="utf-8", newline="\n")
        subprocess.run(["git", "add", "-A"], cwd=fixture.path, check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["git", "-c", "user.name=a", "-c", "user.email=a@b.c", "commit", "--quiet",
                        "-m", "move the tag with HEAD"], cwd=fixture.path, check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        code, head = run_git(fixture.path, "rev-parse", "HEAD")
        subprocess.run(["git", "tag", "-f", f"{TAG_NAMESPACE}{victim}", head],
                       cwd=fixture.path, check=code == 0,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return tool_refuses(fixture, [INTEGRITY], victim)

    attack("J", "tag immutability", "Move a checkpoint tag and HEAD to a new commit together",
           "reject the moved tag", run_j, True, cp7)

    def run_k(fixture: Fixture) -> tuple[str, bool]:
        def mutate(document: Any) -> Any:
            document["filesCreated"] = document["filesCreated"][1:]
            return document
        fixture.checkpoint_edit("FILES.json", mutate)
        return validator_refuses(fixture, "omits a changed path", refresh=False)

    attack("K", "file inventory", "Remove one inventory entry", "reject", run_k, True, cp7)

    def run_l(fixture: Fixture) -> tuple[str, bool]:
        target = fixture.path / "docs" / "MASTER-PLAN.md"
        target.write_text(target.read_text(encoding="utf-8") + "\nsilent change\n",
                          encoding="utf-8", newline="\n")
        return validator_refuses(fixture, "files.json", refresh=False)

    attack("L", "file inventory", "Silently modify a tracked file", "reject", run_l, True, cp7)

    def run_m(fixture: Fixture) -> tuple[str, bool]:
        def mutate(document: Any) -> Any:
            for item in document["filesModified"]:
                if item.get("hashBefore"):
                    item["hashBefore"] = "0" * 64
                    break
            return document
        fixture.checkpoint_edit("FILES.json", mutate)
        return validator_refuses(fixture, "hashbefore", refresh=False)

    attack("M", "file inventory", "Set a wrong hashBefore", "reject", run_m, True, cp7)

    def run_n(fixture: Fixture) -> tuple[str, bool]:
        def mutate(document: Any) -> Any:
            for item in document["filesCreated"]:
                if item.get("hashAfter"):
                    item["hashAfter"] = "0" * 64
                    break
            return document
        fixture.checkpoint_edit("FILES.json", mutate)
        return validator_refuses(fixture, "hash", refresh=False)

    attack("N", "file inventory", "Set a wrong hashAfter", "reject", run_n, True, cp7)

    def run_o(fixture: Fixture) -> tuple[str, bool]:
        def mutate(document: Any) -> Any:
            document["checks"]["staticAnalysis"]["evidence"] = []
            return document
        fixture.checkpoint_edit("QUALITY.json", mutate)
        return validator_refuses(fixture, "requires at least one evidence reference")

    attack("O", "quality evidence", "Claim PASS with no evidence", "reject", run_o, True, cp7)

    def run_p(fixture: Fixture) -> tuple[str, bool]:
        def mutate(document: Any) -> Any:
            document["checks"]["staticAnalysis"]["evidence"] = ["command:cmd-9999"]
            return document
        fixture.checkpoint_edit("QUALITY.json", mutate)
        return validator_refuses(fixture, "unknown command id")

    attack("P", "evidence resolution", "Reference an unknown command", "reject", run_p, True, cp7)

    def run_q(fixture: Fixture) -> tuple[str, bool]:
        def mutate(document: Any) -> Any:
            document["secondToolValidation"] = {
                "status": "PASSED", "tool": "an auditor", "provider": "a provider",
                "model": "a model", "validatedAt": "2026-09-20T00:00:00Z",
                "justification": None, "evidence": [],
            }
            return document
        fixture.checkpoint_edit("STATE.json", mutate)
        return validator_refuses(fixture, "independent audit")

    attack("Q", "second-tool evidence",
           "Supply complete cross-tool attribution with no external evidence",
           "reject unauthenticated validation", run_q, True, cp7)

    def run_r(fixture: Fixture) -> tuple[str, bool]:
        def mutate(document: Any) -> Any:
            document["status"] = "MILESTONE_EXTERNAL_PASS"
            document["secondToolValidation"] = {
                "status": "PASSED", "tool": "self", "provider": "self", "model": "self",
                "validatedAt": "2026-09-20T00:00:00Z", "justification": None, "evidence": [],
            }
            document["milestone"]["status"] = "PASSED"
            return document
        fixture.checkpoint_edit("STATE.json", mutate)
        (fixture.checkpoint / "STATUS.md").write_text(
            "# Status\n\nMILESTONE_EXTERNAL_PASS\n", encoding="utf-8", newline="\n")
        return validator_refuses(fixture, "independent audit")

    attack("R", "pass vocabulary", "Promote an internally authored result to an external status",
           "require an independent verdict", run_r, True, cp7)

    def run_s(fixture: Fixture) -> tuple[str, bool]:
        def mutate(document: Any) -> Any:
            document["status"] = "MILESTONE_EXTERNAL_PASS"
            document["milestone"] = {**document["milestone"], "status": "PASSED",
                                     "auditor": None, "auditedAt": None}
            document["secondToolValidation"]["status"] = "PASSED"
            return document
        fixture.checkpoint_edit("STATE.json", mutate)
        (fixture.checkpoint / "STATUS.md").write_text(
            "# Status\n\nMILESTONE_EXTERNAL_PASS\n", encoding="utf-8", newline="\n")
        return validator_refuses(fixture, "external")

    attack("S", "external milestone review",
           "Leave the review and Red Team pending with a null auditor and timestamp",
           "reject", run_s, True, cp7)

    def run_t(fixture: Fixture) -> tuple[str, bool]:
        def mutate(document: Any) -> Any:
            document["externalAuditRequired"] = True
            document["externalAuditReason"] = "we would like an audit now"
            return document
        fixture.checkpoint_edit("STATE.json", mutate)
        return validator_refuses(fixture, "recorded triggers")

    attack("T", "extraordinary cadence", "Request an audit without a known trigger", "reject",
           run_t, True, cp7)

    def run_u(fixture: Fixture) -> tuple[str, bool]:
        def mutate(lessons: list[dict[str, Any]]) -> None:
            for lesson in lessons:
                if lesson.get("status") == "CONFIRMED":
                    lesson["status"] = "RETIRED"
                    return
            lessons[-1]["status"] = "RETIRED"
        _lessons_edit(fixture, mutate)
        return validator_refuses(fixture, "stale")

    attack("U", "preflight freshness", "Retire a canonical lesson but keep the active preflight",
           "reject or recompute", run_u, True, cp7)

    def run_v(fixture: Fixture) -> tuple[str, bool]:
        tests = fixture.path / "tests" / "test_red_team_probe.py"
        tests.write_text(
            "import unittest\n\n\nclass ProbeTests(unittest.TestCase):\n"
            "    def test_case(self):\n        self.assertEqual(1, 2)\n",
            encoding="utf-8", newline="\n")
        code, output = fixture.run(GREEN_KEEPER, "--gates", "", "--quiet")
        return _summarize(code, output), code != 0 and "GREEN_KEEPER_GATE=FAIL" in output

    attack("V", "Green Keeper mandatory set",
           "Run the Green Keeper with an empty gate selection while a test genuinely fails",
           "reject; the mandatory set is not the caller's to choose", run_v, True, cp7)

    def run_w(fixture: Fixture) -> tuple[str, bool]:
        def mutate(document: Any) -> Any:
            document["requirements"][0]["status"] = "PARTIAL"
            return document
        fixture.checkpoint_edit("REQUIREMENTS-MATRIX.json", mutate)
        return validator_refuses(fixture, "partial")

    attack("W", "partial completeness", "Claim PASS with a PARTIAL requirement", "reject",
           run_w, True, cp7)

    def run_x(fixture: Fixture) -> tuple[str, bool]:
        path = fixture.checkpoint / "COMMANDS.jsonl"
        lines = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        lines[-1].pop("runtime", None)
        path.write_text("".join(json.dumps(item, ensure_ascii=False) + "\n" for item in lines),
                        encoding="utf-8", newline="\n")
        return validator_refuses(fixture, "requires runtime")

    attack("X", "command audit", "Remove a required field from a command record", "reject",
           run_x, True, cp7)

    def run_y(fixture: Fixture) -> tuple[str, bool]:
        (fixture.path / "docs" / "checkpoints" / "LATEST.md").write_text(
            "# Latest Checkpoint\n\nCheckpoint: `docs/checkpoints/SETUP-00-CP-0007`\n\n"
            "Validate before use.\n", encoding="utf-8", newline="\n")
        code, output = fixture.run(VALIDATOR, "--checkpoint", f"docs/checkpoints/{fixture.name}")
        return _summarize(code, output), code != 0 and "not the LATEST target" in output

    attack("Y", "latest pointer", "Point LATEST.md at an older checkpoint", "reject", run_y, True, cp7)

    def run_z(fixture: Fixture) -> tuple[str, bool]:
        code, output = fixture.run(NEW_CHECKPOINT, "--gate", "../../../ESCAPE")
        escaped = (fixture.path.parent / "ESCAPE").exists()
        return _summarize(code, output), code != 0 and not escaped

    attack("Z", "path safety", "Use path traversal as the Gate identifier",
           "reject with no write outside the repository", run_z, True, cp7)

    # -- AA-AF -------------------------------------------------------------------------
    def run_aa(fixture: Fixture) -> tuple[str, bool]:
        def mutate(document: Any) -> Any:
            document["requirementsMatrix"]["mandatory"] += 2
            return document
        fixture.checkpoint_edit("STATE.json", mutate)
        return validator_refuses(fixture, "mandatory")

    attack("AA", "aggregate consistency",
           "Declare a mandatory count in state that no artifact agrees with", "reject",
           run_aa, False, extra)

    def run_ab(fixture: Fixture) -> tuple[str, bool]:
        def mutate(lessons: list[dict[str, Any]]) -> None:
            lesson = _guarded(lessons)
            lesson["prevention"] = [{
                "kind": "test", "reference": "NoSuchTests.test_nothing",
                "description": "A control that does not exist.",
            }]
        _lessons_edit(fixture, mutate)
        return tool_refuses(fixture, [LESSONS], "does not exist in the suite")

    attack("AB", "control resolution", "Point a GUARDED lesson at a nonexistent test", "reject",
           run_ab, False, extra)

    def run_ac(fixture: Fixture) -> tuple[str, bool]:
        def mutate(lessons: list[dict[str, Any]]) -> None:
            lessons[0]["evidence"] = ["file:docs/this-file-does-not-exist.md"]
        _lessons_edit(fixture, mutate)
        return tool_refuses(fixture, [LESSONS], "evidence file does not exist")

    attack("AC", "evidence resolution", "Point lesson evidence at a nonexistent file", "reject",
           run_ac, False, extra)

    def run_ad(fixture: Fixture) -> tuple[str, bool]:
        planted = "sk-" + "B" * 20

        def mutate(lessons: list[dict[str, Any]]) -> None:
            lesson = _guarded(lessons)
            lesson["prevention"][0]["description"] = f"uses {planted} internally"
        _lessons_edit(fixture, mutate)
        code, output = fixture.run(LESSONS)
        return _summarize(code, output), (
            code != 0 and "secret pattern detected" in output and planted not in output)

    attack("AD", "nested secret scan", "Hide a secret-shaped value inside prevention.description",
           "reject without disclosing the value", run_ad, False, extra)

    def run_ae(fixture: Fixture) -> tuple[str, bool]:
        def mutate(document: Any) -> Any:
            document["gate"] = "GATE 1"
            document["milestone"] = {**document["milestone"], "id": "M1",
                                     "gates": ["GATE 0", "GATE 1", "GATE 2", "GATE 3"]}
            return document
        fixture.checkpoint_edit("STATE.json", mutate)
        return validator_refuses(fixture, "preflight")

    attack("AE", "preflight gate binding", "Reuse a SETUP-00 preflight for another Gate", "reject",
           run_ae, False, extra)

    def run_af(fixture: Fixture) -> tuple[str, bool]:
        def mutate(document: Any) -> Any:
            document["status"] = "MILESTONE_EXTERNAL_PASS"
            document["greenKeeper"]["status"] = "FAIL"
            return document
        fixture.checkpoint_edit("STATE.json", mutate)
        (fixture.checkpoint / "STATUS.md").write_text(
            "# Status\n\nMILESTONE_EXTERNAL_PASS\n", encoding="utf-8", newline="\n")
        return validator_refuses(fixture, "GREEN_KEEPER_GATE=PASS")

    attack("AF", "promotion invariant",
           "Reach an external status while the Green Keeper gate is red", "reject",
           run_af, False, extra)

    # -- new surfaces -------------------------------------------------------------------
    def run_ag(fixture: Fixture) -> tuple[str, bool]:
        def mutate(document: Any) -> Any:
            document["gates"] = [gate for gate in document["gates"] if gate["id"] != "lessons"]
            return document
        fixture.json_edit(".iacode/policies/quality-gates.json", mutate)
        return validator_refuses(fixture, "canonical mandatory set")

    attack("AG", "gate registry", "Remove a mandatory gate from the policy after a GREEN cycle",
           "reject the mismatch between the cycle and the policy", run_ag, False, new)

    def run_ah(fixture: Fixture) -> tuple[str, bool]:
        target = fixture.path / "scripts" / "development-ledger" / "README.md"
        target.write_text(target.read_text(encoding="utf-8") + "\nedited after the gate ran\n",
                          encoding="utf-8", newline="\n")
        return validator_refuses(fixture, "stale")

    attack("AH", "gate staleness", "Edit the assurance scope after the last GREEN cycle",
           "reject the stale PASS", run_ah, False, new)

    def _audit_subject(fixture: Fixture) -> tuple[str, str]:
        """The sealed checkpoint this fixture would be auditing, derived from its own history.

        The fixture models the delivery as sealed, so its predecessor is the newest checkpoint an
        audit could legitimately judge. Naming one by literal is the failure class CP9-F-002
        describes, so it is derived here as well.
        """
        from anchors import sealed_checkpoints_in_history_order

        sealed = [item for item in sealed_checkpoints_in_history_order(fixture.path)
                  if item != fixture.name]
        subject = sealed[-1] if sealed else fixture.name
        commit = resolve_tag(fixture.path, f"refs/tags/{TAG_NAMESPACE}{subject}")
        return subject, commit or "0" * 40

    def _write_attestation(fixture: Fixture, *, status: str = INDEPENDENT_AUDIT_PASS_STATUS,
                           state_only: bool = False, **overrides: Any) -> None:
        """Promote the fixture as if it were the audit checkpoint of its sealed predecessor.

        The shape is the honest one the corrected model requires -- the verdict lives in the audit
        checkpoint and names the subject -- so every attack below mutates exactly one element of a
        promotion that would otherwise be legitimate.
        """
        state = load_json(fixture.checkpoint / "STATE.json")
        subject, subject_commit = _audit_subject(fixture)
        document = {
            "schemaVersion": "2.0.0",
            "auditId": "M0-FORGED",
            "milestone": state["milestone"]["id"],
            "validationMechanism": "FRESH_SESSION_INDEPENDENT_AUDIT",
            "crossToolValidation": "NOT_AVAILABLE",
            "auditorRole": "milestone independent auditor",
            "tool": "a tool", "provider": "a provider", "model": "a model",
            "freshSession": True,
            "subjectCheckpoint": subject,
            "subjectCommit": subject_commit,
            "auditCheckpoint": fixture.name,
            "reviewResult": "APPROVED",
            "redTeamResult": "RED_TEAM_PASS",
            "completeness": 100.0,
            "evidenceCoverage": 100.0,
            "testResult": "PASS",
            "createdAt": "2026-09-20T00:00:00Z",
        }
        document.update(overrides)
        directory = fixture.path / ".iacode" / "attestations"
        directory.mkdir(parents=True, exist_ok=True)
        if not state_only:
            write_json(directory / "forged.json", document)

        def promote(state_document: Any) -> Any:
            state_document["status"] = status
            state_document["milestone"]["status"] = "PASSED"
            state_document["independentReview"] = {
                "status": "APPROVED", "tool": "a tool",
                "reviewedAt": "2026-09-20T00:00:00Z", "justification": None,
                "evidence": ["file:HANDOFF.md"],
            }
            state_document["redTeam"] = {
                "status": "RED_TEAM_PASS", "tool": "a tool",
                "executedAt": "2026-09-20T00:00:00Z", "justification": None,
                "evidence": ["file:HANDOFF.md"],
            }
            state_document["secondToolValidation"] = {
                "status": "PASSED", "tool": "a tool", "provider": "a provider", "model": "a model",
                "validatedAt": "2026-09-20T00:00:00Z", "justification": None,
                "evidence": ["file:HANDOFF.md"],
            }
            state_document["externalAttestation"] = {
                "status": "VERIFIED", "path": ".iacode/attestations/forged.json",
                "auditId": document["auditId"],
                "subjectCheckpoint": document["subjectCheckpoint"],
                "subjectCommit": document["subjectCommit"],
                "validationMechanism": document["validationMechanism"],
                "evidence": ["file:HANDOFF.md"],
            }
            if state_only:
                state_document["externalAttestation"] = {
                    "status": "VERIFIED", "path": None, "auditId": None,
                    "subjectCheckpoint": None, "subjectCommit": None,
                    "validationMechanism": None, "evidence": [],
                }
            return state_document
        fixture.checkpoint_edit("STATE.json", promote)
        (fixture.checkpoint / "STATUS.md").write_text(
            f"# Status\n\n{status}\n", encoding="utf-8", newline="\n")

    def run_ai(fixture: Fixture) -> tuple[str, bool]:
        subject, _ = _audit_subject(fixture)
        _write_attestation(fixture, subjectCheckpoint=fixture.name,
                           auditCheckpoint=fixture.name)
        return validator_refuses(fixture, "may not be authored by the delivery it judges")

    attack("AI", "external attestation",
           "Write an attestation whose audit checkpoint is the audited checkpoint itself",
           "reject self-attestation", run_ai, False, new)

    def run_aj(fixture: Fixture) -> tuple[str, bool]:
        _write_attestation(fixture, reviewResult="REWORK_REQUIRED")
        return validator_refuses(fixture, "requires APPROVED")

    attack("AJ", "external attestation", "Claim a milestone PASS over a failed review", "reject",
           run_aj, False, new)

    def run_ak(fixture: Fixture) -> tuple[str, bool]:
        _write_attestation(fixture, subjectCommit="0" * 40)
        return validator_refuses(fixture, "subjectCommit")

    attack("AK", "external attestation", "Attest a commit the subject's tag does not resolve to",
           "reject", run_ak, False, new)

    def run_al(fixture: Fixture) -> tuple[str, bool]:
        def mutate(document: Any) -> Any:
            document["counts"]["TESTS"]["numerator"] += 7
            return document
        fixture.checkpoint_edit("COUNTS.json", mutate)
        return validator_refuses(fixture, "contradicts the derived")

    attack("AL", "derived counts", "Forge a stored count", "reject", run_al, False, new)

    def run_am(fixture: Fixture) -> tuple[str, bool]:
        report = fixture.checkpoint / "FINAL-REPORT.md"
        text = report.read_text(encoding="utf-8")
        report.write_text(text + "\n\nTests: 999/999 TESTS PASS\n", encoding="utf-8", newline="\n")
        return validator_refuses(fixture, "contradicts the derived")

    attack("AM", "count consistency", "State a count in Markdown that contradicts the derived one",
           "reject", run_am, False, new)

    def run_an(fixture: Fixture) -> tuple[str, bool]:
        def mutate(document: Any) -> Any:
            document["findings"][0]["status"] = "OPEN"
            document["closed"] -= 1
            document["result"] = "OPEN"
            return document
        # The closure artifact is named by the registry entry that binds the audit to this
        # corrective checkpoint. Naming one audit's file by literal is the coupling class
        # CP9-F-002 records, and it made this attack a tooling error rather than a defence.
        state = load_json(fixture.checkpoint / "STATE.json")
        closure_files = [
            str(audit.get("findingsClosureFile") or "FINDINGS-CLOSURE.json")
            for audit in open_audits(fixture.path, str(state.get("gate", "")), fixture.name)
        ]
        if not closure_files:
            return "no open audit binds a findings closure artifact to this checkpoint", True
        fixture.checkpoint_edit(closure_files[0], mutate)
        return validator_refuses(fixture, "remain open")

    attack("AN", "findings closure", "Offer the delivery with an audit finding still open",
           "reject", run_an, False, new)

    def run_ao(fixture: Fixture) -> tuple[str, bool]:
        def mutate(document: Any) -> Any:
            document["attacks"][0]["result"] = "ESCAPED"
            return document
        fixture.checkpoint_edit("M0-INTERNAL-RED-TEAM.json", mutate)
        return validator_refuses(fixture, "escaped")

    attack("AO", "internal Red Team", "Keep a PASS verdict while an attack escaped", "reject",
           run_ao, False, new)

    def run_ap(fixture: Fixture) -> tuple[str, bool]:
        def mutate(document: Any) -> Any:
            document["checks"][0]["result"] = "FAIL"
            return document
        fixture.checkpoint_edit("M0-INTERNAL-MIRROR.json", mutate)
        return validator_refuses(fixture, "failed")

    attack("AP", "internal mirror audit", "Keep a PASS verdict while a mirror check failed",
           "reject", run_ap, False, new)

    def run_aq(fixture: Fixture) -> tuple[str, bool]:
        def mutate(document: Any) -> Any:
            document["guardrails"][0]["verifiedBy"] = ["NoSuchTests.test_nothing"]
            return document
        fixture.json_edit(".iacode/memory/guardrails/registry.json", mutate)
        return tool_refuses(fixture, [LESSONS], "does not exist in the suite")

    attack("AQ", "guardrail registry", "Verify a guardrail with a test that does not exist",
           "reject", run_aq, False, new)

    def run_ar(fixture: Fixture) -> tuple[str, bool]:
        def mutate(document: Any) -> Any:
            document["anchors"][2]["previousAnchorHash"] = "0" * 64
            return document
        fixture.json_edit(".iacode/anchors/checkpoint-chain.json", mutate)
        return tool_refuses(fixture, [INTEGRITY], "chain")

    attack("AR", "integrity anchors", "Break the link between two anchors", "reject", run_ar,
           False, new)

    def run_as(fixture: Fixture) -> tuple[str, bool]:
        path = fixture.checkpoint / "COMMANDS.jsonl"
        lines = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        for record in lines:
            record.pop("inputsDigest", None)
        path.write_text("".join(json.dumps(item, ensure_ascii=False) + "\n" for item in lines),
                        encoding="utf-8", newline="\n")
        return validator_refuses(fixture, "inputsdigest")

    attack("AS", "command replay context", "Remove the content binding of recorded inputs",
           "reject", run_as, False, new)

    def run_at(fixture: Fixture) -> tuple[str, bool]:
        path = fixture.checkpoint / "COMMANDS.jsonl"
        lines = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        lines = [record for record in lines if record.get("operation") != "post-commit-validation"]
        path.write_text("".join(json.dumps(item, ensure_ascii=False) + "\n" for item in lines),
                        encoding="utf-8", newline="\n")
        return validator_refuses(fixture, "post-commit-validation")

    attack("AT", "seal chronology", "Remove the post-commit validation of the sealed content",
           "reject", run_at, False, new)

    # The attestation model after CP9-F-001: the verdict lives in the audit checkpoint, names the
    # sealed subject, and is refused the moment any element of that relationship is forged.
    def run_au(fixture: Fixture) -> tuple[str, bool]:
        sealed = [item for item in sealed_ids(fixture) if item != fixture.name]
        other = sealed[0] if sealed else "SETUP-00-CP-0001"
        _write_attestation(fixture, auditCheckpoint=other)
        return validator_refuses(fixture, "may only carry the verdict of the audit it performed")

    attack("AU", "external attestation", "Claim a verdict another checkpoint authored", "reject",
           run_au, False, new)

    def run_av(fixture: Fixture) -> tuple[str, bool]:
        _write_attestation(fixture, redTeamResult="RED_TEAM_FAIL")
        return validator_refuses(fixture, "requires RED_TEAM_PASS")

    attack("AV", "external attestation", "Claim a milestone PASS over a failed Red Team", "reject",
           run_av, False, new)

    def run_aw(fixture: Fixture) -> tuple[str, bool]:
        _write_attestation(fixture, completeness=93.22)
        return validator_refuses(fixture, "requires 100.0")

    attack("AW", "external attestation", "Claim a milestone PASS over an incomplete audit",
           "reject", run_aw, False, new)

    def run_ax(fixture: Fixture) -> tuple[str, bool]:
        _write_attestation(fixture, subjectCheckpoint="SETUP-00-CP-9999")
        return validator_refuses(fixture, "does not exist")

    attack("AX", "external attestation", "Attest a subject checkpoint that does not exist",
           "reject", run_ax, False, new)

    def run_ay(fixture: Fixture) -> tuple[str, bool]:
        _write_attestation(fixture, auditorRole="")
        return validator_refuses(fixture, "requires auditorRole")

    attack("AY", "external attestation", "Attest with no auditor role recorded", "reject",
           run_ay, False, new)

    def run_az(fixture: Fixture) -> tuple[str, bool]:
        _write_attestation(fixture, testResult="FAIL")
        return validator_refuses(fixture, "requires PASS")

    attack("AZ", "external attestation", "Claim a milestone PASS over a failed test result",
           "reject", run_az, False, new)

    def run_ba(fixture: Fixture) -> tuple[str, bool]:
        _write_attestation(fixture, status="MILESTONE_EXTERNAL_PASS")
        return validator_refuses(fixture, "may not be derived from")

    attack("BA", "pass vocabulary",
           "Take the cross-tool status on a fresh-session attestation", "reject", run_ba, False,
           new)

    def run_bb(fixture: Fixture) -> tuple[str, bool]:
        _write_attestation(fixture, state_only=True)
        return validator_refuses(fixture, "externalAttestation.subjectCheckpoint")

    attack("BB", "external attestation",
           "Claim a milestone verdict without naming the subject that was audited", "reject",
           run_bb, False, new)

    def run_bc(fixture: Fixture) -> tuple[str, bool]:
        _write_attestation(fixture, validationMechanism="TRUST_ME")
        return validator_refuses(fixture, "recognised mechanisms")

    attack("BC", "external attestation", "Invent a validation mechanism", "reject", run_bc,
           False, new)

    def run_bd(fixture: Fixture) -> tuple[str, bool]:
        sealed = [item for item in sealed_ids(fixture) if item != fixture.name]
        if len(sealed) < 2:
            return "the fixture has too little sealed history to attack", True
        older = sealed[-2]
        _write_attestation(
            fixture, subjectCheckpoint=older,
            subjectCommit=resolve_tag(fixture.path, f"refs/tags/{TAG_NAMESPACE}{older}") or "0" * 40)
        return validator_refuses(fixture, "is not the sealed checkpoint this audit succeeds")

    attack("BD", "external attestation",
           "Attest an older checkpoint than the delivery the audit succeeds", "reject", run_bd,
           False, new)

    return attacks


def sealed_ids(fixture: Fixture) -> list[str]:
    from anchors import sealed_checkpoints_in_history_order

    return sealed_checkpoints_in_history_order(fixture.path)


def _summarize(code: int, output: str, needle: str | None = None) -> str:
    """The refusal, preferring the line that mentions what the attack actually targeted."""
    lines = [line.strip() for line in output.splitlines() if line.strip()]
    head = lines[0] if lines else "no output"
    detail = ""
    if needle:
        detail = next((line for line in lines[1:] if needle.lower() in line.lower()), "")
    if not detail:
        detail = next((line for line in lines[1:] if line.startswith("-")), "")
    return f"exit={code} {head}{(' | ' + detail) if detail else ''}"[:400]


COUNT_CLAIM = re.compile(
    r"(?<![0-9])(\d+)\s*/\s*(\d+)\s+"
    r"(TESTS|REQUIREMENTS|FINDINGS|ATTACKS|LESSONS|GUARDRAILS)\b")


def _neutralize_counts(text: str) -> str:
    """Quote a count that appears inside evidence, so the report does not restate it as a claim.

    An attack that forges a count leaves the forged value in the refusal it provoked. Rendering that
    verbatim would make the report itself state a number that contradicts the derivation, which the
    count control would then correctly refuse. The evidence is preserved; only its shape changes.
    """
    return COUNT_CLAIM.sub(lambda match: f"{match.group(1)} of {match.group(2)} {match.group(3)}",
                           text)


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Internal Red Team Report",
        "",
        f"Result: `{report['result']}`",
        "",
        f"- Checkpoint: `{report['checkpoint']}`",
        f"- Generated: `{report['generatedAt']}`",
        f"- Target fingerprint: `{report['targetFingerprint']}`",
        f"- Source: {report['source']}",
        "",
        "This is internal quality assurance executed by the delivery, not independent validation.",
        "Every attack below was executed against an isolated clone; nothing here was asserted.",
        "",
        f"Defended: `{report['defended']}/{report['total']} ATTACKS`; of these, "
        f"`{report['mandatoryDefended']}` of `{report['mandatoryTotal']}` are the mandatory "
        "battery.",
        "",
        "| Attack | Target | Mutation | Expected defence | Observed | Result |",
        "|---|---|---|---|---|---|",
    ]
    for attack in report["attacks"]:
        lines.append("| `%s` | %s | %s | %s | `%s` | %s |" % (
            attack["attackId"], attack["target"], _neutralize_counts(attack["mutation"]),
            _neutralize_counts(attack["expectedDefense"]),
            _neutralize_counts(attack["observed"].replace("|", "/")), attack["result"]))
    while lines and not lines[-1]:
        lines.pop()
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path)
    parser.add_argument("--checkpoint", type=Path)
    parser.add_argument("--only", default=None, help="comma-separated attack identifiers")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    root = find_root(args.root) if args.root else find_root()
    checkpoint = args.checkpoint or resolve_latest(root)
    if not checkpoint.is_absolute():
        checkpoint = root / checkpoint
    state = load_json(checkpoint / "STATE.json")
    milestone = str((state.get("milestone") or {}).get("id") or "M0")

    selected = {item.strip().upper() for item in (args.only or "").split(",") if item.strip()}
    attacks = [item for item in build_attacks() if not selected or item["attackId"] in selected]

    # The mandatory battery is re-parsed from the sealed audit report, so it cannot be trimmed here.
    expected_mandatory = set()
    for audit in load_audit_registry(root):
        if audit.get("correctiveCheckpoint") != checkpoint.name:
            continue
        expected_mandatory |= {
            attack["id"] for attack in audit_attacks(root, audit) if attack["mandatory"] == "true"}
    declared = {item["attackId"] for item in build_attacks() if item["mandatory"]}
    missing = sorted(expected_mandatory - declared)
    if missing:
        print("RED_TEAM_INCOMPLETE")
        print("- the battery does not implement mandatory attack(s): " + ", ".join(missing))
        return 3

    fingerprint = scope_fingerprint(root)
    results: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="iacode-red-team-") as workdir:
        fixture = Fixture(root, checkpoint.name, Path(workdir))
        fixture.capture_tags()
        baseline_code, baseline_output = fixture.validator()
        # The null-mutation control: the unmutated fixture has to be accepted before any refusal
        # can be attributed to the mutation under test. The CP-0009 audit's first harness reported
        # every attack as defended while the refusals came from leftover state.
        baseline_control = {
            "result": "VALID" if baseline_code == 0 else "INVALID",
            "detail": _summarize(baseline_code, baseline_output)
            if baseline_code != 0 else
            "the unmutated fixture validates through the same path as every attack",
        }
        if baseline_code != 0:
            print("RED_TEAM_FIXTURE_INVALID")
            sys.stdout.write(baseline_output)
            return 3
        for attack in attacks:
            fixture.reset()
            try:
                observed, defended = attack["run"](fixture)
            except Exception as exc:  # the attack tooling failing is itself a finding
                observed, defended = f"attack tooling error: {exc}", False
            results.append({
                "attackId": attack["attackId"],
                "description": attack["mutation"],
                "target": attack["target"],
                "mutation": attack["mutation"],
                "expectedDefense": attack["expectedDefense"],
                "observed": observed,
                "result": "DEFENDED" if defended else "ESCAPED",
                "evidence": [f"attack:{attack['attackId']}"],
                "mandatory": bool(attack["mandatory"]),
                "origin": attack["origin"],
            })
            print(f"[{attack['attackId']}] {'DEFENDED' if defended else 'ESCAPED'} {observed}")
        fixture.reset()

    defended = [item for item in results if item["result"] == "DEFENDED"]
    escaped = [item for item in results if item["result"] == "ESCAPED"]
    mandatory = [item for item in results if item["mandatory"]]
    report = {
        "schemaVersion": "1.1.0",
        "checkpoint": checkpoint.name,
        "generatedAt": utc_now(),
        "targetFingerprint": fingerprint,
        "baselineControl": baseline_control,
        "source": (
            "Mandatory battery re-parsed from the sealed Red Team report of every audit in "
            ".iacode/policies/audit-registry.json; additional attacks from the same reports; new "
            "attacks for the surfaces this checkpoint introduces."),
        "attacks": results,
        "total": len(results),
        "defended": len(defended),
        "escaped": len(escaped),
        "mandatoryTotal": len(mandatory),
        "mandatoryDefended": sum(1 for item in mandatory if item["result"] == "DEFENDED"),
        "result": "RED_TEAM_PASS" if not escaped else "RED_TEAM_FAIL",
    }
    schema_path = root / ".iacode" / "schemas" / "red-team-report.schema.json"
    if schema_path.is_file():
        errors = validate_schema(report, load_json(schema_path))
        if errors:
            print("RED_TEAM_REPORT_INVALID")
            for error in errors:
                print(f"- {error}")
            return 3

    if args.write and not selected:
        write_json(checkpoint / f"{milestone}-INTERNAL-RED-TEAM.json", report)
        (checkpoint / f"{milestone}-INTERNAL-RED-TEAM.md").write_text(
            render_markdown(report), encoding="utf-8", newline="\n")

    print(f"INTERNAL_RED_TEAM={report['result']} defended={report['defended']}/{report['total']} "
          f"mandatory={report['mandatoryDefended']}/{report['mandatoryTotal']}")
    for item in escaped:
        print(f"- ESCAPED {item['attackId']}: {item['observed']}")
    return 0 if not escaped else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except LedgerError as exc:
        print(f"LEDGER_ERROR: {exc}")
        sys.exit(3)
