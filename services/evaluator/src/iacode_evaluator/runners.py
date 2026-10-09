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
        _runner("python.build", "python", "build", ("python", "-m", "compileall", "-q", ".")),
        _runner("python.unit", "python", "unit", ("python", "-m", "unittest", "discover"), 900),
        _runner(
            "python.integration",
            "python",
            "integration",
            ("python", "-m", "pytest", "tests", "-m", "integration"),
            1200,
        ),
        _runner("python.lint", "python", "lint", ("python", "-m", "ruff", "check", ".")),
        _runner("python.static", "python", "static", ("python", "-m", "compileall", "-q", ".")),
        _runner(
            "python.dependency", "python", "dependency-security", ("python", "-m", "pip", "check")
        ),
        _runner(
            "python.coverage",
            "python",
            "coverage",
            ("python", "-m", "coverage", "run", "-m", "pytest"),
            1200,
            ("coverage",),
        ),
        _runner(
            "python.migration", "python", "migration", ("alembic", "check"), 600, ("migration",)
        ),
        _runner("node.build", "node", "build", ("npm", "run", "build", "--if-present"), 900),
        _runner("node.unit", "node", "unit", ("npm", "test", "--", "--runInBand"), 900),
        _runner(
            "node.integration", "node", "integration", ("npm", "run", "test:integration"), 1200
        ),
        _runner("node.lint", "node", "lint", ("npm", "run", "lint", "--if-present"), 600),
        _runner(
            "node.dependency",
            "node",
            "dependency-security",
            ("npm", "audit", "--offline"),
            600,
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
        _runner("typescript.static", "typescript", "static", ("npx", "tsc", "--noEmit"), 600),
        _runner(
            "angular.build",
            "angular",
            "build",
            ("npx", "ng", "build", "--configuration", "production"),
            1200,
        ),
        _runner("angular.unit", "angular", "unit", ("npx", "ng", "test", "--watch=false"), 1200),
        _runner("maven.build", "maven", "build", ("mvn", "--offline", "verify"), 1800),
        _runner("maven.unit", "maven", "unit", ("mvn", "--offline", "test"), 1200),
        _runner(
            "maven.integration",
            "maven",
            "integration",
            ("mvn", "--offline", "verify", "-Pintegration"),
            1800,
        ),
        _runner("maven.static", "maven", "static", ("mvn", "--offline", "checkstyle:check"), 1200),
        _runner(
            "maven.dependency",
            "maven",
            "dependency-security",
            ("mvn", "--offline", "org.owasp:dependency-check-maven:check"),
            1800,
            ("dependency-scan",),
        ),
        _runner(
            "maven.coverage",
            "maven",
            "coverage",
            ("mvn", "--offline", "jacoco:check"),
            1200,
            ("coverage",),
        ),
        _runner(
            "maven.migration",
            "maven",
            "migration",
            ("mvn", "--offline", "flyway:validate"),
            1200,
            ("migration",),
        ),
        _runner("gradle.build", "gradle", "build", ("./gradlew", "--offline", "build"), 1800),
        _runner("gradle.unit", "gradle", "unit", ("./gradlew", "--offline", "test"), 1200),
        _runner(
            "gradle.integration",
            "gradle",
            "integration",
            ("./gradlew", "--offline", "integrationTest"),
            1800,
        ),
        _runner("gradle.static", "gradle", "static", ("./gradlew", "--offline", "check"), 1200),
        _runner(
            "gradle.dependency",
            "gradle",
            "dependency-security",
            ("./gradlew", "--offline", "dependencyCheckAnalyze"),
            1800,
            ("dependency-scan",),
        ),
        _runner(
            "gradle.coverage",
            "gradle",
            "coverage",
            ("./gradlew", "--offline", "jacocoTestCoverageVerification"),
            1200,
            ("coverage",),
        ),
        _runner(
            "gradle.migration",
            "gradle",
            "migration",
            ("./gradlew", "--offline", "flywayValidate"),
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
            "common.diff", "common", "diff-integrity", ("git", "diff", "--check"), 300, ("diff",)
        ),
    )
}


def get_runner(identifier: str) -> Runner:
    try:
        return RUNNERS[identifier]
    except KeyError:
        raise QualityError("RUNNER_UNKNOWN", f"unknown quality runner: {identifier!r}") from None
