"""Run the evaluator suite from a checkout or from its installed image."""

from __future__ import annotations

import sys
from pathlib import Path

# These are input repositories for live evaluator scenarios, not tests of the evaluator package.
# Keeping them under ``tests/fixtures`` makes their provenance obvious, while excluding them from
# collection prevents equal module names in independent snapshots from colliding in pytest.
collect_ignore_glob = ["fixtures/**"]

ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / ".iacode" / "policies").is_dir()
)
for source in (
    Path(__file__).resolve().parents[1] / "src",
    ROOT / "packages" / "contracts" / "src",
):
    if source.is_dir() and str(source) not in sys.path:
        sys.path.insert(0, str(source))
