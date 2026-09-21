#!/usr/bin/env python3
"""Independent fixture engine for the SETUP-00-CP-0009 fresh-session audit.

Written by the auditor. It deliberately does not import the delivery's own
``m0_red_team`` fixture, so an attack that is defended here is defended by the
product, not by the product's own test harness.

Safety: every mutation happens inside a disposable clone under the session
scratchpad. The real repository, its history and its tags are never written to.
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

TAG_NS = "iacode-checkpoints/"


def git(cwd: Path, *args: str) -> tuple[int, str]:
    proc = subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True)
    return proc.returncode, (proc.stdout + proc.stderr).strip()


class Fixture:
    """A disposable clone of the repository positioned at a sealed checkpoint tag."""

    def __init__(self, source: Path, checkpoint: str, workdir: Path) -> None:
        self.source = Path(source)
        self.name = checkpoint
        self.path = Path(workdir) / "fixture"
        self.tag = TAG_NS + checkpoint
        if self.path.exists():
            def _force(func, target, _info):
                try:
                    os.chmod(target, 0o700)
                    func(target)
                except Exception:
                    pass
            shutil.rmtree(self.path, onerror=_force)
            if self.path.exists():
                time.sleep(0.5)
                shutil.rmtree(self.path, onerror=_force)
        code, out = git(Path("."), "clone", "--quiet", "--no-hardlinks",
                        str(self.source), str(self.path))
        if code != 0:
            raise RuntimeError("fixture clone failed: " + out)
        code, out = git(self.path, "checkout", "-B", "main", self.tag)
        if code != 0:
            raise RuntimeError("fixture checkout failed: " + out)
        code, self.base = git(self.path, "rev-parse", "HEAD")
        git(self.path, "config", "user.name", "cp0009-audit")
        git(self.path, "config", "user.email", "cp0009-audit@iacode.local")
        self.checkpoint = self.path / "docs" / "checkpoints" / self.name
        # Every namespaced tag is captured so that reset() restores the whole sealed history,
        # not only this checkpoint's tag. Without it an attack that moves a predecessor tag
        # would poison every later attack and no rejection would be attributable.
        code, listing = git(self.path, "for-each-ref", "--format=%(refname)|%(objectname)",
                            "refs/tags/")
        self.tags = {}
        for line in listing.splitlines():
            if "|" in line:
                ref, object_id = line.split("|", 1)
                self.tags[ref.strip()] = object_id.strip()

    # -- lifecycle ---------------------------------------------------------------
    def reset(self) -> None:
        git(self.path, "checkout", "-q", "-B", "main", self.base)
        git(self.path, "reset", "--hard", "-q", self.base)
        git(self.path, "clean", "-qfdx")
        code, listing = git(self.path, "for-each-ref", "--format=%(refname)", "refs/tags/")
        for ref in listing.splitlines():
            ref = ref.strip()
            if ref and ref not in self.tags:
                git(self.path, "tag", "-d", ref.split("refs/tags/", 1)[-1])
        for ref, object_id in self.tags.items():
            git(self.path, "tag", "-f", ref.split("refs/tags/", 1)[-1], object_id)

    def commit(self, message: str, retag: bool = True) -> str:
        git(self.path, "add", "-A")
        git(self.path, "commit", "--quiet", "--allow-empty", "-m", message)
        code, head = git(self.path, "rev-parse", "HEAD")
        if retag:
            git(self.path, "tag", "-f", self.tag, head)
        return head

    # -- reading and writing checkpoint artifacts --------------------------------
    def read_json(self, relative: str):
        return json.loads((self.checkpoint / relative).read_text(encoding="utf-8"))

    def write_json(self, relative: str, document) -> None:
        (self.checkpoint / relative).write_text(
            json.dumps(document, indent=2) + "\n", encoding="utf-8", newline="\n")

    def read_repo_json(self, relative: str):
        return json.loads((self.path / relative).read_text(encoding="utf-8"))

    def write_repo_json(self, relative: str, document) -> None:
        (self.path / relative).write_text(
            json.dumps(document, indent=2) + "\n", encoding="utf-8", newline="\n")

    def refresh_inventory(self) -> None:
        """Recompute FILES.json hashes exactly as the delivery's finalizer would.

        An attacker with repository control would of course do this, so every
        inventory-independent control has to hold with the inventory refreshed.
        """
        sys.path.insert(0, str(self.path / "scripts" / "development-ledger"))
        for module in [m for m in list(sys.modules) if m in (
                "finalize_checkpoint", "ledger_common", "policies", "lessons",
                "anchors", "attestation", "delivery_assurance")]:
            del sys.modules[module]
        try:
            from finalize_checkpoint import _refresh_inventory_hashes  # type: ignore
            from ledger_common import load_json, write_json  # type: ignore
            state = load_json(self.checkpoint / "STATE.json")
            write_json(self.checkpoint / "FILES.json", _refresh_inventory_hashes(
                self.path, self.checkpoint, state, load_json(self.checkpoint / "FILES.json")))
        finally:
            sys.path.pop(0)

    def amend(self, message: str = "") -> str:
        """Fold a mutation into the seal-evidence commit, keeping HEAD^ intact."""
        git(self.path, "add", "-A")
        git(self.path, "commit", "--quiet", "--amend", "--no-edit")
        code, head = git(self.path, "rev-parse", "HEAD")
        git(self.path, "tag", "-f", self.tag, head)
        return head

    def declare_created(self, relative: str, reason: str) -> None:
        """Declare a new repository path in the checkpoint inventory, as an author would."""
        files = self.read_json("FILES.json")
        files.setdefault("filesCreated", []).append({"path": relative, "reason": reason})
        self.write_json("FILES.json", files)

    def reseal(self, message: str) -> str:
        """Re-seal the mutated content the way the product's two-step seal does.

        Without this, every mutation would additionally break the seal-chronology
        control, and a rejection could not be attributed to the mutation under
        test. Modelling a faithful re-seal is also the stronger threat model: an
        actor who controls the repository would of course re-seal.
        """
        self.refresh_inventory()
        content = self.commit(message + " (content)", retag=False)
        path = self.checkpoint / "COMMANDS.jsonl"
        records = [json.loads(line) for line in
                   path.read_text(encoding="utf-8").splitlines() if line.strip()]
        for record in reversed(records):
            if record.get("operation") == "post-commit-validation":
                record["commit"] = content
                record["subjectCommit"] = content
                if isinstance(record.get("repositoryState"), dict):
                    record["repositoryState"]["head"] = content
                    record["repositoryState"]["dirty"] = False
                    record["repositoryState"]["detached"] = False
                break
        path.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in records) + "\n",
                        encoding="utf-8", newline="\n")
        self.refresh_inventory()
        return self.commit(message + " (seal evidence)", retag=True)

    # -- running the controls ----------------------------------------------------
    def script(self, name: str, *args: str) -> tuple[int, str]:
        env = dict(os.environ)
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        proc = subprocess.run(
            [sys.executable, "scripts/development-ledger/" + name, *args],
            cwd=str(self.path), capture_output=True, text=True, env=env)
        return proc.returncode, (proc.stdout + proc.stderr).strip()

    def validator(self, *args: str) -> tuple[int, str]:
        return self.script("validate_checkpoint.py", *args)


def rejected(code: int, output: str) -> bool:
    """A control refused the mutation."""
    return code != 0


def summarize(output: str, limit: int = 400) -> str:
    text = " | ".join(line.strip() for line in output.splitlines() if line.strip())
    return text[:limit]
