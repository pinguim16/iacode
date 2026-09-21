# Independent Review Report — M0 / SETUP-00

- Audit checkpoint: `SETUP-00-CP-0013`
- Subject: `SETUP-00-CP-0012`, sealed under `refs/tags/iacode-checkpoints/SETUP-00-CP-0012`
- Mechanism: `FRESH_SESSION_INDEPENDENT_AUDIT`
- Tool, provider, model: Claude Code, Anthropic, `claude-opus-5` — the implementer's. This is
  independence of the session, not of the tool, and `crossToolValidation` is `NOT_AVAILABLE`.
- Verdict: **`APPROVED`**

## What was audited and how

`SETUP-00-CP-0012` is the corrective delivery of `CP11-F-001`, the single critical finding of the
fresh-session independent audit sealed in `SETUP-00-CP-0011`. The finding was read from that sealed
review report, not from the closure record that claims to have closed it.

The audit matrix was written before substantive execution, with every row `NOT_STARTED`, and its
results were merged afterwards from an append-only execution record. Nothing in this checkpoint's
`derive_expected.py`, `resolve_evidence.py` or `verify_memory.py` imports `policies.py`,
`delivery_assurance.py` or `lessons.py`: where this audit agrees with the delivery, two independent
readers agreed.

Every mirror verdict here was produced by executing `m0_mirror_audit.py`. That is not a formality:
`CP11-F-001` survived a passing rehearsal precisely because a simulation wrote the artifact the tool
would have produced.

## Findings

None. No defect of this delivery was found that this audit can substantiate.

## `CP11-F-001` — CRITICAL — `CLOSED`

### What the finding was

`m0_mirror_audit.py` derived two of its eighteen checks from the audit registry. `MIR-002` returned
`closed == total and total > 0` and `MIR-003` required `bool(expected)`, so a checkpoint with
nothing to audit reported `FAIL` rather than `NOT_APPLICABLE`. The report then failed, and
`validate_checkpoint` refused every positive terminal status. The consequence was that the
protocol's own prescribed next step could not be completed with the shipped tooling: the audit
checkpoint could not close at the status its subject's `NEXT.md` instructed it to use, and the first
delivery of any later Gate could not reach `READY_FOR_REVIEW`.

### What the repair is, and why it is the right shape

An empty applicable set and a missing required set are now different outcomes. The first is
`NOT_APPLICABLE` carrying three things that make it auditable rather than a silent escape: a reason,
an `expectedCount` of zero, and the canonical source the emptiness was derived from. The second is
still `FAIL`. The applicable set is derived in exactly one place, `policies.audit_applicability`,
from the audit registry matched on the Gate and on the checkpoint the registry itself names as the
corrective delivery, with the findings and the mandatory attacks re-parsed from the sealed reports
at every call. An audit whose sealed report cannot be read raises rather than reducing to an empty
set.

This is the shape the role contract already prescribed. `.iacode/agents/m0-closure-auditor.md`
required that a check which cannot run be recorded as `NOT_APPLICABLE` with a reason, and
`mirror-audit.schema.json` already admitted the value. The defect was that no check ever emitted one.
Implementation and documentation now agree, which is what `docs/DEFINITION-OF-DONE.md` asks for.

### How this audit proved it, rather than read it

Six applicability states were executed against the real tool in disposable clones by this audit's own
probe (`audit-harness/probe_mirror.py`, results in `MIRROR-SEMANTICS-PROBE.json`):

| State | Expected | Observed |
|---|---|---|
| The subject as it stands, one applicable finding, all closed | `MIR-002` `PASS` | `PASS`, whole report 18/18 |
| The applicable finding set back to `OPEN` | `FAIL` | `FAIL`: `0/1 audit findings CLOSED; CP11-F-001 is OPEN` |
| The required closure record deleted | `FAIL` | `FAIL`: `CP11-FINDINGS-CLOSURE.json is missing` |
| The delivery declaring its own empty expected set | `FAIL` | `FAIL`: `CP11-F-001 is undeclared` |
| The registry repointed at a report with no parseable finding | `FAIL` | `FAIL`: the check raises rather than emptying |
| The registry entry deleted so nothing is applicable | `NOT_APPLICABLE`, report still fails | `NOT_APPLICABLE`, report `FAIL` on the shrunken expected set |

The zero-set state reaching a **passing** overall report was proved where it actually occurs rather
than by deleting a registry entry: `gate_transition_simulation.py` builds the first checkpoint of the
next Gate in a disposable repository, produces its mirror by executing `m0_mirror_audit.py`, and
reaches `READY_FOR_REVIEW` with the two empty dimensions `NOT_APPLICABLE` and justified — nine checks
of nine. `mirror_semantics_validation.py`, the delivery's own control, was executed as well and
reported six states of six, with `MSV-001` the passing zero-set case.

