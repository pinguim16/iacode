# Closure Requirements - GATE-3-CP-0003

Derived from the canonical sources listed below, before implementation. The expected set
is recomputed by `policies.expected_requirement_refs` and compared exactly with the
declared set, so a requirement cannot be dropped and the denominator cannot be reduced.

## Sources

- SOURCE A: docs/GATE-3-CHECKLIST.md, the canonical GATE-3 specification
- SOURCE B: docs/MILESTONE-VALIDATION.md, the milestone requirements of the audit
- SOURCE C: docs/checkpoints/GATE-3-CP-0002/REVIEW-REPORT.md, the findings of M1-CP-0002
- SOURCE D: LESSON-PREFLIGHT.json, the lessons the engineering memory imposes

## Requirements

| ID | Source | Anchor | Mandatory | Implementation | Final | Description |
|---|---|---|---|---|---|---|
| `REQ-0001` | GATE_SPECIFICATION | `canonical:GATE-3#1.1` | yes | `NOT_STARTED` | `NOT_STARTED` | A canonical, machine-readable requirement specification exists for this Gate and the registry mirrors it row for row. |
| `REQ-0002` | GATE_SPECIFICATION | `canonical:GATE-3#1.2` | yes | `NOT_STARTED` | `NOT_STARTED` | The closed mandatory gate registry carries the executable gate this Gate introduces, and that gate builds what it measures before measuring it. |
| `REQ-0003` | GATE_SPECIFICATION | `canonical:GATE-3#1.3` | yes | `NOT_STARTED` | `NOT_STARTED` | The test suite this Gate introduces is declared canonically, is counted by the count derivation and is resolvable as evidence. |
| `REQ-0004` | GATE_SPECIFICATION | `canonical:GATE-3#1.4` | yes | `NOT_STARTED` | `NOT_STARTED` | The internal Red Team battery of this Gate is executable, scoped to the sandbox, runs its attacks against the real container engine and records a null-mutation control. |
| `REQ-0005` | GATE_SPECIFICATION | `canonical:GATE-3#1.5` | yes | `NOT_STARTED` | `NOT_STARTED` | The reservation of the sandbox directory is consumed by the Gate that owns it, and every reservation of a later Gate is still enforced. |
| `REQ-0006` | GATE_SPECIFICATION | `canonical:GATE-3#1.6` | yes | `NOT_STARTED` | `NOT_STARTED` | One documented command verifies this Gate, adds the stages it introduces and keeps a targeted mode that does not restart the stack. |
| `REQ-0007` | GATE_SPECIFICATION | `canonical:GATE-3#2.1` | yes | `NOT_STARTED` | `NOT_STARTED` | The repository publishes to exactly one authorised remote, and a remote pointing anywhere else is refused rather than used. |
| `REQ-0008` | GATE_SPECIFICATION | `canonical:GATE-3#2.2` | yes | `NOT_STARTED` | `NOT_STARTED` | The whole history was scanned for credentials before its first publication, and a finding names the commit, the file, the line and the kind but never the value. |
| `REQ-0009` | GATE_SPECIFICATION | `canonical:GATE-3#2.3` | yes | `NOT_STARTED` | `NOT_STARTED` | The published history carries no credential, and the check is repeatable against the history as it now stands. |
| `REQ-0010` | GATE_SPECIFICATION | `canonical:GATE-3#2.4` | yes | `NOT_STARTED` | `NOT_STARTED` | Every push is preceded by a scan of exactly the staged content, and an allowance matches a value's digest rather than a path. |
| `REQ-0011` | GATE_SPECIFICATION | `canonical:GATE-3#2.5` | yes | `NOT_STARTED` | `NOT_STARTED` | Whether the branch and the checkpoint tag are on the remote is asked of the remote, an unpushed commit or a missing tag fails, and an unreachable remote is never a pass. |
| `REQ-0012` | GATE_SPECIFICATION | `canonical:GATE-3#2.6` | yes | `NOT_STARTED` | `NOT_STARTED` | The commit, push, tag and correction rules are stated in the development contract and recorded as a decision: atomic commits, green commits only, no rewriting of published history, no moving of a published tag, and no credential in a URL, a configuration or a versioned file. |
| `REQ-0013` | GATE_SPECIFICATION | `canonical:GATE-3#2.7` | yes | `NOT_STARTED` | `NOT_STARTED` | The history of this Gate's development is preserved as observable data — requirement, commits, tests, fixes, checkpoint — and nothing in it is marked as training-eligible. |
| `REQ-0014` | GATE_SPECIFICATION | `canonical:GATE-3#3.1` | yes | `NOT_STARTED` | `NOT_STARTED` | A command the ledger could not replay is refused before it executes, the refusal is itself recorded, and the recorder and the validator apply one shared replayability rule. |
| `REQ-0015` | GATE_SPECIFICATION | `canonical:GATE-3#3.2` | yes | `NOT_STARTED` | `NOT_STARTED` | A guardrail entry that names a file or a path where a test is required is refused, and lesson validation and guardrail effectiveness resolve an entry through one function. |
| `REQ-0016` | GATE_SPECIFICATION | `canonical:GATE-3#3.3` | yes | `NOT_STARTED` | `NOT_STARTED` | The committed lesson index is the render of the memory, and a memory changed without re-rendering it, or an index edited by hand, is refused under the memory policy that introduced the rule. |
| `REQ-0017` | GATE_SPECIFICATION | `canonical:GATE-3#3.4` | yes | `NOT_STARTED` | `NOT_STARTED` | The event stream of a run that is already terminal delivers every event after the cursor, however many pages that takes, before it closes. |
| `REQ-0018` | GATE_SPECIFICATION | `canonical:GATE-3#3.5` | yes | `NOT_STARTED` | `NOT_STARTED` | A canonical ADR index exists, lists every record with its title and status, resolves every link, and its test asserts rather than skips. |
| `REQ-0019` | GATE_SPECIFICATION | `canonical:GATE-3#4.1` | yes | `NOT_STARTED` | `NOT_STARTED` | The sandbox is its own service in the directory the scope registry reserved for it, with its own contracts, and the decision is recorded. |
| `REQ-0020` | GATE_SPECIFICATION | `canonical:GATE-3#4.2` | yes | `NOT_STARTED` | `NOT_STARTED` | No sandbox logic lives in the API routes, the Agent Runtime or the Model Gateway: none of them imports the sandbox package or a container client. |
| `REQ-0021` | GATE_SPECIFICATION | `canonical:GATE-3#4.3` | yes | `NOT_STARTED` | `NOT_STARTED` | The Agent Runtime and the workflow that drives it still execute nothing themselves; a tool reaches the sandbox only as an activity on the sandbox's own task queue. |
| `REQ-0022` | GATE_SPECIFICATION | `canonical:GATE-3#4.4` | yes | `NOT_STARTED` | `NOT_STARTED` | Inside the sandbox service only the engine backend and the in-container helper start a process, and the controller never uses a shell. |
| `REQ-0023` | GATE_SPECIFICATION | `canonical:GATE-3#4.5` | yes | `NOT_STARTED` | `NOT_STARTED` | The controller starts only the container client, with an argument vector, and never a command a request supplied. |
| `REQ-0024` | GATE_SPECIFICATION | `canonical:GATE-3#4.6` | yes | `NOT_STARTED` | `NOT_STARTED` | The controller is the only service given the container engine, and it holds no capability, cannot gain one, and publishes no port. |
| `REQ-0025` | GATE_SPECIFICATION | `canonical:GATE-3#5.1` | yes | `NOT_STARTED` | `NOT_STARTED` | Versioned contracts exist for the sandbox session, the policy, the workspace, the execution request, the execution result, the command execution, the file operation, the Git operation and the artifact reference. |
| `REQ-0026` | GATE_SPECIFICATION | `canonical:GATE-3#5.2` | yes | `NOT_STARTED` | `NOT_STARTED` | A contract of another version is refused rather than interpreted, and a request carrying a field the contract does not declare or missing one it requires is refused. |
| `REQ-0027` | GATE_SPECIFICATION | `canonical:GATE-3#5.3` | yes | `NOT_STARTED` | `NOT_STARTED` | A command result carries the exit code, standard output, standard error, duration, whether it timed out, whether it was truncated and its artifact references, and no exit code is invented for a command that never started. |
| `REQ-0028` | GATE_SPECIFICATION | `canonical:GATE-3#5.4` | yes | `NOT_STARTED` | `NOT_STARTED` | The execution status, session state, workspace and operation vocabularies are closed, and the database accepts exactly the declared ones. |
| `REQ-0029` | GATE_SPECIFICATION | `canonical:GATE-3#5.5` | yes | `NOT_STARTED` | `NOT_STARTED` | The result an agent receives cannot present a cancellation, a denial or a timeout as a success. |
| `REQ-0030` | GATE_SPECIFICATION | `canonical:GATE-3#6.1` | yes | `NOT_STARTED` | `NOT_STARTED` | An explicit registry names every executable tool — list, read, write, patch and search of files, shell execution, and the local Git status, diff, log, show, add and commit — and only a registered name can execute. |
| `REQ-0031` | GATE_SPECIFICATION | `canonical:GATE-3#6.2` | yes | `NOT_STARTED` | `NOT_STARTED` | An unknown tool name is refused, and no name is ever mapped to a shell. |
| `REQ-0032` | GATE_SPECIFICATION | `canonical:GATE-3#6.3` | yes | `NOT_STARTED` | `NOT_STARTED` | A canonical sandbox tool policy defines, per policy, the allowed tools, the resource profile, the network profile, the workspace permissions, the command timeout and the output limits. |
| `REQ-0033` | GATE_SPECIFICATION | `canonical:GATE-3#6.4` | yes | `NOT_STARTED` | `NOT_STARTED` | A tool the run's policy does not allow is refused, a policy naming an unregistered tool is refused, and an unknown policy is refused. |
| `REQ-0034` | GATE_SPECIFICATION | `canonical:GATE-3#6.5` | yes | `NOT_STARTED` | `NOT_STARTED` | Tool arguments are structured and typed: an undeclared argument is refused, and a wrong type, an absent value and a wrong value each carry their own reason. |
| `REQ-0035` | GATE_SPECIFICATION | `canonical:GATE-3#6.6` | yes | `NOT_STARTED` | `NOT_STARTED` | No request can change its policy, its limits, its network or its mounts; a request that tries is denied, and a request may lower a timeout but never raise it. |
| `REQ-0036` | GATE_SPECIFICATION | `canonical:GATE-3#6.7` | yes | `NOT_STARTED` | `NOT_STARTED` | The limits a tool runs under come from the policy, and every limit a policy applies is inside its declared bound. |
| `REQ-0037` | GATE_SPECIFICATION | `canonical:GATE-3#6.8` | yes | `NOT_STARTED` | `NOT_STARTED` | A policy document with an unknown key, or a read-only policy that allows a writing tool, is refused when it is loaded. |
| `REQ-0038` | GATE_SPECIFICATION | `canonical:GATE-3#6.9` | yes | `NOT_STARTED` | `NOT_STARTED` | Tools the policy allows execute automatically, inside the sandbox, without a confirmation per call; nothing is executed on the host under any policy. |
| `REQ-0039` | GATE_SPECIFICATION | `canonical:GATE-3#7.1` | yes | `NOT_STARTED` | `NOT_STARTED` | Every run executes in its own disposable container with its own workspace; two runs never share either. |
| `REQ-0040` | GATE_SPECIFICATION | `canonical:GATE-3#7.2` | yes | `NOT_STARTED` | `NOT_STARTED` | The sandbox runs unprivileged, as a non-root user, with every capability dropped and no way to gain privileges. |
| `REQ-0041` | GATE_SPECIFICATION | `canonical:GATE-3#7.3` | yes | `NOT_STARTED` | `NOT_STARTED` | The root filesystem is read-only, and the only writable places are the workspace and a temporary directory, both in-memory filesystems with a size limit. |
| `REQ-0042` | GATE_SPECIFICATION | `canonical:GATE-3#7.4` | yes | `NOT_STARTED` | `NOT_STARTED` | The container engine's socket, and any other engine endpoint, is absent from a sandbox. |
| `REQ-0043` | GATE_SPECIFICATION | `canonical:GATE-3#7.5` | yes | `NOT_STARTED` | `NOT_STARTED` | No host path is mounted into a sandbox — no drive, no root, no home, no profile, no SSH directory, no credential store, no secret environment file — and no argument of a request can add one. |
| `REQ-0044` | GATE_SPECIFICATION | `canonical:GATE-3#7.6` | yes | `NOT_STARTED` | `NOT_STARTED` | Every sandbox container carries labels naming the service instance that owns it, the session, the run, the policy and its expiry, so ownership is read from the engine rather than from memory. |
| `REQ-0045` | GATE_SPECIFICATION | `canonical:GATE-3#8.1` | yes | `NOT_STARTED` | `NOT_STARTED` | CPU, memory, process count, workspace size, execution timeout and output size are mandatory, configurable limits, and a zero, negative, absurd or missing value is refused. |
| `REQ-0046` | GATE_SPECIFICATION | `canonical:GATE-3#8.2` | yes | `NOT_STARTED` | `NOT_STARTED` | The memory limit holds the in-memory filesystems, so a full workspace cannot starve the processes of the limit they were promised. |
| `REQ-0047` | GATE_SPECIFICATION | `canonical:GATE-3#8.3` | yes | `NOT_STARTED` | `NOT_STARTED` | A process that multiplies without end is contained by the process limit, and the sandbox remains usable afterwards. |
| `REQ-0048` | GATE_SPECIFICATION | `canonical:GATE-3#8.4` | yes | `NOT_STARTED` | `NOT_STARTED` | A process that exceeds the memory limit fails in a controlled way, and the host is unaffected. |
| `REQ-0049` | GATE_SPECIFICATION | `canonical:GATE-3#8.5` | yes | `NOT_STARTED` | `NOT_STARTED` | The workspace cannot outgrow its limit. |
| `REQ-0050` | GATE_SPECIFICATION | `canonical:GATE-3#8.6` | yes | `NOT_STARTED` | `NOT_STARTED` | A command that exceeds its timeout is ended together with every process it started, including a process that left its session, and nothing is left running. |
| `REQ-0051` | GATE_SPECIFICATION | `canonical:GATE-3#8.7` | yes | `NOT_STARTED` | `NOT_STARTED` | Standard output and standard error are bounded while they are read; what exceeds the bound is truncated explicitly and stored whole as an artifact, and memory is never unbounded. |
| `REQ-0052` | GATE_SPECIFICATION | `canonical:GATE-3#9.1` | yes | `NOT_STARTED` | `NOT_STARTED` | A sandbox has no network by default: only loopback exists, and every policy the Gate ships denies the network. |
| `REQ-0053` | GATE_SPECIFICATION | `canonical:GATE-3#9.2` | yes | `NOT_STARTED` | `NOT_STARTED` | An attempt to reach an external address from a sandbox without network fails. |
| `REQ-0054` | GATE_SPECIFICATION | `canonical:GATE-3#9.3` | yes | `NOT_STARTED` | `NOT_STARTED` | The one other network profile is local services only, on an internal network with no route outside, and it is chosen by the policy, never by a request. |
| `REQ-0055` | GATE_SPECIFICATION | `canonical:GATE-3#9.4` | yes | `NOT_STARTED` | `NOT_STARTED` | No package installation from the internet is offered; the image carries the toolchain the Gate's tests need. |
| `REQ-0056` | GATE_SPECIFICATION | `canonical:GATE-3#10.1` | yes | `NOT_STARTED` | `NOT_STARTED` | A sandbox receives only the variables its policy explicitly allows, and no variable of the controller — provider key, repository token, agent socket, cloud credential or engine address — reaches it. |
| `REQ-0057` | GATE_SPECIFICATION | `canonical:GATE-3#10.2` | yes | `NOT_STARTED` | `NOT_STARTED` | A command's environment inside the sandbox is the allowlist and nothing else. |
| `REQ-0058` | GATE_SPECIFICATION | `canonical:GATE-3#10.3` | yes | `NOT_STARTED` | `NOT_STARTED` | A policy cannot allow a credential-shaped variable into a command's environment. |
| `REQ-0059` | GATE_SPECIFICATION | `canonical:GATE-3#10.4` | yes | `NOT_STARTED` | `NOT_STARTED` | No Git credential, credential helper, SSH key or agent socket exists in a sandbox. |
| `REQ-0060` | GATE_SPECIFICATION | `canonical:GATE-3#11.1` | yes | `NOT_STARTED` | `NOT_STARTED` | A workspace has an identity and an explicit lifecycle, belongs to exactly one run, and a run holds at most one active session. |
| `REQ-0061` | GATE_SPECIFICATION | `canonical:GATE-3#11.2` | yes | `NOT_STARTED` | `NOT_STARTED` | A workspace is provisioned only from an authorised snapshot, named by its artifact identifier and never by a path, and becomes a repository the tools can work on. |
| `REQ-0062` | GATE_SPECIFICATION | `canonical:GATE-3#11.3` | yes | `NOT_STARTED` | `NOT_STARTED` | Anything but a workspace snapshot artifact is refused before the run exists, and a snapshot for a team that executes no tool is refused. |
| `REQ-0063` | GATE_SPECIFICATION | `canonical:GATE-3#11.4` | yes | `NOT_STARTED` | `NOT_STARTED` | A snapshot whose digest differs from its record, or that carries a link or an escaping member, is refused, and no session survives the refusal. |
| `REQ-0064` | GATE_SPECIFICATION | `canonical:GATE-3#11.5` | yes | `NOT_STARTED` | `NOT_STARTED` | One run cannot read or write another run's files, nor see its processes. |
| `REQ-0065` | GATE_SPECIFICATION | `canonical:GATE-3#11.6` | yes | `NOT_STARTED` | `NOT_STARTED` | The development working tree of this repository is never an agent's workspace. |
| `REQ-0066` | GATE_SPECIFICATION | `canonical:GATE-3#12.1` | yes | `NOT_STARTED` | `NOT_STARTED` | One canonical path resolver decides every path a tool touches; no other module re-implements path safety. |
| `REQ-0067` | GATE_SPECIFICATION | `canonical:GATE-3#12.2` | yes | `NOT_STARTED` | `NOT_STARTED` | Traversal, absolute paths, drive letters, UNC paths, null bytes and normalisation tricks are refused, each with its own reason. |
| `REQ-0068` | GATE_SPECIFICATION | `canonical:GATE-3#12.3` | yes | `NOT_STARTED` | `NOT_STARTED` | A link inside the workspace that points outside it cannot be read or written through, whether it names a file, a directory, the root or climbs out relatively; a link that stays inside is followed. |
| `REQ-0069` | GATE_SPECIFICATION | `canonical:GATE-3#12.4` | yes | `NOT_STARTED` | `NOT_STARTED` | Listing, reading, writing, searching and patching work inside the workspace of a real sandbox. |
| `REQ-0070` | GATE_SPECIFICATION | `canonical:GATE-3#12.5` | yes | `NOT_STARTED` | `NOT_STARTED` | A read and a write are bounded in size, an oversized one is refused, and binary content is refused as text rather than mangled. |
| `REQ-0071` | GATE_SPECIFICATION | `canonical:GATE-3#12.6` | yes | `NOT_STARTED` | `NOT_STARTED` | A write validates its parent directory and replaces the file atomically. |
| `REQ-0072` | GATE_SPECIFICATION | `canonical:GATE-3#12.7` | yes | `NOT_STARTED` | `NOT_STARTED` | A patch applies only inside the workspace; a patch whose context does not match, or that has one bad file, changes nothing. |
| `REQ-0073` | GATE_SPECIFICATION | `canonical:GATE-3#12.8` | yes | `NOT_STARTED` | `NOT_STARTED` | A search is confined to the workspace and bounded in results, output and duration. |
| `REQ-0074` | GATE_SPECIFICATION | `canonical:GATE-3#12.9` | yes | `NOT_STARTED` | `NOT_STARTED` | A path refused inside the sandbox reaches the agent as a denial, not as a failure of the sandbox. |
| `REQ-0075` | GATE_SPECIFICATION | `canonical:GATE-3#13.1` | yes | `NOT_STARTED` | `NOT_STARTED` | Shell execution runs only inside the sandbox container, with the command, the working directory, the allowed environment and the timeout passed as structured arguments. |
| `REQ-0076` | GATE_SPECIFICATION | `canonical:GATE-3#13.2` | yes | `NOT_STARTED` | `NOT_STARTED` | Standard output, standard error, a zero and a non-zero exit code, a missing executable and a child process are all reported faithfully. |
| `REQ-0077` | GATE_SPECIFICATION | `canonical:GATE-3#13.3` | yes | `NOT_STARTED` | `NOT_STARTED` | The working directory resolves inside the workspace, and an escaping one is refused. |
| `REQ-0078` | GATE_SPECIFICATION | `canonical:GATE-3#13.4` | yes | `NOT_STARTED` | `NOT_STARTED` | A payload that tries to reach a host command affects only the sandbox, inside its policy, and the host is unchanged. |
| `REQ-0079` | GATE_SPECIFICATION | `canonical:GATE-3#13.5` | yes | `NOT_STARTED` | `NOT_STARTED` | A command still running when its run is cancelled is stopped, with every process it started. |
| `REQ-0080` | GATE_SPECIFICATION | `canonical:GATE-3#14.1` | yes | `NOT_STARTED` | `NOT_STARTED` | Inside the workspace an agent can read the status, the working and the staged diff, the log and a commit, stage files and commit locally. |
| `REQ-0081` | GATE_SPECIFICATION | `canonical:GATE-3#14.2` | yes | `NOT_STARTED` | `NOT_STARTED` | Every Git tool builds a fixed argument vector, a revision that looks like an option is refused, and a commit skips hooks and carries its message as one argument. |
| `REQ-0082` | GATE_SPECIFICATION | `canonical:GATE-3#14.3` | yes | `NOT_STARTED` | `NOT_STARTED` | No remote Git operation is offered or possible — no push, fetch, clone or remote — and no destructive operation — hard reset, clean, rebase, history filtering, forced push — is offered by default. |
| `REQ-0083` | GATE_SPECIFICATION | `canonical:GATE-3#14.4` | yes | `NOT_STARTED` | `NOT_STARTED` | An agent's commits carry an explicit sandbox identity that is not a person, separate from the owner's development identity, and the difference is documented. |
| `REQ-0084` | GATE_SPECIFICATION | `canonical:GATE-3#14.5` | yes | `NOT_STARTED` | `NOT_STARTED` | Git output is bounded like any other output. |
| `REQ-0085` | GATE_SPECIFICATION | `canonical:GATE-3#15.1` | yes | `NOT_STARTED` | `NOT_STARTED` | A session moves through explicit states, is created ready for its run and is removed with it. |
| `REQ-0086` | GATE_SPECIFICATION | `canonical:GATE-3#15.2` | yes | `NOT_STARTED` | `NOT_STARTED` | A running tool holds its session in the running state, and inspecting a session reports the store and the engine side by side. |
| `REQ-0087` | GATE_SPECIFICATION | `canonical:GATE-3#15.3` | yes | `NOT_STARTED` | `NOT_STARTED` | When a run ends or is cancelled its sandbox is removed, and no container or temporary volume is left behind. |
| `REQ-0088` | GATE_SPECIFICATION | `canonical:GATE-3#15.4` | yes | `NOT_STARTED` | `NOT_STARTED` | A restarted service reconciles from the store and the engine rather than from memory: it keeps a live session, removes a container no session owns, and fails a session whose container vanished. |
| `REQ-0089` | GATE_SPECIFICATION | `canonical:GATE-3#15.5` | yes | `NOT_STARTED` | `NOT_STARTED` | Reconciliation touches only containers this service instance owns, so another stack or a test on the same engine is never cleaned up by it. |
| `REQ-0090` | GATE_SPECIFICATION | `canonical:GATE-3#15.6` | yes | `NOT_STARTED` | `NOT_STARTED` | An orphan sweeper expires only sessions that have expired and are not running, in bounded, deterministic batches, and never removes an active workspace. |
| `REQ-0091` | GATE_SPECIFICATION | `canonical:GATE-3#16.1` | yes | `NOT_STARTED` | `NOT_STARTED` | This Gate adds its schema through a new migration and edits no migration that has already been applied. |
| `REQ-0092` | GATE_SPECIFICATION | `canonical:GATE-3#16.2` | yes | `NOT_STARTED` | `NOT_STARTED` | The existing tool call, artifact and run entities are evolved rather than duplicated, and the one new table holds only what nothing else could: the sandbox session. |
| `REQ-0093` | GATE_SPECIFICATION | `canonical:GATE-3#16.3` | yes | `NOT_STARTED` | `NOT_STARTED` | A database created from nothing reaches the head revision, and a database at the previous Gate's head upgrades without losing a row. |
| `REQ-0094` | GATE_SPECIFICATION | `canonical:GATE-3#16.4` | yes | `NOT_STARTED` | `NOT_STARTED` | Every execution is traceable from the task through the run, the agent run, the tool request, the sandbox session and the execution to the result, and none of it holds private reasoning. |
| `REQ-0095` | GATE_SPECIFICATION | `canonical:GATE-3#16.5` | yes | `NOT_STARTED` | `NOT_STARTED` | A retried request never executes twice: the execution is keyed by the tool request it answers. |
| `REQ-0096` | GATE_SPECIFICATION | `canonical:GATE-3#16.6` | yes | `NOT_STARTED` | `NOT_STARTED` | The store the service runs against in the stack records sessions and executions in the real database with the same behaviour the suite asserts in memory. |
| `REQ-0097` | GATE_SPECIFICATION | `canonical:GATE-3#16.7` | yes | `NOT_STARTED` | `NOT_STARTED` | Nothing this Gate persists is training-eligible, and no table stores a credential. |
| `REQ-0098` | GATE_SPECIFICATION | `canonical:GATE-3#17.1` | yes | `NOT_STARTED` | `NOT_STARTED` | A pending tool request of a stage with a sandbox policy is checked against the policy, executed in the run's sandbox, its result persisted, and the workflow resumes. |
| `REQ-0099` | GATE_SPECIFICATION | `canonical:GATE-3#17.2` | yes | `NOT_STARTED` | `NOT_STARTED` | A stage without a sandbox policy keeps the previous Gate's behaviour: the request waits for a result delivered through the API. |
| `REQ-0100` | GATE_SPECIFICATION | `canonical:GATE-3#17.3` | yes | `NOT_STARTED` | `NOT_STARTED` | The run plan names the sandbox policy of each stage and the workspace source, frozen when the run is created. |
| `REQ-0101` | GATE_SPECIFICATION | `canonical:GATE-3#17.4` | yes | `NOT_STARTED` | `NOT_STARTED` | A tool result returns to the agent as labelled data in its own channel and never as an instruction. |
| `REQ-0102` | GATE_SPECIFICATION | `canonical:GATE-3#17.5` | yes | `NOT_STARTED` | `NOT_STARTED` | A large result reaches the model truncated inline with an artifact reference, within the size the runtime accepts for a tool result. |
| `REQ-0103` | GATE_SPECIFICATION | `canonical:GATE-3#17.6` | yes | `NOT_STARTED` | `NOT_STARTED` | A tool that times out returns a normalised error result the agent receives, and the run never stays waiting for a tool for ever. |
| `REQ-0104` | GATE_SPECIFICATION | `canonical:GATE-3#17.7` | yes | `NOT_STARTED` | `NOT_STARTED` | Cancelling a run during a long command stops the command, records the cancellation, ends the run cancelled and leaves no process behind. |
| `REQ-0105` | GATE_SPECIFICATION | `canonical:GATE-3#17.8` | yes | `NOT_STARTED` | `NOT_STARTED` | A sandbox service restart while a run executes does not lose the run: the session is reconciled and the run completes. |
| `REQ-0106` | GATE_SPECIFICATION | `canonical:GATE-3#18.1` | yes | `NOT_STARTED` | `NOT_STARTED` | A profile that may request tools names the sandbox policy that governs them, and a profile with tools and no policy is refused. |
| `REQ-0107` | GATE_SPECIFICATION | `canonical:GATE-3#18.2` | yes | `NOT_STARTED` | `NOT_STARTED` | No agent is given every tool: each profile's permitted actions are within its policy's tools. |
| `REQ-0108` | GATE_SPECIFICATION | `canonical:GATE-3#18.3` | yes | `NOT_STARTED` | `NOT_STARTED` | A developer profile may read, search, write, patch, run tests and use the local Git tools its policy allows. |
| `REQ-0109` | GATE_SPECIFICATION | `canonical:GATE-3#18.4` | yes | `NOT_STARTED` | `NOT_STARTED` | The reviewer is read-only: read, search, diff and test results, and no writing tool. |
| `REQ-0110` | GATE_SPECIFICATION | `canonical:GATE-3#18.5` | yes | `NOT_STARTED` | `NOT_STARTED` | The planner has no writing tool and works from context alone. |
| `REQ-0111` | GATE_SPECIFICATION | `canonical:GATE-3#18.6` | yes | `NOT_STARTED` | `NOT_STARTED` | A minimal coding team — planner, developer, reviewer — proves the flow, and no larger team is built. |
| `REQ-0112` | GATE_SPECIFICATION | `canonical:GATE-3#19.1` | yes | `NOT_STARTED` | `NOT_STARTED` | Full output, large diffs and workspace snapshots are stored in the existing artifact infrastructure, recorded as artifacts, and no second store is created. |
| `REQ-0113` | GATE_SPECIFICATION | `canonical:GATE-3#19.2` | yes | `NOT_STARTED` | `NOT_STARTED` | A workspace snapshot is created from an explicit source directory by a documented command, and never from the development working tree implicitly. |
| `REQ-0114` | GATE_SPECIFICATION | `canonical:GATE-3#20.1` | yes | `NOT_STARTED` | `NOT_STARTED` | A registry of sandbox image profiles exists, the architecture accepts new profiles, and one functional profile for this project carries Git and Python. |
| `REQ-0115` | GATE_SPECIFICATION | `canonical:GATE-3#20.2` | yes | `NOT_STARTED` | `NOT_STARTED` | The image is built as part of the Gate from a base pinned by digest and packages pinned by version, and never from a moving tag. |
| `REQ-0116` | GATE_SPECIFICATION | `canonical:GATE-3#20.3` | yes | `NOT_STARTED` | `NOT_STARTED` | The image is addressed by a fingerprint of its inputs, and a missing or stale image is refused rather than substituted. |
| `REQ-0117` | GATE_SPECIFICATION | `canonical:GATE-3#20.4` | yes | `NOT_STARTED` | `NOT_STARTED` | The sandbox gate builds the service image and the sandbox image before it measures anything. |
| `REQ-0118` | GATE_SPECIFICATION | `canonical:GATE-3#20.5` | yes | `NOT_STARTED` | `NOT_STARTED` | The sandbox service installs the one dependency lock the dependency scan reads, so its Python dependencies are scanned with the rest; the sandbox image's system packages are pinned by version, and what the scan does not cover is documented rather than implied. |
| `REQ-0119` | GATE_SPECIFICATION | `canonical:GATE-3#21.1` | yes | `NOT_STARTED` | `NOT_STARTED` | An internal service contract creates a session, executes a tool, inspects a session and terminates it, and it is reached only as activities on the sandbox's task queue. |
| `REQ-0120` | GATE_SPECIFICATION | `canonical:GATE-3#21.2` | yes | `NOT_STARTED` | `NOT_STARTED` | A refusal is recorded as an execution with its reason, so a denied request is as traceable as an executed one. |
| `REQ-0121` | GATE_SPECIFICATION | `canonical:GATE-3#21.3` | yes | `NOT_STARTED` | `NOT_STARTED` | The service's health is a poller on its queue and an engine that answers, not a process that exists. |
| `REQ-0122` | GATE_SPECIFICATION | `canonical:GATE-3#22.1` | yes | `NOT_STARTED` | `NOT_STARTED` | The service publishes instruments for sessions created and active, tool executions, their duration, failures, timeouts and policy refusals. |
| `REQ-0123` | GATE_SPECIFICATION | `canonical:GATE-3#22.2` | yes | `NOT_STARTED` | `NOT_STARTED` | Every metric label is low cardinality, a command never becomes a label, and a refusal is counted by its reason. |
| `REQ-0124` | GATE_SPECIFICATION | `canonical:GATE-3#22.3` | yes | `NOT_STARTED` | `NOT_STARTED` | Logs carry the run, the agent, the sandbox, the tool, the status and the duration, and never a whole result, a secret or the host environment. |
| `REQ-0125` | GATE_SPECIFICATION | `canonical:GATE-3#22.4` | yes | `NOT_STARTED` | `NOT_STARTED` | The observability stack scrapes the sandbox service. |
| `REQ-0126` | GATE_SPECIFICATION | `canonical:GATE-3#23.1` | yes | `NOT_STARTED` | `NOT_STARTED` | The run page shows each tool the sandbox executed: the tool, its status, its duration, the abbreviated sandbox identifier and a summary. |
| `REQ-0127` | GATE_SPECIFICATION | `canonical:GATE-3#23.2` | yes | `NOT_STARTED` | `NOT_STARTED` | The page never receives a tool's output and offers no interactive shell. |
| `REQ-0128` | GATE_SPECIFICATION | `canonical:GATE-3#23.3` | yes | `NOT_STARTED` | `NOT_STARTED` | The command line interface stays reserved for the Gate that owns it. |
| `REQ-0129` | GATE_SPECIFICATION | `canonical:GATE-3#24.1` | yes | `NOT_STARTED` | `NOT_STARTED` | A synthetic repository with a defective function and a failing test is provisioned as a snapshot, and a coding run over it reads the code, runs the failing test, patches the code, runs the passing test, reads the diff, commits locally, is reviewed and finishes. |
| `REQ-0130` | GATE_SPECIFICATION | `canonical:GATE-3#24.2` | yes | `NOT_STARTED` | `NOT_STARTED` | The scenario drives the real workflow, the real activities, the real sandbox service and the real container engine, with only the model replaced by a deterministic script. |
| `REQ-0131` | GATE_SPECIFICATION | `canonical:GATE-3#24.3` | yes | `NOT_STARTED` | `NOT_STARTED` | An automatic proof shows a shell request did not execute on the host: a sentinel outside the sandbox is neither created nor modified. |
| `REQ-0132` | GATE_SPECIFICATION | `canonical:GATE-3#24.4` | yes | `NOT_STARTED` | `NOT_STARTED` | The scenario asserts what the run recorded — its terminal state, its tool executions and the test that passed — rather than what the harness sent. |
| `REQ-0133` | GATE_SPECIFICATION | `canonical:GATE-3#25.1` | yes | `NOT_STARTED` | `NOT_STARTED` | The repository's one verification command covers this Gate, in its targeted and its full mode. |
| `REQ-0134` | GATE_SPECIFICATION | `canonical:GATE-3#25.2` | yes | `NOT_STARTED` | `NOT_STARTED` | A runbook documents the lifecycle, the tool policy, the filesystem, the shell, Git, the network, resources, artifacts, cleanup, debugging and the security boundary. |
| `REQ-0135` | GATE_SPECIFICATION | `canonical:GATE-3#25.3` | yes | `NOT_STARTED` | `NOT_STARTED` | The architecture, development, version and entry documents describe what this Gate delivered rather than what was planned. |
| `REQ-0136` | GATE_SPECIFICATION | `canonical:GATE-3#25.4` | yes | `NOT_STARTED` | `NOT_STARTED` | The structural decisions of this Gate are recorded as ADRs and listed in the index. |
| `REQ-0137` | GATE_SPECIFICATION | `canonical:GATE-3#25.5` | yes | `NOT_STARTED` | `NOT_STARTED` | The Gate produces its retrospective from the canonical template, and its reusable lessons are recorded with the guardrail that protects the property rather than one file. |
| `REQ-0138` | GATE_SPECIFICATION | `canonical:GATE-3#25.6` | yes | `NOT_STARTED` | `NOT_STARTED` | Every commit of the Gate and its checkpoint tag are on the authorised remote when the Gate closes. |
| `REQ-0139` | GATE_SPECIFICATION | `canonical:GATE-3#25.7` | yes | `NOT_STARTED` | `NOT_STARTED` | The Gate closes at the project's own internal verdict, leaves the milestone verdict to a fresh-session audit, and starts no part of the Gate that follows it. |
| `REQ-0140` | AUDIT_FINDING | `finding:M1-F-003` | yes | `NOT_STARTED` | `NOT_STARTED` | The published history cannot validate GATE-1-CP-0001, so every clean clone of the remote fails the mandatory tests gate |
| `REQ-0141` | AUDIT_FINDING | `finding:M1-F-001` | yes | `NOT_STARTED` | `NOT_STARTED` | A model is never shown the shape of a tool request, and the configured live model cannot make one |
| `REQ-0142` | AUDIT_FINDING | `finding:M1-F-002` | yes | `NOT_STARTED` | `NOT_STARTED` | The API accepts a tool result for a request the sandbox is executing, and the agent receives it instead of the sandbox's |
| `LESSON-REQ-0001` | LESSON | `lesson:LSN-0001` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify checkpoint validation must succeed from a detached checkout of the checkpoint tag |
| `LESSON-REQ-0002` | LESSON | `lesson:LSN-0002` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a file inventory must be recomputed from the repository, never trusted as an assertion |
| `LESSON-REQ-0003` | LESSON | `lesson:LSN-0003` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify every operation attempt must be auditable, including a refusal decided before execution |
| `LESSON-REQ-0004` | LESSON | `lesson:LSN-0004` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a checkpoint may never claim readiness while it also claims to be blocked |
| `LESSON-REQ-0005` | LESSON | `lesson:LSN-0005` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a PASS requires evidence that can be executed or resolved, not a statement |
| `LESSON-REQ-0006` | LESSON | `lesson:LSN-0006` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify the repository must be self-contained; a specification may not live outside it |
| `LESSON-REQ-0007` | LESSON | `lesson:LSN-0007` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify independent validation cannot be declared by the run that did the work |
| `LESSON-REQ-0008` | LESSON | `lesson:LSN-0008` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify requirement completeness must be total and evidence-backed before handoff |
| `LESSON-REQ-0009` | LESSON | `lesson:LSN-0009` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a red gate requires rework, never a waiver, and never a weakened check |
| `LESSON-REQ-0010` | LESSON | `lesson:LSN-0010` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a recorded command must carry runtime, working directory, commit and purpose to be replayable |
| `LESSON-REQ-0011` | LESSON | `lesson:LSN-0011` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a control over a checkpoint's own evidence must be scoped to the moment it matters |
| `LESSON-REQ-0012` | LESSON | `lesson:LSN-0012` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify sealed checkpoints and their tags are immutable, and tooling must keep validating them |
| `LESSON-REQ-0013` | LESSON | `lesson:LSN-0013` | no | `NOT_STARTED` | `NOT_STARTED` | Verify an installed capability must be detected by resolved path, not by a bare command lookup |
| `LESSON-REQ-0014` | LESSON | `lesson:LSN-0014` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify evidence must be recorded as it happens, not reconstructed at the end of a run |
| `LESSON-REQ-0015` | LESSON | `lesson:LSN-0015` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify every positive terminal status needs one shared promotion invariant |
| `LESSON-REQ-0016` | LESSON | `lesson:LSN-0016` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a mandatory set must be closed by policy, never chosen by the caller |
| `LESSON-REQ-0017` | LESSON | `lesson:LSN-0017` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a completeness denominator must come from a source the delivery does not own |
| `LESSON-REQ-0018` | LESSON | `lesson:LSN-0018` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a structured reference must be resolved, not merely well typed |
| `LESSON-REQ-0019` | LESSON | `lesson:LSN-0019` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a derived artifact must carry a fingerprint of the inputs that produced it |
| `LESSON-REQ-0020` | LESSON | `lesson:LSN-0020` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify evidence produced from a dirty tree needs immutable input identity |
| `LESSON-REQ-0021` | LESSON | `lesson:LSN-0021` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify sealed history needs an anchor outside the content it describes |
| `LESSON-REQ-0022` | LESSON | `lesson:LSN-0022` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify an authoritative count must be derived once, never maintained by hand twice |
| `LESSON-REQ-0023` | LESSON | `lesson:LSN-0023` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a lesson must cite a source that actually records the finding it claims |
| `LESSON-REQ-0024` | LESSON | `lesson:LSN-0024` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a control is finished only when its positive path has been executed, not only its refusals |
| `LESSON-REQ-0025` | LESSON | `lesson:LSN-0025` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a generic guardrail derives repository state instead of naming today's checkpoint |
| `LESSON-REQ-0026` | LESSON | `lesson:LSN-0026` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify an adversarial battery without a null-mutation control proves nothing |
| `LESSON-REQ-0027` | LESSON | `lesson:LSN-0027` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a lesson's prose may record a residual limit but may never contradict its status |
| `LESSON-REQ-0028` | LESSON | `lesson:LSN-0028` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a configuration key that no code reads is a defect, not documentation |
| `LESSON-REQ-0029` | LESSON | `lesson:LSN-0029` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a required protocol transition must never turn a mandatory gate red |
| `LESSON-REQ-0030` | LESSON | `lesson:LSN-0031` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify an empty applicable set is not a missing required set, and a control must tell them apart |
| `LESSON-REQ-0031` | LESSON | `lesson:LSN-0032` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a control written while one Gate was the only Gate stops being a control when the next one starts |
| `LESSON-REQ-0032` | LESSON | `lesson:LSN-0033` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a value bound in middleware is absent in the handlers that run outside it |
| `LESSON-REQ-0033` | LESSON | `lesson:LSN-0034` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify re-deriving what the framework already computed diverges from the framework |
| `LESSON-REQ-0034` | LESSON | `lesson:LSN-0035` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify captured subprocess output decoded or re-emitted with the platform codepage crashes the tool, not the work |
| `LESSON-REQ-0035` | LESSON | `lesson:LSN-0036` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a gate that runs inside an image measures the image, not the source |
| `LESSON-REQ-0036` | LESSON | `lesson:LSN-0037` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a shared control that names an identifier the repository derives stops being a control when that identifier moves |
| `LESSON-REQ-0037` | LESSON | `lesson:LSN-0038` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify two representations of one concept in one module disagree, and the safer one loses |
| `LESSON-REQ-0038` | LESSON | `lesson:LSN-0039` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a test that writes to the operational database leaves production data behind |
| `LESSON-REQ-0039` | LESSON | `lesson:LSN-0040` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a control that judges sealed history only runs once a successor anchors it |
| `LESSON-REQ-0040` | LESSON | `lesson:LSN-0041` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify an editing path that consumes a backslash escape leaves a control character, and the control it belonged to silently matches nothing |
| `LESSON-REQ-0041` | LESSON | `lesson:LSN-0042` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a naming convention rewrites a CHECK constraint's name and leaves a UNIQUE constraint's alone |
| `LESSON-REQ-0042` | LESSON | `lesson:LSN-0043` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a log line is not evidence that another process is ready |
| `LESSON-REQ-0043` | LESSON | `lesson:LSN-0044` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a boundary scan must read the code rather than the prose, and must be shown to fire on a mutated module |
| `LESSON-REQ-0044` | LESSON | `lesson:LSN-0045` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a counted test suite must declare its cases statically, because the denominator is read from the source |
| `LESSON-REQ-0045` | LESSON | `lesson:LSN-0046` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a timeout that cancels the task it runs in leaves nothing able to record what happened |
| `LESSON-REQ-0046` | LESSON | `lesson:LSN-0047` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a refusal that misnames the defect spends the only repair on the wrong correction |
| `LESSON-REQ-0047` | LESSON | `lesson:LSN-0048` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a state and the event that explains it, written in two commits, are written event first |
| `LESSON-REQ-0048` | LESSON | `lesson:LSN-0049` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a metric read the instant after the call that moved it is read before the scrape that carries it |
| `LESSON-REQ-0049` | LESSON | `lesson:LSN-0050` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a checkpoint sealed without naming its own tag cannot be validated from that tag |
| `LESSON-REQ-0050` | LESSON | `lesson:LSN-0051` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a payload one service bounds for another must be bounded as the receiver measures it |
| `LESSON-REQ-0051` | LESSON | `lesson:LSN-0052` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify two processes that meet on a queue must name what crosses it once, and a real run must exercise both |
| `LESSON-REQ-0052` | LESSON | `lesson:LSN-0053` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a process sweep that reads what a forking process holds waits on the processes it has to kill |
| `LESSON-REQ-0053` | LESSON | `lesson:LSN-0054` | no | `NOT_STARTED` | `NOT_STARTED` | Verify a pre-push check narrower than the change's reach lets a red gate reach the public remote |

