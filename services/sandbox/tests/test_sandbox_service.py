"""The service's decisions against a double of the engine: what it refuses, records, recovers."""

from __future__ import annotations

import asyncio
from datetime import timedelta

from iacode_sandbox.service import SandboxService
from sandbox_fixtures import FakeBackend, fake_service, request, utc


def run(coroutine):
    return asyncio.run(coroutine)


class SandboxServiceDecisionTests:
    def test_an_unknown_tool_is_denied_and_nothing_is_started(self) -> None:
        backend = FakeBackend()
        service, store = fake_service(backend)
        result = run(service.execute(request("shell", {"command": "id"}, run_id="r-1")))

        assert result.status == "DENIED"
        assert result.error_code == "UNKNOWN_TOOL"
        assert backend.created == [] and backend.requests == []
        assert run(store.active_session_for_run("r-1")) is None

    def test_a_denial_is_recorded_as_an_execution(self) -> None:
        backend = FakeBackend()
        service, store = fake_service(backend)
        payload = request("git.push", {}, run_id="r-1")
        run(service.execute(payload))
        recorded = run(store.execution(payload["toolRequestId"]))
        assert recorded is not None and recorded.status == "DENIED"
        assert recorded.exit_code is None

    def test_an_unknown_policy_is_denied(self) -> None:
        service, _store = fake_service(FakeBackend())
        result = run(service.execute(request("filesystem.read", {"path": "a"}, run_id="r-1",
                                             policy="root")))
        assert (result.status, result.error_code) == ("DENIED", "POLICY_UNKNOWN")

    def test_a_request_that_tries_to_set_a_limit_is_denied(self) -> None:
        service, _store = fake_service(FakeBackend())
        payload = request("shell.exec", {"command": "true"}, run_id="r-1")
        payload["memory"] = "unlimited"
        result = run(service.execute(payload))
        assert (result.status, result.error_code) == ("DENIED", "CONTRACT_UNKNOWN_FIELD")

    def test_no_request_can_change_the_network_the_limits_or_the_mounts(self) -> None:
        """An agent asking for more than its policy gives is refused, in every spelling of it.

        Each escalation is tried at both places a request has: beside the contract's fields,
        where the contract refuses it, and inside the tool's arguments, where the tool refuses it.
        Nothing is started for any of them.
        """
        escalations = ({"network": "full"}, {"networkProfile": "local-services"},
                       {"memory": "unlimited"}, {"cpus": 64}, {"pids": 0},
                       {"mount": "C:\\"}, {"volumes": ["/:/host"]}, {"privileged": True},
                       {"image": "alpine:latest"},
                       {"environment": {"DOCKER_HOST": "tcp://host.docker.internal:2375"}})
        for escalation in escalations:
            backend = FakeBackend()
            service, _store = fake_service(backend)
            beside = request("shell.exec", {"command": "true"}, run_id="r-1")
            beside.update(escalation)
            result = run(service.execute(beside))
            beside_verdict = (result.status, result.error_code)
            assert beside_verdict == ("DENIED", "CONTRACT_UNKNOWN_FIELD"), escalation
            inside = request("shell.exec", {"command": "true", **escalation}, run_id="r-1")
            result = run(service.execute(inside))
            inside_verdict = (result.status, result.error_code)
            assert inside_verdict in (("DENIED", "ARGUMENT_UNKNOWN"),
                                      ("DENIED", "ENVIRONMENT_NOT_ALLOWED")), inside_verdict
            assert backend.created == [] and backend.requests == [], escalation

        control = FakeBackend()
        service, _store = fake_service(control)
        result = run(service.execute(request("shell.exec", {"command": "true"}, run_id="r-1")))
        assert result.status == "SUCCEEDED", "the unmutated request must pass the same path"
        assert len(control.created) == 1

    def test_an_execution_is_never_repeated_for_a_retried_request(self) -> None:
        backend = FakeBackend(responses=[{"ok": True, "result": {
            "started": True, "exitCode": 0, "stdout": "once", "stderr": "", "durationMs": 3,
            "timedOut": False, "truncated": False}}])
        service, _store = fake_service(backend)
        payload = request("shell.exec", {"command": "echo once"}, run_id="r-1")
        first = run(service.execute(payload))
        second = run(service.execute(payload))

        assert first.status == "SUCCEEDED" and not first.replayed
        assert second.replayed and second.error_code == "EXECUTION_REPLAYED"
        assert [item["op"] for item in backend.requests].count("exec") == 1

    def test_one_run_gets_one_session_and_two_runs_get_two(self) -> None:
        backend = FakeBackend()
        service, _store = fake_service(backend)
        for run_id in ("r-1", "r-1", "r-2"):
            run(service.execute(request("git.status", {}, run_id=run_id)))
        assert len(backend.created) == 2
        assert {spec.run_id for spec in backend.created} == {"r-1", "r-2"}

    def test_a_missing_or_stale_image_is_refused_rather_than_substituted(self) -> None:
        for labels, code in ((None, "SANDBOX_IMAGE_MISSING"),
                             ({"org.iacode.sandbox.fingerprint": "0" * 64},
                              "SANDBOX_IMAGE_STALE")):
            backend = FakeBackend(labels=labels)
            store_service, store = fake_service(backend)
            store_service.backend.labels = labels
            result = run(store_service.execute(request("git.status", {}, run_id="r-1")))
            assert (result.status, result.error_code) == ("FAILED", code)
            assert backend.created == []
            assert run(store.active_session_for_run("r-1")) is None

    def test_a_path_refusal_from_inside_the_sandbox_is_a_denial(self) -> None:
        backend = FakeBackend(responses=[{"ok": False, "errorCode": "PATH_SYMLINK_ESCAPE",
                                          "error": "resolves outside"}])
        service, _store = fake_service(backend)
        result = run(service.execute(request("filesystem.read", {"path": "leak"}, run_id="r-1")))
        assert (result.status, result.error_code) == ("DENIED", "PATH_SYMLINK_ESCAPE")

    def test_truncated_output_goes_to_the_artifact_store(self) -> None:
        import base64

        full = b"x" * 5000
        backend = FakeBackend(responses=[{"ok": True, "result": {
            "started": True, "exitCode": 0, "stdout": "x" * 100, "stderr": "", "durationMs": 1,
            "timedOut": False, "truncated": True, "stdoutBytes": 5000, "stderrBytes": 0,
            "stdoutFull": base64.b64encode(full).decode(), "stderrFull": ""}}])
        service, store = fake_service(backend)
        result = run(service.execute(request("shell.exec", {"command": "yes"}, run_id="r-1")))
        assert result.truncated and len(result.artifacts) == 1
        assert result.artifacts[0].size_bytes == 5000
        assert "stdoutFull" not in result.output
        assert store.artifacts[0]["kind"] == "sandbox.stdout"


