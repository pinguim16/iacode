# Development Ledger Tools

These Python 3 tools use only the standard library and are portable across Windows and Unix-like systems.

## Create

```text
python scripts/development-ledger/new_checkpoint.py --gate GATE-0 --status IN_PROGRESS --phase "GATE 0 — Foundation"
```

The command allocates the next four-digit checkpoint ID, creates every mandatory file with truthful non-PASS defaults, and updates the textual `LATEST.md` pointer.

## Validate

```text
python scripts/development-ledger/validate_checkpoint.py
```

Exit code `0` means valid. Any nonzero exit means invalid. Validation checks required and nonempty files, JSON parsing, bound JSON Schemas, command JSONL, file manifest structure, canonical status, branch, commit, dirty state, secret-shaped values, provenance, quality, handoff, next action, and the `LATEST.md` target.

Dirty-state relaxation is internal to `finalize_checkpoint.py` and is not exposed by the validation CLI, so unrelated working-tree changes cannot be hidden from a normal validation.

A checkpoint declaring `schemaVersion` `2.0.0` is additionally checked for a file inventory that
matches the real change set since `baseCommit` with bound content hashes, unique command identifiers,
quality verdicts backed by resolvable evidence references, and a structured `secondToolValidation`
state. A `1.0.0` checkpoint keeps the rules it was sealed under.

Validation also runs from a detached checkout of a checkpoint's own canonical tag, which is how a
second tool inspects an immutable reference. That mode requires a clean worktree and an existing tag
that resolves to the checked-out commit.

## Finalize

```text
python scripts/development-ledger/finalize_checkpoint.py --status READY_FOR_REVIEW
python scripts/development-ledger/finalize_checkpoint.py --status GATE_PASS --commit-ref refs/tags/iacode-checkpoints/SETUP-00-CP-0001
```

Finalization records timestamps, expects the checkpoint to become clean after commit, and performs a pre-commit validation. A Gate-closing checkpoint uses a namespaced tag reference: commit the result, create that tag at the resulting commit, and then run the validator normally. The tag binds the checkpoint to one immutable Git object without requiring a commit to contain its own hash.

Every attempt appends its own record, with its exit code, to the checkpoint's `COMMANDS.jsonl`. A
failed attempt restores the previous metadata and keeps its record, including a sanitized summary of
the validation errors, so the correction that followed stays visible. The successful attempt is
recorded before the inventory hashes are sealed. For `2.0.0` checkpoints, finalization re-derives
every declared hash from the repository, but it never adds or removes a declaration: an incomplete
manifest fails finalization until the author declares the missing paths. Finalization requires an
attached branch.

## Record a command

```text
python scripts/development-ledger/record_command.py --purpose "why this is evidence" -- python -m unittest discover -s tests
```

Runs the command, times it, and appends a reproducible record to the current checkpoint's
`COMMANDS.jsonl`: identifier, runtime, working directory, literal command, sanitized arguments,
referenced repository inputs, the repository commit, the purpose, the canonical result, the exit
code, and the duration. The recorded command keeps the portable `python` token while execution uses
the current interpreter, so the record replays from the working directory it names.

## Green Keeper

```text
python scripts/development-ledger/green_keeper.py --gates tests,staticAnalysis,checkpointValidation --trigger "delivery gate run"
```

Executes the mandatory gates, records each invocation, and appends the cycle to `REWORK-LOG.jsonl`.
Exit `0` means `GREEN_KEEPER_GATE=PASS`; exit `1` means a gate is still red; exit `2` means a real
external blocker was declared, which maps to a `BLOCKED` checkpoint and never to `PASS`. The tool
proves the state and never edits code: repairing the cause belongs to the role defined in
`.iacode/agents/test-rework-greenkeeper.md`.

## Delivery completeness

```text
python scripts/development-ledger/check_completeness.py --write
```

Audits `REQUIREMENTS-MATRIX.json` requirement by requirement, resolving every evidence reference, and
writes `COMPLETENESS-REPORT.json` and `COMPLETENESS-REPORT.md`. Exit `0` means
`DELIVERY_COMPLETENESS_GATE=PASS`, which requires total coverage, zero partial, zero missing, and
every reference resolved. `validate_checkpoint.py` recomputes the same audit, so a stored report
cannot disagree with the matrix it describes.

## Redact

```text
python scripts/development-ledger/redact_secrets.py input.txt
python scripts/development-ledger/redact_secrets.py input.txt --in-place
```

Standard output is the safest default. In-place mode writes a redacted temporary replacement; it never prints the original value.

## Schema scope

`checkpoint.schema.json` validates `STATE.json`; run metadata, command lines, tests, quality, and provenance each have a bound schema. `decision.schema.json` defines future structured decision exports while ADRs remain the canonical Markdown records. `experience.schema.json` is reserved for Gate 6 and later and implements no runtime.

## Engineering memory

```text
python scripts/development-ledger/validate_lessons.py --render-index
python scripts/development-ledger/lesson_preflight.py --gate "GATE 0" --scope runtime --write
python scripts/development-ledger/extract_lessons.py --write
```