## Evidence

### REQ-0001 - canonical:GATE-3#1.1

- Source reference: docs/GATE-3-CHECKLIST.md row 1.1
- Description: A canonical, machine-readable requirement specification exists for this Gate and the registry mirrors it row for row.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0002 - canonical:GATE-3#1.2

- Source reference: docs/GATE-3-CHECKLIST.md row 1.2
- Description: The closed mandatory gate registry carries the executable gate this Gate introduces, and that gate builds what it measures before measuring it.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0003 - canonical:GATE-3#1.3

- Source reference: docs/GATE-3-CHECKLIST.md row 1.3
- Description: The test suite this Gate introduces is declared canonically, is counted by the count derivation and is resolvable as evidence.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0004 - canonical:GATE-3#1.4

- Source reference: docs/GATE-3-CHECKLIST.md row 1.4
- Description: The internal Red Team battery of this Gate is executable, scoped to the sandbox, runs its attacks against the real container engine and records a null-mutation control.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0005 - canonical:GATE-3#1.5

- Source reference: docs/GATE-3-CHECKLIST.md row 1.5
- Description: The reservation of the sandbox directory is consumed by the Gate that owns it, and every reservation of a later Gate is still enforced.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0006 - canonical:GATE-3#1.6

- Source reference: docs/GATE-3-CHECKLIST.md row 1.6
- Description: One documented command verifies this Gate, adds the stages it introduces and keeps a targeted mode that does not restart the stack.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0007 - canonical:GATE-3#2.1

