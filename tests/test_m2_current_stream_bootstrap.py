"""Cold actual entry blocks with harmless work; original runtime/cleanup bodies never run."""

import os
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))


class M2CurrentStreamBootstrapTests(unittest.TestCase):
    def test_actual_capture_entry_blocks_reject_cold_bootstrap_removal(self):
        child = r'''
import ast
import sys
from pathlib import Path
assert sys.stdout.encoding.lower() == "cp1252"
sys.path.insert(0, sys.argv[1])
from ledger_common import use_utf8_stdout
source = Path(sys.argv[2])
tree = ast.parse(source.read_text(encoding="utf-8"))
entries = [node for node in tree.body if isinstance(node, ast.If)
           and ast.unparse(node.test) == "__name__ == '__main__'"]
assert len(entries) == 1
entry = entries[0]
boots = [node for node in entry.body if isinstance(node, ast.Expr)
         and isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name)
         and node.value.func.id == "use_utf8_stdout"]
assert len(boots) == 1
if sys.argv[3] == "omit-bootstrap": entry.body.remove(boots[0])
def harmless_work():
    print(chr(0x276F))
    print(chr(0x2713), file=sys.stderr)
    return 0
exec(compile(ast.Module(body=[entry], type_ignores=[]), str(source), "exec"),
     {"__name__": "__main__", "main": harmless_work, "use_utf8_stdout": use_utf8_stdout})
'''
        environment = {**os.environ, "PYTHONIOENCODING": "cp1252:strict", "PYTHONUTF8": "0"}
        environment.pop("PYTHONPATH", None)
        for name in ("capture_owned_build_history", "diagnose_owned_builder", "inspect_environment",
                     "owned_docker_scope", "probe_bridge_boundary", "prove_canonical_bridge"):
            source = ROOT / "docs/checkpoints/GATE-7-CP-0003/audit-harness" / (name + ".py")
            arguments = [sys.executable, "-S", "-P", "-c", child,
                         str(ROOT / "scripts/development-ledger"), str(source)]
            with self.subTest(entry=name):
                actual = subprocess.run([*arguments, "configured"], cwd=ROOT, env=environment,
                                        capture_output=True, timeout=15, check=False)
                self.assertEqual(0, actual.returncode, actual.stderr.decode("utf-8", errors="replace"))
                self.assertEqual(chr(0x276F).encode(), actual.stdout.strip())
                self.assertEqual(chr(0x2713).encode(), actual.stderr.strip())
                refused = subprocess.run([*arguments, "omit-bootstrap"], cwd=ROOT, env=environment,
                                         capture_output=True, timeout=15, check=False)
                self.assertNotEqual(0, refused.returncode)
                self.assertIn(b"UnicodeEncodeError", refused.stderr)


if __name__ == "__main__":
    from ledger_common import use_utf8_stdout
    use_utf8_stdout()
    unittest.main()
