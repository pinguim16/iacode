"""Inspect ownership and isolate build cache; never a global cleanup command."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import uuid
import shutil
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))
sys.path.insert(0, str(ROOT / "scripts/iacode"))
from ledger_common import find_secrets, load_json, utc_now, write_json
from audit_runner_bridge import cleanup_plan
from client_checks import _safe_stream

SCOPE = CHECKPOINT / "OWNED-DOCKER-SCOPE.json"
DOCKER_CONFIG = Path("C:/Users/cesar/.docker/config.json")
ENDPOINT = "npipe:////./pipe/dockerDesktopLinuxEngine"


def docker(arguments, *, environment=None):
    if environment is None:
        environment = {**os.environ, "DOCKER_HOST": ENDPOINT, "DOCKER_CONTEXT": ""}
    completed = subprocess.run(["docker", *arguments], cwd=ROOT, env=environment,
                               capture_output=True, timeout=60, check=False)
    if completed.returncode:
        # Do not publish arbitrary engine diagnostics or credentials.
        raise RuntimeError("DOCKER_QUERY_FAILED:" + str(completed.returncode))
    return completed.stdout.decode("utf-8", errors="strict")


def configuration_hash():
    return hashlib.sha256(DOCKER_CONFIG.read_bytes()).hexdigest() if DOCKER_CONFIG.exists() else None


def snapshot():
    containers, images, networks, volumes = [], [], [], []
    for kind, rows in (("container", containers), ("image", images),
                       ("network", networks), ("volume", volumes)):
        arguments = [kind, "ls", "--quiet"]
        if kind in ("container", "image"):
            arguments.append("--all")
        if kind == "image":
            arguments.append("--no-trunc")
        names = sorted(set(docker(arguments).splitlines()))
        for offset in range(0, len(names), 64):
            documents = json.loads(docker([kind, "inspect", *names[offset:offset + 64]]))
            for value in documents:
                if kind == "container":
                    rows.append({"id": value["Id"], "name": value["Name"].lstrip("/"),
                                 "image": value["Image"], "running": value["State"]["Running"],
                                 "startedAt": value["State"]["StartedAt"],
                                 "restartCount": value["RestartCount"],
                                 "project": (value["Config"].get("Labels") or {}).get("com.docker.compose.project")})
                elif kind == "image":
                    rows.append({"id": value["Id"], "tags": value.get("RepoTags") or [],
                                 "digests": value.get("RepoDigests") or [], "size": value["Size"],
                                 "project": (value.get("Config", {}).get("Labels") or {}).get("com.docker.compose.project")})
                else:
                    rows.append({"id": value.get("Id", value["Name"]), "name": value["Name"],
                                 "project": (value.get("Labels") or {}).get("com.docker.compose.project")})
    result = {"observedAt": utc_now(), "containers": containers, "images": images,
              "networks": networks, "volumes": volumes, "dockerConfigHash": configuration_hash()}
    if find_secrets(json.dumps(result)):
        raise ValueError("UNSAFE_DOCKER_INVENTORY")
    return result


def child_environment():
    scope = load_json(SCOPE)
    if scope["status"] != "ACTIVE":
        raise ValueError("OWNED_SCOPE_NOT_ACTIVE")
    directory = Path(scope["privateBuildxConfig"])
    if (directory.parent != Path(tempfile.gettempdir()).resolve()
            or not directory.name.startswith("iacode-m2cp3-buildx-")
            or directory.is_symlink() or directory.is_junction()
            or directory.resolve() != directory or not directory.is_dir()):
        raise ValueError("PRIVATE_BUILDX_ROOT_CHANGED")
    return {**os.environ, "DOCKER_HOST": ENDPOINT, "DOCKER_CONTEXT": "",
            "BUILDX_CONFIG": str(directory), "BUILDX_BUILDER": scope["builder"],
            "DOCKER_BUILDKIT": "1", "PYTHONIOENCODING": "utf-8"}


def prepare():
    if SCOPE.exists():
        raise ValueError("DO_NOT_REPLACE_EXISTING_OWNERSHIP_RECEIPT")
    before = snapshot()
    directory = Path(tempfile.mkdtemp(prefix="iacode-m2cp3-buildx-")).resolve()
    builder = "iacode-m2cp3-" + uuid.uuid4().hex
    scope = {"schemaVersion": "1.0.0", "status": "CREATING", "createdAt": utc_now(),
             "builder": builder, "privateBuildxConfig": str(directory),
             "engineEndpoint": ENDPOINT, "before": before,
             "inheritedOwnedProject": "iacode-m2cp3-aa560f386fe44e21876d0e3ccfdfef31",
             "registeredProjects": ["iacode-m2cp3-aa560f386fe44e21876d0e3ccfdfef31"],
             "claimedAuxiliaryImages": []}
    write_json(SCOPE, scope)
    environment = {**os.environ, "DOCKER_HOST": ENDPOINT, "DOCKER_CONTEXT": "",
                   "BUILDX_CONFIG": str(directory)}
    try:
        created = docker(["buildx", "create", "--name", builder, "--driver", "docker-container",
                          "--driver-opt", "default-load=true", "--driver-opt", "restart-policy=no"],
                         environment=environment).strip()
        if created != builder:
            raise ValueError("BUILDER_IDENTITY_MISMATCH")
        scope["status"] = "ACTIVE"
        scope["createdBuilderOutput"] = created
    except Exception as error:
        scope.update(status="CREATE_FAILED", errorType=type(error).__name__)
        raise
    finally:
        scope["dockerConfigUnchanged"] = before["dockerConfigHash"] == configuration_hash()
        write_json(SCOPE, scope)
    if not scope["dockerConfigUnchanged"]:
        raise ValueError("UNEXPECTED_GLOBAL_DOCKER_CONFIG_CHANGE")
    print(json.dumps({"status": scope["status"], "builder": builder,
                      "baselineContainers": len(before["containers"]),
                      "baselineImages": len(before["images"]),
                      "dockerConfigUnchanged": scope["dockerConfigUnchanged"]}))


def capture_builder_ownership():
    scope = load_json(SCOPE)
    environment = child_environment()
    name = "buildx_buildkit_" + scope["builder"] + "0"
    names = docker(["container", "ls", "--all", "--filter", "name=^/" + name + "$", "--quiet"],
                   environment=environment).splitlines()
    if len(names) != 1:
        raise ValueError("EXACT_OWNED_BUILDER_CONTAINER_REQUIRED")
    document = json.loads(docker(["container", "inspect", names[0]], environment=environment))[0]
    if (document["Name"] != "/" + name
            or document["Id"] in {row["id"] for row in scope["before"]["containers"]}
            or document["Config"]["Image"] != "moby/buildkit:buildx-stable-1"):
        raise ValueError("BUILDER_PROVENANCE_MISMATCH")
    evidence = {"observedAt": utc_now(), "name": name, "id": document["Id"],
                "imageId": document["Image"], "imageReference": document["Config"]["Image"],
                "source": "Exact private registered Buildx builder; container absent from baseline"}
    caches = [row["Name"] for row in document["Mounts"]
              if row["Type"] == "volume" and row["Destination"] == "/var/lib/buildkit"]
    if (caches != [name + "_state"]
            or any(row["name"] in caches for row in scope["before"]["volumes"])):
        raise ValueError("EXACT_NEW_PRIVATE_BUILDER_CACHE_REQUIRED")
    evidence["cacheVolumes"] = caches
    evidence["cacheOwnership"] = "Actual exact builder Mounts; absent from baseline; no global cache claim"
    scope.setdefault("registeredProjects", [scope["inheritedOwnedProject"]])
    scope["builderOwnership"] = evidence
    if document["Image"] not in {row["id"] for row in scope["before"]["images"]}:
        claims = scope.setdefault("claimedAuxiliaryImages", [])
        claim = next((row for row in claims if row["id"] == document["Image"]), None)
        if claim is None:
            claim = {"id": document["Image"], "evidence": "OWNED-DOCKER-SCOPE.json builderOwnership"}
            claims.append(claim)
        claim.update(allowedTags=[document["Config"]["Image"]], allowedDigestRepositories=["moby/buildkit"])
    write_json(SCOPE, scope)
    print(json.dumps(evidence))


def cleanup():
    output = CHECKPOINT / "OWNED-RESOURCE-CLEANUP.json"
    if output.exists():
        # Refuse before the first effect, not in finally after replaying removals.
        raise ValueError("Prior cleanup observation exists; explicit recorded recovery required")
    scope = load_json(SCOPE)
    environment = child_environment()
    current = snapshot()
    plan = cleanup_plan(scope, current)
    directory = Path(scope["privateBuildxConfig"])
    builder = scope["builder"]
    if not builder.startswith("iacode-m2cp3-") or builder in {row["name"] for row in scope["before"]["containers"]}:
        raise ValueError("BUILDER_OWNER_MISMATCH")
    builder_owner = scope.get("builderOwnership", {})
    caches = builder_owner.get("cacheVolumes", [])
    if (len(caches) != len(set(caches))
            or any(name != "buildx_buildkit_" + builder + "0_state" for name in caches)
            or any(row["name"] in caches for row in scope["before"]["volumes"])
            or caches and not any(row["id"] == builder_owner.get("id")
                                 and row["name"] == builder_owner.get("name")
                                 and row["image"] == builder_owner.get("imageId")
                                 for row in current["containers"])):
        raise ValueError("PRIVATE_CACHE_OWNERSHIP_CHANGED")
    for cache in caches:
        consumers = set(docker(["container", "ls", "--all", "--quiet", "--no-trunc",
                                "--filter", "volume=" + cache], environment=environment).splitlines())
        if consumers != {builder_owner["id"]}:
            raise ValueError("PRIVATE_CACHE_HAS_UNVERIFIED_OR_EXTERNAL_CONSUMERS")
    receipt = {"startedAt": utc_now(), "before": current, "plan": plan,
               "ownedBuilderCacheVolumes": caches, "commands": [], "result": "FAIL"}

    def remove(arguments):
        status, code, stdout, stderr = "COMPLETED", None, None, None
        try:
            completed = subprocess.run(["docker", *arguments], cwd=ROOT, env=environment,
                                       capture_output=True, timeout=60, check=False)
            code, stdout, stderr = completed.returncode, completed.stdout, completed.stderr
        except subprocess.TimeoutExpired as error:
            status, stdout, stderr = "TIMEOUT", error.stdout, error.stderr
        except OSError:
            status = "LAUNCH_ERROR"
        # Canonical corrected observation boundary, before later removal or postprocessing.
        streams = {name: _safe_stream(raw) for name, raw in (("stdout", stdout), ("stderr", stderr))}
        receipt["commands"].append({"arguments": ["docker", *arguments], "status": status,
                                    "exitCode": code, "streams": streams})
        return status == "COMPLETED" and code == 0 and not any(row["refusal"] for row in streams.values())

    # No prune, broad ID delta, forced image removal, or deletion of shared resources.
    try:
        # A canonical build has a fixed toolchain tag. Restore its original target,
        # but only while that tag still points at a proven task-produced replacement.
        # Never overwrite an unrelated concurrent tag change.
        success = True
        for restore in scope.get("tagRestorations", []):
            baseline = restore["baselineImageId"]
            tag = restore["tag"]
            expected = {row["id"] for row in scope["before"]["images"] if tag in row["tags"]}
            observed = {row["id"] for row in current["images"] if tag in row["tags"]}
            if (expected != {baseline} or len(observed) != 1
                    or not observed <= {baseline, *restore["producedImageIds"]}):
                receipt.setdefault("restorationConflicts", []).append(tag)
                success = False
                continue
            if observed != {baseline}:
                success = remove(["image", "tag", baseline, tag]) and success
        if not success:
            raise ValueError("Refusing cleanup after an unverified tag restoration")
        success = remove(["buildx", "rm", builder])
        for identifier in plan["containers"]:
            success = remove(["container", "rm", "--force", identifier]) and success
        for identifier in plan["networks"]:
            success = remove(["network", "rm", identifier]) and success
        for identifier in plan["volumes"]:
            success = remove(["volume", "rm", identifier]) and success
        # Re-evaluate after removing dependencies. The original conservative plan rightly
        # preserves the image still consumed by the private builder before buildx rm.
        # Never convert that initial preservation into an orphan left behind afterwards.
        post_dependencies = snapshot()
        for identifier in caches:
            if any(row["name"] == identifier for row in post_dependencies["volumes"]):
                # An exact observed private cache only; Docker refuses any new consumer.
                success = remove(["volume", "rm", identifier]) and success
        image_plan = cleanup_plan(scope, post_dependencies)
        receipt["postDependencyImagePlan"] = image_plan
        for identifier in image_plan["images"]:
            # No --force: Docker itself refuses an image still in use or ambiguously tagged.
            success = remove(["image", "rm", identifier]) and success
        after = snapshot()
        receipt["after"] = after
        receipt["ownedBuilderCacheVolumesRemaining"] = [name for name in caches
            if any(row["name"] == name for row in after["volumes"])]
        baseline_apps = {row["id"]: row for row in scope["before"]["containers"]
                         if row.get("project") not in set(scope.get("registeredProjects", [scope["inheritedOwnedProject"]]))}
        now_apps = {row["id"]: row for row in after["containers"]}
        receipt["unrelatedApplicationsUnchanged"] = all(now_apps.get(key) == value for key, value in baseline_apps.items())
        immediate_apps = {row["id"]: row for row in current["containers"]
            if row.get("project") not in set(scope.get("registeredProjects", [scope["inheritedOwnedProject"]]))
            and row["id"] != builder_owner.get("id")}
        receipt["unrelatedApplicationsUnchangedDuringCleanup"] = all(
            now_apps.get(key) == value for key, value in immediate_apps.items())
        receipt["remainingOwned"] = cleanup_plan(scope, after)
        remaining = receipt["remainingOwned"]
        # External application changes do not authorize touching those applications and must
        # not leave an otherwise disposable private config behind. Keep the original full
        # baseline comparison false and the overall result failed; report disposal separately.
        own_clean = (success and not any(remaining[key] for key in ("containers", "networks", "volumes", "images"))
                   and not receipt["ownedBuilderCacheVolumesRemaining"]
                   and scope["before"]["dockerConfigHash"] == configuration_hash())
        receipt["ownedResourceCleanupResult"] = "PASS" if own_clean else "FAIL"
        success = (own_clean and receipt["unrelatedApplicationsUnchanged"]
                   and receipt["unrelatedApplicationsUnchangedDuringCleanup"])
        # Revalidate the absolute private target immediately before recursive deletion.
        child_environment()
        if any(path.is_symlink() or path.is_junction() for path in directory.rglob("*")):
            raise ValueError("REDIRECTED_PRIVATE_CONFIG")
        if own_clean:
            shutil.rmtree(directory)
        receipt["privateBuildxConfigRemoved"] = not directory.exists()
        if not own_clean:
            receipt["privateBuildxConfigRetainedForRecovery"] = True
        receipt["result"] = "PASS" if success and receipt["privateBuildxConfigRemoved"] else "FAIL"
        scope["status"] = ("CLEANED" if receipt["result"] == "PASS" else
                           "CLEANED_EXTERNAL_OBSERVATION_CHANGED" if own_clean and receipt["privateBuildxConfigRemoved"]
                           else "CLEANUP_FAILED")
    finally:
        receipt["finishedAt"] = utc_now()
        write_json(output, receipt)
        write_json(SCOPE, scope)
    final_plan = receipt.get("postDependencyImagePlan", plan)
    print(json.dumps({"result": receipt["result"], "removedImages": len(final_plan["images"]),
                      "sharedResourcesPreserved": len(final_plan["preservedShared"]),
                      "unrelatedApplicationsUnchanged": receipt.get("unrelatedApplicationsUnchanged")}))
    return int(receipt["result"] != "PASS")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("prepare", "snapshot", "cleanup", "capture-builder"))
    options = parser.parse_args()
    if options.action == "prepare":
        prepare()
    elif options.action == "cleanup":
        return cleanup()
    elif options.action == "capture-builder":
        capture_builder_ownership()
    else:
        folder = CHECKPOINT / "resource-observations"
        folder.mkdir(parents=True, exist_ok=True)
        index = len(list(folder.glob("run-*.json"))) + 1
        value = snapshot()
        write_json(folder / f"run-{index:04d}.json", value)
        print(json.dumps({kind: len(value[kind]) for kind in ("containers", "images", "networks", "volumes")}))
    return 0


if __name__ == "__main__":
    from ledger_common import use_utf8_stdout
    use_utf8_stdout()
    raise SystemExit(main())
