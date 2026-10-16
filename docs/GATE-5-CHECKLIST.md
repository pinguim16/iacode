# GATE 5 — VS Code + CLI Checklist

This canonical specification expands the Gate 5 objective, deliverables, acceptance and failure
conditions in `docs/MASTER-PLAN.md`. The registry mirrors these ordered rows; requirement derivation
unites them with the lesson preflight and applicable audit findings before implementation. Every
row is mandatory. No implementation or test result is implied by this specification.

Gate 5 exposes the existing governed runtime, sandbox and quality engine through a standalone CLI
and a VS Code extension. It grants no authority to execute generated work on the host, submit a
verdict, use private credentials, or implement Gates 6 and later. Internal closure follows ADR-0037;
independent M2 validation remains a separate later audit.

## 1. Canonical scope and inherited controls

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 1.1 | The canonical checklist and registry mirror agree exactly; the complete requirement set is derived before implementation. | `docs/GATE-5-CHECKLIST.md`, `.iacode/policies/canonical-requirements.json` | Gate5SpecificationTests. |
| 1.2 | The CLI and editor reservations are consumed only by Gate 5; all later Gate reservations remain enforced. | `.iacode/policies/gate-scope.json` | Gate5ScopeTests. |
| 1.3 | Every inherited mandatory quality gate remains mandatory, and client build, tests and packaging receive a mandatory gate. | `.iacode/policies/quality-gates.json` | Gate5QualityIntegrationTests. |
| 1.4 | Counted client cases are statically discoverable, and non-counted executed suites declare their reason rather than disappearing. | `.iacode/policies/test-suites.json` | Gate5QualityIntegrationTests. |
| 1.5 | Clients never execute generated code, project commands, tool requests or patches on the host and cannot submit sandbox-owned results or quality verdicts. | `apps/cli`, `apps/vscode-extension` | Gate5BoundaryTests; FUNCTIONAL-ACCEPTANCE.json. |
| 1.6 | No experience, knowledge, training or held-out evaluation capability is implemented, and trainingAllowed remains false. | `.iacode/policies/gate-scope.json`, `PROVENANCE.json` | Gate5ScopeTests. |

## 2. Secure communication and configuration

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 2.1 | Desktop communication authenticates the configured runtime and refuses absent, invalid or expired authorization before domain effects. | `apps/api`, `apps/cli`, `apps/vscode-extension` | DesktopAuthenticationTests; FUNCTIONAL-ACCEPTANCE.json. |
| 2.2 | Client connections are bounded to explicit loopback endpoints, reject userinfo, redirects, unexpected paths and remote hosts, and cannot inherit a workspace-controlled endpoint. | `apps/cli`, `apps/vscode-extension` | DesktopTransportTests. |
| 2.3 | A hardened desktop deployment has no unauthenticated alternate domain API path; legacy development mode is explicit and refused by desktop clients. | `apps/api` | DesktopAuthenticationTests. |
| 2.4 | Tokens never appear in process arguments, workspace settings, logs, error bodies or exported results; editor secrets use SecretStorage. | `apps/cli`, `apps/vscode-extension` | DesktopCredentialTests. |
| 2.5 | Requests and responses use versioned shared contracts with closed operations, strict identities and types, byte limits, deadlines and explicit reason codes. | `packages/contracts`, `apps/cli` | DesktopContractTests; DesktopTransportTests. |
| 2.6 | Authorization, response validation, disconnected state and uncertain mutations fail closed; a retry cannot silently create duplicate work. | `apps/cli`, `apps/vscode-extension` | DesktopRecoveryTests; FUNCTIONAL-ACCEPTANCE.json. |

## 3. Workspace consent and immutable input

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 3.1 | Uploading a workspace requires explicit informed consent to the selected root and bounded inventory, and does not transmit the whole environment or local credentials. | `apps/cli`, `apps/vscode-extension` | DesktopSnapshotTests; FUNCTIONAL-ACCEPTANCE.json. |
| 3.2 | Snapshot ingress rejects traversal, absolute paths, duplicate or ambiguous names, links, special files, excessive counts and oversized payloads before persistence. | `apps/api`, `apps/cli` | DesktopSnapshotTests. |
| 3.3 | Secret-bearing and excluded control/dependency/cache paths cannot enter a desktop snapshot; canonical secret detection scans exact decoded content and fails closed. | `apps/api`, `apps/cli` | DesktopSnapshotSecurityTests; FUNCTIONAL-ACCEPTANCE.json. |
| 3.4 | Stored snapshots use the existing authorized artifact contract, real digest verification and stable retry identity; no host path is mounted for client tasks. | `apps/api`, `packages/contracts` | DesktopSnapshotPersistenceTests; FUNCTIONAL-ACCEPTANCE.json. |
| 3.5 | The editor refuses mutation in untrusted, unsupported virtual or ambiguous multi-root workspaces; trust changes or folder changes invalidate pending consent. | `apps/vscode-extension` | DesktopWorkspaceTrustTests; FUNCTIONAL-ACCEPTANCE.json. |

