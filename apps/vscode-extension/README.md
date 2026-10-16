# IACode VS Code extension

Native commands and an Explorer status view over the governed local runtime. No webview, shell
broker, generated host execution, automatic patch application or client-authored verdict exists.
Gate 5 delivery acceptance remains in `docs/checkpoints/LATEST.md`.

Build with `python scripts/iacode/build_clients.py`, then **Extensions: Install from VSIX** and
select `artifacts/clients/iacode-0.1.0.vsix`. Requires desktop VS Code **1.138.0+**; no marketplace
publication or repository build output is needed. The embedded Node runtime belongs to VS Code,
not the standalone CLI's Node installation. Runtime dependencies are built-ins only; the package
contains the exact shared core and protocol.

Use **IACode: Configure Local Runtime**. Enter an explicit numeric-loopback HTTP endpoint and the
expiring desktop credential. Both are extension-owned SecretStorage configuration; the credential
is never a workspace setting or process argument. The exported operator configuration API only
configures a connection: it cannot approve/upload/start/cancel a task. No workspace/environment
configuration is automatically accepted. Wrong, expired, legacy or contract-mismatched endpoints
fail closed.

Open exactly one trusted local folder, then:

1. **Preview Workspace Inventory**: read the bounded source inventory; nothing is uploaded.
2. **Approve Workspace Snapshot**: review the plaintext inventory/digest/root/runtime and explicitly
   select **Approve exact operation**. **Cancel** is the default.
3. **Approve New Task**: enter the task (selected editor text can prefill it), select a declared
   team and review/approve the exact immutable snapshot/task/target.
4. **Refresh Runtime Truth**, **Inspect Task / Result**, and **Read Next Task Event Page** show
   actual states, stages, budgets, tools and result. Queued, waiting and cancel requested are not
   success. The status view is labelled stale after disconnect/failure; refresh is explicit.
5. **Approve Task Cancellation** requests cancellation. Continue refreshing until the actual
   terminal/cleanup state; stopping the editor or disconnecting does not cancel remote work.
6. Quality commands start, inspect, page events, cancel or reproduce the existing Quality Engine.
   Checks, results, findings, evidence and derived verdicts are rendered as plaintext, not links,
   executable markup or commands. Generated changes stay in the sandbox.

Mutations are refused in untrusted, virtual and multi-root workspaces. Trust/root/connection changes
invalidate pending consent. Changed source bytes require a new preview. No dynamic runtime text
becomes a filesystem path or executable target.

Reload/restart preserves only stable snapshot/run/cursor/pending identity metadata in workspaceState;
tasks, file contents and credentials are not stored there. The credential stays in SecretStorage.
After reconnect, **Reconcile Pending Operation (Read Only)** queries the original identity and
never replays a mutation. `found=false` keeps uncertainty because the original request may still
commit. An explicit endpoint change cannot silently use identifiers from the former runtime.
**Select Existing Task** discovers server truth; errors have typed codes, not raw server content.

To remove, uninstall `iacode.iacode` through Extensions. Dispose/reload removes owned commands,
subscriptions and transport resources but does not cancel work. Rotate/remove the server credential
when retiring access; clearing a profile alone does not revoke the server capability. Do not share
a profile containing SecretStorage data.

See [Desktop runbook](https://github.com/pinguim16/iacode/blob/main/docs/runbooks/DESKTOP-CLIENTS.md) for server setup, exact limits and
CLI recovery. Node API doubles are unit evidence only; actual isolated Extension Host installation,
trust and live-runtime proof are separate mandatory acceptance.
