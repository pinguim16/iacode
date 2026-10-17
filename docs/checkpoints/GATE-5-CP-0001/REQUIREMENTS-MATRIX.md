# Requirements Matrix - GATE-5-CP-0001

Expected set derived by: `policies.expected_requirement_refs over docs/GATE-5-CHECKLIST.md, .iacode/policies/canonical-requirements.json, .iacode/policies/audit-registry.json and LESSON-PREFLIGHT.json`.

| ID | Anchor | Mandatory | Status | Requirement | Source |
|---|---|---|---|---|---|
| `REQ-0001` | `canonical:GATE-5#1.1` | yes | `COMPLETE` | The canonical checklist and registry mirror agree exactly; the complete requirement set is derived before implementation. | docs/GATE-5-CHECKLIST.md row 1.1 |
| `REQ-0002` | `canonical:GATE-5#1.2` | yes | `COMPLETE` | The CLI and editor reservations are consumed only by Gate 5; all later Gate reservations remain enforced. | docs/GATE-5-CHECKLIST.md row 1.2 |
| `REQ-0003` | `canonical:GATE-5#1.3` | yes | `COMPLETE` | Every inherited mandatory quality gate remains mandatory, and client build, tests and packaging receive a mandatory gate. | docs/GATE-5-CHECKLIST.md row 1.3 |
| `REQ-0004` | `canonical:GATE-5#1.4` | yes | `COMPLETE` | Counted client cases are statically discoverable, and non-counted executed suites declare their reason rather than disappearing. | docs/GATE-5-CHECKLIST.md row 1.4 |
| `REQ-0005` | `canonical:GATE-5#1.5` | yes | `COMPLETE` | Clients never execute generated code, project commands, tool requests or patches on the host and cannot submit sandbox-owned results or quality verdicts. | docs/GATE-5-CHECKLIST.md row 1.5 |
| `REQ-0006` | `canonical:GATE-5#1.6` | yes | `COMPLETE` | No experience, knowledge, training or held-out evaluation capability is implemented, and trainingAllowed remains false. | docs/GATE-5-CHECKLIST.md row 1.6 |
| `REQ-0007` | `canonical:GATE-5#2.1` | yes | `COMPLETE` | Desktop communication authenticates the configured runtime and refuses absent, invalid or expired authorization before domain effects. | docs/GATE-5-CHECKLIST.md row 2.1 |
| `REQ-0008` | `canonical:GATE-5#2.2` | yes | `COMPLETE` | Client connections are bounded to explicit loopback endpoints, reject userinfo, redirects, unexpected paths and remote hosts, and cannot inherit a workspace-controlled endpoint. | docs/GATE-5-CHECKLIST.md row 2.2 |
| `REQ-0009` | `canonical:GATE-5#2.3` | yes | `COMPLETE` | A hardened desktop deployment has no unauthenticated alternate domain API path; legacy development mode is explicit and refused by desktop clients. | docs/GATE-5-CHECKLIST.md row 2.3 |
| `REQ-0010` | `canonical:GATE-5#2.4` | yes | `COMPLETE` | Tokens never appear in process arguments, workspace settings, logs, error bodies or exported results; editor secrets use SecretStorage. | docs/GATE-5-CHECKLIST.md row 2.4 |
| `REQ-0011` | `canonical:GATE-5#2.5` | yes | `COMPLETE` | Requests and responses use versioned shared contracts with closed operations, strict identities and types, byte limits, deadlines and explicit reason codes. | docs/GATE-5-CHECKLIST.md row 2.5 |
| `REQ-0012` | `canonical:GATE-5#2.6` | yes | `COMPLETE` | Authorization, response validation, disconnected state and uncertain mutations fail closed; a retry cannot silently create duplicate work. | docs/GATE-5-CHECKLIST.md row 2.6 |
| `REQ-0013` | `canonical:GATE-5#3.1` | yes | `COMPLETE` | Uploading a workspace requires explicit informed consent to the selected root and bounded inventory, and does not transmit the whole environment or local credentials. | docs/GATE-5-CHECKLIST.md row 3.1 |
| `REQ-0014` | `canonical:GATE-5#3.2` | yes | `COMPLETE` | Snapshot ingress rejects traversal, absolute paths, duplicate or ambiguous names, links, special files, excessive counts and oversized payloads before persistence. | docs/GATE-5-CHECKLIST.md row 3.2 |
| `REQ-0015` | `canonical:GATE-5#3.3` | yes | `COMPLETE` | Secret-bearing and excluded control/dependency/cache paths cannot enter a desktop snapshot; canonical secret detection scans exact decoded content and fails closed. | docs/GATE-5-CHECKLIST.md row 3.3 |
| `REQ-0016` | `canonical:GATE-5#3.4` | yes | `COMPLETE` | Stored snapshots use the existing authorized artifact contract, real digest verification and stable retry identity; no host path is mounted for client tasks. | docs/GATE-5-CHECKLIST.md row 3.4 |
| `REQ-0017` | `canonical:GATE-5#3.5` | yes | `COMPLETE` | The editor refuses mutation in untrusted, unsupported virtual or ambiguous multi-root workspaces; trust changes or folder changes invalidate pending consent. | docs/GATE-5-CHECKLIST.md row 3.5 |
| `REQ-0018` | `canonical:GATE-5#4.1` | yes | `COMPLETE` | Both clients discover declared teams and agents, start an authorized task from an immutable snapshot and show server-assigned identifiers and budgets. | docs/GATE-5-CHECKLIST.md row 4.1 |
| `REQ-0019` | `canonical:GATE-5#4.2` | yes | `COMPLETE` | Mutations require explicit approval of the exact action and target; cancellation or dismissal of approval causes no domain request. | docs/GATE-5-CHECKLIST.md row 4.2 |
| `REQ-0020` | `canonical:GATE-5#4.3` | yes | `COMPLETE` | Clients display real run, stage, tool-wait, failure and cancellation states without translating queued or pending work into success. | docs/GATE-5-CHECKLIST.md row 4.3 |
| `REQ-0021` | `canonical:GATE-5#4.4` | yes | `COMPLETE` | Event pagination resumes from server cursors, deduplicates events and preserves ordering across reconnects without writing artificial events. | docs/GATE-5-CHECKLIST.md row 4.4 |
| `REQ-0022` | `canonical:GATE-5#4.5` | yes | `COMPLETE` | Cancellation displays requested and completed states separately, observes cleanup acknowledgement, and remains safe when repeated. | docs/GATE-5-CHECKLIST.md row 4.5 |
| `REQ-0023` | `canonical:GATE-5#4.6` | yes | `COMPLETE` | Quality runs, checks, findings, evidence and derived verdicts are visible in both clients; no client may choose a passing denominator. | docs/GATE-5-CHECKLIST.md row 4.6 |
| `REQ-0024` | `canonical:GATE-5#4.7` | yes | `COMPLETE` | Completion exposes actual result and quality outcome without automatically applying generated changes to the local workspace. | docs/GATE-5-CHECKLIST.md row 4.7 |
| `REQ-0025` | `canonical:GATE-5#5.1` | yes | `COMPLETE` | The CLI has discoverable help, explicit configuration, machine-readable output, documented exit codes and actionable bounded failures. | docs/GATE-5-CHECKLIST.md row 5.1 |
| `REQ-0026` | `canonical:GATE-5#5.2` | yes | `COMPLETE` | The CLI supports snapshot consent, task creation, run inspection, event following, cancellation and quality lifecycle without an editor. | docs/GATE-5-CHECKLIST.md row 5.2 |
| `REQ-0027` | `canonical:GATE-5#5.3` | yes | `COMPLETE` | CLI mutations require an explicit approval flag and stable request identity; a timeout reports an uncertain outcome and a reconciliation route rather than retrying silently. | docs/GATE-5-CHECKLIST.md row 5.3 |
| `REQ-0028` | `canonical:GATE-5#5.4` | yes | `COMPLETE` | User cancellation stops local observation without pretending to cancel a remote run, and process shutdown closes owned resources. | docs/GATE-5-CHECKLIST.md row 5.4 |
| `REQ-0029` | `canonical:GATE-5#6.1` | yes | `COMPLETE` | An installable versioned VSIX activates the declared commands and status view in a fresh isolated VS Code profile without repository build artifacts. | docs/GATE-5-CHECKLIST.md row 6.1 |
| `REQ-0030` | `canonical:GATE-5#6.2` | yes | `COMPLETE` | The editor exposes connection health, snapshot/task approvals, status, events, cancellation and quality results through accessible native editor controls. | docs/GATE-5-CHECKLIST.md row 6.2 |
| `REQ-0031` | `canonical:GATE-5#6.3` | yes | `COMPLETE` | External runtime content is rendered as untrusted text, never executable markup, commands, links or filesystem targets. | docs/GATE-5-CHECKLIST.md row 6.3 |
| `REQ-0032` | `canonical:GATE-5#6.4` | yes | `COMPLETE` | Disconnect, reload and extension-host restart recover server truth from stable identifiers; stale views are labelled and cannot approve new mutations. | docs/GATE-5-CHECKLIST.md row 6.4 |
| `REQ-0033` | `canonical:GATE-5#6.5` | yes | `COMPLETE` | Disposal removes commands, subscriptions, timers and observers without cancelling unrelated editor resources or remote work. | docs/GATE-5-CHECKLIST.md row 6.5 |
| `REQ-0034` | `canonical:GATE-5#7.1` | yes | `COMPLETE` | Client runtime and build inputs are pinned or dependency-free, compatible with their declared oldest runtime, and current advisory checks cover every delivered dependency graph. | docs/GATE-5-CHECKLIST.md row 7.1 |
| `REQ-0035` | `canonical:GATE-5#7.2` | yes | `COMPLETE` | The production VSIX includes every runtime dependency and shared contract while excluding credentials, tests, developer caches and source workspaces. | docs/GATE-5-CHECKLIST.md row 7.2 |
| `REQ-0036` | `canonical:GATE-5#7.3` | yes | `COMPLETE` | Mandatory lint and quality discovery cover every newly introduced project root and the real packaged client source. | docs/GATE-5-CHECKLIST.md row 7.3 |
| `REQ-0037` | `canonical:GATE-5#7.4` | yes | `COMPLETE` | Current controls keep validating all sealed predecessors and preserve the distinction between fixed historical fixtures and current lifecycle state. | docs/GATE-5-CHECKLIST.md row 7.4 |
| `REQ-0038` | `canonical:GATE-5#8.1` | yes | `COMPLETE` | A fresh CLI installation and fresh isolated editor installation complete an actual task through the real runtime and provider, including sandbox and quality evidence. | docs/GATE-5-CHECKLIST.md row 8.1 |
| `REQ-0039` | `canonical:GATE-5#8.2` | yes | `COMPLETE` | Live acceptance proves refusal of unauthorized access, malicious IPC, secret upload, untrusted workspace mutation and forged quality or tool results alongside a valid clean control. | docs/GATE-5-CHECKLIST.md row 8.2 |
| `REQ-0040` | `canonical:GATE-5#8.3` | yes | `COMPLETE` | Live recovery and running cancellation prove truthful final state, ordered events and no duplicated task or abandoned owned sandbox. | docs/GATE-5-CHECKLIST.md row 8.3 |
| `REQ-0041` | `canonical:GATE-5#8.4` | yes | `COMPLETE` | Functional reports bind the immutable subject and actual process results; a failed or timed-out rerun cannot retain an old PASS. | docs/GATE-5-CHECKLIST.md row 8.4 |
| `REQ-0042` | `canonical:GATE-5#8.5` | yes | `COMPLETE` | Disposable integration and installation tests own their profiles, ports, services and data; operational namespaces remain unchanged and cleanup is observed. | docs/GATE-5-CHECKLIST.md row 8.5 |
| `REQ-0043` | `canonical:GATE-5#9.1` | yes | `COMPLETE` | Runbooks document installation, authenticated setup, approvals, normal task flow, limits, disconnection, cancellation, recovery and removal. | docs/GATE-5-CHECKLIST.md row 9.1 |
| `REQ-0044` | `canonical:GATE-5#9.2` | yes | `COMPLETE` | All selected lessons and canonical requirements have truthful resolvable implementation, positive/negative test and validation evidence before readiness. | docs/GATE-5-CHECKLIST.md row 9.2 |
| `REQ-0045` | `canonical:GATE-5#9.3` | yes | `COMPLETE` | The full non-fast repository verifier passes with every inherited scenario and new client scenario; no old mandatory stage is removed. | docs/GATE-5-CHECKLIST.md row 9.3 |
| `REQ-0046` | `canonical:GATE-5#9.4` | yes | `COMPLETE` | Full Green Keeper, completeness, internal Red Team with a valid null control and closure mirror pass in mandatory order against unchanged implementation inputs. | docs/GATE-5-CHECKLIST.md row 9.4 |
| `REQ-0047` | `canonical:GATE-5#9.5` | yes | `COMPLETE` | Every changed path is explicitly declared and hashes are bound; counts, provenance, risks and handoff remain current and training rights are not inferred. | docs/GATE-5-CHECKLIST.md row 9.5 |
| `REQ-0048` | `canonical:GATE-5#9.6` | yes | `COMPLETE` | The checkpoint is finalized, committed separately from Gate 4, canonically sealed, published and validated through detached remote transport and reproducible final archive. | docs/GATE-5-CHECKLIST.md row 9.6 |
| `REQ-0049` | `canonical:GATE-5#9.7` | yes | `COMPLETE` | Intermediate closure claims only INTERNAL_GATE_PASS with no blockers; independent M2 review, Red Team and second-tool validation remain pending until the later audit. | docs/GATE-5-CHECKLIST.md row 9.7 |
| `REQ-0050` | `canonical:GATE-5#9.8` | yes | `COMPLETE` | Gate 6 is not started without a separate explicit owner authorization and valid sealed predecessor. | docs/GATE-5-CHECKLIST.md row 9.8 |
| `LESSON-REQ-0001` | `lesson:LSN-0001` | yes | `COMPLETE` | Verify checkpoint validation must succeed from a detached checkout of the checkpoint tag | LESSON-PREFLIGHT.json LESSON-REQ-0001 |
| `LESSON-REQ-0002` | `lesson:LSN-0002` | yes | `COMPLETE` | Verify a file inventory must be recomputed from the repository, never trusted as an assertion | LESSON-PREFLIGHT.json LESSON-REQ-0002 |
| `LESSON-REQ-0003` | `lesson:LSN-0003` | yes | `COMPLETE` | Verify every operation attempt must be auditable, including a refusal decided before execution | LESSON-PREFLIGHT.json LESSON-REQ-0003 |
| `LESSON-REQ-0004` | `lesson:LSN-0004` | yes | `COMPLETE` | Verify a checkpoint may never claim readiness while it also claims to be blocked | LESSON-PREFLIGHT.json LESSON-REQ-0004 |
| `LESSON-REQ-0005` | `lesson:LSN-0005` | yes | `COMPLETE` | Verify a PASS requires evidence that can be executed or resolved, not a statement | LESSON-PREFLIGHT.json LESSON-REQ-0005 |
| `LESSON-REQ-0006` | `lesson:LSN-0006` | yes | `COMPLETE` | Verify the repository must be self-contained; a specification may not live outside it | LESSON-PREFLIGHT.json LESSON-REQ-0006 |
| `LESSON-REQ-0007` | `lesson:LSN-0007` | yes | `COMPLETE` | Verify independent validation cannot be declared by the run that did the work | LESSON-PREFLIGHT.json LESSON-REQ-0007 |
| `LESSON-REQ-0008` | `lesson:LSN-0008` | yes | `COMPLETE` | Verify requirement completeness must be total and evidence-backed before handoff | LESSON-PREFLIGHT.json LESSON-REQ-0008 |
| `LESSON-REQ-0009` | `lesson:LSN-0009` | yes | `COMPLETE` | Verify a red gate requires rework, never a waiver, and never a weakened check | LESSON-PREFLIGHT.json LESSON-REQ-0009 |
| `LESSON-REQ-0010` | `lesson:LSN-0010` | yes | `COMPLETE` | Verify a recorded command must carry runtime, working directory, commit and purpose to be replayable | LESSON-PREFLIGHT.json LESSON-REQ-0010 |
| `LESSON-REQ-0011` | `lesson:LSN-0011` | yes | `COMPLETE` | Verify a control over a checkpoint's own evidence must be scoped to the moment it matters | LESSON-PREFLIGHT.json LESSON-REQ-0011 |
| `LESSON-REQ-0012` | `lesson:LSN-0012` | yes | `COMPLETE` | Verify sealed checkpoints and their tags are immutable, and tooling must keep validating them | LESSON-PREFLIGHT.json LESSON-REQ-0012 |
| `LESSON-REQ-0013` | `lesson:LSN-0013` | yes | `COMPLETE` | Verify an installed capability must be detected by resolved path, not by a bare command lookup | LESSON-PREFLIGHT.json LESSON-REQ-0013 |
| `LESSON-REQ-0014` | `lesson:LSN-0014` | yes | `COMPLETE` | Verify evidence must be recorded as it happens, not reconstructed at the end of a run | LESSON-PREFLIGHT.json LESSON-REQ-0014 |
| `LESSON-REQ-0015` | `lesson:LSN-0015` | yes | `COMPLETE` | Verify every positive terminal status needs one shared promotion invariant | LESSON-PREFLIGHT.json LESSON-REQ-0015 |
| `LESSON-REQ-0016` | `lesson:LSN-0016` | yes | `COMPLETE` | Verify a mandatory set must be closed by policy, never chosen by the caller | LESSON-PREFLIGHT.json LESSON-REQ-0016 |
| `LESSON-REQ-0017` | `lesson:LSN-0017` | yes | `COMPLETE` | Verify a completeness denominator must come from a source the delivery does not own | LESSON-PREFLIGHT.json LESSON-REQ-0017 |
| `LESSON-REQ-0018` | `lesson:LSN-0018` | yes | `COMPLETE` | Verify a structured reference must be resolved, not merely well typed | LESSON-PREFLIGHT.json LESSON-REQ-0018 |
| `LESSON-REQ-0019` | `lesson:LSN-0019` | yes | `COMPLETE` | Verify a derived artifact must carry a fingerprint of the inputs that produced it | LESSON-PREFLIGHT.json LESSON-REQ-0019 |
| `LESSON-REQ-0020` | `lesson:LSN-0020` | yes | `COMPLETE` | Verify evidence produced from a dirty tree needs immutable input identity | LESSON-PREFLIGHT.json LESSON-REQ-0020 |
| `LESSON-REQ-0021` | `lesson:LSN-0021` | yes | `COMPLETE` | Verify sealed history needs an anchor outside the content it describes | LESSON-PREFLIGHT.json LESSON-REQ-0021 |
| `LESSON-REQ-0022` | `lesson:LSN-0022` | yes | `COMPLETE` | Verify an authoritative count must be derived once, never maintained by hand twice | LESSON-PREFLIGHT.json LESSON-REQ-0022 |
| `LESSON-REQ-0023` | `lesson:LSN-0023` | yes | `COMPLETE` | Verify a lesson must cite a source that actually records the finding it claims | LESSON-PREFLIGHT.json LESSON-REQ-0023 |
| `LESSON-REQ-0024` | `lesson:LSN-0024` | yes | `COMPLETE` | Verify a control is finished only when its positive path has been executed, not only its refusals | LESSON-PREFLIGHT.json LESSON-REQ-0024 |
| `LESSON-REQ-0025` | `lesson:LSN-0025` | yes | `COMPLETE` | Verify a generic guardrail derives repository state instead of naming today's checkpoint | LESSON-PREFLIGHT.json LESSON-REQ-0025 |
| `LESSON-REQ-0026` | `lesson:LSN-0026` | yes | `COMPLETE` | Verify an adversarial battery without a null-mutation control proves nothing | LESSON-PREFLIGHT.json LESSON-REQ-0026 |
| `LESSON-REQ-0027` | `lesson:LSN-0027` | yes | `COMPLETE` | Verify a lesson's prose may record a residual limit but may never contradict its status | LESSON-PREFLIGHT.json LESSON-REQ-0027 |
| `LESSON-REQ-0028` | `lesson:LSN-0028` | yes | `COMPLETE` | Verify a configuration key that no code reads is a defect, not documentation | LESSON-PREFLIGHT.json LESSON-REQ-0028 |
| `LESSON-REQ-0029` | `lesson:LSN-0029` | yes | `COMPLETE` | Verify a required protocol transition must never turn a mandatory gate red | LESSON-PREFLIGHT.json LESSON-REQ-0029 |
| `LESSON-REQ-0030` | `lesson:LSN-0031` | yes | `COMPLETE` | Verify an empty applicable set is not a missing required set, and a control must tell them apart | LESSON-PREFLIGHT.json LESSON-REQ-0030 |
| `LESSON-REQ-0031` | `lesson:LSN-0032` | yes | `COMPLETE` | Verify a control written while one Gate was the only Gate stops being a control when the next one starts | LESSON-PREFLIGHT.json LESSON-REQ-0031 |
| `LESSON-REQ-0032` | `lesson:LSN-0033` | yes | `COMPLETE` | Verify a value bound in middleware is absent in the handlers that run outside it | LESSON-PREFLIGHT.json LESSON-REQ-0032 |
| `LESSON-REQ-0033` | `lesson:LSN-0034` | yes | `COMPLETE` | Verify re-deriving what the framework already computed diverges from the framework | LESSON-PREFLIGHT.json LESSON-REQ-0033 |
| `LESSON-REQ-0034` | `lesson:LSN-0035` | yes | `COMPLETE` | Verify captured subprocess output decoded or re-emitted with the platform codepage crashes the tool, not the work | LESSON-PREFLIGHT.json LESSON-REQ-0034 |
| `LESSON-REQ-0035` | `lesson:LSN-0036` | yes | `COMPLETE` | Verify a gate that runs inside an image measures the image, not the source | LESSON-PREFLIGHT.json LESSON-REQ-0035 |
| `LESSON-REQ-0036` | `lesson:LSN-0037` | yes | `COMPLETE` | Verify a shared control that names an identifier the repository derives stops being a control when that identifier moves | LESSON-PREFLIGHT.json LESSON-REQ-0036 |
| `LESSON-REQ-0037` | `lesson:LSN-0038` | yes | `COMPLETE` | Verify two representations of one concept in one module disagree, and the safer one loses | LESSON-PREFLIGHT.json LESSON-REQ-0037 |
| `LESSON-REQ-0038` | `lesson:LSN-0039` | yes | `COMPLETE` | Verify a test that writes to the operational database leaves production data behind | LESSON-PREFLIGHT.json LESSON-REQ-0038 |
| `LESSON-REQ-0039` | `lesson:LSN-0040` | yes | `COMPLETE` | Verify a control that judges sealed history only runs once a successor anchors it | LESSON-PREFLIGHT.json LESSON-REQ-0039 |
| `LESSON-REQ-0040` | `lesson:LSN-0041` | yes | `COMPLETE` | Verify an editing path that consumes a backslash escape leaves a control character, and the control it belonged to silently matches nothing | LESSON-PREFLIGHT.json LESSON-REQ-0040 |
| `LESSON-REQ-0041` | `lesson:LSN-0042` | yes | `COMPLETE` | Verify a naming convention rewrites a CHECK constraint's name and leaves a UNIQUE constraint's alone | LESSON-PREFLIGHT.json LESSON-REQ-0041 |
| `LESSON-REQ-0042` | `lesson:LSN-0043` | yes | `COMPLETE` | Verify a log line is not evidence that another process is ready | LESSON-PREFLIGHT.json LESSON-REQ-0042 |
| `LESSON-REQ-0043` | `lesson:LSN-0044` | yes | `COMPLETE` | Verify a boundary scan must read the code rather than the prose, and must be shown to fire on a mutated module | LESSON-PREFLIGHT.json LESSON-REQ-0043 |
| `LESSON-REQ-0044` | `lesson:LSN-0045` | yes | `COMPLETE` | Verify a counted test suite must declare its cases statically, because the denominator is read from the source | LESSON-PREFLIGHT.json LESSON-REQ-0044 |
| `LESSON-REQ-0045` | `lesson:LSN-0046` | yes | `COMPLETE` | Verify a timeout that cancels the task it runs in leaves nothing able to record what happened | LESSON-PREFLIGHT.json LESSON-REQ-0045 |
| `LESSON-REQ-0046` | `lesson:LSN-0047` | yes | `COMPLETE` | Verify a refusal that misnames the defect spends the only repair on the wrong correction | LESSON-PREFLIGHT.json LESSON-REQ-0046 |
| `LESSON-REQ-0047` | `lesson:LSN-0048` | yes | `COMPLETE` | Verify a state and the event that explains it, written in two commits, are written event first | LESSON-PREFLIGHT.json LESSON-REQ-0047 |
| `LESSON-REQ-0048` | `lesson:LSN-0049` | yes | `COMPLETE` | Verify a metric read the instant after the call that moved it is read before the scrape that carries it | LESSON-PREFLIGHT.json LESSON-REQ-0048 |
| `LESSON-REQ-0049` | `lesson:LSN-0050` | yes | `COMPLETE` | Verify a checkpoint sealed without naming its own tag cannot be validated from that tag | LESSON-PREFLIGHT.json LESSON-REQ-0049 |
| `LESSON-REQ-0050` | `lesson:LSN-0051` | yes | `COMPLETE` | Verify a payload one service bounds for another must be bounded as the receiver measures it | LESSON-PREFLIGHT.json LESSON-REQ-0050 |
| `LESSON-REQ-0051` | `lesson:LSN-0052` | yes | `COMPLETE` | Verify two processes that meet on a queue must name what crosses it once, and a real run must exercise both | LESSON-PREFLIGHT.json LESSON-REQ-0051 |
| `LESSON-REQ-0052` | `lesson:LSN-0053` | yes | `COMPLETE` | Verify a process sweep that reads what a forking process holds waits on the processes it has to kill | LESSON-PREFLIGHT.json LESSON-REQ-0052 |
| `LESSON-REQ-0053` | `lesson:LSN-0054` | no | `COMPLETE` | Verify a pre-push check narrower than the change's reach lets a red gate reach the public remote | LESSON-PREFLIGHT.json LESSON-REQ-0053 |
| `LESSON-REQ-0054` | `lesson:LSN-0055` | yes | `COMPLETE` | Verify a contract a model must follow has to reach the model, rendered from the definition the parser enforces | LESSON-PREFLIGHT.json LESSON-REQ-0054 |
| `LESSON-REQ-0055` | `lesson:LSN-0056` | yes | `COMPLETE` | Verify a result is accepted only from the executor that owns the request, decided when the request is created | LESSON-PREFLIGHT.json LESSON-REQ-0055 |
| `LESSON-REQ-0056` | `lesson:LSN-0057` | yes | `COMPLETE` | Verify a pinned lock can become unsafe without changing, so advisory state is live evidence | LESSON-PREFLIGHT.json LESSON-REQ-0056 |
| `LESSON-REQ-0057` | `lesson:LSN-0058` | yes | `COMPLETE` | Verify container health does not prove Docker Desktop host-port forwarding | LESSON-PREFLIGHT.json LESSON-REQ-0057 |
| `LESSON-REQ-0058` | `lesson:LSN-0059` | yes | `COMPLETE` | Verify a lesson exclusion must declare the scope it excludes | LESSON-PREFLIGHT.json LESSON-REQ-0058 |
| `LESSON-REQ-0059` | `lesson:LSN-0060` | yes | `COMPLETE` | Verify parent and child facts without an ORM relationship require an explicit flush boundary | LESSON-PREFLIGHT.json LESSON-REQ-0059 |
| `LESSON-REQ-0060` | `lesson:LSN-0061` | yes | `COMPLETE` | Verify cancellation completion must not bypass cleanup acknowledgement | LESSON-PREFLIGHT.json LESSON-REQ-0060 |
| `LESSON-REQ-0061` | `lesson:LSN-0062` | yes | `COMPLETE` | Verify provenance digests are a set even when their sources are distinct | LESSON-PREFLIGHT.json LESSON-REQ-0061 |
| `LESSON-REQ-0062` | `lesson:LSN-0063` | yes | `COMPLETE` | Verify an identity shared across services must satisfy the strictest persistence type and remain stable | LESSON-PREFLIGHT.json LESSON-REQ-0062 |
| `LESSON-REQ-0063` | `lesson:LSN-0064` | yes | `COMPLETE` | Verify a shared execution resource needs an explicit exclusive owner for every owning domain | LESSON-PREFLIGHT.json LESSON-REQ-0063 |
| `LESSON-REQ-0064` | `lesson:LSN-0065` | yes | `COMPLETE` | Verify a shared execution identifier must not be written into a foreign key owned by another domain | LESSON-PREFLIGHT.json LESSON-REQ-0064 |
| `LESSON-REQ-0065` | `lesson:LSN-0066` | yes | `COMPLETE` | Verify immutable content identity excludes observation time and the first observer | LESSON-PREFLIGHT.json LESSON-REQ-0065 |
| `LESSON-REQ-0066` | `lesson:LSN-0067` | yes | `COMPLETE` | Verify cancellation semantics must survive orchestration-library exception wrapping | LESSON-PREFLIGHT.json LESSON-REQ-0066 |
| `LESSON-REQ-0067` | `lesson:LSN-0068` | yes | `COMPLETE` | Verify a bounded parser must apply each content limit only to content it interprets | LESSON-PREFLIGHT.json LESSON-REQ-0067 |
| `LESSON-REQ-0068` | `lesson:LSN-0069` | yes | `COMPLETE` | Verify a polyglot plan binds each check to both its project root and its toolchain | LESSON-PREFLIGHT.json LESSON-REQ-0068 |
| `LESSON-REQ-0069` | `lesson:LSN-0070` | yes | `COMPLETE` | Verify project discovery must separate deployable roots, nested fixtures and check applicability | LESSON-PREFLIGHT.json LESSON-REQ-0069 |
| `LESSON-REQ-0070` | `lesson:LSN-0071` | yes | `COMPLETE` | Verify every quality image must provision snapshots on its oldest runtime and prepare each isolated check | LESSON-PREFLIGHT.json LESSON-REQ-0070 |
| `LESSON-REQ-0071` | `lesson:LSN-0072` | yes | `COMPLETE` | Verify secret findings and reviewed false positives must share one policy-owned taxonomy | LESSON-PREFLIGHT.json LESSON-REQ-0071 |
| `LESSON-REQ-0072` | `lesson:LSN-0073` | yes | `COMPLETE` | Verify the canonical lint denominator must cover every detected project root | LESSON-PREFLIGHT.json LESSON-REQ-0072 |
| `LESSON-REQ-0073` | `lesson:LSN-0074` | yes | `COMPLETE` | Verify an importable source tree is not an installed or repository-configured test environment | LESSON-PREFLIGHT.json LESSON-REQ-0073 |
| `LESSON-REQ-0074` | `lesson:LSN-0075` | yes | `COMPLETE` | Verify offline package installation requires its build backend inside the quality image | LESSON-PREFLIGHT.json LESSON-REQ-0074 |
| `LESSON-REQ-0075` | `lesson:LSN-0076` | yes | `COMPLETE` | Verify projected nested configuration requires an explicit monorepo root | LESSON-PREFLIGHT.json LESSON-REQ-0075 |
| `LESSON-REQ-0076` | `lesson:LSN-0077` | yes | `COMPLETE` | Verify harness wait bounds must reflect workload size without changing product deadlines | LESSON-PREFLIGHT.json LESSON-REQ-0076 |
| `LESSON-REQ-0077` | `lesson:LSN-0078` | yes | `COMPLETE` | Verify evidence recorders must resolve caller-supplied commit references before execution | LESSON-PREFLIGHT.json LESSON-REQ-0077 |
| `LESSON-REQ-0078` | `lesson:LSN-0079` | yes | `COMPLETE` | Verify test discovery and the unit runner must cover the same project scope | LESSON-PREFLIGHT.json LESSON-REQ-0078 |
| `LESSON-REQ-0079` | `lesson:LSN-0080` | yes | `COMPLETE` | Verify a failed verification stage must not leave an older PASS report addressable | LESSON-PREFLIGHT.json LESSON-REQ-0079 |
| `LESSON-REQ-0080` | `lesson:LSN-0081` | yes | `COMPLETE` | Verify canonical requirement evidence must name a test the repository actually discovers | LESSON-PREFLIGHT.json LESSON-REQ-0080 |
| `LESSON-REQ-0081` | `lesson:LSN-0082` | yes | `COMPLETE` | Verify engineering memory cannot depend on an ephemeral generated report | LESSON-PREFLIGHT.json LESSON-REQ-0081 |
| `LESSON-REQ-0082` | `lesson:LSN-0083` | yes | `COMPLETE` | Verify a command that decodes captured UTF-8 must also configure the stream that re-emits it | LESSON-PREFLIGHT.json LESSON-REQ-0082 |
| `LESSON-REQ-0083` | `lesson:LSN-0084` | yes | `COMPLETE` | Verify a historical Gate documentation test must derive the current entry-point state | LESSON-PREFLIGHT.json LESSON-REQ-0083 |
| `LESSON-REQ-0084` | `lesson:LSN-0085` | yes | `COMPLETE` | Verify a source-based control must assert syntax semantics rather than formatter layout | LESSON-PREFLIGHT.json LESSON-REQ-0084 |
| `LESSON-REQ-0085` | `lesson:LSN-0086` | yes | `COMPLETE` | Verify a subprocess assertion must preserve the exit code when both streams are empty | LESSON-PREFLIGHT.json LESSON-REQ-0085 |
| `LESSON-REQ-0086` | `lesson:LSN-0087` | yes | `COMPLETE` | Verify a rehearsal worker must register every workflow activity boundary | LESSON-PREFLIGHT.json LESSON-REQ-0086 |
| `LESSON-REQ-0087` | `lesson:LSN-0088` | yes | `COMPLETE` | Verify a test inside a built image can consume only inputs copied into that image | LESSON-PREFLIGHT.json LESSON-REQ-0087 |
| `LESSON-REQ-0088` | `lesson:LSN-0089` | yes | `COMPLETE` | Verify domain not-applicability and operational failure need distinct orchestration outcomes | LESSON-PREFLIGHT.json LESSON-REQ-0088 |
| `LESSON-REQ-0089` | `lesson:LSN-0090` | yes | `COMPLETE` | Verify a clean-clone control must use only versioned configuration inputs | LESSON-PREFLIGHT.json LESSON-REQ-0089 |
| `LESSON-REQ-0090` | `lesson:LSN-0091` | yes | `COMPLETE` | Verify secret detection must run on the exact bytes at the durable evidence boundary | LESSON-PREFLIGHT.json LESSON-REQ-0090 |
| `LESSON-REQ-0091` | `lesson:LSN-0092` | yes | `COMPLETE` | Verify canonical audit parsers must consume every bounded sealed report rendering | LESSON-PREFLIGHT.json LESSON-REQ-0091 |
| `LESSON-REQ-0092` | `lesson:LSN-0093` | yes | `COMPLETE` | Verify disposable control repositories must carry every imported repository package | LESSON-PREFLIGHT.json LESSON-REQ-0092 |
| `LESSON-REQ-0093` | `lesson:LSN-0094` | yes | `COMPLETE` | Verify a review bundle must include unchanged canonical artifact categories | LESSON-PREFLIGHT.json LESSON-REQ-0093 |
| `LESSON-REQ-0094` | `lesson:LSN-0095` | yes | `COMPLETE` | Verify a complete verifier must own its Compose runtime by checkout | LESSON-PREFLIGHT.json LESSON-REQ-0094 |
| `LESSON-REQ-0095` | `lesson:LSN-0096` | yes | `COMPLETE` | Verify evidence publishers must consume the producer's canonical result schema | LESSON-PREFLIGHT.json LESSON-REQ-0095 |
| `LESSON-REQ-0096` | `lesson:LSN-0097` | yes | `COMPLETE` | Verify a review-bundle declaration must bind an immutable reconstruction subject | LESSON-PREFLIGHT.json LESSON-REQ-0096 |
| `LESSON-REQ-0097` | `lesson:LSN-0098` | yes | `COMPLETE` | Verify accepted cancellation must be enforced from durable state across activity boundaries | LESSON-PREFLIGHT.json LESSON-REQ-0097 |
| `LESSON-REQ-0098` | `lesson:LSN-0099` | yes | `COMPLETE` | Verify a refused subject is an attempted input, not executed commit evidence | LESSON-PREFLIGHT.json LESSON-REQ-0098 |
| `LESSON-REQ-0099` | `lesson:LSN-0100` | yes | `COMPLETE` | Verify pre-seal detached validation must bind the explicit subject namespace | LESSON-PREFLIGHT.json LESSON-REQ-0099 |
| `LESSON-REQ-0100` | `lesson:LSN-0101` | yes | `COMPLETE` | Verify a structural record and its canonical index are one atomic change | LESSON-PREFLIGHT.json LESSON-REQ-0100 |
| `LESSON-REQ-0101` | `lesson:LSN-0102` | yes | `COMPLETE` | Verify assurance denominators must derive category counts from the current source set | LESSON-PREFLIGHT.json LESSON-REQ-0101 |
| `LESSON-REQ-0102` | `lesson:LSN-0103` | yes | `COMPLETE` | Verify adversarial fixtures must hash the complete validated contract | LESSON-PREFLIGHT.json LESSON-REQ-0102 |
| `LESSON-REQ-0103` | `lesson:LSN-0104` | yes | `COMPLETE` | Verify intermediate closure and independent validation must have unambiguous contracts | LESSON-PREFLIGHT.json LESSON-REQ-0103 |
| `LESSON-REQ-0104` | `lesson:LSN-0105` | yes | `COMPLETE` | Verify new behavioral tests must satisfy the unchanged source-quality contract | LESSON-PREFLIGHT.json LESSON-REQ-0104 |
| `LESSON-REQ-0105` | `lesson:LSN-0106` | yes | `COMPLETE` | Verify a security repair must execute at the causal output boundary, not a similarly shaped branch | LESSON-PREFLIGHT.json LESSON-REQ-0105 |
| `LESSON-REQ-0106` | `lesson:LSN-0107` | yes | `COMPLETE` | Verify an adversarial marker must satisfy the canonical detector before it can judge containment | LESSON-PREFLIGHT.json LESSON-REQ-0106 |
| `LESSON-REQ-0107` | `lesson:LSN-0108` | yes | `COMPLETE` | Verify evidence timestamp transport must preserve RFC3339 rather than a shell locale rendering | LESSON-PREFLIGHT.json LESSON-REQ-0107 |
| `LESSON-REQ-0108` | `lesson:LSN-0109` | yes | `COMPLETE` | Verify regression counts and evidence must exclude only policy-bound live input repositories | LESSON-PREFLIGHT.json LESSON-REQ-0108 |
| `LESSON-REQ-0109` | `lesson:LSN-0110` | yes | `COMPLETE` | Verify a timed-out live proof retains bounded diagnostics before owned cleanup | LESSON-PREFLIGHT.json LESSON-REQ-0109 |
| `LESSON-REQ-0110` | `lesson:LSN-0111` | yes | `COMPLETE` | Verify polling watcher cleanup must preserve completed checks and accepted cancellation | LESSON-PREFLIGHT.json LESSON-REQ-0110 |
| `LESSON-REQ-0111` | `lesson:LSN-0112` | yes | `COMPLETE` | Verify canonical scanner consumers must share transport decoding, not only patterns | LESSON-PREFLIGHT.json LESSON-REQ-0111 |
| `LESSON-REQ-0112` | `lesson:LSN-0113` | yes | `COMPLETE` | Verify stronger delivery controls must follow the immutable subject policy version | LESSON-PREFLIGHT.json LESSON-REQ-0112 |
| `LESSON-REQ-0113` | `lesson:LSN-0114` | yes | `COMPLETE` | Verify transport line metadata must not repeatedly scan the source prefix | LESSON-PREFLIGHT.json LESSON-REQ-0113 |
| `LESSON-REQ-0114` | `lesson:LSN-0115` | yes | `COMPLETE` | Verify a failing full verifier retains every bounded case identifier beyond its output tail | LESSON-PREFLIGHT.json LESSON-REQ-0114 |
| `LESSON-REQ-0115` | `lesson:LSN-0116` | yes | `COMPLETE` | Verify a live resumability pointer is generated after Git boundaries, not committed into its own subject | LESSON-PREFLIGHT.json LESSON-REQ-0115 |
| `LESSON-REQ-0116` | `lesson:LSN-0117` | yes | `COMPLETE` | Verify an architecture rollup must not contradict the delivered capability described below it | LESSON-PREFLIGHT.json LESSON-REQ-0116 |
| `LESSON-REQ-0117` | `lesson:LSN-0118` | yes | `COMPLETE` | Verify post-response validation failures must preserve an accepted mutation's uncertain outcome | LESSON-PREFLIGHT.json LESSON-REQ-0117 |
| `LESSON-REQ-0118` | `lesson:LSN-0119` | yes | `COMPLETE` | Verify a clean publication scan does not replace the stricter checkpoint secret scan | LESSON-PREFLIGHT.json LESSON-REQ-0118 |
| `LESSON-REQ-0119` | `lesson:LSN-0120` | yes | `COMPLETE` | Verify native installation proofs must resolve the installed CLI entrypoint | LESSON-PREFLIGHT.json LESSON-REQ-0119 |
| `LESSON-REQ-0120` | `lesson:LSN-0121` | yes | `COMPLETE` | Verify standard-library host probes must not initialize application dependency graphs | LESSON-PREFLIGHT.json LESSON-REQ-0120 |
| `LESSON-REQ-0121` | `lesson:LSN-0122` | yes | `COMPLETE` | Verify engine-allocated host ports must be rediscovered after container restart | LESSON-PREFLIGHT.json LESSON-REQ-0121 |
| `LESSON-REQ-0122` | `lesson:LSN-0123` | yes | `COMPLETE` | Verify consent binds workspace identity, not an uncanonicalized path spelling | LESSON-PREFLIGHT.json LESSON-REQ-0122 |
| `LESSON-REQ-0123` | `lesson:LSN-0124` | yes | `COMPLETE` | Verify durable editor recovery must not use an in-memory test host | LESSON-PREFLIGHT.json LESSON-REQ-0123 |
| `LESSON-REQ-0124` | `lesson:LSN-0125` | yes | `COMPLETE` | Verify native parent exit is not proof of process and profile cleanup | LESSON-PREFLIGHT.json LESSON-REQ-0124 |
| `LESSON-REQ-0125` | `lesson:LSN-0126` | yes | `COMPLETE` | Verify known authentication material is not domain or presentation data | LESSON-PREFLIGHT.json LESSON-REQ-0125 |
| `LESSON-REQ-0126` | `lesson:LSN-0127` | yes | `COMPLETE` | Verify fresh runtime health does not initialize an operator-managed model catalog | LESSON-PREFLIGHT.json LESSON-REQ-0126 |
| `LESSON-REQ-0127` | `lesson:LSN-0128` | yes | `COMPLETE` | Verify adversarial premises must use the actual public contract | LESSON-PREFLIGHT.json LESSON-REQ-0127 |
| `LESSON-REQ-0128` | `lesson:LSN-0129` | yes | `COMPLETE` | Verify repeated cancellation must preserve an already cancelled terminal result | LESSON-PREFLIGHT.json LESSON-REQ-0128 |
| `LESSON-REQ-0129` | `lesson:LSN-0130` | yes | `COMPLETE` | Verify executable export line endings belong to the source and packaging contract | LESSON-PREFLIGHT.json LESSON-REQ-0129 |
| `LESSON-REQ-0130` | `lesson:LSN-0131` | yes | `COMPLETE` | Verify raw evidence digests require byte-preserving Git export, not text normalization | LESSON-PREFLIGHT.json LESSON-REQ-0130 |
| `LESSON-REQ-0131` | `lesson:LSN-0132` | yes | `COMPLETE` | Verify owned Git clones need read-only-aware cleanup, not native-profile lock retry | LESSON-PREFLIGHT.json LESSON-REQ-0131 |
| `LESSON-REQ-0132` | `lesson:LSN-0133` | yes | `COMPLETE` | Verify shared field names do not imply shared schema types | LESSON-PREFLIGHT.json LESSON-REQ-0132 |
| `LESSON-REQ-0133` | `lesson:LSN-0134` | yes | `COMPLETE` | Verify configuration classifiers consume decoded values, not dotenv quote syntax | LESSON-PREFLIGHT.json LESSON-REQ-0133 |
| `LESSON-REQ-0134` | `lesson:LSN-0135` | yes | `COMPLETE` | Verify capture producer evidence before fallible interpretation or owned cleanup | LESSON-PREFLIGHT.json LESSON-REQ-0134 |
