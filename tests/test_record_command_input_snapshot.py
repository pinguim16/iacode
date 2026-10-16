from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))

from ledger_common import canonical_hash_path
import green_keeper


class CommandInputSnapshotTests(unittest.TestCase):
    def run_recorded(self, root: Path, source: str, executor: str) -> tuple[dict, dict]:
        (root / ".iacode").mkdir()
        checkpoint = root / "docs/checkpoints/TEST-CP-0001"
        checkpoint.mkdir(parents=True)
        (root / "mutator.py").write_text(source, encoding="utf-8")
        (root / "payload.txt").write_text("before", encoding="utf-8")
        for arguments in (
            ["git", "init", "-b", "main"],
            ["git", "add", "mutator.py", "payload.txt"],
            ["git", "-c", "user.name=IACode fixture", "-c", "user.email=fixture@example.invalid",
             "-c", "commit.gpgsign=false", "commit", "-m", "fixture input"],
        ):
            subprocess.run(arguments, cwd=root, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", check=True)
        before = {name: canonical_hash_path(root / name) for name in ("mutator.py", "payload.txt")}
        if executor == "recorder":
            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts/development-ledger/record_command.py"),
                 "--root", str(root), "--checkpoint", str(checkpoint),
                 "--purpose", "real child input snapshot control", "--input", "payload.txt",
                 "--", "python", "mutator.py", "payload.txt"],
                cwd=root, capture_output=True, text=True, encoding="utf-8", errors="replace",
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        else:
            _identifier, code, output = green_keeper._run_gate(
                root, checkpoint, "snapshot-control", {
                    "command": ["python", "mutator.py", "payload.txt"],
                    "purpose": "actual child input snapshot unit control",
                })
            self.assertEqual(code, 0, output)
        record = json.loads((checkpoint / "COMMANDS.jsonl").read_text(encoding="utf-8"))
        self.assertEqual(record["exitCode"], 0)
        return record, before

    def test_input_digests_are_frozen_before_a_real_child_rewrites_its_inputs(self) -> None:
        source = (
            "from pathlib import Path\n"
            "assert Path('payload.txt').read_text(encoding='utf-8') == 'before'\n"
            "Path('payload.txt').write_text('after', encoding='utf-8')\n"
            "Path(__file__).write_text(\"print('replacement input')\\n\", encoding='utf-8')\n"
        )
        for executor in ("recorder", "green-keeper"):
            with self.subTest(executor=executor), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                record, before = self.run_recorded(root, source, executor)
                after = {name: canonical_hash_path(root / name) for name in before}
                self.assertNotEqual(after, before, "the actual child must change both input files")
                self.assertEqual((root / "payload.txt").read_text(), "after")
                recorded = {entry["path"]: entry["hash"] for entry in record["inputsDigest"]}
                self.assertEqual(recorded, before)

    def test_stable_real_child_inputs_keep_their_pre_execution_identity(self) -> None:
        for executor in ("recorder", "green-keeper"):
            with self.subTest(executor=executor), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                record, before = self.run_recorded(
                    root, "from pathlib import Path\n"
                    "assert Path('payload.txt').read_text(encoding='utf-8') == 'before'\n", executor)
                self.assertEqual({entry["path"]: entry["hash"] for entry in record["inputsDigest"]},
                                 before)
                self.assertEqual({name: canonical_hash_path(root / name) for name in before}, before)


if __name__ == "__main__":
    unittest.main()
