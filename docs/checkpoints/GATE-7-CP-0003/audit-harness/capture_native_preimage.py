"""Preserve the exact original native wrapper before the M2-F-002 extension."""

import hashlib
import sys
from pathlib import Path

sys.path.insert(
    0, str(Path(__file__).resolve().parents[1].parents[2] / "scripts/development-ledger")
)
from ledger_common import scope_fingerprint, utc_now, write_json

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]


def main():
    source = ROOT / "scripts/iacode/native_editor.py"
    raw = source.read_bytes()
    folder = CHECKPOINT / "raw-preimages"
    folder.mkdir(exist_ok=True)
    target = folder / "M2-F-002-NATIVE.py.raw"
    with target.open("xb") as stream:
        stream.write(raw)
    if target.read_bytes() != raw:
        raise ValueError("Original byte preservation failed")
    write_json(
        folder / "M2-F-002-NATIVE.json",
        {
            "observedAt": utc_now(),
            "source": source.relative_to(ROOT).as_posix(),
            "archive": target.relative_to(CHECKPOINT).as_posix(),
            "sha256": hashlib.sha256(raw).hexdigest(),
            "bytes": len(raw),
            "sourceFingerprint": scope_fingerprint(ROOT),
            "acceptanceGranted": False,
        },
    )
    print("Exact native source preimage retained; no source alteration")
    return 0


if __name__ == "__main__":
    from ledger_common import use_utf8_stdout

    use_utf8_stdout()
    raise SystemExit(main())
