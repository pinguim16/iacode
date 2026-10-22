"""Save observed private disposal and the unresolved external baseline, without acceptance."""

import json
import sys
from pathlib import Path

sys.path.insert(
    0, str(Path(__file__).resolve().parents[1].parents[2] / "scripts/development-ledger")
)
from ledger_common import load_json, scope_fingerprint, utc_now, write_json
from sync_in_progress_metadata import synchronize
from validate_checkpoint import FINAL_REPORT_HEADINGS, HANDOFF_HEADINGS

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]

BLOCKER = "OWNER_CONFIRMATION_EXTERNAL_DOCKER_APPLICATION_TRANSITION"
NEXT = (
    "Confirm the two externally originated esteira-videos replace"
    "ments without changing that project or rewriting the origina"
    "l comparison. Then establish an explicit controlled validati"
    "on interval and a new separately owned disposable resource p"
    "hase, complete all16 canonical gates and the full immutable "
    "non-fast verifier, DCV, fresh internal Red Team/mirror, and "
    "seal READY_FOR_REVIEW before a new independent M2 auditor. N"
    "o Gate8."
)


def render(title, headings, sections, preamble=""):
    if set(headings) != set(sections) or any(
        len(value.strip()) < 20 for value in sections.values()
    ):
        raise ValueError("Every canonical report section needs substantive actual content")
    return (
        "# "
        + title
        + "\n\n"
        + preamble
        + "\n\n".join(key + "\n\n" + sections[key] for key in headings)
        + "\n"
    )


