"""Actual owned VSIX installation and native Extension Host execution; never a UI mock."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

from build_clients import ROOT, build
from native_execution import NativeExecutionError, execute_owned
from native_process import NativeJobCleanupError, WindowsJob, owned_directory


def executable() -> Path:
    configured = os.environ.get("IACODE_VSCODE_EXECUTABLE")
    if configured:
        target = Path(configured).resolve()
    else:
        command = shutil.which("code")
        if not command:
            raise RuntimeError("actual VS Code is required; configure IACODE_VSCODE_EXECUTABLE")
        cli = Path(command).resolve()
        target = cli.parents[1] / "Code.exe" if os.name == "nt" else cli
    if not target.is_file():
        raise RuntimeError("the configured VS Code executable does not exist")
    return target


def cli_command(code: Path) -> list[str]:
    """Read the installed Windows adapter; recent installs use a versioned resources path."""
    if code.suffix.lower() != ".exe":
        return [str(code)]
    adapter = code.parent / "bin/code.cmd"
    text = adapter.read_text(encoding="utf-8-sig")
    match = re.search(r'"%~dp0\.\.\\([^\"]+cli\.js)"', text)
    if not match:
        raise RuntimeError("installed Code CLI adapter has an unsupported layout")
    script = (code.parent / match.group(1).replace("\\", "/")).resolve()
    if not script.is_relative_to(code.parent.resolve()) or not script.is_file():
        raise RuntimeError("installed Code CLI adapter points outside its verified installation")
    return [str(code), str(script)]


def require_persistent_host(arguments: list[str]) -> None:
    if any(value.startswith("--extensionTestsPath") for value in arguments):
        raise RuntimeError(
            "native recovery proof cannot use Code's in-memory extension-test storage"
        )


def run_owned(
    arguments: list[str], *, environment: dict[str, str], timeout: int, as_node: bool = False
) -> subprocess.CompletedProcess:
    return execute_owned(
        arguments,
        environment=environment,
        timeout=timeout,
        as_node=as_node,
        root=ROOT,
        job_factory=WindowsJob,
    )


class NativeEditor:
    def __init__(self, directory: Path, workspace: Path, vsix: Path, protocol_digest: str) -> None:
        self.directory = directory.resolve()
        self.workspace = workspace.resolve()
        self.protocol_digest = protocol_digest
        self.code = executable()
        self.profile = self.directory / "profile"
        self.shared = self.directory / "shared"
        self.extensions = self.directory / "extensions"
        self.driver = self.directory / "driver"
        self.driver.mkdir(parents=True)
        (self.profile / "User").mkdir(parents=True)
        (self.profile / "User/settings.json").write_text(
            json.dumps(
                {
                    "workbench.startupEditor": "none",
                    "workbench.enableExperiments": False,
                    "security.workspace.trust.enabled": True,
                    "security.workspace.trust.startupPrompt": "never",
                    "extensions.autoCheckUpdates": False,
                    "extensions.autoUpdate": False,
                    "telemetry.telemetryLevel": "off",
                    "update.mode": "none",
                }
            ),
            encoding="utf-8",
        )
        (self.driver / "package.json").write_text(
            json.dumps(
                {
                    "name": "iacode-acceptance-driver",
                    "publisher": "iacode-test",
                    "version": "0.0.1",
                    "engines": {"vscode": "^1.138.0"},
                    "main": "./driver.cjs",
                    "activationEvents": ["onStartupFinished"],
                    "capabilities": {"untrustedWorkspaces": {"supported": True}},
                }
            ),
            encoding="utf-8",
        )
        shutil.copyfile(
            ROOT / "apps/vscode-extension/host-tests/driver.cjs", self.driver / "driver.cjs"
        )
        shutil.copyfile(
            ROOT / "apps/vscode-extension/host-tests/index.cjs", self.driver / "test.cjs"
        )
        self.common = [
            str(self.code),
            "--user-data-dir",
            str(self.profile),
            "--shared-data-dir",
            str(self.shared),
            "--extensions-dir",
            str(self.extensions),
        ]
        # The CLI process exits after an actual install. It cannot touch the user's real profile.
        installed = run_owned(
            [
                *cli_command(self.code),
                *self.common[1:],
                "--install-extension",
                str(vsix.resolve()),
                "--force",
            ],
            environment=dict(os.environ),
            timeout=120,
            as_node=os.name == "nt",
        )
        package = self.extensions / "iacode.iacode-0.1.0/package.json"
        if installed.returncode or not package.is_file():
            raise RuntimeError(
                "actual isolated VSIX installation failed: " + installed.stdout[-1200:]
            )
        metadata = json.loads(package.read_text(encoding="utf-8"))
        if (metadata.get("name"), metadata.get("publisher"), metadata.get("version")) != (
            "iacode",
            "iacode",
            "0.1.0",
        ):
            raise RuntimeError("installed extension identity differs from the built VSIX")
        self.installation = {
            "exitCode": installed.returncode,
            "result": "PASS",
            "freshProfile": True,
            "sharedDataDirectoryOwned": True,
            "processCleanup": getattr(installed, "owned_tree_cleanup", None),
        }

    def run(self, mode: str, *, extra_env: dict[str, str] | None = None) -> dict:
        report = self.directory / f"{mode}.json"
        report.unlink(missing_ok=True)
        environment = {
            **os.environ,
            **(extra_env or {}),
            "IACODE_EDITOR_MODE": mode,
            "IACODE_EDITOR_REPORT": str(report),
            "IACODE_EDITOR_EXTENSIONS": str(self.extensions),
            "IACODE_EDITOR_PROTOCOL_DIGEST": self.protocol_digest,
        }
        args = [
            *self.common,
            "--new-window",
            "--skip-welcome",
            "--skip-release-notes",
            "--disable-gpu",
            "--disable-crash-reporter",
            "--disable-telemetry",
            "--extensionDevelopmentPath=" + str(self.driver),
            str(self.workspace),
        ]
        if mode != "untrusted":
            args.append(
                "--disable-workspace-trust"
            )  # Explicit trusted fixture, never a production setting.
        require_persistent_host(args)
        try:
            result = run_owned(
                args, environment=environment, timeout=1800 if mode == "resume" else 180
            )
        except NativeJobCleanupError as error:
            execution = getattr(error, "report", None)
            return {
                "result": "FAIL",
                "mode": mode,
                "failure": "native owned process cleanup failed",
                "exitCode": execution["producer"]["exitCode"] if execution else None,
                "processCleanup": error.observation,
                **({"execution": execution} if execution else {}),
            }
        except (subprocess.TimeoutExpired, NativeExecutionError) as error:
            execution = getattr(error, "report", None)
            return {
                "result": "FAIL",
                "mode": mode,
                "failure": (
                    "native host deadline elapsed"
                    if isinstance(error, subprocess.TimeoutExpired)
                    else "native owned execution failed"
                ),
                "exitCode": execution["producer"]["exitCode"] if execution else None,
                **(
                    {"execution": execution, "processCleanup": execution["cleanup"]["observation"]}
                    if execution
                    else {}
                ),
            }
        document = (
            json.loads(report.read_text(encoding="utf-8"))
            if report.is_file()
            else {"result": "FAIL", "mode": mode, "failure": "native host produced no report"}
        )
        document["exitCode"] = result.returncode
        document["processCleanup"] = getattr(result, "owned_tree_cleanup", None)
        expected_shared = str(self.directory / "shared").replace("\\", "/").casefold()
        storage_lines = []
        for log in (self.directory / "profile/logs").glob("*/main.log"):
            with log.open(encoding="utf-8", errors="replace") as stream:
                storage_lines.extend(
                    line
                    for line in stream.read(1048576).splitlines()
                    if "Creating shared storage database at" in line
                )
        document["sharedStorageObservedOwned"] = bool(storage_lines) and all(
            expected_shared in line.replace("\\", "/").casefold() for line in storage_lines
        )
        if not document["sharedStorageObservedOwned"]:
            document["result"] = "FAIL"
            document["storageIsolationFailure"] = (
                "actual shared storage location was absent or outside the owned directory"
            )
        if result.returncode or document.get("result") != "PASS":
            document["result"] = "FAIL"
            document["outputTail"] = result.stdout[-2000:]
        return document


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, default=ROOT / "var/native-editor-package.json")
    args = parser.parse_args()
    requested = args.report
    runtime = ROOT / "var"
    if runtime.is_symlink() or runtime.is_junction() or requested.is_symlink():
        raise ValueError("refusing redirected native report")
    args.report = requested.resolve()
    if not args.report.is_relative_to(runtime.resolve()) or args.report.suffix != ".json":
        raise ValueError("native reports must remain under this checkout's var directory")
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.unlink(missing_ok=True)
    result = {
        "kind": "NATIVE_INSTALLATION_AND_TRUST_NOT_LIVE_PROVIDER_ACCEPTANCE",
        "result": "FAIL",
        "runs": [],
    }
    owned = None
    mode = None
    try:
        with owned_directory("iacode-native-editor-") as owned:
            directory = owned["path"]
            workspace = directory / "workspace"
            workspace.mkdir()
            (workspace / "README.md").write_text(
                "Owned clean native installation fixture.\n", encoding="utf-8"
            )
            packages = build(directory / "packages")
            for mode in ("package", "untrusted"):
                native = NativeEditor(
                    directory / mode,
                    workspace,
                    directory / "packages/iacode-0.1.0.vsix",
                    packages["protocolDigest"],
                )
                run = native.run(mode)
                result["runs"].append({"installation": native.installation, **run})
                if run["result"] != "PASS":
                    break
        if (
            len(result["runs"]) == 2
            and owned["removed"]
            and all(run["result"] == "PASS" for run in result["runs"])
        ):
            result["result"] = "PASS"
    except Exception as error:
        result["failure"] = str(error)[:1200]
        if isinstance(error, NativeJobCleanupError):
            result["failedNativeMode"] = mode
            result["processCleanupFailure"] = error.observation
        if getattr(error, "report", None) is not None:
            result["executionFailure"] = error.report
    finally:
        if owned is not None:
            result["ownedTemporaryDirectoryRemoved"] = owned["removed"]
            result["directoryCleanupRetries"] = owned["cleanupRetries"]
            result["directoryCleanup"] = {
                key: owned[key]
                for key in (
                    "removed",
                    "cleanupRetries",
                    "cleanupAttempts",
                    "cleanupElapsedSeconds",
                    "firstSharingLockAfterSeconds",
                    "cleanupFailure",
                )
            }
    args.report.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if result["result"] == "PASS" else 1


if __name__ == "__main__":
    sys.path.insert(0, str(ROOT / "scripts/development-ledger"))
    from ledger_common import use_utf8_stdout

    use_utf8_stdout()
    raise SystemExit(main())
