"""Exercise a proposed implementation only; never claim the canonical source is repaired."""

import runpy
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT / "scripts/iacode"))
import native_editor
from native_execution_candidate import execute_owned


def candidate(arguments, **kwargs):
    return execute_owned(arguments, root=native_editor.ROOT,
                         job_factory=native_editor.WindowsJob, **kwargs)


if __name__ == "__main__":
    sys.path.insert(0, str(ROOT / "scripts/development-ledger"))
    from ledger_common import use_utf8_stdout
    use_utf8_stdout()
    native_editor.run_owned = candidate
    runpy.run_path(str(HERE / "test_native_producer_observation.py"), run_name="__main__")
