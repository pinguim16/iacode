"""Hash only the four previously declared global configuration files; never edit them."""

import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(
    0, str(Path(__file__).resolve().parents[1].parents[2] / "scripts/development-ledger")
)
from ledger_common import load_json, utc_now, write_json

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]


def main():
    prior = load_json(CHECKPOINT / "ENVIRONMENT-SCOPE.json")
    allowed = {
        "C:/Users/cesar/.codex/config.toml",
        "C:/Users/cesar/.gitconfig",
        "C:/Users/cesar/.config/git/ignore",
        "C:/Program Files/Git/etc/gitconfig",
    }
    if {row["path"] for row in prior["globalConfigurations"]} != allowed:
        raise ValueError("Global read scope must remain exactly the four original files")
    observations = []
    for row in prior["globalConfigurations"]:
        current = hashlib.sha256(Path(row["path"]).read_bytes()).hexdigest()
        observations.append(
            {
                "path": row["path"],
                "baseline": row["before"],
                "observed": current,
                "unchanged": current == row["before"],
            }
        )
    folder = CHECKPOINT / "environment-preservation"
    folder.mkdir(exist_ok=True)
    target = folder / ("run-" + f"{len(list(folder.glob('run-*.json'))) + 1:04d}" + ".json")
    document = {
        "observedAt": utc_now(),
        "kind": "READ_ONLY_GLOBAL_CONFIGURATION_HASH_COMPARISON",
        "globalConfigurations": observations,
        "allUnchanged": all(row["unchanged"] for row in observations),
        "otherChatSettingWritesPerformed": False,
        "applicationRestartsPerformed": False,
        "newAuditorTurnStarted": False,
        "limitation": (
            "Other-chat preservation records no writes, not a newly measured chat-database hash."
        ),
    }
    write_json(target, document)
    print(
        json.dumps({"filesCompared": len(observations), "allUnchanged": document["allUnchanged"]})
    )
    return int(not document["allUnchanged"])


if __name__ == "__main__":
    from ledger_common import use_utf8_stdout

    use_utf8_stdout()
    raise SystemExit(main())
