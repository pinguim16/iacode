# Independent Review Report — M0 / SETUP-00

Verdict: `REWORK_REQUIRED`
Audit classification: fresh-session independent milestone audit (`FRESH_SESSION_INDEPENDENT_AUDIT`)
Subject: `SETUP-00-CP-0010` at `90b67a7e0a11179465bc5c92dee22c78da36801f` /
`refs/tags/iacode-checkpoints/SETUP-00-CP-0010`
Auditor: Claude Code 2.1.195, Anthropic, `claude-opus-5`, new session, no memory of the implementing
run
Cross-tool validation: `NOT_AVAILABLE` — the implementing run used the same tool, the same provider
and the same model
Gate 0: `BLOCKED`

## What was audited and how

Nothing below rests on a statement made by the delivery. The expected requirement set was re-derived
by a parser that never imports `policies.py`; every declared evidence reference was resolved by a
resolver written for this audit; every integrity anchor was recomputed from Git without `anchors.py`;
the prose-count control was re-implemented and checked against a planted offender; and every test
named by the closure record was executed by identifier rather than read.

## The five findings of `SETUP-00-CP-0009`

### `CP9-F-001` — CRITICAL — `CLOSED`

The defect was a control whose reachable state space was empty: the attestation was consumed as if
it belonged to the checkpoint being promoted, so satisfying it required a tree containing its own
commit identifier, and twelve rejection tests passed with no acceptance case.

The repair separates the two objects. A delivery checkpoint is sealed, tagged, anchored and closed at
`READY_FOR_REVIEW`; a later audit checkpoint anchors it and carries
`.iacode/attestations/<auditId>.json`, which names the subject and the commit the subject tag already
resolves to, never its own. `attestation.derive_milestone_verdict` computes the verdict from the
repository, and `milestone_status.py` prints the derivation.

The positive path is reachable, and this audit did not take that on trust in three separate ways.
`promotion_simulation.py`, executed from a clean clone, builds a throwaway repository, delivers and
seals a subject, authors a second checkpoint as its audit with a valid attestation, seals that, and
derives `PASSED`: seven checks of seven. `AuditAttestationModelTests` contains an acceptance case
over the repository's own sealed history, which this audit executed. And this audit performed the
promotion against the real repository: it anchored `SETUP-00-CP-0010`, wrote the attestation about
it, and in a sealed snapshot of this checkpoint built by the same finalize and seal tooling the real
one uses, `validate_checkpoint.py` exits zero and
`milestone_status.py --milestone M0` prints `MILESTONE_PASSED` with one accepted attestation naming
`SETUP-00-CP-0010` at its sealed commit as audited by `SETUP-00-CP-0011`.

The attestation architecture is therefore closed and reachable. One artifact had to be modelled in
that snapshot rather than produced, and that is finding `CP11-F-001` below: it is a defect in a
different control, not in this one.

Rejection still works. The sixteen attestation cases in the suite were executed by identifier and
passed. This audit additionally probed three refusal branches directly — an unsealed audit
checkpoint, an unanchored one, and a subject commit that is not an ancestor of the audit commit — and
each refused with the message the model predicts. The mandatory battery refused every forged
attestation from `AU` to `BD`.

The subject is untouched. Its tag still resolves to the same commit, its tree is unchanged, and its
`STATE.json` still records `READY_FOR_REVIEW` with `externalAttestation` `NONE`. Adding the audit
makes nothing stale: all four assurance fingerprints recomputed in a clean clone at the subject tag,
after this audit existed, and matched exactly, because the subject's results describe the tree its
own tag names and that tree does not contain a file created later.

The semantics are honest. A `FRESH_SESSION_INDEPENDENT_AUDIT` authorises only
`MILESTONE_INDEPENDENT_AUDIT_PASS`; `MILESTONE_EXTERNAL_PASS` is refused for it, which attack `BA`
executes and which this audit re-executed. `crossToolValidation` must be `AVAILABLE` for a cross-tool
mechanism and `freshSession` must be true for a fresh-session one.

### `CP9-F-002` — CRITICAL — `CLOSED`

The defect was one semantic rule with two implementations, one derived and one typed: a guardrail
test excluded a checkpoint by literal name, so performing the protocol's own next step turned the
mandatory `tests` gate red.

There is now one implementation, `anchors.pending_anchor_exclusion`, and the command-line tool, the
validator and the suite all ask it. The anchor test that used to name its victim now derives one that
the pending rule does not forgive, so both assertions stay meaningful. This audit scanned every
remaining literal checkpoint identifier in `scripts/` and `tests/` and classified each: narrative
docstrings, provenance labels for attack origins, assertions that deliberately name specific sealed
history, and one fallback used only when a fixture repository has sealed nothing. None decides
integrity behaviour.

