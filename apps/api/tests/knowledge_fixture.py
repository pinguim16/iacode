"""Synthetic validation-only source deployment, never production content or inferred user rights."""

from __future__ import annotations

import hashlib
import json
import uuid
from datetime import timedelta
from pathlib import Path

from iacode_knowledge.domain import canonical


def deploy_source(
    root: Path,
    project: str,
    now,
    *,
    name: str = "migration",
    revision: str = "fixture-v1",
    text: str = "PostgreSQL migrations preserve records. Exact citations bind source versions.",
    grant_updates: dict | None = None,
) -> dict:
    """Create explicit owned synthetic inputs; the real adapter still validates every byte."""
    if not name.replace("-", "").isalnum():
        raise ValueError("invalid fixture source identity")
    (root / "artifacts").mkdir(parents=True, exist_ok=True)
    (root / "grants").mkdir(exist_ok=True)
    source_id = str(uuid.uuid5(uuid.NAMESPACE_URL, project + ":knowledge-fixture:" + name))
    artifact = {
        "schemaVersion": "1.0.0",
        "classification": "curated-project-knowledge",
        "createdAt": (now - timedelta(seconds=1)).isoformat(),
        "title": "Synthetic validation-only " + name,
        "text": text,
    }
    raw = canonical(artifact)
    source_digest = hashlib.sha256(raw).hexdigest()
    artifact_path = f"artifacts/{name}.json"
    grant_path = f"grants/{name}.json"
    (root / artifact_path).write_bytes(raw)
    grant = {
        "schemaVersion": "1.0.0",
        "kind": "operator-reviewed-source-grant",
        "grantId": str(uuid.uuid4()),
        "projectId": project,
        "sourceId": source_id,
        "revision": revision,
        "sourceDigest": source_digest,
        "ownership": "synthetic-validation-corpus",
        "license": "validation-only",
        "authority": "explicit fixture author for isolated automated validation",
        "evidence": (
            "Permits storage/RAG of this synthetic fixture only, not any actual user/provider data."
        ),
        "reviewed": True,
        "status": "ACTIVE",
        "storageAllowed": True,
        "ragAllowed": True,
        "trainingAllowed": False,
        "distillationAllowed": False,
        "validFrom": (now - timedelta(seconds=60)).isoformat(),
        "validUntil": (now + timedelta(hours=1)).isoformat(),
        **(grant_updates or {}),
    }
    grant_raw = canonical(grant)
    (root / grant_path).write_bytes(grant_raw)
    entry = {
        "projectId": project,
        "sourceId": source_id,
        "revision": revision,
        "artifactPath": artifact_path,
        "sourceDigest": source_digest,
        "grantPath": grant_path,
        "grantDigest": hashlib.sha256(grant_raw).hexdigest(),
    }
    registry_path = root / "registry.json"
    registry = (
        json.loads(registry_path.read_bytes())
        if registry_path.exists()
        else {
            "schemaVersion": "1.0.0",
            "sources": [],
        }
    )
    registry["sources"] = [
        row
        for row in registry["sources"]
        if (row["projectId"], row["sourceId"]) != (project, source_id)
    ] + [entry]
    registry_path.write_bytes(canonical(registry))
    return {
        "entry": entry,
        "artifact": artifact,
        "grant": grant,
        "request": {
            "sourceKind": "curated",
            "sourceId": source_id,
            "revision": revision,
            "storageConsent": True,
            "idempotencyKey": str(uuid.uuid4()),
            "retentionSeconds": 600,
        },
    }


def mutate_grant(root: Path, entry: dict, updates: dict) -> dict:
    path = root / entry["grantPath"]
    grant = {**json.loads(path.read_bytes()), **updates}
    raw = canonical(grant)
    path.write_bytes(raw)
    registry = json.loads((root / "registry.json").read_bytes())
    for row in registry["sources"]:
        if (row["projectId"], row["sourceId"]) == (entry["projectId"], entry["sourceId"]):
            row["grantDigest"] = hashlib.sha256(raw).hexdigest()
    (root / "registry.json").write_bytes(canonical(registry))
    return grant
