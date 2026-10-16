# Desktop clients — authenticated local operation

Gate 5 exposes the delivered agent, sandbox and Quality Engine through a CLI and native VS Code
extension. No generated host execution, client verdict or future experience/knowledge capability
is added. Follow `docs/checkpoints/LATEST.md` for actual delivery status.

## Server setup and boundary

Start with the Foundation, Model Gateway, Agent Runtime, Sandbox and Quality Engine runbooks.
Generate **32 cryptographically random bytes encoded as 64 lowercase hexadecimal characters**
out of band with an OS cryptographic source/password manager. Configure the capability as
`IACODE_DESKTOP_TOKEN`, paired with a timezone-aware future ISO timestamp in
`IACODE_DESKTOP_TOKEN_EXPIRES_AT`, in the ignored local Compose configuration/process environment.
Never put a real value in tracked files, command arguments, tasks, reports or chat. Do not use a
test fixture as a credential. Use a finite lifetime and rotate after disclosure or retiring access.
Provide the same capability to the client through its documented secure input, not argv.

Recreate API and worker after changing configuration:

```text
python scripts/iacode/stack.py up --build
```

The API refuses an incomplete pair, malformed key or timezone-less expiration at startup. Empty
pair is explicit **legacy development mode**, not desktop authentication; desktop clients refuse
it. Hardened mode authenticates **every `/api/v1` domain route**, not just the desktop facade.
Health/version/metrics remain probes only. The existing browser workflow does not implement this
HMAC protocol and its domain calls are refused in hardened mode: there is no unauthenticated web
fallback. Disable/rotate desktop configuration explicitly to return to legacy local web development.

The worker receives only the infrastructure API capability, not a provider credential. The
capability is never forwarded to a model, sandbox, evaluator or generated project. Compose supplies
the same `IACODE_GATEWAY_MAX_RESPONSE_BYTES` to API and worker; both derive the same bounded JSON
envelope limit. Provider credentials remain in the existing Model Gateway boundary.

Clients accept canonical numeric loopback HTTP with an explicit non-default port, no path/query,
userinfo, redirect or workspace-controlled discovery. HMAC-SHA256 authenticates exact
method/path/query/body/request identity/timestamp and exact response status/body bytes. The
capability itself is not transmitted. Redis NX replay claims survive API restart; Redis failure
refuses domain access. Clock skew is bounded to 30 seconds, replay claims to 120 seconds.

This is a **single trusted local OS account** boundary, not TLS, remote/multi-tenant deployment,
protection from other privileged extensions or OS compromise, or encryption of local task traffic.
A process holding the capability has the existing local API authority; closed clients do not
replace server/domain controls. Do not expose these loopback ports remotely.

## Installation and workflow

`python scripts/iacode/build_clients.py` emits deterministic `artifacts/clients/iacode-cli-0.1.0.tgz`,
`iacode-0.1.0.vsix` and `BUILD.json` hashes from a closed inventory. The CLI requires Node 22.23.2+
or 24.19.0+ in those major lines. Desktop VS Code requires 1.138.0+ and owns its embedded runtime
(the actual native baseline runs embedded Node 24.18.1). No runtime dependency, test driver,
workspace source, install hook, environment file or test double ships in the VSIX.

See [CLI instructions](../../apps/cli/README.md) and [native editor instructions](../../apps/vscode-extension/README.md).
Authenticate, preview inventory, approve the exact snapshot, explicitly start a task, inspect
server-assigned identifiers/budgets/stages and read ordered events/results. Dismissing consent
sends no mutation. Editor consent uses native default-Cancel controls; the handler rechecks trust,
the single local root, connection generation and exact intent after asynchronous approvals.

Snapshots are immutable artifacts, never mounts of a host folder. Limits: 512 UTF-8 files,
1 MiB/file, 2 MiB decoded total, 4,096 traversed local entries, 240 UTF-8 bytes/path and 8 MiB wire
request/response, with a 30-second request deadline. Traversal counts even excluded entries.
Links, binary/oversized content, duplicate/case-ambiguous names, platform-special and non-NFC names
fail closed. Private/control/dependency/cache paths are excluded. The API scans exact decoded
content and names with the existing canonical detector before building/looking up/storing a
snapshot. A scan outage refuses upload. Detection cannot prove absence of unknown secret formats;
do not intentionally select sensitive source.

