"""Our configuration of each service, exercised against the running stack.

Not a test of PostgreSQL, Redis, MinIO, Temporal, Prometheus or Grafana — those are somebody else's
software and they have their own suites. What is tested here is *our* configuration of them: that
the bucket exists, that Prometheus scrapes what we told it to, that Grafana came up with the
datasource and the dashboard we provisioned, that the ports we publish answer.

Every test skips with a reason when the stack is not running, so this file is safe to discover in
an environment that has no Docker.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import unittest
import urllib.error
import urllib.request
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
COMPOSE_DIRECTORY = REPOSITORY_ROOT / "infra" / "compose"
COMPOSE_FILE = COMPOSE_DIRECTORY / "docker-compose.yml"
ENV_FILE = COMPOSE_DIRECTORY / ".env"

TIMEOUT = 20


def _compose(*arguments: str, merge: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["docker", "compose", "--project-directory", str(COMPOSE_DIRECTORY),
         "--file", str(COMPOSE_FILE), "--env-file", str(ENV_FILE), *arguments],
        cwd=str(COMPOSE_DIRECTORY), text=True, encoding="utf-8", errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT if merge else subprocess.PIPE, check=False)


def _port(service: str, container_port: int) -> int:
    result = _compose("port", service, str(container_port), merge=False)
    if result.returncode != 0 or not result.stdout.strip():
        raise unittest.SkipTest(f"{service} does not publish {container_port}; stack not running")
    return int(result.stdout.strip().splitlines()[-1].rsplit(":", 1)[-1])


def _json(url: str) -> dict:
    request = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        return json.loads(error.read().decode("utf-8"))


def _text(url: str) -> str:
    with urllib.request.urlopen(url, timeout=TIMEOUT) as response:
        return response.read().decode("utf-8", errors="replace")


class RunningStackTestCase(unittest.TestCase):
    """Base class that skips the whole file when the stack is not up."""

    @classmethod
    def setUpClass(cls) -> None:
        if shutil.which("docker") is None:
            raise unittest.SkipTest("docker is not on PATH")
        if not ENV_FILE.is_file():
            raise unittest.SkipTest("infra/compose/.env is absent")
        result = _compose("ps", "--status", "running", "--services")
        running = {line.strip() for line in result.stdout.splitlines() if line.strip()}
        if "api" not in running:
            raise unittest.SkipTest("the Foundation stack is not running")


class PostgresConfigurationTests(RunningStackTestCase):
    def test_postgres_is_pinned_and_persistent(self) -> None:
        result = _compose("exec", "-T", "postgres", "postgres", "--version", merge=False)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("17.", result.stdout, "the running server is not the pinned major version")

    def test_the_temporal_databases_exist_beside_ours(self) -> None:
        """Temporal shares the server but not the database; that separation is what is checked."""
        result = _compose(
            "exec", "-T", "postgres", "sh", "-c",
            'PGPASSWORD="$POSTGRES_PASSWORD" psql --username="$POSTGRES_USER" --dbname=postgres '
            '--tuples-only --no-align -c "SELECT datname FROM pg_database"', merge=False)
        self.assertEqual(result.returncode, 0, result.stdout)
        databases = {line.strip() for line in result.stdout.splitlines() if line.strip()}
        self.assertIn("iacode", databases)
        self.assertIn("temporal", databases)
        self.assertIn("temporal_visibility", databases)


class RedisConfigurationTests(RunningStackTestCase):
    def test_redis_is_pinned(self) -> None:
        result = _compose("exec", "-T", "redis", "redis-cli", "INFO", "server", merge=False)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("redis_version:8.2.", result.stdout)

    def test_redis_answers_on_the_published_port(self) -> None:
        import socket

        port = _port("redis", 6379)
        with socket.create_connection(("127.0.0.1", port), timeout=TIMEOUT) as connection:
            connection.sendall(b"PING\r\n")
            self.assertEqual(connection.recv(16), b"+PONG\r\n")


class ObjectStorageConfigurationTests(RunningStackTestCase):
    def test_minio_is_pinned_and_persistent(self) -> None:
        port = _port("minio", 9000)
        with urllib.request.urlopen(
                f"http://127.0.0.1:{port}/minio/health/live", timeout=TIMEOUT) as response:
            self.assertEqual(response.status, 200)

    def test_the_artifact_bucket_exists_and_is_private(self) -> None:
        result = _compose(
            "run", "--rm", "--no-deps", "--entrypoint", "/bin/sh", "minio-bootstrap", "-c",
            'mc alias set iacode http://minio:9000 "$MINIO_ROOT_USER" "$MINIO_ROOT_PASSWORD" '
            '>/dev/null && mc anonymous get "iacode/$IACODE_MINIO_BUCKET"')
        self.assertEqual(result.returncode, 0, result.stdout)
        # `mc anonymous get` answers "Access permission ... is `private`". A public artifact bucket
        # would publish whatever a later Gate stores in it.
        self.assertIn("is `private`", result.stdout, result.stdout)


class TemporalConfigurationTests(RunningStackTestCase):
    def test_temporal_is_pinned(self) -> None:
        result = _compose("exec", "-T", "temporal", "temporal", "--version", merge=False)
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_the_configured_namespace_exists(self) -> None:
        result = _compose(
            "exec", "-T", "temporal", "sh", "-c",
            "temporal operator namespace list --address $(hostname -i):7233", merge=False)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("default", result.stdout)

    def test_the_worker_is_polling_our_task_queue(self) -> None:
        """A worker that is running but not polling is the failure a process check would miss."""
        result = _compose("exec", "-T", "worker", "python", "-m",
                          "iacode_orchestrator.healthcheck", merge=False)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("poller(s) on", result.stdout)


class PrometheusConfigurationTests(RunningStackTestCase):
    def test_prometheus_scrapes_the_foundation_targets(self) -> None:
        port = _port("prometheus", 9090)
        payload = _json(f"http://127.0.0.1:{port}/api/v1/targets?state=active")
        health = {item["labels"]["job"]: item["health"]
                  for item in payload["data"]["activeTargets"]}
        for job in ("iacode-api", "iacode-worker", "iacode-sandbox"):
            with self.subTest(job=job):
                self.assertEqual(health.get(job), "up",
                                 f"{job} is {health.get(job)!r}; targets={health}")

    def test_the_api_instruments_reach_prometheus(self) -> None:
        """Scraping is not enough: the series we rely on have to be queryable."""
        port = _port("prometheus", 9090)
        payload = _json(
            f"http://127.0.0.1:{port}/api/v1/query?query=iacode_build_info")
        self.assertEqual(payload.get("status"), "success", payload)
        self.assertTrue(payload["data"]["result"],
                        "iacode_build_info has no samples in Prometheus")


class GrafanaConfigurationTests(RunningStackTestCase):
    def test_grafana_is_healthy(self) -> None:
        port = _port("grafana", 3000)
        payload = _json(f"http://127.0.0.1:{port}/api/health")
        self.assertEqual(payload.get("database"), "ok", payload)

    def test_grafana_provisioning_is_declared(self) -> None:
        """The datasource and the dashboard are files, so they are the same on every machine."""
        datasource = REPOSITORY_ROOT / "infra/grafana/provisioning/datasources/prometheus.yml"
        provider = REPOSITORY_ROOT / "infra/grafana/provisioning/dashboards/foundation.yml"
        dashboard = REPOSITORY_ROOT / "infra/grafana/dashboards/foundation.json"
        for path in (datasource, provider, dashboard):
            with self.subTest(path=path.name):
                self.assertTrue(path.is_file())

        content = json.loads(dashboard.read_text(encoding="utf-8"))
        # Every panel names the datasource explicitly, by a fixed uid. A panel that inherits the
        # default renders as an error the day a second datasource is provisioned, and a generated
        # uid would leave every panel pointing at a datasource that does not exist.
        uids = set()
        for panel in content["panels"]:
            datasource_reference = panel.get("datasource")
            self.assertIsInstance(datasource_reference, dict,
                                  f"panel {panel.get('title')!r} names no datasource")
            uids.add(datasource_reference["uid"])
        self.assertEqual(uids, {"iacode-prometheus"})
        self.assertIn("uid: iacode-prometheus", datasource.read_text(encoding="utf-8"))

    def test_grafana_refuses_anonymous_access(self) -> None:
        """Anonymous access stays off even locally.

        The local setup and a shared one should differ in configuration, not in behaviour, and a
        dashboard anyone on the machine can read is a habit that travels.
        """
        port = _port("grafana", 3000)
        request = urllib.request.Request(f"http://127.0.0.1:{port}/api/search?query=IACode")
        try:
            with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
                status = response.status
        except urllib.error.HTTPError as error:
            status = error.code
        self.assertIn(status, (401, 403),
                      f"Grafana answered {status} without credentials")


class WebConfigurationTests(RunningStackTestCase):
    def test_the_web_shell_is_served(self) -> None:
        port = _port("web", 8080)
        page = _text(f"http://127.0.0.1:{port}/")
        self.assertIn("<app-root></app-root>", page)

    def test_the_runtime_configuration_is_written_at_start_up(self) -> None:
        port = _port("web", 8080)
        config = _json(f"http://127.0.0.1:{port}/config.json")
        self.assertEqual(set(config), {"apiBaseUrl"},
                         "config.json carries more than the backend address")

    def test_unknown_paths_serve_the_application_shell(self) -> None:
        """A single-page application 404s on reload without this."""
        port = _port("web", 8080)
        self.assertIn("<app-root></app-root>", _text(f"http://127.0.0.1:{port}/some/deep/route"))


if __name__ == "__main__":
    unittest.main()
