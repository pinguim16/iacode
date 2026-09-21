#!/usr/bin/env python3
"""Section 19: history and tag integrity, exercised in a disposable clone only.

The real repository and its tags are never written to. Every mutation happens in a
clone under the session scratchpad, and the read-only inspection of the real history
is reported separately.
"""
from __future__ import annotations

import hashlib
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
FIELDS = ("checkpointId", "tag", "commit", "treeHash", "previousCheckpoint",
          "previousAnchorHash")
RESULTS: list[dict] = []


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
    target = workdir / "history-clone"
    rmtree(target)
    subprocess.run(["git", "clone", "--quiet", "--no-hardlinks", str(ROOT), str(target)],
                   check=True, capture_output=True)
    subprocess.run(["git", "checkout", "--quiet", "-B", "main",
                    "iacode-checkpoints/SETUP-00-CP-0008"], cwd=target, check=True,
                   capture_output=True)
    return target


def anchor_hash(anchor: dict) -> str:
    payload = {field: anchor.get(field) for field in FIELDS}
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def integrity(root: Path):
    proc = subprocess.run([sys.executable, "scripts/development-ledger/verify_integrity.py",
                           "--exclude", "SETUP-00-CP-0008"],
                          cwd=root, capture_output=True, text=True)
    return proc.returncode, (proc.stdout + proc.stderr).strip()


def edit_anchors(root: Path, mutate) -> None:
    path = root / ".iacode" / "anchors" / "checkpoint-chain.json"
    document = json.loads(path.read_text(encoding="utf-8"))
    mutate(document)
    path.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8", newline="\n")


def record(scenario_id, description, code, output, marker) -> None:
    lines = [line.strip() for line in output.splitlines() if line.strip().startswith("-")]
    matched = [line for line in lines if marker.lower() in line.lower()] if marker else lines
    RESULTS.append({"id": scenario_id, "description": description, "expected": "reject",
                    "exit": code, "observed": lines[:4] or [output[:200]],
                    "result": "DEFENDED" if code != 0 and matched else "ESCAPED"})
    print("[" + scenario_id + "] " + RESULTS[-1]["result"] + " :: " + description)
    for line in RESULTS[-1]["observed"]:
        print("      " + line[:200])


def main() -> int:
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)

    base = clone(out)
    code, output = integrity(base)
    RESULTS.append({"id": "HIST-000", "description": "unmutated clone (control)", "exit": code,
                    "observed": [output.strip()], "expected": "accept",
                    "result": "ACCEPTED" if code == 0 else "REFUSED"})
    print("[HIST-000] " + RESULTS[-1]["result"] + " :: " + output.strip())

    root = clone(out)
    subprocess.run(["git", "tag", "-f", "iacode-checkpoints/SETUP-00-CP-0003",
                    "refs/tags/iacode-checkpoints/SETUP-00-CP-0004"], cwd=root,
                   check=True, capture_output=True)
    record("HIST-001", "a historical tag moved to another commit", *integrity(root),
           "SETUP-00-CP-0003")

    root = clone(out)
    edit_anchors(root, lambda d: d["anchors"][2].update(
        {"tag": "refs/tags/iacode-checkpoints/SETUP-00-CP-0099"}))
    record("HIST-002", "an anchor naming the wrong tag", *integrity(root), "")

    root = clone(out)
    edit_anchors(root, lambda d: d["anchors"][2].update({"commit": "0" * 40}))
    record("HIST-003", "an anchor naming the wrong commit", *integrity(root), "")

    root = clone(out)

    def wrong_tree(document):
        document["anchors"][2]["treeHash"] = "0" * 40
        document["anchors"][2]["anchorHash"] = anchor_hash(document["anchors"][2])
        previous = document["anchors"][2]["anchorHash"]
        for anchor in document["anchors"][3:]:
            anchor["previousAnchorHash"] = previous
            anchor["anchorHash"] = anchor_hash(anchor)
            previous = anchor["anchorHash"]

    edit_anchors(root, wrong_tree)
    record("HIST-004", "an anchor naming the wrong tree, with the chain recomputed around it",
           *integrity(root), "tree")

    root = clone(out)
    edit_anchors(root, lambda d: d["anchors"][3].update({"previousAnchorHash": "0" * 64}))
    record("HIST-005", "a wrong previous-anchor digest", *integrity(root), "")

    root = clone(out)
    edit_anchors(root, lambda d: d.update({"anchors": d["anchors"][:-1]}))
    record("HIST-006", "a link removed from the chain", *integrity(root), "no integrity anchor")

    root = clone(out)

    def wrong_previous(document):
        document["anchors"][3]["previousCheckpoint"] = "SETUP-00-CP-0001"
        document["anchors"][3]["anchorHash"] = anchor_hash(document["anchors"][3])
        previous = document["anchors"][3]["anchorHash"]
        for anchor in document["anchors"][4:]:
            anchor["previousAnchorHash"] = previous
            anchor["anchorHash"] = anchor_hash(anchor)
            previous = anchor["anchorHash"]

    edit_anchors(root, wrong_previous)
    record("HIST-007", "an anchor naming the wrong predecessor", *integrity(root), "")

    # -- read-only inspection of the real history --------------------------------
    real = []
    chain = json.loads((ROOT / ".iacode" / "anchors" / "checkpoint-chain.json").read_text(
        encoding="utf-8"))
    previous_hash = None
    previous_id = None
    for anchor in chain["anchors"]:
        commit = subprocess.run(["git", "rev-parse", anchor["tag"] + "^{commit}"],
                                cwd=ROOT, capture_output=True, text=True).stdout.strip()
        tree = subprocess.run(["git", "rev-parse", anchor["tag"] + "^{tree}"],
                              cwd=ROOT, capture_output=True, text=True).stdout.strip()
        real.append({
            "checkpointId": anchor["checkpointId"],
            "commitMatches": commit == anchor["commit"],
            "treeMatches": tree == anchor["treeHash"],
            "linkMatches": (anchor["previousAnchorHash"] == previous_hash
                            and anchor["previousCheckpoint"] == previous_id),
            "digestMatches": anchor_hash(anchor) == anchor["anchorHash"],
        })
        previous_hash = anchor["anchorHash"]
        previous_id = anchor["checkpointId"]
    intact = all(all(v for k, v in item.items() if k != "checkpointId") for item in real)
    RESULTS.append({"id": "HIST-008",
                    "description": "CP-0001 to CP-0007 intact under read-only inspection",
                    "expected": "intact", "observed": real,
                    "result": "DEFENDED" if intact else "ESCAPED"})
    print("[HIST-008] " + RESULTS[-1]["result"] + " :: "
          + str(len(real)) + " sealed checkpoints, all anchors consistent = " + str(intact))

    (out / "history-results.json").write_text(json.dumps(RESULTS, indent=2) + "\n",
                                              encoding="utf-8", newline="\n")
    bad = [item for item in RESULTS if item["result"] in ("ESCAPED", "REFUSED")]
    print("TOTAL=" + str(len(RESULTS)) + " PROBLEMS=" + str(len(bad)))
    rmtree(out / "history-clone")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
