"""Inspect completed full verification; pause only its pinned, idle private builder."""

from __future__ import annotations

import argparse
import hashlib
import http.client
import json
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlsplit

from current_resources import child_environment, current_scope_path

sys.path.insert(
    0, str(Path(__file__).resolve().parents[1].parents[2] / "scripts/development-ledger")
)

from audit_runner_bridge import Job, run_owned
from ledger_common import find_secrets, load_json, utc_now, write_json
from native_process import WindowsJob

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]


def dependency_metadata():
    rows = []
    urls = [
        "https://registry.npmjs.org/%40angular%2Fbuild/22.2.3",
        "https://registry.npmjs.org/%40angular%2Fbuild/22.2.4",
        "https://registry.npmjs.org/vitest/latest",
        "https://registry.npmjs.org/vite/8.3.3",
    ]
    for url in urls:
        parsed = urlsplit(url)
        if parsed.scheme != "https" or parsed.netloc != "registry.npmjs.org":
            raise ValueError("FIXED_PRIMARY_REGISTRY_ORIGIN_REQUIRED")
        connection = http.client.HTTPSConnection(parsed.netloc, timeout=20)
        try:
            connection.request("GET", parsed.path)
            response = connection.getresponse()
            if response.status == 404:
                rows.append({"url": url, "status": 404})
                continue
            if response.status != 200:
                raise ValueError("UNEXPECTED_PRIMARY_REGISTRY_STATUS")
            raw = response.read(1024 * 1024 + 1)
        finally:
            connection.close()
        if len(raw) > 1024 * 1024:
            raise ValueError("BOUNDED_PUBLIC_REGISTRY_METADATA_REQUIRED")
        value = json.loads(raw)
        dependencies = value.get("dependencies", {})
        rows.append(
            {
                "url": url,
                "status": 200,
                "bytes": len(raw),
                "sha256": hashlib.sha256(raw).hexdigest(),
                "name": value["name"],
                "version": value["version"],
                "engines": value.get("engines"),
                "relevantDependencies": {
                    key: dependencies[key]
                    for key in ("vite", "@vitest/mocker")
                    if key in dependencies
                },
            }
        )
    directory = CHECKPOINT / "environment-observations/dependency-metadata"
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / f"run-{len(list(directory.glob('run-*.json'))) + 1:04d}.json"
    write_json(
        target,
        {
            "observedAt": utc_now(),
            "kind": "PUBLIC_PRIMARY_REGISTRY_METADATA_NOT_INSTALLATION",
            "observations": rows,
        },
    )
    print(json.dumps({"observations": rows, "receipt": target.relative_to(ROOT).as_posix()}))


def capture_host_test_preimage(*, self_source=False):
    source = ROOT / (
        "scripts/iacode/self_qualification_source.py"
        if self_source
        else "tests/test_m2_host_transport.py"
    )
    raw = source.read_bytes()
    if find_secrets(raw.decode("utf-8", errors="strict")):
        raise ValueError("UNSAFE_PREIMAGE")
    target = (
        CHECKPOINT
        / "raw-preimages"
        / (
            "SELF-QUALIFICATION-SOURCE-BEFORE-OBJECT-BATCH.raw"
            if self_source
            else "HOST-TRANSPORT-TEST-BEFORE-FIXTURE-PATH.raw"
        )
    )
    with target.open("xb") as stream:
        stream.write(raw)
    write_json(
        target.with_suffix(".json"),
        {
            "source": source.relative_to(ROOT).as_posix(),
            "sha256": hashlib.sha256(raw).hexdigest(),
            "bytes": len(raw),
            "reason": "Preserve actual failed input before its causal correction",
            "originalCommand": "cmd-0566" if self_source else "cmd-0557",
        },
    )
    print(json.dumps({"archive": target.relative_to(ROOT).as_posix(), "bytes": len(raw)}))


