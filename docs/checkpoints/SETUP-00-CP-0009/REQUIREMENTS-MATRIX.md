# Requirements Matrix — SETUP-00-CP-0009

The canonical SETUP-00 specification with this audit's verdict per row. 69 of 71 confirmed, 2 not confirmed.

| ID | Source | Status | Description |
|---|---|---|---|
| REQ-0001 | canonical:SETUP-00#1.1 | `COMPLETE` | A single entry point states the phase, current Gate, latest checkpoint, and start protocol. |
| REQ-0002 | canonical:SETUP-00#1.2 | `COMPLETE` | A Codex adapter binds the canonical contracts without adding independent policy. |
| REQ-0003 | canonical:SETUP-00#1.3 | `COMPLETE` | A Claude Code adapter binds the same contracts. |
| REQ-0004 | canonical:SETUP-00#1.4 | `COMPLETE` | Tool adapters stay semantically equivalent to the canonical roles. |
| REQ-0005 | canonical:SETUP-00#2.1 | `COMPLETE` | The Gate sequence, dependencies, acceptance, and fail conditions are recorded. |
| REQ-0006 | canonical:SETUP-00#2.2 | `COMPLETE` | The completion standard, mandatory controls, and Git and evidence discipline are recorded. |
| REQ-0007 | canonical:SETUP-00#2.3 | `COMPLETE` | Tool-to-tool transfer is formal in both directions. |
| REQ-0008 | canonical:SETUP-00#2.4 | `COMPLETE` | Checkpoint statuses, required events, required contents, commit semantics, and divergence handling are defined. |
| REQ-0009 | canonical:SETUP-00#2.5 | `COMPLETE` | Done is defined and excludes assertion-only PASS. |
| REQ-0010 | canonical:SETUP-00#2.6 | `COMPLETE` | Quality outcomes, required dimensions, and the promotion rule are defined. |
| REQ-0011 | canonical:SETUP-00#2.7 | `COMPLETE` | Structural decisions are recorded as ADRs. |
| REQ-0012 | canonical:SETUP-00#2.8 | `COMPLETE` | Architecture, roadmap, provenance, model usage, and detected tool capabilities are documented. |
| REQ-0013 | canonical:SETUP-00#3.1 | `COMPLETE` | The canonical, tool-neutral role contracts exist, one per role of the delivery protocol. |
| REQ-0014 | canonical:SETUP-00#3.2 | `COMPLETE` | Documentation, provenance, secret, tool-execution, and training-data policies exist. |
| REQ-0015 | canonical:SETUP-00#3.3 | `COMPLETE` | Reusable templates exist for ADRs, checkpoints, gate reports, and handoffs. |
| REQ-0016 | canonical:SETUP-00#4.1 | `COMPLETE` | Checkpoint state, run metadata, command, test, quality, provenance, and decision schemas exist and are loadable. |
| REQ-0017 | canonical:SETUP-00#4.2 | `COMPLETE` | An experience schema is reserved for Gate 6 and implements no runtime. |
| REQ-0018 | canonical:SETUP-00#4.3 | `COMPLETE` | Schema evolution is versioned and never invalidates a sealed checkpoint. |
| REQ-0019 | canonical:SETUP-00#5.1 | `COMPLETE` | A checkpoint can be created with truthful non-PASS defaults. |
| REQ-0020 | canonical:SETUP-00#5.2 | `COMPLETE` | A checkpoint can be finalized, and every finalization attempt is recorded with its exit code. |
| REQ-0021 | canonical:SETUP-00#5.3 | `COMPLETE` | A checkpoint is validated against schemas, Git state, inventory, quality evidence, and secrets. |
| REQ-0022 | canonical:SETUP-00#5.4 | `COMPLETE` | Secret redaction is available and documented to its real scope. |
| REQ-0023 | canonical:SETUP-00#5.5 | `COMPLETE` | The tooling is standard-library only and portable across Windows and Unix-like checkouts. |
| REQ-0024 | canonical:SETUP-00#6.1 | `COMPLETE` | Every checkpoint carries status, handoff, run metadata, state, plan, decisions, commands, file inventory, tests, quality, provenance, diff summary, risks, and next action. |
| REQ-0025 | canonical:SETUP-00#6.2 | `COMPLETE` | `LATEST.md` points textually to the last checkpoint accepted by validation. |
| REQ-0026 | canonical:SETUP-00#6.3 | `COMPLETE` | The file inventory matches the real change set, with bound content hashes. |
| REQ-0027 | canonical:SETUP-00#6.4 | `COMPLETE` | Provenance is complete and `trainingAllowed` defaults to `false`. |
| REQ-0028 | canonical:SETUP-00#6.5 | `COMPLETE` | A quality `PASS` carries resolvable evidence. |
| REQ-0029 | canonical:SETUP-00#6.6 | `COMPLETE` | Handoff-ready and terminal checkpoints are anchored to an immutable namespaced tag. |
| REQ-0030 | canonical:SETUP-00#7.1 | `COMPLETE` | A cold-start continuation prompt exists and depends only on checked-in files. |
| REQ-0031 | canonical:SETUP-00#7.2 | `COMPLETE` | Cold-start validation is executed and recorded truthfully, including a blocked attempt. |
| REQ-0032 | canonical:SETUP-00#7.3 | `COMPLETE` | Cross-tool validation state is structured and explicit. |
| REQ-0033 | canonical:SETUP-00#7.4 | `COMPLETE` | A sealed checkpoint can be validated from a detached checkout of its own tag. |
| REQ-0034 | canonical:SETUP-00#7.5 | `COMPLETE` | The handoff is executable by another tool without the producing session. |
| REQ-0035 | canonical:SETUP-00#7b.1 | `COMPLETE` | Every requirement of a delivery exists in a versioned matrix before implementation. |
| REQ-0036 | canonical:SETUP-00#7b.2 | `COMPLETE` | A Test Rework / Green Keeper role forbids shipping anything red and records every cycle. |
| REQ-0037 | canonical:SETUP-00#7b.3 | `COMPLETE` | A Delivery Completeness Validator audits the matrix before handoff and may not implement. |
| REQ-0038 | canonical:SETUP-00#7b.4 | `COMPLETE` | `GREEN_KEEPER_GATE` and `DELIVERY_COMPLETENESS_GATE` are preconditions of `READY_FOR_REVIEW`. |
| REQ-0039 | canonical:SETUP-00#7b.5 | `COMPLETE` | Readiness and blockage can never be claimed together. |
| REQ-0040 | canonical:SETUP-00#7b.6 | `COMPLETE` | Every operation attempt is recorded, including a refusal decided before execution. |
| REQ-0041 | canonical:SETUP-00#7b.7 | `COMPLETE` | Every recorded command is reproducible from its declared working directory. |
| REQ-0042 | canonical:SETUP-00#7b.8 | `COMPLETE` | The mandatory delivery order is stated in full in every governing document and both adapters. |
| REQ-0043 | canonical:SETUP-00#7c.1 | `COMPLETE` | The project keeps an organizational engineering memory of confirmed failures. |
| REQ-0044 | canonical:SETUP-00#7c.2 | `COMPLETE` | A lesson is `GUARDED` only when an automated control prevents recurrence. |
| REQ-0045 | canonical:SETUP-00#7c.3 | `COMPLETE` | A repeat increments recurrence, and a repeat against a guardrail is a `GUARDRAIL_FAILURE`. |
| REQ-0046 | canonical:SETUP-00#7c.4 | `COMPLETE` | A mandatory preflight selects the lessons that constrain each Gate. |
| REQ-0047 | canonical:SETUP-00#7c.5 | `COMPLETE` | Applicable lessons become requirements whose absence blocks completeness. |
| REQ-0048 | canonical:SETUP-00#7c.6 | `COMPLETE` | Lesson candidates can be extracted from recorded delivery evidence, never above `OBSERVED`. |
| REQ-0049 | canonical:SETUP-00#7c.7 | `COMPLETE` | External validation is grouped into milestones `M0` to `M6`. |
| REQ-0050 | canonical:SETUP-00#7c.8 | `COMPLETE` | An internal verdict is never described as independent external validation. |
| REQ-0051 | canonical:SETUP-00#7c.9 | `COMPLETE` | An extraordinary audit requires a recorded trigger. |
| REQ-0052 | canonical:SETUP-00#7c.10 | `COMPLETE` | Every completed Gate produces a retrospective. |
| REQ-0053 | canonical:SETUP-00#7d.1 | `COMPLETE` | One promotion invariant governs every positive terminal status, not only `READY_FOR_REVIEW`. |
| REQ-0054 | canonical:SETUP-00#7d.2 | `COMPLETE` | The mandatory quality gate set is a closed machine-readable registry that an invocation cannot narrow. |
| REQ-0055 | canonical:SETUP-00#7d.3 | `COMPLETE` | The expected requirement set is derived from canonical sources and compared exactly with the declared set. |
| REQ-0056 | canonical:SETUP-00#7d.4 | `PARTIAL` | An external milestone PASS is derived from an audit attestation authored by another sealed checkpoint. |
| REQ-0057 | canonical:SETUP-00#7d.5 | `COMPLETE` | A derived artifact carries a fingerprint of its inputs, and staleness is decided by recomputation. |
| REQ-0058 | canonical:SETUP-00#7d.6 | `COMPLETE` | Every lesson control, evidence path and provenance locator is resolved against the repository. |
| REQ-0059 | canonical:SETUP-00#7d.7 | `COMPLETE` | Every `GUARDED` lesson names a registered guardrail, and guardrail effectiveness is measured. |
| REQ-0060 | canonical:SETUP-00#7d.8 | `PARTIAL` | Sealed checkpoints are anchored by a hash-linked chain over tag, commit and tree. |
| REQ-0061 | canonical:SETUP-00#7d.9 | `COMPLETE` | Every count used as evidence is derived once and verified wherever a report states it. |
| REQ-0062 | canonical:SETUP-00#7d.10 | `COMPLETE` | Sealing is monotonic and post-commit, and every recorded command binds its declared inputs by content. |
| REQ-0063 | canonical:SETUP-00#7d.11 | `COMPLETE` | A milestone delivery carries an internal Red Team and an internal mirror audit, and neither is recorded as external validation. |
| REQ-0064 | canonical:SETUP-00#7d.12 | `COMPLETE` | Every finding of an independent audit is closed before the corrective delivery is offered. |
| REQ-0065 | canonical:SETUP-00#8.1 | `COMPLETE` | An independent review is recorded. |
| REQ-0066 | canonical:SETUP-00#8.2 | `COMPLETE` | An adversarial Red Team is recorded. |
| REQ-0067 | canonical:SETUP-00#8.3 | `COMPLETE` | `GATE_PASS` is granted only by a run independent of the implementer. |
| REQ-0068 | canonical:SETUP-00#9.1 | `COMPLETE` | No Gate 0 or later runtime is implemented during SETUP-00. |
| REQ-0069 | canonical:SETUP-00#9.2 | `COMPLETE` | Documentation is maintained continuously rather than reconstructed at the end. |
| REQ-0070 | canonical:SETUP-00#9.3 | `COMPLETE` | No secret, credential, or private chain-of-thought is stored. |
| REQ-0071 | canonical:SETUP-00#9.4 | `COMPLETE` | Gate advancement requires explicit authorization and a passing previous Gate. |
