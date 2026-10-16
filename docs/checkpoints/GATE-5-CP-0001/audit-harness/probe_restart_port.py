#!/usr/bin/env python3
"""Observe actual engine-allocated host-port identity over restart on one owned HTTP actor."""

from __future__ import annotations

import http.client
import json
import subprocess
import time
import uuid


def docker(*args):
    result = subprocess.run(["docker", *args], text=True, encoding="utf-8",
                            errors="replace", capture_output=True, check=False, timeout=60)
    if result.returncode:
        raise RuntimeError(result.stderr[-500:])
    return result.stdout.strip()


def main() -> int:
    name = "iacode-desktop-port-probe-" + uuid.uuid4().hex[:12]
    report = {"kind": "ACTUAL_OWNED_ENGINE_HOST_PORT_RESTART_OBSERVATION", "container": name}
    try:
        docker("run", "--rm", "-d", "--name", name, "--publish", "127.0.0.1:0:8000",
               "--workdir", "/tmp", "iacode/api:0.1.0", "python", "-m", "http.server",
               "8000", "--bind", "0.0.0.0")
        for phase in ("before", "after"):
            port = int(docker("port", name, "8000").rsplit(":", 1)[1])
            report[phase + "Port"] = port
            attempts = 0
            deadline = time.monotonic() + 30
            while time.monotonic() < deadline:
                attempts += 1
                connection = http.client.HTTPConnection("127.0.0.1", port, timeout=2)
                try:
                    connection.request("GET", "/")
                    if connection.getresponse().status == 200:
                        break
                except OSError:
                    time.sleep(0.1)
                finally:
                    connection.close()
            else:
                raise RuntimeError("owned published HTTP endpoint was not ready")
            report[phase + "ForwardingAttempts"] = attempts
            if phase == "before":
                docker("restart", name)
        report["hostPortChanged"] = report["beforePort"] != report["afterPort"]
        report["result"] = "PASS"
    finally:
        docker("rm", "-f", name)
        report["ownedContainerRemoved"] = not docker("ps", "-aq", "--filter", "name=^/" + name + "$")
    print(json.dumps(report, indent=2))
    return 0 if report["result"] == "PASS" and report["ownedContainerRemoved"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
