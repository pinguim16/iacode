# Retrospective — GATE 0 — FOUNDATION / GATE-0-CP-0001

Record observations, decisions and evidence. Never record private chain-of-thought, and never record
a secret. Every claim points at an artifact in this repository.

## What went well

**The delivery's own tests found the delivery's own defects.** Three of them, none found by review:
a configuration key nothing read, error responses missing the correlation identifier they told
callers to quote, and every HTTP metric labelled with the unmatched bucket. Each was written as a
test *of a property* rather than of an endpoint answering, which is what made them fail. Evidence:
`apps/api/tests/unit/test_configuration.py`, `test_errors_and_correlation.py`,
`test_observability.py`, and `docs/checkpoints/GATE-0-CP-0001/DECISIONS.md`.

**Executing the transition before needing it paid for itself.** `gate_transition_simulation.py`,
built in SETUP-00 to prove the next Gate could be handed over, failed on this Gate's very first
artifact — a real `GATE-0` specification colliding with the synthetic one it installs. That is the
control working: the collision surfaced in a disposable repository in seconds rather than at
handoff. Evidence: `scripts/development-ledger/promotion_fixture.py`.

**Attacking a control rather than describing it.** Twenty-eight adversarial scenarios, each
executing a real mutation and requiring the specific refusal it aimed at, over a null-mutation
control that had to be accepted first. The infrastructure attacks edit the real compose file and run
the real suite over it; the dependency attacks stop the real container. Evidence:
`docs/checkpoints/GATE-0-CP-0001/RED-TEAM-REPORT.md`.

**Verifying the claim the Gate actually makes.** The verification ends by deleting every volume and
rebuilding from nothing, because "a new machine can reproduce this" is the Gate's definition of
done. Evidence: `scripts/iacode/scenarios/fresh_install.py`.

## What failed

**Four control-plane controls refused this Gate for reasons that were correct under SETUP-00.** The
expected requirement set cited one Gate's checklist by literal, the delivery-assurance scope did not
cover the runtime, the `TESTS` denominator counted one suite, and the internal mirror audit asserted
that no Gate 0 runtime existed. Root cause: each encoded the current Gate's content instead of
deriving it. Recorded as `LSN-0032`; the replacements derive from registries.

**The repository secret scan walked every file on disk, including ignored ones.** Gate 0's own
bootstrap creates `infra/compose/.env` with real local credentials, so the control refused the
repository for containing exactly the file the runbook tells an operator to create. Narrowed to what
Git carries, with both paths executed: `SecretScanScopeTests`.

**Two fixtures copied a policy without the content it names.** The Green Keeper fixture and the
promotion fixture inherit `.iacode/policies/` and almost no content, so four new mandatory gates
whose commands live outside `scripts/development-ledger` made every fixture fail for its own
reasons. Repaired by `promotion_fixture.restrict_policies_to_available_content`.

**A parameter that documented an effect it did not have.** `compose(merge_stderr=...)` was added with
its docstring in one edit and its implementation in another; only the first landed. Found while
writing the backup verification. Same class as `LSN-0028`.

**A configuration key with no reader, and a test file that looked like a credential.** Both recorded
below.

**The Green Keeper aborted while reading the output of a gate that was green.** `UnicodeDecodeError:
'charmap' codec can't decode byte 0x9d`. Every capture in the repository inherited its decoder from
the machine -- `cp1252` here -- while every tool writes UTF-8, so the reader worked until a gate's
output happened to contain a character the codepage has no mapping for. Eleven call sites now state
`encoding="utf-8"` with `errors="replace"`, and `GRD-0037` parses the tree so the next one cannot
omit it. Recorded as `LSN-0035`.

**Then the repaired reader broke the writer.** The recorder captured an eighteen-minute verification
correctly and died printing it: `sys.stdout` encodes with the codepage too, and the replacement
character the tolerant read had just produced is exactly what `cp1252` cannot encode. The first fix
addressed one direction of a two-directional defect, which is why `GRD-0037` now also requires every
entry point that re-emits captured output to configure its own stream.

## What repeated

**`LSN-0028` — a configuration key that no code reads is a defect.** It recurred twice in this Gate:
`IACODE_TEMPORAL_TASK_QUEUE` declared in the API's settings and read by nothing, and the
`merge_stderr` parameter above. The lesson was `GUARDED` when both happened, so this is a
`GUARDRAIL_FAILURE` and is recorded as one rather than repaired quietly.

