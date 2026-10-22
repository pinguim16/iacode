# ADR-0063 — Historical review producers inherit only process-scoped Git path handling

Status: Accepted
Date: 2026-10-22
Owners: GATE 7 — corrective M2 assurance and immutable historical review transport

## Context

The complete runtime-v3 quality cycle rejected historical review declarations. Actual same-depth
diagnostics identify two distinct Windows boundaries: cloning materializes long observation names,
then older immutable producers read long SHA:path expressions. ADR-0058 handled the current object
reader, but its per-command setting did not cover clone/checkout or travel into older producers.

Original failures remain in CP0003 published-green-keeper/run-0003 and history-diagnostics. The
first scoped clone/checkout correction succeeds, and CP0001's own producer reproduces its original
declaration. Gate5 and Gate6 then fail in their original readers with Filename too long. Rewriting
those historical readers or accepting a failed reconstruction would invalidate the audit boundary.

## Decision

Apply core.longpaths=true before Git's clone and checkout subcommands through per-command -c.
Supply the immutable Python producer a fresh environment dictionary containing one appended
runtime Git configuration pair for the same key. Preserve inherited pairs and every unrelated
environment value. Never modify os.environ, a repository/global configuration file, historical
source, an archive member, a declaration, a tag or a promotion rule.

Use Git's documented GIT_CONFIG_COUNT / GIT_CONFIG_KEY_n / GIT_CONFIG_VALUE_n mechanism. Validate
the inherited decimal count and complete pairs before launch; refuse malformed input and more
than the bounded adapter capacity rather than discarding configuration. An explicit Git -c still
takes precedence. This is a process environment for the exact transported producer, not a general
auditor bypass or a setting for other applications.

The mechanism and precedence are described in the
[official Git configuration documentation](https://git-scm.com/docs/git-config#ENVIRONMENT).

## Alternatives Considered

- Global or shared repository changes: outside authority and unnecessary.
- Rename or omit published observations: breaks immutable bytes and complete membership.
- Rewrite an old producer or substitute the current producer: no longer audits the sealed subject.
- Shorten only this workstation's temporary path: does not preserve legitimate transported paths.
- Temporarily mutate the parent environment: leaks scope to unrelated concurrent children.

## Consequences

The original subject-carried producer executes unchanged with a narrowly scoped Git path setting.
No positive result follows from the setting itself. Actual clone, detached checkout, both producer
exits, archive identity, original declaration comparison and observed owner removal must still pass.
Genuine bad references, missing producers and malformed inherited configuration remain failures.

## Validation and Risks

Real short-HEAD null and long-path materialization controls, exact binary object reads, explicit
override removal, inherited-pair preservation, malformed-input refusal and unchanged configuration
controls are required. Minimal transport fixtures deliberately lack a review producer and remain
FAIL as whole reconstructions; they never substitute for actual historical archive proof.

The actual Gate5, Gate6 and Gate7 declarations must be rebuilt through their original producers
at the failing temporary depth. Complete current quality, functional assurance and internal closure
must be rerun before sealing. No independent M2 verdict is granted by this decision.

## Reversal Strategy

Remove or replace the adapter only with equivalent real transported/historical byte and failure
proof. Preserve every failed attempt and never rewrite a historical seal to accommodate the host.

## Related Artifacts

[ADR-0058](ADR-0058-immutable-review-git-reads-use-child-scoped-long-path-handling.md);
[review transport](../../scripts/development-ledger/review_bundle.py);
[actual boundary controls](../../tests/test_m2_history_transport.py);
[diagnostic originals](../checkpoints/GATE-7-CP-0003/history-diagnostics/).
