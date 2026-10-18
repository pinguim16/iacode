"""Execute the complete authored knowledge SQL/HTTP suite in a fresh owned service namespace.

This is targeted causal proof, never the full non-fast verifier or a production fallback. It
starts only real PostgreSQL, Redis and MinIO needed here; each case owns its actual database.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import uuid
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/iacode"))
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))


def docker(*arguments: str) -> str:
    result = subprocess.run(
        ["docker", *arguments],
        cwd=ROOT,
        capture_output=True,
        check=False,
        text=True,
        encoding="utf-8",
        errors="strict",
        timeout=60,
    )
    if result.returncode:
        raise RuntimeError("owned integration Docker observation failed")
    return result.stdout.strip()


def containers() -> dict[str, bool]:
    identities = docker("ps", "-aq", "--no-trunc").splitlines()
    if not identities:
        return {}
    values = json.loads(docker("inspect", *identities))
    return {value["Id"]: value["State"]["Running"] for value in values}


def main() -> int:
    from ledger_common import use_utf8_stdout

    use_utf8_stdout()
    from compose import build_service, compose, wait_for_health
    from desktop_test_support import environment
    from verify import VERIFICATION_PORT_VARIABLES

    owner = "iacode-knowledge-sql-" + uuid.uuid4().hex[:12]
    if not re.fullmatch(r"iacode-knowledge-sql-[0-9a-f]{12}", owner):
        raise ValueError("invalid integration namespace")
    before = containers()
    report = {
        "schemaVersion": "1.0.0",
        "kind": "TARGETED_REAL_SQL_HTTP",
        "owner": owner,
        "result": "FAIL",
        "pytestExitCode": None,
        "cleanup": None,
        "unrelatedContainersPreserved": False,
    }
    values = {
        "COMPOSE_PROJECT_NAME": owner,
        **dict.fromkeys(VERIFICATION_PORT_VARIABLES, "0"),
        "IACODE_DESKTOP_TOKEN": "",
        "IACODE_DESKTOP_TOKEN_EXPIRES_AT": "",
    }
    try:
        with environment(values):
            labels = ("--filter", "label=com.docker.compose.project=" + owner)
            for kind in ("container", "network", "volume"):
                if docker(kind, "ls", "-aq" if kind == "container" else "-q", *labels):
                    raise RuntimeError("fresh integration namespace collision")
            try:
                build_service("api")
                started = compose("up", "-d", "postgres", "redis", "minio", capture=False)
                if not started.ok:
                    raise RuntimeError("owned actual dependencies did not start")
                wait_for_health(("postgres", "redis", "minio"), timeout=180)
                result = compose(
                    "run",
                    "--rm",
                    "--no-deps",
                    "--entrypoint",
                    "",
                    "api",
                    "python",
                    "-m",
                    "pytest",
                    "tests/integration/test_knowledge_engine.py",
                    "-p",
                    "no:cacheprovider",
                    "--no-header",
                    capture=False,
                )
                report["pytestExitCode"] = result.exit_code
            finally:
                removed = compose(
                    "down", "--volumes", "--remove-orphans", capture=False, timeout=180
                )
                report["cleanup"] = {
                    "exitCode": removed.exit_code,
                    **{
                        kind: len(
                            docker(
                                kind, "ls", "-aq" if kind == "container" else "-q", *labels
                            ).splitlines()
                        )
                        for kind in ("container", "volume", "network")
                    },
                }
        after = containers()
        report["unrelatedContainersPreserved"] = all(
            after.get(key) == value for key, value in before.items()
        )
        if (
            report["pytestExitCode"] == 0
            and report["cleanup"] == {"exitCode": 0, "container": 0, "volume": 0, "network": 0}
            and report["unrelatedContainersPreserved"]
        ):
            report["result"] = "PASS"
    except Exception as error:
        report["failureType"] = type(error).__name__
    directory = CHECKPOINT / "suite-attempts"
    number = 1 + len(list(directory.glob("KNOWLEDGE-SQL-RECEIPT-*.json")))
    path = directory / f"KNOWLEDGE-SQL-RECEIPT-{number:04d}.json"
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report), flush=True)
    return 0 if report["result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
