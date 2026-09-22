# Retrospective — GATE 1 — Model Gateway / GATE-1-CP-0001

Record observations, decisions and evidence. Never record private chain-of-thought, and never record
a secret. Every claim points at an artifact in this repository.

## What went well

**The checklist was parsed, not transcribed.** `docs/GATE-1-CHECKLIST.md` is the canonical
requirement source, and `.iacode/policies/canonical-requirements.json` was generated from it with
`policies.parse_checklist` rather than typed alongside it. The mirror is exact by construction — 122
rows, all mandatory — and `tests/test_gate1_model_gateway.py::Gate1CanonicalSpecificationTests`
fails if they ever diverge. A hand-copied mirror is a second source of truth that agrees until it
does not.

**Ports declared inward.** The gateway names the storage it needs (`CatalogStore`, `ModelCallStore`,
`Clock`, `Jitter`) and the application implements it. Injecting `Clock` and `Jitter` is what made
the retry and circuit-breaker suites deterministic and instant: the circuit breaker's threshold,
open state, cooldown, half-open probe, recovery and reopening are all covered without a single real
wait. `ADR-0016` records the decision.

**Adapters that perform no I/O.** Three protocol adapters — OpenAI Chat Completions, OpenAI
Responses, Anthropic Messages — translate and nothing else; one `HttpModelProvider` opens sockets.
`test_provider_contract.py` runs the same nine scenarios against all three with
`httpx.MockTransport`. Adding a fourth adapter is translation plus a row in that suite.

**Failure modes proved with fixtures, not against the provider.** Rate limiting, invalid
credentials, provider unavailability, timeouts and cancellation are all exercised deterministically.
The live provider was touched three times per smoke run — catalog, one inference, one stream — with
a 32-token cap. `test_live_smoke_is_bounded_and_minimal` keeps it that way.

**A static boundary scan with a negative control.** `GatewayBoundaryTests` fails if a gateway module
imports `iacode_api` or names a provider in a provider-neutral module, and it carries a case the
rule must reject, so a scan that has stopped scanning is itself detected. The same pattern was used
for the image-build and Gate-literal rules added by this Gate.

**The live blocker was reported as a blocker.** Without a credential, the smoke check exits `2` and
names the variable that is missing. The Gate stopped there and said so, rather than claiming a live
integration it had not run.

## What failed

**A mandatory gate was measuring a stale image (`G1-F-001`, HIGH).** `apiTests` runs pytest inside
the API image and nothing rebuilt it. A red test —
`test_a_documented_placeholder_is_not_redacted` — had been failing at HEAD and the gate had
reported PASS throughout GATE 0. Root cause: the gate measured whatever was baked into the last
build. Fixed with `compose.build_service`, called by every image-executing gate, and guarded by
`GRD-0038`. Recorded as `LSN-0036`.

**A shared control was bound to a Gate literal (`G1-F-002`, MEDIUM).**
`test_no_future_gate_capability_is_implemented` called `scope_violations(root, "GATE-0")` and so
refused the directory GATE 1 was authorized to fill. Fixed with `ledger_common.delivered_gate` and
`policies.reservations_in_force`; guarded by `GRD-0039`. Recorded as `LSN-0037`.

**One concept defined twice in one module (`G1-F-003`, MEDIUM).** The redactor stated what a
placeholder looks like in two places that disagreed about the repository's own documented
placeholder, so `redact_text` hid the example file's placeholders while `redact_value` did not. The
duplicate lookahead was removed and the text redactor now consults the single anchored definition.
Guarded by `GRD-0040`. Recorded as `LSN-0038`. It was found only because `G1-F-001` was fixed first.

**Integration fixtures were left in the operational database (`G1-F-004`, HIGH).** The first live
synchronisation returned 36 models and the catalog reported 56; twenty rows were fixtures from the
store tests, visible in the API and rendered by the web page. Cleanup was added per test and a
standing invariant now asserts the catalog holds no provider the policy does not declare. Guarded by
`GRD-0041`. Recorded as `LSN-0039`.

