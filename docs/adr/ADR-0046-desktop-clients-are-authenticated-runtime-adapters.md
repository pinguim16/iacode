# ADR-0046 — Desktop clients are authenticated runtime adapters

- Status: Accepted
- Gate: GATE 5

## Context

Gate 5 must expose the delivered runtime, sandbox and quality engine without moving execution to
the host or granting the UI verdict authority. The existing loopback development API is not an
authenticated desktop transport. The editor must not accept endpoints or credentials from a
workspace. CLI and editor behavior must not diverge.

## Decision

Use one dependency-free Node client core, packaged with both the standalone CLI and the VSIX.
Use native editor commands, a status/tree view and plain-text result documents; no webview,
command URI, shell broker or project-supplied executable is needed. The minimum supported CLI
runtime is the repository's pinned Node 22.23.2; editor compatibility is exercised with the actual
installed Extension Host and declared engine floor before acceptance.

A shared versioned JSON protocol declares closed operations, field types and byte bounds. The
desktop adapter dispatches to existing API handlers/services, not a second execution engine.
Snapshot ingress creates only the existing authorized snapshot artifact. Mutation intent binds
the exact approved inputs; domain idempotency keys remain stable across uncertain delivery.

Desktop clients accept only an explicit numeric-loopback endpoint. A secret configured out of
band authenticates HMAC-SHA256 request bytes and response bytes, with per-request identity,
timestamp and bounded replay refusal. The secret itself is never sent in a header or process
argument. A separately configured expiration bounds its lifetime. Responses are authenticated
before parsing or presentation; redirects are never followed. Requests and buffered desktop
responses have finite byte and time limits. The UI never changes remote state on a read retry.

In hardened desktop mode every domain API route requires authentication, not only the desktop
facade. The orchestrator supplies an authenticated HTTP transport to the existing gateway client;
the agent-runtime domain gains no provider credential, execution authority or alternate model path.
Health/metrics remain operational probes, not domain access. Legacy development mode is retained
explicitly for the existing local web workflow and is refused by desktop clients. Enabling hardened
mode cannot silently retain unauthenticated alternate domain routes; its web compatibility and
operator setup must be explicit in the runbook and tested.

Editor connection metadata is extension-owned state and its credential uses SecretStorage.
Mutations recheck workspace trust, root, connection generation and exact approval after the
confirmation returns. Runtime text remains plain text and can never supply a command or path.

## Evidence

The Gate 4 seal and Gate 5 baseline are recorded in
`docs/checkpoints/GATE-5-CP-0001/BASELINE.md`; the 50 canonical requirements and 115 lessons precede
implementation. The VS Code API documents native [commands](https://code.visualstudio.com/api/extension-guides/command),
[tree views](https://code.visualstudio.com/api/extension-guides/tree-view),
[runtime workspace trust checks](https://code.visualstudio.com/api/extension-guides/workspace-trust)
and [encrypted SecretStorage](https://code.visualstudio.com/api/references/vscode-api#SecretStorage).
[Extension testing](https://code.visualstudio.com/api/working-with-extensions/testing-extension)
supports real Extension Host runs; trusted and untrusted states require separate runs.
These references support API choices, not a claim that this implementation has passed them.

## Alternatives

- Webview plus a child-process broker: more message and process boundaries without a product need.
- Direct unauthenticated development API calls: insufficient endpoint/replay protection.
- Two independent clients or a second runtime: duplicate policy and lifecycle semantics.
- Shipping third-party runtime SDKs: avoidable dependency and packaging surface at this scope.

## Consequences and risks

No generated command runs on the host and no patch is automatically applied. Clients need an
explicit authenticated runtime setup. This is a single-user local capability, not multi-tenant
authorization, TLS, remote deployment or protection against a compromised OS account/extension
host. HMAC does not encrypt local traffic. Clock skew, token expiration, uncertain mutations,
replay bounds and snapshot path/content races require positive and negative execution evidence.
No model output, credential or private reasoning is made trainable.

## Reversal

Keep runtime APIs and the versioned facade separate. A later transport or UI can replace this
adapter only with a new protocol/ADR and compatibility tests; sealed predecessors remain intact.
Remove the clients and disable hardened mode explicitly to recover the original development
workflow, without changing stored run or quality semantics.

## Related artifacts

- `docs/GATE-5-CHECKLIST.md`
- `docs/checkpoints/GATE-5-CP-0001/PLAN.md`
- `docs/adr/ADR-0037-intermediate-gates-use-internal-closure.md`
