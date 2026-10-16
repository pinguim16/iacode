#!/usr/bin/env python3
"""Read nonblocking stack frames from this checkpoint's active verifier, never locals."""

from __future__ import annotations

import sys

import argparse
import hashlib
import io
import json
import re
import subprocess
import tempfile
import urllib.parse
import urllib.request
import zipfile
from datetime import UTC, datetime
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
VERSION = "0.4.2"
WHEEL = f"py_spy-{VERSION}-py2.py3-none-win_amd64.whl"
SHA256 = "8b06a353c177677e4e1701b288d8c58e2f8d4208ee81a8048d9f72ba800918f8"


def download(url: str, maximum: int) -> bytes:
    with urllib.request.urlopen(url, timeout=20) as response:
        content = response.read(maximum + 1)
    if len(content) > maximum:
        raise ValueError("diagnostic download exceeds its fixed size bound")
    return content


def active_test_process(
    subject: str, root_probe: bool = False, working_tree: bool = False,
) -> int | None:
    if not re.fullmatch(r"[0-9a-f]{40}", subject):
        raise ValueError("the verifier subject is not an exact commit")
    script = r'''
$observed = @(Get-CimInstance Win32_Process -Filter "Name='python.exe'")
$runners = @($observed | Where-Object {
    $_.CommandLine -match 'run_full_verification[.]py' -and
    $_.CommandLine -match 'SUBJECT_COMMIT' -and
    $_.CommandLine -notmatch 'record_command[.]py'
})
$targets = @()
foreach ($runner in $runners) {
    foreach ($verifier in @($observed | Where-Object {
        $_.ParentProcessId -eq $runner.ProcessId -and $_.CommandLine -match 'verify[.]py'
    })) {
        $targets += @($observed | Where-Object {
            $_.ParentProcessId -eq $verifier.ProcessId -and
            $_.CommandLine -match '-m\s+unittest\s+discover\s+-s\s+tests(?:\s|$)'
        } | Select-Object -ExpandProperty ProcessId)
    }
}
ConvertTo-Json -InputObject @($targets)
'''.replace("SUBJECT_COMMIT", subject)
    if root_probe:
        script = script.replace("run_full_verification[.]py", "diagnose_published_root_failure[.]py")
        script = script.replace(f"$_.CommandLine -match '{subject}' -and", "")
        script = script.replace(
            "foreach ($verifier in @($observed | Where-Object {\n"
            "        $_.ParentProcessId -eq $runner.ProcessId -and $_.CommandLine -match 'verify[.]py'\n"
            "    })) {",
            "foreach ($verifier in @($runner)) {",
        )
    elif working_tree:
        script = r'''
$observed = @(Get-CimInstance Win32_Process -Filter "Name='python.exe'")
$parents = @($observed | Where-Object {
    $_.CommandLine -match 'record_command[.]py' -and
    $_.CommandLine -match 'Execute the complete root regression suite on all current corrections'
} | Select-Object -ExpandProperty ProcessId)
$targets = @($observed | Where-Object {
    $_.ParentProcessId -in $parents -and
    $_.CommandLine -match '-m unittest discover -s tests -v$'
} | Select-Object -ExpandProperty ProcessId)
ConvertTo-Json -InputObject @($targets)
'''
    observed = subprocess.run(
        ["pwsh", "-NoProfile", "-Command", script], cwd=ROOT,
        capture_output=True, text=True, encoding="utf-8", check=True, timeout=20,
    )
    targets = json.loads(observed.stdout)
    if len(targets) > 1:
        raise ValueError("more than one current-subject test process; diagnosis refused")
    return int(targets[0]) if targets else None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    selection = parser.add_mutually_exclusive_group()
    selection.add_argument("--root-probe", action="store_true")
    selection.add_argument("--working-tree-root", action="store_true")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    destination = CHECKPOINT / (
        "WORKING-TREE-ROOT-PERFORMANCE.json" if args.working_tree_root else
        "ROOT-PROBE-PERFORMANCE.json" if args.root_probe else "VALIDATION-PERFORMANCE.json")
    if args.report:
        destination = (ROOT / args.report).resolve()
        if not args.working_tree_root or destination.parent != CHECKPOINT:
            raise ValueError("named observations must be working-tree diagnostics in this checkpoint")
    if destination.exists():
        raise ValueError("preserve the prior diagnostic before another attempt")
    progress = ({"subjectCommit": "4c53e4f788adc24e1b9cd9f581a7dc0d0f3c1340", "clone": ""}
                if args.root_probe or args.working_tree_root else json.loads(
                    (CHECKPOINT / "FULL-VERIFY-PROGRESS.json").read_text(encoding="utf-8")))
    report: dict[str, object] = {
        "schemaVersion": "1.0.0", "generatedAt": datetime.now(UTC).isoformat(),
        "subjectCommit": progress["subjectCommit"], "kind": "NONBLOCKING_READ_ONLY_DIAGNOSTIC",
        "tool": f"py-spy {VERSION}", "toolLicense": "MIT", "wheelSha256": SHA256,
        "source": f"https://pypi.org/project/py-spy/{VERSION}/",
        "capturesLocals": False, "modifiesTestedCode": False,
    }
    temporary: str | None = None
    if args.working_tree_root:
        report["kind"] = "WORKING_TREE_NONBLOCKING_DIAGNOSTIC_NOT_IMMUTABLE_SUBJECT"
        report["sourceState"] = "deliberate dirty Gate 4 corrective tree; HEAD is ancestry only"
        report["promotionEvidence"] = False
    try:
        target = active_test_process(
            str(report["subjectCommit"]), args.root_probe, args.working_tree_root)
        if target is None:
            report.update(result="NOT_APPLICABLE", reason="no active current-subject root suite")
        else:
            metadata = json.loads(download(f"https://pypi.org/pypi/py-spy/{VERSION}/json", 1_000_000))
            matches = [row for row in metadata["urls"] if row["filename"] == WHEEL]
            if len(matches) != 1 or matches[0]["digests"]["sha256"] != SHA256:
                raise ValueError("the published diagnostic wheel identity changed")
            url = matches[0]["url"]
            parsed = urllib.parse.urlsplit(url)
            if parsed.scheme != "https" or parsed.hostname != "files.pythonhosted.org":
                raise ValueError("the diagnostic download is not the approved package host")
            wheel = download(url, 4_000_000)
            if hashlib.sha256(wheel).hexdigest() != SHA256:
                raise ValueError("the diagnostic wheel failed content verification")
            with tempfile.TemporaryDirectory(prefix="iacode-cp0010-profiler-") as temporary:
                executable = Path(temporary) / "py-spy.exe"
                with zipfile.ZipFile(io.BytesIO(wheel)) as archive:
                    members = [name for name in archive.namelist() if name.endswith("/py-spy.exe")]
                    if len(members) != 1:
                        raise ValueError("the pinned wheel has no unique profiler executable")
                    executable.write_bytes(archive.read(members[0]))
                sampled = subprocess.run(
                    [str(executable), "dump", "--pid", str(target), "--nonblocking"],
                    capture_output=True, text=True, encoding="utf-8", errors="replace",
                    check=False, timeout=15,
                )
                frames = [line.strip() for line in sampled.stdout.splitlines()
                          if re.fullmatch(r"\s+.+ \(.+:\d+\)", line)]
                report.update(
                    processId=target, profilerExitCode=sampled.returncode,
                    frames=[line.replace(str(progress["clone"]), "<verification-clone>")
                            if progress["clone"] else line
                            for line in frames],
                    result="PROFILE_CAPTURED" if sampled.returncode == 0 and frames else "FAIL",
                )
                if sampled.returncode != 0:
                    report["failure"] = "nonblocking profiler could not read the target; no fallback attached"
    except Exception as error:
        report.update(result="FAIL", failureType=type(error).__name__)
    report["temporaryProfilerRemoved"] = temporary is None or not Path(temporary).exists()
    if not report["temporaryProfilerRemoved"]:
        report["result"] = "FAIL"
    destination.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(report, indent=2))
    return 1 if report["result"] == "FAIL" else 0


if __name__ == "__main__":
    sys.path.insert(0, str(ROOT / "scripts/development-ledger"))
    from ledger_common import use_utf8_stdout

    use_utf8_stdout()
    raise SystemExit(main())
