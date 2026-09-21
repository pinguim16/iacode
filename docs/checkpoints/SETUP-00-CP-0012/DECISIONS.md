# Decisions

## D1 — An empty applicable set is a first-class outcome, not a failure and not a pass

The role contract already prescribed `NOT_APPLICABLE` and the report schema already permitted it, so
no new vocabulary was invented. What was missing was a check that could emit one. A dimension whose
canonically derived set is empty now reports `NOT_APPLICABLE`; a dimension whose sources name items
the delivery does not satisfy stays `FAIL`.

Alternative considered and rejected: scoping the mirror requirement in the validator to the
checkpoints it was written for. That would have removed the control from every delivery that
corrects no audit instead of making it correct, and the first Gate 0 delivery would have shipped
without a mirror at all.

Alternative considered and rejected: deriving the expected findings from what the checkpoint claims
to close rather than from the registry. That is the shrinkable-denominator shape the `M0` audit of
`SETUP-00-CP-0006` already found once.

## D2 — `NOT_APPLICABLE` justifies itself, or it is a failure of the auditor

Making the state reachable opens the opposite escape: declaring a dimension inapplicable instead of
satisfying it. Four things prevent that, and they are deliberately layered:

- the outcome object cannot be constructed without a reason and a derivation source;
- recording one with a non-zero count, or without a justification, is written down as `FAIL` by the
  auditor itself;
- the report schema carries the fields only from version `1.1.0`, and a `1.0.0` report may not
  record an inapplicable dimension at all;
- checkpoint validation re-derives the registry-bound dimensions from the canonical sources, so a
  well-formed declaration over work that exists is still refused.

## D3 — The verdict does not rewrite the individual status

`NOT_APPLICABLE` is never mapped to `PASS` in the artifact. The report fails only on a `FAIL`, and
`passed + failed + notApplicable` must equal the total, which is checked by validation. A reader of
a sealed report can therefore see which dimensions were judged and which had nothing to judge.

## D4 — The audit is registered even though registration is not the fix

`NEXT.md` of the sealed audit requires it, and registration is what binds `CP11-F-001` and the
twelve mandatory attacks of the sealed battery into this delivery's expected requirement set, so the
closure cannot be self-declared. It is recorded here, as the audit itself asked, that registration
makes *this* delivery's mirror satisfiable and is not the repair: the repair is proven in the states
where there is nothing to close at all.

## D5 — The sealed reports are parsed as they were written

Registering the third audit was impossible with the shipped parsers: its findings are rendered with
quoted identifiers and its battery in one table with a category column, and both parsers read the
sealed reports as empty. That is the same confusion in another place — an unreadable report looked
like a report with nothing in it — so the parsers were repaired rather than the registry weakened.

`parse_findings` is bounded to the report's own `## Findings` section, because an audit also
verifies its predecessor's findings under the same heading shape and those were closed by an earlier
delivery. `parse_attacks` reads a table by its header and only when the first column is an attack
identifier, so a positive control, a guardrail probe and a scenario log are not read as attacks. The
parses of the two earlier sealed audits are asserted unchanged, because the expected requirement set
of sealed checkpoints depends on them.

## D6 — The twelve mandatory attacks of the sealed battery are executed, not credited

Most of them name failure classes this battery already attacks. Each is executed again under the
identifier the sealed report uses, against its own fixture, and where the mutation is one an
existing attack performs, the alias records which one. Two of them isolate mutations this battery
did not have and are written out in full.

## D7 — A simulation runs the control it reports

`promotion_fixture` now executes `m0_mirror_audit.py`. The internal Red Team of the fixture delivery
is still modelled, because executing that battery would mean building a fixture inside a fixture,
and the simulation declares that in `artifactProvenance` instead of implying it. What is executed
and what is modelled is stated in the artifact.

## D8 — The Gate transition is proven with a synthetic specification

A Gate's expected requirement set is derived from its specification document, so proving that the
first delivery of the next Gate can be handed over needs one. Writing a real Gate 0 specification
would be starting Gate 0, which is not authorized. The fixture declares a synthetic specification
inside the disposable repository, about the delivery machinery and not about what the Gate would
build, and the simulation states that its subject is the state machine.

## D9 — The language rule belongs to the Claude adapter, not to the artifacts

`CLAUDE.md` records that every response to the user is written in Brazilian Portuguese. The
repository artifacts stay in English: they are the tool-neutral contract both adapters read and the
tooling parses them, and the rule explicitly does not license translating a sealed checkpoint or any
other historical artifact.

## D10 — A delivery may declare requirements of its own

`MIR-009` compared the *total* number of declared requirements with the derived expected set, so a
delivery that declared any requirement of its own failed the mirror. The matrix schema defines a
`local:` kind for exactly that, and the exact set comparison already refuses an omitted, substituted
or duplicated anchor, so nothing about the denominator depended on the equality.

The control now compares the *anchored* rows with the expected set, which is the set the derivation
governs, and the completeness report carries that count as `anchoredRequirements`. This is the same
shape as `CP11-F-001` in a neighbouring control — a legitimate state refused by a check that was
stricter than the policy it enforces — and it was found by this delivery's own mirror audit refusing
this delivery's own requirement register.

The denominator is not weakened: an anchored row that goes missing is still blocking, a local row
still needs resolvable evidence, and a local row still cannot stand in for an anchor.
`LocalRequirementDeclarationTests` executes all four cases.

## D11 — The recurrence is escalated, not repaired quietly

`LSN-0024` (a control is finished only when its positive path has been executed) and `LSN-0029` (a
required protocol transition must never turn a mandatory gate red) were both `GUARDED` and both
classes recurred. Each carries a `GUARDRAIL_FAILURE` naming what the control missed, resolved in
this checkpoint by a new control rather than by deleting the occurrence: `GRD-0031` binds a
simulation's artifact to the tool's output, and `GRD-0032` executes the transition into the next
Gate.