## 4. Governed workflow lifecycle

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 4.1 | Both clients discover declared teams and agents, start an authorized task from an immutable snapshot and show server-assigned identifiers and budgets. | `apps/cli`, `apps/vscode-extension` | DesktopLifecycleTests; FUNCTIONAL-ACCEPTANCE.json. |
| 4.2 | Mutations require explicit approval of the exact action and target; cancellation or dismissal of approval causes no domain request. | `apps/cli`, `apps/vscode-extension` | DesktopApprovalTests; FUNCTIONAL-ACCEPTANCE.json. |
| 4.3 | Clients display real run, stage, tool-wait, failure and cancellation states without translating queued or pending work into success. | `apps/cli`, `apps/vscode-extension` | DesktopPresentationTests. |
| 4.4 | Event pagination resumes from server cursors, deduplicates events and preserves ordering across reconnects without writing artificial events. | `apps/cli`, `apps/vscode-extension` | DesktopEventTests; FUNCTIONAL-ACCEPTANCE.json. |
| 4.5 | Cancellation displays requested and completed states separately, observes cleanup acknowledgement, and remains safe when repeated. | `apps/cli`, `apps/vscode-extension` | DesktopLifecycleTests; FUNCTIONAL-ACCEPTANCE.json. |
| 4.6 | Quality runs, checks, findings, evidence and derived verdicts are visible in both clients; no client may choose a passing denominator. | `apps/cli`, `apps/vscode-extension` | DesktopQualityTests; FUNCTIONAL-ACCEPTANCE.json. |
| 4.7 | Completion exposes actual result and quality outcome without automatically applying generated changes to the local workspace. | `apps/cli`, `apps/vscode-extension` | DesktopPresentationTests; FUNCTIONAL-ACCEPTANCE.json. |

## 5. CLI experience

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 5.1 | The CLI has discoverable help, explicit configuration, machine-readable output, documented exit codes and actionable bounded failures. | `apps/cli` | DesktopCliTests. |
| 5.2 | The CLI supports snapshot consent, task creation, run inspection, event following, cancellation and quality lifecycle without an editor. | `apps/cli` | DesktopCliTests; FUNCTIONAL-ACCEPTANCE.json. |
| 5.3 | CLI mutations require an explicit approval flag and stable request identity; a timeout reports an uncertain outcome and a reconciliation route rather than retrying silently. | `apps/cli` | DesktopApprovalTests; DesktopRecoveryTests. |
| 5.4 | User cancellation stops local observation without pretending to cancel a remote run, and process shutdown closes owned resources. | `apps/cli` | DesktopRecoveryTests. |

## 6. Editor experience

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 6.1 | An installable versioned VSIX activates the declared commands and status view in a fresh isolated VS Code profile without repository build artifacts. | `apps/vscode-extension` | DesktopPackagingTests; FUNCTIONAL-ACCEPTANCE.json. |
| 6.2 | The editor exposes connection health, snapshot/task approvals, status, events, cancellation and quality results through accessible native editor controls. | `apps/vscode-extension` | DesktopExtensionTests; FUNCTIONAL-ACCEPTANCE.json. |
| 6.3 | External runtime content is rendered as untrusted text, never executable markup, commands, links or filesystem targets. | `apps/vscode-extension` | DesktopPresentationTests. |
| 6.4 | Disconnect, reload and extension-host restart recover server truth from stable identifiers; stale views are labelled and cannot approve new mutations. | `apps/vscode-extension` | DesktopRecoveryTests; FUNCTIONAL-ACCEPTANCE.json. |
| 6.5 | Disposal removes commands, subscriptions, timers and observers without cancelling unrelated editor resources or remote work. | `apps/vscode-extension` | DesktopExtensionTests. |

