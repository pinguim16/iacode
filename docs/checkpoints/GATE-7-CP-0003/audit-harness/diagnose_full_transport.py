"""Reproduce the unchanged host Red Team transport at the full verifier's nested depth."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(
    0, str(Path(__file__).resolve().parents[1].parents[2] / "scripts/development-ledger")
)
sys.path.insert(0, str(Path(__file__).resolve().parents[1].parents[2] / "scripts/iacode"))

from audit_runner_bridge import Job, run_owned
from ledger_common import find_secrets, load_json, scope_fingerprint, utc_now, write_json
from native_process import WindowsJob

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]
SUBJECT = "3cafb3cf77c09fc7c651df0fc82b0fca12c880b3"


def inner(root):
    import gate4_red_team

    original = subprocess.run
    observations = []

    def observe(arguments, *args, **kwargs):
        result = original(arguments, *args, **kwargs)
        if isinstance(arguments, (tuple, list)) and (
            (arguments[0] == "git" and "clone" in arguments)
            or any(str(value).endswith("review_bundle.py") for value in arguments)
        ):
            observations.append(
                {
                    "kind": "GIT_CLONE" if arguments[0] == "git" else "REVIEW_PRODUCER",
                    "exitCode": result.returncode,
                    "output": result.stdout,
                }
            )
        return result

    subprocess.run = observe
    try:
        attacks = gate4_red_team._host_attacks(root, root / "docs/checkpoints/GATE-7-CP-0003")
    finally:
        subprocess.run = original
    document = {
        "kind": "UNCHANGED_HOST_ATTACK_DIAGNOSTIC_NOT_WHOLE_ACCEPTANCE",
        "attackT": next(row for row in attacks if row["attackId"] == "T"),
        "originalProducerObservations": observations,
    }
    text = json.dumps(document)
    if find_secrets(text):
        raise ValueError("UNSAFE_DIAGNOSTIC_OUTPUT_REFUSED")
    print(text, flush=True)
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inner", type=Path)
    args = parser.parse_args()
    if args.inner is not None:
        return inner(args.inner)
    from current_resources import child_environment

    before = scope_fingerprint(ROOT)
    folder = CHECKPOINT / "causal-attempts/full-host-transport"
    folder.mkdir(parents=True, exist_ok=True)
    destination = folder / f"run-{len(list(folder.glob('run-*'))) + 1:04d}"
    destination.mkdir()
    environment = child_environment()
    environment.update(GIT_TERMINAL_PROMPT="0", GCM_INTERACTIVE="Never")
    owner_path = None
    with tempfile.TemporaryDirectory(prefix="iacode-gate7-full-diagnostic-") as directory:
        owner_path = Path(directory)
        clone = owner_path / "repository"
        for arguments, cwd in (
            (
                [
                    "git",
                    "-c",
                    "core.longpaths=true",
                    "clone",
                    "--quiet",
                    "--no-local",
                    str(ROOT),
                    str(clone),
                ],
                ROOT,
            ),
            (["git", "checkout", "--quiet", "--detach", SUBJECT], clone),
        ):
            completed = subprocess.run(
                arguments, cwd=cwd, env=environment, capture_output=True, check=False
            )
            if completed.returncode:
                raise ValueError("OUTER_TRANSPORT_PRECONDITION_FAILED")
        (clone / "var").mkdir(exist_ok=True)
        manifest = load_json(CHECKPOINT / "attempts/FULL-PRODUCER-a611076fb7ce-MANIFEST.json")
        for row in manifest["reports"]:
            name = row["producerName"]
            if name in {
                "quality-recovery.json",
                "quality-cancellation.json",
                "quality-timeout.json",
                "sandbox-tool-result-origin.json",
                "quality-secret-output.json",
            }:
                shutil.copyfile(CHECKPOINT / "attempts" / row["archive"], clone / "var" / name)
        children = owner_path / "temporary"
        children.mkdir()
        environment.update(TEMP=str(children), TMP=str(children), PYTHONIOENCODING="utf-8")
        execution, streams = run_owned(
            Job((sys.executable, str(Path(__file__).resolve()), "--inner", str(clone)), 1800),
            clone,
            environment,
            find_secrets,
            WindowsJob,
        )
        for name, raw in streams.items():
            with (destination / name).open("xb") as stream:
                stream.write(raw)
        write_json(destination / "EXECUTION.json", execution)
    receipt = {
        "observedAt": utc_now(),
        "kind": "DIAGNOSTIC_NOT_ACCEPTANCE",
        "subjectCommit": SUBJECT,
        "sourceFingerprint": before,
        "sourceUnchanged": before == scope_fingerprint(ROOT),
        "execution": execution,
        "temporaryOwnerRemoved": not owner_path.exists(),
        "owner": str(owner_path),
        "applicationsControlled": False,
    }
    write_json(destination / "RECEIPT.json", receipt)
    print(
        json.dumps(
            {
                "receipt": (destination / "RECEIPT.json").relative_to(ROOT).as_posix(),
                "exitCode": execution["producer"]["exitCode"],
                "cleanup": execution["cleanup"]["result"],
                "temporaryOwnerRemoved": receipt["temporaryOwnerRemoved"],
            }
        )
    )
    return int(execution["producer"]["exitCode"] != 0 or execution["cleanup"]["result"] != "PASS")


if __name__ == "__main__":
    raise SystemExit(main())