def main():
    state = load_json(CHECKPOINT / "STATE.json")
    if state["status"] != "IN_PROGRESS":
        raise ValueError("This one-shot handoff must not rewrite a terminal checkpoint")
    cleanup = load_json(CHECKPOINT / "OWNED-RESOURCE-CLEANUP.json")
    scope = load_json(CHECKPOINT / "OWNED-DOCKER-SCOPE.json")
    if (
        cleanup["ownedResourceCleanupResult"] != "PASS"
        or cleanup["result"] != "FAIL"
        or cleanup["unrelatedApplicationsUnchanged"] is not False
        or cleanup["unrelatedApplicationsUnchangedDuringCleanup"] is not True
        or not cleanup["privateBuildxConfigRemoved"]
        or Path(scope["privateBuildxConfig"]).exists()
        or cleanup["ownedBuilderCacheVolumesRemaining"]
        or any(
            cleanup["remainingOwned"][key]
            for key in ("containers", "images", "networks", "volumes")
        )
        or any(row["status"] != "COMPLETED" or row["exitCode"] != 0 for row in cleanup["commands"])
    ):
        raise ValueError(
            "Actual complete private disposal beside the retained externa"
            "l comparison failure required"
        )
    for restore in scope["tagRestorations"]:
        if not any(
            row["id"] == restore["baselineImageId"] and restore["tag"] in row["tags"]
            for row in cleanup["after"]["images"]
        ):
            raise ValueError("Original preexisting tag was not actually restored")
    removed = [
        row["arguments"][3]
        for row in cleanup["commands"]
        if row["arguments"][:3] == ["docker", "image", "rm"]
    ]
    before_ids = {row["id"] for row in cleanup["before"]["images"]}
    after_ids = {row["id"] for row in cleanup["after"]["images"]}
    if set(removed) - before_ids or set(removed) & after_ids:
        raise ValueError("Actual removed image identities must resolve before and be absent after")
    current = {row["id"]: row for row in cleanup["after"]["containers"]}
    changed = [row for row in scope["before"]["containers"] if current.get(row["id"]) != row]
    if {row["name"] for row in changed} != {"esteira-videos-web-1", "esteira-videos-worker-1"}:
        raise ValueError("The external divergence set changed; do not silently generalize it")
    replacements = [
        row for row in current.values() if row["name"] in {old["name"] for old in changed}
    ]
    now = utc_now()
    write_json(
        CHECKPOINT / "OWNED-DISPOSAL-SUMMARY.json",
        {
            "observedAt": now,
            "source": "OWNED-RESOURCE-CLEANUP.json",
            "componentResult": "PASS",
            "removedImageIds": removed,
            "removedImageCount": len(removed),
            "privateBuilderRemoved": True,
            "builderCacheVolumesRemoved": cleanup["ownedBuilderCacheVolumes"],
            "removedNetworkIds": cleanup["plan"]["networks"],
            "removedVolumeNames": cleanup["plan"]["volumes"],
            "privateBuildxConfigRemoved": True,
            "preexistingToolchainTagRestored": True,
            "remainingProvenOwnedDisposableResources": cleanup["remainingOwned"],
            "applicationsUnchangedDuringDisposal": True,
            "originalFullBaselineComparison": "FAIL",
            "globalPrunePerformed": False,
            "milestoneOrGateVerdictGranted": False,
        },
    )
    write_json(
        CHECKPOINT / "RESOURCE-DIVERGENCE-0001.json",
        {
            "observedAt": now,
            "source": "resource-preservation/run-0004.json",
            "baselineObservedAt": scope["before"]["observedAt"],
            "originalContainers": changed,
            "observedReplacements": replacements,
            "originalComparisonRetained": "FAIL",
            "readOnlyEngineLabelObservation": {
                "workingDirectory": "E:/esteira_videos",
                "composeFile": "E:/esteira_videos/compose.yaml",
            },
            "observationLimit": (
                "Working-directory labels and start times establish a differe"
                "nt project; they do not identify the initiating person or es"
                "tablish their authority."
            ),
            "ownerConfirmation": "PENDING",
            "otherProjectResourcesModifiedByThisTask": False,
            "otherProjectAddedToCleanupScope": False,
            "originalBaselineRewritten": False,
            "originalDenominator": len(scope["before"]["containers"]),
        },
    )
    archive = CHECKPOINT / "attempts"
    archive.mkdir(exist_ok=True)
    for name in ("HANDOFF.md", "FINAL-REPORT.md", "NEXT.md", "RISKS.md"):
        target = archive / ("PRE-DISPOSAL-HANDOFF-" + name)
        with target.open("xb") as stream:
            stream.write((CHECKPOINT / name).read_bytes())
    common = {
        "completed": (
            "Literal checkpoint invocation/replay, safe separate Docker/n"
            "ative producer and cleanup observations, closed-runner/physi"
            "cal-path controls, generic original-observation byte boundar"
            "ies and local guard restoration. Actual private disposal rem"
            "oved five images, the dedicated builder/cache, one network, "
            "two test volumes and its private config; restored the origin"
            "al toolchain tag. No global prune or other-project cleanup o"
            "ccurred."
        ),
        "pending": (
            "Both finding closures, the complete current16-gate cycle, on"
            "e complete immutable49-stage non-fast verifier, DCV, fresh i"
            "nternal Red Team/mirror, canonical seal/reconstruction and a"
            " later fresh independent M2 report remain pending. The origi"
            "nal findings remain IN_PROGRESS, not CLOSED."
        ),
        "tests": (
            "Current static-analysis run-0006 and complete lint run-0008 "
            "exit0 at unchanged67c1c0fa. Lint run-0007's private OCI-expo"
            "rt timeout remains failed evidence. Three actual transport c"
            "ases and206 staged comparisons pass. Nine distinct operator "
            "boundary controls pass in dependency-cleanup/run-0004; run-0"
            "002's two missing-ownership fixture failures remain beside c"
            "orrected measured premises. The old Root1018 baseline has se"
            "ven failures; the first public whole cycle was deliberately "
            "canceled with exit20 and exact Job/clone cleanup, never give"
            "n a unit verdict."
        ),
        "divergence": (
            "The initial37-container comparison fails for two esteira-vid"
            "eos containers recreated with another image at2026-10-22T00:"
            "09:57Z and00:10:15Z. Their engine labels name E:/esteira_vid"
            "eos, outside this repository. Original IDs/snapshots and the"
            " failed comparison remain. Their replacements and every othe"
            "r unrelated application present before our disposal stayed u"
            "nchanged during it. Attribution/authority confirmation was r"
            "equested from the owner and is still pending."
        ),
        "scope": (
            "Remain within authorized Gate7 corrections. No source/test w"
            "eakening, global configuration change, application restart, "
            "other-chat setting write, independent self-attestation or Ga"
            "te8. Four global configuration files were rechecked byte-ide"
            "ntical after disposal. Other-chat preservation records no wr"
            "ites, not a newly measured chat-database hash."
        ),
        "resume": NEXT,
    }
    handoff = {
        "## Objective": (
            "Finish the Gate7 M2-F-001/M2-F-002 correction and later inde"
            "pendent M2 audit; the latest task-owned waste cleanup is obs"
            "erved complete, but Gate7 is not sealed."
        ),
        "## What was completed": common["completed"],
        "## What was NOT completed": common["pending"],
        "## Current repository state": (
            "Branch main; published IN_PROGRESS runtime-v1 is8312bb282844"
            "dc5d6b5e3e3f7a96f3c77cdbdca9. Current source67c1c0fa is late"
            "r unsealed corrective work. Immutable CP0001 remains the las"
            "t valid seal at823cf164c6931dab7f957c92721ded7a916655bd; fai"
            "led/unsealed CP0002 bytes are preserved."
        ),
        "## Files changed": (
            "FILES.json declares the operational replay/client/native/bri"
            "dge changes, their regressions, Git byte boundaries, memory/"
            "ADR records and all current observations. No files belonging"
            " to E:/esteira_videos were changed."
        ),
        "## Important decisions": common["scope"],
        "## Tests executed": common["tests"],
        "## Known failures": common["divergence"],
        "## Known risks": (
            "The Docker engine responds, but OCI tar export experienced a"
            " retained session timeout before an unchanged complete retry"
            " passed. The old private resource scope is now disposed and "
            "refuses replay. Historical refused/ambiguous temporary targe"
            "ts remain outside deletion authority. No current complete or"
            " independent acceptance exists."
        ),
        "## Do not repeat": (
            "Never rerun the historical PID controller or the one-shot cl"
            "eanup receipt. Do not restart Docker/applications, alter glo"
            "bal settings/other chats, rewrite CP0001/CP0002, prune globa"
            "l resources, delete ambiguous targets, narrow mandatory memb"
            "ership or silently accept/rebaseline the original external t"
            "ransition."
        ),
        "## Required next action": common["resume"],
        "## Exact continuation sequence": (
            "Read canonical intake, LATEST and this complete checkpoint; "
            "validate and compare Git/STATE. Resolve the explicitly named"
            " external factual question before changing the frozen enviro"
            "nment reference. Create a new separately receipted disposabl"
            "e phase rather than replacing/reusing the cleaned ownership "
            "receipt, then complete every ordered control and seal before"
            " commissioning a history-free auditor."
        ),
        "## Validation commands": (
            "Use record_command.py with explicit current checkpoint. The "
            "ledger validator itself needs no Docker: run python scripts/"
            "development-ledger/validate_checkpoint.py. Do not use run_ca"
            "usal.py --gate for this after disposal, since its old child_"
            "environment correctly refuses the cleaned scope."
        ),
        "## Stop conditions": (
            "Stop on unexpected Git divergence, unsafe output, unverified"
            " ownership, a new installation or authority requirement, or "
            "application/global-setting changes. Never issue readiness or"
            " milestone PASS while blocked or internal proof is incomplet"
            "e."
        ),
    }
    final = {
        "## Status": (
            "BLOCKED awaiting the external application-transition confirm"
            "ation. Scoped private disposal is complete. No Gate7 seal or"
            " M2 verdict is issued."
        ),
        "## Environment": (
            "E:/iacode, Windows/PowerShell, host Docker29.8.1/Compose5.5."
            "1. The private Buildx instance and config have been removed;"
            " existing applications remain running. No Docker/application"
            " restart was performed."
        ),
        "## Tool / Model / Effort": (
            "Codex desktop / OpenAI. Exact active desktop model/effort/ve"
            "rsion are not exposed. No new independent auditor model turn"
            " has started."
        ),
        "## Deliverables": common["completed"],
        "## Files Created": (
            "See FILES.json for causal/raw observations, immutable preima"
            "ges, structural ADRs, private ownership/cleanup and divergen"
            "ce receipts, and current checkpoint reports. Evidence is ret"
            "ained intentionally, not treated as disposable garbage."
        ),
        "## Files Modified": (
            "See FILES.json for the current authorized Gate7 code/tests, "
            "generic evidence transport rules, lesson/guardrail registrie"
            "s, approved one-location old-report prose repair and working"
            " checkpoint pointer. No other project or global configuratio"
            "n was edited."
        ),
        "## Validation": (
            "Current static and full lint pass at67c1c0fa; original-byte "
            "controls pass. The private cleanup component passes with eve"
            "ry removal producer exit0 and no remaining claimed disposabl"
            "e resource/cache/config. Its overall original-baseline resul"
            "t remains FAIL, not relabeled. Final canonical bookkeeping v"
            "alidation must report its actual result; this report never p"
            "redicts its exit."
        ),
        "## Tests": common["tests"],
        "## Red Team": (
            "Registered M2-RT-01 has actual local old/current replay regr"
            "ession evidence, but the complete fresh post-Green-Keeper/DC"
            "V internal Red Team, closure mirror and later independent Re"
            "d Team remain unexecuted."
        ),
        "## Known Risks": common["divergence"] + " " + common["scope"],
        "## Remaining Work": common["pending"] + " " + common["resume"],
        "## Handoff Readiness": (
            "A truthful resumable BLOCKED checkpoint only, not READY_FOR_"
            "REVIEW. CP0001 remains the last immutable valid seal; curren"
            "t corrected code is not offered as approved or independently"
            " audited."
        ),
        "## Next Gate": (
            "Remain at Gate7. Gate8 is not authorized and has not been st"
            "arted. Independent M2 acceptance remains a later boundary."
        ),
        "## Evidence": (
            "COMMANDS.jsonl; OWNED-RESOURCE-CLEANUP.json; OWNED-DISPOSAL-"
            "SUMMARY.json; RESOURCE-DIVERGENCE-0001.json; environment-pre"
            "servation/run-0002.json; lint/run-0008 and staticAnalysis/ru"
            "n-0006 under quality-attempts; byte-transport-attempts contr"
            "ols/index; dependency-cleanup controls; published-green-keep"
            "er/run-0001 original cancellation and cleanup facts."
        ),
    }
    synchronize(ROOT, CHECKPOINT)
    state = load_json(CHECKPOINT / "STATE.json")
    state.update(
        status="BLOCKED", blockedBy=[BLOCKER], nextAllowedAction=NEXT, updatedAt=now, dirty=True
    )
    write_json(CHECKPOINT / "STATE.json", state)
    metadata = load_json(CHECKPOINT / "RUN-METADATA.json")
    metadata["finishedAt"] = utc_now()
    write_json(CHECKPOINT / "RUN-METADATA.json", metadata)
    (CHECKPOINT / "STATUS.md").write_text("# Status\n\nBLOCKED\n", encoding="utf-8", newline="\n")
    (CHECKPOINT / "HANDOFF.md").write_text(
        render(
            "Handoff",
            HANDOFF_HEADINGS,
            handoff,
            "Current Gate: GATE-7\nCurrent Status: BLOCKED\n\n",
        ),
        encoding="utf-8",
        newline="\n",
    )
    (CHECKPOINT / "FINAL-REPORT.md").write_text(
        render("Scoped disposal and blocked corrective report", FINAL_REPORT_HEADINGS, final),
        encoding="utf-8",
        newline="\n",
    )
    (CHECKPOINT / "NEXT.md").write_text(
        "# Next\n\n## Required next action\n\n" + NEXT + "\n", encoding="utf-8", newline="\n"
    )
    (CHECKPOINT / "RISKS.md").write_text(
        "# Risks\n\n"
        + common["divergence"]
        + "\n\n"
        + common["pending"]
        + "\n\n"
        + common["scope"]
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    (CHECKPOINT / "DIVERGENCE.md").write_text(
        "# Docker resource observation divergence — not Git reconciliation\n\n"
        + common["divergence"]
        + (
            "\n\nThe source Git branch/HEAD did not unexpectedly change; th"
            "is is a separately retained shared-environment observation. "
            "No baseline or other project has been repaired or silently r"
            "ewritten.\n"
        ),
        encoding="utf-8",
        newline="\n",
    )
    owner = load_json(CHECKPOINT / "OWNER-REQUIREMENTS.json")
    for row in owner["requirements"]:
        if row["ownerRequirement"].startswith("Remove all verified task-owned"):
            row.update(
                status="COMPLETE",
                evidence=["OWNED-RESOURCE-CLEANUP.json", "OWNED-DISPOSAL-SUMMARY.json"],
                notes=(
                    "Private disposal is actually complete and current applicatio"
                    "ns were unchanged during it. The original external transitio"
                    "n comparison remains failed and is not an M2 approval."
                ),
            )
    write_json(CHECKPOINT / "OWNER-REQUIREMENTS.json", owner)
    write_json(
        CHECKPOINT / "ACTIVE-VALIDATION.json",
        {
            "recordedAt": now,
            "kind": "TRANSIENT_OPERATOR_RESUME_MARKER_NOT_ACCEPTANCE",
            "sourceFingerprint": scope_fingerprint(ROOT),
            "nativeToolSessions": [],
            "cleanup": "COMPLETED_PRIVATE_RESOURCES_ABSENT",
            "ownedBuilderReceipt": "OWNED-DOCKER-SCOPE.json",
            "independentAuditorStarted": False,
            "gate8Authorized": False,
            "blocker": BLOCKER,
            "warning": (
                "Historical process IDs may be reused; no old PID controller "
                "or cleanup receipt may be replayed."
            ),
        },
    )
    steps = load_json(CHECKPOINT / "STEPS.json")
    for row in steps["steps"]:
        if row["stepId"] == "G7-S01":
            row["functionalProof"] = (
                common["completed"]
                + " Final deployed capability and full functional proof remain pending."
            )
            row["evidence"] += ["OWNED-RESOURCE-CLEANUP.json", "RESOURCE-DIVERGENCE-0001.json"]
        elif row["stepId"] == "G7-S02":
            row["functionalProof"] = common["tests"] + (
                " Full ordered controls remain pending while the named external fact is unresolved."
            )
        elif row["stepId"] == "G7-S03":
            row["functionalProof"] = (
                "Observed scoped disposal completed, but no canonical seal or"
                " independent audit is claimed; runtime-v1 remains an IN_PROG"
                "RESS publication only."
            )
            row["evidence"] = ["OWNED-DISPOSAL-SUMMARY.json", "RESOURCE-DIVERGENCE-0001.json"]
    write_json(CHECKPOINT / "STEPS.json", steps)
    latest = (
        "# Latest Checkpoint\n\nCheckpoint: `docs/checkpoints/GATE-7-CP"
        "-0003`\n\nBLOCKED corrective work; scoped private disposal is "
        "complete. The original shared-Docker comparison records two "
        "replacements in E:/esteira_videos, not silently reconciled; "
        "owner confirmation is pending. No other-project cleanup, glo"
        "bal setting change, application restart, Gate8 or new audito"
        "r turn occurred. CP0001 remains the immutable last valid sea"
        "l. Read the complete current handoff and RESOURCE-DIVERGENCE"
        "-0001.json before resuming; full controls and independent M2"
        " closure remain pending.\n"
    )
    (ROOT / "docs/checkpoints/LATEST.md").write_text(latest, encoding="utf-8", newline="\n")
    print(
        json.dumps(
            {
                "scopedDisposal": "PASS",
                "imagesRemoved": len(removed),
                "checkpointStatus": "BLOCKED",
                "independentM2": "PENDING",
                "gate8": "NOT_STARTED",
            }
        )
    )
    return 0


if __name__ == "__main__":
    from ledger_common import use_utf8_stdout

    use_utf8_stdout()
    raise SystemExit(main())