def inspect():
    verification = load_json(CHECKPOINT / "VERIFY.json")
    isolation = load_json(CHECKPOINT / "COMPOSE-ISOLATION-AUDIT.json")
    changes = [
        {"id": key, "before": state, "after": isolation["unrelatedAfter"].get(key)}
        for key, state in isolation["unrelatedBefore"].items()
        if isolation["unrelatedAfter"].get(key) != state
    ]
    tracked = (
        subprocess.run(["git", "ls-files", "-z"], cwd=ROOT, capture_output=True, check=True)
        .stdout.decode("utf-8")
        .split("\0")
    )
    sizes = []
    for name in tracked:
        if not name:
            continue
        path = ROOT / name
        if path.is_file() and not path.is_symlink():
            sizes.append((path.stat().st_size, name))
    lessons = [
        json.loads(line)
        for line in (ROOT / ".iacode/memory/lessons.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    candidates = [
        {
            "id": row["lessonId"],
            "title": row["title"],
            "status": row["status"],
            "recurrenceCount": row["recurrenceCount"],
            "guardrails": row["guardrails"],
        }
        for row in lessons
        if any(
            token in (row["title"] + " " + row["symptom"]).lower()
            for token in (
                "snapshot",
                "long path",
                "long-path",
                "dependency",
                "catalog",
                "provider",
                "oci",
                "unrelated",
                "container identit",
            )
        )
    ]
    print(
        json.dumps(
            {
                "kind": "DIAGNOSTIC_NOT_ACCEPTANCE",
                "failedStages": [
                    row["name"] for row in verification["stages"] if row["result"] == "FAIL"
                ],
                "containerStateChanges": changes,
                "trackedWorkingBytes": sum(size for size, _ in sizes),
                "checkpointBytes": sum(
                    size for size, name in sizes if name.startswith("docs/checkpoints/")
                ),
                "largestTrackedFiles": sorted(sizes, reverse=True)[:12],
                "lessonCandidatesNotAutomaticClassification": candidates,
            },
            indent=2,
        )
    )


def pause_builder():
    scope = load_json(current_scope_path())
    receipt = load_json(CHECKPOINT / "PUBLISHED-CLEAN-CLONE-REPORT.json")
    histories = sorted(
        (CHECKPOINT / "resource-observations/build-history").glob("run-*/RECEIPT.json")
    )
    if not histories:
        raise ValueError("ACTUAL_PRIVATE_BUILDER_HISTORY_REQUIRED")
    history = load_json(histories[-1])
    owner = scope["builderOwnership"]
    if (
        receipt["publishedCommit"] != "3cafb3cf77c09fc7c651df0fc82b0fca12c880b3"
        or not receipt["temporaryCloneRemoved"]
        or not receipt["ownedComposeProjectRemoved"]
        or history["builder"] != scope["builder"]
        or history["result"] != "CAPTURED_NOT_OWNERSHIP_CLAIM_OR_ACCEPTANCE"
        or any(
            row["status"] not in {"completed", "canceled", "error"}
            for row in history["inspectSummary"]
        )
        or owner["id"] in {row["id"] for row in scope["before"]["containers"]}
    ):
        raise ValueError("COMPLETED_OWNED_PRODUCER_AND_TERMINAL_HISTORY_REQUIRED")
    environment = child_environment()
    checked = (
        subprocess.run(
            ["docker", "inspect", "--format", "{{.Id}}:{{.Name}}:{{.Image}}", owner["id"]],
            cwd=ROOT,
            env=environment,
            capture_output=True,
            timeout=30,
            check=True,
        )
        .stdout.decode("utf-8")
        .strip()
    )
    if checked != owner["id"] + ":/" + owner["name"] + ":" + owner["imageId"]:
        raise ValueError("PINNED_BUILDER_IDENTITY_CHANGED")
    execution, streams = run_owned(
        Job(("docker", "stop", "--time=30", owner["id"]), 60),
        ROOT,
        environment,
        find_secrets,
        WindowsJob,
    )
    observed = (
        subprocess.run(
            ["docker", "inspect", "--format", "{{.Id}}:{{.State.Running}}", owner["id"]],
            cwd=ROOT,
            env=environment,
            capture_output=True,
            timeout=30,
            check=True,
        )
        .stdout.decode("utf-8")
        .strip()
    )
    producer = execution["producer"]
    passed = (
        producer["status"] == "COMPLETED"
        and producer["exitCode"] == 0
        and execution["cleanup"]["result"] == "PASS"
        and observed == owner["id"] + ":false"
        and not any(producer[name]["refusal"] for name in ("stdout", "stderr"))
    )
    folder = CHECKPOINT / "resource-observations/builder-idle"
    folder.mkdir(parents=True, exist_ok=True)
    target = folder / f"run-{len(list(folder.glob('run-*.json'))) + 1:04d}.json"
    write_json(
        target,
        {
            "observedAt": utc_now(),
            "result": "PASS" if passed else "FAIL",
            "action": "STOP_ONLY_EXACT_OWNED_IDLE_BUILDER_NOT_FINAL_DISPOSAL",
            "builder": scope["builder"],
            "containerId": owner["id"],
            "runningAfter": observed != owner["id"] + ":false",
            "execution": execution,
            "streamHashesRechecked": all(
                hashlib.sha256(streams.get(name + ".log", b"")).hexdigest()
                == producer[name]["sha256"]
                for name in ("stdout", "stderr")
            ),
            "cacheStillRequiredForCorrectiveBuilds": True,
            "finalDisposalStillRequired": True,
            "otherApplicationsControlled": False,
        },
    )
    print(
        json.dumps(
            {
                "result": "PASS" if passed else "FAIL",
                "builderRunning": not passed,
                "observation": target.relative_to(ROOT).as_posix(),
                "finalDisposal": False,
            }
        )
    )
    return int(not passed)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pause-builder", action="store_true")
    parser.add_argument("--dependency-metadata", action="store_true")
    parser.add_argument("--capture-host-test-preimage", action="store_true")
    parser.add_argument("--capture-self-source-preimage", action="store_true")
    options = parser.parse_args()
    if options.dependency_metadata:
        raise SystemExit(dependency_metadata())
    if options.capture_host_test_preimage:
        raise SystemExit(capture_host_test_preimage())
    if options.capture_self_source_preimage:
        raise SystemExit(capture_host_test_preimage(self_source=True))
    raise SystemExit(pause_builder() if options.pause_builder else inspect())
