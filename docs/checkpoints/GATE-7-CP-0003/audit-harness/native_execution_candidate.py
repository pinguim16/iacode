"""Unreleased M2-F-002 candidate; canonical sources remain unchanged during baseline."""

from __future__ import annotations

import hashlib
import math
import os
import signal
import subprocess
import tempfile
from contextlib import contextmanager
from pathlib import Path

from client_checks import MAX_OBSERVATION_BYTES, _safe_observation, _safe_stream
from native_process import NativeJobCleanupError


class NativeExecutionError(RuntimeError):
    """Bounded observations, never arbitrary native exception messages."""

    def __init__(self, report: dict):
        self.report = report
        super().__init__("native owned execution failed; structured observations retained")


@contextmanager
def owned_capture(release: dict):
    stream = tempfile.TemporaryFile()
    try:
        yield stream
    finally:
        try:
            stream.close()
            release["result"] = "PASS"
        except OSError as error:
            # This is a recorded failure, not a suppressed success. The caller
            # raises with its primary observation after this exact handle release.
            release.update(result="FAIL", errorType=type(error).__name__)


def observe_native(stream) -> dict:
    digest = hashlib.sha256()
    raw = bytearray()
    try:
        stream.flush()
        stream.seek(0, os.SEEK_END)
        size = remaining = stream.tell()
        stream.seek(0)
        # A timed-out producer may still write. Read only the prefix whose end was
        # observed now, not an unbounded moving EOF before cleanup can run.
        while remaining:
            block = stream.read(min(65536, remaining))
            if not block:
                raise OSError("producer prefix changed during observation")
            remaining -= len(block)
            digest.update(block)
            if size <= MAX_OBSERVATION_BYTES:
                raw.extend(block)
    except OSError:
        return {"text": None, "sha256": None, "bytes": None, "refusal": "OUTPUT_READ_FAILED"}
    if size > MAX_OBSERVATION_BYTES:
        return {"text": None, "sha256": digest.hexdigest(), "bytes": size, "refusal": "OUTPUT_LIMIT"}
    return _safe_stream(bytes(raw))


def safe_cleanup_facts(value) -> dict:
    allowed = {"jobOwned", "remainingBeforeCleanup", "remainingAfterCleanup", "observedProcessCount",
               "signaledProcessCount", "forcedTermination", "naturalExitBudgetWithinOriginalDeadlineSeconds",
               "result", "phase", "totalDeadlineSeconds", "naturalExitBudgetSeconds", "remainingJobActive",
               "pendingProcessCount", "lastObservedElapsedSeconds"}
    if type(value) is not dict or set(value) - allowed:
        return {"refusal": "UNSAFE_CLEANUP_FACTS"}
    for key, item in value.items():
        if (item is None or type(item) in (bool, int)
                or type(item) is float and math.isfinite(item)
                or key == "result" and item == "FAIL"
                or key == "phase" and item in ("MEMBER_SNAPSHOT", "NATURAL_DRAIN", "FORCE_SNAPSHOT", "FORCED_DRAIN")):
            continue
        return {"refusal": "UNSAFE_CLEANUP_FACTS"}
    return dict(value)


def execute_owned(arguments: list[str], *, environment: dict[str, str], timeout: int | float,
                  root: Path, job_factory, as_node: bool = False) -> subprocess.CompletedProcess:
    environment = dict(environment)
    environment.pop("ELECTRON_RUN_AS_NODE", None)
    if as_node:
        environment["ELECTRON_RUN_AS_NODE"] = "1"
    producer = {"status": "LAUNCH_ERROR", "exitCode": None, "arguments": list(arguments)}
    # No raw argument list is published if the same canonical scanner refuses it.
    import json

    if _safe_stream(json.dumps(arguments, ensure_ascii=True))["refusal"]:
        producer.update(arguments=None, argumentsRefused=True)
    job = process = None
    cleanup = {"result": "NOT_CREATED", "observation": None}
    cleanup_error = None
    release = {"result": "NOT_EXECUTED"}
    with owned_capture(release) as stream:
        try:
            options = {"start_new_session": True}
            if os.name == "nt":
                job = job_factory()
                startup = subprocess.STARTUPINFO()
                startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startup.wShowWindow = subprocess.SW_HIDE
                options = {"startupinfo": startup,
                           "creationflags": subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.CREATE_NO_WINDOW | 4}
            process = subprocess.Popen(arguments, cwd=root, env=environment, stdin=subprocess.DEVNULL,
                                       stdout=stream, stderr=subprocess.STDOUT, **options)
            if job:
                job.attach_and_resume(process)
            producer["status"] = "RUNNING"
            try:
                producer["exitCode"] = process.wait(timeout=timeout)
                producer["status"] = "COMPLETED"
            except subprocess.TimeoutExpired:
                producer["status"] = "TIMEOUT"
        except Exception as error:
            producer.update(status="LAUNCH_ERROR", launchErrorType=type(error).__name__)
        finally:
            fact = observe_native(stream)
            producer.update(stdout=fact["text"], stdoutSha256=fact["sha256"],
                            stdoutBytes=fact["bytes"], stdoutRefusal=fact["refusal"],
                            stderr="", stderrSha256=hashlib.sha256(b"").hexdigest(),
                            stderrBytes=0, stderrRefusal=None, mergedStreams=True,
                            capturedBeforeCleanup=True)
            try:
                if job is not None:
                    if process is not None and not job.attached and process.poll() is None:
                        process.kill()  # This exact still-suspended Popen handle only.
                    observation = safe_cleanup_facts(job.close())
                    cleanup = {"result": "FAIL" if observation.get("refusal") else "PASS",
                               "observation": observation}
                elif process is not None:
                    try:
                        os.killpg(process.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass  # Only the exact owned session group is absent.
                    cleanup = {"result": "PASS", "observation": None}
            except NativeJobCleanupError as error:
                facts = safe_cleanup_facts(error.observation)
                cleanup_error = NativeJobCleanupError("owned native job cleanup failed", facts)
                cleanup = {"result": "FAIL", "observation": facts}
            except Exception as error:
                cleanup = {"result": "FAIL", "errorType": type(error).__name__, "observation": None}
            if process is not None:
                try:
                    process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    cleanup.update(result="FAIL", ownedProcessStillAlive=True)
                except OSError as error:
                    cleanup.update(result="FAIL", processWaitErrorType=type(error).__name__)
    report = {"schemaVersion": "1.0.0", "result": "FAIL", "producer": producer,
              "cleanup": cleanup, "outputRelease": release}
    safe = _safe_observation(producer)
    if (producer["status"] == "COMPLETED" and producer["exitCode"] == 0 and safe
            and cleanup["result"] == "PASS" and release["result"] == "PASS"):
        report["result"] = "PASS"
    if cleanup_error is not None:
        cleanup_error.report, cleanup_error.producer = report, producer
        raise cleanup_error from None
    if (not safe or cleanup["result"] != "PASS" or release["result"] != "PASS"
            or producer["status"] == "LAUNCH_ERROR"):
        raise NativeExecutionError(report) from None
    if producer["status"] == "TIMEOUT":
        error = subprocess.TimeoutExpired(arguments, timeout, output=producer["stdout"], stderr="")
        error.report, error.producer = report, producer
        raise error from None
    result = subprocess.CompletedProcess(arguments, producer["exitCode"], producer["stdout"], "")
    result.owned_tree_cleanup = cleanup["observation"]
    result.execution = report
    return result
