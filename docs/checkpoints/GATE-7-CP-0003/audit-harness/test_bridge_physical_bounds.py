"""Actual owned filesystem bounds and a labeled controlled growing-output boundary."""

import hashlib
import importlib.util
import io
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))
import audit_runner_bridge as bridge
from ledger_common import find_secrets


class BridgePhysicalBoundsTests(unittest.TestCase):
    def setUp(self):
        self.owner = tempfile.TemporaryDirectory(prefix="iacode-m2-physical-bounds-")
        self.addCleanup(self.owner.cleanup)
        self.parent = Path(self.owner.name)
        self.root = self.parent / "private"
        self.root.mkdir()
        self.inside = self.root / "inside.bin"
        self.inside.write_bytes(b"VALID_OWNED_NULL")
        self.outside = self.parent / "outside.bin"
        self.outside.write_bytes(b"OUTSIDE_FIXTURE_NOT_A_PUBLISHED_REPORT")

    def test_actual_inside_null_and_absolute_escape_refusal(self):
        frozen = bridge.FrozenInputs(self.root, [self.inside])
        frozen.verify()
        self.assertEqual(hashlib.sha256(self.inside.read_bytes()).hexdigest(), frozen.hashes["inside.bin"])
        with self.assertRaises(ValueError):
            bridge.FrozenInputs(self.root, [self.outside])

    def test_parent_relative_existing_escape_is_refused(self):
        with self.assertRaises(ValueError):
            bridge.FrozenInputs(self.root, [self.root / ".." / "outside.bin"])

    def test_parent_alias_in_the_source_root_is_refused(self):
        alias = self.root / ".." / "private"
        with self.assertRaises(ValueError):
            bridge.FrozenInputs(alias, [alias / "inside.bin"])

    def test_redirected_owned_ancestor_and_hardlink_are_refused(self):
        outside_directory = self.parent / "external-fixture"
        outside_directory.mkdir()
        (outside_directory / "fixture.bin").write_bytes(b"OUTSIDE_OWNED_FIXTURE")
        link = self.root / "redirect"
        if os.name == "nt":
            result = subprocess.run(["cmd", "/d", "/c", "mklink", "/J", str(link), str(outside_directory)],
                                    capture_output=True, timeout=10, check=False,
                                    creationflags=subprocess.CREATE_NO_WINDOW)
            self.assertEqual(0, result.returncode, "actual owned junction creation is a required premise")
        else:
            link.symlink_to(outside_directory, target_is_directory=True)
        try:
            with self.assertRaises(ValueError):
                bridge.FrozenInputs(self.root, [link / "fixture.bin"])
        finally:
            if os.name == "nt":
                link.rmdir()  # Only the actual freshly created junction, never its target.
            else:
                link.unlink()
        self.assertEqual(b"OUTSIDE_OWNED_FIXTURE", (outside_directory / "fixture.bin").read_bytes())
        hardlink = self.root / "alias.bin"
        os.link(self.inside, hardlink)
        with self.assertRaises(ValueError):
            bridge.FrozenInputs(self.root, [self.inside])

    def test_report_escape_keeps_producer_but_never_archives_outside_content(self):
        if os.name != "nt":
            self.skipTest("Actual privileged runner uses the Windows Job boundary")
        sys.path.insert(0, str(ROOT / "scripts/iacode"))
        from native_process import WindowsJob

        script = self.root / "runner.py"
        script.write_text("print('REAL_REPORT_PRODUCER')\n", encoding="utf-8")
        actor = bridge.ClosedBridge(bridge.FrozenInputs(self.root, [script]),
                                   {"bounds": bridge.Job((sys.executable, str(script)), 5,
                                                         ("../outside.bin",))},
                                   dict(os.environ), find_secrets, WindowsJob)
        actor._execute("bounds")
        observed = actor.results["bounds"]
        self.assertEqual(0, observed["producer"]["exitCode"])
        self.assertEqual("FAIL", observed["result"])
        self.assertEqual("ValueError", observed["postprocessingErrorType"])
        self.assertFalse(any(key.startswith("report-") for key in actor.artifacts["bounds"]))
        self.assertNotIn(self.outside.read_bytes(), actor.artifacts["bounds"].values())

    def test_output_prefix_is_fixed_before_a_controlled_actual_append(self):
        path = self.root / "producer.bin"
        primary = b"OBSERVED_PREFIX"
        path.write_bytes(primary)
        with path.open("r+b") as actual:
            class AppendAfterFirstRead:
                appended = False

                def __getattr__(self, name):
                    return getattr(actual, name)

                def read(self, size=-1):
                    block = actual.read(size)
                    if not self.appended:
                        self.appended = True
                        with path.open("ab") as writer:
                            writer.write(b"LATER_PRODUCER_SUFFIX")
                    return block

            # The append is an explicit boundary fault control, not OS/live acceptance.
            fact, raw = bridge.observe(AppendAfterFirstRead(), find_secrets)
        self.assertEqual(primary, raw)
        self.assertEqual(len(primary), fact["bytes"])
        self.assertEqual(hashlib.sha256(primary).hexdigest(), fact["sha256"])
        null, raw_null = bridge.observe(io.BytesIO(primary), find_secrets)
        self.assertEqual(primary, raw_null)
        self.assertEqual(null, fact)


if __name__ == "__main__":
    from ledger_common import use_utf8_stdout
    use_utf8_stdout()
    unittest.main()
