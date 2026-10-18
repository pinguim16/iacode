"""Bounded owner-capture diagnosis; no non-reproduction is promoted to a repair verdict."""

from __future__ import annotations

import hashlib
import io
import json
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))
sys.path.insert(0, str(ROOT / "scripts/iacode"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import native_editor
import native_process
from diagnose_native_owner import query_processes
from inspect_native_file_lock import owners
from ledger_common import find_secrets, use_utf8_stdout, utc_now, write_json


def observe(sequence: int) -> dict:
    stem = f"NATIVE-OWNER-SERIES-{sequence:04d}"
    producer = ROOT / "var" / (stem.lower() + ".json")
    destination = CHECKPOINT / "attempts" / (stem + ".json")
    raw_destination = CHECKPOINT / "attempts" / (stem + "-PRODUCER.json")
    if destination.exists() or producer.exists() or raw_destination.exists():
        raise ValueError("immutable series observation already exists; do not replay")
    actual_remove, observation, pending = native_process.shutil.rmtree, {}, None
    with ThreadPoolExecutor(max_workers=1) as executor:
        def remove(*args, **kwargs):
            nonlocal pending
            try:
                return actual_remove(*args, **kwargs)
            except PermissionError as error:
                if getattr(error, "winerror", None) == 32 and not observation:
                    target = Path(error.filename).resolve()
                    relative = target.relative_to(Path(tempfile.gettempdir()).resolve())
                    if not relative.parts[0].startswith("iacode-native-editor-"):
                        raise ValueError("unexpected native owner") from error
                    identities = owners(target)
                    observation.update({"observedAt": utc_now(), "target": str(target),
                                        "ownersDuringFirstLock": identities})
                    if identities:
                        pending = executor.submit(query_processes, identities)
                raise
        with (mock.patch.object(native_process.shutil, "rmtree", side_effect=remove),
              mock.patch.object(sys, "argv", ["native_editor.py", "--report", str(producer)]),
              redirect_stdout(io.StringIO())):
            native_exit = native_editor.main()
        # Preserve exact native bytes before fallible concurrent-query interpretation.
        raw = producer.read_bytes()
        if find_secrets(raw.decode("utf-8", "strict")):
            raise RuntimeError("unsafe native observation refused")
        with raw_destination.open("xb") as output:
            output.write(raw)
        if pending:
            try:
                query = pending.result()
            except Exception as error:
                query = {"queryFailed": True, "errorType": type(error).__name__}
        else:
            query = {"queryStarted": False}
    native = json.loads(raw)
    report = {"kind": "BOUNDED_NATIVE_OWNER_DIAGNOSIS_NOT_ACCEPTANCE", "observedAt": utc_now(),
              "sequence": sequence, "nativeExitCode": native_exit, "nativeResult": native.get("result"),
              "actualNativeRoots": [row.get("processId") for row in native.get("runs", [])],
              "directoryCleanup": native.get("directoryCleanup"), "firstLock": observation,
              "ownerQuery": query, "externalProcessesStopped": 0, "gateVerdictIssued": False,
              "nativeProducerArchive": raw_destination.relative_to(ROOT).as_posix(),
              "nativeProducerSha256": hashlib.sha256(raw).hexdigest()}
    write_json(destination, report)
    print(json.dumps(report, ensure_ascii=False), flush=True)
    return report


def main() -> int:
    for sequence in (1, 2, 3):
        report = observe(sequence)
        if report["firstLock"]:
            return 0 if report["ownerQuery"].get("creationIdentitiesMatched") else 1
        if report["nativeExitCode"]:
            return 1
    print("OWNER_DIAGNOSIS=NOT_REPRODUCED; no repair or Gate verdict inferred")
    return 1


if __name__ == "__main__":
    use_utf8_stdout()
    raise SystemExit(main())
