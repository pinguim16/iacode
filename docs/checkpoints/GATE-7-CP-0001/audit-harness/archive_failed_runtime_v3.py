"""Preserve the completed failed runtime-v3 exactly, without promoting its green fragments."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]
SUBJECT = "31ee804ecffb14add59f89b1b5cbd2f4de9216a8"
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))


def main() -> int:
    from ledger_common import (
        LedgerError,
        find_secrets,
        load_json,
        use_utf8_stdout,
        utc_now,
        write_json,
    )

    use_utf8_stdout()
    state = load_json(CHECKPOINT / "STATE.json")
    tag = subprocess.run(
        ["git", "rev-parse", "--verify", "refs/tags/iacode-checkpoints/" + CHECKPOINT.name],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    if state["status"] != "IN_PROGRESS" or state["gate"] != "GATE-7" or tag.returncode == 0:
        raise LedgerError("only the unsealed Gate7 implementing checkpoint may retire this attempt")
    verification = load_json(CHECKPOINT / "VERIFY.json")
    publication = load_json(CHECKPOINT / "PUBLISHED-CLEAN-CLONE-REPORT.json")
    stages = verification["stages"]
    failed = [row["name"] for row in stages if row["result"] == "FAIL"]
    if (
        verification["result"] != "FAIL"
        or publication["publishedCommit"] != SUBJECT
        or len(stages) != 49
        or failed != ["native-client-installation"]
        or sum(row["result"] == "PASS" for row in stages) != 48
    ):
        raise LedgerError("only the actual complete 48/49 failed runtime-v3 is owned here")
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
    if (
        len(runs) != 1
        or runs[0]["id"] != "cmd-0180"
        or runs[0]["result"] != "COMPLETED"
        or runs[0]["exitCode"] != 1
    ):
        raise LedgerError("the actual failed full invocation must have ended in the ledger")
    manifest = CHECKPOINT / "attempts/RUNTIME-V3-FAILED-FULL-MANIFEST.json"
    if manifest.exists():
        raise LedgerError("never replay one-time original archival")
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
        source = CHECKPOINT / name
        if source.is_symlink() or source.is_junction() or not source.is_file():
            raise LedgerError("an expected regular original is absent or redirected")
        raw = source.read_bytes()
        if find_secrets(raw.decode("utf-8", errors="strict")):
            raise LedgerError("unsafe original refused before transport")
        target = CHECKPOINT / "attempts" / ("RUNTIME-V3-FAILED-" + name)
        with target.open("xb") as stream:
            stream.write(raw)
        if target.read_bytes() != raw:
            raise LedgerError("original byte equality failed")
        entries.append(
            {
                "original": name,
                "archive": target.name,
                "sizeBytes": len(raw),
                "sha256": hashlib.sha256(raw).hexdigest(),
            }
        )
    write_json(
        manifest,
        {
            "kind": "EXACT_FAILED_IMMUTABLE_FULL_ATTEMPT_NOT_CURRENT_ACCEPTANCE",
            "observedAt": utc_now(),
            "subjectCommit": SUBJECT,
            "subjectTag": "iacode-subjects/GATE-7-CP-0001-runtime-v3",
            "commandId": runs[0]["id"],
            "result": "FAIL",
            "originalProducerManifest": load_json(CHECKPOINT / "PRODUCER-REPORTS.json")["manifest"],
            "files": entries,
            "acceptanceGranted": False,
            "immutableTagMoved": False,
        },
    )
    # Retire only the closed current destinations after all exact originals are durable.
    for name in names[:5]:
        (CHECKPOINT / name).unlink()
    print("FAILED_RUNTIME_V3_ORIGINALS_ARCHIVED; no acceptance or independent verdict")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
