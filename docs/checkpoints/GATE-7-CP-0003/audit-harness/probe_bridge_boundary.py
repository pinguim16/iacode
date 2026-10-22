"""Actual restricted-token transport/write-refusal diagnostic; no model turn."""

from __future__ import annotations

import hashlib
import http.server
import json
import os
import secrets
import subprocess
import sys
import tempfile
import threading
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))
from ledger_common import find_secrets, utc_now, write_json

CHILD = """import json, os, pathlib, urllib.request
transport = False
request = urllib.request.Request(os.environ['IACODE_PROBE_URL'],
    headers={'X-IACode-Capability': os.environ['IACODE_PROBE_CAPABILITY']})
with urllib.request.build_opener(urllib.request.ProxyHandler({})).open(request, timeout=8) as response:
    transport = response.read(32) == b'FIXED_BRIDGE_PROBE_OK'
denied = False
try:
    pathlib.Path(os.environ['IACODE_PROBE_WRITE']).write_bytes(b'PROBE_ONLY')
except PermissionError:
    denied = True
print(json.dumps({'transport': transport, 'privateWriteDenied': denied}))
raise SystemExit(0 if transport and denied else 1)
"""


def main() -> int:
    capability = secrets.token_urlsafe(32)

    class Handler(http.server.BaseHTTPRequestHandler):
        def log_message(self, *_args):
            return

        def do_GET(self):
            valid = (self.path == "/probe"
                     and secrets.compare_digest(
                         self.headers.get("X-IACode-Capability", ""), capability))
            body = b"FIXED_BRIDGE_PROBE_OK" if valid else b"REFUSED"
            self.send_response(200 if valid else 403)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    started = utc_now()
    with tempfile.TemporaryDirectory(prefix="iacode-m2cp3-private-") as temporary:
        private = Path(temporary)
        target = private / "write-probe.bin"
        server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        command = ["C:/Users/cesar/AppData/Local/OpenAI/Codex/bin/896a0166b774037a/codex.exe",
                   "-c", 'windows.sandbox="elevated"', "-c", "features.prefer_mxc=false",
                   "-c", "sandbox_workspace_write.network_access=true", "sandbox",
                   "--cd", str(ROOT), "--include-managed-config", "-P", ":workspace",
                   "--", sys.executable, "-c", CHILD]
        environment = {**os.environ, "PYTHONIOENCODING": "utf-8",
                       "IACODE_PROBE_URL": f"http://127.0.0.1:{server.server_port}/probe",
                       "IACODE_PROBE_CAPABILITY": capability,
                       "IACODE_PROBE_WRITE": str(target)}
        streams = {}
        status, code = "COMPLETED", None
        try:
            result = subprocess.run(command, cwd=ROOT, env=environment, capture_output=True,
                                    timeout=45, check=False)
            code, stdout, stderr = result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired as exc:
            status, stdout, stderr = "TIMEOUT", exc.stdout or b"", exc.stderr or b""
        except OSError:
            status, stdout, stderr = "LAUNCH_ERROR", b"", b""
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=3)
        for name, raw in (("stdout", stdout), ("stderr", stderr)):
            item = {"sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw),
                    "text": None, "refused": True}
            try:
                text = raw.decode("utf-8", errors="strict")
                if len(raw) <= 262144 and capability not in text and not find_secrets(text):
                    item.update(text=text, refused=False)
            except Exception:
                pass  # Remains an explicit neutral refusal, never raw publication.
            streams[name] = item
        unexpected_write = target.exists()
        passed = (status == "COMPLETED" and code == 0 and not unexpected_write
                  and not any(item["refused"] for item in streams.values()))
        receipt = {"startedAt": started, "finishedAt": utc_now(), "status": status,
                   "exitCode": code, "result": "PASS" if passed else "FAIL",
                   "unexpectedPrivateWrite": unexpected_write, "streams": streams,
                   "privateRoot": str(private), "temporaryRootRemoved": False}
    receipt["temporaryRootRemoved"] = not private.exists()
    output = CHECKPOINT / "environment-attempts/bridge-boundary"
    output.mkdir(parents=True, exist_ok=True)
    index = len(list(output.glob("run-*.json"))) + 1
    write_json(output / f"run-{index:04d}.json", receipt)
    print(json.dumps(receipt))
    return 0 if passed and receipt["temporaryRootRemoved"] else 1


if __name__ == "__main__":
    from ledger_common import use_utf8_stdout
    use_utf8_stdout()
    raise SystemExit(main())