**A sealed predecessor did not validate from its own tag (`G1-F-007`, HIGH).** `MIR-016`
validates every anchored checkpoint from a detached checkout, and `GATE-0-CP-0001` entered the
anchor chain only when this Gate built it, because a checkpoint cannot anchor its own tag. Checked
there for the first time, it failed: six of its recorded commands declare `var/verify-report.json`
as an input, `var/` is ignored by Git, and no checkout carries it. The recorder now refuses to
declare an ignored path as an input, and the validator accepts an absent ignored input only when
the record binds its content by digest — every path the repository does carry is still required to
resolve. Sealed history was not rewritten. Guarded by `GRD-0042`. Recorded as `LSN-0040`.

**The repository secret scan flagged our own protection.** An assignment to a name ending in
`SECRET`, a test fixture containing a plausible key shape, and the literal authorization header name
in a comment were each read as leaks. Resolved by naming the resolved value `credential` throughout
and by building fixture values rather than writing them. No control was weakened; the source was
changed to stop looking like the thing the scanner exists to find.

**The redactors disagreed about a second value, and the new control found it immediately.**
`GRD-0040` was written to assert that both redaction paths classify every value in the committed
example file identically. Its first run failed on `IACODE_GATEWAY_MAX_OUTPUT_TOKENS`:
`redact_value` hid it because the key name contains `TOKENS`, while `redact_text` did not. An
operational limit was being redacted out of the configuration dump, which is the over-redaction
failure the Gate 0 tests already warn about — redaction markers that outnumber the information
teach operators to switch redaction off. The sensitive-key rule now reads `token` but not
`tokens`, the same judgement `infra/tests/test_compose_definition.py` already made about the same
names. A guardrail that finds a second instance of its own failure class on its first execution is
the argument for writing the control rather than the note.

**A red-team attack escaped on its first formulation.** `G1-Q` planted a credential-shaped value
that matched neither the scanner's pattern list nor its named-key list, and passed. It was
reformulated to mutate the real `.env.example` and run the real infrastructure control, and a second
attack `G1-R` was added at the configuration layer. Final result: 17 of 17 defended, with the
null-mutation control valid.

## What repeated

**`LSN-0038` recurred against its own guardrail — `GUARDRAIL_FAILURE`, recorded as `G1-F-008`.**

The lesson was written for two definitions of "placeholder" in one module, and `GRD-0040` asserted
that the two redactors agree. The class was larger than the control. The question *which names
carry a credential* turned out to be answered in three places — `iacode_common.redaction`,
`infra/tests/test_compose_definition.py` and `infra/tests/test_backup_tooling.py` — and they
disagreed: one read `IACODE_GATEWAY_MAX_OUTPUT_TOKENS` as a credential and the infrastructure suite
failed on it after the other two had been repaired.

Investigated as a failure of the control rather than as a third defect, which is what the contract
requires. Two things came out of it:

- The question has one home. Every consumer imports `is_sensitive_key`; a repository-wide scan
  fails the build if a module starts writing its own name rule, and it carries a negative control
  written the way the three offenders actually were.
- A second question had been conflated with the first. "Should this be redacted in a log" and "may
  this value sit in a committed file" are different: `IACODE_MINIO_ACCESS_KEY` is masked in a log
  because it half-identifies a credential, and is published in the example file beside the secret
  it pairs with. `carries_a_secret_value` is the narrower predicate, defined once, next to the
  wider one, with a test asserting that the two stay different.

The honest reading is that the first formulation of the guardrail was too narrow, not that the
lesson was wrong. `GRD-0040` now verifies five cases instead of two.

**`LSN-0011` recurred against its own guardrail — `GUARDRAIL_FAILURE`, recorded as `G1-F-009`.**

