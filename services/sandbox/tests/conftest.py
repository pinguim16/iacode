"""Suite-wide wiring for the sandbox suite.

The suite runs in two places: from the repository during development, and from
``/app/sandbox_tests`` inside the sandbox service's image, where the package is installed and the
container engine's socket is mounted. Adding the source directory when it exists makes both work
without a second configuration, the arrangement the agent runtime's suite uses.

The suite's own helper module carries the ``sandbox_`` prefix because pytest refuses two modules
with one basename in one interpreter.
"""

from __future__ import annotations

import sys
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / "src"
if SOURCE.is_dir() and str(SOURCE) not in sys.path:
    sys.path.insert(0, str(SOURCE))

if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