`successor_durability.py`, executed from a clean clone, seals three checkpoints in succession, each
anchoring its predecessor, and re-runs the integrity controls at every state: eight checks of eight,
green throughout, including the negative control that removes an anchor the rule does not forgive and
the restoration that follows. This audit then performed the same transition for real — it anchored
its sealed predecessor and the mandatory gate set stayed green — which is the exact step that turned
the suite red in `SETUP-00-CP-0009`.

### `CP9-F-003` — LOW — `CLOSED`

The superseded cardinality is gone from every current artifact. The only surviving occurrence is
inside an ordinary string literal in the test that plants the offending shape, which
`docs/QUALITY-GATES.md` explicitly exempts as data rather than a claim.

The control now reaches the comments and docstrings of `scripts/` and `tests/`, and the policy
decision the finding asked for is written down: a count stated in a source comment or docstring is
not evidence, canonical counts live in `COUNTS.json`, and a count inside a string literal is data.
This audit re-implemented the control rather than invoking it: twenty-eight Python sources tokenised
and parsed, no offender, and the same implementation detects both a planted cardinality and a planted
count claim.

The repeat is recorded as a `GUARDRAIL_FAILURE` on `LSN-0022` with `GRD-0026` as the new control and
`SETUP-00-CP-0010` named as the checkpoint that resolved it, rather than as a new lesson. That is the
correct treatment of a recurrence.

### `CP9-F-004` — LOW — `CLOSED`

`LSN-0014` is `GUARDED`, names `GRD-0013`, and its note now describes the residual limit of the
control instead of restating a status. Memory validation refuses a `GUARDED` lesson that describes
itself as unguarded, and both named tests were executed. `LSN-0013`, which really is `CONFIRMED`,
keeps its unguarded note, so the two records agree with their own statuses rather than with each
other.

### `CP9-F-005` — LOW — `CLOSED`

The `guardrailRegistry` key is gone. The memory policy schema is closed against additional
properties, so a setting no code reads cannot be declared and quietly ignored; the registry path has
one resolver and the policy document states that it is fixed and why. All three named tests were
executed, and the battery refuses a re-declaration of the key.

## Everything the previous audit confirmed, re-confirmed

The whole suite executes green in the working repository and in a clean clone detached at the subject
tag: three hundred and sixty-three discovered, three hundred and sixty-three run, zero failures and
zero errors in both. Every canonical mandatory validator exits zero in both environments. The
declared requirement set equals an independently derived expected set exactly, one hundred and
thirty-four for one hundred and thirty-four, and all seven hundred and twenty-three evidence
references resolve. The Green Keeper cycle was measured against the canonical mandatory gate set with
no gate dropped, every gate exited zero with command evidence, and its scope fingerprint still
describes the sealed content. The engineering memory is valid, every guardrail is effective and no
guardrail failure is unresolved. The preflight is fresh by recomputation and every derived lesson
requirement is in the matrix. The sealed chain verifies, every anchored tag resolves to its anchored
commit and tree, and all ten sealed checkpoints validate from a detached checkout of their own tag
under the current tooling.


## Findings

### `CP11-F-001` — CRITICAL — the internal mirror audit cannot pass for a delivery that corrects no audit, and checkpoint validation requires it to pass

- Requirement: `.iacode/agents/m0-closure-auditor.md`, *A check that cannot run is recorded as
  `NOT_APPLICABLE` with a reason, never silently omitted*; `docs/DEFINITION-OF-DONE.md`,
  implementation and documentation agree; `docs/SETUP-00-CHECKLIST.md` 7d.11; `LSN-0029`, *a
  required protocol transition must never turn a mandatory gate red*; `LSN-0024`, *a control is
  finished only when its positive path has been executed*.
- Expected: a checkpoint that carries out the protocol's own next step reaches a handoff-ready
  status with the shipped tooling. For this audit that step is written in `NEXT.md` of the subject:
  anchor the subject, write the attestation, and close at `MILESTONE_INDEPENDENT_AUDIT_PASS`. For
  the delivery that follows it is `READY_FOR_REVIEW`.
- Observed: `m0_mirror_audit.py` derives two of its eighteen checks from
  `policies.open_audits(root, gate, checkpoint)`, which is empty for any checkpoint that is not the
  registered corrective delivery of an audit. `MIR-002` returns `closed == total and total > 0` and
  `MIR-003` returns `... and bool(expected)`, so both report `FAIL` rather than `NOT_APPLICABLE`
  when there is nothing to audit. The report is then `FAIL`, and
  `validate_checkpoint._validate_internal_assurance` refuses every positive terminal status:
  `MILESTONE_INDEPENDENT_AUDIT_PASS requires the internal mirror audit to pass, found 'FAIL'`.
  Two states were executed rather than predicted:
  1. **This audit checkpoint.** `m0_mirror_audit.py --write --clean-clone` against
     `SETUP-00-CP-0011` produced fifteen passing checks and `MIR-002` `FAIL: 0/0 audit findings
     CLOSED`. The two other failures in that run were the absent red-team report and the absent
     counts, both of which a delivery supplies; `MIR-002` is not one a delivery can supply.
  2. **The next delivery.** In a disposable clone, `new_checkpoint.py --gate GATE-0` followed by
     `m0_mirror_audit.py` produced the same `MIR-002` `FAIL: 0/0 audit findings CLOSED`. A Gate 0
     delivery corrects no audit, so no amount of populating the checkpoint can make that check pass.
  The schema already admits the correct outcome: `mirror-audit.schema.json` allows
  `NOT_APPLICABLE`, and the tool counts such checks, but no check ever emits one.
