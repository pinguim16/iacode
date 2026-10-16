"""Remove only exact observed failed owned test directories; never a broad cleanup."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "scripts/iacode"))
from native_process import remove_owned_directory  # noqa: E402

temporary = Path("C:/Users/cesar/AppData/Local/Temp").resolve()
results = []
for name in ("iacode-native-editor-2hzp2ekf", "iacode-native-editor-aorj2q1p", "iacode-desktop-live-hj33m0qt"):
    target = temporary / name
    existed = target.exists()
    retries = remove_owned_directory(target, temporary)
    results.append({"name": name, "existed": existed, "removed": not target.exists(), "retries": retries})
print(json.dumps(results))