`validate_lessons.py` checks the memory in `.iacode/memory/`: schema, unique identifiers, valid
status, provenance, training policy, evidence, preventive evidence behind every `GUARDED` lesson,
absence of secrets, and recurrence consistency. Exit `0` means valid. It is part of the Green Keeper
gate set, so a broken memory is a red delivery.

`lesson_preflight.py` selects the lessons that constrain a Gate and writes `LESSON-PREFLIGHT.json`
and `LESSON-PREFLIGHT.md` into the checkpoint, deriving a `LESSON-REQ-` requirement from each one.
Running it is mandatory before a Gate starts.

`extract_lessons.py` derives candidates from rework logs and finding documents. A candidate is never
stronger than `OBSERVED`; promotion is a human judgement, and `GUARDED` additionally requires a
control the tool cannot invent. A candidate matching an existing recurrence key increments that
lesson instead, and a repeat against a `GUARDED` lesson is recorded as a `GUARDRAIL_FAILURE`.

## Milestone closure tooling

```text
python scripts/development-ledger/derive_requirements.py --write
python scripts/development-ledger/verify_integrity.py
python scripts/development-ledger/verify_integrity.py --rebuild
python scripts/development-ledger/derive_counts.py --write
python scripts/development-ledger/m0_red_team.py --write
python scripts/development-ledger/m0_mirror_audit.py --clean-clone --write
python scripts/development-ledger/milestone_status.py --milestone M0
python scripts/development-ledger/promotion_simulation.py --write
python scripts/development-ledger/successor_durability.py --write
python scripts/development-ledger/affected_red_team.py --write
python scripts/development-ledger/seal_checkpoint.py
```

`policies.py` derives what the delivery is measured against. It reads the closed mandatory gate
registry in `.iacode/policies/quality-gates.json`, re-parses the canonical Gate checklist, and
re-parses the findings and attacks of every open audit named in `.iacode/policies/audit-registry.json`
directly from the sealed audit reports. Nothing here is transcribed, so nothing here can be trimmed.

`derive_requirements.py` writes `CLOSURE-REQUIREMENTS.json`/`.md` and `REQUIREMENTS-MATRIX.json`/`.md`
together from that derivation, preserving whatever evidence a run has already recorded. Re-running it
is how the matrix stays equal to the expected set.

`anchors.py` and `verify_integrity.py` maintain the hash-linked chain in
`.iacode/anchors/checkpoint-chain.json` over every sealed checkpoint's tag, commit and tree. This is
tamper evidence inside the local trust model, not a signature; the limit is documented in
`docs/CHECKPOINT-PROTOCOL.md`.

`attestation.py` derives a milestone verdict from `.iacode/attestations/<auditId>.json`, which the
**audit** checkpoint writes about the sealed subject it judged. A verdict cannot be produced by
editing `STATE.json`, and the subject is never rewritten to become approved: an audit is recorded
about sealed content, in a later checkpoint. `milestone_status.py --milestone M0` performs the whole
derivation from a clean checkout and exits nonzero when no valid attestation supports a PASS.
`CROSS_TOOL_INDEPENDENT_AUDIT` authorises `MILESTONE_EXTERNAL_PASS`;
`FRESH_SESSION_INDEPENDENT_AUDIT` authorises `MILESTONE_INDEPENDENT_AUDIT_PASS` and nothing
stronger.

`derive_counts.py` writes `COUNTS.json` from the artifact that owns each count, and the validator
rejects both a stored count and a Markdown claim that contradicts the derivation.

`m0_red_team.py` executes the mandatory attack battery against a disposable clone of the delivery and
writes `<milestone>-INTERNAL-RED-TEAM.json`/`.md`. `m0_mirror_audit.py` reproduces the dimensions of
the independent milestone audit and writes `<milestone>-INTERNAL-MIRROR.json`/`.md`. Both are internal
quality assurance and neither may be recorded as external validation.

`promotion_fixture.py` builds disposable repositories that execute the protocol's own positive
paths, and the two entry points over it record what they observed:
`promotion_simulation.py` delivers and seals a subject checkpoint, authors a second checkpoint as its
audit, and derives the milestone verdict, writing `POSITIVE-PROMOTION-VALIDATION.json`/`.md`;
`successor_durability.py` seals a chain of checkpoints, each anchoring its predecessor, re-runs the
integrity controls at every state and writes `SUCCESSOR-DURABILITY.json`/`.md`. A control proven only
by refusals is not proven, and a protocol transition that breaks a mandatory gate must be found by
the delivery that introduces it.

`affected_red_team.py` reports the adversarial position by explicit derived category — the mandatory
battery, the additional battery, the attestation scenarios and the executed positive controls — so no
two totals in a report can overlap or drift.

`seal_checkpoint.py` validates the committed content with a clean worktree, records that run as
`post-commit-validation`, stamps the end of the run after it, and commits the append-only evidence
before creating the canonical tag.
