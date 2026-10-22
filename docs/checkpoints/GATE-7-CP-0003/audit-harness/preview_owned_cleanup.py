"""Resolve exact private disposal targets without changing Docker or filesystem resources."""

import json
import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))
from audit_runner_bridge import cleanup_plan
from ledger_common import load_json, utc_now, write_json
from owned_docker_scope import SCOPE, child_environment, snapshot


def main():
    child_environment()
    scope = load_json(SCOPE)
    history = load_json(CHECKPOINT / "resource-observations/build-history/run-0005/RECEIPT.json")
    if (history["builder"] != scope["builder"]
            or history["result"] != "CAPTURED_NOT_OWNERSHIP_CLAIM_OR_ACCEPTANCE"
            or any(row["status"] not in {"completed", "canceled", "failed"}
                   for row in history["inspectSummary"])):
        raise ValueError("Complete quiescent private history observation required")
    current = snapshot()
    plan = cleanup_plan(scope, current)
    builder = scope["builderOwnership"]
    released = {**current, "containers": [row for row in current["containers"] if row["id"] != builder["id"]]}
    forecast = cleanup_plan(scope, released)
    external = [row for row in current["containers"] if row.get("project") == "esteira-videos"]
    if any(row["id"] in plan["containers"] for row in external):
        raise ValueError("Other project's container entered the disposal plan")
    images = {row["id"] for row in current["images"]}
    if any(row["baselineImageId"] not in images for row in scope.get("tagRestorations", [])):
        raise ValueError("Original preexisting image for safe tag restoration is absent")
    document = {"observedAt": utc_now(), "kind": "READ_ONLY_DISPOSAL_PREVIEW_NOT_EXECUTION",
        "builder": builder, "privateBuildxConfig": scope["privateBuildxConfig"], "initialPlan": plan,
        "projectedPostBuilderPlan": forecast, "projectionIsNotActualExecution": True,
        "preexistingTagRestorations": scope.get("tagRestorations", []),
        "externalProjectContainersExcluded": [row["id"] for row in external],
        "dockerMutationsPerformed": False, "fileResourceDeletionsPerformed": False}
    folder = CHECKPOINT / "cleanup-previews"
    folder.mkdir(exist_ok=True)
    target = folder / ("run-" + f"{len(list(folder.glob('run-*.json'))) + 1:04d}" + ".json")
    write_json(target, document)
    print(json.dumps({"builder": scope["builder"], "privateConfig": scope["privateBuildxConfig"],
        "projectedImages": forecast["images"], "networks": plan["networks"], "volumes": plan["volumes"],
        "builderCacheVolumes": builder["cacheVolumes"], "externalContainersExcluded": len(external),
        "deletionsPerformed": False}))
    return 0


if __name__ == "__main__":
    from ledger_common import use_utf8_stdout
    use_utf8_stdout()
    raise SystemExit(main())