The content-addressed object is stored before its SQL pointer. A failed write can leave an orphan
object but cannot authorize a partial artifact. Exact approved bytes retry to the same archive/UUID
identity; actual stored bytes are re-hashed before runtime/quality use.

## Recovery and outcomes

Keep a CLI create/reproduce UUID before sending. The editor persists stable identity metadata
before a mutation and restores it after reload; tasks, file contents and credentials are not in
workspaceState. No client automatically retries a mutation. Use read-only identity lookup or native
**Reconcile Pending Operation**. An authenticated lookup identifies server truth; `found=false`
does not prove no later commit and retains uncertainty. A declared authenticated pre-effect refusal
is definite; unknown errors, deadlines, lost/tampered/truncated responses and malformed accepted
results remain uncertain. A deliberate retry uses the original identity and exact inputs with new
explicit consent, never a newly generated identity just because the response was lost.

CLI follow commands resume from `--after`; editor event pages persist actual next cursors only
after display. Events remain ordered and cursor-consistent. Disconnect/reload labels views stale
and does not cancel remote work. Cancellation is separately approved: observe requested state,
then actual terminal state/cleanup acknowledgement. Ctrl+C stops only CLI observation.

Task success and quality verdict are distinct facts. Inspect actual checks, findings, results,
evidence and derived PASS/FAIL, including failures, timeout and cancellation. Neither client can
submit sandbox-owned tool results, narrow mandatory checks or author a verdict. Generated changes
remain in the run sandbox; nothing is automatically applied to the local workspace.

## Validation and removal

`python scripts/iacode/gates/client_tests.py` builds both packages twice and executes all Node
decision cases on the pinned minimum runtime; API doubles are explicit, not live acceptance.
`python scripts/iacode/native_editor.py` actually installs the VSIX into fresh owned profiles and
executes native trusted/untrusted controls. Full verification additionally requires real provider,
runtime, persistence, sandbox, quality, recovery and cancellation proofs. No inherited mandatory
gate or full-verifier stage is removed.

Uninstall the CLI from its explicit npm prefix and the extension from its installed profile.
Removing a client/profile does not revoke a capability; rotate/disable it explicitly at the server.
Disposal closes only owned local resources and never unrelated processes or remote work.

## Additional bounded client controls

The shared protocol limits JSON to 64 levels and 100,000 nodes in addition to wire/snapshot bounds.
An authenticated malformed/excessive response after a mutation retains uncertainty and its stable
identity; it never causes a retry. The exact known desktop capability and closed case/base64/hex/
percent/literal-Unicode forms are refused as operation or presentation data. This supplements the
canonical unknown-secret scan; it does not prove every arbitrary encoding or unknown secret absent.

The editor reuses at most three read-only plaintext views. Pending reconciliation cannot be erased
by switching endpoints. Selecting/cancelling existing work needs no unrelated upload; same-run
cancellation keeps event cursors, while a recovered different identity starts its cursor at zero.
Late reads cannot relabel an invalidated connection as fresh.

Native acceptance uses a normal persistent host, not extensionTestsPath's in-memory context, and
pins profile, extensions and shared-data-dir inside one owned temporary directory. Actual storage
location/process draining/removal are checked. The full verifier includes native and desktop stages;
use `python scripts/iacode/verify.py --node PATH_TO_SUPPORTED_NODE` when the default host Node is
unsupported. No runtime is silently downloaded or globally replaced.

Fresh runtime setup also requires the existing operator catalog synchronization for the configured
provider. Process health is not a populated catalog. The live proof authenticates that setup,
checks the exact IACODE_GATEWAY_SMOKE_MODEL is active, and never substitutes a different model.
This operator prerequisite does not add a client IPC operation or change production routing.