The same shape a second time, and it is worth naming: the guardrail listed
`green_keeper._refresh_declared_hashes` as its prevention — a *function*, not a property. So it
guarded the Green Keeper and nothing else. `scripts/iacode/verify.py` runs the same mandatory gate
set, did not re-derive the declared hashes, and reported `checkpointValidation` red for evidence
its own run had produced, minutes after the Green Keeper had reported it green.

The refresh now has one public home, both runners call it, and the control is expressed as a
property: every command that executes the mandatory gate set refreshes first, and a third runner
fails the test until somebody lists it and says why.

**`LSN-0037` recurred against its own guardrail — `GUARDRAIL_FAILURE`, recorded as `G1-F-010`.**

The lesson this Gate wrote for the Gate literal said "a Gate", so the scan it produced looked for
Gate literals. The fresh-installation scenario then failed with
`alembic_version='0002_model_gateway'`, because it compared the recorded revision with the literal
`"0001_foundation"` — the identical class with a different kind of identifier, invisible to a scan
that had been told which kind to look for.

The lesson is now about any identifier the repository derives. The head revision is derived once,
in `apps/api/migrations/head.py`, next to the migrations it reads, and both consumers import it.
The scan refuses a Gate named in a shared control and a revision compared for equality, and it
distinguishes naming a revision as *the answer* from naming one as a *starting point*, because an
upgrade-path test needs the second and the rule would be wrong to refuse it.

Three times in one Gate, a guardrail named a *place* where the failure had been fixed rather than
the *rule* that has to hold — twice a function or a consumer, once a kind of identifier. That is
the pattern worth carrying into Gate 2, and it is why this Gate's own new guardrails each carry a
case they must reject as well as the tree they must accept.

`LSN-0035` (subprocess output and the platform codepage) was exercised rather than repeated: the
new tooling states its codec at every capture, and the control that parses the tree stayed green as
those files were added.

`LSN-0035` (subprocess output and the platform codepage) was exercised rather than repeated: the new
tooling — `gateway_smoke.py`, `gateway_tests.py`, `gate1_red_team.py` — states its codec at every
capture, and the control that parses the tree stayed green as those files were added.

## What was learned

1. **A gate that measures inside a build artefact must build it.** Otherwise the gate's subject is
   not the repository, and its green is evidence about something else. True for any container,
   bundle or compiled artefact, not only for this image.
2. **A control that names the current Gate expires without saying so.** Anything shared across Gates
   derives the Gate from the checkpoint.
3. **Two definitions of one concept in one module will disagree, and a comment saying they must
   agree is not a mechanism.** One is authoritative; the other derives from it or does not exist.
4. **A specification can name a test that nobody wrote.** Rows 13.3 and 13.4 cited
   `test_frontend_calls_only_the_iacode_backend` and
   `test_frontend_adds_no_conversation_capability` by name; neither existed until the requirements
   matrix tried to resolve the reference. Deriving evidence from the specification rather than
   typing it is what surfaced it, and it is the argument for deriving.
5. **A control over sealed history first runs one Gate after the history is sealed.** A
   checkpoint cannot anchor its own tag, so the successor is the first run that can judge it. The
   delay is structural; what is not structural is leaving the property to a single audit step, so
   the suite now asserts it every run.
6. **A guardrail that names a function guards that function; a guardrail that names a
   property guards the property.** All three `GUARDRAIL_FAILURE`s in this Gate were controls
   written against the place a failure had been fixed — a function, a pair of consumers, a kind of
   identifier — rather than against the rule that has to hold.
7. **A test that writes to a shared service is writing production data.** Cleanup belongs in the
   test, and an invariant should detect the residue rather than trust the cleanup.
8. **`UNKNOWN` is not `UNSUPPORTED`.** Every model in the live catalog reported every capability
   except streaming as unknown, because the provider publishes nothing. A two-state model defaulting
   to "no" would have declared a fully capable catalog unusable; defaulting to "yes" would have
   spent money to discover each error. Recorded as `ADR-0017`.
