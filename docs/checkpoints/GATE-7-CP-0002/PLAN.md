# Plan — M2 fresh-session independent milestone audit

Audit checkpoint `GATE-7-CP-0002`. Immutable subject: `GATE-7-CP-0001`, canonical tag
`refs/tags/iacode-checkpoints/GATE-7-CP-0001`, sealed commit
`823cf164c6931dab7f957c92721ded7a916655bd`, offered as `READY_FOR_REVIEW`.

This is an audit-only run over accumulated Gates 4–7. It will not implement corrections, change
product code/tests/policies, rewrite the subject, move a tag, reduce a denominator, start Gate 8,
or relabel internal evidence as independent. Allowed writes are this later audit checkpoint, its
audit evidence, the subject anchor owed by a successor, `LATEST.md`, and an attestation only if
every passing precondition is independently demonstrated.

## Independence

- Role: M2 independent auditor and independent Red Team.
- Tool: Codex CLI `0.163.0-alpha.10.2`.
- Provider/model: OpenAI / GPT-5 as exposed by the session; subversion and effort are not exposed.
- Mechanism: `FRESH_SESSION_INDEPENDENT_AUDIT`.
- Cross-tool status: `NOT_AVAILABLE`; this run can never grant `MILESTONE_EXTERNAL_PASS`.
- The owner states this is an isolated session without inherited implementation conversation.

## Frozen denominator and criteria

`FROZEN-M2-AUDIT-CRITERIA.json` fixes 45 criteria before substantive execution. The canonical
requirements denominator is independently derived from the checked registry/checklist pair for
each Gate: 105 Gate 4 + 50 Gate 5 + 51 Gate 6 + 48 Gate 7 = 254 Gate requirements, plus every
applicable `LESSON-REQ-` row (150 at preflight), for 404 accumulated rows. The audit checkpoint's
canonical Gate 7 matrix remains intact; `M2-AUDIT-REQUIREMENTS.json` is an additional milestone
denominator and does not replace, narrow or edit it.

## Execution order

1. Preserve entry attempts, verify subject identity/publication/tag, anchor the sealed subject, and
   derive the 404-row accumulated denominator.
2. Review architecture, ADRs, implementation, requirements, evidence, provenance, rights,
   security, isolation, documentation, risks and cross-Gate integration.
3. Reconstruct `G4-F-004` independently: reproduce the historical stale declaration, prove the
   corrective subject, and reconstruct the final M2 bundle twice from public detached sources.
4. Snapshot pre-existing infrastructure identities, use only resources demonstrably owned by this
   run, and execute one complete non-fast verifier against the exact published subject. Preserve
   the integral result; no partial rerun may supersede it.
5. Execute dedicated real functional proofs for the Gate 4 quality flow, Gate 5 installed
   CLI/editor boundary, Gate 6 experience lifecycle, Gate 7 knowledge lifecycle, and their
   cross-Gate preservation where the canonical harness exposes them.
6. Execute an independent Red Team over a valid clean/null control, including false-PASS,
   authentication, workspace/project isolation, rights laundering, secret ingress, corruption,
   stale citation, retention/resurrection, transport and attestation attacks.
7. Execute a fresh public no-credential clone validation, full verification, publication/history
   probes, dependency/security controls, and exact review-package comparison.
8. Populate the frozen matrix and findings, run the audit checkpoint's Green Keeper,
   completeness, internal controls, inventory, secret scan and checkpoint validation.
9. Derive the verdict. Write an attestation only if all 45 criteria pass with no blocker; otherwise
   close truthfully as `REWORK_REQUIRED` or `BLOCKED`, without correcting the subject.

## Continuation and stop rules

- A Critical/High finding, escaped mandatory attack, guardrail recurrence, incomplete proof or red
  mandatory gate blocks PASS. Safe read-only and isolated tests continue so the final report is as
  complete as possible, as explicitly requested by the owner.
- A need for broader permissions, a new installation, a Docker/WSL/application restart, global
  configuration change, destructive cleanup, third-party mutation or unowned resource use stops
  that path and is reported; it is not silently bypassed.
- Unexpected Git/STATE divergence triggers the canonical divergence protocol. The known prior
  untracked reports remain a declared entry condition and are never deleted or absorbed silently.
- A failed command and its original output remain evidence. A later success cannot erase it.
- Gate 8 is never started, regardless of verdict.