- Source reference: docs/GATE-3-CHECKLIST.md row 2.1
- Description: The repository publishes to exactly one authorised remote, and a remote pointing anywhere else is refused rather than used.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0008 - canonical:GATE-3#2.2

- Source reference: docs/GATE-3-CHECKLIST.md row 2.2
- Description: The whole history was scanned for credentials before its first publication, and a finding names the commit, the file, the line and the kind but never the value.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0009 - canonical:GATE-3#2.3

- Source reference: docs/GATE-3-CHECKLIST.md row 2.3
- Description: The published history carries no credential, and the check is repeatable against the history as it now stands.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0010 - canonical:GATE-3#2.4

- Source reference: docs/GATE-3-CHECKLIST.md row 2.4
- Description: Every push is preceded by a scan of exactly the staged content, and an allowance matches a value's digest rather than a path.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0011 - canonical:GATE-3#2.5

- Source reference: docs/GATE-3-CHECKLIST.md row 2.5
- Description: Whether the branch and the checkpoint tag are on the remote is asked of the remote, an unpushed commit or a missing tag fails, and an unreachable remote is never a pass.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0012 - canonical:GATE-3#2.6

- Source reference: docs/GATE-3-CHECKLIST.md row 2.6
- Description: The commit, push, tag and correction rules are stated in the development contract and recorded as a decision: atomic commits, green commits only, no rewriting of published history, no moving of a published tag, and no credential in a URL, a configuration or a versioned file.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0013 - canonical:GATE-3#2.7

