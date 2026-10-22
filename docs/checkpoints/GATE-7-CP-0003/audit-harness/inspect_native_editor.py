"""Read the actual installed editor adapter/package without starting or changing it."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))
sys.path.insert(0, str(ROOT / "scripts/iacode"))
from ledger_common import find_secrets, utc_now, write_json
from native_editor import cli_command, executable


def main():
    code = executable()
    command = cli_command(code)
    if len(command) != 2:
        raise ValueError("Expected the real Windows installed editor adapter")
    cli = Path(command[1])
    package = next(parent / "package.json" for parent in cli.parents
                   if parent.name == "app" and (parent / "package.json").is_file())
    metadata = json.loads(package.read_text(encoding="utf-8"))
    version = metadata["version"]
    if type(version) is not str or re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", version) is None:
        raise ValueError("Expected an exact installed editor version")
    numbers = tuple(map(int, version.split(".")))
    report = {"observedAt": utc_now(), "kind": "INSTALLED_CAPABILITY_NOT_NATIVE_ACCEPTANCE",
              "version": version, "supportedVersionObserved": numbers >= (1, 138, 0),
              "files": [{"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
                        for path in (code, code.parent / "bin/code.cmd", cli, package)],
              "processStarted": False, "installationPerformed": False, "configurationChanged": False}
    if find_secrets(json.dumps(report)):
        raise ValueError("Unsafe environment metadata")
    write_json(CHECKPOINT / "NATIVE-EDITOR-CAPABILITY.json", report)
    print(json.dumps(report))
    return int(not report["supportedVersionObserved"])


if __name__ == "__main__":
    from ledger_common import use_utf8_stdout
    use_utf8_stdout()
    raise SystemExit(main())
