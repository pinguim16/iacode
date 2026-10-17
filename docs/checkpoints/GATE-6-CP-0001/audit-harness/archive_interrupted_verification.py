"""Observe incomplete-attempt cleanup neutrally after its original and interrupt recorders exit."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))
sys.path.insert(0, str(ROOT / "scripts/iacode"))
from ledger_common import load_json, utc_now, use_utf8_stdout, write_json
from verify import verification_environment


def main() -> int:
    attempt = load_json(CHECKPOINT / "attempts/FULL-VERIFY-INTERRUPTED-0001.json")
    clone = Path(attempt["progress"]["clone"]).resolve()
    owner = clone.parent
    if owner.parent != Path(tempfile.gettempdir()).resolve() or not owner.name.startswith("iacode-gate6-full-verification-"):
        raise ValueError("unexpected owned clone identity; no cleanup is attempted")
    project = verification_environment(clone, {})["COMPOSE_PROJECT_NAME"]
    remaining = {}
    for resource, arguments in (("containers", ["ps", "-aq"]),
                                ("volumes", ["volume", "ls", "-q"]),
                                ("networks", ["network", "ls", "-q"])):
        result = subprocess.run(["docker", *arguments, "--filter", "label=com.docker.compose.project=" + project],
            cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
        if result.returncode:
            raise ValueError("owned resource observation failed")
        remaining[resource] = len(result.stdout.splitlines())
    progress_path = CHECKPOINT / "FULL-VERIFY-PROGRESS.json"
    raw = progress_path.read_bytes()
    if json.loads(raw)["subjectCommit"] != attempt["subjectCommit"]:
        raise ValueError("original incomplete progress is no longer current; do not synthesize it")
    destination = CHECKPOINT / "attempts/FULL-VERIFY-INTERRUPTED-0001-PROGRESS.json"
    with destination.open("xb") as output:
        output.write(raw)
    write_json(CHECKPOINT / "attempts/FULL-VERIFY-INTERRUPTED-0001-CLEANUP.json", {
        "kind": "OBSERVED_INCOMPLETE_ATTEMPT_NOT_ACCEPTANCE", "observedAt": utc_now(),
        "subjectCommit": attempt["subjectCommit"], "temporaryCloneOwnerRemoved": not owner.exists(),
        "ownedComposeProject": project, "remainingOwnedResources": remaining,
        "progressBytes": len(raw), "progressSha256": hashlib.sha256(raw).hexdigest(),
        "completedStageVerdictAvailable": False, "verifierReportAvailable": False,
        "gateVerdictIssued": False,
        "limits": "Only exact verifier owner/project cleanup is observed; no global temporary-directory cleanup or test PASS is claimed."})
    if owner.exists() or any(remaining.values()):
        raise ValueError("an interrupted owned resource remains; no acceptance is claimed")
    print("INCOMPLETE_ATTEMPT_OBSERVED cloneRemoved=true ownedResources=0 completedStageVerdict=UNAVAILABLE")
    return 0


if __name__ == "__main__":
    use_utf8_stdout()
    raise SystemExit(main())