9. **A stream commits to one model at its first delivered event.** Retry and fallback are free
   before it and forbidden after it, because the alternative is a single stream carrying two models'
   text with no marker. Recorded as `ADR-0018`.
10. **Policy names a credential; only the environment holds one.** A versioned file that holds a
   value is a published value, and the check that refuses a value where a variable name belongs has
   to run at load, not at review. Recorded as `ADR-0019`.

## What should become a guardrail

| Item | Control | Kind | Where it lives | What breaks if removed |
|---|---|---|---|---|
| Image gates build first | `test_every_image_gate_builds_before_it_measures` + rejecting case | test | `tests/test_gate1_model_gateway.py` | A mandatory gate can be green about code that is not in the repository |
| No Gate literal in a shared control | `test_no_shared_control_is_bound_to_a_gate_literal` + rejecting case | test | `tests/test_gate1_model_gateway.py` | A scope control refuses the authorized Gate and gets edited away instead of fixed |
| One placeholder definition | `test_both_redactors_agree_on_every_value_the_example_file_carries` | test | `apps/api/tests/unit/test_redaction.py` | The redactors disagree again and hide whether a real credential reached the example file |
| No control names a derived identifier | `test_no_control_names_a_migration_revision_literally` + a rejecting and an accepting case | test | `tests/test_gate1_model_gateway.py` | A control names today's Gate, checkpoint or migration revision and refuses the next one |
| Every runner of the mandatory gates refreshes the declared hashes | `test_every_runner_of_the_mandatory_gates_refreshes_the_declared_hashes` + two supporting cases | test | `tests/test_gate1_model_gateway.py` | The same gate is green under one runner and red under another, for evidence the run itself produced |
| Sealed history validates from its own tag | `test_every_sealed_checkpoint_validates_from_its_own_tag` + the recorder and validator rules | test | `tests/test_gate1_model_gateway.py` | A sealed checkpoint stops validating and nothing notices until a successor anchors it, one Gate later |
| Catalog holds only declared providers | `test_the_operational_catalog_holds_only_providers_the_policy_declares` | test | `apps/api/tests/integration/test_gateway_persistence.py` | Fixtures accumulate in the operator-visible catalog |

## New lessons

| Lesson | Status | Guarded by |
|---|---|---|
| `LSN-0036` — A gate that runs inside an image measures the image, not the source | GUARDED | `GRD-0038` |
| `LSN-0037` — A shared control that names an identifier the repository derives stops being a control when that identifier moves | GUARDED | `GRD-0039` |
| `LSN-0038` — Two representations of one concept in one module disagree, and the safer one loses | GUARDED | `GRD-0040` |
| `LSN-0039` — A test that writes to the operational database leaves production data behind | GUARDED | `GRD-0041` |
| `LSN-0040` — A control that judges sealed history only runs once a successor anchors it | GUARDED | `GRD-0042` |

## Updated lessons

| Lesson | Change | Reason |
|---|---|---|
| `LSN-0011` | `recurrenceCount` 0 → 1; `GRD-0006` broadened from one named function to the property, with three verifying cases | `G1-F-009`: the guardrail named a function, so it guarded one runner of the mandatory gate set |
| `LSN-0037` | Title and `recurrenceKey` generalised from "a Gate" to "an identifier the repository derives"; `recurrenceCount` 0 → 1; `GRD-0039` gains three cases | `G1-F-010`: the same class with a migration revision instead of a Gate |
| `LSN-0038` | `recurrenceCount` 0 → 1; `GRD-0040` broadened from two consumers to a repository-wide rule, with five verifying cases | `G1-F-008`: three modules answered the same question and disagreed |

## Retired lessons

| Lesson | Superseded by | Reason |
|---|---|---|
| — | — | None retired. |
