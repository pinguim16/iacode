"""The one path resolver: no path it returns lies outside the workspace."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path, PurePosixPath

import pytest
from iacode_sandbox.paths import PathRejectedError, normalize_request_path, resolve_workspace_path

#: Every spelling of an escape the resolver must refuse, with the code it must give.
HOSTILE = (
    ("../etc/passwd", "PATH_ESCAPE"),
    ("a/../../etc/passwd", "PATH_ESCAPE"),
    ("./../../..", "PATH_ESCAPE"),
    ("/etc/passwd", "PATH_ABSOLUTE_OUTSIDE"),
    ("/workspace/../etc/passwd", "PATH_ESCAPE"),
    ("/workspacex/file", "PATH_ABSOLUTE_OUTSIDE"),
    ("C:\\Windows\\system32", "PATH_BACKSLASH"),
    ("C:/Users/owner/.ssh/id_rsa", "PATH_DRIVE"),
    ("c:relative", "PATH_DRIVE"),
    ("\\\\server\\share\\file", "PATH_BACKSLASH"),
    ("//server/share/file", "PATH_UNC"),
    ("..\\..\\secret", "PATH_BACKSLASH"),
    ("a\x00b", "PATH_NULL_BYTE"),
    ("a\nb", "PATH_CONTROL_CHARACTER"),
    ("", "PATH_EMPTY"),
    ("   ", "PATH_EMPTY"),
    ("x" * 2000, "PATH_TOO_LONG"),
)


class PathResolverTests:
    def test_every_hostile_spelling_is_refused_with_its_own_code(self) -> None:
        for requested, code in HOSTILE:
            with pytest.raises(PathRejectedError) as refused:
                normalize_request_path(requested)
            assert refused.value.code == code, requested

    def test_a_non_string_is_refused(self) -> None:
        for value in (None, 7, ["a"], {"path": "a"}):
            with pytest.raises(PathRejectedError):
                normalize_request_path(value)

    def test_legitimate_paths_are_normalised_inside_the_workspace(self) -> None:
        """The null control: the same function accepts what it should."""
        cases = {
            ".": PurePosixPath("."),
            "src/module.py": PurePosixPath("src/module.py"),
            "./src//module.py": PurePosixPath("src/module.py"),
            "src/../README.md": PurePosixPath("README.md"),
            "/workspace/src/module.py": PurePosixPath("src/module.py"),
            "/workspace": PurePosixPath("."),
        }
        for requested, expected in cases.items():
            assert normalize_request_path(requested) == expected, requested

    def test_the_workspace_itself_is_not_a_file(self) -> None:
        with pytest.raises(PathRejectedError) as refused:
            normalize_request_path(".", allow_root=False)
        assert refused.value.code == "PATH_IS_WORKSPACE"


@pytest.fixture
def workspace():
    with tempfile.TemporaryDirectory(prefix="iacode-resolver-") as directory:
        root = Path(directory) / "workspace"
        outside = Path(directory) / "outside"
        root.mkdir()
        outside.mkdir()
        (outside / "secret.txt").write_text("not yours", encoding="utf-8")
        (root / "inside.txt").write_text("yours", encoding="utf-8")
        yield root, outside


class SymlinkContainmentTests:
    def test_a_link_to_a_file_outside_is_refused_for_reading(self, workspace) -> None:
        root, outside = workspace
        os.symlink(outside / "secret.txt", root / "leak")
        with pytest.raises(PathRejectedError) as refused:
            resolve_workspace_path(root, "leak")
        assert refused.value.code == "PATH_SYMLINK_ESCAPE"

    def test_a_link_to_a_directory_outside_is_refused_for_writing(self, workspace) -> None:
        root, outside = workspace
        os.symlink(outside, root / "door", target_is_directory=True)
        with pytest.raises(PathRejectedError) as refused:
            resolve_workspace_path(root, "door/planted.txt", for_write=True)
        assert refused.value.code == "PATH_SYMLINK_ESCAPE"
        assert not (outside / "planted.txt").exists()

    def test_a_link_to_the_root_is_refused(self, workspace) -> None:
        root, _outside = workspace
        os.symlink("/", root / "root")
        for requested in ("root/etc/passwd", "root", "root/proc/1/environ"):
            with pytest.raises(PathRejectedError):
                resolve_workspace_path(root, requested)

    def test_a_relative_link_that_climbs_out_is_refused(self, workspace) -> None:
        root, _outside = workspace
        os.symlink("../outside/secret.txt", root / "climb")
        with pytest.raises(PathRejectedError):
            resolve_workspace_path(root, "climb")

    def test_a_link_that_stays_inside_is_followed(self, workspace) -> None:
        """The null control: containment, not a ban on links."""
        root, _outside = workspace
        os.symlink(root / "inside.txt", root / "alias")
        resolved = resolve_workspace_path(root, "alias")
        assert resolved.read_text(encoding="utf-8") == "yours"
