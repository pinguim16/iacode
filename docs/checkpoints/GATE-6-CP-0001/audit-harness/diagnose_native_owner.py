"""Observe the current log owner at the first real lock; never stop an external process."""

from __future__ import annotations

import base64
import hashlib
import io
import json
import os
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
from inspect_native_file_lock import owners
from ledger_common import find_secrets, use_utf8_stdout, utc_now, write_json


def query_processes(identities: list[dict]) -> dict:
    shell = Path("C:/Users/cesar/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/powershell/pwsh.exe")
    if not shell.is_file():
        raise RuntimeError("observed bundled NoProfile PowerShell executable is unavailable")
    identifiers = ",".join(str(int(row["pid"])) for row in identities)
    script = ("$ErrorActionPreference='Stop'; $ProgressPreference='SilentlyContinue'; "
              "$seen=@{}; $front=@(" + identifiers + "); $rows=@(); "
              "for($depth=0;$depth -lt 6 -and $front.Count -gt 0;$depth++){ "
              "$next=@(); foreach($processNumber in $front){ "
              "if($seen.ContainsKey([string]$processNumber)){continue}; "
              "$seen[[string]$processNumber]=$true; "
              "$p=Get-CimInstance Win32_Process -Filter ('ProcessId='+$processNumber); "
              "if($p){$rows += [pscustomobject]@{pid=$p.ProcessId;parent=$p.ParentProcessId;"
              "creationFileTime=$p.CreationDate.ToUniversalTime().ToFileTimeUtc().ToString();"
              "executable=$p.ExecutablePath;commandLine=$p.CommandLine}; "
              "$next += $p.ParentProcessId}}; $front=$next}; "
              "ConvertTo-Json -InputObject @($rows) -Depth 4 -Compress")
    encoded = base64.b64encode(script.encode("utf-16-le")).decode("ascii")
    # Only this newly created read-only query shell is owned/drained, never a listed process.
    completed = native_editor.run_owned(
        [str(shell), "-NoProfile", "-NonInteractive", "-EncodedCommand", encoded],
        environment=dict(os.environ), timeout=30,
    )
    payload = completed.stdout.encode("utf-8")
    if completed.returncode or find_secrets(completed.stdout):
        return {"queryExitCode": completed.returncode, "detailRetained": False,
                "outputSha256": hashlib.sha256(payload).hexdigest()}
    rows = json.loads(completed.stdout)
    matched = all(any(int(row["pid"]) == identity["pid"]
                      and int(row["creationFileTime"]) == identity["creationFileTime"]
                      for row in rows) for identity in identities)
    return {"queryExitCode": completed.returncode, "creationIdentitiesMatched": matched,
            "processes": rows, "queryOwnedCleanup": completed.owned_tree_cleanup}


def main() -> int:
    destination = CHECKPOINT / "attempts/NATIVE-OWNER-DIAGNOSTIC-0001.json"
    producer = ROOT / "var/native-owner-diagnostic-0001.json"
    raw_destination = CHECKPOINT / "attempts/NATIVE-OWNER-DIAGNOSTIC-0001-PRODUCER.json"
    if destination.exists() or producer.exists() or raw_destination.exists():
        raise ValueError("immutable owner diagnostic already exists; do not replay")
    actual_remove = native_process.shutil.rmtree
    observation = {}
    pending = None
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
                        raise ValueError("unexpected native diagnostic owner") from error
                    identities = owners(target)
                    observation.update({"observedAt": utc_now(), "target": str(target),
                                        "ownersDuringFirstLock": identities})
                    if identities:
                        pending = executor.submit(query_processes, identities)
                raise
        arguments = ["native_editor.py", "--report", str(producer)]
        with (mock.patch.object(native_process.shutil, "rmtree", side_effect=remove),
              mock.patch.object(sys, "argv", arguments), redirect_stdout(io.StringIO())):
            native_exit = native_editor.main()
        query = pending.result() if pending else {"queryStarted": False}
    raw = producer.read_bytes()
    unsafe = find_secrets(raw.decode("utf-8", "strict"))
    if unsafe:
        raise RuntimeError("unsafe native diagnostic output refused")
    with raw_destination.open("xb") as output:
        output.write(raw)
    native = json.loads(raw)
    report = {"kind": "ACTUAL_NATIVE_OWNER_DIAGNOSTIC_NOT_ACCEPTANCE", "observedAt": utc_now(),
              "nativeExitCode": native_exit, "nativeResult": native.get("result"),
              "actualNativeRoots": [row.get("processId") for row in native.get("runs", [])],
              "directoryCleanup": native.get("directoryCleanup"), "firstLock": observation,
              "ownerQuery": query, "externalProcessesStopped": 0,
              "nativeProducerArchive": raw_destination.relative_to(ROOT).as_posix(),
              "nativeProducerSha256": hashlib.sha256(raw).hexdigest(),
              "gateVerdictIssued": False}
    write_json(destination, report)
    print(json.dumps(report, ensure_ascii=False))
    return 0 if observation and query.get("creationIdentitiesMatched") else 1


if __name__ == "__main__":
    use_utf8_stdout()
    raise SystemExit(main())
