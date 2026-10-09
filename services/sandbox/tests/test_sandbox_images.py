"""Content addressing includes every file that can change a sandbox image."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from iacode_sandbox.image import image_inputs, input_fingerprint
from sandbox_fixtures import repository_root


class SandboxImageInputTests:
    def test_node_lock_and_manifest_are_content_addressed_inputs(self) -> None:
        inputs = image_inputs(repository_root(), "services/sandbox/images/quality-node")
        assert "apps/web/package.json" in inputs
        assert "apps/web/package-lock.json" in inputs
        assert "services/sandbox/src/iacode_sandbox/helper.py" in inputs

    @pytest.mark.parametrize("profile", ["quality-python", "quality-node", "quality-java"])
    def test_quality_images_bind_the_policy_owned_secret_scanner(self, profile: str) -> None:
        inputs = image_inputs(repository_root(), f"services/sandbox/images/{profile}")
        assert ".iacode/policies/secret-scan-allowlist.json" in inputs
        assert "services/sandbox/images/quality_secret_scan.py" in inputs

    def test_an_external_input_changes_the_fingerprint(self, tmp_path: Path) -> None:
        root = tmp_path
        context = root / "images" / "quality"
        context.mkdir(parents=True)
        (context / "Dockerfile").write_text("FROM scratch\n", encoding="utf-8")
        (context / "image-inputs.json").write_text(
            json.dumps(["locks/tool.lock"]), encoding="utf-8"
        )
        (root / "locks").mkdir()
        lock = root / "locks" / "tool.lock"
        lock.write_text("version=1\n", encoding="utf-8")
        for helper in (
            "services/sandbox/src/iacode_sandbox/helper.py",
            "services/sandbox/src/iacode_sandbox/paths.py",
            "services/sandbox/src/iacode_sandbox/patching.py",
        ):
            path = root / helper
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(helper, encoding="utf-8")
        before = input_fingerprint(root, "images/quality")
        lock.write_text("version=2\n", encoding="utf-8")
        assert input_fingerprint(root, "images/quality") != before

    @pytest.mark.parametrize("entry", ["../escape", "/absolute", "missing.lock"])
    def test_unsafe_or_missing_external_inputs_are_refused(
        self, tmp_path: Path, entry: str
    ) -> None:
        context = tmp_path / "images" / "quality"
        context.mkdir(parents=True)
        (context / "Dockerfile").write_text("FROM scratch\n", encoding="utf-8")
        (context / "image-inputs.json").write_text(json.dumps([entry]), encoding="utf-8")
        for helper in (
            "services/sandbox/src/iacode_sandbox/helper.py",
            "services/sandbox/src/iacode_sandbox/paths.py",
            "services/sandbox/src/iacode_sandbox/patching.py",
        ):
            path = tmp_path / helper
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(helper, encoding="utf-8")
        with pytest.raises((ValueError, FileNotFoundError)):
            image_inputs(tmp_path, "images/quality")
