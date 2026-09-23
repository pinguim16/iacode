"""The tools, executed for real inside sandboxes: filesystem, shell and local Git."""

from __future__ import annotations

import json

import pytest
from sandbox_fixtures import engine_harness

BUGGY = "def add(a, b):\n    return a - b\n"
FIX = ("--- a/calc.py\n+++ b/calc.py\n@@ -1,2 +1,2 @@\n def add(a, b):\n"
       "-    return a - b\n+    return a + b\n")


@pytest.fixture
def harness():
    created = engine_harness()
    yield created
    created.close()


def stdout(result) -> str:
    return str(result.output.get("stdout", ""))


class FilesystemToolTests:
    def test_write_read_list_search_and_patch(self, harness) -> None:
        run_id = harness.run_id()
        written = harness.execute("filesystem.write", {"path": "calc.py", "content": BUGGY},
                                  run_id=run_id)
        assert written.status == "SUCCEEDED" and written.output["size"] == len(BUGGY)
        read = harness.execute("filesystem.read", {"path": "calc.py"}, run_id=run_id)
        assert read.output["content"] == BUGGY
        listing = harness.execute("filesystem.list", {"path": "."}, run_id=run_id)
        assert {"path": "calc.py", "type": "file", "size": len(BUGGY)} in listing.output["entries"]
        found = harness.execute("filesystem.search", {"pattern": "return a - b"}, run_id=run_id)
        assert found.output["matches"] == [{"path": "calc.py", "line": 2,
                                            "text": "    return a - b"}]
        patched = harness.execute("filesystem.apply_patch", {"patch": FIX}, run_id=run_id)
        assert patched.status == "SUCCEEDED", patched
        after = harness.execute("filesystem.read", {"path": "calc.py"}, run_id=run_id)
        assert "return a + b" in after.output["content"]

    def test_a_failing_patch_changes_nothing(self, harness) -> None:
        run_id = harness.run_id()
        harness.execute("filesystem.write", {"path": "calc.py", "content": BUGGY}, run_id=run_id)
        stale = FIX.replace("-    return a - b", "-    return b - a")
        result = harness.execute("filesystem.apply_patch", {"patch": stale}, run_id=run_id)
        assert (result.status, result.error_code) == ("FAILED", "PATCH_CONTEXT_MISMATCH")
        read = harness.execute("filesystem.read", {"path": "calc.py"}, run_id=run_id)
        assert read.output["content"] == BUGGY

    def test_traversal_and_absolute_escapes_are_denied(self, harness) -> None:
        run_id = harness.run_id()
        for arguments in ({"path": "../etc/passwd"}, {"path": "/etc/passwd"},
                          {"path": "/proc/1/environ"}, {"path": "C:/Windows/win.ini"},
                          {"path": "..\\..\\etc\\passwd"}):
            result = harness.execute("filesystem.read", arguments, run_id=run_id)
            assert result.status == "DENIED", (arguments, result)
            assert result.error_code.startswith("PATH_")

    def test_a_symlink_that_points_outside_cannot_be_read_or_written_through(self,
                                                                            harness) -> None:
        run_id = harness.run_id()
        harness.shell("ln -s /etc/passwd leak && ln -s / root && ln -s /tmp door", run_id=run_id)
        for tool, arguments in (("filesystem.read", {"path": "leak"}),
                                ("filesystem.read", {"path": "root/etc/hostname"}),
                                ("filesystem.write", {"path": "leak", "content": "x"}),
                                ("filesystem.write", {"path": "door/planted", "content": "x"}),
                                ("filesystem.list", {"path": "root"})):
            result = harness.execute(tool, arguments, run_id=run_id)
            assert (result.status, result.error_code) == ("DENIED", "PATH_SYMLINK_ESCAPE"), \
                (tool, arguments, result)
        planted = harness.shell("test -e /tmp/planted && echo PLANTED || echo absent",
                                run_id=run_id)
        assert stdout(planted).strip() == "absent"

    def test_oversized_reads_and_writes_are_refused(self, harness) -> None:
        run_id = harness.run_id()
        limits = harness.service.policies.get("developer").resources
        harness.shell(f"python3 -c \"open('big.txt','w').write('z' * {limits.read_bytes + 1})\"",
                      run_id=run_id)
        read = harness.execute("filesystem.read", {"path": "big.txt"}, run_id=run_id)
        assert (read.status, read.error_code) == ("FAILED", "FILE_TOO_LARGE")
        write = harness.execute("filesystem.write",
                                {"path": "huge.txt", "content": "w" * (limits.write_bytes + 1)},
                                run_id=run_id)
        assert (write.status, write.error_code) == ("FAILED", "CONTENT_TOO_LARGE")

    def test_binary_content_is_refused_as_text(self, harness) -> None:
        run_id = harness.run_id()
        harness.shell("printf '\\377\\376\\000binary' > blob.bin", run_id=run_id)
        result = harness.execute("filesystem.read", {"path": "blob.bin"}, run_id=run_id)
        assert (result.status, result.error_code) == ("FAILED", "FILE_NOT_UTF8")


