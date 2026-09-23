#!/usr/bin/env python3
"""M1-F-003 acceptance: the preserved commits reach a clone of the remote, and only through their refs.

Every clone here comes from the authorised remote over its transport, never from this working
tree, so this machine's object store -- which still holds the commits as local objects -- cannot
make anything pass.

Two clones are made:

1. **The causal pair.** A clone with ``--no-tags`` fetches the branch, then every checkpoint tag
   and nothing else. The preserved commits must be *absent* there: no branch and no checkpoint tag
   reaches them. The same clone then fetches ``refs/tags/iacode-preserved/*`` and nothing else, and
   the commits must now be *present*. The only difference between the two observations is the
   published preserved reference, which is the claim: the object exists in a clone of the remote
   only because a published reference reaches it.
2. **The ordinary clone.** A plain ``git clone`` of the remote, which is what a reviewer runs. The
   commits must be present, each reached by its preserved tag, and every commit any checkpoint's
   sealed evidence names must be reachable from a published reference
   (``sealed_evidence_commits.py --root`` over that clone).

    python remote_published_objects.py --report ../REMOTE-PUBLISHED-OBJECTS.json
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
REMOTE = "https://github.com/pinguim16/iacode.git"
sys.path.insert(0, str(ROOT / "scripts" / "development-ledger"))

from ledger_common import utc_now  # noqa: E402

PRESERVED = {
    "b59d66f9f3f9add2ae9dcd1cd4609fb4a1bf0b55": "iacode-preserved/gate1-ledger-b59d66f9f3f9",
    "13ab172fcc06c466e62af41286cc09734cd7b5d4": "iacode-preserved/setup00-ledger-13ab172fcc06",
    "643e721ee519eaa88e0e92a274e8903fb8ba774a": "iacode-preserved/gate2-ledger-643e721ee519",
}


def git(cwd: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *arguments], cwd=cwd, text=True, encoding="utf-8",
                          errors="replace", capture_output=True, check=False, timeout=900)


def presence(clone: Path) -> dict[str, dict[str, object]]:
    observed = {}
    for commit, tag in PRESERVED.items():
        kind = git(clone, "cat-file", "-t", commit)
        reaching = git(clone, "for-each-ref", "--contains", commit, "--format=%(refname)",
                       "refs/heads", "refs/tags", "refs/remotes").stdout.split() \
            if kind.returncode == 0 else []
        observed[commit] = {"tag": tag, "objectType": kind.stdout.strip() or None,
                            "present": kind.returncode == 0 and kind.stdout.strip() == "commit",
                            "reachedBy": reaching}
    return observed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path, required=True)
    arguments = parser.parse_args()
    checks: list[dict[str, object]] = []
    scratch = Path(tempfile.mkdtemp(prefix="iacode-m1f003-"))
    try:
        causal = scratch / "causal"
        cloned = git(scratch, "clone", "--quiet", "--no-tags", REMOTE, str(causal))
        checks.append({"check": "clone the remote with no tags", "ok": cloned.returncode == 0,
                       "detail": cloned.stderr.strip()[-200:]})
        fetched = git(causal, "fetch", "--quiet", "origin",
                      "+refs/tags/iacode-checkpoints/*:refs/tags/iacode-checkpoints/*")
        checkpoint_tags = git(causal, "tag", "--list", "iacode-checkpoints/*").stdout.split()
        checks.append({"check": "fetch every checkpoint tag and nothing else",
                       "ok": fetched.returncode == 0 and bool(checkpoint_tags),
                       "detail": f"{len(checkpoint_tags)} checkpoint tag(s)"})
        before = presence(causal)
        checks.append({
            "check": "without the preserved references the commits are absent",
            "ok": not any(item["present"] for item in before.values()),
            "detail": {commit[:12]: item["present"] for commit, item in before.items()}})
        fetched = git(causal, "fetch", "--quiet", "origin",
                      "+refs/tags/iacode-preserved/*:refs/tags/iacode-preserved/*")
        after = presence(causal)
        checks.append({
            "check": "fetching only the preserved references brings every commit",
            "ok": fetched.returncode == 0 and all(
                item["present"] and f"refs/tags/{item['tag']}" in item["reachedBy"]
                for item in after.values()),
            "detail": {commit[:12]: item["reachedBy"] for commit, item in after.items()}})

        plain = scratch / "plain"
        cloned = git(scratch, "clone", "--quiet", REMOTE, str(plain))
        head = git(plain, "rev-parse", "HEAD").stdout.strip()
        ordinary = presence(plain)
        checks.append({
            "check": "an ordinary clone of the remote holds every preserved commit",
            "ok": cloned.returncode == 0 and all(
                item["present"] and f"refs/tags/{item['tag']}" in item["reachedBy"]
                for item in ordinary.values()),
            "detail": {commit[:12]: item["objectType"] for commit, item in ordinary.items()}})
        sealed = subprocess.run(
            [sys.executable, str(Path(__file__).with_name("sealed_evidence_commits.py")),
             "--root", str(plain), "--report", str(scratch / "sealed.json")],
            text=True, encoding="utf-8", errors="replace", capture_output=True, check=False)
        document = json.loads((scratch / "sealed.json").read_text(encoding="utf-8")) \
            if (scratch / "sealed.json").is_file() else {}
        checks.append({
            "check": "every commit the clone's sealed evidence names is reachable there",
            "ok": sealed.returncode == 0 and document.get("unpublished") == 0,
            "detail": f"{document.get('commitsNamed')} commit(s) named, "
                      f"{document.get('unpublished')} unpublished"})
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    report = {
        "schemaVersion": "1.0.0", "artifact": "REMOTE-PUBLISHED-OBJECTS",
        "checkpoint": CHECKPOINT.name, "generatedAt": utc_now(), "remote": REMOTE,
        "clonedHead": head, "preserved": PRESERVED,
        "withoutPreservedReferences": before, "withPreservedReferencesOnly": after,
        "ordinaryClone": ordinary, "checks": checks,
        "result": "PASS" if all(item["ok"] for item in checks) else "FAIL",
    }
    arguments.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n",
                                encoding="utf-8", newline="\n")
    for item in checks:
        print(f"[{'PASS' if item['ok'] else 'FAIL'}] {item['check']}: {item['detail']}")
    print(f"REMOTE_PUBLISHED_OBJECTS={report['result']}")
    return 0 if report["result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
