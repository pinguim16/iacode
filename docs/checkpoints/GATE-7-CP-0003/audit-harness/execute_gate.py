"""Capture safe exact process output before interpreting a complete policy-owned local gate."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))

from ledger_common import find_secrets, git_snapshot, scope_fingerprint, utc_now, use_utf8_stdout, write_json
from policies import gate_definitions


def preserve_execution(command: list[str], stem: str, kind: str, identity: str) -> int:
    from owned_docker_scope import child_environment

    argv = list(command)
    if argv[0] == "python":
        argv[0] = sys.executable
    directory = CHECKPOINT / "suite-attempts"
    directory.mkdir(exist_ok=True)
    number = len(list(directory.glob(stem + "-*.json"))) + 1
    prefix = directory / (stem + f"-{number:04d}")
    if prefix.with_suffix(".json").exists() or prefix.with_suffix(".log").exists():
        raise ValueError("refuse overwriting an observation")
    before = scope_fingerprint(ROOT)
    snapshot = git_snapshot(ROOT)
    from compose import read_env_file

    environment = child_environment()
    # Build-only canonical gates must not fall back to a preexisting application's tag.
    environment.update(read_env_file(CHECKPOINT / "RUNTIME-OWNER.txt", {}))
    result = subprocess.run(argv, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            check=False, env=environment)
    raw = result.stdout
    encoding_valid = True
    try:
        output = raw.decode("utf-8", errors="strict")
    except UnicodeError:
        output = ""
        encoding_valid = False
    findings = find_secrets(output) if encoding_valid else ["unscannable output"]
    artifact = None
    if not findings:
        artifact = prefix.with_suffix(".log")
        with artifact.open("xb") as stream:
            stream.write(raw)
    unchanged = scope_fingerprint(ROOT) == before
    report = {
        "schemaVersion": "1.0.0", "kind": kind, "gate": identity, "command": command,
        "observedAt": utc_now(), "subjectCommit": snapshot["head"], "sourceDirty": snapshot["dirty"],
        "sourceFingerprint": before, "sourceUnchanged": unchanged, "exitCode": result.returncode,
        "outputEncodingValid": encoding_valid, "unsafeOutputOccurrences": len(findings),
        "outputBytes": len(raw), "outputSha256": hashlib.sha256(raw).hexdigest(),
        "safeOutputArtifact": artifact.relative_to(ROOT).as_posix() if artifact else None,
        "result": "PASS" if result.returncode == 0 and unchanged and not findings else "FAIL",
    }
    write_json(prefix.with_suffix(".json"), report)
    print(json.dumps(report))
    return 0 if report["result"] == "PASS" else (result.returncode or 1)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gate", required=True)
    options = parser.parse_args()
    gates = gate_definitions(ROOT)
    if options.gate not in gates:
        raise ValueError("gate must resolve against the canonical registry")
    return preserve_execution(list(gates[options.gate]["command"]),
                              "GATE-" + options.gate.upper(), "COMPLETE_POLICY_GATE", options.gate)


if __name__ == "__main__":
    use_utf8_stdout()
    raise SystemExit(main())
