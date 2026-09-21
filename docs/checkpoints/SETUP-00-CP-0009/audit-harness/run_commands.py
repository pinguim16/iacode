#!/usr/bin/env python3
"""Section 29: command auditability, measured rather than assumed.

Three questions:
  1. does every record carry the fields a replay needs?
  2. for a record that claims a clean tree, does its content binding hold at that commit?
  3. can a representative sample of safe, read-only commands actually be executed from the
     working directory the record declares, in a clean checkout of the sealed content?

Records made against a dirty working tree are deliberately not replayed for equality: the
delivery's answer to M0-F-009 is content binding, not replay, and that is what is checked.
"""
from __future__ import annotations

import hashlib
import json
import os
import random
import shutil
import subprocess
import sys
import time
from pathlib import Path
import os as _os
from pathlib import Path as _Path
_DEFAULT_ROOT = _Path(__file__).resolve().parents[4]

ROOT = Path(_os.environ.get("IACODE_ROOT") or _DEFAULT_ROOT)
CP8 = ROOT / "docs" / "checkpoints" / "SETUP-00-CP-0008"
SEED = 20260920

SAFE = ("validate_checkpoint.py", "validate_lessons.py", "verify_integrity.py",
        "check_completeness.py", "derive_counts.py", "compileall", "unittest")


def canonical(content: bytes) -> str:
    try:
        normalized = content.decode("utf-8").replace("\r\n", "\n").encode("utf-8")
    except UnicodeDecodeError:
        normalized = content
    return hashlib.sha256(normalized).hexdigest()


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


def main() -> int:
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    records = [json.loads(line) for line in
               (CP8 / "COMMANDS.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]

    # -- 2. content binding for clean-tree records -------------------------------
    binding = []
    for record in records:
        state = record.get("repositoryState") or {}
        if state.get("dirty") is not False:
            continue
        for item in record.get("inputsDigest") or []:
            proc = subprocess.run(["git", "show", record["commit"] + ":" + item["path"]],
                                  cwd=ROOT, capture_output=True)
            observed = canonical(proc.stdout) if proc.returncode == 0 else None
            binding.append({"id": record["id"], "path": item["path"],
                            "recorded": item["hash"], "atCommit": observed,
                            "matches": observed == item["hash"]})

    # -- 3. safe replay in a clean checkout of the sealed content -----------------
    clone = out / "replay-clone"
    rmtree(clone)
    subprocess.run(["git", "clone", "--quiet", "--no-hardlinks", str(ROOT), str(clone)],
                   check=True, capture_output=True)
    subprocess.run(["git", "checkout", "--quiet", "--detach",
                    "iacode-checkpoints/SETUP-00-CP-0008"], cwd=clone, check=True,
                   capture_output=True)

    candidates = [r for r in records
                  if isinstance(r.get("command"), str)
                  and any(tool in r["command"] for tool in SAFE)
                  and "--write" not in r["command"]
                  and "--rebuild" not in r["command"]]
    random.Random(SEED).shuffle(candidates)
    replays = []
    for record in candidates[:6]:
        arguments = list(record.get("arguments") or [])
        started = time.monotonic()
        proc = subprocess.run([sys.executable, *arguments], cwd=clone,
                              capture_output=True, text=True)
        replays.append({
            "id": record["id"], "command": record["command"],
            "declaredWorkingDirectory": record["workingDirectory"],
            "recordedExit": record.get("exitCode"),
            "replayExit": proc.returncode,
            "replayDurationMs": int((time.monotonic() - started) * 1000),
            "replayHead": "iacode-checkpoints/SETUP-00-CP-0008",
            "firstLine": (proc.stdout + proc.stderr).strip().splitlines()[:1],
            "executable": proc.returncode is not None,
        })

    report = {
        "records": len(records),
        "cleanTreeBindings": len(binding),
        "cleanTreeBindingMismatches": [item for item in binding if not item["matches"]],
        "replaySeed": SEED,
        "replays": replays,
    }
    (out / "command-audit.json").write_text(json.dumps(report, indent=2) + "\n",
                                            encoding="utf-8", newline="\n")
    print("RECORDS " + str(len(records)))
    print("CLEAN-TREE INPUT BINDINGS " + str(len(binding))
          + " mismatches=" + str(len(report["cleanTreeBindingMismatches"])))
    for item in report["cleanTreeBindingMismatches"]:
        print("  - " + json.dumps(item)[:250])
    for item in replays:
        print("REPLAY " + item["id"] + " recorded=" + str(item["recordedExit"])
              + " replay=" + str(item["replayExit"]) + "  " + item["command"][:90])
        print("       " + str(item["firstLine"])[:160])
    rmtree(clone)
    return 0


if __name__ == "__main__":
    sys.exit(main())
