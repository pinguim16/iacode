"""Pinned unchanged Ruff rules over derived current helpers and regression sources."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import uuid
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))
sys.path.insert(0, str(ROOT / "scripts/iacode"))


def authored_paths():
    from audit_runner_bridge import regular
    from ledger_common import git_delta, load_json

    delta = git_delta(ROOT, load_json(CHECKPOINT / "STATE.json")["baseCommit"], None)
    prefix = CHECKPOINT.relative_to(ROOT).as_posix() + "/audit-harness/"
    paths = sorted(
        name
        for name, status in delta.items()
        if status != "D"
        and name.endswith(".py")
        and (
            name.startswith(prefix)
            or name.startswith("tests/test_m2_")
            or name.startswith("scripts/iacode/")
        )
    )
    if not paths:
        raise ValueError("Derived authored source scope must not be empty")
    for name in paths:
        regular(ROOT / name, ROOT)
    return paths


def main():
    from audit_runner_bridge import Job, run_owned
    from compose import project_image
    from current_resources import child_environment, current_owner_file
    from ledger_common import find_secrets, scope_fingerprint, utc_now, write_json
    from native_process import WindowsJob

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("check", "format"))
    options = parser.parse_args()
    paths = authored_paths()
    before = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in paths}
    source = scope_fingerprint(ROOT)
    folder = CHECKPOINT / "quality-attempts/helper-quality"
    folder.mkdir(parents=True, exist_ok=True)
    output = folder / f"run-{len(list(folder.glob('run-*'))) + 1:04d}"
    output.mkdir()
    environment = child_environment()
    commands = (
        [("check", ["check", *paths])]
        if options.mode == "check"
        else [("format", ["format", *paths]), ("safe-fix", ["check", "--fix", *paths])]
    )
    receipt = {
        "startedAt": utc_now(),
        "kind": "DERIVED_AUTHORED_SOURCE_QUALITY",
        "mode": options.mode,
        "paths": paths,
        "hashesBefore": before,
        "sourceFingerprint": source,
        "result": "FAIL",
        "executions": [],
        "scopeNote": (
            "All current active checkpoint Python helpers and changed M2 "
            "regressions/runtime scripts; historical raw observations and"
            " inherited audit subjects are not active authored code. Exis"
            "ting sealed control-plane Ruff exclusion is unchanged; its o"
            "wning mandatory suite still runs."
        ),
    }
    write_json(output / "RECEIPT.json", receipt)
    for label, arguments in commands:
        command = [
            "docker",
            "run",
            "--rm",
            "--name",
            "iacode-m2cp3-style-" + uuid.uuid4().hex,
            "--label",
            "com.docker.compose.project=" + environment["COMPOSE_PROJECT_NAME"],
            "--network",
            "none",
            "--read-only",
            "--tmpfs",
            "/var/cache/iacode-quality:rw,nosuid,size=67108864",
            "--env",
            "RUFF_CACHE_DIR=/var/cache/iacode-quality/ruff-cache",
            "--volume",
            str(ROOT) + (":/repo:ro" if options.mode == "check" else ":/repo"),
            "--workdir",
            "/repo",
            project_image("api", current_owner_file()),
            "ruff",
            *arguments,
        ]
        execution, streams = run_owned(
            Job(tuple(command), 300), ROOT, environment, find_secrets, WindowsJob
        )
        receipt["executions"].append({"step": label, **execution})
        write_json(output / "RECEIPT.json", receipt)
        for name, raw in streams.items():
            with (output / (label + "." + name)).open("xb") as stream:
                stream.write(raw)
        if (
            execution["producer"]["status"] != "COMPLETED"
            or execution["producer"]["exitCode"] != 0
            or execution["cleanup"]["result"] != "PASS"
            or any(execution["producer"][name]["refusal"] for name in ("stdout", "stderr"))
        ):
            break
    after = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in paths}
    receipt.update(
        finishedAt=utc_now(),
        hashesAfter=after,
        sourceUnchanged=scope_fingerprint(ROOT) == source and before == after,
    )
    complete = len(receipt["executions"]) == len(commands) and all(
        value["producer"]["status"] == "COMPLETED"
        and value["producer"]["exitCode"] == 0
        and value["cleanup"]["result"] == "PASS"
        and not any(value["producer"][name]["refusal"] for name in ("stdout", "stderr"))
        for value in receipt["executions"]
    )
    if options.mode == "check" and complete and receipt["sourceUnchanged"]:
        receipt["result"] = "PASS"
    elif options.mode == "format" and complete:
        receipt["result"] = "FORMATTED_NOT_READ_ONLY_ACCEPTANCE"
    write_json(output / "RECEIPT.json", receipt)
    print(
        json.dumps(
            {
                "result": receipt["result"],
                "mode": options.mode,
                "sourceUnchanged": receipt["sourceUnchanged"],
                "paths": len(paths),
                "receipt": (output / "RECEIPT.json").relative_to(CHECKPOINT).as_posix(),
            }
        )
    )
    return 0 if complete and (options.mode == "format" or receipt["sourceUnchanged"]) else 1


if __name__ == "__main__":
    from ledger_common import use_utf8_stdout

    use_utf8_stdout()
    raise SystemExit(main())