- Consequence: the protocol's prescribed next step cannot be completed with the shipped tooling.
  This audit could not close at the status `NEXT.md` instructs it to use, and the first Gate 0
  delivery cannot reach `READY_FOR_REVIEW`. The milestone verdict itself is derivable — the sealed
  snapshot proves it — so the blocked control is the internal mirror, not the attestation.
- Why the existing controls did not catch it: `promotion_simulation.py` does reach
  `MILESTONE_INDEPENDENT_AUDIT_PASS`, but its fixture writes the mirror report by hand instead of
  running `m0_mirror_audit.py`, so the rehearsal passed while the real path was blocked. That is the
  failure class of `LSN-0024`, whose own lesson is that a control is finished only when its positive
  path has been executed, and of `LSN-0029`, guarded by `GRD-0029`, *the protocol's own next steps
  are executed before handoff*. Both are `GUARDED`, and both classes recurred, so this is a
  `GUARDRAIL_FAILURE` and the controls themselves need investigating, not only the defect.
- Reproduction: `python scripts/development-ledger/m0_mirror_audit.py --checkpoint
  docs/checkpoints/SETUP-00-CP-0011` in this repository, and the `GATE-0` probe recorded in
  `AUDIT-EXECUTIONS.json` under `mirrorReachability`. Both are read-only or run in a disposable
  clone.
- Evidence: `M0-INTERNAL-MIRROR.json` in this checkpoint, which records the failing run;
  `AUDIT-EXECUTIONS.json` `mirrorReachability`; `FINAL-M0-AUDIT-MATRIX.json`.
- Classification: `PRODUCT_DEFECT`, deterministic. Not environmental and not flaky: the predicate is
  in the source, and both states were executed.
- Acceptance criteria: a checkpoint that corrects no audit must be able to obtain a passing internal
  mirror through the shipped tooling. Any of these satisfies it, and the choice is the
  implementer's: record a check with nothing to audit as `NOT_APPLICABLE` with its reason, which is
  what the role contract already prescribes; or scope the mirror requirement in the validator to the
  checkpoints it was written for; or derive the expected findings and attacks from what the
  checkpoint claims to close rather than from the registry alone. Whatever is chosen, the positive
  path must be executed by running `m0_mirror_audit.py` itself, not by writing the artifact it would
  have produced.
- Regression scenario: a test that creates a checkpoint with no open audit in a disposable clone,
  runs the mirror audit over it, and asserts a `PASS` with the two checks recorded as
  `NOT_APPLICABLE` with reasons; and a positive-path simulation that produces the mirror report by
  executing the tool rather than by writing it.

## What this audit examined and did not raise

Five further properties were examined and judged not to be defects, and each is recorded in
`AUDIT-EXECUTIONS.json` with the condition that would turn it into one: the one-case difference in
the passing count between environments, a loose narrative sentence about adversarial categories, the
three attestation refusal branches that have no test, the documented scope of the prose-count
control, and the structural rather than cryptographic trust model. Recording them is deliberate: an
audit that reports only its verdict hides what it looked at.

One result of this audit is classified as an environment failure rather than a defect and is
recorded as such: re-running `green_keeper.py` against the sealed subject appends to a closed ledger
and dirties the worktree, so its final gate refuses. Its first four gates were green, and the
recorded verdict was verified instead by re-executing the five canonical mandatory gate commands
individually in a clean clone, all of which exited zero.

Two defects in this audit's own instruments were found and corrected, and both are recorded rather
than quietly repaired: the first matrix generation read the closure record with the wrong field
names and derived no regression row, and the first revision of the adversarial battery carried four
wrong expectations. Neither changed a product result.

## Limits of this verdict

This is independence from the implementing run, not from the tool. The auditing session shares the
tool, the provider and the model with the run that produced the subject, so a systematic blind spot
of that tool or that model would not be detected here. No part of this audit is recorded as
cross-tool validation, and the attestation records `crossToolValidation: NOT_AVAILABLE` so the limit
stays visible instead of implied.

## Decision

`REWORK_REQUIRED`. The five `CP-0009` findings are closed, the attestation architecture works in
both directions, and every other dimension of the milestone is green — but `CP11-F-001` is a
mandatory finding of the class this milestone has already corrected twice: a control whose positive
path cannot be reached with the shipped tooling, blocking the protocol's own next step. `M0` does
not pass, `SETUP-00` returns to the implementer, and `GATE 0 — FOUNDATION` remains `BLOCKED`.

No product code was changed by this audit.
