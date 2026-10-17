"""Run all new real SQL/HTTP cases plus the complete migration suite in a fresh owned namespace."""

from __future__ import annotations

import hashlib
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

from compose import build_service, compose, wait_for_health
from desktop_test_support import environment
from ledger_common import find_secrets, scope_fingerprint, utc_now, use_utf8_stdout, write_json
from verify import VERIFICATION_PORT_VARIABLES


def docker(*arguments: str) -> str:
    result = subprocess.run(["docker", *arguments], cwd=ROOT, capture_output=True, text=True,
                            encoding="utf-8", errors="replace", check=False)
    if result.returncode:
        raise RuntimeError("owned integration engine observation failed")
    return result.stdout.strip()


def main() -> int:
    project = "iacode-experience-tests-" + uuid.uuid4().hex[:12]
    before = set(docker("ps", "-aq", "--no-trunc").splitlines())
    fingerprint = scope_fingerprint(ROOT)
    directory = CHECKPOINT / "suite-attempts"
    directory.mkdir(exist_ok=True)
    sequence = len(list(directory.glob("INTEGRATION-*.json"))) + 1
    name = f"INTEGRATION-{sequence:04d}"
    report = {"schemaVersion": "1.0.0", "kind": "ACTUAL_OWNED_POSTGRESQL_HTTP_MIGRATIONS",
              "observedAt": utc_now(), "composeProject": project, "sourceFingerprint": fingerprint,
              "result": "FAIL", "commands": [], "containerIdentitiesBefore": sorted(before)}
    owned = {"COMPOSE_PROJECT_NAME": project, **dict.fromkeys(VERIFICATION_PORT_VARIABLES, "0"),
             "IACODE_DESKTOP_TOKEN": "", "IACODE_DESKTOP_TOKEN_EXPIRES_AT": ""}
    with environment(owned):
        if docker("ps", "-aq", "--filter", "label=com.docker.compose.project=" + project):
            raise RuntimeError("fresh integration namespace collision; no cleanup authorized")
        try:
            build_service("api")
            start = compose("up", "-d", "postgres", "redis", "minio", "minio-bootstrap", timeout=300)
            report["commands"].append({"phase": "dependencies", "exitCode": start.exit_code})
            if not start.ok:
                raise RuntimeError("owned real dependency startup failed")
            wait_for_health(("postgres", "redis", "minio"), timeout=150)
            arguments = ("run", "--rm", "--no-deps", "--entrypoint", "", "api", "python", "-m",
                         "pytest", "tests/integration/test_experience_store.py",
                         "tests/integration/test_migrations.py", "-p", "no:cacheprovider", "--no-header")
            result = compose(*arguments, capture=True, timeout=1200)
            raw = result.output.encode("utf-8")
            # Capture before interpreting or cleaning the namespace; unsafe output is not exported.
            findings = find_secrets(result.output)
            if not findings:
                (directory / (name + ".log")).write_bytes(raw)
                report["safeOutputArtifact"] = (directory / (name + ".log")).relative_to(ROOT).as_posix()
            report["commands"].append({"phase": "complete-selected-suites", "arguments": list(arguments),
                "exitCode": result.exit_code, "outputSha256": hashlib.sha256(raw).hexdigest(),
                "outputBytes": len(raw), "unsafeOutputOccurrences": len(findings),
                "summaryFragments": re.findall(r"\d+ (?:passed|failed|errors?|skipped|warnings?)", result.output)[-12:]})
            report["result"] = "PASS" if result.ok and not findings else "FAIL"
        except Exception as error:
            report["failure"] = {"type": type(error).__name__, "code": "OWNED_INTEGRATION_FAILED"}
        finally:
            if not re.fullmatch(r"iacode-experience-tests-[0-9a-f]{12}", project):
                raise RuntimeError("integration cleanup ownership invalid")
            removed = compose("down", "--volumes", "--remove-orphans", timeout=180)
            report["cleanup"] = {"exitCode": removed.exit_code,
                "remainingContainers": len(docker("ps", "-aq", "--filter",
                    "label=com.docker.compose.project=" + project).splitlines()),
                "remainingVolumes": len(docker("volume", "ls", "-q", "--filter",
                    "label=com.docker.compose.project=" + project).splitlines()),
                "remainingNetworks": len(docker("network", "ls", "-q", "--filter",
                    "label=com.docker.compose.project=" + project).splitlines())}
    after = set(docker("ps", "-aq", "--no-trunc").splitlines())
    report["containerIdentitiesAfter"] = sorted(after)
    report["missingOriginalContainerIdentities"] = sorted(before - after)
    report["operationalContainerIdentitiesPreserved"] = before <= after
    report["sourceUnchanged"] = scope_fingerprint(ROOT) == fingerprint
    if (report["cleanup"] != {"exitCode": 0, "remainingContainers": 0, "remainingVolumes": 0,
                              "remainingNetworks": 0}
            or not report["operationalContainerIdentitiesPreserved"] or not report["sourceUnchanged"]):
        report["result"] = "FAIL"
    write_json(directory / (name + ".json"), report)
    print(json.dumps(report, ensure_ascii=False))
    return 0 if report["result"] == "PASS" else 1


if __name__ == "__main__":
    use_utf8_stdout()
    raise SystemExit(main())
