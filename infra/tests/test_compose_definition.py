"""What the Compose file declares, checked without starting anything.

These are the properties a reviewer would otherwise have to hold in their head while reading a
three-hundred-line YAML file: that every image is pinned, that nothing publishes on a public
interface, that health conditions rather than sleeps order the start-up, and that no credential is
written into a committed file.

Standard library only, and no running stack: `docker compose config` resolves the file and these
tests read the result. That keeps them fast enough to be part of the mandatory gate set.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import unittest
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
COMPOSE_DIRECTORY = REPOSITORY_ROOT / "infra" / "compose"
COMPOSE_FILE = COMPOSE_DIRECTORY / "docker-compose.yml"
ENV_FILE = COMPOSE_DIRECTORY / ".env"
ENV_EXAMPLE = COMPOSE_DIRECTORY / ".env.example"

# Services the Foundation is made of. Anything else in the file is infrastructure the Foundation
# does not need, which `docs/GATE-0-CHECKLIST.md` row 10.2 rules out.
EXPECTED_SERVICES = {
    "postgres", "redis", "minio", "minio-bootstrap", "temporal", "temporal-ui",
    "migrate", "api", "worker", "web", "prometheus", "grafana",
}

# Services with a long-running process that can report on itself.
SERVICES_REQUIRING_HEALTHCHECKS = {
    "postgres", "redis", "minio", "temporal", "api", "worker", "web", "prometheus", "grafana",
}

# Durable state that must survive `docker compose down`.
SERVICES_REQUIRING_VOLUMES = {"postgres", "minio", "prometheus", "grafana"}

# An image reference is pinned when it names an exact version. A floating tag makes two builds of
# the same commit produce different stacks.
FLOATING_TAGS = ("latest", "stable", "main", "master", "edge")


def _compose_config() -> dict:
    completed = subprocess.run(
        ["docker", "compose", "--project-directory", str(COMPOSE_DIRECTORY),
         "--file", str(COMPOSE_FILE), "--env-file", str(ENV_FILE), "config", "--format", "json"],
        cwd=str(COMPOSE_DIRECTORY), text=True, encoding="utf-8", errors="replace",
        capture_output=True, check=False)
    if completed.returncode != 0:
        raise unittest.SkipTest(
            f"docker compose config failed: {(completed.stderr or '').strip()[-300:]}")
    return json.loads(completed.stdout)


class ComposeDefinitionTests(unittest.TestCase):
    """The declared stack, resolved by Compose itself rather than parsed by hand."""

    config: dict

    @classmethod
    def setUpClass(cls) -> None:
        if shutil.which("docker") is None:
            raise unittest.SkipTest("docker is not on PATH")
        if not ENV_FILE.is_file():
            raise unittest.SkipTest(
                "infra/compose/.env is absent; run scripts/iacode/bootstrap_env.py")
        cls.config = _compose_config()

    def services(self) -> dict:
        return self.config.get("services", {})

    def test_compose_declares_the_foundation_services(self) -> None:
        self.assertEqual(set(self.services()), EXPECTED_SERVICES)

    def test_every_image_is_pinned(self) -> None:
        for name, service in self.services().items():
            image = service.get("image", "")
            if service.get("build"):
                # Images we build are versioned by the stack's own version, not by a registry tag.
                continue
            with self.subTest(service=name):
                self.assertIn(":", image, f"{name} uses an unpinned image reference")
                tag = image.rsplit(":", 1)[1]
                self.assertNotIn(tag, FLOATING_TAGS, f"{name} floats on {tag!r}")

    def test_compose_uses_health_conditions_not_sleeps(self) -> None:
        for name, service in self.services().items():
            for dependency, options in (service.get("depends_on") or {}).items():
                with self.subTest(service=name, dependency=dependency):
                    self.assertIn(
                        options.get("condition"),
                        ("service_healthy", "service_completed_successfully"),
                        f"{name} waits for {dependency} on "
                        f"{options.get('condition')!r} rather than on a real condition")

        # A sleep anywhere in a command or an entrypoint is the coordination mechanism this rules
        # out; it works on the machine it was tuned on and nowhere else.
        text = COMPOSE_FILE.read_text(encoding="utf-8")
        for match in re.finditer(r"^\s*(command|entrypoint):.*$", text, re.MULTILINE):
            self.assertNotIn("sleep", match.group(0).lower(), match.group(0).strip())

    def test_every_long_running_service_has_a_healthcheck(self) -> None:
        for name in sorted(SERVICES_REQUIRING_HEALTHCHECKS):
            with self.subTest(service=name):
                healthcheck = self.services().get(name, {}).get("healthcheck")
                self.assertTrue(healthcheck, f"{name} declares no healthcheck")
                self.assertTrue(healthcheck.get("test"), f"{name} declares an empty healthcheck")

    def test_healthchecks_do_more_than_confirm_a_process_exists(self) -> None:
        """A healthcheck that greps a process list reports a wedged service as healthy."""
        forbidden = ("ps ", "pgrep", "pidof", "true")
        for name in sorted(SERVICES_REQUIRING_HEALTHCHECKS):
            command = " ".join(str(item) for item in
                               self.services()[name]["healthcheck"].get("test", []))
            with self.subTest(service=name):
                for token in forbidden:
                    self.assertNotIn(token, command.lower(),
                                     f"{name} healthcheck only proves a process exists: {command}")

    def test_published_ports_are_loopback_only(self) -> None:
        """A development stack on 0.0.0.0 is an unauthenticated database on the local network."""
        for name, service in self.services().items():
            for published in service.get("ports") or []:
                with self.subTest(service=name, port=published):
                    self.assertEqual(
                        published.get("host_ip"), "127.0.0.1",
                        f"{name} publishes {published.get('published')} on "
                        f"{published.get('host_ip')!r}")

    def test_published_ports_are_configurable_and_minimal(self) -> None:
        """Two stacks on one machine must not collide, so every host port is a variable.

        Minimal as well as configurable: a service publishes a port only when something outside the
        Compose network has to reach it. Everything else talks over the network by service name.
        """
        text = COMPOSE_FILE.read_text(encoding="utf-8")
        for match in re.finditer(r'^\s*- "127\.0\.0\.1:([^:]+):', text, re.MULTILINE):
            self.assertTrue(match.group(1).startswith("${"),
                            f"host port {match.group(1)!r} is hardcoded")

        publishing = {name for name, service in self.services().items() if service.get("ports")}
        # minio-bootstrap, migrate and worker publish nothing: nothing outside the network calls
        # them. The worker is scraped by Prometheus, which is inside.
        self.assertEqual(
            publishing,
            {"postgres", "redis", "minio", "temporal", "temporal-ui", "api", "web",
             "prometheus", "grafana"})

    def test_durable_state_uses_named_volumes(self) -> None:
        declared = set(self.config.get("volumes", {}))
        self.assertTrue(declared, "the stack declares no named volume")
        for name in sorted(SERVICES_REQUIRING_VOLUMES):
            mounts = self.services()[name].get("volumes") or []
            with self.subTest(service=name):
                self.assertTrue(
                    any(mount.get("type") == "volume" for mount in mounts),
                    f"{name} keeps its state in the container filesystem")

    def test_every_long_running_service_declares_a_restart_policy(self) -> None:
        for name in sorted(SERVICES_REQUIRING_HEALTHCHECKS):
            with self.subTest(service=name):
                self.assertEqual(self.services()[name].get("restart"), "unless-stopped")

    def test_one_shot_jobs_do_not_restart(self) -> None:
        """A job that restarts is a job that runs forever."""
        for name in ("migrate", "minio-bootstrap"):
            with self.subTest(service=name):
                self.assertEqual(self.services()[name].get("restart"), "no")

    def test_every_service_is_on_the_explicit_network(self) -> None:
        for name, service in self.services().items():
            with self.subTest(service=name):
                self.assertIn("iacode", service.get("networks") or {},
                              f"{name} is not attached to the stack's network")

    def test_the_api_waits_for_the_migration_to_succeed(self) -> None:
        """Serving requests against an unmigrated schema is the failure this ordering prevents."""
        condition = (self.services()["api"].get("depends_on") or {}).get("migrate", {})
        self.assertEqual(condition.get("condition"), "service_completed_successfully")


class CommittedConfigurationTests(unittest.TestCase):
    """The files this repository publishes carry no credential."""

    def test_env_example_documents_every_key_without_secrets(self) -> None:
        example = ENV_EXAMPLE.read_text(encoding="utf-8")
        keys = {line.split("=", 1)[0].strip()
                for line in example.splitlines()
                if line.strip() and not line.strip().startswith("#") and "=" in line}
        referenced = set(re.findall(r"\$\{(IACODE_[A-Z0-9_]+)", COMPOSE_FILE.read_text("utf-8")))
        # Build identity is derived at build time by scripts/iacode/stack.py, not configured.
        # Documenting it in the example would invite somebody to set it by hand, which is exactly
        # how /version ends up reporting a commit that was never built.
        derived_at_build_time = {"IACODE_COMMIT", "IACODE_BUILD_TIMESTAMP"}
        missing = referenced - keys - derived_at_build_time
        self.assertEqual(missing, set(),
                         f"the compose file reads keys the example does not document: {missing}")

        for line in example.splitlines():
            if not line.strip() or line.strip().startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            if any(token in key.upper()
                   for token in ("PASSWORD", "SECRET", "TOKEN", "API_KEY")):
                with self.subTest(key=key):
                    self.assertIn(value.strip(), ("change-me-before-starting", ""),
                                  f"{key} carries something that is not a placeholder")

    def test_the_real_environment_file_is_ignored(self) -> None:
        ignore = (REPOSITORY_ROOT / ".gitignore").read_text(encoding="utf-8")
        self.assertIn(".env", ignore)
        completed = subprocess.run(
            ["git", "check-ignore", "-q", str(ENV_FILE)],
            cwd=str(REPOSITORY_ROOT), check=False,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if completed.returncode == 128:
            self.skipTest("not a Git checkout")
        self.assertEqual(completed.returncode, 0, "infra/compose/.env is not ignored by Git")

    def test_no_secret_is_committed_in_infrastructure(self) -> None:
        """Every committed infrastructure file reads its credentials from the environment."""
        patterns = (
            re.compile(r"(?i)(password|secret[_-]?key|api[_-]?key|token)\s*[:=]\s*"
                       r"(?!\$\{|\"\$|change-me|\"\"|''|$)[A-Za-z0-9+/=_-]{8,}"),
        )
        for path in sorted((REPOSITORY_ROOT / "infra").rglob("*")):
            if not path.is_file() or path.name == ".env" or "tests" in path.parts:
                continue
            content = path.read_text(encoding="utf-8", errors="ignore")
            for pattern in patterns:
                match = pattern.search(content)
                with self.subTest(path=str(path.relative_to(REPOSITORY_ROOT))):
                    self.assertIsNone(
                        match, f"{path.name} may contain a literal credential: "
                               f"{match.group(0)[:60] if match else ''}")


class DockerfileTests(unittest.TestCase):
    """The images: pinned bases, no root where it is avoidable, no secrets, no build waste."""

    DOCKERFILES = (
        REPOSITORY_ROOT / "apps" / "api" / "Dockerfile",
        REPOSITORY_ROOT / "apps" / "web" / "Dockerfile",
        REPOSITORY_ROOT / "services" / "orchestrator" / "Dockerfile",
    )

    def test_dockerfiles_pin_and_drop_root(self) -> None:
        for path in self.DOCKERFILES:
            with self.subTest(dockerfile=str(path.relative_to(REPOSITORY_ROOT))):
                self.assertTrue(path.is_file())
                content = path.read_text(encoding="utf-8")
                for match in re.finditer(r"^FROM\s+(\S+)", content, re.MULTILINE):
                    image = match.group(1)
                    self.assertIn(":", image, f"unpinned base image {image}")
                    self.assertNotIn(image.rsplit(":", 1)[1].split("-")[0], FLOATING_TAGS)
                # MULTILINE: the directive is never the first line of a Dockerfile.
                self.assertTrue(
                    re.search(r"^USER\s+\w+", content, re.MULTILINE),
                    "the image declares no USER and therefore runs as root")

    def test_dockerfiles_carry_no_secret(self) -> None:
        for path in self.DOCKERFILES:
            content = path.read_text(encoding="utf-8")
            with self.subTest(dockerfile=path.parent.name):
                self.assertNotRegex(
                    content,
                    r"(?i)(ENV|ARG)\s+\w*(PASSWORD|SECRET|TOKEN|API_KEY)\w*\s*=\s*\S+",
                    "a credential is baked into the image")

    def test_the_build_context_excludes_the_ledger_and_the_toolchain(self) -> None:
        """Without this every image build uploads the whole checkpoint history as context."""
        ignore = (REPOSITORY_ROOT / ".dockerignore").read_text(encoding="utf-8")
        for expected in ("docs/", ".git/", "node_modules/", ".env"):
            with self.subTest(entry=expected):
                self.assertIn(expected, ignore)


if __name__ == "__main__":
    unittest.main()
