"""Persist the actual scope boundary and incomplete handoff; never manufacture readiness."""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))
from ledger_common import git_snapshot, load_json, utc_now, write_json

BASELINE = {
    "C:/Users/cesar/.codex/config.toml": "28611435eb10f99f2c458136fa3eb9c0941b1814d82324a76ab03738bf21f9c9",
    "C:/Users/cesar/.gitconfig": "a5677fb2056312d31a57b58d8ca526e3519fcc60dfe2ed1779de8d244576b791",
    "C:/Users/cesar/.config/git/ignore": "744e3b6c0e736af11840443f60f3f4b38176d214e026a54763628d8a6c317cbb",
    "C:/Program Files/Git/etc/gitconfig": "381c2fda5a3b5adf7102f5b05f68d7dc3281a44171f9b40556ca56cfdd8461c3",
}


def main() -> int:
    rows = []
    for path, before in BASELINE.items():
        after = hashlib.sha256(Path(path).read_bytes()).hexdigest()
        rows.append({"path": path, "before": before, "after": after, "unchanged": after == before})
    write_json(CHECKPOINT / "ENVIRONMENT-SCOPE.json", {
        "observedAt": utc_now(), "globalConfigurations": rows,
        "allUnchanged": all(row["unchanged"] for row in rows),
        "otherChatSettingWritesPerformed": False, "applicationRestartsPerformed": False,
        "newAuditorTurnStarted": False,
        "note": "Other-chat preservation here records absence of writes, not a new independently measured database hash.",
    })
    if not all(row["unchanged"] for row in rows):
        raise ValueError("global configuration baseline mismatch; retain receipt and investigate")
    now = utc_now()
    snapshot = git_snapshot(ROOT)
    state = load_json(CHECKPOINT / "STATE.json")
    if snapshot["branch"] != state["branch"] or snapshot["head"] != state["baseCommit"]:
        raise ValueError("unexpected Git divergence; do not save a reconciled state")
    state.update({"status": "BLOCKED", "updatedAt": now, "dirty": snapshot["dirty"],
        "blockedBy": [
            "M2 Docker isolation: restricted token is denied at the engine pipe; narrow host-runner bridge approval pending.",
            "Strict scan: benign prose in the prior unsealed entry report; documented wording repair approval pending.",
        ]})
    completeness = load_json(CHECKPOINT / "COMPLETENESS-REPORT.json")
    state["deliveryCompleteness"].update({"status": completeness["result"],
        "coveragePercent": completeness["coveragePercent"],
        "evidenceCoveragePercent": completeness["evidenceCoveragePercent"],
        "auditor": completeness["auditor"],
        "evidence": ["file:docs/checkpoints/GATE-7-CP-0003/COMPLETENESS-REPORT.json"]})
    write_json(CHECKPOINT / "STATE.json", state)
    (CHECKPOINT / "STATUS.md").write_text("# Status\n\nBLOCKED\n", encoding="utf-8", newline="\n")
    metadata = load_json(CHECKPOINT / "RUN-METADATA.json")
    metadata.update({"finishedAt": now, "finalCommit": snapshot["head"]})
    write_json(CHECKPOINT / "RUN-METADATA.json", metadata)
    provenance = load_json(CHECKPOINT / "PROVENANCE.json")
    provenance["artifacts"][0].update({"artifact": CHECKPOINT.relative_to(ROOT).as_posix(),
        "sourceType": "repository-generated and AI-assisted corrective work/evidence",
        "provider": "OpenAI / local execution", "model": "not-exposed",
        "ownership": "project-generated engineering evidence", "license": "project-policy",
        "evidence": "AUTHORIZATION.md, BASELINE.md, COMMANDS.jsonl and FILES.json",
        "notes": "No independent verdict, private reasoning, secrets or inferred reuse rights; original audit evidence is preserved."})
    write_json(CHECKPOINT / "PROVENANCE.json", provenance)
    print("BLOCKED_HANDOFF_SAVED no_seal_no_audit_no_Gate8")
    return 0


if __name__ == "__main__":
    from ledger_common import use_utf8_stdout
    use_utf8_stdout()
    raise SystemExit(main())
