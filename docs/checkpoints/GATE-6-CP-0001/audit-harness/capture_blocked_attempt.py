"""Retain incomplete v3 facts and bounded read-only Docker management observations; never pass."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))
from ledger_common import use_utf8_stdout, utc_now, write_json


def probe(arguments: list[str]) -> dict:
    """Bound only this newly launched diagnostic; never stop the daemon or any container."""
    try:
        result = subprocess.run(["docker", "--context", "desktop-linux", *arguments],
            cwd=ROOT, capture_output=True, timeout=5, check=False)
    except subprocess.TimeoutExpired:
        return {"arguments": arguments, "result": "TIMEOUT", "timeoutSeconds": 5,
                "ownedResources": None}
    # Do not export stderr, daemon configuration, environment or arbitrary output.
    output = result.stdout.decode("utf-8", errors="strict").strip()
    safe = re.fullmatch(r"[A-Za-z0-9_. \-\r\n]*", output) is not None
    return {"arguments": arguments, "result": "RESPONDED" if result.returncode == 0 else "ERROR",
            "exitCode": result.returncode, "safeOutput": output if safe else None}


def main() -> int:
    destination = CHECKPOINT / "attempts/FULL-VERIFY-INTERRUPTED-0003.json"
    if destination.exists():
        raise ValueError("original v3 interruption receipt must never be overwritten")
    progress = json.loads((CHECKPOINT / "FULL-VERIFY-PROGRESS.json").read_bytes())
    if progress["subjectCommit"] != "127926d4922e8e63e51fd64681fbe1cd04f21800":
        raise ValueError("unexpected interrupted subject")
    # This only observes the exact owner already removed by its original context manager.
    clone = Path(progress["clone"])
    project = "iacode-verify-acf6759435d1"
    observations = [probe(["version", "--format", "{{.Server.Version}}"])]
    for kind in ("container", "volume", "network"):
        observations.append(probe([kind, "ls", "--filter",
            "label=com.docker.compose.project=" + project, "--format", "{{.ID}}"
            if kind != "volume" else "{{.Name}}", *( ["--all"] if kind == "container" else [])]))
    completed = []
    for line in progress["transitions"]:
        match = re.fullmatch(r"\[iacode\] --- (.+): (PASS|FAIL) in ([0-9.]+)s", line)
        if match:
            completed.append({"stage": match[1], "result": match[2], "durationSeconds": float(match[3])})
    write_json(destination, {
        "kind": "ENVIRONMENT_BLOCKED_INTERRUPTED_VERIFICATION_NOT_PASS",
        "generatedAt": utc_now(), "subjectCommit": progress["subjectCommit"],
        "sourceFingerprintAtInterruption": "9c4d40cb7d04f512d29c8383a5f6c158f024062a23ede2447ab05fd6ddc6e43b",
        "originalCommand": "command:cmd-0136", "progress": progress,
        "completedStageObservations": completed, "canonicalStageDenominator": 47,
        "verificationResult": "NOT_COMPLETED", "gateVerdictIssued": False,
        "completedStageVerdictAvailable": True, "completeVerifierReportAvailable": False,
        "termination": {"observedAt": "2026-10-17T19:45:37.5093892Z",
            "targetPid": 12240, "parentPid": 39612, "recorderPid": 42424,
            "targetCreatedUtc": "2026-10-17T17:52:43Z", "identityRevalidatedBeforeStop": True,
            "onlyVerifierProcessTreeStopped": True, "exitCode": 0,
            "originalRecorderFinished": True},
        "temporaryCloneRemovedByOriginalOwner": not clone.parent.exists(),
        "composeProject": project, "dockerObservations": observations,
        "ownedCleanup": "UNVERIFIED", "sharedProjectIdentityComparison": "UNAVAILABLE",
        "dockerRestarted": False, "serviceOrContainerStopPerformed": False,
        "reason": "The owned quality-pass port query stalled from 19:29:39 UTC; fresh version, owned list and both direct named-pipe pings also did not respond within bounds. The owner asked to retry without disrupting other applications. No exact daemon root cause is asserted.",
        "rootSuite": {"result": "FAIL", "testsRun": 892, "failures": 2,
            "evidenceKind": "direct original captured console observation, not a complete producer report",
            "cases": ["LessonPreflightTests.test_the_repository_preflight_covers_every_applicable_lesson",
                "Gate5QualityIntegrationTests.test_every_inherited_gate_remains_and_clients_are_mandatory"],
            "causalReproductions": ["command:cmd-0138", "command:cmd-0139"]},
        "limits": "Original full output had no configured raw artifact. The safe direct observations and actual command outcome are retained; no missing raw report, cleanup result, stage or test is inferred."
    })
    print("INCOMPLETE_V3_RETAINED completed=" + str(len(completed)) +
          " canonical=47 root=FAIL cleanup=UNVERIFIED no_gate_verdict=true")
    return 0


if __name__ == "__main__":
    use_utf8_stdout()
    raise SystemExit(main())
