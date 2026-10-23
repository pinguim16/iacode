"""Claim exact non-baseline image outputs from captured private-builder history; no deletion."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

from current_resources import child_environment, current_scope_path
from owned_docker_scope import snapshot

sys.path.insert(
    0, str(Path(__file__).resolve().parents[1].parents[2] / "scripts/development-ledger")
)

from audit_runner_bridge import Job, cleanup_plan, regular, run_owned
from ledger_common import find_secrets, load_json, utc_now, write_json
from native_process import WindowsJob

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]


def captured(row):
    fact = row["streams"]["stdout"]
    path = CHECKPOINT / fact["path"]
    regular(path, CHECKPOINT)
    raw = path.read_bytes()
    if (
        row["exitCode"] != 0
        or row["execution"]["cleanup"]["result"] != "PASS"
        or fact["refused"]
        or len(raw) != fact["bytes"]
        or hashlib.sha256(raw).hexdigest() != fact["sha256"]
        or find_secrets(raw.decode("utf-8", errors="strict"))
    ):
        raise ValueError("EXACT_SAFE_SUCCESSFUL_PRIVATE_HISTORY_REQUIRED")
    return json.loads(raw), fact


def measured_namespaces():
    """Only exact byte-bound reports from actual recorded producers may extend scope."""
    from run_full_verification import captured_manifest, captured_original_bytes

    kinds = {
        "desktop-e2e.json": "desktop",
        "experience-store-e2e.json": "experience",
        "knowledge-engine-e2e.json": "knowledge",
    }
    measured = []
    for path in sorted((CHECKPOINT / "attempts").glob("FULL-PRODUCER-*-MANIFEST.json")):
        document = captured_manifest(path)
        for row in document["reports"]:
            kind = kinds.get(row["producerName"])
            if kind:
                value = json.loads(captured_original_bytes(path.parent, row))
                if value["subjectCommit"] != document["subjectCommit"]:
                    raise ValueError("ORIGINAL_FULL_NAMESPACE_SUBJECT_MISMATCH")
                measured.append((kind, value))
    for path in sorted((CHECKPOINT / "causal-attempts/live-stages").glob("*/run-*/RECEIPT.json")):
        regular(path, CHECKPOINT)
        receipt = load_json(path)
        kind = receipt["scenario"]
        if kind == "native":
            continue  # This explicitly Docker-free observation cannot claim an image namespace.
        if kind not in {"desktop", "experience"}:
            raise ValueError("UNKNOWN_LIVE_DIAGNOSTIC_NAMESPACE")
        report = path.parent / "ORIGINAL-PRODUCER.json"
        regular(report, CHECKPOINT)
        raw = report.read_bytes()
        if (
            receipt["kind"] != "TARGETED_UNCHANGED_ACTUAL_LIVE_DIAGNOSTIC_NOT_WHOLE_ACCEPTANCE"
            or receipt["originalReportSha256"] != hashlib.sha256(raw).hexdigest()
            or receipt["execution"]["cleanup"]["result"] != "PASS"
            or find_secrets(raw.decode("utf-8", errors="strict"))
        ):
            raise ValueError("ACTUAL_BOUND_LIVE_DIAGNOSTIC_REQUIRED")
        measured.append((kind, json.loads(raw)))
    result = {}
    for kind, value in measured:
        project = value["composeProject"]
        commit = value["subjectCommit"]
        if (
            re.fullmatch("iacode-" + kind + "-[a-f0-9]{12}", project) is None
            or re.fullmatch("[a-f0-9]{40}", commit) is None
        ):
            raise ValueError("ORIGINAL_PRODUCER_NAMESPACE_MISMATCH")
        if project in result and result[project] != commit:
            raise ValueError("AMBIGUOUS_PRODUCER_NAMESPACE_SUBJECT")
        result[project] = commit
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--claim", action="store_true")
    parser.add_argument("--remove-unused-images", action="store_true")
    args = parser.parse_args()
    scope_path = current_scope_path()
    scope = load_json(scope_path)
    if scope["status"] != "ACTIVE":
        raise ValueError("ACTIVE_PRIVATE_PHASE_REQUIRED")
    original_scope = scope_path.read_bytes()
    before_ids = {row["id"] for row in scope["before"]["images"]}
    current = snapshot()
    namespaces = set(scope["registeredProjects"])
    measured = measured_namespaces()
    namespaces.update(measured)
    outputs = {}
    for directory in sorted((CHECKPOINT / "resource-observations/build-history").glob("run-*")):
        receipt = load_json(directory / "RECEIPT.json")
        if receipt["builder"] != scope["builder"]:
            continue
        if receipt["result"] != "CAPTURED_NOT_OWNERSHIP_CLAIM_OR_ACCEPTANCE":
            continue
        for row in receipt["observations"]:
            if "inspect" not in row["arguments"]:
                continue
            document, fact = captured(row)
            if (
                document.get("Status") != "completed"
                or document.get("VCSRepository") != "https://github.com/pinguim16/iacode.git"
                or re.fullmatch("[0-9a-f]{40}", document.get("VCSRevision", "")) is None
            ):
                continue
            dockerfile = document.get("Dockerfile", "").replace("\\", "/")
            if dockerfile not in {
                "apps/web/Dockerfile",
                "apps/api/Dockerfile",
                "services/orchestrator/Dockerfile",
                "services/evaluator/Dockerfile",
                "services/sandbox/Dockerfile",
            }:
                continue
            labels = {row["Name"]: row["Value"] for row in document.get("Labels", [])}
            project = labels.get("com.docker.compose.project")
            toolchain = dockerfile == "apps/web/Dockerfile" and document.get("Target") == "builder"
            if project not in namespaces and not toolchain:
                continue
            if project in measured and measured[project] != document["VCSRevision"]:
                raise ValueError("PRIVATE_OUTPUT_AND_ORIGINAL_PRODUCER_SUBJECT_DIFFER")
            for attachment in document.get("Attachments", []):
                if attachment["Type"] != "application/vnd.oci.image.manifest.v1+json":
                    continue
                identifier = attachment["Digest"]
                if (
                    re.fullmatch("sha256:[a-f0-9]{64}", identifier) is None
                    or identifier in before_ids
                ):
                    continue
                outputs.setdefault(identifier, []).append(
                    {
                        "history": fact["path"],
                        "sha256": fact["sha256"],
                        "project": project,
                        "toolchain": toolchain,
                        "revision": document["VCSRevision"],
                    }
                )
    claims = []
    for image in current["images"]:
        proofs = outputs.get(image["id"], [])
        if not proofs:
            continue
        owned_namespaces = {row["project"] for row in proofs if row["project"]}
        prefixes = tuple(name + "/" for name in owned_namespaces)
        allowed = [
            tag
            for tag in image["tags"]
            if (prefixes and tag.startswith(prefixes))
            or (tag == "iacode/web-toolchain:0.1.0" and any(row["toolchain"] for row in proofs))
        ]
        repositories = [tag.rsplit(":", 1)[0] for tag in allowed]
        claims.append(
            {
                "id": image["id"],
                "allowedTags": allowed,
                "allowedDigestRepositories": repositories,
                "evidence": proofs[0]["history"],
                "evidenceSha256": proofs[0]["sha256"],
                "builder": scope["builder"],
                "proofs": proofs,
            }
        )
    existing = {row["id"]: row for row in scope["claimedAuxiliaryImages"]}
    for row in claims:
        existing[row["id"]] = row
    scope["claimedAuxiliaryImages"] = list(existing.values())
    for row in claims:
        tag = "iacode/web-toolchain:0.1.0"
        if tag not in row["allowedTags"]:
            continue
        baseline = [image["id"] for image in scope["before"]["images"] if tag in image["tags"]]
        if len(baseline) != 1:
            raise ValueError("EXACT_BASELINE_TOOLCHAIN_TAG_REQUIRED")
        previous = [item for item in scope.get("tagRestorations", []) if item["tag"] == tag]
        if any(item["baselineImageId"] != baseline[0] for item in previous):
            raise ValueError("EXACT_BASELINE_TAG_RESTORATION_CHANGED")
        produced = {identifier for item in previous for identifier in item["producedImageIds"]}
        produced.update(
            item["id"] for item in claims if any(proof["toolchain"] for proof in item["proofs"])
        )
        scope["tagRestorations"] = [
            item for item in scope.get("tagRestorations", []) if item["tag"] != tag
        ] + [
            {
                "tag": tag,
                "baselineImageId": baseline[0],
                "producedImageIds": sorted(produced),
                "evidence": row["evidence"],
                "requiredBeforeOwnedImageRemoval": True,
            }
        ]
    plan = cleanup_plan(scope, current)
    directory = CHECKPOINT / "cleanup-previews/private-history"
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / f"run-{len(list(directory.glob('run-*.json'))) + 1:04d}.json"
    write_json(
        target,
        {
            "observedAt": utc_now(),
            "kind": "EXACT_PRIVATE_OUTPUT_CLAIMS_NOT_DISPOSAL",
            "phase": scope["phase"],
            "builder": scope["builder"],
            "scopeBeforeSha256": hashlib.sha256(original_scope).hexdigest(),
            "claims": claims,
            "plan": plan,
            "claimsWritten": args.claim or args.remove_unused_images,
            "resourcesDeleted": False,
        },
    )
    if args.claim or args.remove_unused_images:
        if scope_path.read_bytes() != original_scope:
            raise ValueError("ACTIVE_SCOPE_CHANGED_BEFORE_CLAIM")
        write_json(scope_path, scope)
    if args.remove_unused_images:
        images = {row["id"]: row for row in current["images"]}
        candidates = [
            identifier
            for identifier in plan["images"]
            if identifier not in before_ids
            and identifier != scope["builderOwnership"]["imageId"]
            and "iacode/web-toolchain:0.1.0" not in images[identifier]["tags"]
            and not any(
                tag.startswith(scope["inheritedOwnedProject"] + "/")
                for tag in images[identifier]["tags"]
            )
        ]
        receipt = {
            "startedAt": utc_now(),
            "kind": "EXACT_UNUSED_PRIVATE_IMAGES_ONLY",
            "ownershipPreview": target.relative_to(CHECKPOINT).as_posix(),
            "candidates": candidates,
            "executions": [],
            "result": "FAIL",
            "builderAndNeededCacheRetained": True,
        }
        output = target.with_name(target.stem + "-removal.json")
        write_json(output, receipt)
        environment = child_environment()
        for identifier in candidates:
            execution, _streams = run_owned(
                Job(("docker", "image", "rm", identifier), 60),
                ROOT,
                environment,
                find_secrets,
                WindowsJob,
            )
            receipt["executions"].append({"imageId": identifier, **execution})
            write_json(output, receipt)
        after = snapshot()
        remaining_ids = {row["id"] for row in after["images"]}
        after_containers = {row["id"]: row for row in after["containers"]}
        receipt.update(
            {
                "finishedAt": utc_now(),
                "remainingCandidates": [
                    identifier for identifier in candidates if identifier in remaining_ids
                ],
                "removedImages": [
                    identifier for identifier in candidates if identifier not in remaining_ids
                ],
                "containerObservationsUnchanged": all(
                    after_containers.get(row["id"]) == row for row in current["containers"]
                ),
                "baselineImagesRemovedByTheseCommands": sorted(set(candidates) & before_ids),
                "after": after,
            }
        )
        valid = all(
            row["producer"]["status"] == "COMPLETED"
            and row["producer"]["exitCode"] == 0
            and row["cleanup"]["result"] == "PASS"
            and not any(row["producer"][name]["refusal"] for name in ("stdout", "stderr"))
            for row in receipt["executions"]
        )
        receipt["result"] = (
            "PASS"
            if valid
            and not receipt["remainingCandidates"]
            and receipt["containerObservationsUnchanged"]
            else "FAIL"
        )
        write_json(output, receipt)
        print(
            json.dumps(
                {
                    "result": receipt["result"],
                    "removedImages": len(receipt["removedImages"]),
                    "remainingCandidates": len(receipt["remainingCandidates"]),
                    "containerObservationsUnchanged": receipt["containerObservationsUnchanged"],
                    "finalDisposal": False,
                    "observation": output.relative_to(ROOT).as_posix(),
                }
            )
        )
        return int(receipt["result"] != "PASS")
    print(
        json.dumps(
            {
                "claims": len(claims),
                "removableImages": len(plan["images"]),
                "preservedShared": len(plan["preservedShared"]),
                "claimsWritten": args.claim,
                "resourcesDeleted": False,
                "observation": target.relative_to(ROOT).as_posix(),
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
