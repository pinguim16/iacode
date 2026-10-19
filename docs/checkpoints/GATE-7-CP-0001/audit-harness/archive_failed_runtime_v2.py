"""One-time preservation/retirement of the failed immutable runtime-v2 attempt.

Invoke only after observing the full parent recorder's actual exit. No failure is promoted,
no immutable tag is moved, and no source is repaired here.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]
SUBJECT = "13749adfa616c7f52aa7407cb9a9d7aef3d19c76"
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))


def main() -> int:
    from ledger_common import use_utf8_stdout

    use_utf8_stdout()
    from ledger_common import LedgerError, find_secrets, load_json, utc_now, write_json

    state = load_json(CHECKPOINT / "STATE.json")
    if (
        CHECKPOINT.name != "GATE-7-CP-0001"
        or state["status"] != "IN_PROGRESS"
        or state["gate"] != "GATE-7"
    ):
        raise LedgerError("only the unsealed implementing checkpoint may retire an attempt")
    if (
        subprocess.run(
            ["git", "rev-parse", "--verify", "refs/tags/iacode-checkpoints/" + CHECKPOINT.name],
            cwd=ROOT,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        ).returncode
        == 0
    ):
        raise LedgerError("never rewrite a sealed checkpoint")
    verification = load_json(CHECKPOINT / "VERIFY.json")
    publication = load_json(CHECKPOINT / "PUBLISHED-CLEAN-CLONE-REPORT.json")
    if verification.get("result") != "FAIL" or publication.get("publishedCommit") != SUBJECT:
        raise LedgerError("this one-time helper owns only the actual failed runtime-v2 subject")
    root = [row for row in verification["stages"] if row["name"] == "gate:tests"]
    if len(root) != 1 or root[0]["result"] != "FAIL":
        raise LedgerError("the original complete root failure must be retained")
    records = [
        json.loads(line)
        for line in (CHECKPOINT / "COMMANDS.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    runs = [
        row
        for row in records
        if row.get("subjectCommit") == SUBJECT
        and "audit-harness/run_full_verification.py" in row.get("command", "")
    ]
    if len(runs) != 1 or runs[0].get("exitCode") == 0:
        raise LedgerError("the failed completed full invocation must be in the ledger")
    manifest_path = CHECKPOINT / "attempts/RUNTIME-V2-FAILED-FULL-MANIFEST.json"
    if manifest_path.exists():
        raise LedgerError("one-time original archival must not be replayed")
    names = (
        "VERIFY.json",
        "PUBLISHED-CLEAN-CLONE-REPORT.json",
        "FUNCTIONAL-SCENARIOS.json",
        "COMPOSE-ISOLATION-AUDIT.json",
        "PRODUCER-REPORTS.json",
        "FULL-VERIFY-PROGRESS.json",
        "RUNTIME-SUBJECT.json",
    )
    entries = []
    for name in names:
        path = CHECKPOINT / name
        if path.is_symlink() or path.is_junction() or not path.is_file():
            raise LedgerError("an expected original regular attempt artifact is absent")
        raw = path.read_bytes()
        if find_secrets(raw.decode("utf-8", errors="strict")):
            raise LedgerError("unsafe attempt artifact cannot be transported")
        target = CHECKPOINT / "attempts" / ("RUNTIME-V2-FAILED-" + name)
        with target.open("xb") as stream:
            stream.write(raw)
        if target.read_bytes() != raw:
            raise LedgerError("original failed attempt archival byte equality failed")
        entries.append(
            {
                "original": name,
                "archive": target.name,
                "sizeBytes": len(raw),
                "sha256": hashlib.sha256(raw).hexdigest(),
            }
        )
    write_json(
        manifest_path,
        {
            "kind": "EXACT_FAILED_IMMUTABLE_FULL_ATTEMPT_NOT_CURRENT_ACCEPTANCE",
            "observedAt": utc_now(),
            "subjectCommit": SUBJECT,
            "subjectTag": "iacode-subjects/GATE-7-CP-0001-runtime-v2",
            "commandId": runs[0]["id"],
            "result": "FAIL",
            "originalProducerManifest": load_json(CHECKPOINT / "PRODUCER-REPORTS.json")["manifest"],
            "files": entries,
            "acceptanceGranted": False,
            "immutableTagMoved": False,
        },
    )
    # Every original is durable before retiring only the closed current report destinations.
    for name in names[:5]:
        (CHECKPOINT / name).unlink()
    print("FAILED_RUNTIME_V2_ORIGINALS_ARCHIVED; no acceptance or independent verdict")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
