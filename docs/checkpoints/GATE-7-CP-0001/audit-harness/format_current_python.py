"""Use the already built pinned formatter on the explicit current authored Python scope."""

from __future__ import annotations

import subprocess
import sys
import argparse
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/iacode"))
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))

from compose import project_image
from ledger_common import use_utf8_stdout

PATHS = (
    "packages/contracts/src/iacode_contracts/knowledge.py",
    "packages/persistence/src/iacode_persistence/models.py",
    "packages/telemetry/src/iacode_telemetry/logging.py",
    "apps/api/src/iacode_api/knowledge", "apps/api/src/iacode_api/routes/knowledge.py",
    "apps/api/src/iacode_api/config.py", "apps/api/src/iacode_api/lifespan.py",
    "apps/api/src/iacode_api/main.py", "apps/api/src/iacode_api/middleware/correlation.py",
    "apps/api/migrations/versions/0008_knowledge_engine.py",
    "apps/api/tests/knowledge_fixture.py", "apps/api/tests/unit/test_knowledge_api.py",
    "apps/api/tests/unit/test_domain_model.py", "apps/api/tests/unit/test_knowledge_structure.py",
    "apps/api/tests/integration/test_knowledge_engine.py",
    "services/knowledge/src", "services/knowledge/tests",
    "scripts/iacode/knowledge_schema.py", "scripts/iacode/gates/knowledge_tests.py",
    "scripts/iacode/gates/lint.py",
)


def run(*arguments: str) -> int:
    return subprocess.run([
        "docker", "run", "--rm", "--network", "none", "--read-only",
        "--tmpfs", "/tmp:rw,nosuid,size=67108864", "--env", "RUFF_CACHE_DIR=/tmp/ruff-cache",
        "--label", "org.iacode.verification.owner=GATE-7-CP-0001-format",
        "--volume", f"{ROOT}:/repo", "--workdir", "/repo", project_image("api"),
        "ruff", *arguments,
    ], cwd=ROOT, check=False).returncode


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-only", action="store_true")
    options = parser.parse_args()
    for path in PATHS:
        if not (ROOT / path).exists() or not (ROOT / path).resolve().is_relative_to(ROOT.resolve()):
            raise ValueError("format scope must consist of existing current workspace paths")
    if options.check_only:
        return run("check", *PATHS)
    formatted = run("format", *PATHS, "tests/test_gate7_knowledge.py")
    if formatted:
        return formatted
    return run("check", "--fix", *PATHS)


if __name__ == "__main__":
    use_utf8_stdout()
    raise SystemExit(main())
