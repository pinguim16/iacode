# Decisions

## D1 — Audit the immutable published subject

The subject is `GATE-3-CP-0005` at
`3ef2bf77ddbddd378d35f5c4d32f2d90d42fc97d`. Every product assertion is judged at that tag or in
a transport clone of the authorised remote. This run changes no product, test, policy or historical
checkpoint and does not start Gate 4.

## D2 — Record session independence exactly

The active auditor is Codex desktop application, OpenAI, GPT-5, in a fresh session. No different
tool or provider is exposed in this task. The mechanism is therefore
`FRESH_SESSION_INDEPENDENT_AUDIT`, with `crossToolValidation=NOT_AVAILABLE`; it can grant
`MILESTONE_INDEPENDENT_AUDIT_PASS` and cannot grant `MILESTONE_EXTERNAL_PASS`.

## D3 — Treat the configured-model SUCCEEDED run as the positive cross-Gate proof

`LIVE-CODING-RUN.json` is the positive criterion evidence: the configured model reached terminal
`SUCCEEDED`, made ten calls through the Model Gateway, emitted seven canonical ToolRequests, received
seven authoritative Sandbox results, called the model again, required zero repair, left the host
sentinel unchanged and removed every sandbox container. Two repetitions of a broader diagnostic
prompt performed eleven valid tool cycles and then exhausted `maxTurns=12`. They are retained as
`M1-F-005` (LOW), not substituted for the successful proof and not hidden.

## D4 — Repair only audit instrumentation

The first 19-attack Red Team attempt defended every mutation but its audit reader searched for a
nonexistent top-level `nullControl` field. The canonical scenario records the control as the named
`control.agent_saw_the_sandbox_timeout` step. The failed report hash and cause are preserved in
`RED-TEAM-ATTEMPT-1.json`; only the audit-only reader changed, and the complete battery repeated.
The repeated battery passed 19 of 19 with a `VALID` control.

## D5 — Keep R-G3-001 as an accepted local architectural risk

All ten controls remain proved and the independent mutation against engine arguments was defended.
No ToolRequest, run identifier, workspace path or external API field becomes an arbitrary engine
operation. The controller still holds the local engine capability, so the disposition remains
`ACCEPTED_LOCAL_ARCHITECTURAL_RISK`, not “risk removed.”

## D6 — Separate the sealed checkpoint from post-seal derivations

The attestation is inside the checkpoint and all assurance gates execute after it is written. The
canonical milestone verdict and the final review ZIP are derived only after the audit checkpoint is
committed, tagged and published. The post-seal artifacts validate that transition without rewriting
the sealed checkpoint.