class ShellToolTests:
    def test_echo_stdout_stderr_and_exit_codes(self, harness) -> None:
        run_id = harness.run_id()
        ok = harness.shell("echo hello; echo oops >&2", run_id=run_id)
        assert (ok.status, ok.exit_code) == ("SUCCEEDED", 0)
        assert stdout(ok) == "hello\n" and ok.output["stderr"] == "oops\n"
        failed = harness.shell("exit 3", run_id=run_id)
        assert (failed.status, failed.exit_code) == ("FAILED", 3)

    def test_a_missing_executable_is_a_failure_with_its_exit_code(self, harness) -> None:
        run_id = harness.run_id()
        result = harness.shell("definitely-not-a-program-7731", run_id=run_id)
        assert result.status == "FAILED" and result.exit_code == 127
        assert "not found" in result.output["stderr"]

    def test_a_child_process_runs_and_reports(self, harness) -> None:
        run_id = harness.run_id()
        result = harness.shell("sh -c 'echo from-child'; echo from-parent", run_id=run_id)
        assert stdout(result).split() == ["from-child", "from-parent"]

    def test_the_working_directory_is_resolved_inside_the_workspace(self, harness) -> None:
        run_id = harness.run_id()
        harness.shell("mkdir -p sub", run_id=run_id)
        inside = harness.shell("pwd", run_id=run_id, cwd="sub")
        assert stdout(inside).strip() == "/workspace/sub"
        missing = harness.shell("pwd", run_id=run_id, cwd="absent")
        assert (missing.status, missing.error_code) == ("FAILED", "CWD_NOT_A_DIRECTORY")
        assert missing.exit_code is None
        escaping = harness.shell("pwd", run_id=run_id, cwd="../..")
        assert (escaping.status, escaping.error_code) == ("DENIED", "PATH_ESCAPE")

    def test_an_injected_host_command_only_reaches_the_sandbox(self, harness) -> None:
        run_id = harness.run_id()
        result = harness.shell("echo safe; touch /etc/pwned 2>&1; cat /etc/shadow 2>&1 | head -1;"
                               " touch /workspace/injected; ls /workspace", run_id=run_id)
        text = stdout(result)
        assert "Read-only file system" in text
        assert "Permission denied" in text
        assert "injected" in text

    def test_the_environment_is_the_allowlist_and_nothing_else(self, harness) -> None:
        run_id = harness.run_id()
        result = harness.execute("shell.exec", {"command": "env | sort",
                                                "environment": {"CI": "true"}}, run_id=run_id)
        names = {line.split("=", 1)[0] for line in stdout(result).splitlines() if "=" in line}
        assert "CI" in names
        assert names <= {"CI", "PATH", "HOME", "LANG", "LC_ALL", "PYTHONDONTWRITEBYTECODE",
                         "GIT_CONFIG_NOSYSTEM", "GIT_CONFIG_GLOBAL", "GIT_TERMINAL_PROMPT",
                         "GIT_ALLOW_PROTOCOL", "PWD", "SHLVL", "_", "OLDPWD"}


class GitToolTests:
    def test_status_diff_add_commit_log_and_show(self, harness) -> None:
        run_id = harness.run_id()
        harness.execute("filesystem.write", {"path": "calc.py", "content": BUGGY}, run_id=run_id)
        status = harness.execute("git.status", {}, run_id=run_id)
        assert "?? calc.py" in stdout(status)
        added = harness.execute("git.add", {"paths": ["calc.py"]}, run_id=run_id)
        assert added.status == "SUCCEEDED"
        committed = harness.execute("git.commit", {"message": "Add the calculator"}, run_id=run_id)
        assert committed.status == "SUCCEEDED", committed
        harness.execute("filesystem.apply_patch", {"patch": FIX}, run_id=run_id)
        working = harness.execute("git.diff", {}, run_id=run_id)
        assert "+    return a + b" in stdout(working)
        harness.execute("git.add", {"paths": ["calc.py"]}, run_id=run_id)
        staged = harness.execute("git.diff", {"staged": True}, run_id=run_id)
        assert "+    return a + b" in stdout(staged)
        assert stdout(harness.execute("git.diff", {}, run_id=run_id)) == ""
        harness.execute("git.commit", {"message": "Fix add"}, run_id=run_id)
        log = harness.execute("git.log", {"maxCount": 5}, run_id=run_id)
        lines = stdout(log).splitlines()
        assert "Fix add" in lines[0] and "IACode Agent" in lines[0]
        shown = harness.execute("git.show", {"revision": "HEAD"}, run_id=run_id)
        assert "Author: IACode Agent <agent@sandbox.iacode.invalid>" in stdout(shown)

    def test_no_remote_operation_is_offered_or_possible(self, harness) -> None:
        run_id = harness.run_id()
        denied = harness.execute("git.push", {}, run_id=run_id)
        assert (denied.status, denied.error_code) == ("DENIED", "UNKNOWN_TOOL")
        attempt = harness.shell(
            "git remote add origin https://github.com/pinguim16/iacode.git && "
            "git push origin HEAD:main 2>&1; echo push-exit:$?", run_id=run_id, timeoutSeconds=60)
        text = stdout(attempt)
        assert "push-exit:0" not in text
        assert "not allowed" in text or "Could not resolve" in text or "unable" in text

    def test_git_output_is_bounded(self, harness) -> None:
        run_id = harness.run_id()
        limit = harness.service.policies.get("developer").resources.output_bytes
        harness.shell(f"python3 -c \"open('wide.txt','w').write('line\\n' * {limit})\"; "
                      "git add wide.txt", run_id=run_id)
        diff = harness.execute("git.diff", {"staged": True}, run_id=run_id)
        assert diff.truncated is True
        assert len(stdout(diff)) == limit
        assert json.dumps(diff.output)
