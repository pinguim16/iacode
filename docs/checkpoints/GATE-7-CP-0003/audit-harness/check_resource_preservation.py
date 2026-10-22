"""Compare captured exact identities; this is progress evidence, not final cleanup."""

from __future__ import annotations

import json
import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))
from ledger_common import load_json, utc_now, write_json


def main():
    scope = load_json(CHECKPOINT / "OWNED-DOCKER-SCOPE.json")
    observations = sorted((CHECKPOINT / "resource-observations").glob("run-*.json"))
    latest = observations[-1]
    current = load_json(latest)
    previous = {row["id"]: row for row in scope["before"]["containers"]}
    now = {row["id"]: row for row in current["containers"]}
    changed = [identifier for identifier, row in previous.items() if now.get(identifier) != row]
    new_containers = [row for identifier, row in now.items() if identifier not in previous]
    baseline_images = {row["id"] for row in scope["before"]["images"]}
    new_images = [row for row in current["images"] if row["id"] not in baseline_images]
    receipt = {"recordedAt": utc_now(), "observedAt": current["observedAt"],
               "kind": "PROGRESS_NOT_CLEANUP_OR_ACCEPTANCE",
               "inventorySource": latest.relative_to(CHECKPOINT).as_posix(),
               "baselineContainers": len(previous), "changedBaselineContainerIds": changed,
               "baselineContainersUnchanged": not changed, "newContainers": new_containers,
               "newImages": new_images,
               "dockerConfigUnchanged": current["dockerConfigHash"] == scope["before"]["dockerConfigHash"],
               "finalCleanup": "PENDING_WHILE_CANONICAL_TESTS_ACTIVE", "deletionsPerformed": False}
    output = CHECKPOINT / "resource-preservation"
    output.mkdir(exist_ok=True)
    index = len(list(output.glob("run-*.json"))) + 1
    write_json(output / f"run-{index:04d}.json", receipt)
    print(json.dumps({"baselineContainersUnchanged": receipt["baselineContainersUnchanged"],
                      "baselineContainers": len(previous), "newContainers": len(new_containers),
                      "newImages": len(new_images), "finalCleanup": receipt["finalCleanup"]}))
    return int(bool(changed) or not receipt["dockerConfigUnchanged"])


if __name__ == "__main__":
    from ledger_common import use_utf8_stdout
    use_utf8_stdout()
    raise SystemExit(main())
