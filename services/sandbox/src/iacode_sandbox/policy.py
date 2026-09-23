"""The canonical Sandbox Tool Policy, loaded and validated.

``.iacode/policies/sandbox-policy.json`` says what every named policy may do. This module reads it
and refuses it whole when any value is wrong, because a sandbox that started with half a policy is a
sandbox whose limits are whatever the missing half defaulted to.

**The bounds are code, not configuration.** :data:`BOUNDS` is the range each resource value must
fall in. Zero, a negative number and an absurd number — a hundred CPUs, a terabyte of memory, a day
of command time, a million processes — are refused when the policy is loaded, so a typo in the
policy fails the service's start rather than taking the machine. Raising a bound is a code change,
reviewed like one.

**A request can never change a policy.** Nothing here takes a request as input. The policy an
execution runs under is looked up by the name the run's frozen plan carries, and the tools module
refuses any argument that would try to describe a limit, a mount, an image or a network.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

__all__ = [
    "BOUNDS",
    "FORBIDDEN_ENVIRONMENT",
    "NETWORK_PROFILES",
    "ImageProfile",
    "PolicyError",
    "PolicyRegistry",
    "ResourceProfile",
    "SandboxPolicy",
    "load_policy_registry",
]

POLICY_PATH = Path(".iacode") / "policies" / "sandbox-policy.json"

#: The network profiles the backend implements. A policy naming anything else is refused.
NETWORK_PROFILES = ("none", "local-services")

#: Hard bounds on every resource value: ``(minimum, maximum)``, both inclusive.
BOUNDS: dict[str, tuple[float, float]] = {
    "cpus": (0.1, 4.0),
    "memoryMb": (64, 4096),
    "pids": (16, 1024),
    "workspaceMb": (8, 2048),
    "tmpMb": (4, 512),
    "commandTimeoutSeconds": (1, 1800),
    "gitTimeoutSeconds": (1, 300),
    "outputBytes": (1024, 1048576),
    "artifactBytes": (1024, 16777216),
    "readBytes": (1024, 4194304),
    "writeBytes": (1024, 4194304),
    "patchBytes": (1024, 4194304),
    "listEntries": (1, 10000),
    "searchResults": (1, 5000),
    "searchSeconds": (1, 120),
    "searchFileBytes": (1024, 16777216),
    "sessionTtlSeconds": (60, 86400),
}

#: Names no policy may let a command set, whatever else it allows: credentials, and the variables
#: that would point a process at the host's Docker, SSH agent or Git credentials.
FORBIDDEN_ENVIRONMENT = re.compile(
    r"(?i)(KEY|TOKEN|SECRET|PASSWORD|PASSWD|CREDENTIAL|AUTH|SESSION|COOKIE|"
    r"^DOCKER_|^SSH_|^GIT_ASKPASS$|^GIT_SSH|^AWS_|^AZURE_|^GOOGLE_|^GCP_|^DEVWORLD_|"
    r"^OPENAI_|^ANTHROPIC_|^GH_|^GITHUB_|^LD_PRELOAD$|^LD_LIBRARY_PATH$|^PYTHONPATH$)")

_NAME = re.compile(r"^[a-z][a-z0-9-]{1,63}$")


class PolicyError(ValueError):
    """The canonical policy cannot be used as written."""


@dataclass(frozen=True)
class ResourceProfile:
    name: str
    cpus: float
    memory_mb: int
    pids: int
    workspace_mb: int
    tmp_mb: int
    command_timeout_seconds: int
    git_timeout_seconds: int
    output_bytes: int
    artifact_bytes: int
    read_bytes: int
    write_bytes: int
    patch_bytes: int
    list_entries: int
    search_results: int
    search_seconds: int
    search_file_bytes: int
    session_ttl_seconds: int


@dataclass(frozen=True)
class ImageProfile:
    name: str
    context: str
    repository: str
    description: str


@dataclass(frozen=True)
class SandboxPolicy:
    name: str
    tools: frozenset[str]
    image: ImageProfile
    resources: ResourceProfile
    network_profile: str
    workspace_access: str
    request_environment_names: frozenset[str]
    request_environment_max_length: int
    git_identity_name: str
    git_identity_email: str


@dataclass(frozen=True)
class PolicyRegistry:
    policies: dict[str, SandboxPolicy]
    images: dict[str, ImageProfile]

    def get(self, name: str) -> SandboxPolicy | None:
        return self.policies.get(name)


def _resource_profile(entry: dict[str, Any]) -> ResourceProfile:
    name = entry.get("name")
    if not isinstance(name, str) or not _NAME.match(name):
        raise PolicyError(f"a resource profile needs a valid name, found {name!r}")
    unknown = sorted(set(entry) - set(BOUNDS) - {"name"})
    if unknown:
        raise PolicyError(f"resource profile {name!r} declares unknown keys: {', '.join(unknown)}")
    values: dict[str, float] = {}
    for key, (low, high) in BOUNDS.items():
        value = entry.get(key)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise PolicyError(f"resource profile {name!r}: {key} must be a number")
        if value < low or value > high:
            raise PolicyError(f"resource profile {name!r}: {key}={value} is outside the bound "
                              f"[{low:g}, {high:g}]; zero, negative and absurd values are refused")
        if key != "cpus" and int(value) != value:
            raise PolicyError(f"resource profile {name!r}: {key} must be a whole number")
        values[key] = value
    if values["workspaceMb"] + values["tmpMb"] >= values["memoryMb"]:
        raise PolicyError(f"resource profile {name!r}: the workspace and /tmp live in memory, so "
                          "their sizes must leave room inside memoryMb")
    return ResourceProfile(
        name=name, cpus=float(values["cpus"]), memory_mb=int(values["memoryMb"]),
        pids=int(values["pids"]), workspace_mb=int(values["workspaceMb"]),
        tmp_mb=int(values["tmpMb"]),
        command_timeout_seconds=int(values["commandTimeoutSeconds"]),
        git_timeout_seconds=int(values["gitTimeoutSeconds"]),
        output_bytes=int(values["outputBytes"]), artifact_bytes=int(values["artifactBytes"]),
        read_bytes=int(values["readBytes"]), write_bytes=int(values["writeBytes"]),
        patch_bytes=int(values["patchBytes"]), list_entries=int(values["listEntries"]),
        search_results=int(values["searchResults"]), search_seconds=int(values["searchSeconds"]),
        search_file_bytes=int(values["searchFileBytes"]),
        session_ttl_seconds=int(values["sessionTtlSeconds"]),
    )


def parse_policy_document(document: Any) -> PolicyRegistry:
    """Validate the whole policy document, or refuse it with the first reason found."""
    from iacode_sandbox.tools import REGISTRY  # the registry imports this module

    if not isinstance(document, dict) or document.get("schemaVersion") != "1.0.0":
        raise PolicyError("the sandbox policy must declare schemaVersion 1.0.0")
    allowed_keys = {"schemaVersion", "policy", "imageProfiles", "networkProfiles",
                    "resourceProfiles", "requestEnvironment", "gitIdentity", "sandboxPolicies"}
    unknown = sorted(set(document) - allowed_keys)
    if unknown:
        raise PolicyError(f"the sandbox policy declares unknown keys: {', '.join(unknown)}")

    images: dict[str, ImageProfile] = {}
    for entry in document.get("imageProfiles") or []:
        name = entry.get("name")
        if not isinstance(name, str) or not _NAME.match(name) or name in images:
            raise PolicyError(f"an image profile needs a unique valid name, found {name!r}")
        repository = str(entry.get("repository") or "")
        if not re.fullmatch(r"[a-z0-9]+(?:[._/-][a-z0-9]+)*", repository):
            raise PolicyError(f"image profile {name!r} needs a repository name")
        images[name] = ImageProfile(name=name, context=str(entry.get("context") or ""),
                                    repository=repository,
                                    description=str(entry.get("description") or ""))
    if not images:
        raise PolicyError("the sandbox policy declares no image profile")

    networks = [entry.get("name") for entry in document.get("networkProfiles") or []]
    if sorted(networks) != sorted(NETWORK_PROFILES):
        raise PolicyError(f"the network profiles must be exactly {', '.join(NETWORK_PROFILES)}")

    resources = {}
    for entry in document.get("resourceProfiles") or []:
        profile = _resource_profile(entry)
        if profile.name in resources:
            raise PolicyError(f"resource profile {profile.name!r} is declared twice")
        resources[profile.name] = profile

    environment = document.get("requestEnvironment") or {}
    names = environment.get("allowedNames") or []
    for name in names:
        if not isinstance(name, str) or not re.fullmatch(r"[A-Z][A-Z0-9_]{0,63}", name):
            raise PolicyError(f"{name!r} is not an environment variable name")
        if FORBIDDEN_ENVIRONMENT.search(name):
            raise PolicyError(f"the policy may not let a command set {name!r}: it names a "
                              "credential or a host endpoint")
    max_length = environment.get("maxValueLength")
    if not isinstance(max_length, int) or not 1 <= max_length <= 4096:
        raise PolicyError("requestEnvironment.maxValueLength must be between 1 and 4096")

    identity = document.get("gitIdentity") or {}
    identity_name = str(identity.get("name") or "")
    identity_email = str(identity.get("email") or "")
    if not identity_name or not identity_email.endswith(".invalid"):
        raise PolicyError("the sandbox Git identity needs a name and an address under the "
                          "reserved .invalid domain, so a sandbox commit is never mistaken for a "
                          "person's")

    policies: dict[str, SandboxPolicy] = {}
    for entry in document.get("sandboxPolicies") or []:
        name = entry.get("name")
        if not isinstance(name, str) or not _NAME.match(name) or name in policies:
            raise PolicyError(f"a sandbox policy needs a unique valid name, found {name!r}")
        tools = entry.get("tools") or []
        unknown_tools = sorted(set(tools) - set(REGISTRY))
        if unknown_tools:
            raise PolicyError(f"policy {name!r} names tools that are not registered: "
                              + ", ".join(unknown_tools))
        access = entry.get("workspaceAccess")
        if access not in ("read-only", "read-write"):
            raise PolicyError(f"policy {name!r}: workspaceAccess must be read-only or read-write")
        if access == "read-only":
            writers = sorted(tool for tool in tools if REGISTRY[tool].access != "read")
            if writers:
                raise PolicyError(f"policy {name!r} is read-only but allows "
                                  + ", ".join(writers))
        image = images.get(entry.get("imageProfile"))
        resource = resources.get(entry.get("resourceProfile"))
        network = entry.get("networkProfile")
        if image is None or resource is None or network not in NETWORK_PROFILES:
            raise PolicyError(f"policy {name!r} names an image, resource or network profile that "
                              "does not exist")
        policies[name] = SandboxPolicy(
            name=name, tools=frozenset(tools), image=image, resources=resource,
            network_profile=network, workspace_access=access,
            request_environment_names=frozenset(names),
            request_environment_max_length=max_length,
            git_identity_name=identity_name, git_identity_email=identity_email)
    if not policies:
        raise PolicyError("the sandbox policy declares no policy")
    return PolicyRegistry(policies=policies, images=images)


def load_policy_registry(root: Path) -> PolicyRegistry:
    path = root / POLICY_PATH
    if not path.is_file():
        raise PolicyError(f"{POLICY_PATH.as_posix()} does not exist under {root}")
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise PolicyError(f"{POLICY_PATH.as_posix()} is not JSON: {error}") from None
    return parse_policy_document(document)
