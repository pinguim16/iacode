"""Run frozen canonical client/API jobs through the actual restricted-token bridge."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))
sys.path.insert(0, str(ROOT / "scripts/iacode"))
from audit_runner_bridge import ClosedBridge, FrozenInputs, Job, regular
from owned_docker_scope import child_environment, snapshot
from ledger_common import find_secrets, load_json, utc_now, write_json
from native_process import WindowsJob
from policies import gate_definitions

CHILD = """import json, os, pathlib, time, urllib.request
try:
    pathlib.Path(os.environ['IACODE_BRIDGE_PRIVATE_WRITE']).write_bytes(b'REFUSE_WRITE')
except PermissionError:
    pass
else:
    print('PRIVATE_WRITE_NOT_DENIED'); raise SystemExit(2)
base = os.environ['IACODE_BRIDGE_URL']
capability = os.environ['IACODE_BRIDGE_CAPABILITY']
opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
def request(path, body=None):
    headers = {'X-IACode-Capability': capability}
    if body is not None: headers['Content-Type'] = 'application/json'
    with opener.open(urllib.request.Request(base + path, body, headers), timeout=10) as response:
        return json.load(response)
for key in ('clientTests', 'apiTests'):
    request('/jobs', json.dumps({'job': key}).encode())
    deadline = time.monotonic() + 1200
    while True:
        result = request('/jobs/' + key)
        if result['status'] == 'DONE': break
        if time.monotonic() >= deadline: raise SystemExit(3)
        time.sleep(1)
    print(json.dumps({'job': key, 'result': result['result']}), flush=True)
    if result['result'] != 'PASS': raise SystemExit(1)
"""


def main():
    started = utc_now()
    folder = CHECKPOINT / "environment-attempts/canonical-bridge"
    folder.mkdir(parents=True, exist_ok=True)
    index = len(list(folder.glob("run-*"))) + 1
    output = folder / f"run-{index:04d}"
    output.mkdir()
    receipt = {"startedAt": started, "kind": "INTERNAL_CAPABILITY_NOT_INDEPENDENT_AUDIT",
               "result": "FAIL", "before": snapshot()}
    with tempfile.TemporaryDirectory(prefix="iacode-m2cp3-frozen-probe-") as temporary:
        private = Path(temporary).absolute()
        names = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
                               cwd=ROOT, capture_output=True, check=True).stdout.decode().split("\0")
        paths = []
        for name in sorted(set(names) - {""}):
            path = ROOT / name
            regular(path, ROOT)
            destination = private / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, destination)
            paths.append(destination)
        # Build/unit capability does not require the workstation's real provider credentials.
        shutil.copyfile(private / "infra/compose/.env.example", private / "infra/compose/.env")
        frozen = FrozenInputs(private, paths)
        definitions = gate_definitions(private)
        jobs = {key: Job((sys.executable, *definitions[key]["command"][1:]), 1100)
                for key in ("clientTests", "apiTests")}
        environment = child_environment()
        environment["COMPOSE_PROJECT_NAME"] = load_json(CHECKPOINT / "OWNED-DOCKER-SCOPE.json")["inheritedOwnedProject"]
        environment["IACODE_VERSION"] = "0.1.0"
        environment["PYTHONNOUSERSITE"] = "1"
        environment.pop("PYTHONPATH", None)
        bridge = ClosedBridge(frozen, jobs, environment, find_secrets, WindowsJob,
                              (Path(sys.executable), Path(shutil.which("docker"))))
        server = bridge.listen()
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        command = ["C:/Users/cesar/AppData/Local/OpenAI/Codex/bin/896a0166b774037a/codex.exe",
                   "-c", 'windows.sandbox="elevated"', "-c", "features.prefer_mxc=false",
                   "-c", "sandbox_workspace_write.network_access=true", "sandbox",
                   "--cd", str(ROOT), "--include-managed-config", "-P", ":workspace",
                   "--", sys.executable, "-c", CHILD]
        client_env = {**os.environ, "PYTHONIOENCODING": "utf-8",
                      "IACODE_BRIDGE_URL": f"http://127.0.0.1:{server.server_port}",
                      "IACODE_BRIDGE_CAPABILITY": bridge.capability,
                      "IACODE_BRIDGE_PRIVATE_WRITE": str(private / "private-write-probe.bin")}
        try:
            completed = subprocess.run(command, cwd=ROOT, env=client_env, capture_output=True,
                                       timeout=2400, check=False)
            receipt["restrictedClientExitCode"] = completed.returncode
            for name, raw in (("stdout", completed.stdout), ("stderr", completed.stderr)):
                receipt[name] = {"sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw), "refused": True}
                try:
                    text = raw.decode("utf-8", errors="strict")
                    if len(raw) <= 262144 and bridge.capability not in text and not find_secrets(text):
                        (output / (name + ".log")).write_bytes(raw)
                        receipt[name]["refused"] = False
                except Exception:
                    pass  # Explicit refusal remains; raw stream is never published.
        finally:
            bridge.close()
            thread.join(timeout=3)
            # Archive already scanned original bytes before deleting their private source tree.
            for key, result in bridge.results.items():
                write_json(output / (key + ".json"), result)
                for name, raw in bridge.artifacts.get(key, {}).items():
                    (output / (key + "-" + name)).write_bytes(raw)
            receipt["privateSourceRoot"] = str(private)
            receipt["frozenSourceFiles"] = len(frozen.hashes)
            receipt["jobs"] = bridge.results
            receipt["unexpectedPrivateWrite"] = (private / "private-write-probe.bin").exists()
            receipt["after"] = snapshot()
    receipt["privateSourceRemoved"] = not private.exists()
    passed = (receipt.get("restrictedClientExitCode") == 0
              and len(receipt["jobs"]) == 2
              and all(value.get("result") == "PASS" for value in receipt["jobs"].values())
              and not receipt["unexpectedPrivateWrite"] and receipt["privateSourceRemoved"]
              and not any(receipt.get(name, {}).get("refused", True) for name in ("stdout", "stderr")))
    receipt.update(finishedAt=utc_now(), result="PASS" if passed else "FAIL")
    write_json(output / "RECEIPT.json", receipt)
    print(json.dumps({"result": receipt["result"], "output": output.relative_to(ROOT).as_posix(),
                      "privateSourceRemoved": receipt["privateSourceRemoved"]}))
    return 0 if passed else 1


if __name__ == "__main__":
    from ledger_common import use_utf8_stdout
    use_utf8_stdout()
    raise SystemExit(main())