## 7. Reproducible build and compatibility

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 7.1 | Client runtime and build inputs are pinned or dependency-free, compatible with their declared oldest runtime, and current advisory checks cover every delivered dependency graph. | `apps/cli`, `apps/vscode-extension`, `scripts/iacode` | DesktopPackagingTests; recorded dependency scan. |
| 7.2 | The production VSIX includes every runtime dependency and shared contract while excluding credentials, tests, developer caches and source workspaces. | `apps/vscode-extension` | DesktopPackagingTests. |
| 7.3 | Mandatory lint and quality discovery cover every newly introduced project root and the real packaged client source. | `scripts/iacode/gates`, `.iacode/policies/test-suites.json` | Gate5QualityIntegrationTests. |
| 7.4 | Current controls keep validating all sealed predecessors and preserve the distinction between fixed historical fixtures and current lifecycle state. | `scripts/development-ledger`, `tests` | Gate5TransitionTests; recorded historical validation. |

## 8. Executed acceptance and adversarial proof

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 8.1 | A fresh CLI installation and fresh isolated editor installation complete an actual task through the real runtime and provider, including sandbox and quality evidence. | `scripts/iacode/scenarios`, `apps/vscode-extension` | FUNCTIONAL-ACCEPTANCE.json. |
| 8.2 | Live acceptance proves refusal of unauthorized access, malicious IPC, secret upload, untrusted workspace mutation and forged quality or tool results alongside a valid clean control. | `scripts/iacode/scenarios` | FUNCTIONAL-ACCEPTANCE.json; M2-INTERNAL-RED-TEAM.json. |
| 8.3 | Live recovery and running cancellation prove truthful final state, ordered events and no duplicated task or abandoned owned sandbox. | `scripts/iacode/scenarios` | FUNCTIONAL-ACCEPTANCE.json. |
| 8.4 | Functional reports bind the immutable subject and actual process results; a failed or timed-out rerun cannot retain an old PASS. | `scripts/iacode/verify.py`, `docs/checkpoints` | Gate5AcceptanceTests; FUNCTIONAL-ACCEPTANCE.json. |
| 8.5 | Disposable integration and installation tests own their profiles, ports, services and data; operational namespaces remain unchanged and cleanup is observed. | `scripts/iacode/scenarios` | Gate5AcceptanceTests; FUNCTIONAL-ACCEPTANCE.json. |

## 9. Delivery and closure

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 9.1 | Runbooks document installation, authenticated setup, approvals, normal task flow, limits, disconnection, cancellation, recovery and removal. | `docs/runbooks`, `apps/cli/README.md`, `apps/vscode-extension/README.md` | Gate5DocumentationTests. |
| 9.2 | All selected lessons and canonical requirements have truthful resolvable implementation, positive/negative test and validation evidence before readiness. | `docs/checkpoints` | Recorded completeness and lesson validation. |
| 9.3 | The full non-fast repository verifier passes with every inherited scenario and new client scenario; no old mandatory stage is removed. | `scripts/iacode/verify.py` | Gate5QualityIntegrationTests; recorded full verification. |
| 9.4 | Full Green Keeper, completeness, internal Red Team with a valid null control and closure mirror pass in mandatory order against unchanged implementation inputs. | `docs/checkpoints` | Recorded internal assurance. |
| 9.5 | Every changed path is explicitly declared and hashes are bound; counts, provenance, risks and handoff remain current and training rights are not inferred. | `docs/checkpoints` | Recorded checkpoint validation. |
| 9.6 | The checkpoint is finalized, committed separately from Gate 4, canonically sealed, published and validated through detached remote transport and reproducible final archive. | `scripts/development-ledger`, `docs/checkpoints` | Recorded seal, transport and bundle validation. |
| 9.7 | Intermediate closure claims only INTERNAL_GATE_PASS with no blockers; independent M2 review, Red Team and second-tool validation remain pending until the later audit. | `docs/checkpoints/STATE.json`, `docs/MILESTONE-VALIDATION.md` | Gate5TransitionTests; checkpoint validation. |
| 9.8 | Gate 6 is not started without a separate explicit owner authorization and valid sealed predecessor. | `docs/checkpoints/AUTHORIZATION.md`, `.iacode/policies/gate-scope.json` | Gate5ScopeTests. |
