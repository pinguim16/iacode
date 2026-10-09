# Quality Engine operations

The Gate 4 Quality Engine turns one immutable workspace snapshot into a frozen plan, executes every
applicable check through the Gate 3 sandbox, stores content-addressed evidence, and derives a
fail-closed verdict. The API and evaluator never run project commands. Only the sandbox service has
access to the container engine; the evaluator has no host project mount, engine socket, or provider
credential.

## Lifecycle

Create a run with `POST /api/v1/quality-runs`, supplying only `snapshotId`, `snapshotDigest`, the
canonical `policyId`, an optional bounded project configuration, owner run, and idempotency key.
The response names the frozen plan and applicable checks. Inspect the run at
`GET /api/v1/quality-runs/{runId}` and its cursor-paginated history at
`GET /api/v1/quality-runs/{runId}/events`. The `/events/stream` endpoint drains all recorded events
before closing after a terminal state.

States advance through `CREATED`, `PLANNED`, `QUEUED`, and `RUNNING` to `SUCCEEDED`, `FAILED`,
`TIMED_OUT`, `CANCELLED`, or `INVALID`. A `PASS` verdict is possible only when the complete
applicable mandatory set has successful results and every required evidence object resolves with
its recorded digest. Missing, stale, denied, timed-out, cancelled, malformed, or unresolved input
fails closed.

## Policy and runners

`.iacode/policies/quality-policy.json` is the canonical closed policy. It owns profiles, runner
names, mandatory checks, limits, evidence requirements, and verdict rules. Project configuration
may select declared optional checks or lower limits; it cannot remove mandatory checks, raise a
limit, choose an image, author a command, or submit a result or verdict. Runner identifiers map to
fixed argument vectors in `services/evaluator/src/iacode_evaluator/runners.py`.

## Cancellation, deadlines, and recovery

Cancel with `POST /api/v1/quality-runs/{runId}/cancel`. Cancellation is idempotent. A running
sandbox activity is cancelled, its cleanup is awaited, a cancellation result and evidence are
recorded, and only then does the run become `CANCELLED`. Late callbacks are refused.

Temporal owns workflow durability. Restarting `iacode-evaluator` recreates workflow state from
history; the database idempotency keys prevent duplicate results, events, or verdicts. Per-check and
whole-run deadlines come from the frozen policy. A deadline still produces a terminal result,
evidence, verdict, and state transition.

## Evidence and reproduction

Complete redacted check output is stored in MinIO as immutable, content-addressed evidence. The
database stores bounded summaries and metadata. Evidence is re-downloaded and re-hashed before it
can support a verdict. Reproduce a terminal run with
`POST /api/v1/quality-runs/{runId}/reproductions`; the new run keeps a distinct identity while using
the same frozen plan, snapshot, policy digest, runners, images, commands, and limits. The original
run is never rewritten.

## Health and metrics

`python -m iacode_evaluator.healthcheck` proves all four dependencies: a quality Temporal poller, a
sandbox poller, PostgreSQL, and the artifact bucket. The container health check runs the same
probe. Prometheus scrapes `evaluator:9103/metrics`. Useful metric families start with
`quality_runs_`, `quality_checks_`, `quality_findings_`, `quality_evidence_`, and
`quality_verdicts_`; all labels use closed, low-cardinality vocabularies.

## Troubleshooting

- A run stuck before `RUNNING`: inspect API and evaluator logs for the run correlation and verify a
  poller on `iacode-quality`.
- A check not starting: run the evaluator health check and verify the sandbox service is healthy;
  never execute the command on the host as a workaround.
- `FAILED` with missing evidence: verify MinIO availability and object integrity. Do not edit the
  database row or replace the object; start a reproduction after restoring the dependency.
- `INVALID`: inspect event history first. It records the reason before the terminal state becomes
  visible.
- A worker restart: wait for the evaluator to become healthy and reread the same run. Do not create
  a replacement run unless an operator intentionally requests reproduction.
- Suspected secret in output: evidence persistence redacts and scans before storage. Keep the
  quarantined artifact unavailable and rotate the affected credential outside IACode.

Routine recovery is `docker compose ... up -d evaluator sandbox`, followed by the evaluator health
check and an event-history read. Destructive database or object-store repair is not part of this
runbook.