The most direct proof is this checkpoint. No registered audit names `SETUP-00-CP-0013` as its
corrective delivery, so its own applicable set is empty and its own mirror records the two
registry-bound dimensions as `NOT_APPLICABLE`. Under the defect, this audit checkpoint could not
have existed in a valid state at all.

### The escape the repair could have opened, and did not

Making `NOT_APPLICABLE` reachable invites the mirror-image defect: declaring a dimension inapplicable
instead of satisfying it. This audit attacked that state directly, each attack in its own disposable
clone, over a null-mutation control the unmutated subject passed first:

| Attack | Refusal |
|---|---|
| Inapplicable with no reason | `check MIR-002 is NOT_APPLICABLE without a reason; an unjustified inapplicable check is indistinguishable from a skipped one` |
| Inapplicable over work the registry names | `recorded as NOT_APPLICABLE while the canonical sources name 1 applicable audit finding(s)` |
| Inapplicable while carrying items | `is NOT_APPLICABLE with expectedCount=4; a dimension that has items to audit is not inapplicable` |
| Inapplicable under report version `1.0.0` | `requires the justification fields of report schemaVersion 1.1.0` |
| Inapplicable counted as a pass | `passed does not match the recorded checks` |
| Every dimension inapplicable at once | refused on the first registry-bound dimension |
| A failed dimension with an overall `PASS` | `a failed check cannot produce a PASS` |

The refusals come from two independent layers: the auditor refuses to emit such a check, and
`validate_checkpoint._validate_mirror_applicability` re-derives the applicable set from the registry
and the sealed reports and refuses the claim rather than believing it.

### Deleting the audit from the registry does not buy a pass

The applicable set is derived from the registry, so the obvious attack is to delete the entry. This
audit executed it. The two registry-bound dimensions do become `NOT_APPLICABLE` — correctly, because
nothing is then applicable — and the overall mirror still **fails**, on two other dimensions that
were not written for this attack: the expected requirement set shrinks with the registry, so the
anchored declared set no longer equals it (`118 anchored against an expected set of 105`), and
editing a policy file makes the last green Green Keeper cycle stale.

### Why the earlier controls did not catch it, and whether that is fixed

`promotion_simulation.py` reached `MILESTONE_INDEPENDENT_AUDIT_PASS` while the real control refused
every delivery, because its fixture wrote the mirror report by hand. That is now
`promotion_fixture._execute_internal_mirror`, which runs `m0_mirror_audit.py --write --checkpoint`,
fails loudly if the tool produced no report, and records the real exit code; no code path in the
fixture writes that artifact. `POS-008` asserts it for every checkpoint in the simulation and
`GT-004` for the Gate transition. Both were re-executed here: `POSITIVE_PROMOTION=PASS verdict=PASSED
checks=9/9` and `GATE_TRANSITION=PASS checks=9/9 status=READY_FOR_REVIEW`.

The recurrence itself is recorded the way the project's policy requires. It is a `GUARDRAIL_FAILURE`
on `LSN-0024` (*a control is finished only when its positive path has been executed*) and `LSN-0029`
(*a required protocol transition must never turn a mandatory gate red*), both resolved in
`SETUP-00-CP-0012`, with `GRD-0031` and `GRD-0032` as the new controls — not a fresh lesson that
would have hidden the repeat. The genuinely new class became `LSN-0031`, `GUARDED` by `GRD-0030` and
`GRD-0031`.

## Everything else this audit re-derived rather than believed

**The expected requirement set.** Derived independently from the Gate checklist, this checkpoint's
preflight and the audit registry: 118 references for the subject — 75 canonical, 30 lesson-derived,
1 finding, 12 mandatory attacks — equal to the 118 anchored rows the delivery declares, with no
omission, no duplicate and no unexpected anchor. The 38 further rows the subject declares are
`local:` and are audited like any other row without entering the denominator.

**Evidence.** All 881 evidence references of the subject's matrix resolve: 350 repository files, 327
checkpoint artifacts, 201 suite identifiers and 3 command records. No row is `COMPLETE` without
evidence. Coverage and evidence coverage are both 100.00.

**Counts.** Every count the subject uses as evidence was re-derived and matched its sealed
`COUNTS.json` exactly: four hundred and ten tests of four hundred and ten, one hundred and
fifty-six requirements of one hundred and fifty-six, one finding of one, seventy-three attacks of
seventy-three, twenty-nine guarded lessons of thirty-one, and thirty-two effective guardrails of
thirty-two. The same derivation in a clean clone produced the same values. The figures are written
in words here because a count stated in prose is not evidence: the machine-readable value lives in
`COUNTS.json` and the derivation is what checks it.

