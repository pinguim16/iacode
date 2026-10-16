# Retrospective — GATE 4 / GATE-4-CP-0010

## What went well

A behavioral workflow test reproduced a cancellation defect before production correction. The
null/positive path, unrelated failure and both persistence arrival orders were tested; actual
PostgreSQL concurrency and live sandbox cleanup passed. Evidence: CP0010 commands and cancellation
reports. Sealed CP0009 remained immutable and owner authorization was recorded explicitly.

## What failed

Cmd-0005 confirmed a durable cancellation race. Cmd-0009 caught a noncanonical new verdict fixture.
Cmd-0014 caught overlong new regression source lines. All red attempts remain in the ledger.
Cmd-0022 and cmd-0029 caught metadata drift and an evidence/policy producer still changing content
after the inventory boundary. The unsealed-only synchronizer and a quiescent validation sequence
passed as cmd-0024 and cmd-0034; no terminal evidence was relaxed or rewritten.
Cmd-0007/0008 launched no process because the command recorder refused unreplayable filename tokens;
the intended suites subsequently ran with replayable globs.

The complete published v1 verifier remained FAIL (40/42). Its real self-evaluation exposed a typed
polling-cleanup failure; its root output also exposed historical policy reinterpretation. Published
v2 remained FAIL (41/42; 801 root cases and ten failures). Both five-report attempts are retained
byte-for-byte. A same-session all-anchor component probe reproduced nine collection incompatibilities;
an unchanged published-v2 Foundation test reproduced the UTF-8 stream configuration class.
Targeted corrected controls are green, but a new complete immutable subject is still required.

Measured transport metadata work was initially 100368 examined characters for a 1002-character
input. Incremental carrier accounting alone stayed red; JSONDecodeError coordinate construction
still rescanned prefixes. Lazy metadata indexing passed the identical cost bound and exact builtin
coordinate/message tests. Separately, a 25-line verifier tail lost earlier failed-case identifiers;
real child-process controls now prove bounded identifier retention without parameters or messages.

## What repeated

LSN-0098/GRD-0099 recurred beyond the old flag/watcher boundary. It was reopened and escalated as a
GUARDRAIL_FAILURE, not repaired silently. The new persistence barrier and complete workflow tests
close the gap; actual SQL and live cleanup proof are recorded as cmd-0016.
LSN-0011/GRD-0006 also recurred during in-progress metadata preparation and was explicitly reopened.
Its correction derives aggregates and commit semantics together, requires evidence producers to
finish first and retains the validator's strict hash and preflight freshness checks.

A further LSN-0011 recurrence occurred in the wrapper, not the synchronizer: the initially clean
wrapper cached STATE, synchronized correctly, then restored its stale aggregates. Cmd-0210 measured
1 instead of derived 7 at the pre-hash boundary. Removing that redundant write passed all five
metadata controls in cmd-0214. No validator success was simulated; actual quiescent validation and
the complete newly published subject are still required.

LSN-0012 and LSN-0113 recurred when collection-bound counting was introduced without versioning
the subject policy. They are escalated, not treated as already covered by the earlier two-subject
internal-verdict probe. ADR-0043 preserves sealed 1.0.0 source enumeration and makes live 1.1.0
collection semantics mandatory. Actual validation of every canonical tag is required.

LSN-0035 and LSN-0083 recurred because checkpoint capture harnesses omitted their own UTF-8 output
configuration. The existing AST guard remained unchanged. Cmd-0197 reproduced six offenders in the
immutable v2 subject; cmd-0198 passed every current Foundation control after canonical stream setup.

## What was learned

Cmd-0255 repeated producer overlap when the inventory launcher returned a running session ID.
Six strict hash refusals were preserved and LSN-0011 was reopened/escalated to recurrence 13.
Cmd-0259 passed actual main-tree validation with producers strictly serialized. Never interpret a
session ID as completion, and never edit validation inputs while a dependent producer is active.

The local broad run crossed source/registry epochs and correctly finished red with five missing
loaded-method errors (cmd-0229). Fresh provenance passed; later memory selections correctly refused
the still-stale derived index (cmd-0238/0239). Render derived artifacts before testing and freeze all
source/memory during authoritative verification. No partial green run replaces a failed full one.

LSN-0020 recurred because both process owners hashed inputs after children could rewrite them.
Actual rewriting/stable controls reproduced and corrected both owners (cmd-0230/0235/0236).
ADR-0044 records the launch boundary; cmd-0200 is qualified, not rewritten or reconstructed.

Durable reads need write-boundary invariants. Cancellation and immutable verdict commitment require
a single serialization point. Internal closure and independent milestone approval are distinct
claims, and live contracts must express one unambiguous cadence.

## What should become a guardrail

Workflow completion/result/verdict cancellation races and unrelated-error propagation are executable
regressions in GRD-0099. Canonical fixture positive paths, honest internal verdicts and unchanged
mandatory lint are registered in GRD-0104 through GRD-0106. None substitutes for independent audit.

## New lessons

LSN-0103 records canonical fixture digests; LSN-0104 records cadence consistency and truthful
independence; LSN-0105 records source-quality coverage for new tests. Their machine records own
status, evidence and provenance rather than duplicated retrospective counts.

LSN-0106 through LSN-0113 cover actual output boundaries, fixture premises, metadata timestamps,
runner-bound counts, lost timeout diagnostics, polling lifecycle, shared transport interpretation and
subject-policy semantics. LSN-0114 and LSN-0115 add measured metadata cost and durable failure
identifiers. The machine records and executed controls own their current statuses and evidence.

## Updated lessons

LSN-0098 retains its earlier resolved recurrence and records the new recurrence and corrective proof.
LSN-0011 retains all earlier failures and adds the quiescent metadata synchronization proof.

## Retired lessons

None.