- Source reference: docs/GATE-3-CHECKLIST.md row 2.7
- Description: The history of this Gate's development is preserved as observable data — requirement, commits, tests, fixes, checkpoint — and nothing in it is marked as training-eligible.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0014 - canonical:GATE-3#3.1

- Source reference: docs/GATE-3-CHECKLIST.md row 3.1
- Description: A command the ledger could not replay is refused before it executes, the refusal is itself recorded, and the recorder and the validator apply one shared replayability rule.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0015 - canonical:GATE-3#3.2

- Source reference: docs/GATE-3-CHECKLIST.md row 3.2
- Description: A guardrail entry that names a file or a path where a test is required is refused, and lesson validation and guardrail effectiveness resolve an entry through one function.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0016 - canonical:GATE-3#3.3

- Source reference: docs/GATE-3-CHECKLIST.md row 3.3
- Description: The committed lesson index is the render of the memory, and a memory changed without re-rendering it, or an index edited by hand, is refused under the memory policy that introduced the rule.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0017 - canonical:GATE-3#3.4

- Source reference: docs/GATE-3-CHECKLIST.md row 3.4
- Description: The event stream of a run that is already terminal delivers every event after the cursor, however many pages that takes, before it closes.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0018 - canonical:GATE-3#3.5

- Source reference: docs/GATE-3-CHECKLIST.md row 3.5
- Description: A canonical ADR index exists, lists every record with its title and status, resolves every link, and its test asserts rather than skips.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0019 - canonical:GATE-3#4.1

