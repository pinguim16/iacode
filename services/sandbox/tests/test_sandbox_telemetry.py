"""The sandbox's instruments: the declared names, low-cardinality labels, and no content."""

from __future__ import annotations

import asyncio
import logging

from iacode_sandbox.telemetry import (
    METRIC_NAMES,
    PERMITTED_LABELS,
    SandboxMetrics,
    sandbox_log_fields,
)
from prometheus_client import CollectorRegistry, generate_latest
from sandbox_fixtures import FakeBackend, fake_service, request


class SandboxMetricsTests:
    def test_every_required_instrument_exists(self) -> None:
        registry = CollectorRegistry()
        SandboxMetrics(registry)
        exposed = generate_latest(registry).decode("utf-8")
        for name in METRIC_NAMES:
            assert name in exposed, name

    def test_no_instrument_declares_a_label_outside_the_permitted_set(self) -> None:
        registry = CollectorRegistry()
        SandboxMetrics(registry)
        for collector in registry._collector_to_names:  # reading the registry, not writing it
            labels = set(getattr(collector, "_labelnames", ()))
            assert labels <= PERMITTED_LABELS, labels

    def test_a_command_never_becomes_a_label(self) -> None:
        backend = FakeBackend(responses=[{"ok": True, "result": {
            "started": True, "exitCode": 0, "stdout": "", "stderr": "", "durationMs": 1,
            "timedOut": False, "truncated": False}}])
        service, _store = fake_service(backend)
        secret_command = "echo very-specific-command-text-9731"
        asyncio.run(service.execute(request("shell.exec", {"command": secret_command},
                                            run_id="r-1")))
        exposed = generate_latest(service.metrics.registry).decode("utf-8")
        assert "very-specific-command-text-9731" not in exposed
        assert 'tool="shell.exec"' in exposed

    def test_a_refusal_is_counted_by_reason(self) -> None:
        service, _store = fake_service(FakeBackend())
        asyncio.run(service.execute(request("git.push", {}, run_id="r-1")))
        exposed = generate_latest(service.metrics.registry).decode("utf-8")
        assert 'sandbox_policy_rejections_total{reason="UNKNOWN_TOOL"' in exposed


class SandboxLogTests:
    def test_log_fields_carry_identifiers_and_never_output(self) -> None:
        fields = sandbox_log_fields(run_id="r", agent_id="developer", sandbox_id="s",
                                    tool="shell.exec", status="SUCCEEDED", duration_ms=12)
        assert fields == {"runId": "r", "agentId": "developer", "sandboxId": "s",
                          "toolName": "shell.exec", "status": "SUCCEEDED", "durationMs": "12"}
        assert "stdout" not in fields and "command" not in fields

    def test_an_execution_log_record_holds_no_command_or_output(self, caplog) -> None:
        backend = FakeBackend(responses=[{"ok": True, "result": {
            "started": True, "exitCode": 0, "stdout": "OUTPUT-SENTINEL-4417", "stderr": "",
            "durationMs": 1, "timedOut": False, "truncated": False}}])
        service, _store = fake_service(backend)
        with caplog.at_level(logging.INFO):
            asyncio.run(service.execute(request(
                "shell.exec", {"command": "echo COMMAND-SENTINEL-8821"}, run_id="r-1")))
        text = " ".join(f"{record.getMessage()} {record.__dict__}" for record in caplog.records)
        assert "sandbox tool executed" in text
        assert "OUTPUT-SENTINEL-4417" not in text
        assert "COMMAND-SENTINEL-8821" not in text