**Investigating the control rather than the defect**, which is what the contract asks for: `GRD-0028`
is a closed schema over `.iacode/memory/POLICY.json`. It guards one document, and the lesson's title
states a general rule. The guardrail could not have reached either recurrence. The control was
generalised — `GRD-0033` now checks the application's declared settings against the source that must
read them — and the failure is resolved in this checkpoint. Severity escalated `MEDIUM` → `HIGH`.

The residual limit is recorded on the lesson: the new check reads a declaring module against its own
package, and a key read by a *different* process is exempted by name rather than derived.

## What was learned

- A control that names the current Gate's content by literal is not a control for the next Gate. It
  is a blocker or a blind spot, and which one is luck. (`LSN-0032`)
- A value bound in middleware is absent in the handlers that run outside it, and the absence is
  silent because an empty identifier reads as "not generated yet". (`LSN-0033`)
- Re-deriving what the framework already computed diverges from the framework the moment the
  framework changes shape, and the divergence is invisible while the endpoint keeps answering.
  (`LSN-0034`)
- A scan over the working tree and a scan over the repository are different controls. The policy is
  about what reaches the ledger, so the second is the one that matches it — and the first refuses
  correct states.
- A test fixture that looks like a credential is indistinguishable from a leak to a text scanner.
  Assembling it at runtime keeps both the fixture and the scanner honest.
- A mandatory gate that needs nine healthy containers is a gate that gets skipped. The split between
  a unit gate and an integration stage is what keeps the mandatory set runnable.
- A defect in the instrument that reads a result is indistinguishable, from the outside, from a
  defect in what is being measured -- and it is intermittent, because it depends on which character
  the measured process happened to print. (`LSN-0035`)
- Repairing one direction of a symmetric defect leaves the other half live, and the half that is
  left runs later: the reader fails before the work, the writer fails after it. A control written
  for the direction that was observed is half a control. (`LSN-0035`)

## What should become a guardrail

Everything below has one. Nothing is left here as prose.

| Item | Control | Kind | Where | Removing it would allow |
|---|---|---|---|---|
| The application declares only configuration it reads | `GRD-0033` | test | `test_every_declared_key_is_read_somewhere` | a key promising behaviour nothing implements |
| Scope is judged against a registry, not a literal | `GRD-0034` | policy | `.iacode/policies/gate-scope.json` | a later Gate's capability implemented early, unnoticed |
| An error outside the middleware still carries its correlation | `GRD-0035` | test | `test_internal_error_still_carries_a_correlation_identifier` | a failure telling a caller to quote an identifier it does not contain |
| Metrics are labelled by the route the router matched | `GRD-0036` | test | `test_metrics_label_routes_by_template_not_by_url` | one time series for everything, while the dashboard renders |
| Every subprocess capture, and every tool that re-emits one, states its codec | `GRD-0037` | test | `test_no_capture_relies_on_the_platform_codepage`, `test_every_tool_that_re_emits_captured_output_configures_its_own_stream` | a tool aborting with a Unicode error on output it was only meant to pass along |

## New lessons

| Lesson | Status | Guarded by |
|---|---|---|
| `LSN-0032` — a control written while one Gate was the only Gate stops being a control when the next one starts | `GUARDED` | `GRD-0034` |
| `LSN-0033` — a value bound in middleware is absent in the handlers that run outside it | `GUARDED` | `GRD-0035` |
| `LSN-0034` — re-deriving what the framework already computed diverges from the framework | `GUARDED` | `GRD-0036` |
| `LSN-0035` — captured subprocess output decoded or re-emitted with the platform codepage crashes the tool, not the work | `GUARDED` | `GRD-0037` |

## Updated lessons

| Lesson | Change | Reason |
|---|---|---|
| `LSN-0028` | recurrence recorded, severity `MEDIUM` → `HIGH`, `GRD-0033` added, resolved in `GATE-0-CP-0001` | the class recurred twice against a guardrail scoped to one document |

## Retired lessons

| Lesson | Superseded by | Reason |
|---|---|---|
| _none_ | | Every lesson from `M0` still applies; this Gate exercised them rather than outgrowing them. |
