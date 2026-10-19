"""Import exact historical scratch contexts as inert short raw names, never acceptance."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tempfile
from pathlib import Path, PurePosixPath

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))

EXPECTED_INVENTORY_SHA256 = "eb289d0a73159cc7e33c299ef0cccc0c22c4de5a3411bf0b2f515b0e3df6099a"
EXPECTED_INVENTORY_BYTES = 33897
BASE_COMMIT = "13749adfa616c7f52aa7407cb9a9d7aef3d19c76"


def main() -> int:
    from ledger_common import find_secrets, load_json, run_git, use_utf8_stdout, write_json

    use_utf8_stdout()
    from verify_original_bytes import verify_file_bytes

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--owner", required=True, type=Path)
    options = parser.parse_args()
    state = load_json(CHECKPOINT / "STATE.json")
    code, _ = run_git(
        ROOT, "rev-parse", "--verify", "refs/tags/iacode-checkpoints/" + CHECKPOINT.name
    )
    if state["status"] != "IN_PROGRESS" or state["gate"] != "GATE-7" or code == 0:
        raise ValueError("only this unsealed implementing checkpoint may import rework context")
    owner = options.owner.resolve(strict=True)
    if (
        owner.parent != Path(tempfile.gettempdir()).resolve()
        or owner.name != "iacode-gate7-scope-rework-817a4ca5e0af445babf55b6f010efeab"
        or options.owner.is_symlink()
        or options.owner.is_junction()
    ):
        raise ValueError("only the exact observed disposable context owner is readable")
    inventory_path = owner / "TRANSFER-MANIFEST.json"
    verify_file_bytes(inventory_path, EXPECTED_INVENTORY_SHA256, EXPECTED_INVENTORY_BYTES)
    inventory_bytes = inventory_path.read_bytes()
    inventory = json.loads(inventory_bytes)
    if (
        inventory.get("kind") != "EXACT_CONTEXTUAL_REWORK_TRANSFER_INVENTORY_NOT_ACCEPTANCE"
        or inventory.get("baseCommit") != BASE_COMMIT
        or inventory.get("independentValidation") is not False
        or inventory.get("gateVerdictGranted") is not False
        or not inventory.get("files")
    ):
        raise ValueError("the fixed observed contextual inventory is required")
    destination = CHECKPOINT / "REWORK-CONTEXT-ARCHIVE.json"
    archive = CHECKPOINT / "attempts"
    if destination.exists() or archive.is_symlink() or archive.is_junction():
        raise ValueError("completed or redirected context import must not be overwritten")
    pending = [
        (
            archive / "G7SCR-TRANSFER.raw",
            inventory_bytes,
            {
                "context": "ORIGINAL_TRANSFER_INVENTORY",
                "source": "TRANSFER-MANIFEST.json",
                "bytes": EXPECTED_INVENTORY_BYTES,
                "sha256": EXPECTED_INVENTORY_SHA256,
            },
        )
    ]
    sources = set()
    for index, row in enumerate(inventory["files"], 1):
        relative = PurePosixPath(row["source"])
        if (
            relative.is_absolute()
            or ".." in relative.parts
            or "\\" in row["source"]
            or ":" in row["source"]
            or row["source"] in sources
        ):
            raise ValueError("duplicate or unsafe contextual source path")
        sources.add(row["source"])
        path = owner / Path(*relative.parts)
        if not path.resolve(strict=True).is_relative_to(owner):
            raise ValueError("context source escaped its exact owner")
        verify_file_bytes(path, row["sha256"], row["bytes"])
        pending.append((archive / f"G7SCR-{index:04d}.raw", path.read_bytes(), row))
    # All originals, destinations and privacy are checked before writing the first copy.
    for target, raw, row in pending:
        if (
            not raw
            or hashlib.sha256(raw).hexdigest() != row["sha256"]
            or find_secrets(raw.decode("utf-8", errors="strict"))
        ):
            raise ValueError("context byte identity or safe transport precondition failed")
        if target.exists():
            verify_file_bytes(target, row["sha256"], row["bytes"])
    receipts = []
    for target, raw, row in pending:
        if not target.exists():
            with target.open("xb") as stream:
                stream.write(raw)
        verify_file_bytes(target, row["sha256"], row["bytes"])
        receipts.append(
            {
                "context": row["context"],
                "originalRelativePath": row["source"],
                "archive": target.relative_to(CHECKPOINT).as_posix(),
                "bytes": row["bytes"],
                "sha256": row["sha256"],
            }
        )
    report = {
        "kind": "EXACT_HISTORICAL_CONTEXT_ARCHIVE_NOT_CURRENT_OR_INDEPENDENT_ACCEPTANCE",
        "baseCommit": BASE_COMMIT,
        "sourceInventorySha256": EXPECTED_INVENTORY_SHA256,
        "sourceInventory": "attempts/G7SCR-TRANSFER.raw",
        "files": receipts,
        "commandNamespaceRule": inventory["commandNamespaceRule"],
        "activeSourceOrDocumentation": False,
        "configurationIncluded": False,
        "gateVerdictGranted": False,
        "independentValidation": False,
    }
    write_json(destination, report)
    print(f"RAW_REWORK_CONTEXT_IMPORTED originals={len(receipts)}; no acceptance granted")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
