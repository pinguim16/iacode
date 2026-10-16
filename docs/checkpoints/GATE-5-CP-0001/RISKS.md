# Risks

## Current incomplete-attempt residue — never silently cleaned

The v1 full invocation was intentionally stopped before its mandatory root suite completed; it is
not a PASS. Cmd-0238 then observes failed Git clone cleanup because a real pack index is ReadOnly
(attribute value 33 = ReadOnly + Archive). Cmd-0240 reproduces the causal failure; cmd-0241 passes
the corrected readonly-aware manager on a fresh owned fixture. That manager never accepts an
existing target; the native-profile process/lock helper is unchanged.

Environment policy refused direct removal of
`C:\Users\cesar\AppData\Local\Temp\iacode-gate5-full-verification-cprc_a8t`.
Do not retry that directory through another tool/API, do not claim it removed and do not pass it
to the new manager. It remains a responsible-owner manual cleanup item. A read-only observation
confirms its ignored `repository/infra/compose/.env` copy remains; no value was read or recorded.
The original workspace configuration was not changed. The two older Gate 4 refused directories
remain equally out of bounds. No broader temporary-directory cleanup is authorized.

The source/status coupling and cleanup-manager defect are corrected with actual regressions;
the new immutable runtime subject and complete non-fast assurance are still required. No new full
verifier is active until its subsequent publication/invocation is recorded.

## Current status (supersedes historical pending statements below)

Cmd-0199 supplies the complete real desktop proof, including actual two-host recovery, successful
unittest in sandbox, identical client truth, quality evidence/reproduction, loss reconciliation,
RUNNING task/quality cancellation and repeat, local-only SIGINT, tamper refusal and complete cleanup.
Cmd-0200 preserves it exactly. All 21 recorded findings are causally closed, and cmd-0206 passes
complete lint. Current live proof is still dirty-source evidence, not the immutable full verifier.
The runtime subject is now published as 76e659e5cfb0db1bf7dd50c6d3a04ec101e9fce0 and its full
non-fast verifier is active in an isolated exact detached clone. Source remains frozen at
22fa32a378ae64ea96adf9b06fe5eee865a11a96ef3b3f0ec5b80311bdc1ec3d (cmd-0229).
All 22 actual findings are causally closed; the last one preserves raw evidence across Git transport.
The completed verifier, all fourteen mandatory Green Keeper gates, completeness, internal Red Team/null
control, mirror and canonical seal/publication are still required. No terminal PASS is claimed.

The earlier explicit review obligations now have scoped controls: async candidate/disposal
ownership, late-read staleness, cursor identity, cancellation without new uploads, pending identity
preservation, known capability data refusal and deep signed JSON. Cmd-0146 passes all 35 complete
client decisions. Subject-versioned root lint/ignore scope is implemented and covered. None of
this substitutes for the full current live workflow, verifier or ordered internal assurance.

- Gate 5 is incomplete and unsealed. Actual CLI/native installation passed; full live acceptance
  remains pending. Cmd-0128 additionally proves owned shared storage and complete removal.
- The 165-case API observation at cmd-0131 is not a current
  frozen-delivery verdict. The API must rebuild before actual cross-process acceptance.
- The complete 35-case Node decision suite is canonically registered and mandatory. It cannot
  replace the inherited full verifier or actual native/provider acceptance.
- G5-INT-004 is causally repaired with registered GRD-0121 and GUARDED LSN-0118; complete cross-client
  proof is still pending. G5-INT-011 requires actual persistent second-host recovery.
- Authentication has a single-user, trusted-local-OS scope. HMAC authenticates but does not encrypt;
  clients must reject non-loopback endpoints. Legacy development mode is not secure desktop mode.
- API/worker rendered gateway bounds share a helper and scoped unit controls; actual hardened
  worker/provider integration still needs proof.
- Snapshot path edge cases (dot names, Unicode format characters and platform-special characters)
  have API/client parity controls. Source/BOM bytes, traversal and links have Node controls;
  actual stable persistence/retry/rights/lookup passed, but tamper and full live acceptance remain.
- Source snapshots intentionally exclude private/control/dependency/cache paths and are limited
  to bounded regular UTF-8 files. The canonical API scan fails closed on credential-shaped content,
  including reviewed source-like output; no detector proves absence of unrecognized secrets.
- Snapshot object/DB writes are not a distributed transaction. Failure cannot authorize partial
  bytes; deterministic retry can recover the pointer, while orphan cleanup must be proven in an
  owned namespace and documented.
- No operational profile, global editor installation, unrelated container, old refused cleanup
  directory, Git history or future-Gate reservation may be changed for test convenience.