**The suite.** 410 discovered, 410 run, 0 failures, 0 errors, and one skip, investigated below. The
same result in a clean clone detached at the subject tag.

**The engineering memory.** 31 lessons, 29 `GUARDED` and 2 `CONFIRMED`; 32 guardrails, every one
resolving to a real control, every one naming verifying tests that exist — all 72 `verifiedBy`
references resolve — and no guardrail failure unresolved. Measured with this audit's own readers,
which look invariant symbols up by importing the module rather than by searching the source text.

**Integrity.** `INTEGRITY_VALID anchors=11`, every tag resolving to its anchored commit, the chain
linking, and every sealed checkpoint still validating under the current tooling. A moved tag, a
forged anchored commit, a broken link and a removed anchor were each attacked and each refused.

**The subject is untouched.** Its tag resolves to the same commit, its tree is unchanged, and its
`STATE.json` still records `READY_FOR_REVIEW` with `externalAttestation` `NONE`. The clean-clone run
at that tag, performed after this checkpoint existed, reproduced every one of the subject's own
results, because a sealed checkpoint is validated from its canonical tag and that tree contains no
file created later.

**Secrets.** All 514 tracked files scanned with the project's own redaction patterns: no hit. The
credential-shaped strings that exist anywhere in the checkout are synthetic fixtures composed at run
time — `"sk-" + ("a" * 20)` and its siblings — so the literal never appears in a source file, and
they survive only inside ignored `__pycache__` artifacts. `git diff --check` is clean.

## What this audit examined and did not raise

Each of these was looked at and judged not to be a defect. The condition that would turn it into one
is recorded, because an audit that reports only its verdict hides what it looked at.

**The single skip.** `AuditAttestationModelTests.test_an_unsealed_subject_is_rejected` skips with
*every checkpoint directory in this checkout is sealed*. The skip is state-conditional and inverts
with the lifecycle: during any delivery the current checkpoint is unsealed and the case executes; it
skips only in a repository at rest, which is what an auditor checks out. No guardrail and no
checklist row names that method, and the rest of its class executes unconditionally. The subject's
recorded *0 skipped* was true of the pre-seal tree it measured, and is not a false claim about the
sealed tree. It becomes a finding if a guardrail or a checklist row ever names that method
specifically, or if the number of state-conditional skips grows.

**The documented evidence format is narrower than the accepted one.**
`delivery_assurance` documents `test:<TestClass.test_name>` and accepts a bare class name and a bare
method name as well. Every such reference in the subject names a case that exists, so nothing is
unverified; the looseness is in the documentation, not in the resolution. It becomes a finding if a
reference is ever accepted that names no discoverable case.

**Three attacks were refused by the inventory binding before reaching their target.** Any edit to a
sealed checkpoint changes a declared hash and `FILES.json` says so first. That is a real defence but
it is not evidence about the control under test, so those three were re-run as variants that
re-derive the declared hashes with the project's own helper before validating. Each was then refused
by the control it was aimed at: the derived-count comparison, the rule that a milestone verdict
belongs to the audit checkpoint, and the Green Keeper staleness rule.

**`producedBy: "execution"` is a literal.** The fixture's proof that it ran the tool is a constant
string. It is load-bearing only in combination with the real subprocess exit code and the
`FixtureError` raised when the tool produces no report, both of which the same function records. It
becomes a finding if that flag is ever set on a path that does not execute the tool.

**The trust model is structural.** A milestone verdict needs a second sealed, tagged, anchored
checkpoint authored about an already sealed subject. An actor controlling the whole repository can
still recompute the chain. The limit is already written down rather than papered over, and it is not
a defect of this delivery.

## Limits of this verdict

This audit is independent of the implementing run and of its session. It is not independent of the
tool, the provider or the model, all three of which are the implementer's. A defect both runs share
— a blind spot of the model, or a wrong belief in the contracts both read — is outside what this
mechanism can detect. `crossToolValidation` is recorded as `NOT_AVAILABLE` so that limit stays
visible, and the derivation refuses to promote `MILESTONE_EXTERNAL_PASS` from this attestation,
which this audit executed as an attack rather than assumed.

## Decision

`CP11-F-001` is `CLOSED`. No new finding. The delivery is **`APPROVED`**.

`M0` passes by `MILESTONE_INDEPENDENT_AUDIT_PASS`, carried by this checkpoint about the sealed
`SETUP-00-CP-0012`. `SETUP-00` is closed. `GATE 0 — FOUNDATION` is authorised and not started: its
first deliverable is the canonical requirement specification that
`.iacode/policies/canonical-requirements.json` does not yet contain.
