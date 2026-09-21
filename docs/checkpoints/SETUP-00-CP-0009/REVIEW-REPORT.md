# Independent Review Report — M0 / SETUP-00

Verdict: `REWORK_REQUIRED`
Audit classification: fresh-session independent milestone audit (`FRESH_SESSION_INDEPENDENT_AUDIT`)
Subject: `SETUP-00-CP-0008` at `c53f4c59a77870414324efa6b5f61b35d26c5090` / `refs/tags/iacode-checkpoints/SETUP-00-CP-0008`
Auditor: Claude Code 2.1.195, Anthropic, `claude-opus-5`, new session, no memory of the implementing run
Cross-tool validation: `NOT_AVAILABLE` — the implementing run used the same tool and the same provider
Gate 0: `BLOCKED`

## What this audit confirms

The corrective delivery is substantively good. All eleven `M0-F-0NN` findings of `SETUP-00-CP-0007`
are closed with regression tests that represent the original defects and that execute green. All
twenty-six mandatory `A`–`Z` attacks and all twenty additional attacks were re-executed by this
auditor's own harness, against the product rather than against the delivery's harness, and every one
was defended. The four guardrails `SETUP-00-CP-0007` reported as ineffective — `LSN-0005`,
`LSN-0007`, `LSN-0008`, `LSN-0009` — now block both their original bypass and a variation of it. The
canonical requirement set was re-derived independently and equals the declared set exactly, 131 for
131. Every semantic count recomputes. The suite is 306 for 306 in a clean clone of the sealed commit, and 305 for 306 in the working repository once the predecessor is anchored, which is finding CP9-F-002.

That is recorded here before the findings, because the findings are narrower than the delivery.

## Findings

### CP9-F-001 — CRITICAL — the external audit attestation can be written but never consumed, so `MILESTONE_EXTERNAL_PASS` is unreachable

- Requirement: `docs/SETUP-00-CHECKLIST.md` 7d.4; `docs/MILESTONE-VALIDATION.md`, *External
  validation is derived, never asserted*; `.iacode/attestations/README.md`; `NEXT.md` of
  `SETUP-00-CP-0008`, which instructs the auditor to write the attestation that produces the
  external PASS.
- Expected: an attestation authored by a different sealed, anchored checkpoint, with `APPROVED`,
  `RED_TEAM_PASS`, `100.0`, `100.0` and `PASS`, lets the audited subject reach
  `MILESTONE_EXTERNAL_PASS`.
- Observed: the verification logic is sound in isolation — a structurally valid attestation is
  accepted by `verify_attestation` (audit row `EXT-011`), and fifteen forged variants are refused
  (`EXT-001` to `EXT-010c`). The *workflow* cannot be completed:
  1. `validate_checkpoint.py` resolves the subject commit from the promoted checkpoint's own
     canonical tag, and `attestation.verify_attestation` requires `subjectCommit` to equal it. The
     attestation file is part of the tree of the commit the tag names, so satisfying the check
     requires a tree that contains its own commit identifier. Three attempts and a fixed-point
     iteration all end with `attests commit X, not the subject commit Y`.
  2. Writing the attestation in the *audit* checkpoint, which is what
     `.iacode/attestations/README.md` prescribes, moves `HEAD` past the subject's tag, after which
     the subject cannot be validated at all: `commit mismatch: expected
     'refs/tags/iacode-checkpoints/SETUP-00-CP-0008' -> 'c53f4c5…', observed '790d090…'`.
  3. `.iacode/attestations/` is inside the delivery-assurance scope, so merely adding an attestation
     marks the Green Keeper, the completeness audit, the internal Red Team and the internal mirror
     `STALE`, and re-running them changes the content again.
  No test asserts that a valid attestation is *accepted* end to end; `ExternalAttestationTests`
  contains twelve rejection cases and no acceptance case.
- Reproduction: `audit-harness/ext_reachability.py` (three attempts plus the fixed-point
  iteration), and the consume experiment recorded in `AUDIT-EXECUTIONS.json` under
  `externalPassReachability`. Both run entirely inside disposable clones.
