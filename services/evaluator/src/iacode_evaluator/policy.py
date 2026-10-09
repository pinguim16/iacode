"""Strict canonical quality policy loading and project-owned narrowing."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from iacode_contracts.quality import QUALITY_CHECK_KINDS, QualityPolicy

from iacode_evaluator.canonical import digest
from iacode_evaluator.errors import QualityError
from iacode_evaluator.runners import get_runner

ROOT_KEYS = frozenset({"schemaVersion", "policy", "defaults", "profiles"})
DEFAULT_KEYS = frozenset({"maxRunSeconds", "maxCheckSeconds", "maxOutputBytes"})
PROFILE_KEYS = frozenset({"stacks", "runners", "optionalRunners", "coverageThreshold"})
CONFIG_KEYS = frozenset({"additionalRunners", "timeoutSeconds", "coverageThreshold"})


@dataclass(frozen=True)
class PolicyProfile:
    name: str
    stacks: tuple[str, ...]
    runners: tuple[str, ...]
    optional_runners: tuple[str, ...]
    coverage_threshold: float | None


@dataclass(frozen=True)
class PolicyRegistry:
    version: str
    digest: str
    max_run_seconds: int
    max_check_seconds: int
    max_output_bytes: int
    profiles: dict[str, PolicyProfile]

    def profile(self, name: str) -> PolicyProfile:
        try:
            return self.profiles[name]
        except KeyError:
            raise QualityError(
                "QUALITY_PROFILE_UNKNOWN", f"unknown quality profile: {name!r}"
            ) from None

    def contract(
        self, profile: PolicyProfile, configuration: dict[str, Any] | None = None
    ) -> QualityPolicy:
        config = validate_configuration(configuration or {})
        additional = tuple(config.get("additionalRunners") or ())
        outside = sorted(set(additional) - set(profile.optional_runners))
        if outside:
            raise QualityError(
                "RUNNER_NOT_DECLARED_FOR_PROFILE",
                "additional runners are outside the profile: " + ", ".join(outside),
            )
        selected = profile.runners + additional
        kinds = tuple(dict.fromkeys(get_runner(identifier).kind for identifier in selected))
        threshold = profile.coverage_threshold
        requested_threshold = config.get("coverageThreshold")
        if requested_threshold is not None:
            if threshold is not None and requested_threshold < threshold:
                raise QualityError(
                    "QUALITY_THRESHOLD_WEAKENED", "coverage threshold cannot be lowered"
                )
            threshold = float(requested_threshold)
        timeout = int(config.get("timeoutSeconds", self.max_check_seconds))
        if timeout > self.max_check_seconds:
            raise QualityError("QUALITY_LIMIT_RAISED", "check timeout cannot be raised")
        if threshold is not None and "coverage" not in kinds:
            raise QualityError(
                "COVERAGE_RUNNER_REQUIRED",
                "a coverage threshold requires a declared coverage runner",
            )
        return QualityPolicy(
            policyId="default",
            version=self.version,
            digest=self.digest,
            profile=profile.name,
            mandatoryCheckKinds=kinds,
            maxRunSeconds=self.max_run_seconds,
            maxCheckSeconds=timeout,
            maxOutputBytes=self.max_output_bytes,
            coverageThreshold=threshold,
        )


def _exact(actual: set[str], allowed: frozenset[str], where: str) -> None:
    unknown = sorted(actual - allowed)
    if unknown:
        raise QualityError(
            "QUALITY_POLICY_UNKNOWN_KEY", f"{where} has unknown keys: {', '.join(unknown)}"
        )


def _bounded_int(value: Any, name: str, low: int, high: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise QualityError("QUALITY_POLICY_WRONG_TYPE", f"{name} must be an integer")
    if value < low or value > high:
        raise QualityError("QUALITY_POLICY_OUT_OF_RANGE", f"{name} is outside {low}..{high}")
    return value


def load_policy(path: Path) -> PolicyRegistry:
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise QualityError(
            "QUALITY_POLICY_UNREADABLE", f"quality policy cannot be read: {error}"
        ) from None
    if not isinstance(document, dict):
        raise QualityError("QUALITY_POLICY_WRONG_TYPE", "quality policy root must be an object")
    _exact(set(document), ROOT_KEYS, "quality policy")
    if document.get("schemaVersion") != "1.0.0":
        raise QualityError(
            "QUALITY_POLICY_VERSION_UNSUPPORTED", "quality policy version is unsupported"
        )
    defaults = document.get("defaults")
    profiles = document.get("profiles")
    if not isinstance(defaults, dict) or not isinstance(profiles, dict) or not profiles:
        raise QualityError("QUALITY_POLICY_MISSING", "defaults and non-empty profiles are required")
    _exact(set(defaults), DEFAULT_KEYS, "quality defaults")
    max_run = _bounded_int(defaults.get("maxRunSeconds"), "maxRunSeconds", 1, 14400)
    max_check = _bounded_int(defaults.get("maxCheckSeconds"), "maxCheckSeconds", 1, 3600)
    max_output = _bounded_int(
        defaults.get("maxOutputBytes"), "maxOutputBytes", 1024, 4 * 1024 * 1024
    )
    loaded: dict[str, PolicyProfile] = {}
    for name, raw in profiles.items():
        if not isinstance(name, str) or not isinstance(raw, dict):
            raise QualityError(
                "QUALITY_POLICY_WRONG_TYPE", "profile names and bodies must be objects"
            )
        _exact(set(raw), PROFILE_KEYS, f"profile {name}")
        stacks = raw.get("stacks")
        runners = raw.get("runners")
        optional = raw.get("optionalRunners")
        if (
            not isinstance(stacks, list)
            or not stacks
            or not all(isinstance(item, str) for item in stacks)
        ):
            raise QualityError("QUALITY_POLICY_WRONG_TYPE", f"profile {name} stacks are invalid")
        if (
            not isinstance(runners, list)
            or not runners
            or not all(isinstance(item, str) for item in runners)
        ):
            raise QualityError("QUALITY_POLICY_WRONG_TYPE", f"profile {name} runners are invalid")
        if not isinstance(optional, list) or not all(isinstance(item, str) for item in optional):
            raise QualityError(
                "QUALITY_POLICY_WRONG_TYPE", f"profile {name} optional runners are invalid"
            )
        if (
            set(runners) & set(optional)
            or len(runners) != len(set(runners))
            or len(optional) != len(set(optional))
        ):
            raise QualityError(
                "QUALITY_POLICY_DUPLICATE_RUNNER", f"profile {name} repeats a runner"
            )
        for identifier in runners + optional:
            runner = get_runner(identifier)
            if runner.kind not in QUALITY_CHECK_KINDS:
                raise QualityError("CHECK_KIND_UNKNOWN", f"runner {identifier} has unknown kind")
            if runner.stack not in set(stacks) | {"common"}:
                raise QualityError(
                    "RUNNER_STACK_MISMATCH", f"runner {identifier} is outside profile {name}"
                )
        threshold = raw.get("coverageThreshold")
        if threshold is not None and (
            isinstance(threshold, bool)
            or not isinstance(threshold, (int, float))
            or threshold < 0
            or threshold > 100
        ):
            raise QualityError("QUALITY_POLICY_OUT_OF_RANGE", f"profile {name} coverage is invalid")
        loaded[name] = PolicyProfile(
            name,
            tuple(stacks),
            tuple(runners),
            tuple(optional),
            float(threshold) if threshold is not None else None,
        )
    return PolicyRegistry(
        str(document["schemaVersion"]), digest(document), max_run, max_check, max_output, loaded
    )


def validate_configuration(configuration: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(configuration, dict):
        raise QualityError("QUALITY_CONFIG_WRONG_TYPE", "quality configuration must be an object")
    _exact(set(configuration), CONFIG_KEYS, "quality configuration")
    expected_types = {
        "timeoutSeconds": int,
        "coverageThreshold": (int, float),
        "additionalRunners": list,
    }
    for key, value in configuration.items():
        expected = expected_types[key]
        if isinstance(value, bool) or not isinstance(value, expected):
            raise QualityError("QUALITY_CONFIG_WRONG_TYPE", f"{key} has the wrong type")
    additional = configuration.get("additionalRunners")
    if additional is not None and (
        not additional
        or not all(isinstance(item, str) for item in additional)
        or len(additional) != len(set(additional))
    ):
        raise QualityError(
            "QUALITY_CONFIG_WRONG_VALUE", "additionalRunners must be unique non-empty strings"
        )
    return dict(configuration)
