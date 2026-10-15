"""Both artifact implementations refuse prohibited bytes before any external operation."""

from __future__ import annotations

import asyncio
from types import SimpleNamespace

import pytest
from iacode_sandbox.artifacts import MemoryArtifactSink, MinioArtifactSink
from iacode_sandbox.output_security import OutputSecurityError
from iacode_sandbox.store import MemorySandboxStore


def test_memory_artifact_sink_rejects_exact_secret_bytes_without_writes() -> None:
    store = MemorySandboxStore()
    sink = MemoryArtifactSink(store)
    with pytest.raises(OutputSecurityError) as refusal:
        asyncio.run(sink.put(
            run_id="r-1", tool_request_id="t-1", name="stdout.log", kind="sandbox.stdout",
            content=("gh" + "p_" + "y" * 20).encode(),
        ))
    assert refusal.value.code == "SANDBOX_OUTPUT_SECRET_DETECTED"
    assert sink.objects == {} and store.artifacts == []


def test_minio_artifact_sink_rejects_exact_secret_bytes_before_client_or_metadata() -> None:
    calls = []
    store = MemorySandboxStore()
    sink = MinioArtifactSink(SimpleNamespace(put_object=lambda *_a, **_k: calls.append("write")),
                             "artifacts", store)
    with pytest.raises(OutputSecurityError) as refusal:
        asyncio.run(sink.put(
            run_id="r-1", tool_request_id="t-1", name="stdout.log", kind="sandbox.stdout",
            content=("gh" + "p_" + "y" * 20).encode(),
        ))
    assert refusal.value.code == "SANDBOX_OUTPUT_SECRET_DETECTED"
    assert calls == [] and store.artifacts == []


def test_minio_artifact_sink_clean_control_performs_the_real_write_path() -> None:
    calls = []
    store = MemorySandboxStore()
    sink = MinioArtifactSink(SimpleNamespace(put_object=lambda *_a, **_k: calls.append("write")),
                             "artifacts", store)
    reference = asyncio.run(sink.put(
        run_id="r-1", tool_request_id="t-1", name="stdout.log", kind="sandbox.stdout",
        content=b"clean output",
    ))
    assert calls == ["write"] and len(store.artifacts) == 1
    assert reference.size_bytes == len(b"clean output")
