"""Observe dotenv encoding at the actual Compose boundary without starting services."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "scripts/iacode"))
sys.path.insert(0, str(ROOT / "packages/common/src"))
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))

from compose import read_env_file  # noqa: E402
from iacode_common.redaction import is_placeholder  # noqa: E402
from ledger_common import use_utf8_stdout  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", required=True, type=Path)
    arguments = parser.parse_args()
    report = arguments.report.resolve()
    checkpoint = Path(__file__).resolve().parent.parent
    if report.parent != checkpoint or report.exists():
        raise ValueError("a new current-checkpoint observation report is required")
    example = ROOT / "infra/compose/.env.example"
    names = ("IACODE_DESKTOP_TOKEN", "IACODE_DESKTOP_TOKEN_EXPIRES_AT")
    raw = read_env_file(example, {})
    # Prevent workstation values from taking precedence over the committed template. The
    # resolved config can contain unrelated placeholders; it is never printed or persisted.
    environment = dict(os.environ)
    for name in raw:
        environment.pop(name, None)
    completed = subprocess.run(
        ["docker", "compose", "--project-directory", str(example.parent),
         "--file", str(example.parent / "docker-compose.yml"), "--env-file", str(example),
         "config", "--format", "json"],
        cwd=ROOT, env=environment, capture_output=True, text=True, check=False,
    )
    if completed.returncode:
        raise RuntimeError("Compose could not resolve the committed template")
    config = json.loads(completed.stdout)
    observations = {
        "kind": "READ_ONLY_DOTENV_OBSERVATION_NOT_GATE_VERDICT",
        "templateComposeExitCode": completed.returncode,
        "templateFields": {
            name: {
                "composeValueIsEmpty": config["services"]["api"]["environment"][name] == "",
                "hostParserValueIsEmpty": raw[name] == "",
                "hostParserValueIsPlaceholder": is_placeholder(raw[name]),
            }
            for name in names
        },
        "literalCases": [],
    }
    with tempfile.TemporaryDirectory(prefix="iacode-gate5-dotenv-diagnostic-") as temporary:
        path = Path(temporary) / ".env"
        probe_name = "IACODE_ENV_LITERAL_PROBE"
        environment.pop(probe_name, None)
        for encoding, expected in (
            ('""', ""), ("''", ""), ('"not-placeholder"', "not-placeholder"),
            ("'not-placeholder'", "not-placeholder"),
        ):
            path.write_text(f"{probe_name}={encoding}\n", encoding="utf-8")
            result = subprocess.run(
                ["docker", "compose", "--project-directory", str(Path(temporary)),
                 "--file", "-", "--env-file", str(path), "config", "--format", "json"],
                input='services:\n  probe:\n    image: busybox:1.37.0\n'
                      f'    environment:\n      {probe_name}: ${{{probe_name}}}\n',
                cwd=ROOT, env=environment, capture_output=True, text=True, check=False,
            )
            if result.returncode:
                raise RuntimeError("Compose could not resolve an isolated literal fixture")
            value = json.loads(result.stdout)["services"]["probe"]["environment"][probe_name]
            assert value == expected
            assert is_placeholder(value) == (expected == "")
            observations["literalCases"].append({
                "quoteStyle": "double" if encoding.startswith('"') else "single",
                "inputIsEmpty": expected == "",
                "composeMatchesExpected": value == expected,
                "decodedValueIsPlaceholder": is_placeholder(value),
            })
    rendered = json.dumps(observations, indent=2) + "\n"
    report.write_text(rendered, encoding="utf-8", newline="\n")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    use_utf8_stdout()
    raise SystemExit(main())
