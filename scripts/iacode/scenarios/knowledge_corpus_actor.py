"""Privileged validation-only actor, invoked in an exact host-verified owned API container.

This is not an endpoint or fallback. It deploys project-authored synthetic source grants and
deliberately mutates only that fresh proof namespace. It never reads user/provider content.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import uuid
from datetime import UTC, datetime
from pathlib import Path


def main() -> int:
    from iacode_api.config import Settings
    from iacode_knowledge.domain import canonical
    from sqlalchemy import create_engine, text
    from tests.knowledge_fixture import deploy_source, mutate_grant

    owner = os.environ.get("IACODE_KNOWLEDGE_PROOF_OWNER", "")
    if not re.fullmatch(r"iacode-knowledge-[0-9a-f]{12}", owner):
        raise ValueError("an exact isolated knowledge proof owner is required")
    project = str(uuid.UUID(sys.argv[1]))
    mode = sys.argv[2]
    settings = Settings()
    root = Path(settings.knowledge_source_root)
    if root != Path("/tmp/iacode-knowledge-corpus") or root.is_symlink():
        raise ValueError("only the owned proof container's exact temporary corpus root is allowed")
    corpus = json.loads(Path("/app/knowledge_tests/fixtures/retrieval-corpus.json").read_bytes())
    if corpus["classification"] != "synthetic-validation-only":
        raise ValueError("synthetic validation corpus required")
    documents = {row["name"]: row for row in corpus["documents"]}
    if mode == "seed":
        root.mkdir(parents=True, exist_ok=False)
        rows = {}
        for name, document in documents.items():
            fixture = deploy_source(
                root,
                project,
                datetime.now(UTC),
                name=name,
                revision=corpus["version"],
                text=document["text"],
            )
            rows[name] = {"entry": fixture["entry"], "request": fixture["request"]}
        result = {"corpusVersion": corpus["version"], "sources": rows}
    elif mode in {"revoke", "change", "remove", "supersede"}:
        name = sys.argv[3]
        if name not in documents:
            raise ValueError("an exact predefined corpus source is required")
        source = str(uuid.uuid5(uuid.NAMESPACE_URL, project + ":knowledge-fixture:" + name))
        registry = json.loads((root / "registry.json").read_bytes())
        matches = [
            row
            for row in registry["sources"]
            if (row["projectId"], row["sourceId"]) == (project, source)
        ]
        if len(matches) != 1:
            raise ValueError("exact owned current source is required")
        entry = matches[0]
        # Paths were created above, but still resolve and confine before any test mutation.
        artifact = (root / entry["artifactPath"]).resolve(strict=True)
        if not artifact.is_relative_to(root.resolve()) or artifact.is_symlink():
            raise ValueError("redirected validation artifact refused")
        if mode == "revoke":
            mutate_grant(root, entry, {"status": "REVOKED"})
            result = {"sourceId": source, "mode": mode}
        elif mode == "change":
            artifact.write_bytes(artifact.read_bytes() + b" ")
            result = {"sourceId": source, "mode": mode}
        elif mode == "remove":
            artifact.unlink()
            result = {"sourceId": source, "mode": mode}
        else:
            fixture = deploy_source(
                root,
                project,
                datetime.now(UTC),
                name=name,
                revision=corpus["version"] + "-v2",
                text=corpus["replacementText"],
            )
            result = {"entry": fixture["entry"], "request": fixture["request"]}
    elif mode in {"corrupt-body", "restore-body", "remove-index"}:
        document = str(uuid.UUID(sys.argv[3]))
        engine = create_engine(settings.database_url.replace("+asyncpg", "+psycopg", 1))
        backup = root / ("body-" + document + ".backup")
        try:
            with engine.begin() as connection:
                body = connection.execute(
                    text(
                        "SELECT body FROM knowledge_documents WHERE id=:id AND project_id=:project"
                    ),
                    {"id": document, "project": project},
                ).scalar_one()
                if not body or backup.is_symlink():
                    raise ValueError("an exact active owned validation document is required")
                if mode == "remove-index":
                    connection.execute(
                        text("DELETE FROM knowledge_index_entries WHERE document_id=:id"),
                        {"id": document},
                    )
                else:
                    if mode == "corrupt-body":
                        with backup.open("xb") as output:
                            output.write(canonical(body))
                        replacement = {**body, "title": "Deliberate owned corruption"}
                    else:
                        replacement = json.loads(backup.read_bytes())
                    connection.execute(
                        text(
                            "ALTER TABLE knowledge_documents DISABLE TRIGGER "
                            "knowledge_document_immutable"
                        )
                    )
                    connection.execute(
                        text(
                            "UPDATE knowledge_documents SET body=CAST(:body AS JSONB) "
                            "WHERE id=:id AND project_id=:project"
                        ),
                        {
                            "id": document,
                            "project": project,
                            "body": json.dumps(replacement, ensure_ascii=False),
                        },
                    )
                    connection.execute(
                        text(
                            "ALTER TABLE knowledge_documents ENABLE TRIGGER "
                            "knowledge_document_immutable"
                        )
                    )
            if mode == "restore-body":
                backup.unlink()
            result = {
                "documentId": document,
                "mode": mode,
                "observedBodyDigest": hashlib.sha256(canonical(body)).hexdigest(),
            }
        finally:
            engine.dispose()
    else:
        raise ValueError("unknown closed validation actor mode")
    print(json.dumps({"result": "APPLIED", **result}), flush=True)
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="strict")
    raise SystemExit(main())
