# Experience Store

Gate 6 implements source-bound, consented observable engineering facts (ADR-0050/0051).
Its acceptance status is owned by [the current checkpoint](../../docs/checkpoints/LATEST.md), not
by this module's presence. Independent M2 audit remains pending; Gate 7 is not implemented here.

`iacode_experience` is an in-process provider-neutral domain library. It depends only on shared
contracts/common scanning and Pydantic. Source/store ports are supplied by the API's actual SQL,
runtime, quality and object adapters. There is no production in-memory fallback, provider client,
executor, transcript upload, retrieval engine or training pipeline.

Capture selects a completed task run, matching optional quality run, explicit storage consent and
stable request UUID. All document categories are closed and bounded. Unknown provider/model/effort,
Git repository/base identity, test case counts and reviews stay unknown; configuration and storage
consent are not observations of execution or human review. Only allowlisted facts, identities,
digests and counts are copied. Prompts, answers, event payloads, tool output and source files are not.

Existing `experiences` stores immutable current bodies; legacy rows remain quarantined. One atomic
transaction records capture and minimal audit fact. Project/request and project/source uniqueness
enforce replay without renewal. Reads verify content/schema/lineage, referenced source/evidence,
rights and time before delivery. Unknown reuse rights deny RAG, training and distillation.

The consumed [policy](../../.iacode/policies/experience-policy.json) sets finite primary retention,
capture age, tombstone lifetime, automatic bounded sweep and all payload/page limits. Expiration
denies access immediately; sweep/withdrawal physically remove primary bodies, not source records
or separate backups. Minimal tombstones prevent resurrection until the source is too old to capture.

See [the operational runbook](../../docs/runbooks/experience-store.md) for authenticated endpoints,
consent, deletion, backup/restore reconciliation and limits. Complete domain tests run through
`python scripts/iacode/gates/experience_tests.py`; actual PostgreSQL/migration/HTTP tests belong to
the counted API integration suite. Live provider/sandbox acceptance is a separate full-verifier stage.
