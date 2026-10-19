"""Preserve owned external native observations as inert context, never canonical execution."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]
OWNER = Path(
    "C:/Users/cesar/AppData/Local/Temp/"
    "iacode-gate7-native-observation-32f15cca4802450ca926e687a9bc814a"
)
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))


def main() -> int:
    from ledger_common import find_secrets, load_json, use_utf8_stdout, utc_now, write_json

    use_utf8_stdout()
    if load_json(CHECKPOINT / "STATE.json")["status"] != "IN_PROGRESS":
        raise ValueError("only unsealed implementing context may be imported")
    destination = CHECKPOINT / "NATIVE-REWORK-CONTEXT.json"
    if destination.exists() or OWNER.is_junction() or OWNER.is_symlink():
        raise ValueError("never replay import or read a redirected owner")
    names = sorted(
        [path for path in OWNER.iterdir() if path.suffix in {".py", ".json"} and path.is_file()]
        + list((OWNER / "originals").glob("*.json"))
    )
    staged = []
    for ordinal, source in enumerate(names, 1):
        if (
            source.is_symlink()
            or source.is_junction()
            or not source.resolve().is_relative_to(OWNER.resolve())
        ):
            raise ValueError("redirected context refused")
        raw = source.read_bytes()
        if not raw or find_secrets(raw.decode("utf-8", errors="strict")):
            raise ValueError("empty or unsafe context refused before export")
        target = CHECKPOINT / "attempts" / f"NATIVE-V3-{ordinal:04d}.raw"
        if target.exists():
            raise ValueError("never overwrite an original")
        staged.append((source, target, raw))
    entries = []
    for source, target, raw in staged:
        with target.open("xb") as stream:
            stream.write(raw)
        if target.read_bytes() != raw:
            raise ValueError("raw byte equality failed")
        entries.append(
            {
                "originalName": source.relative_to(OWNER).as_posix(),
                "archive": target.relative_to(CHECKPOINT).as_posix(),
                "bytes": len(raw),
                "sha256": hashlib.sha256(raw).hexdigest(),
            }
        )
    write_json(
        destination,
        {
            "kind": "RAW_NATIVE_CONTEXT_NOT_CANONICAL_EXECUTION_OR_ACCEPTANCE",
            "observedAt": utc_now(),
            "baselineCommit": "31ee804ecffb14add59f89b1b5cbd2f4de9216a8",
            "sourceFrozenDuringObservation": True,
            "originalCount": len(entries),
            "files": entries,
            "contexts": [
                "V1 diagnostic failed its combined premise before target close; "
                "no original console bytes retained.",
                "V2 real child-ready/member premise observes2 members; "
                "unchanged simple cleanup succeeds.",
                "Actual unchanged native run reproduces job4 physical signal failure "
                "despite zero accounting.",
                "Release experiment01 passes only empty snapshots: "
                "inconclusive, never a causal fix.",
                "Release experiment02 exercises two pending members and fails: "
                "release-order hypothesis rejected.",
                "Grace experiment03 observes two real pending members "
                "signaling in52ms within original10s.",
                "Original full runtime-v3 remains FAIL48/49; "
                "context does not grant any Gate verdict.",
            ],
            "provenance": {
                "sourceType": "repository-generated",
                "provider": "local-execution",
                "model": None,
                "ownership": "owned synthetic diagnostics",
                "license": "not-applicable",
            },
            "trainingAllowed": False,
            "ragAllowed": False,
            "distillationAllowed": False,
            "canonicalCommandIdsAdopted": False,
            "independentValidation": False,
            "gateVerdictIssued": False,
        },
    )
    print(
        json.dumps(
            {"originalCount": len(entries), "allBytesEqual": True, "gateVerdictIssued": False}
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
