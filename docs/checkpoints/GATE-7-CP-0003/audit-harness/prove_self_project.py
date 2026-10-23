"""Compare real evaluator project/check discovery on actual full and selected committed inputs."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import subprocess
import sys
import tarfile
import tempfile
import time
import uuid
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/iacode"))
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))


def inner(base):
    from iacode_evaluator.planner import build_plan
    from iacode_evaluator.policy import load_policy
    from iacode_evaluator.projects import detect_project

    profiles, policies, checks, inventories = {}, {}, {}, {}
    for label in ("full", "view"):
        started = time.monotonic()
        print(json.dumps({"stage": label + "-inventory-started"}), flush=True)
        directory = base / label
        inventory = {}
        with tarfile.open(base / (label + ".tar"), "r:") as archive:
            for member in archive:
                path = PurePosixPath(member.name)
                if (
                    not member.isfile()
                    or path.is_absolute()
                    or ".." in path.parts
                    or "\\" in member.name
                    or path.as_posix() != member.name
                    or member.name in inventory
                ):
                    raise ValueError("REGULAR_UNAMBIGUOUS_PACKED_INPUT_REQUIRED")
                with archive.extractfile(member) as stream:
                    raw = stream.read()
                if len(raw) != member.size:
                    raise ValueError("PACKED_INPUT_TRUNCATED")
                inventory[member.name] = raw
        if (
            inventory[".iacode/policies/quality-policy.json"]
            != (directory / ".iacode/policies/quality-policy.json").read_bytes()
        ):
            raise ValueError("SAME_ACTUAL_POLICY_BYTES_REQUIRED")
        print(
            json.dumps(
                {
                    "stage": label + "-inventory-read",
                    "files": len(inventory),
                    "durationMs": int((time.monotonic() - started) * 1000),
                }
            ),
            flush=True,
        )
        profile = detect_project(inventory)
        plan = build_plan(
            snapshot_id=label + "-actual-committed-inputs",
            snapshot_digest=hashlib.sha256(
                json.dumps(sorted(inventory), separators=(",", ":")).encode()
            ).hexdigest(),
            project=profile,
            registry=load_policy(directory / ".iacode/policies/quality-policy.json"),
            created_at=datetime(2026, 10, 22, tzinfo=UTC),
        )
        profiles[label] = {
            key: value
            for key, value in asdict(profile).items()
            if key not in {"source_paths", "digest"}
        }
        policies[label] = plan.policy.model_dump(mode="json")
        checks[label] = [check.model_dump(mode="json") for check in plan.checks]
        inventories[label] = inventory
    expected = {
        name: raw
        for name, raw in inventories["full"].items()
        if not name.startswith("docs/checkpoints/")
    }
    actual = dict(inventories["view"])
    sidecar = actual.pop(".iacode/SELF-QUALIFICATION-SOURCE.json")
    passed = (
        expected == actual
        and profiles["full"] == profiles["view"]
        and policies["full"] == policies["view"]
        and checks["full"] == checks["view"]
        and len(checks["view"]) > 0
    )
    report = {
        "kind": "ACTUAL_EVALUATOR_PROJECT_CHECK_EQUIVALENCE_NOT_LIVE_ACCEPTANCE",
        "result": "PASS" if passed else "FAIL",
        "selection": json.loads(sidecar),
        "allNonCheckpointBytesEqual": expected == actual,
        "projectProfiles": profiles,
        "policiesEqual": policies["full"] == policies["view"],
        "completeOrderedChecksEqual": checks["full"] == checks["view"],
        "completeOrderedChecks": checks,
        "snapshotLimitsChanged": False,
        "sourceInventoryAndProfileDigestsExpectedToDiffer": True,
        "fullRawBytes": sum(map(len, inventories["full"].values())),
        "viewRawBytes": sum(map(len, inventories["view"].values())),
    }
    print(json.dumps(report, sort_keys=True))
    return int(not passed)


def materialize_full(root, destination):
    from self_qualification_source import git_bytes

    commit = git_bytes(root, "rev-parse", "HEAD^{commit}").decode("ascii").strip()
    rows = {}
    for row in git_bytes(root, "ls-tree", "-r", "-l", "-z", commit).split(b"\0"):
        if not row:
            continue
        header, name_bytes = row.split(b"\t", 1)
        mode, kind, identifier, size = header.decode("ascii").split()
        name = name_bytes.decode("utf-8", errors="strict")
        path = PurePosixPath(name)
        if (
            mode not in {"100644", "100755"}
            or kind != "blob"
            or path.is_absolute()
            or ".." in path.parts
            or "\\" in name
            or path.as_posix() != name
            or name in rows
        ):
            raise ValueError("FULL_RAW_GIT_INPUT_MUST_BE_A_REGULAR_UNAMBIGUOUS_PATH")
        rows[name] = (identifier, int(size))
    sizes = dict(rows.values())
    identifiers = sorted(sizes)
    stream = io.BytesIO(
        git_bytes(
            root, "cat-file", "--batch", input_data=("\n".join(identifiers) + "\n").encode("ascii")
        )
    )
    objects = {}
    for identifier in identifiers:
        if stream.readline(256) != f"{identifier} blob {sizes[identifier]}\n".encode("ascii"):
            raise ValueError("FULL_OBJECT_HEADER_MISMATCH")
        raw = stream.read(sizes[identifier])
        actual = hashlib.sha1(
            b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw, usedforsecurity=False
        ).hexdigest()
        if len(raw) != sizes[identifier] or stream.read(1) != b"\n" or actual != identifier:
            raise ValueError("FULL_OBJECT_IDENTITY_MISMATCH")
        objects[identifier] = raw
    if stream.read(1):
        raise ValueError("FULL_OBJECT_BATCH_TRAILING_BYTES")
    destination.mkdir()
    for name, (identifier, _size) in rows.items():
        path = destination.joinpath(*PurePosixPath(name).parts)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("xb") as output:
            output.write(objects[identifier])
    return commit


def pack_actual_inputs(base, label):
    directory = base / label
    with tarfile.open(base / (label + ".tar"), "x:") as archive:
        for path in sorted(directory.rglob("*")):
            if not path.is_file():
                continue
            raw = path.read_bytes()
            member = tarfile.TarInfo(path.relative_to(directory).as_posix())
            member.size = len(raw)
            member.mode = 0o644
            archive.addfile(member, io.BytesIO(raw))


def remove_only_own_probe(name, environment):
    from audit_runner_bridge import Job, run_owned
    from current_resources import current_scope_path
    from ledger_common import find_secrets, load_json
    from native_process import WindowsJob

    if re.fullmatch("iacode-m2cp3-self-plan-[a-f0-9]{32}", name) is None:
        raise ValueError("EXACT_PRIVATE_PROBE_NAME_REQUIRED")

    def identities():
        result = subprocess.run(
            ["docker", "ps", "-aq", "--no-trunc", "--filter", "name=^/" + name + "$"],
            cwd=ROOT,
            env=environment,
            capture_output=True,
            timeout=30,
            check=True,
        )
        return result.stdout.decode("ascii").splitlines()

    before = identities()
    observations = []
    scope = load_json(current_scope_path())
    for identifier in before:
        if re.fullmatch("[a-f0-9]{64}", identifier) is None or identifier in {
            row["id"] for row in scope["before"]["containers"]
        }:
            raise ValueError("NONBASELINE_PRIVATE_PROBE_ID_REQUIRED")
        value = json.loads(
            subprocess.run(
                ["docker", "inspect", identifier],
                cwd=ROOT,
                env=environment,
                capture_output=True,
                timeout=30,
                check=True,
            ).stdout
        )[0]
        if (
            value["Id"] != identifier
            or value["Name"] != "/" + name
            or value["Config"]["Labels"].get("com.docker.compose.project")
            != scope["inheritedOwnedProject"]
        ):
            raise ValueError("PRIVATE_PROBE_OWNERSHIP_CHANGED")
        execution, _streams = run_owned(
            Job(("docker", "rm", "--force", identifier), 60),
            ROOT,
            environment,
            find_secrets,
            WindowsJob,
        )
        observations.append({"containerId": identifier, "execution": execution})
        if execution["producer"]["exitCode"] != 0 or execution["cleanup"]["result"] != "PASS":
            raise ValueError("OWNED_PROBE_CLEANUP_FAILED")
    after = identities()
    if after:
        raise ValueError("OWNED_PROBE_STILL_PRESENT")
    return {"result": "PASS", "remainingContainers": 0, "recovery": observations}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inner", type=Path)
    args = parser.parse_args()
    if args.inner:
        return inner(args.inner)
    from audit_runner_bridge import Job, run_owned
    from compose import project_image
    from current_resources import child_environment, current_owner_file
    from ledger_common import find_secrets, scope_fingerprint, utc_now, write_json
    from native_process import WindowsJob
    from self_qualification_source import materialize_committed_source

    folder = CHECKPOINT / "causal-attempts/self-project-equivalence"
    folder.mkdir(parents=True, exist_ok=True)
    output = folder / f"run-{len(list(folder.glob('run-*'))) + 1:04d}"
    output.mkdir()
    fingerprint = scope_fingerprint(ROOT)
    with tempfile.TemporaryDirectory(prefix="iacode-m2-self-project-") as temporary:
        base = Path(temporary)
        subject = materialize_full(ROOT, base / "full")
        selection = materialize_committed_source(ROOT, base / "view")
        if selection["subjectCommit"] != subject:
            raise ValueError("SAME_IMMUTABLE_SUBJECT_REQUIRED")
        for label in ("full", "view"):
            pack_actual_inputs(base, label)
        environment = child_environment()
        probe_name = "iacode-m2cp3-self-plan-" + uuid.uuid4().hex
        command = (
            "docker",
            "run",
            "--rm",
            "--name",
            probe_name,
            "--label",
            "com.docker.compose.project=" + environment["COMPOSE_PROJECT_NAME"],
            "--network",
            "none",
            "--read-only",
            "--cap-drop",
            "ALL",
            "--security-opt",
            "no-new-privileges:true",
            "--env",
            "PYTHONDONTWRITEBYTECODE=1",
            "--volume",
            str(ROOT) + ":/repo:ro",
            "--volume",
            str(base) + ":/inputs:ro",
            "--workdir",
            "/repo",
            project_image("api", current_owner_file()),
            "python",
            "/repo/" + Path(__file__).relative_to(ROOT).as_posix(),
            "--inner",
            "/inputs",
        )
        execution, streams = run_owned(
            Job(command, 300), ROOT, environment, find_secrets, WindowsJob
        )
        for name, raw in streams.items():
            with (output / name).open("xb") as stream:
                stream.write(raw)
        disposal = remove_only_own_probe(probe_name, environment)
    passed = (
        execution["producer"]["exitCode"] == 0
        and execution["producer"]["status"] == "COMPLETED"
        and execution["cleanup"]["result"] == "PASS"
        and not any(execution["producer"][name]["refusal"] for name in ("stdout", "stderr"))
        and fingerprint == scope_fingerprint(ROOT)
        and not Path(temporary).exists()
        and disposal["result"] == "PASS"
    )
    write_json(
        output / "RECEIPT.json",
        {
            "observedAt": utc_now(),
            "result": "PASS" if passed else "FAIL",
            "kind": "ACTUAL_COMMITTED_INPUT_PROJECT_CHECK_PROOF_NOT_WHOLE_ACCEPTANCE",
            "subjectCommit": subject,
            "sourceFingerprint": fingerprint,
            "sourceUnchanged": fingerprint == scope_fingerprint(ROOT),
            "execution": execution,
            "temporaryOwnerRemoved": not Path(temporary).exists(),
            "hostPackagesInstalled": False,
            "ownedContainerCleanup": disposal,
        },
    )
    print(
        json.dumps(
            {
                "result": "PASS" if passed else "FAIL",
                "receipt": (output / "RECEIPT.json").relative_to(ROOT).as_posix(),
            }
        )
    )
    return int(not passed)


if __name__ == "__main__":
    raise SystemExit(main())
