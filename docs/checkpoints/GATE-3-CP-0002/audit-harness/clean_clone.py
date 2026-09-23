#!/usr/bin/env python3
"""M1 criterion 5: a clean clone of the authorised remote validates and verifies on its own.

The clone comes from `origin`, not from this working tree, so nothing uncommitted, untracked or
ignored here can make it pass. Three things are run inside the clone, from the clone's own files:

1. `validate_checkpoint.py` — the latest sealed checkpoint of the published history;
2. `verify_integrity.py` — the published chain of anchors and tags;
3. `verify.py` — the full verification, every mandatory gate and every live stage.

The one thing a clone cannot carry is this machine's local configuration: `infra/compose/.env`
holds the database passwords and the provider credential, and Git deliberately never publishes it.
The clone is given a copy of that file — machine configuration, not workspace content — and nothing
else. The copy lives only in the disposable clone and is deleted with it.

The full verification of a clone builds its images from the clone and recreates the local stack
from them, exactly as a fresh installation would.

    python clean_clone.py --report ../CLEAN-CLONE-REPORT.json
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
REMOTE = "https://github.com/pinguim16/iacode.git"
sys.path.insert(0, str(ROOT / "scripts" / "development-ledger"))

from ledger_common import utc_now  # noqa: E402


def run(argv: list[str], cwd: Path, timeout: float) -> tuple[int, str, float]:
    started = time.monotonic()
    completed = subprocess.run(argv, cwd=cwd, text=True, encoding="utf-8", errors="replace",
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False,
                               timeout=timeout)
    return completed.returncode, completed.stdout, round(time.monotonic() - started, 1)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--skip-verify", action="store_true")
    arguments = parser.parse_args()
    steps = []
    scratch = Path(tempfile.mkdtemp(prefix="iacode-m1-clone-"))
    clone = scratch / "iacode"
    try:
        code, output, seconds = run(["git", "clone", "--quiet", REMOTE, str(clone)], scratch, 900)
        steps.append({"step": "clone the authorised remote", "exitCode": code,
                      "seconds": seconds, "tail": output.strip()[-300:]})
        if code != 0:
            raise SystemExit(output)
        head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=clone, text=True,
                              capture_output=True, check=False).stdout.strip()
        tags = subprocess.run(["git", "tag", "--list", "iacode-checkpoints/*"], cwd=clone,
                              text=True, capture_output=True, check=False).stdout.split()
        latest = (clone / "docs" / "checkpoints" / "LATEST.md").read_text(encoding="utf-8")
        for title, argv, timeout in (
                ("validate the latest checkpoint",
                 [sys.executable, "scripts/development-ledger/validate_checkpoint.py"], 900),
                ("verify the integrity chain",
                 [sys.executable, "scripts/development-ledger/verify_integrity.py"], 900),
                ("validate the engineering memory",
                 [sys.executable, "scripts/development-ledger/validate_lessons.py"], 900)):
            code, output, seconds = run(argv, clone, timeout)
            steps.append({"step": title, "exitCode": code, "seconds": seconds,
                          "tail": output.strip()[-300:]})
            print(f"[{'PASS' if code == 0 else 'FAIL'}] {title}: {output.strip()[-160:]}",
                  flush=True)
        if not arguments.skip_verify:
            shutil.copyfile(ROOT / "infra" / "compose" / ".env",
                            clone / "infra" / "compose" / ".env")
            report = clone / "var" / "verify-report.json"
            code, output, seconds = run(
                [sys.executable, "scripts/iacode/verify.py", "--report", str(report),
                 "--keep-going"], clone, 7200)
            document = json.loads(report.read_text(encoding="utf-8")) if report.is_file() else {}
            stages = [{"name": item.get("name"), "exitCode": item.get("exitCode"),
                       "durationSeconds": item.get("durationSeconds")}
                      for item in document.get("stages") or []]
            steps.append({"step": "full verification in the clone", "exitCode": code,
                          "seconds": seconds, "result": document.get("result"),
                          "stages": stages, "tail": output.strip()[-400:]})
            print(f"[{'PASS' if code == 0 else 'FAIL'}] full verification: "
                  f"{document.get('result')} {sum(1 for s in stages if s['exitCode'] == 0)}/"
                  f"{len(stages)}", flush=True)
    finally:
        env_copy = clone / "infra" / "compose" / ".env"
        if env_copy.exists():
            env_copy.unlink()
        shutil.rmtree(scratch, ignore_errors=True)
    failed = [item for item in steps if item["exitCode"] != 0]
    document = {
        "schemaVersion": "1.0.0", "artifact": "CLEAN-CLONE-REPORT", "checkpoint": CHECKPOINT.name,
        "generatedAt": utc_now(), "remote": REMOTE, "clonedHead": head,
        "checkpointTags": len(tags), "latestCheckpoint": latest.strip().splitlines()[2]
        if len(latest.strip().splitlines()) > 2 else latest.strip(),
        "localConfiguration": ("infra/compose/.env copied into the disposable clone and deleted "
                               "with it; no other file came from the working tree"),
        "steps": steps, "result": "PASS" if not failed else "FAIL",
    }
    arguments.report.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n",
                                encoding="utf-8", newline="\n")
    print(f"CLEAN_CLONE={document['result']} steps={len(steps) - len(failed)}/{len(steps)} "
          f"head={head[:12]}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
