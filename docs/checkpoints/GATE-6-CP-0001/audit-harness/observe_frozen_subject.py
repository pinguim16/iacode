"""Observe source immutability during the full run; never issue a test or Gate verdict."""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))
from ledger_common import scope_fingerprint

progress = json.loads((CHECKPOINT / "FULL-VERIFY-PROGRESS.json").read_text(encoding="utf-8"))
clone = Path(progress["clone"]).resolve()
owner = clone.parent
if (owner.parent != Path(tempfile.gettempdir()).resolve()
        or not owner.name.startswith("iacode-gate6-full-verification-") or clone.name != "repository"
        or owner.is_symlink() or owner.is_junction()):
    raise ValueError("unexpected verification clone identity")


def git(root: Path, *arguments: str) -> str:
    return subprocess.check_output(["git", *arguments], cwd=root).decode("utf-8").strip()


subject = progress["subjectCommit"]
if git(ROOT, "rev-parse", "HEAD") != subject or git(clone, "rev-parse", "HEAD") != subject:
    raise ValueError("the observed frozen subject identity changed")
changed = set(git(ROOT, "diff", "--name-only", "HEAD").splitlines())
changed.update(git(ROOT, "ls-files", "--others", "--exclude-standard").splitlines())
prefix = CHECKPOINT.relative_to(ROOT).as_posix() + "/"
if any(not name.startswith(prefix) for name in changed):
    raise ValueError("a change escaped excluded checkpoint bookkeeping")
fingerprint = scope_fingerprint(ROOT)
if fingerprint != scope_fingerprint(clone):
    raise ValueError("the live source differs from the measured immutable clone")
print(json.dumps({"kind": "SOURCE_FREEZE_OBSERVATION_NOT_ACCEPTANCE", "subjectCommit": subject,
                  "sourceFingerprint": fingerprint, "excludedCheckpointChanges": len(changed),
                  "stageTransitions": progress["transitions"], "testVerdictIssued": False}))
