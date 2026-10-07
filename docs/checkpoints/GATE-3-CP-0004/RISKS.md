# Risks — M1 fresh-session re-audit

## Carried into the audit

- `R-G2-009` remains HIGH until the owner rotates the credential exposed outside the repository.
  The audit will not read, print, or rotate it.
- `R-G3-001` remains an accepted local architectural risk only if all ten controls and the live
  adversarial probe still hold.
- `R-G3-009` remains MEDIUM: the configured model previously made valid sandboxed tool requests but
  did not finish the bounded coding task.
- `R-G3-010` remains MEDIUM: pre-push discipline is not itself an automated enforcement point.

## Audit risks

- A passing local-object-store check can conceal an unpublished commit. Published transport clones
  are therefore mandatory evidence.
- A long full verification or live provider call may fail for an external reason. Such a result is
  recorded truthfully and is not converted into PASS.
- The audit harness is repository code from the earlier audit. Null controls and direct artifact
  checks are required before its refusals count as defended attacks.

## Finding returned to implementation

- `M1-F-004` — **CRITICAL**, OPEN: the pinned frontend graph has two Critical and four High npm
  advisories. The complete verification failed only `dependency-scan`, and an immediate repetition
  reached both advisory sources and reproduced the npm result. No risk acceptance can satisfy the
  frozen AM-17 criterion; dependencies and the lock graph must be corrected in `GATE-3-CP-0005`.

## Criteria left unverified by the stop condition

The later cross-gate live repetition, dedicated configured-model and forged-result probes, audit
Red Team and clean-clone run did not execute after `M1-F-004` reproduced. This is a bounded audit
risk recorded as `UNVERIFIED`, not evidence that those behaviours regressed and not a PASS claim.
