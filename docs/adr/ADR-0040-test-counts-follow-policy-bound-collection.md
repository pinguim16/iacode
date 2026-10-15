# ADR-0040 — Test counts follow policy-bound collection

Status: Accepted
Date: 2026-10-15
Owners: GATE 4 — Quality Engine assurance

## Context

The evaluator runner collected 85 regression cases (79 unit and 6 integration), while the static
counter declared 90. Five test-shaped files are input projects for real quality scenarios. Its
existing conftest excludes fixtures/**, including intentionally failing inputs, but the static
counter and evidence resolver did not respect that distinction. Three inputs already existed in
the sealed predecessor; two were added by this correction. Historical seals remain unchanged.

## Decision

Declare input repositories with reasons in the canonical suite registry. The shared source-file
boundary requires those exclusions to equal pytest's literal collection exclusions; an unknown,
escaped, root-wide or runner-collected exclusion is refused. Count derivation and evidence
resolution use that same boundary. No invocation may choose exclusions. No regression test,
mandatory quality gate, functional fixture execution or promotion rule is removed.

## Consequences

The platform count describes actual collected regression cases, not test-shaped project inputs.
Live fixture scenarios continue to require their own execution evidence. The counter's original
overstatement is retained in the finding and earlier seals, not silently rewritten. Positive and
negative tests exercise counts, evidence resolution and policy/runner disagreement.
