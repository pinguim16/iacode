"""Read exact executable/config identities without disclosing configuration contents."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(
    0, str(Path(__file__).resolve().parents[1].parents[2] / "scripts/development-ledger")
)
from ledger_common import find_secrets, load_json, utc_now, write_json

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    before = load_json(CHECKPOINT / "ENVIRONMENT-SCOPE.json")
    configurations = []
    for row in before["globalConfigurations"]:
        current = digest(Path(row["path"]))
        configurations.append(
            {
                "path": row["path"],
                "before": row["before"],
                "after": current,
                "unchanged": current == row["before"],
            }
        )
    versions = []
    for name, path in (
        ("python", Path(sys.executable)),
        ("node", Path("C:/Program Files/nodejs/node.exe")),
        (
            "bundled-node",
            Path(
                "C:/Users/cesar/.cache/codex-runtimes/codex-primary-runtime/d"
                "ependencies/node/bin/node.exe"
            ),
        ),
        ("git", Path("C:/Program Files/Git/cmd/git.exe")),
        ("docker", Path("C:/Program Files/Docker/Docker/resources/bin/docker.exe")),
        ("codex", Path("C:/Users/cesar/AppData/Local/OpenAI/Codex/bin/896a0166b774037a/codex.exe")),
    ):
        result = subprocess.run(
            [str(path), "--version"], cwd=ROOT, capture_output=True, timeout=20, check=False
        )
        value = {
            "name": name,
            "path": str(path),
            "sha256": digest(path),
            "exitCode": result.returncode,
            "version": None,
            "refusal": None,
        }
        try:
            raw = result.stdout + result.stderr
            text = raw.decode("utf-8", errors="strict").strip()
            if len(raw) > 4096 or find_secrets(text):
                value["refusal"] = "UNSAFE_VERSION_OUTPUT"
            else:
                value["version"] = text
        except Exception:
            value["refusal"] = "VERSION_OUTPUT_REFUSED"
        versions.append(value)
    folder = CHECKPOINT / "environment-observations"
    folder.mkdir(exist_ok=True)
    index = len(list(folder.glob("run-*.json"))) + 1
    report = {
        "observedAt": utc_now(),
        "globalConfigurations": configurations,
        "executables": versions,
        "nativeVerificationRuntime": (
            "bundled-node; explicit per-child selection only; no installation or PATH change"
        ),
        "allUnchanged": all(row["unchanged"] for row in configurations),
        "applicationRestartsPerformed": False,
        "otherChatSettingWritesPerformed": False,
        "note": (
            "Other-chat field records absence of operator writes, not a d"
            "atabase-wide hash assertion."
        ),
    }
    write_json(folder / f"run-{index:04d}.json", report)
    print(json.dumps(report))
    return int(
        not report["allUnchanged"] or any(row["refusal"] or row["exitCode"] for row in versions)
    )


if __name__ == "__main__":
    from ledger_common import use_utf8_stdout

    use_utf8_stdout()
    raise SystemExit(main())
