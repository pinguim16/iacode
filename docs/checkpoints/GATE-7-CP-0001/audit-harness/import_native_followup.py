"""Import only newly completed native diagnostic originals; preserve the first archive unchanged."""

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
    destination = CHECKPOINT / "NATIVE-REWORK-CONTEXT-02.json"
    if destination.exists() or load_json(CHECKPOINT / "STATE.json")["status"] != "IN_PROGRESS":
        raise ValueError("only one unsealed follow-up import is allowed")
    if OWNER.is_symlink() or OWNER.is_junction():
        raise ValueError("redirected context owner refused")
    prior = load_json(CHECKPOINT / "NATIVE-REWORK-CONTEXT.json")
    known = {row["originalName"] for row in prior["files"]}
    for row in prior["files"]:
        archived = (CHECKPOINT / row["archive"]).read_bytes()
        if (
            len(archived) != row["bytes"]
            or hashlib.sha256(archived).hexdigest() != row["sha256"]
            or (OWNER / row["originalName"]).read_bytes() != archived
        ):
            raise ValueError("previous originals must remain byte-identical")
    sources = [
        path
        for path in sorted(OWNER.iterdir())
        if path.suffix in {".py", ".json"} and path.name not in known
    ]
    sources.append(ROOT / "var/native-current-local-01.json")
    entries = []
    for ordinal, source in enumerate(sources, 1):
        if source.is_symlink() or source.is_junction() or not source.is_file():
            raise ValueError("an expected regular follow-up original is absent")
        raw = source.read_bytes()
        if not raw or find_secrets(raw.decode("utf-8", errors="strict")):
            raise ValueError("unsafe or empty original refused before export")
        target = CHECKPOINT / "attempts" / f"NATIVE-FOLLOWUP-{ordinal:04d}.raw"
        with target.open("xb") as stream:
            stream.write(raw)
        if target.read_bytes() != raw:
            raise ValueError("original byte equality failed")
        entries.append(
            {
                "originalName": source.name,
                "archive": target.relative_to(CHECKPOINT).as_posix(),
                "bytes": len(raw),
                "sha256": hashlib.sha256(raw).hexdigest(),
            }
        )
    write_json(
        destination,
        {
            "kind": "RAW_NATIVE_FOLLOWUP_NOT_CANONICAL_EXECUTION_OR_ACCEPTANCE",
            "observedAt": utc_now(),
            "originalCount": len(entries),
            "files": entries,
            "contexts": [
                "Cmd0195 is the actual canonical native failure with bounded phase/count facts.",
                "Experiment04 changes only natural allocation to5 inside10, "
                "but all snapshots empty.",
                "Experiment04 inherited summary budget1 is stale; "
                "exact prototype shows5. Inconclusive.",
                "Observer05 passes only empty snapshots: no causal physical-boundary conclusion.",
                "CLI-wait06 fails with two pinned unsignaled members "
                "after job and original handles close.",
                "CLI-wait06 real ctypes and Python Win32 bindings agree: "
                "no binding mismatch observed.",
                "Crash optout07 observes one real member signal in868ms without force; "
                "not historical cause.",
                "No external context command is adopted into the canonical ledger "
                "or grants acceptance.",
            ],
            "trainingAllowed": False,
            "ragAllowed": False,
            "distillationAllowed": False,
            "gateVerdictIssued": False,
            "independentValidation": False,
            "canonicalCommandIdsAdopted": False,
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
