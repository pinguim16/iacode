"""A patch applies entirely or not at all, and only inside the workspace."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest
from iacode_sandbox.patching import PatchRejectedError, apply_patch

ORIGINAL = "def add(a, b):\n    return a - b\n\n\ndef sub(a, b):\n    return a - b\n"

FIX = """--- a/calculator.py
+++ b/calculator.py
@@ -1,2 +1,2 @@
 def add(a, b):
-    return a - b
+    return a + b
"""


@pytest.fixture
def workspace():
    with tempfile.TemporaryDirectory(prefix="iacode-patch-") as directory:
        root = Path(directory) / "workspace"
        root.mkdir()
        (root / "calculator.py").write_text(ORIGINAL, encoding="utf-8", newline="\n")
        yield root


class PatchApplyTests:
    def test_a_valid_patch_applies(self, workspace) -> None:
        changed = apply_patch(str(workspace), FIX, max_bytes=10000)
        assert changed == [{"path": "calculator.py", "change": "modified"}]
        assert "return a + b" in (workspace / "calculator.py").read_text(encoding="utf-8")

    def test_a_context_mismatch_changes_nothing(self, workspace) -> None:
        stale = FIX.replace("-    return a - b", "-    return b - a")
        with pytest.raises(PatchRejectedError) as refused:
            apply_patch(str(workspace), stale, max_bytes=10000)
        assert refused.value.code == "PATCH_CONTEXT_MISMATCH"
        assert (workspace / "calculator.py").read_text(encoding="utf-8") == ORIGINAL

    def test_a_multi_file_patch_with_one_bad_file_writes_no_file(self, workspace) -> None:
        second = """--- /dev/null
+++ b/new_module.py
@@ -0,0 +1 @@
+VALUE = 1
"""
        bad = FIX.replace("-    return a - b", "-    return nothing")
        with pytest.raises(PatchRejectedError):
            apply_patch(str(workspace), second + bad, max_bytes=10000)
        assert not (workspace / "new_module.py").exists()
        assert (workspace / "calculator.py").read_text(encoding="utf-8") == ORIGINAL

    def test_a_patch_can_create_and_delete_files(self, workspace) -> None:
        create = "--- /dev/null\n+++ b/pkg/new.py\n@@ -0,0 +1,2 @@\n+A = 1\n+B = 2\n"
        apply_patch(str(workspace), create, max_bytes=10000)
        assert (workspace / "pkg" / "new.py").read_text(encoding="utf-8") == "A = 1\nB = 2\n"
        delete = "--- a/pkg/new.py\n+++ /dev/null\n@@ -1,2 +0,0 @@\n-A = 1\n-B = 2\n"
        apply_patch(str(workspace), delete, max_bytes=10000)
        assert not (workspace / "pkg" / "new.py").exists()

    def test_a_patch_cannot_reach_outside_the_workspace(self, workspace) -> None:
        for target in ("../outside.py", "/etc/passwd", "C:/Windows/win.ini"):
            escape = f"--- /dev/null\n+++ b/{target}\n@@ -0,0 +1 @@\n+owned\n"
            with pytest.raises(PatchRejectedError) as refused:
                apply_patch(str(workspace), escape, max_bytes=10000)
            assert refused.value.code.startswith("PATH_"), target
        assert not (workspace.parent / "outside.py").exists()

    def test_a_malformed_or_oversized_patch_is_refused(self, workspace) -> None:
        for text, code in (("", "PATCH_EMPTY"), ("not a diff", "PATCH_MALFORMED"),
                           ("--- a/x\n", "PATCH_MALFORMED")):
            with pytest.raises(PatchRejectedError) as refused:
                apply_patch(str(workspace), text, max_bytes=10000)
            assert refused.value.code == code, text
        with pytest.raises(PatchRejectedError) as refused:
            apply_patch(str(workspace), FIX, max_bytes=10)
        assert refused.value.code == "PATCH_TOO_LARGE"