- Evidence: `AUDIT-EXECUTIONS.json` `externalPassReachability`, `attestationProbes`;
  `FINAL-M0-AUDIT-MATRIX.json` rows `EXT-011`, `EXT-012`; `RED-TEAM-REPORT.md` control `POS-EXT`.
- Classification: `PRODUCT_DEFECT`, deterministic. Not environmental and not flaky.
- Acceptance criteria: an external milestone PASS must be reachable by an honest sequence of
  repository states. Any of these satisfies it, and the choice is the implementer's: verify the
  attestation against the checkpoint it names rather than against the checkpoint being validated;
  or bind `subjectCommit` to the subject's content commit, which the audit checkpoint can observe
  without circularity; or let the audit checkpoint carry the promotion of its subject; or exclude
  `.iacode/attestations/` from the assurance scope. Whatever is chosen, the positive path must be
  demonstrated.
- Regression scenario: a test that builds a two-checkpoint fixture — a sealed subject and a sealed,
  anchored audit checkpoint carrying a valid attestation — and asserts `CHECKPOINT_VALID` for a
  `MILESTONE_EXTERNAL_PASS` promotion, alongside the existing rejection cases.

### CP9-F-002 — CRITICAL — a guardrail test is bound to a literal checkpoint name, so performing the protocol's own next step turns the mandatory `tests` gate red

- Requirement: `docs/SETUP-00-CHECKLIST.md` 7d.8 and the Definition of Done, *every guardrail
  resolves, is verified by a test*; `docs/DEVELOPMENT-CONTRACT.md`, no test may be weakened to
  obtain a green result.
- Expected: carrying out the protocol's own next step — a successor anchoring its sealed
  predecessor — leaves the mandatory gate set green.
- Observed: `tests/test_development_ledger.py:3214` calls
  `verify_chain(self.root, require_sealed=True, exclude={"SETUP-00-CP-0008"})`. The mandatory
  `integrity` gate is correct, because `verify_integrity.py` derives the excluded checkpoint from
  `LATEST`, but the test does not. Two distinct failures follow, and both were observed rather than
  predicted:
  1. **Present, in this repository.** `docs/CHECKPOINT-PROTOCOL.md` requires a checkpoint to anchor
     every sealed predecessor, so this audit ran
     `verify_integrity.py --rebuild --exclude SETUP-00-CP-0009`, which produced
     `INTEGRITY_VALID anchors=8`. The full suite then went from 306/306 to 305/306:
     `IntegrityAnchorTests.test_a_sealed_checkpoint_without_an_anchor_is_detected` removes the last
     anchor, which is now `SETUP-00-CP-0008`, and the hardcoded exclusion swallows the error the
     test asserts: `AssertionError: False is not true : []`. Performing the mandatory step breaks
     the mandatory gate.
  2. **On sealing.** In a clone advanced exactly as this checkpoint advances the repository — a
     further checkpoint sealed under its canonical tag, `LATEST.md` updated, the chain rebuilt —
     `verify_integrity.py` exits `0` with eight anchors while
     `IntegrityAnchorTests.test_the_repository_chain_verifies` fails with `['sealed checkpoint
     SETUP-00-CP-0009 has no integrity anchor'] != []`.
- Consequence: this audit's own `tests` gate is red, truthfully recorded as such, and the next
  delivery inherits it. The only remedy available without repairing the cause is editing a guardrail
  test, which the Development Contract forbids as a way to obtain a green result.
  `SETUP-00-CP-0008` was green only because the literal in the test happened to name
  `SETUP-00-CP-0008` and nothing had yet anchored it.
- Reproduction: `command:cmd-0004` (full suite, 305/306), `command:cmd-0008` (the isolated test),
  and `AUDIT-EXECUTIONS.json` `successorSuiteSimulation` for the sealing case.
- Evidence: `FINAL-M0-AUDIT-MATRIX.json` row `TST-011`; `QUALITY.json` `unitTests` and
  `integrationTests`, recorded `FAIL`.
- Classification: `PRODUCT_DEFECT`, deterministic. Not environmental: the failure is in the
  repository's own suite, on the repository's own tooling, after a step the protocol requires.
