"""Preserve exact safe regression output before interpreting a targeted test result."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
import uuid
from pathlib import Path

sys.path.insert(
    0, str(Path(__file__).resolve().parents[1].parents[2] / "scripts/development-ledger")
)
from ledger_common import (
    find_secrets,
    load_json,
    scope_fingerprint,
    use_utf8_stdout,
    utc_now,
    write_json,
)

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--gate")
    mode.add_argument("--changed-source-lint", action="store_true")
    mode.add_argument("--format-current-native", action="store_true")
    mode.add_argument("--restricted-client-probe", action="store_true")
    mode.add_argument("--bridge-controls", action="store_true")
    mode.add_argument("--cleanup-controls", action="store_true")
    mode.add_argument("--operator-cleanup-controls", action="store_true")
    mode.add_argument("--dependency-cleanup-controls", action="store_true")
    mode.add_argument("--resource-phase-controls", action="store_true")
    mode.add_argument("--bootstrap-ownership-controls", action="store_true")
    mode.add_argument("--publication-controls", action="store_true")
    mode.add_argument("--history-transport-controls", action="store_true")
    mode.add_argument("--discovery-isolation-controls", action="store_true")
    mode.add_argument("--all-m2-controls", action="store_true")
    mode.add_argument("--lint-denominator-controls", action="store_true")
    mode.add_argument("--native-controls", action="store_true")
    mode.add_argument("--native-candidate", action="store_true")
    mode.add_argument("--physical-bounds-controls", action="store_true")
    mode.add_argument("--current-stream-controls", action="store_true")
    mode.add_argument("--inherited-stream-controls", action="store_true")
    mode.add_argument("--byte-transport-controls", action="store_true")
    options = parser.parse_args()
    environment = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    if options.gate or options.changed_source_lint or options.format_current_native:
        sys.path.insert(0, str(ROOT / "scripts/iacode"))
        from compose import project_image, read_env_file
        from current_resources import child_environment, current_owner_file

        environment = child_environment()
        owned = read_env_file(current_owner_file(), {})
        environment.update(owned)
    if options.discovery_isolation_controls:
        command = ["python", "tests/test_m2_discovery_isolation.py", "-v"]
        folder = "causal-attempts/discovery-isolation"
    elif options.history_transport_controls:
        command = [
            "python",
            "-m",
            "unittest",
            "discover",
            "-s",
            "tests",
            "-p",
            "test_m2_history_transport.py",
            "-v",
        ]
        folder = "causal-attempts/history-transport"
    elif options.lint_denominator_controls:
        command = [
            "python",
            "-m",
            "unittest",
            "discover",
            "-s",
            "tests",
            "-p",
            "test_gate7_knowledge.py",
            "-k",
            "Gate7LintDenominatorTests",
            "-v",
        ]
        folder = "causal-attempts/lint-denominator"
    elif options.all_m2_controls:
        command = [
            "python",
            "-m",
            "unittest",
            "discover",
            "-s",
            "tests",
            "-p",
            "test_m2_*.py",
            "-v",
        ]
        folder = "causal-attempts/all-m2"
    elif options.publication_controls:
        command = [
            "python",
            "-m",
            "unittest",
            "discover",
            "-s",
            "tests",
            "-p",
            "test_m2_progress_publication.py",
            "-v",
        ]
        folder = "causal-attempts/publication-policy"
    elif options.bootstrap_ownership_controls:
        command = [
            "python",
            "-m",
            "unittest",
            "discover",
            "-s",
            "tests",
            "-p",
            "test_m2_bootstrap_ownership.py",
            "-v",
        ]
        folder = "causal-attempts/bootstrap-ownership"
    elif options.resource_phase_controls:
        command = [
            "python",
            "docs/checkpoints/GATE-7-CP-0003/audit-harness/test_resource_phase.py",
            "-v",
        ]
        folder = "causal-attempts/resource-phase"
    elif options.byte_transport_controls:
        command = [
            "python",
            "-m",
            "unittest",
            "discover",
            "-s",
            "tests",
            "-p",
            "test_m2_observation_transport.py",
            "-v",
        ]
        folder = "byte-transport-attempts/controls"
    elif options.current_stream_controls:
        command = [
            "python",
            "-m",
            "unittest",
            "discover",
            "-s",
            "tests",
            "-p",
            "test_m2_current_stream_bootstrap.py",
            "-v",
        ]
        folder = "causal-attempts/current-streams"
    elif options.inherited_stream_controls:
        command = [
            "python",
            "-m",
            "unittest",
            "discover",
            "-s",
            "tests",
            "-p",
            "test_gate0_foundation.py",
            "-k",
            "SubprocessDecodingTests",
            "-v",
        ]
        folder = "causal-attempts/inherited-streams"
    elif options.physical_bounds_controls:
        command = [
            "python",
            "-m",
            "unittest",
            "discover",
            "-s",
            "tests",
            "-p",
            "test_m2_bridge_physical_bounds.py",
            "-v",
        ]
        folder = "causal-attempts/bridge-physical-bounds"
    elif options.native_candidate:
        command = [
            "python",
            "docs/checkpoints/GATE-7-CP-0003/audit-harness/run_native_candidate.py",
            "-v",
        ]
        folder = "causal-attempts/native-candidate"
    elif options.native_controls:
        command = [
            "python",
            "-m",
            "unittest",
            "discover",
            "-s",
            "tests",
            "-p",
            "test_m2_native_observation.py",
            "-v",
        ]
        folder = "causal-attempts/native-observation"
    elif options.dependency_cleanup_controls:
        command = [
            "python",
            "docs/checkpoints/GATE-7-CP-0003/audit-harness/test_cleanup_dependency_order.py",
            "-v",
        ]
        folder = "causal-attempts/dependency-cleanup"
    elif options.operator_cleanup_controls:
        command = [
            "python",
            "-m",
            "unittest",
            "discover",
            "-s",
            "tests",
            "-p",
            "test_m2_cleanup_operator.py",
            "-v",
        ]
        folder = "causal-attempts/operator-cleanup"
    elif options.cleanup_controls:
        command = [
            "python",
            "-m",
            "unittest",
            "discover",
            "-s",
            "tests",
            "-p",
            "test_m2_owned_resource_cleanup.py",
            "-v",
        ]
        folder = "causal-attempts/owned-cleanup"
    elif options.bridge_controls:
        command = [
            "python",
            "-m",
            "unittest",
            "discover",
            "-s",
            "tests",
            "-p",
            "test_m2_closed_runner_bridge.py",
            "-v",
        ]
        folder = "causal-attempts/bridge"
    elif options.restricted_client_probe:
        command = [
            "C:/Users/cesar/AppData/Local/OpenAI/Codex/bin/896a0166b774037a/codex.exe",
            "-c",
            'windows.sandbox="elevated"',
            "-c",
            "features.prefer_mxc=false",
            "-c",
            "sandbox_workspace_write.network_access=true",
            "sandbox",
            "--cd",
            str(ROOT),
            "--include-managed-config",
            "-P",
            ":workspace",
            "--",
            sys.executable,
            "docs/checkpoints/GATE-7-CP-0003/audit-harness/probe_restricted_client.py",
        ]
        folder = "quality-attempts/restricted-client-probe"
    elif options.format_current_native:
        command = [
            "docker",
            "run",
            "--rm",
            "--name",
            "iacode-m2cp3-format-" + uuid.uuid4().hex,
            "--network",
            "none",
            "--read-only",
            "--cap-drop",
            "ALL",
            "--security-opt",
            "no-new-privileges:true",
            "--env",
            "RUFF_NO_CACHE=true",
            "--volume",
            str(ROOT) + ":/repo",
            "--workdir",
            "/repo",
            project_image("api", current_owner_file()),
            "ruff",
            "format",
            "scripts/iacode/native_editor.py",
            "scripts/iacode/native_execution.py",
        ]
        folder = "quality-attempts/native-format"
    elif options.changed_source_lint:
        # project_image derives the canonical tag; inherited environment must not redirect it.
        if any(key in os.environ and os.environ[key] != value for key, value in owned.items()):
            raise ValueError(
                "inherited runtime selection conflicts with the declared disposable owner"
            )
        command = [
            "docker",
            "run",
            "--rm",
            "--name",
            "iacode-m2cp3-ruff-" + uuid.uuid4().hex,
            "--network",
            "none",
            "--read-only",
            "--cap-drop",
            "ALL",
            "--security-opt",
            "no-new-privileges:true",
            "--env",
            "RUFF_NO_CACHE=true",
            "--volume",
            str(ROOT) + ":/repo:ro",
            "--workdir",
            "/repo",
            project_image("api", current_owner_file()),
            "ruff",
            "check",
            "scripts/iacode/client_checks.py",
            "scripts/iacode/gates/client_tests.py",
            "scripts/iacode/native_editor.py",
            "scripts/iacode/native_execution.py",
        ]
        folder = "quality-attempts/changed-source-lint"
    elif options.gate:
        from policies import gate_definitions

        definitions = gate_definitions(ROOT)
        if options.gate not in definitions:
            parser.error("gate must be defined by canonical policy")
        command = list(definitions[options.gate]["command"])
        folder = "quality-attempts/" + options.gate
    else:
        command = [
            "python",
            "-m",
            "unittest",
            "discover",
            "-s",
            "tests",
            "-p",
            "test_m2_audit_corrections.py",
            "-v",
        ]
        folder = "causal-attempts"
    directory = CHECKPOINT / folder
    directory.mkdir(parents=True, exist_ok=True)
    index = (
        max(
            (int(path.name.split(".")[0].split("-")[1]) for path in directory.glob("run-*.*")),
            default=0,
        )
        + 1
    )
    prefix = directory / f"run-{index:04d}"
    argv = [sys.executable if command[0] == "python" else command[0], *command[1:]]
    if options.gate == "checkpointValidation":
        from finalize_checkpoint import refresh_declared_hashes

        metadata = load_json(CHECKPOINT / "RUN-METADATA.json")
        metadata["finishedAt"] = utc_now()
        write_json(CHECKPOINT / "RUN-METADATA.json", metadata)
        refresh_declared_hashes(ROOT, CHECKPOINT)
    started = utc_now()
    fingerprint = scope_fingerprint(ROOT)
    clock = time.monotonic()
    result = subprocess.run(argv, cwd=ROOT, capture_output=True, check=False, env=environment)
    receipt = {
        "startedAt": started,
        "finishedAt": utc_now(),
        "sourceFingerprint": fingerprint,
        "sourceUnchanged": scope_fingerprint(ROOT) == fingerprint,
        "durationMs": int((time.monotonic() - clock) * 1000),
        "arguments": argv,
        "exitCode": result.returncode,
        "streams": {},
    }
    for name, raw in (("stdout", result.stdout), ("stderr", result.stderr)):
        try:
            text = raw.decode("utf-8", errors="strict")
            refused = bool(find_secrets(text))
        except UnicodeError:
            refused = True
        except Exception:
            # A failed privacy scan never permits publishing raw producer output. Retain the
            # neutral digest/byte inventory, including for failures inside the scanner itself.
            refused = True
        path = prefix.with_suffix("." + name + ".log")
        if not refused:
            with path.open("xb") as stream:
                stream.write(raw)
        receipt["streams"][name] = {
            "sha256": hashlib.sha256(raw).hexdigest(),
            "bytes": len(raw),
            "refused": refused,
            "path": path.relative_to(ROOT).as_posix() if not refused else None,
        }
    write_json(prefix.with_suffix(".json"), receipt)
    print(json.dumps(receipt))
    return result.returncode or int(
        not receipt["sourceUnchanged"]
        or any(item["refused"] for item in receipt["streams"].values())
    )


if __name__ == "__main__":
    use_utf8_stdout()
    raise SystemExit(main())