- Source reference: docs/GATE-3-CHECKLIST.md row 4.1
- Description: The sandbox is its own service in the directory the scope registry reserved for it, with its own contracts, and the decision is recorded.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0020 - canonical:GATE-3#4.2

- Source reference: docs/GATE-3-CHECKLIST.md row 4.2
- Description: No sandbox logic lives in the API routes, the Agent Runtime or the Model Gateway: none of them imports the sandbox package or a container client.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0021 - canonical:GATE-3#4.3

- Source reference: docs/GATE-3-CHECKLIST.md row 4.3
- Description: The Agent Runtime and the workflow that drives it still execute nothing themselves; a tool reaches the sandbox only as an activity on the sandbox's own task queue.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0022 - canonical:GATE-3#4.4

- Source reference: docs/GATE-3-CHECKLIST.md row 4.4
- Description: Inside the sandbox service only the engine backend and the in-container helper start a process, and the controller never uses a shell.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0023 - canonical:GATE-3#4.5

- Source reference: docs/GATE-3-CHECKLIST.md row 4.5
- Description: The controller starts only the container client, with an argument vector, and never a command a request supplied.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0024 - canonical:GATE-3#4.6

- Source reference: docs/GATE-3-CHECKLIST.md row 4.6
- Description: The controller is the only service given the container engine, and it holds no capability, cannot gain one, and publishes no port.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0025 - canonical:GATE-3#5.1

- Source reference: docs/GATE-3-CHECKLIST.md row 5.1
- Description: Versioned contracts exist for the sandbox session, the policy, the workspace, the execution request, the execution result, the command execution, the file operation, the Git operation and the artifact reference.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0026 - canonical:GATE-3#5.2

- Source reference: docs/GATE-3-CHECKLIST.md row 5.2
- Description: A contract of another version is refused rather than interpreted, and a request carrying a field the contract does not declare or missing one it requires is refused.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0027 - canonical:GATE-3#5.3

- Source reference: docs/GATE-3-CHECKLIST.md row 5.3
- Description: A command result carries the exit code, standard output, standard error, duration, whether it timed out, whether it was truncated and its artifact references, and no exit code is invented for a command that never started.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0028 - canonical:GATE-3#5.4

- Source reference: docs/GATE-3-CHECKLIST.md row 5.4
- Description: The execution status, session state, workspace and operation vocabularies are closed, and the database accepts exactly the declared ones.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0029 - canonical:GATE-3#5.5

- Source reference: docs/GATE-3-CHECKLIST.md row 5.5
- Description: The result an agent receives cannot present a cancellation, a denial or a timeout as a success.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0030 - canonical:GATE-3#6.1

- Source reference: docs/GATE-3-CHECKLIST.md row 6.1
- Description: An explicit registry names every executable tool — list, read, write, patch and search of files, shell execution, and the local Git status, diff, log, show, add and commit — and only a registered name can execute.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0031 - canonical:GATE-3#6.2

- Source reference: docs/GATE-3-CHECKLIST.md row 6.2
- Description: An unknown tool name is refused, and no name is ever mapped to a shell.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0032 - canonical:GATE-3#6.3

