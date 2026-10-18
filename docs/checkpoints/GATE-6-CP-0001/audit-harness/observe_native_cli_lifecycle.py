"""Bounded plain native CLI observation with a prewarmed, read-only CIM query shell."""

from __future__ import annotations

import base64
import concurrent.futures
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))
sys.path.insert(0, str(ROOT / "scripts/iacode"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from inspect_native_file_lock import owners
from ledger_common import find_secrets, use_utf8_stdout, utc_now, write_json
from native_process import WindowsJob


def main() -> int:
    destination = CHECKPOINT / "attempts/NATIVE-CLI-LIFECYCLE-0001.json"
    raw_destination = CHECKPOINT / "attempts/NATIVE-CLI-LIFECYCLE-0001-PRODUCER.json"
    producer = ROOT / "var/native-cli-lifecycle-0001.json"
    if any(path.exists() for path in (destination, raw_destination, producer)):
        raise ValueError("immutable lifecycle observation exists; do not replay")
    shell = Path("C:/Users/cesar/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/powershell/pwsh.exe")
    script = """
    $ErrorActionPreference='Stop'
    [Console]::WriteLine('READY')
    while($null -ne ($line=[Console]::ReadLine())) {
      if($line -eq 'QUIT'){break}
      try {
        $seen=@{}; $front=@($line.Split(',') | ForEach-Object {[int]$_}); $rows=@()
        for($depth=0;$depth -lt 6 -and $front.Count -gt 0;$depth++) {
          $next=@()
          foreach($number in $front) {
            if($number -le 0 -or $seen.ContainsKey([string]$number)){continue}
            $seen[[string]$number]=$true
            $p=Get-CimInstance Win32_Process -Filter ('ProcessId='+$number)
            if($p) {
              $rows += [pscustomobject]@{pid=$p.ProcessId; parent=$p.ParentProcessId;
                creationFileTime=$p.CreationDate.ToUniversalTime().ToFileTimeUtc().ToString();
                executable=$p.ExecutablePath; commandLine=$p.CommandLine}
              $next += $p.ParentProcessId
            }
          }
          $front=$next
        }
        [Console]::WriteLine((ConvertTo-Json -InputObject @($rows) -Depth 4 -Compress))
      } catch { [Console]::WriteLine('{"queryFailed":true}') }
    }
    """
    encoded = base64.b64encode(script.encode("utf-16-le")).decode("ascii")
    startup = subprocess.STARTUPINFO()
    startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startup.wShowWindow = subprocess.SW_HIDE
    job = WindowsJob()
    query = None
    observations = []
    before = set(Path(tempfile.gettempdir()).glob("iacode-native-editor-*"))
    scanned = set()
    try:
        query = subprocess.Popen([str(shell), "-NoProfile", "-NonInteractive", "-EncodedCommand", encoded],
                                 stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                 text=True, encoding="utf-8", errors="strict", startupinfo=startup,
                                 creationflags=subprocess.CREATE_NO_WINDOW | subprocess.CREATE_NEW_PROCESS_GROUP | 4)
        job.attach_and_resume(query)
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            ready = executor.submit(query.stdout.readline)
            if ready.result(timeout=30).strip() != "READY":
                raise RuntimeError("read-only query shell not ready")
            native = executor.submit(subprocess.run, [sys.executable, "scripts/iacode/native_editor.py",
                                     "--report", producer.relative_to(ROOT).as_posix()], cwd=ROOT,
                                     capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
            while not native.done():
                for directory in set(Path(tempfile.gettempdir()).glob("iacode-native-editor-*")) - before:
                    for log in directory.glob("*/profile/logs/*/agenthost.log"):
                        try:
                            identities = owners(log)
                        except (FileNotFoundError, PermissionError):
                            continue
                        # Read only current log holders; never kill any listed process.
                        selected = [row for row in identities if "powershell" in row.get("application", "").casefold()]
                        key = tuple((row["pid"], row["creationFileTime"]) for row in selected)
                        if not selected or key in scanned:
                            continue
                        scanned.add(key)
                        query.stdin.write(",".join(str(row["pid"]) for row in selected) + "\n")
                        query.stdin.flush()
                        reply = executor.submit(query.stdout.readline).result(timeout=30)
                        if find_secrets(reply):
                            rows = {"unsafeDetailRefused": True, "sha256": hashlib.sha256(reply.encode()).hexdigest()}
                        else:
                            rows = json.loads(reply)
                        observations.append({"observedAt": utc_now(), "log": str(log),
                                             "owners": selected, "processes": rows})
                time.sleep(0.1)
            completed = native.result()
        query.stdin.write("QUIT\n")
        query.stdin.flush()
        query.wait(timeout=10)
    finally:
        query_cleanup = job.close()
        if query is not None:
            query.communicate(timeout=10)
    raw = producer.read_bytes()
    if find_secrets(raw.decode("utf-8", "strict")):
        raise RuntimeError("unsafe producer detail refused")
    with raw_destination.open("xb") as output:
        output.write(raw)
    document = json.loads(raw)
    # Observations of concurrent foreign fixtures would not establish ownership.
    # This diagnostic grants no process-control authority and no acceptance verdict.
    report = {"kind": "PLAIN_NATIVE_CLI_LIFECYCLE_DIAGNOSIS_NOT_ACCEPTANCE", "observedAt": utc_now(),
              "nativeExitCode": completed.returncode, "nativeResult": document.get("result"),
              "directoryCleanup": document.get("directoryCleanup"), "observations": observations,
              "queryOwnedCleanup": query_cleanup, "externalProcessesStopped": 0,
              "gateVerdictIssued": False, "producerArchive": raw_destination.relative_to(ROOT).as_posix(),
              "producerSha256": hashlib.sha256(raw).hexdigest()}
    write_json(destination, report)
    print(json.dumps(report, ensure_ascii=False), flush=True)
    return 0 if observations else 1


if __name__ == "__main__":
    use_utf8_stdout()
    raise SystemExit(main())
