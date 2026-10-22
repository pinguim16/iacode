"""Bind the actual private-builder output and a baseline-tag restoration obligation."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

from owned_docker_scope import SCOPE, child_environment, docker

sys.path.insert(
    0, str(Path(__file__).resolve().parents[1].parents[2] / "scripts/development-ledger")
)
from ledger_common import find_secrets, load_json, utc_now, write_json

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]


def main():
    scope = load_json(SCOPE)
    receipt = load_json(CHECKPOINT / "resource-observations/build-history/run-0003/RECEIPT.json")
    if receipt["builder"] != scope["builder"]:
        raise ValueError("Builder receipt mismatch")
    observation = next(
        row
        for row in receipt["observations"]
        if row["arguments"][-1] == "u1y9zh45oqq6pnzd7qtnqudhn"
    )
    fact = observation["streams"]["stdout"]
    path = CHECKPOINT / fact["path"]
    raw = path.read_bytes()
    if (
        observation["exitCode"] != 0
        or fact["refused"]
        or len(raw) != fact["bytes"]
        or hashlib.sha256(raw).hexdigest() != fact["sha256"]
        or find_secrets(raw.decode("utf-8", errors="strict"))
    ):
        raise ValueError("Exact safe history observation required")
    document = json.loads(raw)
    if (
        document["Status"] != "completed"
        or document["Target"] != "builder"
        or document["Dockerfile"].replace("\\", "/") != "apps/web/Dockerfile"
        or document["VCSRepository"] != "https://github.com/pinguim16/iacode.git"
        or document["VCSRevision"] != "823cf164c6931dab7f957c92721ded7a916655bd"
    ):
        raise ValueError("Unexpected build source")
    images = [
        row["Digest"]
        for row in document["Attachments"]
        if row["Type"] == "application/vnd.oci.image.manifest.v1+json"
    ]
    if len(images) != 1 or re.fullmatch(r"sha256:[0-9a-f]{64}", images[0]) is None:
        raise ValueError("One actual built image descriptor required")
    image = images[0]
    tag = "iacode/web-toolchain:0.1.0"
    current = docker(
        ["image", "inspect", "--format", "{{.Id}}", tag], environment=child_environment()
    ).strip()
    baseline = next(row["id"] for row in scope["before"]["images"] if tag in row["tags"])
    if current != image or image in {row["id"] for row in scope["before"]["images"]}:
        raise ValueError("Actual newly loaded image must match its private build result")
    claims = scope.setdefault("claimedAuxiliaryImages", [])
    if not any(row["id"] == image for row in claims):
        claims.append(
            {
                "id": image,
                "allowedTags": [tag],
                "allowedDigestRepositories": ["iacode/web-toolchain"],
                "evidence": fact["path"],
                "evidenceSha256": fact["sha256"],
                "builder": scope["builder"],
            }
        )
    restores = scope.setdefault("tagRestorations", [])
    if not any(row["tag"] == tag for row in restores):
        restores.append(
            {
                "tag": tag,
                "baselineImageId": baseline,
                "producedImageIds": [image],
                "evidence": fact["path"],
                "requiredBeforeOwnedImageRemoval": True,
            }
        )
    write_json(SCOPE, scope)
    write_json(
        CHECKPOINT / "OWNED-WEB-IMAGE-CLAIM.json",
        {
            "observedAt": utc_now(),
            "imageId": image,
            "tag": tag,
            "privateBuilder": scope["builder"],
            "historyEvidence": fact["path"],
            "historySha256": fact["sha256"],
            "baselineImageId": baseline,
            "tagRestorationRequired": True,
            "cleanupExecuted": False,
            "note": (
                "Keep the original preexisting tag/image; remove only the pro"
                "ven produced replacement after all tests and safe restoratio"
                "n."
            ),
        },
    )
    print(
        json.dumps(
            {
                "ownedImage": image,
                "baselineImagePreserved": baseline,
                "tagRestorationRequired": True,
                "cleanupExecuted": False,
            }
        )
    )
    return 0


if __name__ == "__main__":
    from ledger_common import use_utf8_stdout

    use_utf8_stdout()
    raise SystemExit(main())