- Source reference: docs/GATE-3-CHECKLIST.md row 6.3
- Description: A canonical sandbox tool policy defines, per policy, the allowed tools, the resource profile, the network profile, the workspace permissions, the command timeout and the output limits.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0033 - canonical:GATE-3#6.4

- Source reference: docs/GATE-3-CHECKLIST.md row 6.4
- Description: A tool the run's policy does not allow is refused, a policy naming an unregistered tool is refused, and an unknown policy is refused.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0034 - canonical:GATE-3#6.5

- Source reference: docs/GATE-3-CHECKLIST.md row 6.5
- Description: Tool arguments are structured and typed: an undeclared argument is refused, and a wrong type, an absent value and a wrong value each carry their own reason.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0035 - canonical:GATE-3#6.6

- Source reference: docs/GATE-3-CHECKLIST.md row 6.6
- Description: No request can change its policy, its limits, its network or its mounts; a request that tries is denied, and a request may lower a timeout but never raise it.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0036 - canonical:GATE-3#6.7

- Source reference: docs/GATE-3-CHECKLIST.md row 6.7
- Description: The limits a tool runs under come from the policy, and every limit a policy applies is inside its declared bound.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0037 - canonical:GATE-3#6.8

- Source reference: docs/GATE-3-CHECKLIST.md row 6.8
- Description: A policy document with an unknown key, or a read-only policy that allows a writing tool, is refused when it is loaded.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0038 - canonical:GATE-3#6.9

- Source reference: docs/GATE-3-CHECKLIST.md row 6.9
- Description: Tools the policy allows execute automatically, inside the sandbox, without a confirmation per call; nothing is executed on the host under any policy.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0039 - canonical:GATE-3#7.1

- Source reference: docs/GATE-3-CHECKLIST.md row 7.1
- Description: Every run executes in its own disposable container with its own workspace; two runs never share either.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0040 - canonical:GATE-3#7.2

- Source reference: docs/GATE-3-CHECKLIST.md row 7.2
- Description: The sandbox runs unprivileged, as a non-root user, with every capability dropped and no way to gain privileges.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0041 - canonical:GATE-3#7.3

- Source reference: docs/GATE-3-CHECKLIST.md row 7.3
- Description: The root filesystem is read-only, and the only writable places are the workspace and a temporary directory, both in-memory filesystems with a size limit.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0042 - canonical:GATE-3#7.4

- Source reference: docs/GATE-3-CHECKLIST.md row 7.4
- Description: The container engine's socket, and any other engine endpoint, is absent from a sandbox.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0043 - canonical:GATE-3#7.5

- Source reference: docs/GATE-3-CHECKLIST.md row 7.5
- Description: No host path is mounted into a sandbox — no drive, no root, no home, no profile, no SSH directory, no credential store, no secret environment file — and no argument of a request can add one.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0044 - canonical:GATE-3#7.6

- Source reference: docs/GATE-3-CHECKLIST.md row 7.6
- Description: Every sandbox container carries labels naming the service instance that owns it, the session, the run, the policy and its expiry, so ownership is read from the engine rather than from memory.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0045 - canonical:GATE-3#8.1

- Source reference: docs/GATE-3-CHECKLIST.md row 8.1
- Description: CPU, memory, process count, workspace size, execution timeout and output size are mandatory, configurable limits, and a zero, negative, absurd or missing value is refused.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0046 - canonical:GATE-3#8.2

- Source reference: docs/GATE-3-CHECKLIST.md row 8.2
- Description: The memory limit holds the in-memory filesystems, so a full workspace cannot starve the processes of the limit they were promised.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0047 - canonical:GATE-3#8.3

- Source reference: docs/GATE-3-CHECKLIST.md row 8.3
- Description: A process that multiplies without end is contained by the process limit, and the sandbox remains usable afterwards.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0048 - canonical:GATE-3#8.4

- Source reference: docs/GATE-3-CHECKLIST.md row 8.4
- Description: A process that exceeds the memory limit fails in a controlled way, and the host is unaffected.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0049 - canonical:GATE-3#8.5

- Source reference: docs/GATE-3-CHECKLIST.md row 8.5
- Description: The workspace cannot outgrow its limit.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0050 - canonical:GATE-3#8.6

- Source reference: docs/GATE-3-CHECKLIST.md row 8.6
- Description: A command that exceeds its timeout is ended together with every process it started, including a process that left its session, and nothing is left running.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0051 - canonical:GATE-3#8.7

- Source reference: docs/GATE-3-CHECKLIST.md row 8.7
- Description: Standard output and standard error are bounded while they are read; what exceeds the bound is truncated explicitly and stored whole as an artifact, and memory is never unbounded.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0052 - canonical:GATE-3#9.1

- Source reference: docs/GATE-3-CHECKLIST.md row 9.1
- Description: A sandbox has no network by default: only loopback exists, and every policy the Gate ships denies the network.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0053 - canonical:GATE-3#9.2

- Source reference: docs/GATE-3-CHECKLIST.md row 9.2
- Description: An attempt to reach an external address from a sandbox without network fails.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0054 - canonical:GATE-3#9.3

- Source reference: docs/GATE-3-CHECKLIST.md row 9.3
- Description: The one other network profile is local services only, on an internal network with no route outside, and it is chosen by the policy, never by a request.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0055 - canonical:GATE-3#9.4

- Source reference: docs/GATE-3-CHECKLIST.md row 9.4
- Description: No package installation from the internet is offered; the image carries the toolchain the Gate's tests need.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0056 - canonical:GATE-3#10.1

- Source reference: docs/GATE-3-CHECKLIST.md row 10.1
- Description: A sandbox receives only the variables its policy explicitly allows, and no variable of the controller — provider key, repository token, agent socket, cloud credential or engine address — reaches it.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0057 - canonical:GATE-3#10.2

- Source reference: docs/GATE-3-CHECKLIST.md row 10.2
- Description: A command's environment inside the sandbox is the allowlist and nothing else.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0058 - canonical:GATE-3#10.3

- Source reference: docs/GATE-3-CHECKLIST.md row 10.3
- Description: A policy cannot allow a credential-shaped variable into a command's environment.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0059 - canonical:GATE-3#10.4

- Source reference: docs/GATE-3-CHECKLIST.md row 10.4
- Description: No Git credential, credential helper, SSH key or agent socket exists in a sandbox.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0060 - canonical:GATE-3#11.1

- Source reference: docs/GATE-3-CHECKLIST.md row 11.1
- Description: A workspace has an identity and an explicit lifecycle, belongs to exactly one run, and a run holds at most one active session.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0061 - canonical:GATE-3#11.2

- Source reference: docs/GATE-3-CHECKLIST.md row 11.2
- Description: A workspace is provisioned only from an authorised snapshot, named by its artifact identifier and never by a path, and becomes a repository the tools can work on.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0062 - canonical:GATE-3#11.3

- Source reference: docs/GATE-3-CHECKLIST.md row 11.3
- Description: Anything but a workspace snapshot artifact is refused before the run exists, and a snapshot for a team that executes no tool is refused.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0063 - canonical:GATE-3#11.4

- Source reference: docs/GATE-3-CHECKLIST.md row 11.4
- Description: A snapshot whose digest differs from its record, or that carries a link or an escaping member, is refused, and no session survives the refusal.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0064 - canonical:GATE-3#11.5

- Source reference: docs/GATE-3-CHECKLIST.md row 11.5
- Description: One run cannot read or write another run's files, nor see its processes.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0065 - canonical:GATE-3#11.6

- Source reference: docs/GATE-3-CHECKLIST.md row 11.6
- Description: The development working tree of this repository is never an agent's workspace.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0066 - canonical:GATE-3#12.1

- Source reference: docs/GATE-3-CHECKLIST.md row 12.1
- Description: One canonical path resolver decides every path a tool touches; no other module re-implements path safety.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0067 - canonical:GATE-3#12.2

- Source reference: docs/GATE-3-CHECKLIST.md row 12.2
- Description: Traversal, absolute paths, drive letters, UNC paths, null bytes and normalisation tricks are refused, each with its own reason.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0068 - canonical:GATE-3#12.3

- Source reference: docs/GATE-3-CHECKLIST.md row 12.3
- Description: A link inside the workspace that points outside it cannot be read or written through, whether it names a file, a directory, the root or climbs out relatively; a link that stays inside is followed.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0069 - canonical:GATE-3#12.4

- Source reference: docs/GATE-3-CHECKLIST.md row 12.4
- Description: Listing, reading, writing, searching and patching work inside the workspace of a real sandbox.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0070 - canonical:GATE-3#12.5

- Source reference: docs/GATE-3-CHECKLIST.md row 12.5
- Description: A read and a write are bounded in size, an oversized one is refused, and binary content is refused as text rather than mangled.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0071 - canonical:GATE-3#12.6

- Source reference: docs/GATE-3-CHECKLIST.md row 12.6
- Description: A write validates its parent directory and replaces the file atomically.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0072 - canonical:GATE-3#12.7

- Source reference: docs/GATE-3-CHECKLIST.md row 12.7
- Description: A patch applies only inside the workspace; a patch whose context does not match, or that has one bad file, changes nothing.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0073 - canonical:GATE-3#12.8

- Source reference: docs/GATE-3-CHECKLIST.md row 12.8
- Description: A search is confined to the workspace and bounded in results, output and duration.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0074 - canonical:GATE-3#12.9

- Source reference: docs/GATE-3-CHECKLIST.md row 12.9
- Description: A path refused inside the sandbox reaches the agent as a denial, not as a failure of the sandbox.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0075 - canonical:GATE-3#13.1

- Source reference: docs/GATE-3-CHECKLIST.md row 13.1
- Description: Shell execution runs only inside the sandbox container, with the command, the working directory, the allowed environment and the timeout passed as structured arguments.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0076 - canonical:GATE-3#13.2

- Source reference: docs/GATE-3-CHECKLIST.md row 13.2
- Description: Standard output, standard error, a zero and a non-zero exit code, a missing executable and a child process are all reported faithfully.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0077 - canonical:GATE-3#13.3

- Source reference: docs/GATE-3-CHECKLIST.md row 13.3
- Description: The working directory resolves inside the workspace, and an escaping one is refused.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0078 - canonical:GATE-3#13.4

- Source reference: docs/GATE-3-CHECKLIST.md row 13.4
- Description: A payload that tries to reach a host command affects only the sandbox, inside its policy, and the host is unchanged.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0079 - canonical:GATE-3#13.5

