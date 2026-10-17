"""Mechanical Ruff formatting/import rewrites only, not a lint verdict or check suppression."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "scripts/iacode"))
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))

from compose import project_image
from ledger_common import use_utf8_stdout

PATHS = (
    "packages/contracts/src/iacode_contracts/experience.py", "services/experience",
    "apps/api/src/iacode_api/experience", "apps/api/src/iacode_api/routes/experiences.py",
    "apps/api/tests/integration/test_experience_store.py", "apps/api/tests/unit/test_experience_api.py",
    "apps/api/migrations/versions/0007_experience_store.py",
    "scripts/iacode/experience_schema.py", "scripts/iacode/gates/experience_tests.py",
    "apps/api/src/iacode_api/middleware/correlation.py",
    "packages/telemetry/src/iacode_telemetry/logging.py",
    "scripts/iacode/scenarios/experience_store_e2e.py",
    "scripts/iacode/scenarios/experience_source_adversary.py",
    "scripts/iacode/desktop_test_support.py",
)


def main() -> int:
    prefix = ["docker", "run", "--rm", "--env", "RUFF_CACHE_DIR=/tmp/ruff-cache",
              "--volume", f"{ROOT}:/repo", "--workdir", "/repo", project_image("api"), "ruff"]
    for command in (("format", *PATHS), ("check", "--fix-only", *PATHS)):
        result = subprocess.run([*prefix, *command], cwd=ROOT, text=True, encoding="utf-8",
                                errors="replace", check=False)
        if result.returncode:
            return result.returncode
    print("MECHANICAL_FORMATTING_COMPLETE; no lint acceptance issued")
    return 0


if __name__ == "__main__":
    use_utf8_stdout()
    raise SystemExit(main())
