"""Run an unchanged actual live scenario with bounded metadata-only catalog observations."""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import runpy
import sys
import time
from ctypes import wintypes
from pathlib import Path

from current_resources import child_environment, current_scope_path

sys.path.insert(
    0, str(Path(__file__).resolve().parents[1].parents[2] / "scripts/development-ledger")
)
sys.path.insert(0, str(Path(__file__).resolve().parents[1].parents[2] / "scripts/iacode"))

from audit_runner_bridge import Job, regular, run_owned
from ledger_common import find_secrets, load_json, scope_fingerprint, utc_now, write_json
from native_process import WindowsJob

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]
SCENARIOS = {
    "experience": "experience_store_e2e",
    "desktop": "desktop_e2e",
    "native": "native_editor",
}
NODE = Path(
    "C:/Users/cesar/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe"
)
KNOWN_FAILURES = {
    "live desktop response exceeded its byte bound": "RESPONSE_BOUND",
    "live response authentication failed": "RESPONSE_AUTHENTICATION",
    "live response reflected protected authentication material": "REFLECTED_AUTHENTICATION",
    "actual authorized provider catalog synchronization failed; no model substituted": (
        "SYNC_REFUSED"
    ),
    "the exact authorized model is absent from the fresh catalog; no model substituted": (
        "MODEL_ABSENT"
    ),
}