- Source reference: docs/GATE-3-CHECKLIST.md row 13.5
- Description: A command still running when its run is cancelled is stopped, with every process it started.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0080 - canonical:GATE-3#14.1

- Source reference: docs/GATE-3-CHECKLIST.md row 14.1
- Description: Inside the workspace an agent can read the status, the working and the staged diff, the log and a commit, stage files and commit locally.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0081 - canonical:GATE-3#14.2

- Source reference: docs/GATE-3-CHECKLIST.md row 14.2
- Description: Every Git tool builds a fixed argument vector, a revision that looks like an option is refused, and a commit skips hooks and carries its message as one argument.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0082 - canonical:GATE-3#14.3

- Source reference: docs/GATE-3-CHECKLIST.md row 14.3
- Description: No remote Git operation is offered or possible — no push, fetch, clone or remote — and no destructive operation — hard reset, clean, rebase, history filtering, forced push — is offered by default.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0083 - canonical:GATE-3#14.4

- Source reference: docs/GATE-3-CHECKLIST.md row 14.4
- Description: An agent's commits carry an explicit sandbox identity that is not a person, separate from the owner's development identity, and the difference is documented.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0084 - canonical:GATE-3#14.5

- Source reference: docs/GATE-3-CHECKLIST.md row 14.5
- Description: Git output is bounded like any other output.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0085 - canonical:GATE-3#15.1

- Source reference: docs/GATE-3-CHECKLIST.md row 15.1
- Description: A session moves through explicit states, is created ready for its run and is removed with it.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0086 - canonical:GATE-3#15.2

- Source reference: docs/GATE-3-CHECKLIST.md row 15.2
- Description: A running tool holds its session in the running state, and inspecting a session reports the store and the engine side by side.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0087 - canonical:GATE-3#15.3

- Source reference: docs/GATE-3-CHECKLIST.md row 15.3
- Description: When a run ends or is cancelled its sandbox is removed, and no container or temporary volume is left behind.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0088 - canonical:GATE-3#15.4

- Source reference: docs/GATE-3-CHECKLIST.md row 15.4
- Description: A restarted service reconciles from the store and the engine rather than from memory: it keeps a live session, removes a container no session owns, and fails a session whose container vanished.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0089 - canonical:GATE-3#15.5

- Source reference: docs/GATE-3-CHECKLIST.md row 15.5
- Description: Reconciliation touches only containers this service instance owns, so another stack or a test on the same engine is never cleaned up by it.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0090 - canonical:GATE-3#15.6

- Source reference: docs/GATE-3-CHECKLIST.md row 15.6
- Description: An orphan sweeper expires only sessions that have expired and are not running, in bounded, deterministic batches, and never removes an active workspace.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0091 - canonical:GATE-3#16.1

- Source reference: docs/GATE-3-CHECKLIST.md row 16.1
- Description: This Gate adds its schema through a new migration and edits no migration that has already been applied.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0092 - canonical:GATE-3#16.2

- Source reference: docs/GATE-3-CHECKLIST.md row 16.2
- Description: The existing tool call, artifact and run entities are evolved rather than duplicated, and the one new table holds only what nothing else could: the sandbox session.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0093 - canonical:GATE-3#16.3

- Source reference: docs/GATE-3-CHECKLIST.md row 16.3
- Description: A database created from nothing reaches the head revision, and a database at the previous Gate's head upgrades without losing a row.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0094 - canonical:GATE-3#16.4

- Source reference: docs/GATE-3-CHECKLIST.md row 16.4
- Description: Every execution is traceable from the task through the run, the agent run, the tool request, the sandbox session and the execution to the result, and none of it holds private reasoning.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0095 - canonical:GATE-3#16.5

- Source reference: docs/GATE-3-CHECKLIST.md row 16.5
- Description: A retried request never executes twice: the execution is keyed by the tool request it answers.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0096 - canonical:GATE-3#16.6

- Source reference: docs/GATE-3-CHECKLIST.md row 16.6
- Description: The store the service runs against in the stack records sessions and executions in the real database with the same behaviour the suite asserts in memory.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0097 - canonical:GATE-3#16.7

- Source reference: docs/GATE-3-CHECKLIST.md row 16.7
- Description: Nothing this Gate persists is training-eligible, and no table stores a credential.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0098 - canonical:GATE-3#17.1

- Source reference: docs/GATE-3-CHECKLIST.md row 17.1
- Description: A pending tool request of a stage with a sandbox policy is checked against the policy, executed in the run's sandbox, its result persisted, and the workflow resumes.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0099 - canonical:GATE-3#17.2

- Source reference: docs/GATE-3-CHECKLIST.md row 17.2
- Description: A stage without a sandbox policy keeps the previous Gate's behaviour: the request waits for a result delivered through the API.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0100 - canonical:GATE-3#17.3

- Source reference: docs/GATE-3-CHECKLIST.md row 17.3
- Description: The run plan names the sandbox policy of each stage and the workspace source, frozen when the run is created.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0101 - canonical:GATE-3#17.4

- Source reference: docs/GATE-3-CHECKLIST.md row 17.4
- Description: A tool result returns to the agent as labelled data in its own channel and never as an instruction.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0102 - canonical:GATE-3#17.5

- Source reference: docs/GATE-3-CHECKLIST.md row 17.5
- Description: A large result reaches the model truncated inline with an artifact reference, within the size the runtime accepts for a tool result.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0103 - canonical:GATE-3#17.6

- Source reference: docs/GATE-3-CHECKLIST.md row 17.6
- Description: A tool that times out returns a normalised error result the agent receives, and the run never stays waiting for a tool for ever.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0104 - canonical:GATE-3#17.7

- Source reference: docs/GATE-3-CHECKLIST.md row 17.7
- Description: Cancelling a run during a long command stops the command, records the cancellation, ends the run cancelled and leaves no process behind.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0105 - canonical:GATE-3#17.8

- Source reference: docs/GATE-3-CHECKLIST.md row 17.8
- Description: A sandbox service restart while a run executes does not lose the run: the session is reconciled and the run completes.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0106 - canonical:GATE-3#18.1

- Source reference: docs/GATE-3-CHECKLIST.md row 18.1
- Description: A profile that may request tools names the sandbox policy that governs them, and a profile with tools and no policy is refused.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0107 - canonical:GATE-3#18.2

- Source reference: docs/GATE-3-CHECKLIST.md row 18.2
- Description: No agent is given every tool: each profile's permitted actions are within its policy's tools.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0108 - canonical:GATE-3#18.3

- Source reference: docs/GATE-3-CHECKLIST.md row 18.3
- Description: A developer profile may read, search, write, patch, run tests and use the local Git tools its policy allows.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0109 - canonical:GATE-3#18.4

- Source reference: docs/GATE-3-CHECKLIST.md row 18.4
- Description: The reviewer is read-only: read, search, diff and test results, and no writing tool.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0110 - canonical:GATE-3#18.5

- Source reference: docs/GATE-3-CHECKLIST.md row 18.5
- Description: The planner has no writing tool and works from context alone.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0111 - canonical:GATE-3#18.6

- Source reference: docs/GATE-3-CHECKLIST.md row 18.6
- Description: A minimal coding team — planner, developer, reviewer — proves the flow, and no larger team is built.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0112 - canonical:GATE-3#19.1

- Source reference: docs/GATE-3-CHECKLIST.md row 19.1
- Description: Full output, large diffs and workspace snapshots are stored in the existing artifact infrastructure, recorded as artifacts, and no second store is created.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0113 - canonical:GATE-3#19.2

- Source reference: docs/GATE-3-CHECKLIST.md row 19.2
- Description: A workspace snapshot is created from an explicit source directory by a documented command, and never from the development working tree implicitly.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0114 - canonical:GATE-3#20.1

- Source reference: docs/GATE-3-CHECKLIST.md row 20.1
- Description: A registry of sandbox image profiles exists, the architecture accepts new profiles, and one functional profile for this project carries Git and Python.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0115 - canonical:GATE-3#20.2

- Source reference: docs/GATE-3-CHECKLIST.md row 20.2
- Description: The image is built as part of the Gate from a base pinned by digest and packages pinned by version, and never from a moving tag.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0116 - canonical:GATE-3#20.3

- Source reference: docs/GATE-3-CHECKLIST.md row 20.3
- Description: The image is addressed by a fingerprint of its inputs, and a missing or stale image is refused rather than substituted.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0117 - canonical:GATE-3#20.4

- Source reference: docs/GATE-3-CHECKLIST.md row 20.4
- Description: The sandbox gate builds the service image and the sandbox image before it measures anything.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0118 - canonical:GATE-3#20.5

- Source reference: docs/GATE-3-CHECKLIST.md row 20.5
- Description: The sandbox service installs the one dependency lock the dependency scan reads, so its Python dependencies are scanned with the rest; the sandbox image's system packages are pinned by version, and what the scan does not cover is documented rather than implied.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0119 - canonical:GATE-3#21.1

- Source reference: docs/GATE-3-CHECKLIST.md row 21.1
- Description: An internal service contract creates a session, executes a tool, inspects a session and terminates it, and it is reached only as activities on the sandbox's task queue.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0120 - canonical:GATE-3#21.2

- Source reference: docs/GATE-3-CHECKLIST.md row 21.2
- Description: A refusal is recorded as an execution with its reason, so a denied request is as traceable as an executed one.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0121 - canonical:GATE-3#21.3

- Source reference: docs/GATE-3-CHECKLIST.md row 21.3
- Description: The service's health is a poller on its queue and an engine that answers, not a process that exists.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0122 - canonical:GATE-3#22.1

- Source reference: docs/GATE-3-CHECKLIST.md row 22.1
- Description: The service publishes instruments for sessions created and active, tool executions, their duration, failures, timeouts and policy refusals.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0123 - canonical:GATE-3#22.2

- Source reference: docs/GATE-3-CHECKLIST.md row 22.2
- Description: Every metric label is low cardinality, a command never becomes a label, and a refusal is counted by its reason.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0124 - canonical:GATE-3#22.3

- Source reference: docs/GATE-3-CHECKLIST.md row 22.3
- Description: Logs carry the run, the agent, the sandbox, the tool, the status and the duration, and never a whole result, a secret or the host environment.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0125 - canonical:GATE-3#22.4

- Source reference: docs/GATE-3-CHECKLIST.md row 22.4
- Description: The observability stack scrapes the sandbox service.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0126 - canonical:GATE-3#23.1

- Source reference: docs/GATE-3-CHECKLIST.md row 23.1
- Description: The run page shows each tool the sandbox executed: the tool, its status, its duration, the abbreviated sandbox identifier and a summary.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0127 - canonical:GATE-3#23.2

