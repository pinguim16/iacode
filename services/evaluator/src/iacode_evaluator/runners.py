"""Closed runner registry: project content can select a declared runner, never author a command."""

from __future__ import annotations

from dataclasses import dataclass

from iacode_evaluator.errors import QualityError


@dataclass(frozen=True)
class Runner:
    identifier: str
    stack: str
    kind: str
    command: tuple[str, ...]
    timeout_seconds: int
    evidence_kinds: tuple[str, ...] = ("report",)


def _runner(
    identifier: str,
    stack: str,
    kind: str,
    command: tuple[str, ...],
    timeout: int = 300,
    evidence: tuple[str, ...] = ("report",),
) -> Runner:
    return Runner(identifier, stack, kind, command, timeout, evidence)


RUNNERS: dict[str, Runner] = {
    runner.identifier: runner
    for runner in (
        _runner(
            "python.build",
            "python",
            "build",
            ("iacode-quality-python", "python", "-m", "compileall", "-q", "."),
        ),
        _runner(
            "python.unit",
            "python",
            "unit",
            (
                "iacode-quality-python",
                "python",
                "-m",
                "pytest",
                "tests",
                "-m",
                "not integration and not engine",
                "-p",
                "no:cacheprovider",
                "--no-header",
            ),
            900,
        ),
        _runner(
            "python.integration",
            "python",
            "integration",
            ("iacode-quality-python", "python", "-m", "pytest", "tests", "-m", "integration"),
            1200,
        ),
        _runner(
            "python.lint",
            "python",
            "lint",
            ("iacode-quality-python", "python", "-m", "ruff", "check", "."),
        ),
        _runner(
            "python.static",
            "python",
            "static",
            ("iacode-quality-python", "python", "-m", "compileall", "-q", "."),
        ),
        _runner(
            "python.dependency", "python", "dependency-security", ("python", "-m", "pip", "check")
        ),
        _runner(
            "python.coverage",
            "python",
            "coverage",
            ("iacode-quality-python", "python", "-m", "coverage", "run", "-m", "pytest"),
            1200,
            ("coverage",),
        ),
        _runner(
            "python.migration",
            "python",
            "migration",
            ("iacode-quality-python", "alembic", "check"),
            600,
            ("migration",),
        ),
        _runner(
            "node.build",
            "node",
            "build",
            ("sh", "-c", "iacode-quality-node-install && npm run build --if-present"),
            900,
        ),
        _runner(
            "node.unit",
            "node",
            "unit",
            ("sh", "-c", "iacode-quality-node-install && npm test -- --runInBand"),
            900,
        ),
        _runner(
            "node.integration", "node", "integration", ("npm", "run", "test:integration"), 1200
        ),
        _runner(
            "node.lint",
            "node",
            "lint",
            ("sh", "-c", "iacode-quality-node-install && npm run lint --if-present"),
            600,
        ),
        _runner(
            "node.dependency",
            "node",
            "dependency-security",
            ("iacode-quality-node-install",),
            1200,
            ("dependency-scan",),
        ),
        _runner(
            "node.coverage", "node", "coverage", ("npm", "run", "coverage"), 1200, ("coverage",)
        ),
        _runner(
            "node.migration",
            "node",
            "migration",
            ("npm", "run", "migration:check"),
            600,
            ("migration",),
        ),
        _runner(
            "typescript.static",
            "typescript",
            "static",
            ("sh", "-c", "iacode-quality-node-install && npx tsc --noEmit"),
            600,
        ),
        _runner(
            "angular.build",
            "angular",
            "build",
            (
                "sh",
                "-c",
                "iacode-quality-node-install && npx ng build --configuration production",
            ),
            1200,
        ),
        _runner(
            "angular.unit",
            "angular",
            "unit",
            ("sh", "-c", "iacode-quality-node-install && npx ng test --watch=false"),
            1200,
        ),
        _runner(
            "maven.build",
            "maven",
            "build",
            (
                "mvn",
                "--offline",
                "-Dmaven.repo.local=/opt/iacode/m2",
                "-Djansi.tmpdir=/workspace",
                "verify",
            ),
            1800,
        ),
        _runner(
            "maven.unit",
            "maven",
            "unit",
            (
                "mvn",
                "--offline",
                "-Dmaven.repo.local=/opt/iacode/m2",
                "-Djansi.tmpdir=/workspace",
                "test",
            ),
            1200,
        ),
        _runner(
            "maven.integration",
            "maven",
            "integration",
            (
                "mvn",
                "--offline",
                "-Dmaven.repo.local=/opt/iacode/m2",
                "-Djansi.tmpdir=/workspace",
                "verify",
                "-Pintegration",
            ),
            1800,
        ),
        _runner(
            "maven.static",
            "maven",
            "static",
            (
                "mvn",
                "--offline",
                "-Dmaven.repo.local=/opt/iacode/m2",
                "-Djansi.tmpdir=/workspace",
                "org.apache.maven.plugins:maven-checkstyle-plugin:3.6.0:check",
            ),
            1200,
        ),
        _runner(
            "maven.dependency",
            "maven",
            "dependency-security",
            ("iacode-quality-java-dependencies",),
            1800,
            ("dependency-scan",),
        ),
        _runner(
            "maven.coverage",
            "maven",
            "coverage",
            (
                "mvn",
                "--offline",
                "-Dmaven.repo.local=/opt/iacode/m2",
                "-Djansi.tmpdir=/workspace",
                "org.jacoco:jacoco-maven-plugin:0.8.13:check",
            ),
            1200,
            ("coverage",),
        ),
        _runner(
            "maven.migration",
            "maven",
            "migration",
            (
                "mvn",
                "--offline",
                "-Dmaven.repo.local=/opt/iacode/m2",
                "-Djansi.tmpdir=/workspace",
                "flyway:validate",
            ),
            1200,
            ("migration",),
        ),
        _runner("gradle.build", "gradle", "build", ("gradle", "--offline", "build"), 1800),
        _runner("gradle.unit", "gradle", "unit", ("gradle", "--offline", "test"), 1200),
        _runner(
            "gradle.integration",
            "gradle",
            "integration",
            ("gradle", "--offline", "integrationTest"),
            1800,
        ),
        _runner("gradle.static", "gradle", "static", ("gradle", "--offline", "check"), 1200),
        _runner(
            "gradle.dependency",
            "gradle",
            "dependency-security",
            ("iacode-quality-java-dependencies",),
            1800,
            ("dependency-scan",),
        ),
        _runner(
            "gradle.coverage",
            "gradle",
            "coverage",
            ("gradle", "--offline", "jacocoTestCoverageVerification"),
            1200,
            ("coverage",),
        ),
        _runner(
            "gradle.migration",
            "gradle",
            "migration",
            ("gradle", "--offline", "flywayValidate"),
            1200,
            ("migration",),
        ),
        _runner(
            "common.secret",
            "common",
            "secret",
            ("iacode-quality-secret-scan",),
            300,
            ("secret-scan",),
        ),
        _runner(
            "common.diff",
            "common",
            "diff-integrity",
            ("sh", "-c", "git init -q && git add -A && git diff --cached --check"),
            300,
            ("diff",),
        ),
    )
}


def get_runner(identifier: str) -> Runner:
    try:
        return RUNNERS[identifier]
    except KeyError:
        raise QualityError("RUNNER_UNKNOWN", f"unknown quality runner: {identifier!r}") from None