class SessionRecoveryTests:
    def test_reconcile_removes_a_labelled_container_no_session_owns(self) -> None:
        backend = FakeBackend()
        service, _store = fake_service(backend)
        backend.containers.append({"name": "iacode-sbx-orphan", "state": "running",
                                   "session": "gone", "run": "r-x", "expiresAt": "0"})
        report = run(service.reconcile())
        assert "iacode-sbx-orphan" in backend.removed
        assert report["removed"]

    def test_reconcile_fails_a_session_whose_container_is_gone(self) -> None:
        backend = FakeBackend()
        service, store = fake_service(backend)
        run(service.execute(request("git.status", {}, run_id="r-1")))
        backend.containers.clear()
        restarted = SandboxService(root=service.root, policies=service.policies, backend=backend,
                                   store=store, artifacts=service.artifacts)
        report = run(restarted.reconcile())
        assert len(report["lost"]) == 1
        assert run(store.active_session_for_run("r-1")) is None

    def test_reconcile_keeps_a_session_whose_container_is_alive(self) -> None:
        """The null control: a restart loses nothing that is still there."""
        backend = FakeBackend()
        service, store = fake_service(backend)
        run(service.execute(request("git.status", {}, run_id="r-1")))
        restarted = SandboxService(root=service.root, policies=service.policies, backend=backend,
                                   store=store, artifacts=service.artifacts)
        report = run(restarted.reconcile())
        assert report == {"lost": [], "recovered": [], "removed": []}
        assert run(store.active_session_for_run("r-1")).state == "READY"

    def test_the_sweeper_expires_only_what_has_expired_and_is_not_running(self) -> None:
        clock = {"now": utc()}
        backend = FakeBackend()
        service, store = fake_service(backend, now=lambda: clock["now"])
        for run_id in ("r-1", "r-2", "r-3"):
            run(service.execute(request("git.status", {}, run_id=run_id)))
        busy = run(store.active_session_for_run("r-2"))
        run(store.update_session(busy.session_id, state="RUNNING"))

        clock["now"] = utc() + timedelta(days=2)
        expired = run(service.sweep(limit=10))

        assert busy.session_id not in expired
        assert len(expired) == 2
        assert run(store.session(busy.session_id)).state == "RUNNING"

    def test_the_sweeper_is_bounded(self) -> None:
        clock = {"now": utc()}
        backend = FakeBackend()
        service, _store = fake_service(backend, now=lambda: clock["now"])
        for index in range(5):
            run(service.execute(request("git.status", {}, run_id=f"r-{index}")))
        clock["now"] = utc() + timedelta(days=2)
        assert len(run(service.sweep(limit=2))) == 2
        assert len(run(service.sweep(limit=2))) == 2
        assert len(run(service.sweep(limit=2))) == 1

    def test_nothing_unexpired_is_swept(self) -> None:
        backend = FakeBackend()
        service, _store = fake_service(backend, now=utc)
        run(service.execute(request("git.status", {}, run_id="r-1")))
        assert run(service.sweep(limit=10)) == []

    def test_releasing_a_run_removes_its_container(self) -> None:
        backend = FakeBackend()
        service, store = fake_service(backend)
        run(service.execute(request("git.status", {}, run_id="r-1")))
        session = run(store.active_session_for_run("r-1"))
        assert run(service.release_run("r-1")) == 1
        assert session.container_name in backend.removed
        assert run(store.session(session.session_id)).state == "STOPPED"