- Source reference: docs/GATE-3-CHECKLIST.md row 23.2
- Description: The page never receives a tool's output and offers no interactive shell.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0128 - canonical:GATE-3#23.3

- Source reference: docs/GATE-3-CHECKLIST.md row 23.3
- Description: The command line interface stays reserved for the Gate that owns it.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0129 - canonical:GATE-3#24.1

- Source reference: docs/GATE-3-CHECKLIST.md row 24.1
- Description: A synthetic repository with a defective function and a failing test is provisioned as a snapshot, and a coding run over it reads the code, runs the failing test, patches the code, runs the passing test, reads the diff, commits locally, is reviewed and finishes.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0130 - canonical:GATE-3#24.2

- Source reference: docs/GATE-3-CHECKLIST.md row 24.2
- Description: The scenario drives the real workflow, the real activities, the real sandbox service and the real container engine, with only the model replaced by a deterministic script.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0131 - canonical:GATE-3#24.3

- Source reference: docs/GATE-3-CHECKLIST.md row 24.3
- Description: An automatic proof shows a shell request did not execute on the host: a sentinel outside the sandbox is neither created nor modified.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0132 - canonical:GATE-3#24.4

- Source reference: docs/GATE-3-CHECKLIST.md row 24.4
- Description: The scenario asserts what the run recorded — its terminal state, its tool executions and the test that passed — rather than what the harness sent.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0133 - canonical:GATE-3#25.1

- Source reference: docs/GATE-3-CHECKLIST.md row 25.1
- Description: The repository's one verification command covers this Gate, in its targeted and its full mode.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0134 - canonical:GATE-3#25.2

- Source reference: docs/GATE-3-CHECKLIST.md row 25.2
- Description: A runbook documents the lifecycle, the tool policy, the filesystem, the shell, Git, the network, resources, artifacts, cleanup, debugging and the security boundary.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0135 - canonical:GATE-3#25.3

- Source reference: docs/GATE-3-CHECKLIST.md row 25.3
- Description: The architecture, development, version and entry documents describe what this Gate delivered rather than what was planned.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0136 - canonical:GATE-3#25.4

- Source reference: docs/GATE-3-CHECKLIST.md row 25.4
- Description: The structural decisions of this Gate are recorded as ADRs and listed in the index.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0137 - canonical:GATE-3#25.5

- Source reference: docs/GATE-3-CHECKLIST.md row 25.5
- Description: The Gate produces its retrospective from the canonical template, and its reusable lessons are recorded with the guardrail that protects the property rather than one file.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0138 - canonical:GATE-3#25.6

- Source reference: docs/GATE-3-CHECKLIST.md row 25.6
- Description: Every commit of the Gate and its checkpoint tag are on the authorised remote when the Gate closes.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0139 - canonical:GATE-3#25.7

- Source reference: docs/GATE-3-CHECKLIST.md row 25.7
- Description: The Gate closes at the project's own internal verdict, leaves the milestone verdict to a fresh-session audit, and starts no part of the Gate that follows it.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0140 - finding:M1-F-003

- Source reference: M1-CP-0002 docs/checkpoints/GATE-3-CP-0002/REVIEW-REPORT.md M1-F-003
- Description: The published history cannot validate GATE-1-CP-0001, so every clean clone of the remote fails the mandatory tests gate
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0141 - finding:M1-F-001

- Source reference: M1-CP-0002 docs/checkpoints/GATE-3-CP-0002/REVIEW-REPORT.md M1-F-001
- Description: A model is never shown the shape of a tool request, and the configured live model cannot make one
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0142 - finding:M1-F-002

- Source reference: M1-CP-0002 docs/checkpoints/GATE-3-CP-0002/REVIEW-REPORT.md M1-F-002
- Description: The API accepts a tool result for a request the sandbox is executing, and the agent receives it instead of the sandbox's
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0001 - lesson:LSN-0001

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0001
- Description: Verify checkpoint validation must succeed from a detached checkout of the checkpoint tag
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0002 - lesson:LSN-0002

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0002
- Description: Verify a file inventory must be recomputed from the repository, never trusted as an assertion
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0003 - lesson:LSN-0003

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0003
- Description: Verify every operation attempt must be auditable, including a refusal decided before execution
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0004 - lesson:LSN-0004

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0004
- Description: Verify a checkpoint may never claim readiness while it also claims to be blocked
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0005 - lesson:LSN-0005

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0005
- Description: Verify a PASS requires evidence that can be executed or resolved, not a statement
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0006 - lesson:LSN-0006

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0006
- Description: Verify the repository must be self-contained; a specification may not live outside it
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0007 - lesson:LSN-0007

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0007
- Description: Verify independent validation cannot be declared by the run that did the work
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0008 - lesson:LSN-0008

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0008
- Description: Verify requirement completeness must be total and evidence-backed before handoff
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0009 - lesson:LSN-0009

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0009
- Description: Verify a red gate requires rework, never a waiver, and never a weakened check
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0010 - lesson:LSN-0010

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0010
- Description: Verify a recorded command must carry runtime, working directory, commit and purpose to be replayable
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0011 - lesson:LSN-0011

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0011
- Description: Verify a control over a checkpoint's own evidence must be scoped to the moment it matters
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0012 - lesson:LSN-0012

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0012
- Description: Verify sealed checkpoints and their tags are immutable, and tooling must keep validating them
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0013 - lesson:LSN-0013

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0013
- Description: Verify an installed capability must be detected by resolved path, not by a bare command lookup
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0014 - lesson:LSN-0014

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0014
- Description: Verify evidence must be recorded as it happens, not reconstructed at the end of a run
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0015 - lesson:LSN-0015

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0015
- Description: Verify every positive terminal status needs one shared promotion invariant
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0016 - lesson:LSN-0016

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0016
- Description: Verify a mandatory set must be closed by policy, never chosen by the caller
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0017 - lesson:LSN-0017

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0017
- Description: Verify a completeness denominator must come from a source the delivery does not own
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0018 - lesson:LSN-0018

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0018
- Description: Verify a structured reference must be resolved, not merely well typed
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0019 - lesson:LSN-0019

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0019
- Description: Verify a derived artifact must carry a fingerprint of the inputs that produced it
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0020 - lesson:LSN-0020

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0020
- Description: Verify evidence produced from a dirty tree needs immutable input identity
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0021 - lesson:LSN-0021

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0021
- Description: Verify sealed history needs an anchor outside the content it describes
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0022 - lesson:LSN-0022

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0022
- Description: Verify an authoritative count must be derived once, never maintained by hand twice
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0023 - lesson:LSN-0023

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0023
- Description: Verify a lesson must cite a source that actually records the finding it claims
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0024 - lesson:LSN-0024

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0024
- Description: Verify a control is finished only when its positive path has been executed, not only its refusals
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0025 - lesson:LSN-0025

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0025
- Description: Verify a generic guardrail derives repository state instead of naming today's checkpoint
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0026 - lesson:LSN-0026

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0026
- Description: Verify an adversarial battery without a null-mutation control proves nothing
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0027 - lesson:LSN-0027

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0027
- Description: Verify a lesson's prose may record a residual limit but may never contradict its status
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0028 - lesson:LSN-0028

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0028
- Description: Verify a configuration key that no code reads is a defect, not documentation
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0029 - lesson:LSN-0029

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0029
- Description: Verify a required protocol transition must never turn a mandatory gate red
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0030 - lesson:LSN-0031

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0030
- Description: Verify an empty applicable set is not a missing required set, and a control must tell them apart
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0031 - lesson:LSN-0032

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0031
- Description: Verify a control written while one Gate was the only Gate stops being a control when the next one starts
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0032 - lesson:LSN-0033

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0032
- Description: Verify a value bound in middleware is absent in the handlers that run outside it
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0033 - lesson:LSN-0034

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0033
- Description: Verify re-deriving what the framework already computed diverges from the framework
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0034 - lesson:LSN-0035

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0034
- Description: Verify captured subprocess output decoded or re-emitted with the platform codepage crashes the tool, not the work
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0035 - lesson:LSN-0036

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0035
- Description: Verify a gate that runs inside an image measures the image, not the source
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0036 - lesson:LSN-0037

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0036
- Description: Verify a shared control that names an identifier the repository derives stops being a control when that identifier moves
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0037 - lesson:LSN-0038

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0037
- Description: Verify two representations of one concept in one module disagree, and the safer one loses
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0038 - lesson:LSN-0039

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0038
- Description: Verify a test that writes to the operational database leaves production data behind
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0039 - lesson:LSN-0040

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0039
- Description: Verify a control that judges sealed history only runs once a successor anchors it
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0040 - lesson:LSN-0041

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0040
- Description: Verify an editing path that consumes a backslash escape leaves a control character, and the control it belonged to silently matches nothing
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0041 - lesson:LSN-0042

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0041
- Description: Verify a naming convention rewrites a CHECK constraint's name and leaves a UNIQUE constraint's alone
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0042 - lesson:LSN-0043

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0042
- Description: Verify a log line is not evidence that another process is ready
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0043 - lesson:LSN-0044

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0043
- Description: Verify a boundary scan must read the code rather than the prose, and must be shown to fire on a mutated module
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0044 - lesson:LSN-0045

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0044
- Description: Verify a counted test suite must declare its cases statically, because the denominator is read from the source
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0045 - lesson:LSN-0046

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0045
- Description: Verify a timeout that cancels the task it runs in leaves nothing able to record what happened
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0046 - lesson:LSN-0047

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0046
- Description: Verify a refusal that misnames the defect spends the only repair on the wrong correction
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0047 - lesson:LSN-0048

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0047
- Description: Verify a state and the event that explains it, written in two commits, are written event first
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0048 - lesson:LSN-0049

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0048
- Description: Verify a metric read the instant after the call that moved it is read before the scrape that carries it
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0049 - lesson:LSN-0050

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0049
- Description: Verify a checkpoint sealed without naming its own tag cannot be validated from that tag
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0050 - lesson:LSN-0051

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0050
- Description: Verify a payload one service bounds for another must be bounded as the receiver measures it
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0051 - lesson:LSN-0052

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0051
- Description: Verify two processes that meet on a queue must name what crosses it once, and a real run must exercise both
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0052 - lesson:LSN-0053

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0052
- Description: Verify a process sweep that reads what a forking process holds waits on the processes it has to kill
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0053 - lesson:LSN-0054

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0053
- Description: Verify a pre-push check narrower than the change's reach lets a red gate reach the public remote
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_
