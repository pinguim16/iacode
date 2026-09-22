"""Suite-wide wiring.

The runtime lives in ``src/``; the suite is executed from the repository in development and from
``/app/agent_runtime_tests`` inside the API image, where the package is installed. Adding the source
directory when it exists makes both work without a second configuration.
"""

from __future__ import annotations

import sys
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / "src"
if SOURCE.is_dir() and str(SOURCE) not in sys.path:
    sys.path.insert(0, str(SOURCE))

# The suite's own modules are imported by name (``from runtime_doubles import ...``) because
# pytest's rootdir differs between the repository and the image, and a package-relative import
# would work in exactly one of them. The module names carry the ``runtime_`` prefix because two
# suites run in the same interpreter and pytest refuses two modules with one basename.
if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
