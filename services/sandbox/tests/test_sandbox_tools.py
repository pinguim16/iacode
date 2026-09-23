"""The closed tool registry and what each tool builds for the helper."""

from __future__ import annotations

import pytest
from iacode_sandbox.tools import REGISTRY, ToolRejectedError, build_helper_request
from sandbox_fixtures import policies

#: The tools the Gate specifies, and no more.
EXPECTED_TOOLS = {
    "filesystem.list", "filesystem.read", "filesystem.search", "filesystem.write",
    "filesystem.apply_patch", "shell.exec", "git.status", "git.diff", "git.log", "git.show",
    "git.add", "git.commit",
}

#: Git verbs this Gate does not offer, however they are asked for.
ABSENT_GIT_VERBS = ("git.push", "git.fetch", "git.pull", "git.clone", "git.remote", "git.reset",
                    "git.clean", "git.rebase", "git.filter-repo", "git.config", "git.checkout")


class ToolRegistryTests:
    def test_the_registry_is_exactly_the_specified_set(self) -> None:
        assert set(REGISTRY) == EXPECTED_TOOLS

    def test_an_unknown_tool_is_refused_and_never_mapped_to_a_shell(self) -> None:
        developer = policies().get("developer")
        for name in ("shell", "bash", "rm -rf /", "exec", "python", "filesystem.delete",
                     "os.system", "shell.exec ", "SHELL.EXEC"):
            with pytest.raises(ToolRejectedError) as refused:
                build_helper_request(name, {"command": "true"}, developer)
            assert refused.value.code == "UNKNOWN_TOOL", name

    def test_no_remote_or_destructive_git_verb_exists(self) -> None:
        developer = policies().get("developer")
        for name in ABSENT_GIT_VERBS:
            with pytest.raises(ToolRejectedError) as refused:
                build_helper_request(name, {}, developer)
            assert refused.value.code == "UNKNOWN_TOOL", name

    def test_a_tool_outside_the_policy_is_refused(self) -> None:
        reviewer = policies().get("reviewer")
        for name in ("filesystem.write", "filesystem.apply_patch", "shell.exec", "git.add",
                     "git.commit"):
            with pytest.raises(ToolRejectedError) as refused:
                build_helper_request(name, {"path": "a", "content": "b", "patch": "c",
                                            "command": "d", "paths": ["a"], "message": "m"},
                                     reviewer)
            assert refused.value.code == "TOOL_NOT_IN_POLICY", name

    def test_an_argument_a_tool_does_not_declare_is_refused(self) -> None:
        developer = policies().get("developer")
        for extra in ({"network": "full"}, {"memory": "unlimited"}, {"mount": "C:\\"},
                      {"image": "ubuntu:latest"}, {"privileged": True}, {"user": "root"}):
            with pytest.raises(ToolRejectedError) as refused:
                build_helper_request("shell.exec", {"command": "true", **extra}, developer)
            assert refused.value.code == "ARGUMENT_UNKNOWN", extra

    def test_a_wrong_type_is_refused_with_its_own_reason(self) -> None:
        developer = policies().get("developer")
        for tool, arguments in (("filesystem.read", {"path": 7}),
                                ("shell.exec", {"command": ["ls"]}),
                                ("shell.exec", {"command": "ls", "timeoutSeconds": True}),
                                ("filesystem.list", {"depth": "2"})):
            with pytest.raises(ToolRejectedError) as refused:
                build_helper_request(tool, arguments, developer)
            assert refused.value.code == "ARGUMENT_WRONG_TYPE", (tool, arguments)
        with pytest.raises(ToolRejectedError) as missing:
            build_helper_request("filesystem.read", {}, developer)
        assert missing.value.code == "ARGUMENT_MISSING"

    def test_a_request_may_lower_a_timeout_and_never_raise_it(self) -> None:
        developer = policies().get("developer")
        ceiling = developer.resources.command_timeout_seconds
        lowered = build_helper_request("shell.exec", {"command": "true", "timeoutSeconds": 5},
                                       developer)
        assert lowered["timeoutSeconds"] == 5
        with pytest.raises(ToolRejectedError) as refused:
            build_helper_request("shell.exec",
                                 {"command": "true", "timeoutSeconds": ceiling + 1}, developer)
        assert refused.value.code == "ARGUMENT_OUT_OF_RANGE"

    def test_the_limits_come_from_the_policy(self) -> None:
        developer = policies().get("developer")
        built = build_helper_request("filesystem.read", {"path": "a"}, developer)
        assert built["maxBytes"] == developer.resources.read_bytes
        built = build_helper_request("shell.exec", {"command": "true"}, developer)
        assert built["outputBytes"] == developer.resources.output_bytes

    def test_the_command_environment_is_an_allowlist(self) -> None:
        developer = policies().get("developer")
        allowed = build_helper_request("shell.exec", {"command": "true",
                                                      "environment": {"CI": "1"}}, developer)
        assert allowed["environment"] == {"CI": "1"}
        for name in ("DEVWORLD_API_KEY", "PATH", "HOME", "GITHUB_TOKEN", "DOCKER_HOST"):
            with pytest.raises(ToolRejectedError) as refused:
                build_helper_request("shell.exec", {"command": "true",
                                                    "environment": {name: "x"}}, developer)
            assert refused.value.code == "ENVIRONMENT_NOT_ALLOWED", name

    def test_a_hostile_path_is_refused_before_the_helper(self) -> None:
        developer = policies().get("developer")
        for tool, arguments in (("filesystem.read", {"path": "../../etc/passwd"}),
                                ("filesystem.write", {"path": "/etc/cron.d/x", "content": ""}),
                                ("shell.exec", {"command": "true", "cwd": "C:/Windows"}),
                                ("git.add", {"paths": ["../outside"]})):
            with pytest.raises(ToolRejectedError) as refused:
                build_helper_request(tool, arguments, developer)
            assert refused.value.code.startswith("PATH_"), (tool, refused.value.code)


class GitOperationTests:
    def test_every_git_tool_builds_a_fixed_argument_vector(self) -> None:
        developer = policies().get("developer")
        for tool, arguments, verb in (
                ("git.status", {}, "status"), ("git.diff", {"staged": True}, "diff"),
                ("git.log", {"maxCount": 5}, "log"), ("git.show", {"revision": "HEAD~1"}, "show"),
                ("git.add", {"paths": ["a.py"]}, "add"),
                ("git.commit", {"message": "Fix"}, "commit")):
            built = build_helper_request(tool, arguments, developer)
            assert built["op"] == "git"
            assert built["argv"][0] == "git"
            assert verb in built["argv"]

    def test_the_staged_diff_is_asked_for_explicitly(self) -> None:
        developer = policies().get("developer")
        assert "--staged" in build_helper_request("git.diff", {"staged": True},
                                                  developer)["argv"]
        assert "--staged" not in build_helper_request("git.diff", {}, developer)["argv"]

    def test_a_revision_that_looks_like_an_option_is_refused(self) -> None:
        developer = policies().get("developer")
        for revision in ("--output=/tmp/x", "-p", "HEAD;rm -rf /", "$(id)", "a b"):
            with pytest.raises(ToolRejectedError) as refused:
                build_helper_request("git.show", {"revision": revision}, developer)
            assert refused.value.code == "GIT_REVISION_INVALID", revision

    def test_a_commit_skips_hooks_and_carries_the_message_as_one_argument(self) -> None:
        developer = policies().get("developer")
        built = build_helper_request("git.commit", {"message": "a; rm -rf /"}, developer)
        assert "--no-verify" in built["argv"]
        assert built["argv"][-1] == "a; rm -rf /"
