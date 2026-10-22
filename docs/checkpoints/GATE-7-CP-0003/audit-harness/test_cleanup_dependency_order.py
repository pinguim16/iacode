"""Operator staging controls: real Python children, isolated Docker/inventory doubles only."""

import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "tests"))
import test_m2_cleanup_operator as operator_controls
from ledger_common import load_json, write_json

ROOT = Path(__file__).resolve().parents[4]

scope_module = operator_controls.scope_module


class CleanupDependencyOrderTests(operator_controls.OperatorCleanupObservationTests):
    def staged(self, shared=False):
        image = {
            "id": "sha256:" + "9" * 64,
            "tags": ["moby/buildkit:buildx-stable-1"],
            "digests": [],
            "project": None,
            "size": 1,
        }
        builder = {
            "id": "exact-private-builder-fixture",
            "name": "private-builder",
            "image": image["id"],
            "project": None,
        }
        external = {
            "id": "concurrent-external-consumer-fixture",
            "name": "other-project",
            "image": image["id"],
            "project": "other-project",
        }
        self.scope["claimedAuxiliaryImages"] = [
            {
                "id": image["id"],
                "allowedTags": image["tags"],
                "evidence": "isolated private-builder fixture",
            }
        ]
        # Match the real constructor's measured identity (cmd-0183), rather than
        # presenting this known private builder as an unclaimed external container.
        self.scope["builderOwnership"] = {
            "id": builder["id"],
            "name": builder["name"],
            "imageId": image["id"],
            "cacheVolumes": [],
        }
        write_json(self.scope_path, self.scope)
        current = {
            **self.baseline,
            "containers": [builder, *([external] if shared else [])],
            "images": [image],
        }
        released = {**self.baseline, "containers": [external] if shared else [], "images": [image]}
        self.snapshot.side_effect = [current, released, released if shared else self.baseline]
        actual_run, operations = subprocess.run, []

        def transport(arguments, **kwargs):
            allowed = [
                ["docker", "buildx", "rm", self.scope["builder"]],
                ["docker", "image", "rm", image["id"]],
            ]
            self.assertIn(arguments, allowed)
            operations.append(arguments)
            return actual_run([sys.executable, "-c", "print('ISOLATED_OPERATOR_NULL')"], **kwargs)

        with patch.object(scope_module.subprocess, "run", side_effect=transport):
            code = scope_module.cleanup()
        receipt = load_json(self.checkpoint / "OWNED-RESOURCE-CLEANUP.json")
        self.assertEqual(0, code)
        self.assertEqual("PASS", receipt["result"])
        self.assertEqual(
            [], receipt["plan"]["images"], "the initial live consumer must preserve its image"
        )
        self.assertTrue(receipt["privateBuildxConfigRemoved"])
        return image, operations, receipt

    def test_builder_release_replans_and_removes_only_the_now_unshared_owned_image(self):
        image, operations, receipt = self.staged()
        self.assertEqual([image["id"]], receipt["postDependencyImagePlan"]["images"])
        self.assertEqual(["docker", "image", "rm", image["id"]], operations[-1])
        self.assertEqual(2, len(operations))

    def test_concurrent_external_consumer_remains_a_shared_preservation_null(self):
        image, operations, receipt = self.staged(shared=True)
        self.assertEqual([], receipt["postDependencyImagePlan"]["images"])
        self.assertEqual(
            image["id"], receipt["postDependencyImagePlan"]["preservedShared"][0]["id"]
        )
        self.assertEqual(1, len(operations), "no image removal or unrelated consumer operation")

    def test_external_baseline_change_stays_failed_but_does_not_retain_disposable_private_config(
        self,
    ):
        old = {
            "id": "external-old",
            "name": "external-app",
            "project": "another-project",
            "image": "external-image",
            "running": True,
        }
        replacement = {**old, "id": "external-replacement"}
        self.scope["before"]["containers"] = [old]
        write_json(self.scope_path, self.scope)
        current = {**self.baseline, "containers": [replacement]}
        self.snapshot.side_effect = [current, current, current]
        actual_run = subprocess.run

        def transport(arguments, **kwargs):
            self.assertEqual(["docker", "buildx", "rm", self.scope["builder"]], arguments)
            return actual_run(
                [sys.executable, "-c", "print('OWNED_DISPOSAL_EXTERNAL_CHANGE_CONTROL')"], **kwargs
            )

        with patch.object(scope_module.subprocess, "run", side_effect=transport):
            code = scope_module.cleanup()
        receipt = load_json(self.checkpoint / "OWNED-RESOURCE-CLEANUP.json")
        self.assertEqual(1, code)
        self.assertEqual(
            "FAIL", receipt["result"], "never silently accept or rewrite the original baseline"
        )
        self.assertFalse(receipt["unrelatedApplicationsUnchanged"])
        self.assertTrue(receipt["unrelatedApplicationsUnchangedDuringCleanup"])
        self.assertEqual("PASS", receipt["ownedResourceCleanupResult"])
        self.assertTrue(receipt["privateBuildxConfigRemoved"])
        self.assertEqual(
            "CLEANED_EXTERNAL_OBSERVATION_CHANGED", load_json(self.scope_path)["status"]
        )

    def test_private_cache_external_consumer_refuses_before_any_disposal_effect(self):
        name = "buildx_buildkit_" + self.scope["builder"] + "0"
        cache = name + "_state"
        builder = {
            "id": "exact-owned-builder",
            "name": name,
            "image": "builder-image",
            "project": None,
        }
        self.scope["builderOwnership"] = {
            "id": builder["id"],
            "name": name,
            "imageId": builder["image"],
            "cacheVolumes": [cache],
        }
        write_json(self.scope_path, self.scope)
        self.snapshot.return_value = {
            **self.baseline,
            "containers": [builder],
            "volumes": [{"name": cache, "id": cache, "project": None}],
        }
        with (
            patch.object(
                scope_module, "docker", return_value="exact-owned-builder\nexternal-consumer\n"
            ),
            patch.object(scope_module.subprocess, "run") as mutation,
            self.assertRaisesRegex(
                ValueError, "PRIVATE_CACHE_HAS_UNVERIFIED_OR_EXTERNAL_CONSUMERS"
            ),
        ):
            scope_module.cleanup()
        mutation.assert_not_called()
        self.assertTrue(Path(self.config.name).exists())
        self.assertFalse((self.checkpoint / "OWNED-RESOURCE-CLEANUP.json").exists())


if __name__ == "__main__":
    from ledger_common import use_utf8_stdout

    use_utf8_stdout()
    unittest.main()
