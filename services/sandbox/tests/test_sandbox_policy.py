"""The canonical policy: loaded whole or refused, bounded by code, and out of a request's reach."""

from __future__ import annotations

import copy
import json

import pytest
from iacode_sandbox.policy import BOUNDS, PolicyError, parse_policy_document
from iacode_sandbox.tools import REGISTRY
from sandbox_fixtures import policies, repository_root


def document() -> dict:
    path = repository_root() / ".iacode" / "policies" / "sandbox-policy.json"
    return json.loads(path.read_text(encoding="utf-8"))


class SandboxPolicyTests:
    def test_the_canonical_policy_loads(self) -> None:
        registry = policies()
        assert set(registry.policies) == {"developer", "reviewer"}
        developer = registry.get("developer")
        assert developer.network_profile == "none"
        assert developer.workspace_access == "read-write"
        assert developer.tools <= set(REGISTRY)

    def test_the_reviewer_is_read_only(self) -> None:
        reviewer = policies().get("reviewer")
        assert reviewer.workspace_access == "read-only"
        assert all(REGISTRY[tool].access == "read" for tool in reviewer.tools)
        assert "shell.exec" not in reviewer.tools

    def test_every_policy_denies_network_by_default(self) -> None:
        for policy in policies().policies.values():
            assert policy.network_profile == "none", policy.name

    def test_no_policy_offers_a_remote_git_operation(self) -> None:
        for policy in policies().policies.values():
            for tool in policy.tools:
                assert not any(word in tool for word in ("push", "fetch", "pull", "clone",
                                                         "remote")), tool

    def test_the_sandbox_git_identity_is_not_a_person(self) -> None:
        developer = policies().get("developer")
        assert developer.git_identity_name == "IACode Agent"
        assert developer.git_identity_email.endswith(".invalid")

    def test_a_read_only_policy_that_allows_a_writer_is_refused(self) -> None:
        mutated = document()
        reviewer = next(item for item in mutated["sandboxPolicies"] if item["name"] == "reviewer")
        reviewer["tools"].append("filesystem.write")
        with pytest.raises(PolicyError, match="read-only"):
            parse_policy_document(mutated)

    def test_a_policy_naming_an_unregistered_tool_is_refused(self) -> None:
        mutated = document()
        mutated["sandboxPolicies"][0]["tools"].append("git.push")
        with pytest.raises(PolicyError, match="not registered"):
            parse_policy_document(mutated)

    def test_a_credential_cannot_be_allowed_into_a_command_environment(self) -> None:
        for name in ("DEVWORLD_API_KEY", "GITHUB_TOKEN", "SSH_AUTH_SOCK", "DOCKER_HOST",
                     "AWS_SECRET_ACCESS_KEY", "OPENAI_API_KEY", "GIT_ASKPASS", "LD_PRELOAD"):
            mutated = document()
            mutated["requestEnvironment"]["allowedNames"].append(name)
            with pytest.raises(PolicyError):
                parse_policy_document(mutated)

    def test_an_unknown_key_is_refused(self) -> None:
        mutated = document()
        mutated["mounts"] = ["C:\\"]
        with pytest.raises(PolicyError, match="unknown keys"):
            parse_policy_document(mutated)

    def test_the_unmutated_document_is_accepted(self) -> None:
        """The null control of the refusals above."""
        assert parse_policy_document(document()).get("developer") is not None


class ResourceLimitValidationTests:
    def test_zero_negative_and_absurd_values_are_refused(self) -> None:
        for key, (low, high) in BOUNDS.items():
            assert low > 0, key
            for value in (0, -1, high * 10, "unlimited", None, True):
                mutated = document()
                mutated["resourceProfiles"][0][key] = value
                with pytest.raises(PolicyError):
                    parse_policy_document(mutated)

    def test_a_missing_limit_is_refused(self) -> None:
        for key in BOUNDS:
            mutated = document()
            del mutated["resourceProfiles"][0][key]
            with pytest.raises(PolicyError):
                parse_policy_document(mutated)

    def test_memory_must_hold_the_in_memory_filesystems(self) -> None:
        mutated = document()
        profile = mutated["resourceProfiles"][0]
        profile["memoryMb"] = profile["workspaceMb"] + profile["tmpMb"]
        with pytest.raises(PolicyError, match="room inside memoryMb"):
            parse_policy_document(mutated)

    def test_every_limit_the_policy_applies_is_inside_its_bound(self) -> None:
        profile = copy.deepcopy(document()["resourceProfiles"][0])
        for key, (low, high) in BOUNDS.items():
            assert low <= profile[key] <= high, key
