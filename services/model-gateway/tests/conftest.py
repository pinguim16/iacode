"""Make the fixtures package importable when the suite runs from a copied directory.

The gate executes these tests inside the API image, where the suite lives at ``/app/gateway_tests``
rather than under the repository. Adding the suite's own directory to the path is what lets
``from fixtures.doubles import ...`` resolve in both places without the import lines differing.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
