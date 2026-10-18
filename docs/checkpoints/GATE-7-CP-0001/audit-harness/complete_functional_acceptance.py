"""Bind the exact canonical runtime set to one completed immutable full execution.

This assembler performs no tests and grants no independent verdict. The original complete
producer and actual process record must already exist and pass; historical local proofs cannot
supply a missing current premise.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))
sys.path.insert(0, str(ROOT / "scripts/iacode"))

GROUPS = {
    "ADMISSION": {
        "requirements": "2.1 2.2 2.3 2.4 2.5 2.6 2.7 2.8",
        "feature": "Closed content-bound source admission, rights and privacy",
        "expected": (
            "Actual operator-curated grants admit only exact project/source/revision bytes. "
            "Closed ingress, canonical scanning and real filesystem/SQL adversaries refuse unsafe "
            "effects; the owning validated storage-only experience remains ineligible for RAG."
        ),
        "steps": [
            "actual-content-bound-synthetic-source-grants-deployed",
            "owning-validated-storage-only-experience-cannot-be-laundered",
            "consent-missing-refused-before-effects",
            "consent-denied-refused-before-effects",
            "consent-coerced-refused-before-effects",
            "caller-text-refused-before-effects",
            "caller-path-refused-before-effects",
            "caller-rights-refused-before-effects",
            "caller-verdict-refused-before-effects",
            "secret-refused-before-effects",
            "actual-capability-refused-before-effects",
            "cross-project-ingestion-refused",
            "upstream-experience-and-rights-remain-unchanged",
        ],
    },
    "DERIVATION": {
        "requirements": "3.1 3.2 3.3",
        "feature": "Closed finite contracts and deterministic exact-span derivation",
        "expected": (
            "The complete owning domain/schema and API suites execute strict JSON, Unicode/CRLF, "
            "all consumed policy bounds, exact source spans and fingerprints. Real publications "
            "and export/citation round-trips preserve source bytes without synthesis."
        ),
        "steps": [
            "actual-corpus-publication-unicode",
            "actual-export-inspect-roundtrip",
            "measured-exact-retrieval-and-citations-4",
        ],
    },
    "INDEX": {
        "requirements": "3.4 3.5 3.6",
        "feature": "Persistent bounded inverted matching and deterministic relevance",
        "expected": (
            "Actual PostgreSQL GIN/parameterized lexical matching ranks a varied predefined corpus "
            "with exact citations, including genuine no-match results. Complete domain/SQL tests "
            "refuse capacity and policy/index drift; corrupt projections never become "
            "empty success."
        ),
        "steps": [
            *[f"measured-exact-retrieval-and-citations-{index}" for index in range(10)],
            "actual-persistent-source-index-after-restart",
            "actual-corrupt-body-is-not-empty-success",
            "actual-missing-index-is-not-empty-success",
            "missing-current-source-is-unavailable-not-empty-success",
        ],
    },
    "PERSISTENCE": {
        "requirements": "4.1 4.2 4.3 4.4 4.5",
        "feature": "Real migration, atomic publication, retries and recovery",
        "expected": (
            "Complete actual PostgreSQL/migration tests prove reversible parity, inherited-data "
            "preservation, atomic audit rollback, concurrency, immutable facts and "
            "retention ceilings. "
            "Real lost-response retry, restart, corruption/refusal and valid rebuild "
            "recover truthfully."
        ),
        "steps": [
            "actual-accepted-response-loss-one-publication",
            "stable-exact-request-recovers-original-publication",
            "owned-api-restart",
            "actual-persistent-source-index-after-restart",
            "actual-corrupt-body-is-not-empty-success",
            "actual-body-restoration-null-control",
            "actual-missing-index-is-not-empty-success",
            "actual-rebuild-publishes-current-revision",
            "rebuilt-retrieval-selects-new-citation",
        ],
    },
    "ACCESS": {
        "requirements": "5.1 5.2 5.3 5.4 5.5 5.6",
        "feature": "Authenticated project-bound cited untrusted evidence",
        "expected": (
            "Actual finite signed HTTP refuses missing/invalid/stale/replayed auth and "
            "cross-project "
            "access/cursors. All predefined relevant/irrelevant queries resolve exact "
            "ranked source "
            "citations. Logs remain useful without ingress; knowledge cannot execute or modify "
            "upstream task, tool, quality, experience or reuse authority."
        ),
        "steps": [
            "unauthenticated-ingestions-refused",
            "unauthenticated-search-refused",
            "unauthenticated-documents-refused",
            "invalid-authentication-refused",
            "stale-authentication-refused",
            "authentication-replay-clean-control",
            "actual-redis-authentication-replay-refused",
            "cross-project-cursor-refused",
            "cross-project-document-get-refused",
            "cross-project-document-delete-refused",
            "actual-bounded-project-pagination",
            "actual-export-inspect-roundtrip",
            "actual-logs-retain-observability-not-private-ingress",
            "knowledge-never-executes-or-mutates-upstream-evidence",
            *[f"measured-exact-retrieval-and-citations-{index}" for index in range(10)],
        ],
    },
    "INVALIDATION": {
        "requirements": "6.1 6.2 6.3 6.4 6.5",
        "feature": "Immediate invalidation, nonrenewing retention and bounded physical purge",
        "expected": (
            "Real grant/source/revision changes, expiry and scoped withdrawal deny old citations "
            "immediately. Actual rebuild supplies only current citations; same/new request keys "
            "cannot resurrect withdrawal. The owned automatic sweeper physically purges primary "
            "content/index. Complete SQL/lifecycle tests cover finite GC, failures and shutdown; "
            "the runbook explicitly limits backup/restore claims."
        ),
        "steps": [
            "revoked-grant-immediately-denies-delivery",
            "superseded-source-immediately-denies-old-citation",
            "actual-rebuild-publishes-current-revision",
            "rebuilt-retrieval-selects-new-citation",
            "actual-withdrawal",
            "same-key-cannot-resurrect-withdrawn-revision",
            "new-key-cannot-resurrect-withdrawn-revision",
            "actual-finite-retention-created",
            "expiry-denial-does-not-require-manual-sweep",
            "owned-background-retention-physically-purges-primary-index",
            "changed-raw-source-immediately-denies-delivery",
            "missing-current-source-is-unavailable-not-empty-success",
            "upstream-experience-and-rights-remain-unchanged",
        ],
    },
    "FULL-LIVE": {
        "requirements": "7.1 7.2 7.3 7.4 7.5",
        "feature": "One full immutable execution, actual integration and preserved producer bytes",
        "expected": (
            "One non-fast public detached-subject invocation runs every inherited/new mandatory "
            "stage. Fresh real provider/sandbox/quality/experience/knowledge integration and all "
            "functional/adverse observations pass, exact safe original producers survive consumer "
            "and cleanup boundaries, owned resources/clone are removed and unrelated identities "
            "and measured source inputs remain unchanged."
        ),
        "steps": [
            "real-provider-and-sandbox-completed",
            "actual-derived-quality-pass-with-evidence",
            "actual-source-bound-experience-captured",
            "owning-validated-storage-only-experience-cannot-be-laundered",
            "actual-export-inspect-roundtrip",
            "owned-background-retention-physically-purges-primary-index",
            "owned-resources-actually-removed",
            "unrelated-container-identities-and-running-states-preserved",
            "measured-source-inputs-unchanged",
        ],
    },
}


def current_execution():
    from ledger_common import LedgerError, load_json, scope_fingerprint
    from verify import build_stages

    verification = load_json(CHECKPOINT / "VERIFY.json")
    publication = load_json(CHECKPOINT / "PUBLISHED-CLEAN-CLONE-REPORT.json")
    functional = load_json(CHECKPOINT / "FUNCTIONAL-SCENARIOS.json")
    expected = [stage.name for stage in build_stages(False)]
    subject = publication["publishedCommit"]
    knowledge = functional["scenarios"]["knowledge-engine-e2e.json"]
    rows = knowledge.get("steps", [])
    if (
        verification.get("result") != "PASS"
        or verification.get("fast") is not False
        or [row["name"] for row in verification["stages"]] != expected
        or any(row["result"] != "PASS" for row in verification["stages"])
        or publication.get("result") != "PASS"
        or publication.get("invocationCount") != 1
        or publication.get("retryCount") != 0
        or publication.get("exitCode") != 0
        or functional.get("subjectCommit") != subject
        or knowledge.get("subjectCommit") != subject
        or knowledge.get("sourceDirty") is not False
        or knowledge.get("sourceFingerprint") != scope_fingerprint(ROOT)
        or knowledge.get("result") != "PASS"
        or not rows
        or any(row.get("result") != "PASS" for row in rows)
        or len({row["name"] for row in rows}) != len(rows)
        or knowledge.get("cleanup")
        != {"composeExitCode": 0, "container": 0, "volume": 0, "network": 0}
        or knowledge.get("sandboxCleanup") != {"container": 0, "network": 0}
    ):
        raise LedgerError("one whole unchanged immutable runtime execution must actually pass")
    corpus_path = ROOT / "services/knowledge/tests/fixtures/retrieval-corpus.json"
    corpus = load_json(corpus_path)
    measures = knowledge.get("retrievalMeasurements", [])
    if len(measures) != len(corpus["queries"]):
        raise LedgerError("the predefined corpus query denominator differs")
    for index, (measurement, query) in enumerate(zip(measures, corpus["queries"], strict=True)):
        if (
            measurement.get("queryOrdinal") != index
            or measurement.get("result") != "PASS"
            or measurement.get("expectedSources") != query["expectedSources"]
            or measurement.get("observedHits") != len(query["expectedSources"])
        ):
            raise LedgerError("an actual predefined retrieval observation did not pass")
    step_map = {row["name"]: row for row in rows}
    source_step = step_map["actual-content-bound-synthetic-source-grants-deployed"]
    if (
        source_step.get("corpusVersion") != corpus["version"]
        or source_step.get("corpusSha256") != hashlib.sha256(corpus_path.read_bytes()).hexdigest()
    ):
        raise LedgerError("the measured versioned corpus is not the current exact corpus")
    records = [
        json.loads(line)
        for line in (CHECKPOINT / "COMMANDS.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    executions = [
        row
        for row in records
        if row.get("exitCode") == 0
        and row.get("subjectCommit") == subject
        and "audit-harness/run_full_verification.py" in row.get("command", "")
    ]
    if len(executions) != 1:
        raise LedgerError("exactly one completed recorded current full invocation must resolve")
    manifest_path = CHECKPOINT / load_json(CHECKPOINT / "PRODUCER-REPORTS.json")["manifest"]
    manifest = load_json(manifest_path)
    originals = [
        row for row in manifest["reports"] if row["producerName"] == "knowledge-engine-e2e.json"
    ]
    if manifest.get("refusedReports") or len(originals) != 1:
        raise LedgerError("exact safe original knowledge producer is required")
    original = originals[0]
    raw_path = manifest_path.parent / original["archive"]
    raw = raw_path.read_bytes()
    if (
        len(raw) != original["bytes"]
        or hashlib.sha256(raw).hexdigest() != original["sha256"]
        or json.loads(raw) != knowledge
    ):
        raise LedgerError("the projected observation differs from its exact original bytes")
    return verification, publication, knowledge, executions[0], step_map


def main() -> int:
    from ledger_common import use_utf8_stdout

    use_utf8_stdout()
    from check_functional_acceptance import functional_requirement_ids
    from ledger_common import LedgerError, load_json, utc_now, write_json

    if load_json(CHECKPOINT / "STATE.json")["status"] != "IN_PROGRESS":
        raise LedgerError("never rewrite a terminal or sealed functional delivery")
    destination = CHECKPOINT / "FUNCTIONAL-ACCEPTANCE.json"
    if destination.exists():
        raise LedgerError("preserve an existing functional assembly before another attempt")
    _, publication, knowledge, execution, steps = current_execution()
    required = set(functional_requirement_ids(ROOT, "GATE-7"))
    mapped = {"GATE-7-" + key for group in GROUPS.values() for key in group["requirements"].split()}
    if mapped != required:
        raise LedgerError("authored functional mapping differs from canonical membership")
    now, rows = utc_now(), []
    for identifier, group in GROUPS.items():
        if any(steps.get(name, {}).get("result") != "PASS" for name in group["steps"]):
            raise LedgerError("a current actual functional premise did not pass: " + identifier)
        rows.append(
            {
                "scenarioId": "G7-FA-" + identifier,
                "requirementIds": ["GATE-7-" + key for key in group["requirements"].split()],
                "feature": group["feature"],
                "scenario": group["expected"],
                "environment": (
                    "Fresh owned real Docker Compose PostgreSQL/Redis/object/API/provider/"
                    "sandbox/quality "
                    f"stack {knowledge['composeProject']}; authenticated HTTP, public detached Git "
                    "subject under the Windows full verifier."
                ),
                "preconditions": [
                    "Exact published detached subject " + publication["publishedCommit"],
                    "Complete unchanged domain, API, PostgreSQL/migration, native/client and "
                    "runtime stages.",
                    "Isolated synthetic test grants do not license actual user/provider content.",
                ],
                "execution": [
                    execution["command"],
                    "Owning complete domain/schema, API unit and actual "
                    "PostgreSQL/migration suites "
                    "in this invocation; live observations supplement rather than replace them.",
                ],
                "expected": [group["expected"]],
                "observed": [name + ": PASS" for name in group["steps"]],
                "result": "PASS",
                "evidence": [
                    execution["id"],
                    "checkpoint:VERIFY.json",
                    "checkpoint:FUNCTIONAL-SCENARIOS.json",
                    "checkpoint:PUBLISHED-CLEAN-CLONE-REPORT.json",
                    "checkpoint:PRODUCER-REPORTS.json",
                    "file:apps/api/tests/integration/test_knowledge_engine.py",
                    "file:apps/api/tests/unit/test_knowledge_api.py",
                    "file:services/knowledge/tests/test_domain.py",
                ],
                "timestamp": now,
                "artifactReferences": [
                    "file:services/knowledge/tests/fixtures/retrieval-corpus.json",
                    "file:scripts/iacode/scenarios/knowledge_engine_e2e.py",
                    "file:docs/runbooks/KNOWLEDGE-ENGINE.md",
                ],
            }
        )
    write_json(
        destination,
        {
            "schemaVersion": "1.0.0",
            "gate": "GATE-7",
            "checkpoint": CHECKPOINT.name,
            "status": "PASS",
            "generatedAt": now,
            "scenarios": rows,
        },
    )
    print(f"FUNCTIONAL_ASSEMBLY=PASS scenarios={len(rows)} requirements={len(required)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
