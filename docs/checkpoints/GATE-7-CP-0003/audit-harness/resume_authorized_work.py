"""Record explicit owner decisions and resume the existing unsealed corrective checkpoint."""

from __future__ import annotations

import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))
from ledger_common import git_snapshot, load_json, utc_now, write_json


def main() -> int:
    state = load_json(CHECKPOINT / "STATE.json")
    snapshot = git_snapshot(ROOT)
    if state["status"] != "BLOCKED" or snapshot["head"] != state["baseCommit"] or snapshot["branch"] != state["branch"]:
        raise ValueError("resume requires the known blocked checkpoint and unchanged Git identity")
    now = utc_now()
    write_json(CHECKPOINT / "OWNER-DECISIONS.json", {
        "recordedAt": now,
        "source": "Direct owner replies to both pending questions and subsequent cleanup instruction.",
        "limitedHostRunnerBridge": "AUTHORIZED",
        "benignUnsealedReportWordingRepair": "AUTHORIZED",
        "taskOwnedWasteCleanup": "REQUIRED",
        "limits": ["Canonical frozen commands/arguments/sources only outside restricted token.",
                   "Rest of auditor remains workspace-write; no general CLI bypass.",
                   "No global changes, other-chat changes, restarts or writes to preexisting applications.",
                   "Preserve CP0002 and all sealed subjects; keep strict secret detector unchanged.",
                   "Remove only verified task-owned disposable resources after preserving evidence; no global prune.",
                   "No Gate8; independent auditor implements no corrections."],
    })
    state.update({"status": "IN_PROGRESS", "blockedBy": [], "updatedAt": now,
                  "nextAllowedAction": "Apply documented prose repair, implement and adversarially validate the limited runner bridge and owned cleanup, then complete all canonical internal assurance before sealing and a fresh M2 auditor."})
    write_json(CHECKPOINT / "STATE.json", state)
    (CHECKPOINT / "STATUS.md").write_text("# Status\n\nIN_PROGRESS\n", encoding="utf-8", newline="\n")
    metadata = load_json(CHECKPOINT / "RUN-METADATA.json")
    metadata["finishedAt"] = now
    write_json(CHECKPOINT / "RUN-METADATA.json", metadata)
    print("AUTHORIZED_CORRECTIVE_WORK_RESUMED no_independent_verdict_no_Gate8")
    return 0


if __name__ == "__main__":
    from ledger_common import use_utf8_stdout
    use_utf8_stdout()
    raise SystemExit(main())
