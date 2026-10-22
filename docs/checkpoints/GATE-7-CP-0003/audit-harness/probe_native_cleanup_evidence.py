"""Actual native Python producer with controlled post-drain callback failure, no editor launch."""

from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(
    0, str(Path(__file__).resolve().parents[1].parents[2] / "scripts/development-ledger")
)
sys.path.insert(0, str(Path(__file__).resolve().parents[1].parents[2] / "scripts/iacode"))
import native_editor
from ledger_common import scope_fingerprint, utc_now, write_json
from native_process import NativeJobCleanupError, WindowsJob

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]


def main():
    arguments = [sys.executable, "-c", "print('NATIVE_PRODUCER_CANARY');raise SystemExit(7)"]
    null = native_editor.run_owned(arguments, environment=dict(os.environ), timeout=15)
    null_ok = null.returncode == 7 and "NATIVE_PRODUCER_CANARY" in null.stdout

    class ControlledPostDrainFailure(WindowsJob):
        def close(self):
            actual = super().close()
            raise NativeJobCleanupError(
                "controlled callback failure after actual owned drain", actual
            )

    observed = {"exceptionType": None, "producerObservationExposed": False, "ownedDrain": None}
    with patch.object(native_editor, "WindowsJob", ControlledPostDrainFailure):
        try:
            native_editor.run_owned(arguments, environment=dict(os.environ), timeout=15)
        except NativeJobCleanupError as error:
            observed["exceptionType"] = type(error).__name__
            observed["ownedDrain"] = error.observation
            observed["producerObservationExposed"] = bool(
                getattr(error, "producer", None) or error.observation.get("producer")
            )
    report = {
        "observedAt": utc_now(),
        "kind": "CONTROLLED_NATIVE_CALLBACK_CAUSAL_PROBE_NOT_FUNCTIONAL_ACCEPTANCE",
        "sourceFingerprint": scope_fingerprint(ROOT),
        "producerArguments": arguments,
        "nullControl": {
            "result": "PASS" if null_ok else "FAIL",
            "exitCode": null.returncode,
            "stdoutSha256": hashlib.sha256(null.stdout.encode()).hexdigest(),
        },
        "controlledCallbackFailure": observed,
        "editorStarted": False,
        "dockerAccessed": False,
        "result": "PASS" if null_ok and observed["producerObservationExposed"] else "FAIL",
        "note": (
            "The callback error is deliberate fault injection after a rea"
            "l owned-tree drain, not an observed OS cleanup failure. The "
            "actual producer result must remain exposed even then."
        ),
    }
    folder = CHECKPOINT / "causal-attempts/native-cleanup-evidence"
    folder.mkdir(parents=True, exist_ok=True)
    index = len(list(folder.glob("run-*.json"))) + 1
    write_json(folder / f"run-{index:04d}.json", report)
    print(json.dumps(report))
    return int(report["result"] != "PASS")


if __name__ == "__main__":
    from ledger_common import use_utf8_stdout

    use_utf8_stdout()
    raise SystemExit(main())
