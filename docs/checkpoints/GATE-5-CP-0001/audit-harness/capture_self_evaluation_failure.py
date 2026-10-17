"""Preserve failed self-evaluation evidence before its owned stack is torn down."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/iacode"))
sys.path.insert(0, str(ROOT / "packages/common/src"))
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))
from iacode_common.secret_scanning import find_secret_kinds  # noqa: E402
from verify import failure_diagnostics, verification_environment  # noqa: E402
from ledger_common import use_utf8_stdout  # noqa: E402

READ_EVIDENCE = r'''
import hashlib
import sys
from iacode_api.config import get_settings
from iacode_api.storage.client import create_client

digest, size = sys.argv[1], int(sys.argv[2])
settings = get_settings()
client = create_client(settings)
response = client.get_object(settings.minio_bucket, "quality/evidence/" + digest)
try:
    content = response.read()
finally:
    response.close()
    response.release_conn()
assert len(content) == size and hashlib.sha256(content).hexdigest() == digest
sys.stdout.buffer.write(content)
'''


def strings(value: object):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from strings(item)


def main() -> int:
    destination = CHECKPOINT / "QUALITY-IACODE-DIAGNOSIS-0001.json"
    if destination.exists():
        raise ValueError("the original failure observation must not be overwritten")
    progress = json.loads((CHECKPOINT / "FULL-VERIFY-PROGRESS.json").read_text(encoding="utf-8"))
    clone = Path(progress["clone"])
    scenario = json.loads((clone / "var/quality-iacode.json").read_text(encoding="utf-8"))
    if scenario.get("result") != "FAIL":
        raise ValueError("a failed actual self-evaluation report is required")
    run_id = next(artifact["runId"] for artifact in scenario["scenarios"][0]["artifacts"]
                  if artifact["kind"] == "quality-run")
    if not re.fullmatch(r"[a-f0-9-]{36}", run_id):
        raise ValueError("unexpected actual run identity")
    project = verification_environment(clone, {})["COMPOSE_PROJECT_NAME"]
    container = project + "-api"
    port = subprocess.run(["docker", "port", container, "8000/tcp"], capture_output=True,
                          text=True, encoding="utf-8", errors="strict", check=True).stdout.strip()
    if not re.fullmatch(r"127\.0\.0\.1:[1-9][0-9]{3,4}", port):
        raise ValueError("the exact owned API is not bound to a numeric loopback port")
    with urllib.request.urlopen(f"http://{port}/api/v1/quality-runs/{run_id}", timeout=30) as response:
        detail = json.load(response)
    failed = [row for row in detail["results"] if row["status"] not in ("PASSED", "NOT_APPLICABLE")]
    observations = []
    for index, result in enumerate(failed, 1):
        artifacts = []
        for evidence in result["evidence"]:
            digest, size = evidence["digest"], evidence["sizeBytes"]
            if not re.fullmatch(r"[a-f0-9]{64}", digest) or not 0 <= size <= 8 * 1024 * 1024:
                raise ValueError("unexpected bounded evidence metadata")
            completed = subprocess.run(
                ["docker", "exec", "-i", container, "python", "-", digest, str(size)],
                input=READ_EVIDENCE.encode("utf-8"), capture_output=True, check=False,
            )
            if completed.returncode:
                raise RuntimeError("the exact owned evidence read failed")
            content = completed.stdout
            if len(content) != size or hashlib.sha256(content).hexdigest() != digest:
                raise ValueError("read-back differs from the actual content-addressed declaration")
            if find_secret_kinds(content.decode("utf-8")):
                raise ValueError("evidence cannot be exported because the canonical scanner refuses it")
            path = CHECKPOINT / f"QUALITY-IACODE-UNIT-RED-0001-{index}-{len(artifacts) + 1}.json"
            if path.exists():
                raise ValueError("original evidence observation already exists")
            document = json.loads(content)
            path.write_bytes(content)
            artifacts.append({"path": path.name, "sha256": digest, "bytes": size,
                              **failure_diagnostics("\n".join(strings(document)))})
        observations.append({**{key: result[key] for key in (
            "checkId", "status", "exitCode", "durationMs", "timedOut", "truncated", "sandboxId")},
                             "evidence": artifacts})
    report = {"kind": "OBSERVED_FAILED_SELF_EVALUATION_NOT_GATE_VERDICT",
              "subjectCommit": progress["subjectCommit"], "composeProject": project,
              "runId": run_id, "state": detail["run"]["state"],
              "verdict": detail["run"]["verdict"], "totalChecks": len(detail["checks"]),
              "totalResults": len(detail["results"]), "failedResults": observations}
    destination.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    use_utf8_stdout()
    raise SystemExit(main())
