"""Preserve actual minimal-protocol mirrors before interpretation and owned cleanup."""

from __future__ import annotations

import hashlib
import json
import re
import sys
import tempfile
import uuid
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))


def capture_protocol_mirrors(workdir: Path, checkpoint: Path, prefix: str) -> list[dict]:
    from ledger_common import find_secrets, write_json
    from promotion_fixture import promotion_repository

    if not re.fullmatch(r"[A-Za-z0-9-]{1,96}", prefix):
        raise ValueError("bounded archive identity required")
    producer_root = promotion_repository(workdir)
    archive = checkpoint / "attempts"
    if archive.is_symlink() or archive.is_junction():
        raise ValueError("redirected original archive refused")
    archive.mkdir(exist_ok=True)
    rows = []
    for path in sorted((producer_root / "docs/checkpoints").glob("*/*-INTERNAL-MIRROR.json")):
        if path.is_symlink() or not path.resolve().is_relative_to(producer_root.resolve()):
            raise ValueError("redirected original producer refused")
        raw = path.read_bytes()
        if find_secrets(raw.decode("utf-8", errors="strict")):
            raise ValueError("unsafe original producer refused")
        target = archive / (prefix + "-" + path.parent.name + "-" + path.name)
        with target.open("xb") as output:
            output.write(raw)
        if target.read_bytes() != raw:
            raise ValueError("original byte equality failed")
        row = {
            "kind": "UNINTERPRETED_REAL_FIXTURE_PRODUCER_NOT_M2_ACCEPTANCE",
            "source": path.relative_to(producer_root).as_posix(),
            "archive": target.relative_to(checkpoint).as_posix(),
            "sizeBytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest(),
            "acceptanceGranted": False,
        }
        write_json(target.with_name(target.stem + "-RECEIPT.json"), row)
        rows.append(row)
    return rows


def main() -> int:
    from ledger_common import load_json, scope_fingerprint, use_utf8_stdout, write_json
    from promotion_fixture import FixtureError, run_positive_promotion

    use_utf8_stdout()
    if load_json(CHECKPOINT / "STATE.json")["status"] != "IN_PROGRESS":
        raise ValueError("diagnostic writer is unsealed only")
    before = scope_fingerprint(ROOT)
    rows, failure = [], None
    prefix = "PROMOTION-DIAGNOSTIC-" + uuid.uuid4().hex
    with tempfile.TemporaryDirectory(prefix="iacode-g7-promotion-diagnostic-") as raw:
        directory = Path(raw)
        if (
            directory.resolve().parent != Path(tempfile.gettempdir()).resolve()
            or directory.is_symlink()
            or directory.is_junction()
        ):
            raise ValueError("unexpected temporary owner")
        workdir = directory / "repository"
        try:
            run_positive_promotion(workdir)
        except FixtureError as error:
            failure = type(error).__name__
        finally:
            rows = capture_protocol_mirrors(workdir, CHECKPOINT, prefix)
    observations = []
    for row in rows:
        report = load_json(CHECKPOINT / row["archive"])
        observations.extend(
            {key: check.get(key) for key in ("id", "dimension", "result", "observed")}
            for check in report["checks"]
            if check["result"] == "FAIL"
        )
    receipt = {
        "kind": "ACTUAL_MINIMAL_PROTOCOL_CAUSAL_DIAGNOSTIC_NOT_GATE_ACCEPTANCE",
        "failureType": failure,
        "originals": rows,
        "failedDimensions": observations,
        "temporaryOwnerRemoved": not directory.exists(),
        "sourceUnchanged": scope_fingerprint(ROOT) == before,
        "acceptanceGranted": False,
    }
    write_json(CHECKPOINT / "attempts" / (prefix + "-SUMMARY.json"), receipt)
    print(json.dumps(receipt))
    return 1 if failure or observations or not rows else 0


if __name__ == "__main__":
    raise SystemExit(main())
