"""Pure cleanup planning controls; these tests never operate Docker resources."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "m2_owned_docker_scope",
    ROOT / "docs/checkpoints/GATE-7-CP-0003/audit-harness/owned_docker_scope.py")
scope_module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(scope_module)


class CleanupTests(unittest.TestCase):
    def fixture(self):
        project = "iacode-m2cp3-fixture"
        before = {"images": [{"id": "old-own", "tags": [project + "/api:0.1.0"]},
                             {"id": "old-shared", "tags": ["shared:1"]}], "containers": []}
        scope = {"inheritedOwnedProject": project, "registeredProjects": [project], "before": before,
                 "claimedAuxiliaryImages": [{"id": "buildkit", "evidence": "exact registered builder",
                                              "allowedTags": ["moby/buildkit:buildx-stable-1"],
                                              "allowedDigestRepositories": ["moby/buildkit"]}]}
        current = {"images": [*before["images"], {"id": "new-own", "tags": [project + "/worker:0.1.0"]},
                              {"id": "new-other", "tags": ["other-app:1"]},
                              {"id": "buildkit", "tags": ["moby/buildkit:buildx-stable-1"]}],
                   "containers": [{"id": "own-container", "image": "new-own", "project": project}],
                   "networks": [{"id": "own-network", "project": project}, {"id": "other", "project": "other"}],
                   "volumes": [{"name": "own-volume", "project": project}, {"name": "other", "project": "other"}]}
        return scope, current

    def test_exact_ownership_not_general_delta_drives_cleanup(self):
        scope, current = self.fixture()
        plan = scope_module.cleanup_plan(scope, current)
        self.assertEqual(["buildkit", "new-own", "old-own"], plan["images"])
        self.assertEqual(["own-container"], plan["containers"])
        self.assertEqual(["own-network"], plan["networks"])
        self.assertEqual(["own-volume"], plan["volumes"])

    def test_external_container_reference_preserved_even_when_owned_tag(self):
        scope, current = self.fixture()
        current["containers"].append({"id": "other-container", "image": "new-own", "project": "other"})
        plan = scope_module.cleanup_plan(scope, current)
        self.assertNotIn("new-own", plan["images"])
        self.assertEqual(["other-container"], plan["preservedShared"][0]["externalContainers"])
        self.assertNotIn("other-container", plan["containers"])

    def test_external_alias_preserved_without_force(self):
        scope, current = self.fixture()
        current["images"][2]["tags"].append("other-application:1")
        plan = scope_module.cleanup_plan(scope, current)
        self.assertNotIn("new-own", plan["images"])
        self.assertEqual(["other-application:1"], plan["preservedShared"][0]["externalTags"])

    def test_auxiliary_external_alias_or_digest_is_not_owned(self):
        for field, value in (("tags", "other-application:1"),
                             ("digests", "other-application@sha256:abc")):
            scope, current = self.fixture()
            current["images"][-1].setdefault(field, []).append(value)
            plan = scope_module.cleanup_plan(scope, current)
            self.assertNotIn("buildkit", plan["images"])
            self.assertEqual("buildkit", plan["preservedShared"][0]["id"])

    def test_auxiliary_delta_without_evidence_and_preexisting_auxiliary_are_not_claimed(self):
        scope, current = self.fixture()
        scope["claimedAuxiliaryImages"] = [{"id": "new-other", "evidence": None},
                                           {"id": "old-shared", "evidence": "not enough: preexisting"}]
        plan = scope_module.cleanup_plan(scope, current)
        self.assertEqual(["new-own", "old-own"], plan["images"])

    def test_generic_project_claim_refused(self):
        scope, current = self.fixture()
        scope["registeredProjects"].append("other")
        with self.assertRaises(ValueError):
            scope_module.cleanup_plan(scope, current)


if __name__ == "__main__":
    unittest.main()
