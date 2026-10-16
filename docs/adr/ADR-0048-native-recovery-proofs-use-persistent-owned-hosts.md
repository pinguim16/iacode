# ADR-0048 — Native recovery proofs use persistent owned hosts

- Status: Accepted
- Gate: GATE 5

## Context and evidence

The actual installed VS Code 1.138 source selects in-memory storage when
`extensionTestsLocationURI` is set (cmd-0101). The first host in cmd-0099 accepted an
interrupted create once, but the second could not recover its workspace state. The harness
had used `--extensionTestsPath`. That environment cannot prove durable recovery.

## Decision

Install the unchanged production VSIX in a fresh owned profile and activate a separate
development-host acceptance driver without `--extensionTestsPath`. Use real SecretStorage,
workspaceState, native approvals and normal owned-window shutdown. The driver is excluded
from the production package. Never seed pending state or replace persistence with a fake.

Pin `--shared-data-dir` explicitly as well as profile/extensions: the installed editor otherwise
uses application shared storage outside user-data-dir. Require actual owned main.log observations
of that storage path; never inspect values or alter/delete the real shared store. Cmd-0128 passed
both native modes, actual shared-storage ownership and complete temporary removal.

On Windows, create each owned process suspended, assign it to a kill-on-close Job Object,
then resume it. Drain only this job, including children surviving the original parent.
Never terminate global Code processes or touch a real user profile. On other platforms,
use the invocation's own process group. A causal test launches a real surviving child.

An empty job does not guarantee instantaneous release of a mapped dictionary file:
cmd-0106 observed zero members but a sharing violation; cmd-0108 found no lock owners later.
Validate the exact created temporary child path and retry only sharing/access locks for
at most ten seconds. Record retries and require actual directory removal. Other errors or
deadline expiry remain FAIL. Cmd-0110 passed installation/trust and actual removal after
62 retries; this is not yet the complete recovery/provider acceptance result.

## Alternatives and consequences

Keeping the in-memory test mode cannot establish recovery. Relaxing persistence assertions,
ignoring cleanup errors or killing every editor process would invalidate or overreach the
proof. The owned normal-host approach requires explicit lifecycle and cleanup controls,
but preserves the product's actual storage semantics and the original acceptance checks.

## Related artifacts

- `scripts/iacode/native_editor.py`
- `scripts/iacode/native_process.py`
- `apps/vscode-extension/host-tests/driver.cjs`
- `tests/test_gate5_clients.py`
- `docs/checkpoints/GATE-5-CP-0001/FINDINGS.json`