- Acceptance criteria: derive the exclusion the way `verify_integrity.py` already does, from
  `resolve_latest` or from the sealed checkpoint that carries no anchor yet, and keep both
  assertions meaningful.
- Regression scenario: a test that seals a synthetic successor in a disposable clone, anchors the
  predecessor, and asserts that both of the suite's chain assertions stay meaningful and green.

### CP9-F-003 — LOW — a stale count survives in a current artifact because the count guardrail only inspects Markdown

- Requirement: `docs/SETUP-00-CHECKLIST.md` 7d.9, every count used as evidence is derived once and
  verified wherever a report states it.
- Expected: no current artifact states a count that contradicts the derivation.
- Observed: `tests/test_development_ledger.py:2600` states *the derived set is 119 anchored
  references*; the derived set is 131. `COUNT_CLAIM` only matches the `N/M NOUN` form and only in
  checkpoint Markdown, so a prose count in a `.py` file is outside the control.
- Evidence: `AUDIT-EXECUTIONS.json` `semanticCounts`.
- Classification: `PRODUCT_DEFECT`, deterministic, cosmetic in effect.
- Acceptance criteria: correct the number, and decide explicitly whether the derived-count control
  should reach prose counts outside checkpoint Markdown.

### CP9-F-004 — LOW — a lesson's own note contradicts its status

- Requirement: `docs/DEFINITION-OF-DONE.md`, implementation and documentation agree.
- Expected: a `GUARDED` lesson does not describe itself as unguarded.
- Observed: `LSN-0014` is `GUARDED` and names `GRD-0013`, while its `notes` field still reads
  *Not guarded: nothing can prove from the artifact alone that a record was written at execution
  time.* The same shape is correct on `LSN-0013`, which really is `CONFIRMED`.
- Evidence: `.iacode/memory/lessons.jsonl`; `AUDIT-EXECUTIONS.json` `engineeringMemory`.
- Classification: `PRODUCT_DEFECT`, deterministic, cosmetic in effect.
- Acceptance criteria: make the note describe the residual limit rather than the status, or remove
  it.

### CP9-F-005 — LOW — a policy key is declared and never read

- Requirement: `docs/DEFINITION-OF-DONE.md`, implementation and documentation agree;
  `.iacode/policies/documentation-policy.md`.
- Expected: a configuration value either governs behaviour or is not declared.
- Observed: `.iacode/memory/POLICY.json` declares `"guardrailRegistry": "guardrails/registry.json"`,
  while `lessons.guardrail_registry_path()` returns a constant path and never consults it.
  Re-pointing the key in a clone changed nothing, which this audit verified rather than assumed.
- Evidence: `AUDIT-EXECUTIONS.json` `preflightFreshness` and the `PRE-005c` probe.
- Classification: `PRODUCT_DEFECT`, deterministic, cosmetic in effect.
- Acceptance criteria: read the key, or remove it and say in the policy that the registry path is
  fixed.

## Failure classification

All five findings are deterministic product defects, reproduced in disposable clones. No finding is
environmental and none is flaky. Two intermediate red results observed during this audit were
classified as `AUDIT_ENVIRONMENT` and repaired in the audit harness only, never in the product: a
first harness revision did not restore historical tags between attacks, and a first harness revision
re-sealed mutations in a way that broke the seal chronology independently of the mutation under test.
Both are described in `AUDIT-EXECUTIONS.md`; every result reported here comes from the corrected
harness, which passes a null-mutation control.

## Decision

`REWORK_REQUIRED`. `CP9-F-001` and `CP9-F-002` are both mandatory findings. `CP9-F-001`: the mechanism that exists to make an external
milestone verdict derivable cannot produce one, and the status the milestone policy depends on is
unreachable. `CP9-F-002` is already red in this repository: anchoring the sealed predecessor, which the checkpoint protocol requires of every successor, took the suite from 306/306 to 305/306, and this audit did not weaken the test to hide it. No product repair was
made in this audit. `M0` does not pass and Gate 0 remains blocked.
