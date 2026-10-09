# Final Report — GATE-3-CP-0006

## Status

`MILESTONE_INDEPENDENT_AUDIT_PASS` for M1, derived from this fresh-session attestation after the
audit checkpoint is sealed. `MILESTONE_EXTERNAL_PASS` is not claimed. The immutable subject is
`GATE-3-CP-0005` at `3ef2bf77ddbddd378d35f5c4d32f2d90d42fc97d`; the review is `APPROVED`.

## Environment

Windows 11, PowerShell, Python 3.13, Git and Docker Desktop. Branch `main`; authorised remote
`https://github.com/pinguim16/iacode.git`. The subject tag, local starting `HEAD` and remote main all
identified the exact subject commit before the audit wrote anything.

## Tool / Model / Effort

Codex desktop application, OpenAI, GPT-5. Effort is not exposed and is recorded as such. This is a
fresh session with no memory of the implementing run. No different tool/provider is exposed here,
so the mechanism is `FRESH_SESSION_INDEPENDENT_AUDIT` with
`crossToolValidation=NOT_AVAILABLE`.

## Deliverables

- `REVIEW-REPORT.md`, `MILESTONE-REPORT.md` and this final report.
- `FINAL-M1-AUDIT-MATRIX.json` and `.md`: all 32 frozen criteria and their evidence.
- `AUDIT-EXECUTIONS.json`, `FINDINGS.json`, `TESTS.json` and `COUNTS.json`.
- Published-history, dependency, full-verification, clean-clone, configured-model, cross-Gate,
  forged-result, SSE, documentation/memory and R-G3-001 reports.
- `M1-INTERNAL-RED-TEAM.json` and `RED-TEAM-REPORT.md`: nineteen attacks over a valid control.
- `.iacode/attestations/M1-CP-0006.json` and the audit-only reproducible harnesses.

## Files Created

This audit checkpoint and its harness, the M1 attestation, and the post-seal review archive outside
the Git history. `FILES.json` is the authoritative per-path inventory and reason list.

## Files Modified

`.iacode/anchors/checkpoint-chain.json` gains the successor-owned anchor for the sealed subject;
`docs/checkpoints/LATEST.md` points to this audit. No product, test, prompt, policy, sealed
checkpoint or historical tag changes.

## Validation

Every sealed M1 checkpoint validates locally and from a transport clone of the authorised remote.
Named historical evidence is reachable from published refs. The non-fast clean-clone verification
passed all 32 stages. Both advisory sources scanned successfully with zero Critical and zero High.
The 198 derived requirements are complete with full evidence coverage. Green Keeper, Delivery
Completeness Validator, internal Red Team, Milestone Closure Auditor, checkpoint validation,
integrity and secret scans are recorded in this checkpoint.

## Tests

The canonical counted suites discovered 1,551 cases and passed all 1,551, deduplicated by physical
execution. The complete verification additionally exercised startup, integration, infrastructure,
smoke, Model Gateway, Agent Runtime, durability, cancellation, deadline, Sandbox integration and
coding scenarios, timeout, recovery, forged-result origin, backup, dependency scan, restart,
dependency failure and fresh installation. The dedicated multi-page terminal SSE regression passed.

## Red Team

`RED_TEAM_PASS`: nineteen of nineteen fresh milestone attacks defended, zero escaped, null-mutation
control `VALID`. The battery covered host execution, secrets, engine socket, traversal/symlink and
cross-run isolation, policy escalation, untrusted engine arguments, Git remote, network, provider
bypass, cancellation, deadline, integrity rewrite, remote drift, dependency false PASS, forged
ToolResult, published-evidence false PASS, timeout bypass and attestation forgery.

The first collection defended every attack but read the canonical null control from the wrong JSON
location. Its hash and cause are preserved. Only the audit reader changed; the entire battery was
then repeated.

## Known Risks

See `RISKS.md`. Session independence is not cross-tool independence; attestation trust is structural,
not cryptographic; R-G3-001 remains an accepted local controller capability; live advisory/provider
evidence is time-bound; and `M1-F-005` is a LOW, non-blocking diagnostic budget finding.

## Remaining Work

None for the M1 audit verdict. A later implementing checkpoint may make the broad cross-Gate
diagnostic prompt terminate more deterministically. The auditor did not implement that correction.

## Handoff Readiness

Ready after canonical finalization, commit, seal, push, clean post-commit validation, milestone
derivation and final review-archive validation. Those post-seal actions do not rewrite the audited
subject or the sealed audit checkpoint.

## Next Gate

Gate 4 is eligible only after explicit owner authorisation and a new pre-Gate checkpoint. It was not
started in this run.

## Evidence

| Claim | Evidence |
|---|---|
| Published immutable subject | `SEALED-SUBJECTS.json`, `SEALED-SUBJECTS-PUBLISHED.json`, `REMOTE-PUBLISHED-OBJECTS.json` |
| Full operational result | `VERIFICATION-REPORT.json`, `CLEAN-CLONE-REPORT.json` |
| Configured-model and tool path | `LIVE-CODING-RUN.json`, `TOOL-RESULT-ORIGIN.json` |
| Sandbox boundary and R-G3-001 | `M1-INTERNAL-RED-TEAM.json`, `R-G3-001-REVIEW.json` |
| Requirements and closure | `REQUIREMENTS-MATRIX.json`, `COMPLETENESS-REPORT.json`, `FINAL-M1-AUDIT-MATRIX.json` |
| Verdict mechanism | `.iacode/attestations/M1-CP-0006.json`, `MILESTONE-REPORT.md` |
| Review archive | `artifacts/review/GATE-3-CP-0006-review.zip` and adjacent validation JSON |

## Review bundle

After publication the final archive is generated at `artifacts/review/GATE-3-CP-0006-review.zip`,
with a SHA-256 sidecar and adjacent `GATE-3-CP-0006-review-validation.json`. Validation covers CRC,
safe and unique paths, embedded checksums, manifest identity and hashes, mandatory evidence and the
canonical credential patterns.
