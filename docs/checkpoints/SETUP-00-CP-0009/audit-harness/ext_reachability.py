#!/usr/bin/env python3
"""Is a legitimate MILESTONE_EXTERNAL_PASS reachable at all?

Every rejection scenario in section 11 of the audit brief tests that a forged
external PASS is refused. A control that refuses every input, including the true
one, is not a control, so this experiment builds the most favourable *legitimate*
promotion the mechanism allows and records what happens.

Most favourable case:
  subject checkpoint  : SETUP-00-CP-0008 (the delivery being promoted)
  audit checkpoint    : SETUP-00-CP-0007 (a different checkpoint, sealed under its
                        canonical tag and present in the integrity chain)
  four results        : APPROVED / RED_TEAM_PASS / 100.0 / 100.0 / PASS
  gate                : SETUP-00, which closes milestone M0

Nothing here touches the real repository.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
import os as _os
from pathlib import Path as _Path
_DEFAULT_ROOT = _Path(__file__).resolve().parents[4]

sys.path.insert(0, str(Path(__file__).parent))
from fixture import Fixture, git, summarize  # noqa: E402

ROOT = Path(_os.environ.get("IACODE_ROOT") or _DEFAULT_ROOT)
NAME = "SETUP-00-CP-0008"
RELATIVE = ".iacode/attestations/M0-REACHABILITY.json"


def attestation(subject_commit: str) -> dict:
    return {
        "schemaVersion": "1.0.0",
        "auditId": "M0-REACHABILITY",
        "milestone": "M0",
        "auditorRole": "milestone independent auditor",
        "tool": "CP-0009 reachability experiment",
        "provider": "audit fixture",
        "model": "not-applicable",
        "subjectCheckpoint": NAME,
        "subjectCommit": subject_commit,
        "auditCheckpoint": "SETUP-00-CP-0007",
        "auditCommit": "502c554575f717c1d57290e4f4aafa575e41170e",
        "reviewResult": "APPROVED",
        "redTeamResult": "RED_TEAM_PASS",
        "completeness": 100.0,
        "evidenceCoverage": 100.0,
        "testResult": "PASS",
        "createdAt": "2026-09-20T23:59:00Z",
        "notes": "Most favourable legitimate attestation the mechanism allows.",
    }


def promote(f: Fixture, subject_commit: str) -> None:
    (f.path / RELATIVE).parent.mkdir(parents=True, exist_ok=True)
    (f.path / RELATIVE).write_text(json.dumps(attestation(subject_commit), indent=2) + "\n",
                                   encoding="utf-8", newline="\n")
    state = f.read_json("STATE.json")
    state["status"] = "MILESTONE_EXTERNAL_PASS"
    state["milestone"].update({"status": "PASSED",
                               "auditor": "CP-0009 reachability experiment",
                               "auditedAt": "2026-09-20T23:59:00Z"})
    state["secondToolValidation"] = {
        "status": "PASSED", "tool": "CP-0009 reachability experiment",
        "provider": "audit fixture", "model": "not-applicable",
        "validatedAt": "2026-09-20T23:59:00Z",
        "justification": "derived from the attestation", "evidence": ["file:" + RELATIVE]}
    state["externalAttestation"] = {"status": "VERIFIED", "path": RELATIVE,
                                    "auditId": "M0-REACHABILITY",
                                    "evidence": ["file:" + RELATIVE]}
    state["independentReview"] = {"status": "APPROVED", "tool": "CP-0009",
                                  "reviewedAt": "2026-09-20T23:59:00Z",
                                  "justification": "experiment", "evidence": ["file:" + RELATIVE]}
    state["redTeam"] = {"status": "RED_TEAM_PASS", "tool": "CP-0009",
                        "executedAt": "2026-09-20T23:59:00Z",
                        "justification": "experiment", "evidence": ["file:" + RELATIVE]}
    f.write_json("STATE.json", state)
    (f.checkpoint / "STATUS.md").write_text("# Status\n\nMILESTONE_EXTERNAL_PASS\n",
                                            encoding="utf-8", newline="\n")
    handoff = f.checkpoint / "HANDOFF.md"
    handoff.write_text(handoff.read_text(encoding="utf-8").replace(
        "Current Status: READY_FOR_REVIEW", "Current Status: MILESTONE_EXTERNAL_PASS"),
        encoding="utf-8", newline="\n")


def main() -> int:
    workdir = Path(sys.argv[1])
    workdir.mkdir(parents=True, exist_ok=True)
    f = Fixture(ROOT, NAME, workdir)
    report = {"attempts": []}

    # Attempt 1: bind the commit the checkpoint currently carries, then re-seal.
    f.reset()
    promote(f, f.base)
    f.declare_created(RELATIVE, "External audit attestation.")
    f.reseal("reachability attempt 1")
    code, head1 = git(f.path, "rev-parse", "HEAD")
    exit1, out1 = f.validator()
    report["attempts"].append({
        "attempt": 1,
        "description": "attestation binds the pre-seal commit; the seal then moves the tag",
        "boundCommit": f.base, "tagCommitAfterSeal": head1,
        "exit": exit1, "observed": summarize(out1, 2000)})
    print("[1] exit=" + str(exit1))
    print(out1)

    # Attempt 2: bind the commit the tag names after the seal, then fold it in.
    f.reset()
    promote(f, f.base)
    f.declare_created(RELATIVE, "External audit attestation.")
    f.reseal("reachability attempt 2")
    code, sealed = git(f.path, "rev-parse", "HEAD")
    (f.path / RELATIVE).write_text(json.dumps(attestation(sealed), indent=2) + "\n",
                                   encoding="utf-8", newline="\n")
    f.refresh_inventory()
    head2 = f.amend()
    exit2, out2 = f.validator()
    report["attempts"].append({
        "attempt": 2,
        "description": "attestation is rewritten to bind the sealed commit, which changes that commit",
        "boundCommit": sealed, "tagCommitAfterAmend": head2,
        "exit": exit2, "observed": summarize(out2, 2000)})
    print("[2] exit=" + str(exit2) + " bound=" + sealed[:12] + " actual=" + head2[:12])
    print(out2)

    # Attempt 3: iterate the fixed point. Each rewrite changes the commit it names.
    bound = head2
    for iteration in range(3):
        (f.path / RELATIVE).write_text(json.dumps(attestation(bound), indent=2) + "\n",
                                       encoding="utf-8", newline="\n")
        f.refresh_inventory()
        bound_before = bound
        bound = f.amend()
        print("    iteration " + str(iteration) + ": named " + bound_before[:12]
              + " -> commit became " + bound[:12]
              + ("  FIXED POINT" if bound == bound_before else ""))
        if bound == bound_before:
            break
    exit3, out3 = f.validator()
    report["attempts"].append({
        "attempt": 3, "description": "iterating the rewrite looking for a fixed point",
        "exit": exit3, "observed": summarize(out3, 2000)})
    print("[3] exit=" + str(exit3))
    print(out3)

    f.reset()
    (workdir / "ext-reachability.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
