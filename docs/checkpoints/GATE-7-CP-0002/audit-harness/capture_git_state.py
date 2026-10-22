from __future__ import annotations

import argparse
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def run(root: Path, *arguments: str) -> dict[str, object]:
    completed = subprocess.run(
        ["git", *arguments],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return {
        "arguments": list(arguments),
        "exitCode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Capture final Git state without changing it.")
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    commands = {
        "status": run(root, "status", "--short", "--branch", "--untracked-files=all"),
        "branch": run(root, "branch", "--show-current"),
        "head": run(root, "rev-parse", "HEAD"),
        "subjectTag": run(
            root,
            "rev-parse",
            "--verify",
            "refs/tags/iacode-checkpoints/GATE-7-CP-0001^{commit}",
        ),
    }
    report = {
        "schemaVersion": "1.0.0",
        "capturedAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "root": str(root),
        "gitConfigGlobalOverridePresent": bool(os.environ.get("GIT_CONFIG_GLOBAL")),
        "commands": commands,
        "result": "PASS"
        if all(item["exitCode"] == 0 for item in commands.values())
        else "FAIL",
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(
        f"FINAL_GIT_STATE={report['result']} "
        f"head={commands['head']['stdout'].strip()} "
        f"branch={commands['branch']['stdout'].strip()}"
    )
    return 0 if report["result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