def inner(scenario, folder):
    import desktop_test_support as support
    import native_editor

    actual = support.request
    observations = []
    native_observations = []

    class ObservedNativeJob(WindowsJob):
        """Read actual owned-handle states; never change statuses, ownership or deadlines."""

        def __init__(self):
            super().__init__()
            self.trace = {"startedAt": utc_now(), "handles": {}, "activeSamples": 0}
            self.actual_wait = self.api.WaitForSingleObject
            self.api.GetExitCodeProcess.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
            self.api.GetExitCodeProcess.restype = wintypes.BOOL

            def observed_wait(handle, timeout):
                status = self.actual_wait(handle, timeout)
                actual_error = ctypes.get_last_error()
                fact = self.trace["handles"].setdefault(str(handle), {"polls": 0})
                fact["polls"] = fact.get("polls", 0) + 1
                now = time.monotonic()
                if fact.get("lastStatus") != status or now - fact.get("lastSample", 0) >= 1:
                    value = wintypes.DWORD()
                    checked = self.api.GetExitCodeProcess(handle, ctypes.byref(value))
                    fact.update(
                        lastStatus=status,
                        lastSample=now,
                        exitCodeRead=bool(checked),
                        processExitCode=value.value if checked else None,
                    )
                ctypes.set_last_error(actual_error)
                return status

            self.api.WaitForSingleObject = observed_wait

        def active(self):
            value = super().active()
            self.trace["activeSamples"] += 1
            self.trace["lastJobActive"] = value
            return value

        def owned_member_handles(self):
            handles = super().owned_member_handles()
            for identifier, handle in handles:
                self.trace["handles"].setdefault(str(handle), {})["processId"] = identifier
            return handles

        def close(self):
            try:
                value = super().close()
                self.trace["result"] = "PASS"
                return value
            except Exception as error:
                self.trace.update(result="FAIL", failureType=type(error).__name__)
                raise
            finally:
                self.trace["finishedAt"] = utc_now()
                native_observations.append(self.trace)

    native_editor.WindowsJob = ObservedNativeJob

    def observed(*arguments, **keywords):
        target = arguments[3]
        catalog = target in {
            "/api/v1/gateway/models/sync",
            "/api/v1/gateway/models?provider=openai&active=true",
        }
        if not catalog:
            return actual(*arguments, **keywords)
        started = time.monotonic()
        row = {"operation": "SYNC" if target.endswith("/sync") else "LIST", "result": "FAIL"}
        observations.append(row)
        try:
            status, value = actual(*arguments, **keywords)
            row.update(status=status, result="HTTP_RESPONSE")
            if isinstance(value, dict):
                outcomes = value.get("outcomes")
                models = value.get("models")
                if isinstance(outcomes, list):
                    row["matchingOutcomeCount"] = sum(
                        isinstance(item, dict) and item.get("provider") == "openai"
                        for item in outcomes
                    )
                    row["providerErrorCount"] = sum(
                        len(item.get("errors", []))
                        for item in outcomes
                        if isinstance(item, dict)
                        and item.get("provider") == "openai"
                        and isinstance(item.get("errors", []), list)
                    )
                if isinstance(models, list):
                    row["catalogModelCount"] = len(models)
                    row["exactAuthorizedModelPresent"] = any(
                        isinstance(item, dict)
                        and item.get("provider") == "openai"
                        and item.get("model") == "gpt-4o-mini"
                        and item.get("active") is True
                        for item in models
                    )
            return status, value
        except Exception as error:
            row.update(
                failureType=type(error).__name__,
                failureCode=KNOWN_FAILURES.get(str(error), "UNCLASSIFIED_NO_RAW_MESSAGE"),
            )
            raise
        finally:
            row["durationMs"] = int((time.monotonic() - started) * 1000)
            write_json(folder / "CATALOG-OBSERVATIONS.json", observations)

    support.request = observed
    report = ROOT / "var" / ("m2-live-diagnostic-" + folder.name + "-" + scenario + ".json")
    if report.exists():
        raise ValueError("FRESH_CANONICAL_REPORT_REQUIRED")
    source = ROOT / "scripts/iacode"
    if scenario != "native":
        source /= "scenarios"
    module = (
        vars(native_editor)
        if scenario == "native"
        else runpy.run_path(str(source / (SCENARIOS[scenario] + ".py")))
    )
    runtime_globals = module["main"].__globals__
    actual_docker = runtime_globals.get("docker")
    snapshots = []
    scope = load_json(current_scope_path())

    def observed_docker(*arguments):
        output = actual_docker(*arguments)
        if arguments == ("ps", "-aq", "--no-trunc"):
            identities = sorted(output.splitlines())
            own = actual_docker(
                "ps",
                "-aq",
                "--no-trunc",
                "--filter",
                "label=com.docker.compose.project=" + scope["inheritedOwnedProject"],
            ).splitlines()
            snapshots.append(
                {
                    "observedAt": utc_now(),
                    "identities": identities,
                    "ownPhaseIdentities": sorted(set(own) | {scope["builderOwnership"]["id"]}),
                }
            )
            missing = sorted(set(snapshots[0]["identities"]) - set(identities))
            write_json(
                folder / "CONTAINER-IDENTITY-OBSERVATIONS.json",
                {
                    "kind": "EXACT_PASSTHROUGH_CANONICAL_IDENTITY_COMPARISON",
                    "snapshots": snapshots,
                    "missingBeforeIdentities": missing,
                    "missingKnownTaskIdentities": sorted(
                        set(missing) & set(snapshots[0]["ownPhaseIdentities"])
                    ),
                    "unrelatedApplicationNamesOrActorAttributionRecorded": False,
                    "originalAssertionChanged": False,
                },
            )
        return output

    if actual_docker is not None:
        runtime_globals["docker"] = observed_docker
    sys.argv = [SCENARIOS[scenario] + ".py", "--report", str(report)]
    try:
        return module["main"]()
    finally:
        write_json(
            folder / "NATIVE-HANDLE-OBSERVATIONS.json",
            {
                "kind": "READ_ONLY_ACTUAL_OWNED_NATIVE_HANDLE_OBSERVATIONS",
                "observations": native_observations,
                "deadlinesOwnershipAndWaitResultsChanged": False,
                "dockerUsedByNativeOnlyScenario": False if scenario == "native" else None,
            },
        )
        if report.is_file():
            regular(report, ROOT)
            raw = report.read_bytes()
            if find_secrets(raw.decode("utf-8", errors="strict")):
                raise ValueError("UNSAFE_CANONICAL_LIVE_REPORT")
            with (folder / "ORIGINAL-PRODUCER.json").open("xb") as stream:
                stream.write(raw)
            report.unlink()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scenario", choices=SCENARIOS)
    parser.add_argument("--inner", type=Path)
    options = parser.parse_args()
    if options.inner:
        folder = options.inner
        base = CHECKPOINT / "causal-attempts/live-stages" / options.scenario
        if folder.parent != base or folder.resolve() != folder or not folder.is_dir():
            raise ValueError("EXACT_OWNED_DIAGNOSTIC_FOLDER_REQUIRED")
        return inner(options.scenario, folder)
    base = CHECKPOINT / "causal-attempts/live-stages" / options.scenario
    base.mkdir(parents=True, exist_ok=True)
    folder = base / f"run-{len(list(base.glob('run-*'))) + 1:04d}"
    folder.mkdir()
    source = scope_fingerprint(ROOT)
    environment = child_environment()
    environment.update(
        IACODE_GATEWAY_SMOKE_MODEL="openai:gpt-4o-mini",
        IACODE_NODE_EXECUTABLE=str(NODE),
    )
    command = (
        sys.executable,
        str(Path(__file__).resolve()),
        options.scenario,
        "--inner",
        str(folder),
    )
    execution, streams = run_owned(Job(command, 10800), ROOT, environment, find_secrets, WindowsJob)
    for name, raw in streams.items():
        with (folder / name).open("xb") as stream:
            stream.write(raw)
    report = folder / "ORIGINAL-PRODUCER.json"
    write_json(
        folder / "RECEIPT.json",
        {
            "observedAt": utc_now(),
            "kind": "TARGETED_UNCHANGED_ACTUAL_LIVE_DIAGNOSTIC_NOT_WHOLE_ACCEPTANCE",
            "scenario": options.scenario,
            "sourceFingerprint": source,
            "sourceUnchanged": source == scope_fingerprint(ROOT),
            "execution": execution,
            "originalReportSha256": hashlib.sha256(report.read_bytes()).hexdigest()
            if report.is_file()
            else None,
            "rawCredentialsOrProviderBodiesRecorded": False,
            "assertionsDeadlinesAndModelUnchanged": True,
        },
    )
    print(
        json.dumps(
            {
                "scenario": options.scenario,
                "exitCode": execution["producer"]["exitCode"],
                "receipt": (folder / "RECEIPT.json").relative_to(ROOT).as_posix(),
            }
        )
    )
    producer = execution["producer"]
    passed = (
        producer["status"] == "COMPLETED"
        and type(producer["exitCode"]) is int
        and producer["exitCode"] == 0
        and execution["cleanup"]["result"] == "PASS"
        and source == scope_fingerprint(ROOT)
        and not any(producer[name]["refusal"] for name in ("stdout", "stderr"))
        and report.is_file()
    )
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
