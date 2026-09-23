# Closure Requirements - GATE-3-CP-0001

Derived from the canonical sources listed below, before implementation. The expected set
is recomputed by `policies.expected_requirement_refs` and compared exactly with the
declared set, so a requirement cannot be dropped and the denominator cannot be reduced.

## Sources

- SOURCE A: docs/GATE-3-CHECKLIST.md, the canonical GATE-3 specification
- SOURCE B: docs/MILESTONE-VALIDATION.md, the milestone requirements of the audit
- SOURCE C: LESSON-PREFLIGHT.json, the lessons the engineering memory imposes

## Requirements

| ID | Source | Anchor | Mandatory | Implementation | Final | Description |
|---|---|---|---|---|---|---|
| `REQ-0001` | GATE_SPECIFICATION | `canonical:GATE-3#1.1` | yes | `COMPLETE` | `COMPLETE` | A canonical, machine-readable requirement specification exists for this Gate and the registry mirrors it row for row. |
| `REQ-0002` | GATE_SPECIFICATION | `canonical:GATE-3#1.2` | yes | `COMPLETE` | `COMPLETE` | The closed mandatory gate registry carries the executable gate this Gate introduces, and that gate builds what it measures before measuring it. |
| `REQ-0003` | GATE_SPECIFICATION | `canonical:GATE-3#1.3` | yes | `COMPLETE` | `COMPLETE` | The test suite this Gate introduces is declared canonically, is counted by the count derivation and is resolvable as evidence. |
| `REQ-0004` | GATE_SPECIFICATION | `canonical:GATE-3#1.4` | yes | `COMPLETE` | `COMPLETE` | The internal Red Team battery of this Gate is executable, scoped to the sandbox, runs its attacks against the real container engine and records a null-mutation control. |
| `REQ-0005` | GATE_SPECIFICATION | `canonical:GATE-3#1.5` | yes | `COMPLETE` | `COMPLETE` | The reservation of the sandbox directory is consumed by the Gate that owns it, and every reservation of a later Gate is still enforced. |
| `REQ-0006` | GATE_SPECIFICATION | `canonical:GATE-3#1.6` | yes | `COMPLETE` | `COMPLETE` | One documented command verifies this Gate, adds the stages it introduces and keeps a targeted mode that does not restart the stack. |
| `REQ-0007` | GATE_SPECIFICATION | `canonical:GATE-3#2.1` | yes | `COMPLETE` | `COMPLETE` | The repository publishes to exactly one authorised remote, and a remote pointing anywhere else is refused rather than used. |
| `REQ-0008` | GATE_SPECIFICATION | `canonical:GATE-3#2.2` | yes | `COMPLETE` | `COMPLETE` | The whole history was scanned for credentials before its first publication, and a finding names the commit, the file, the line and the kind but never the value. |
| `REQ-0009` | GATE_SPECIFICATION | `canonical:GATE-3#2.3` | yes | `COMPLETE` | `COMPLETE` | The published history carries no credential, and the check is repeatable against the history as it now stands. |
| `REQ-0010` | GATE_SPECIFICATION | `canonical:GATE-3#2.4` | yes | `COMPLETE` | `COMPLETE` | Every push is preceded by a scan of exactly the staged content, and an allowance matches a value's digest rather than a path. |
| `REQ-0011` | GATE_SPECIFICATION | `canonical:GATE-3#2.5` | yes | `COMPLETE` | `COMPLETE` | Whether the branch and the checkpoint tag are on the remote is asked of the remote, an unpushed commit or a missing tag fails, and an unreachable remote is never a pass. |
| `REQ-0012` | GATE_SPECIFICATION | `canonical:GATE-3#2.6` | yes | `COMPLETE` | `COMPLETE` | The commit, push, tag and correction rules are stated in the development contract and recorded as a decision: atomic commits, green commits only, no rewriting of published history, no moving of a published tag, and no credential in a URL, a configuration or a versioned file. |
| `REQ-0013` | GATE_SPECIFICATION | `canonical:GATE-3#2.7` | yes | `COMPLETE` | `COMPLETE` | The history of this Gate's development is preserved as observable data — requirement, commits, tests, fixes, checkpoint — and nothing in it is marked as training-eligible. |
| `REQ-0014` | GATE_SPECIFICATION | `canonical:GATE-3#3.1` | yes | `COMPLETE` | `COMPLETE` | A command the ledger could not replay is refused before it executes, the refusal is itself recorded, and the recorder and the validator apply one shared replayability rule. |
| `REQ-0015` | GATE_SPECIFICATION | `canonical:GATE-3#3.2` | yes | `COMPLETE` | `COMPLETE` | A guardrail entry that names a file or a path where a test is required is refused, and lesson validation and guardrail effectiveness resolve an entry through one function. |
| `REQ-0016` | GATE_SPECIFICATION | `canonical:GATE-3#3.3` | yes | `COMPLETE` | `COMPLETE` | The committed lesson index is the render of the memory, and a memory changed without re-rendering it, or an index edited by hand, is refused under the memory policy that introduced the rule. |
| `REQ-0017` | GATE_SPECIFICATION | `canonical:GATE-3#3.4` | yes | `COMPLETE` | `COMPLETE` | The event stream of a run that is already terminal delivers every event after the cursor, however many pages that takes, before it closes. |
| `REQ-0018` | GATE_SPECIFICATION | `canonical:GATE-3#3.5` | yes | `COMPLETE` | `COMPLETE` | A canonical ADR index exists, lists every record with its title and status, resolves every link, and its test asserts rather than skips. |
| `REQ-0019` | GATE_SPECIFICATION | `canonical:GATE-3#4.1` | yes | `COMPLETE` | `COMPLETE` | The sandbox is its own service in the directory the scope registry reserved for it, with its own contracts, and the decision is recorded. |
| `REQ-0020` | GATE_SPECIFICATION | `canonical:GATE-3#4.2` | yes | `COMPLETE` | `COMPLETE` | No sandbox logic lives in the API routes, the Agent Runtime or the Model Gateway: none of them imports the sandbox package or a container client. |
| `REQ-0021` | GATE_SPECIFICATION | `canonical:GATE-3#4.3` | yes | `COMPLETE` | `COMPLETE` | The Agent Runtime and the workflow that drives it still execute nothing themselves; a tool reaches the sandbox only as an activity on the sandbox's own task queue. |
| `REQ-0022` | GATE_SPECIFICATION | `canonical:GATE-3#4.4` | yes | `COMPLETE` | `COMPLETE` | Inside the sandbox service only the engine backend and the in-container helper start a process, and the controller never uses a shell. |
| `REQ-0023` | GATE_SPECIFICATION | `canonical:GATE-3#4.5` | yes | `COMPLETE` | `COMPLETE` | The controller starts only the container client, with an argument vector, and never a command a request supplied. |
| `REQ-0024` | GATE_SPECIFICATION | `canonical:GATE-3#4.6` | yes | `COMPLETE` | `COMPLETE` | The controller is the only service given the container engine, and it holds no capability, cannot gain one, and publishes no port. |
| `REQ-0025` | GATE_SPECIFICATION | `canonical:GATE-3#5.1` | yes | `COMPLETE` | `COMPLETE` | Versioned contracts exist for the sandbox session, the policy, the workspace, the execution request, the execution result, the command execution, the file operation, the Git operation and the artifact reference. |
| `REQ-0026` | GATE_SPECIFICATION | `canonical:GATE-3#5.2` | yes | `COMPLETE` | `COMPLETE` | A contract of another version is refused rather than interpreted, and a request carrying a field the contract does not declare or missing one it requires is refused. |
| `REQ-0027` | GATE_SPECIFICATION | `canonical:GATE-3#5.3` | yes | `COMPLETE` | `COMPLETE` | A command result carries the exit code, standard output, standard error, duration, whether it timed out, whether it was truncated and its artifact references, and no exit code is invented for a command that never started. |
| `REQ-0028` | GATE_SPECIFICATION | `canonical:GATE-3#5.4` | yes | `COMPLETE` | `COMPLETE` | The execution status, session state, workspace and operation vocabularies are closed, and the database accepts exactly the declared ones. |
| `REQ-0029` | GATE_SPECIFICATION | `canonical:GATE-3#5.5` | yes | `COMPLETE` | `COMPLETE` | The result an agent receives cannot present a cancellation, a denial or a timeout as a success. |
| `REQ-0030` | GATE_SPECIFICATION | `canonical:GATE-3#6.1` | yes | `COMPLETE` | `COMPLETE` | An explicit registry names every executable tool — list, read, write, patch and search of files, shell execution, and the local Git status, diff, log, show, add and commit — and only a registered name can execute. |
| `REQ-0031` | GATE_SPECIFICATION | `canonical:GATE-3#6.2` | yes | `COMPLETE` | `COMPLETE` | An unknown tool name is refused, and no name is ever mapped to a shell. |
| `REQ-0032` | GATE_SPECIFICATION | `canonical:GATE-3#6.3` | yes | `COMPLETE` | `COMPLETE` | A canonical sandbox tool policy defines, per policy, the allowed tools, the resource profile, the network profile, the workspace permissions, the command timeout and the output limits. |
| `REQ-0033` | GATE_SPECIFICATION | `canonical:GATE-3#6.4` | yes | `COMPLETE` | `COMPLETE` | A tool the run's policy does not allow is refused, a policy naming an unregistered tool is refused, and an unknown policy is refused. |
| `REQ-0034` | GATE_SPECIFICATION | `canonical:GATE-3#6.5` | yes | `COMPLETE` | `COMPLETE` | Tool arguments are structured and typed: an undeclared argument is refused, and a wrong type, an absent value and a wrong value each carry their own reason. |
| `REQ-0035` | GATE_SPECIFICATION | `canonical:GATE-3#6.6` | yes | `COMPLETE` | `COMPLETE` | No request can change its policy, its limits, its network or its mounts; a request that tries is denied, and a request may lower a timeout but never raise it. |
| `REQ-0036` | GATE_SPECIFICATION | `canonical:GATE-3#6.7` | yes | `COMPLETE` | `COMPLETE` | The limits a tool runs under come from the policy, and every limit a policy applies is inside its declared bound. |
| `REQ-0037` | GATE_SPECIFICATION | `canonical:GATE-3#6.8` | yes | `COMPLETE` | `COMPLETE` | A policy document with an unknown key, or a read-only policy that allows a writing tool, is refused when it is loaded. |
| `REQ-0038` | GATE_SPECIFICATION | `canonical:GATE-3#6.9` | yes | `COMPLETE` | `COMPLETE` | Tools the policy allows execute automatically, inside the sandbox, without a confirmation per call; nothing is executed on the host under any policy. |
| `REQ-0039` | GATE_SPECIFICATION | `canonical:GATE-3#7.1` | yes | `COMPLETE` | `COMPLETE` | Every run executes in its own disposable container with its own workspace; two runs never share either. |
| `REQ-0040` | GATE_SPECIFICATION | `canonical:GATE-3#7.2` | yes | `COMPLETE` | `COMPLETE` | The sandbox runs unprivileged, as a non-root user, with every capability dropped and no way to gain privileges. |
| `REQ-0041` | GATE_SPECIFICATION | `canonical:GATE-3#7.3` | yes | `COMPLETE` | `COMPLETE` | The root filesystem is read-only, and the only writable places are the workspace and a temporary directory, both in-memory filesystems with a size limit. |
| `REQ-0042` | GATE_SPECIFICATION | `canonical:GATE-3#7.4` | yes | `COMPLETE` | `COMPLETE` | The container engine's socket, and any other engine endpoint, is absent from a sandbox. |
| `REQ-0043` | GATE_SPECIFICATION | `canonical:GATE-3#7.5` | yes | `COMPLETE` | `COMPLETE` | No host path is mounted into a sandbox — no drive, no root, no home, no profile, no SSH directory, no credential store, no secret environment file — and no argument of a request can add one. |
| `REQ-0044` | GATE_SPECIFICATION | `canonical:GATE-3#7.6` | yes | `COMPLETE` | `COMPLETE` | Every sandbox container carries labels naming the service instance that owns it, the session, the run, the policy and its expiry, so ownership is read from the engine rather than from memory. |
| `REQ-0045` | GATE_SPECIFICATION | `canonical:GATE-3#8.1` | yes | `COMPLETE` | `COMPLETE` | CPU, memory, process count, workspace size, execution timeout and output size are mandatory, configurable limits, and a zero, negative, absurd or missing value is refused. |
| `REQ-0046` | GATE_SPECIFICATION | `canonical:GATE-3#8.2` | yes | `COMPLETE` | `COMPLETE` | The memory limit holds the in-memory filesystems, so a full workspace cannot starve the processes of the limit they were promised. |
| `REQ-0047` | GATE_SPECIFICATION | `canonical:GATE-3#8.3` | yes | `COMPLETE` | `COMPLETE` | A process that multiplies without end is contained by the process limit, and the sandbox remains usable afterwards. |
| `REQ-0048` | GATE_SPECIFICATION | `canonical:GATE-3#8.4` | yes | `COMPLETE` | `COMPLETE` | A process that exceeds the memory limit fails in a controlled way, and the host is unaffected. |
| `REQ-0049` | GATE_SPECIFICATION | `canonical:GATE-3#8.5` | yes | `COMPLETE` | `COMPLETE` | The workspace cannot outgrow its limit. |
| `REQ-0050` | GATE_SPECIFICATION | `canonical:GATE-3#8.6` | yes | `COMPLETE` | `COMPLETE` | A command that exceeds its timeout is ended together with every process it started, including a process that left its session, and nothing is left running. |
| `REQ-0051` | GATE_SPECIFICATION | `canonical:GATE-3#8.7` | yes | `COMPLETE` | `COMPLETE` | Standard output and standard error are bounded while they are read; what exceeds the bound is truncated explicitly and stored whole as an artifact, and memory is never unbounded. |
| `REQ-0052` | GATE_SPECIFICATION | `canonical:GATE-3#9.1` | yes | `COMPLETE` | `COMPLETE` | A sandbox has no network by default: only loopback exists, and every policy the Gate ships denies the network. |
| `REQ-0053` | GATE_SPECIFICATION | `canonical:GATE-3#9.2` | yes | `COMPLETE` | `COMPLETE` | An attempt to reach an external address from a sandbox without network fails. |
| `REQ-0054` | GATE_SPECIFICATION | `canonical:GATE-3#9.3` | yes | `COMPLETE` | `COMPLETE` | The one other network profile is local services only, on an internal network with no route outside, and it is chosen by the policy, never by a request. |
| `REQ-0055` | GATE_SPECIFICATION | `canonical:GATE-3#9.4` | yes | `COMPLETE` | `COMPLETE` | No package installation from the internet is offered; the image carries the toolchain the Gate's tests need. |
| `REQ-0056` | GATE_SPECIFICATION | `canonical:GATE-3#10.1` | yes | `COMPLETE` | `COMPLETE` | A sandbox receives only the variables its policy explicitly allows, and no variable of the controller — provider key, repository token, agent socket, cloud credential or engine address — reaches it. |
| `REQ-0057` | GATE_SPECIFICATION | `canonical:GATE-3#10.2` | yes | `COMPLETE` | `COMPLETE` | A command's environment inside the sandbox is the allowlist and nothing else. |
| `REQ-0058` | GATE_SPECIFICATION | `canonical:GATE-3#10.3` | yes | `COMPLETE` | `COMPLETE` | A policy cannot allow a credential-shaped variable into a command's environment. |
| `REQ-0059` | GATE_SPECIFICATION | `canonical:GATE-3#10.4` | yes | `COMPLETE` | `COMPLETE` | No Git credential, credential helper, SSH key or agent socket exists in a sandbox. |
| `REQ-0060` | GATE_SPECIFICATION | `canonical:GATE-3#11.1` | yes | `COMPLETE` | `COMPLETE` | A workspace has an identity and an explicit lifecycle, belongs to exactly one run, and a run holds at most one active session. |
| `REQ-0061` | GATE_SPECIFICATION | `canonical:GATE-3#11.2` | yes | `COMPLETE` | `COMPLETE` | A workspace is provisioned only from an authorised snapshot, named by its artifact identifier and never by a path, and becomes a repository the tools can work on. |
| `REQ-0062` | GATE_SPECIFICATION | `canonical:GATE-3#11.3` | yes | `COMPLETE` | `COMPLETE` | Anything but a workspace snapshot artifact is refused before the run exists, and a snapshot for a team that executes no tool is refused. |
| `REQ-0063` | GATE_SPECIFICATION | `canonical:GATE-3#11.4` | yes | `COMPLETE` | `COMPLETE` | A snapshot whose digest differs from its record, or that carries a link or an escaping member, is refused, and no session survives the refusal. |
| `REQ-0064` | GATE_SPECIFICATION | `canonical:GATE-3#11.5` | yes | `COMPLETE` | `COMPLETE` | One run cannot read or write another run's files, nor see its processes. |
| `REQ-0065` | GATE_SPECIFICATION | `canonical:GATE-3#11.6` | yes | `COMPLETE` | `COMPLETE` | The development working tree of this repository is never an agent's workspace. |
| `REQ-0066` | GATE_SPECIFICATION | `canonical:GATE-3#12.1` | yes | `COMPLETE` | `COMPLETE` | One canonical path resolver decides every path a tool touches; no other module re-implements path safety. |
| `REQ-0067` | GATE_SPECIFICATION | `canonical:GATE-3#12.2` | yes | `COMPLETE` | `COMPLETE` | Traversal, absolute paths, drive letters, UNC paths, null bytes and normalisation tricks are refused, each with its own reason. |
| `REQ-0068` | GATE_SPECIFICATION | `canonical:GATE-3#12.3` | yes | `COMPLETE` | `COMPLETE` | A link inside the workspace that points outside it cannot be read or written through, whether it names a file, a directory, the root or climbs out relatively; a link that stays inside is followed. |
| `REQ-0069` | GATE_SPECIFICATION | `canonical:GATE-3#12.4` | yes | `COMPLETE` | `COMPLETE` | Listing, reading, writing, searching and patching work inside the workspace of a real sandbox. |
| `REQ-0070` | GATE_SPECIFICATION | `canonical:GATE-3#12.5` | yes | `COMPLETE` | `COMPLETE` | A read and a write are bounded in size, an oversized one is refused, and binary content is refused as text rather than mangled. |
| `REQ-0071` | GATE_SPECIFICATION | `canonical:GATE-3#12.6` | yes | `COMPLETE` | `COMPLETE` | A write validates its parent directory and replaces the file atomically. |
| `REQ-0072` | GATE_SPECIFICATION | `canonical:GATE-3#12.7` | yes | `COMPLETE` | `COMPLETE` | A patch applies only inside the workspace; a patch whose context does not match, or that has one bad file, changes nothing. |
| `REQ-0073` | GATE_SPECIFICATION | `canonical:GATE-3#12.8` | yes | `COMPLETE` | `COMPLETE` | A search is confined to the workspace and bounded in results, output and duration. |
| `REQ-0074` | GATE_SPECIFICATION | `canonical:GATE-3#12.9` | yes | `COMPLETE` | `COMPLETE` | A path refused inside the sandbox reaches the agent as a denial, not as a failure of the sandbox. |
| `REQ-0075` | GATE_SPECIFICATION | `canonical:GATE-3#13.1` | yes | `COMPLETE` | `COMPLETE` | Shell execution runs only inside the sandbox container, with the command, the working directory, the allowed environment and the timeout passed as structured arguments. |
| `REQ-0076` | GATE_SPECIFICATION | `canonical:GATE-3#13.2` | yes | `COMPLETE` | `COMPLETE` | Standard output, standard error, a zero and a non-zero exit code, a missing executable and a child process are all reported faithfully. |
| `REQ-0077` | GATE_SPECIFICATION | `canonical:GATE-3#13.3` | yes | `COMPLETE` | `COMPLETE` | The working directory resolves inside the workspace, and an escaping one is refused. |
| `REQ-0078` | GATE_SPECIFICATION | `canonical:GATE-3#13.4` | yes | `COMPLETE` | `COMPLETE` | A payload that tries to reach a host command affects only the sandbox, inside its policy, and the host is unchanged. |
| `REQ-0079` | GATE_SPECIFICATION | `canonical:GATE-3#13.5` | yes | `COMPLETE` | `COMPLETE` | A command still running when its run is cancelled is stopped, with every process it started. |
| `REQ-0080` | GATE_SPECIFICATION | `canonical:GATE-3#14.1` | yes | `COMPLETE` | `COMPLETE` | Inside the workspace an agent can read the status, the working and the staged diff, the log and a commit, stage files and commit locally. |
| `REQ-0081` | GATE_SPECIFICATION | `canonical:GATE-3#14.2` | yes | `COMPLETE` | `COMPLETE` | Every Git tool builds a fixed argument vector, a revision that looks like an option is refused, and a commit skips hooks and carries its message as one argument. |
| `REQ-0082` | GATE_SPECIFICATION | `canonical:GATE-3#14.3` | yes | `COMPLETE` | `COMPLETE` | No remote Git operation is offered or possible — no push, fetch, clone or remote — and no destructive operation — hard reset, clean, rebase, history filtering, forced push — is offered by default. |
| `REQ-0083` | GATE_SPECIFICATION | `canonical:GATE-3#14.4` | yes | `COMPLETE` | `COMPLETE` | An agent's commits carry an explicit sandbox identity that is not a person, separate from the owner's development identity, and the difference is documented. |
| `REQ-0084` | GATE_SPECIFICATION | `canonical:GATE-3#14.5` | yes | `COMPLETE` | `COMPLETE` | Git output is bounded like any other output. |
| `REQ-0085` | GATE_SPECIFICATION | `canonical:GATE-3#15.1` | yes | `COMPLETE` | `COMPLETE` | A session moves through explicit states, is created ready for its run and is removed with it. |
| `REQ-0086` | GATE_SPECIFICATION | `canonical:GATE-3#15.2` | yes | `COMPLETE` | `COMPLETE` | A running tool holds its session in the running state, and inspecting a session reports the store and the engine side by side. |
| `REQ-0087` | GATE_SPECIFICATION | `canonical:GATE-3#15.3` | yes | `COMPLETE` | `COMPLETE` | When a run ends or is cancelled its sandbox is removed, and no container or temporary volume is left behind. |
| `REQ-0088` | GATE_SPECIFICATION | `canonical:GATE-3#15.4` | yes | `COMPLETE` | `COMPLETE` | A restarted service reconciles from the store and the engine rather than from memory: it keeps a live session, removes a container no session owns, and fails a session whose container vanished. |
| `REQ-0089` | GATE_SPECIFICATION | `canonical:GATE-3#15.5` | yes | `COMPLETE` | `COMPLETE` | Reconciliation touches only containers this service instance owns, so another stack or a test on the same engine is never cleaned up by it. |
| `REQ-0090` | GATE_SPECIFICATION | `canonical:GATE-3#15.6` | yes | `COMPLETE` | `COMPLETE` | An orphan sweeper expires only sessions that have expired and are not running, in bounded, deterministic batches, and never removes an active workspace. |
| `REQ-0091` | GATE_SPECIFICATION | `canonical:GATE-3#16.1` | yes | `COMPLETE` | `COMPLETE` | This Gate adds its schema through a new migration and edits no migration that has already been applied. |
| `REQ-0092` | GATE_SPECIFICATION | `canonical:GATE-3#16.2` | yes | `COMPLETE` | `COMPLETE` | The existing tool call, artifact and run entities are evolved rather than duplicated, and the one new table holds only what nothing else could: the sandbox session. |
| `REQ-0093` | GATE_SPECIFICATION | `canonical:GATE-3#16.3` | yes | `COMPLETE` | `COMPLETE` | A database created from nothing reaches the head revision, and a database at the previous Gate's head upgrades without losing a row. |
| `REQ-0094` | GATE_SPECIFICATION | `canonical:GATE-3#16.4` | yes | `COMPLETE` | `COMPLETE` | Every execution is traceable from the task through the run, the agent run, the tool request, the sandbox session and the execution to the result, and none of it holds private reasoning. |
| `REQ-0095` | GATE_SPECIFICATION | `canonical:GATE-3#16.5` | yes | `COMPLETE` | `COMPLETE` | A retried request never executes twice: the execution is keyed by the tool request it answers. |
| `REQ-0096` | GATE_SPECIFICATION | `canonical:GATE-3#16.6` | yes | `COMPLETE` | `COMPLETE` | The store the service runs against in the stack records sessions and executions in the real database with the same behaviour the suite asserts in memory. |
| `REQ-0097` | GATE_SPECIFICATION | `canonical:GATE-3#16.7` | yes | `COMPLETE` | `COMPLETE` | Nothing this Gate persists is training-eligible, and no table stores a credential. |
| `REQ-0098` | GATE_SPECIFICATION | `canonical:GATE-3#17.1` | yes | `COMPLETE` | `COMPLETE` | A pending tool request of a stage with a sandbox policy is checked against the policy, executed in the run's sandbox, its result persisted, and the workflow resumes. |
| `REQ-0099` | GATE_SPECIFICATION | `canonical:GATE-3#17.2` | yes | `COMPLETE` | `COMPLETE` | A stage without a sandbox policy keeps the previous Gate's behaviour: the request waits for a result delivered through the API. |
| `REQ-0100` | GATE_SPECIFICATION | `canonical:GATE-3#17.3` | yes | `COMPLETE` | `COMPLETE` | The run plan names the sandbox policy of each stage and the workspace source, frozen when the run is created. |
| `REQ-0101` | GATE_SPECIFICATION | `canonical:GATE-3#17.4` | yes | `COMPLETE` | `COMPLETE` | A tool result returns to the agent as labelled data in its own channel and never as an instruction. |
| `REQ-0102` | GATE_SPECIFICATION | `canonical:GATE-3#17.5` | yes | `COMPLETE` | `COMPLETE` | A large result reaches the model truncated inline with an artifact reference, within the size the runtime accepts for a tool result. |
| `REQ-0103` | GATE_SPECIFICATION | `canonical:GATE-3#17.6` | yes | `COMPLETE` | `COMPLETE` | A tool that times out returns a normalised error result the agent receives, and the run never stays waiting for a tool for ever. |
| `REQ-0104` | GATE_SPECIFICATION | `canonical:GATE-3#17.7` | yes | `COMPLETE` | `COMPLETE` | Cancelling a run during a long command stops the command, records the cancellation, ends the run cancelled and leaves no process behind. |
| `REQ-0105` | GATE_SPECIFICATION | `canonical:GATE-3#17.8` | yes | `COMPLETE` | `COMPLETE` | A sandbox service restart while a run executes does not lose the run: the session is reconciled and the run completes. |
| `REQ-0106` | GATE_SPECIFICATION | `canonical:GATE-3#18.1` | yes | `COMPLETE` | `COMPLETE` | A profile that may request tools names the sandbox policy that governs them, and a profile with tools and no policy is refused. |
| `REQ-0107` | GATE_SPECIFICATION | `canonical:GATE-3#18.2` | yes | `COMPLETE` | `COMPLETE` | No agent is given every tool: each profile's permitted actions are within its policy's tools. |
| `REQ-0108` | GATE_SPECIFICATION | `canonical:GATE-3#18.3` | yes | `COMPLETE` | `COMPLETE` | A developer profile may read, search, write, patch, run tests and use the local Git tools its policy allows. |
| `REQ-0109` | GATE_SPECIFICATION | `canonical:GATE-3#18.4` | yes | `COMPLETE` | `COMPLETE` | The reviewer is read-only: read, search, diff and test results, and no writing tool. |
| `REQ-0110` | GATE_SPECIFICATION | `canonical:GATE-3#18.5` | yes | `COMPLETE` | `COMPLETE` | The planner has no writing tool and works from context alone. |
| `REQ-0111` | GATE_SPECIFICATION | `canonical:GATE-3#18.6` | yes | `COMPLETE` | `COMPLETE` | A minimal coding team — planner, developer, reviewer — proves the flow, and no larger team is built. |
| `REQ-0112` | GATE_SPECIFICATION | `canonical:GATE-3#19.1` | yes | `COMPLETE` | `COMPLETE` | Full output, large diffs and workspace snapshots are stored in the existing artifact infrastructure, recorded as artifacts, and no second store is created. |
| `REQ-0113` | GATE_SPECIFICATION | `canonical:GATE-3#19.2` | yes | `COMPLETE` | `COMPLETE` | A workspace snapshot is created from an explicit source directory by a documented command, and never from the development working tree implicitly. |
| `REQ-0114` | GATE_SPECIFICATION | `canonical:GATE-3#20.1` | yes | `COMPLETE` | `COMPLETE` | A registry of sandbox image profiles exists, the architecture accepts new profiles, and one functional profile for this project carries Git and Python. |
| `REQ-0115` | GATE_SPECIFICATION | `canonical:GATE-3#20.2` | yes | `COMPLETE` | `COMPLETE` | The image is built as part of the Gate from a base pinned by digest and packages pinned by version, and never from a moving tag. |
| `REQ-0116` | GATE_SPECIFICATION | `canonical:GATE-3#20.3` | yes | `COMPLETE` | `COMPLETE` | The image is addressed by a fingerprint of its inputs, and a missing or stale image is refused rather than substituted. |
| `REQ-0117` | GATE_SPECIFICATION | `canonical:GATE-3#20.4` | yes | `COMPLETE` | `COMPLETE` | The sandbox gate builds the service image and the sandbox image before it measures anything. |
| `REQ-0118` | GATE_SPECIFICATION | `canonical:GATE-3#20.5` | yes | `COMPLETE` | `COMPLETE` | The sandbox service installs the one dependency lock the dependency scan reads, so its Python dependencies are scanned with the rest; the sandbox image's system packages are pinned by version, and what the scan does not cover is documented rather than implied. |
| `REQ-0119` | GATE_SPECIFICATION | `canonical:GATE-3#21.1` | yes | `COMPLETE` | `COMPLETE` | An internal service contract creates a session, executes a tool, inspects a session and terminates it, and it is reached only as activities on the sandbox's task queue. |
| `REQ-0120` | GATE_SPECIFICATION | `canonical:GATE-3#21.2` | yes | `COMPLETE` | `COMPLETE` | A refusal is recorded as an execution with its reason, so a denied request is as traceable as an executed one. |
| `REQ-0121` | GATE_SPECIFICATION | `canonical:GATE-3#21.3` | yes | `COMPLETE` | `COMPLETE` | The service's health is a poller on its queue and an engine that answers, not a process that exists. |
| `REQ-0122` | GATE_SPECIFICATION | `canonical:GATE-3#22.1` | yes | `COMPLETE` | `COMPLETE` | The service publishes instruments for sessions created and active, tool executions, their duration, failures, timeouts and policy refusals. |
| `REQ-0123` | GATE_SPECIFICATION | `canonical:GATE-3#22.2` | yes | `COMPLETE` | `COMPLETE` | Every metric label is low cardinality, a command never becomes a label, and a refusal is counted by its reason. |
| `REQ-0124` | GATE_SPECIFICATION | `canonical:GATE-3#22.3` | yes | `COMPLETE` | `COMPLETE` | Logs carry the run, the agent, the sandbox, the tool, the status and the duration, and never a whole result, a secret or the host environment. |
| `REQ-0125` | GATE_SPECIFICATION | `canonical:GATE-3#22.4` | yes | `COMPLETE` | `COMPLETE` | The observability stack scrapes the sandbox service. |
| `REQ-0126` | GATE_SPECIFICATION | `canonical:GATE-3#23.1` | yes | `COMPLETE` | `COMPLETE` | The run page shows each tool the sandbox executed: the tool, its status, its duration, the abbreviated sandbox identifier and a summary. |
| `REQ-0127` | GATE_SPECIFICATION | `canonical:GATE-3#23.2` | yes | `COMPLETE` | `COMPLETE` | The page never receives a tool's output and offers no interactive shell. |
| `REQ-0128` | GATE_SPECIFICATION | `canonical:GATE-3#23.3` | yes | `COMPLETE` | `COMPLETE` | The command line interface stays reserved for the Gate that owns it. |
| `REQ-0129` | GATE_SPECIFICATION | `canonical:GATE-3#24.1` | yes | `COMPLETE` | `COMPLETE` | A synthetic repository with a defective function and a failing test is provisioned as a snapshot, and a coding run over it reads the code, runs the failing test, patches the code, runs the passing test, reads the diff, commits locally, is reviewed and finishes. |
| `REQ-0130` | GATE_SPECIFICATION | `canonical:GATE-3#24.2` | yes | `COMPLETE` | `COMPLETE` | The scenario drives the real workflow, the real activities, the real sandbox service and the real container engine, with only the model replaced by a deterministic script. |
| `REQ-0131` | GATE_SPECIFICATION | `canonical:GATE-3#24.3` | yes | `COMPLETE` | `COMPLETE` | An automatic proof shows a shell request did not execute on the host: a sentinel outside the sandbox is neither created nor modified. |
| `REQ-0132` | GATE_SPECIFICATION | `canonical:GATE-3#24.4` | yes | `COMPLETE` | `COMPLETE` | The scenario asserts what the run recorded — its terminal state, its tool executions and the test that passed — rather than what the harness sent. |
| `REQ-0133` | GATE_SPECIFICATION | `canonical:GATE-3#25.1` | yes | `COMPLETE` | `COMPLETE` | The repository's one verification command covers this Gate, in its targeted and its full mode. |
| `REQ-0134` | GATE_SPECIFICATION | `canonical:GATE-3#25.2` | yes | `COMPLETE` | `COMPLETE` | A runbook documents the lifecycle, the tool policy, the filesystem, the shell, Git, the network, resources, artifacts, cleanup, debugging and the security boundary. |
| `REQ-0135` | GATE_SPECIFICATION | `canonical:GATE-3#25.3` | yes | `COMPLETE` | `COMPLETE` | The architecture, development, version and entry documents describe what this Gate delivered rather than what was planned. |
| `REQ-0136` | GATE_SPECIFICATION | `canonical:GATE-3#25.4` | yes | `COMPLETE` | `COMPLETE` | The structural decisions of this Gate are recorded as ADRs and listed in the index. |
| `REQ-0137` | GATE_SPECIFICATION | `canonical:GATE-3#25.5` | yes | `COMPLETE` | `COMPLETE` | The Gate produces its retrospective from the canonical template, and its reusable lessons are recorded with the guardrail that protects the property rather than one file. |
| `REQ-0138` | GATE_SPECIFICATION | `canonical:GATE-3#25.6` | yes | `COMPLETE` | `COMPLETE` | Every commit of the Gate and its checkpoint tag are on the authorised remote when the Gate closes. |
| `REQ-0139` | GATE_SPECIFICATION | `canonical:GATE-3#25.7` | yes | `COMPLETE` | `COMPLETE` | The Gate closes at the project's own internal verdict, leaves the milestone verdict to a fresh-session audit, and starts no part of the Gate that follows it. |
| `LESSON-REQ-0001` | LESSON | `lesson:LSN-0001` | yes | `COMPLETE` | `COMPLETE` | Verify checkpoint validation must succeed from a detached checkout of the checkpoint tag |
| `LESSON-REQ-0002` | LESSON | `lesson:LSN-0002` | yes | `COMPLETE` | `COMPLETE` | Verify a file inventory must be recomputed from the repository, never trusted as an assertion |
| `LESSON-REQ-0003` | LESSON | `lesson:LSN-0003` | yes | `COMPLETE` | `COMPLETE` | Verify every operation attempt must be auditable, including a refusal decided before execution |
| `LESSON-REQ-0004` | LESSON | `lesson:LSN-0004` | yes | `COMPLETE` | `COMPLETE` | Verify a checkpoint may never claim readiness while it also claims to be blocked |
| `LESSON-REQ-0005` | LESSON | `lesson:LSN-0005` | yes | `COMPLETE` | `COMPLETE` | Verify a PASS requires evidence that can be executed or resolved, not a statement |
| `LESSON-REQ-0006` | LESSON | `lesson:LSN-0006` | yes | `COMPLETE` | `COMPLETE` | Verify the repository must be self-contained; a specification may not live outside it |
| `LESSON-REQ-0007` | LESSON | `lesson:LSN-0007` | yes | `COMPLETE` | `COMPLETE` | Verify independent validation cannot be declared by the run that did the work |
| `LESSON-REQ-0008` | LESSON | `lesson:LSN-0008` | yes | `COMPLETE` | `COMPLETE` | Verify requirement completeness must be total and evidence-backed before handoff |
| `LESSON-REQ-0009` | LESSON | `lesson:LSN-0009` | yes | `COMPLETE` | `COMPLETE` | Verify a red gate requires rework, never a waiver, and never a weakened check |
| `LESSON-REQ-0010` | LESSON | `lesson:LSN-0010` | yes | `COMPLETE` | `COMPLETE` | Verify a recorded command must carry runtime, working directory, commit and purpose to be replayable |
| `LESSON-REQ-0011` | LESSON | `lesson:LSN-0011` | yes | `COMPLETE` | `COMPLETE` | Verify a control over a checkpoint's own evidence must be scoped to the moment it matters |
| `LESSON-REQ-0012` | LESSON | `lesson:LSN-0012` | yes | `COMPLETE` | `COMPLETE` | Verify sealed checkpoints and their tags are immutable, and tooling must keep validating them |
| `LESSON-REQ-0013` | LESSON | `lesson:LSN-0013` | no | `COMPLETE` | `COMPLETE` | Verify an installed capability must be detected by resolved path, not by a bare command lookup |
| `LESSON-REQ-0014` | LESSON | `lesson:LSN-0014` | yes | `COMPLETE` | `COMPLETE` | Verify evidence must be recorded as it happens, not reconstructed at the end of a run |
| `LESSON-REQ-0015` | LESSON | `lesson:LSN-0015` | yes | `COMPLETE` | `COMPLETE` | Verify every positive terminal status needs one shared promotion invariant |
| `LESSON-REQ-0016` | LESSON | `lesson:LSN-0016` | yes | `COMPLETE` | `COMPLETE` | Verify a mandatory set must be closed by policy, never chosen by the caller |
| `LESSON-REQ-0017` | LESSON | `lesson:LSN-0017` | yes | `COMPLETE` | `COMPLETE` | Verify a completeness denominator must come from a source the delivery does not own |
| `LESSON-REQ-0018` | LESSON | `lesson:LSN-0018` | yes | `COMPLETE` | `COMPLETE` | Verify a structured reference must be resolved, not merely well typed |
| `LESSON-REQ-0019` | LESSON | `lesson:LSN-0019` | yes | `COMPLETE` | `COMPLETE` | Verify a derived artifact must carry a fingerprint of the inputs that produced it |
| `LESSON-REQ-0020` | LESSON | `lesson:LSN-0020` | yes | `COMPLETE` | `COMPLETE` | Verify evidence produced from a dirty tree needs immutable input identity |
| `LESSON-REQ-0021` | LESSON | `lesson:LSN-0021` | yes | `COMPLETE` | `COMPLETE` | Verify sealed history needs an anchor outside the content it describes |
| `LESSON-REQ-0022` | LESSON | `lesson:LSN-0022` | yes | `COMPLETE` | `COMPLETE` | Verify an authoritative count must be derived once, never maintained by hand twice |
| `LESSON-REQ-0023` | LESSON | `lesson:LSN-0023` | yes | `COMPLETE` | `COMPLETE` | Verify a lesson must cite a source that actually records the finding it claims |
| `LESSON-REQ-0024` | LESSON | `lesson:LSN-0024` | yes | `COMPLETE` | `COMPLETE` | Verify a control is finished only when its positive path has been executed, not only its refusals |
| `LESSON-REQ-0025` | LESSON | `lesson:LSN-0025` | yes | `COMPLETE` | `COMPLETE` | Verify a generic guardrail derives repository state instead of naming today's checkpoint |
| `LESSON-REQ-0026` | LESSON | `lesson:LSN-0026` | yes | `COMPLETE` | `COMPLETE` | Verify an adversarial battery without a null-mutation control proves nothing |
| `LESSON-REQ-0027` | LESSON | `lesson:LSN-0027` | yes | `COMPLETE` | `COMPLETE` | Verify a lesson's prose may record a residual limit but may never contradict its status |
| `LESSON-REQ-0028` | LESSON | `lesson:LSN-0028` | yes | `COMPLETE` | `COMPLETE` | Verify a configuration key that no code reads is a defect, not documentation |
| `LESSON-REQ-0029` | LESSON | `lesson:LSN-0029` | yes | `COMPLETE` | `COMPLETE` | Verify a required protocol transition must never turn a mandatory gate red |
| `LESSON-REQ-0030` | LESSON | `lesson:LSN-0031` | yes | `COMPLETE` | `COMPLETE` | Verify an empty applicable set is not a missing required set, and a control must tell them apart |
| `LESSON-REQ-0031` | LESSON | `lesson:LSN-0032` | yes | `COMPLETE` | `COMPLETE` | Verify a control written while one Gate was the only Gate stops being a control when the next one starts |
| `LESSON-REQ-0032` | LESSON | `lesson:LSN-0033` | yes | `COMPLETE` | `COMPLETE` | Verify a value bound in middleware is absent in the handlers that run outside it |
| `LESSON-REQ-0033` | LESSON | `lesson:LSN-0034` | yes | `COMPLETE` | `COMPLETE` | Verify re-deriving what the framework already computed diverges from the framework |
| `LESSON-REQ-0034` | LESSON | `lesson:LSN-0035` | yes | `COMPLETE` | `COMPLETE` | Verify captured subprocess output decoded or re-emitted with the platform codepage crashes the tool, not the work |
| `LESSON-REQ-0035` | LESSON | `lesson:LSN-0036` | yes | `COMPLETE` | `COMPLETE` | Verify a gate that runs inside an image measures the image, not the source |
| `LESSON-REQ-0036` | LESSON | `lesson:LSN-0037` | yes | `COMPLETE` | `COMPLETE` | Verify a shared control that names an identifier the repository derives stops being a control when that identifier moves |
| `LESSON-REQ-0037` | LESSON | `lesson:LSN-0038` | yes | `COMPLETE` | `COMPLETE` | Verify two representations of one concept in one module disagree, and the safer one loses |
| `LESSON-REQ-0038` | LESSON | `lesson:LSN-0039` | yes | `COMPLETE` | `COMPLETE` | Verify a test that writes to the operational database leaves production data behind |
| `LESSON-REQ-0039` | LESSON | `lesson:LSN-0040` | yes | `COMPLETE` | `COMPLETE` | Verify a control that judges sealed history only runs once a successor anchors it |
| `LESSON-REQ-0040` | LESSON | `lesson:LSN-0041` | yes | `COMPLETE` | `COMPLETE` | Verify an editing path that consumes a backslash escape leaves a control character, and the control it belonged to silently matches nothing |
| `LESSON-REQ-0041` | LESSON | `lesson:LSN-0042` | yes | `COMPLETE` | `COMPLETE` | Verify a naming convention rewrites a CHECK constraint's name and leaves a UNIQUE constraint's alone |
| `LESSON-REQ-0042` | LESSON | `lesson:LSN-0043` | yes | `COMPLETE` | `COMPLETE` | Verify a log line is not evidence that another process is ready |
| `LESSON-REQ-0043` | LESSON | `lesson:LSN-0044` | yes | `COMPLETE` | `COMPLETE` | Verify a boundary scan must read the code rather than the prose, and must be shown to fire on a mutated module |
| `LESSON-REQ-0044` | LESSON | `lesson:LSN-0045` | yes | `COMPLETE` | `COMPLETE` | Verify a counted test suite must declare its cases statically, because the denominator is read from the source |
| `LESSON-REQ-0045` | LESSON | `lesson:LSN-0046` | yes | `COMPLETE` | `COMPLETE` | Verify a timeout that cancels the task it runs in leaves nothing able to record what happened |
| `LESSON-REQ-0046` | LESSON | `lesson:LSN-0047` | yes | `COMPLETE` | `COMPLETE` | Verify a refusal that misnames the defect spends the only repair on the wrong correction |
| `LESSON-REQ-0047` | LESSON | `lesson:LSN-0048` | yes | `COMPLETE` | `COMPLETE` | Verify a state and the event that explains it, written in two commits, are written event first |
| `LESSON-REQ-0048` | LESSON | `lesson:LSN-0049` | yes | `COMPLETE` | `COMPLETE` | Verify a metric read the instant after the call that moved it is read before the scrape that carries it |
| `LESSON-REQ-0049` | LESSON | `lesson:LSN-0050` | yes | `COMPLETE` | `COMPLETE` | Verify a checkpoint sealed without naming its own tag cannot be validated from that tag |
| `LESSON-REQ-0050` | LESSON | `lesson:LSN-0051` | yes | `COMPLETE` | `COMPLETE` | Verify a payload one service bounds for another must be bounded as the receiver measures it |
| `LESSON-REQ-0051` | LESSON | `lesson:LSN-0052` | yes | `COMPLETE` | `COMPLETE` | Verify two processes that meet on a queue must name what crosses it once, and a real run must exercise both |
| `LESSON-REQ-0052` | LESSON | `lesson:LSN-0053` | yes | `COMPLETE` | `COMPLETE` | Verify a process sweep that reads what a forking process holds waits on the processes it has to kill |
| `LESSON-REQ-0053` | LESSON | `lesson:LSN-0054` | no | `COMPLETE` | `COMPLETE` | Verify a pre-push check narrower than the change's reach lets a red gate reach the public remote |

## Evidence

### REQ-0001 - canonical:GATE-3#1.1

- Source reference: docs/GATE-3-CHECKLIST.md row 1.1
- Description: A canonical, machine-readable requirement specification exists for this Gate and the registry mirrors it row for row.
- Implementation: `file:.iacode/policies/canonical-requirements.json`
- Test: `test:Gate3CanonicalSpecificationTests`
- Negative test: _none_
- Documentation: `file:docs/GATE-3-CHECKLIST.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0002 - canonical:GATE-3#1.2

- Source reference: docs/GATE-3-CHECKLIST.md row 1.2
- Description: The closed mandatory gate registry carries the executable gate this Gate introduces, and that gate builds what it measures before measuring it.
- Implementation: `file:.iacode/policies/quality-gates.json`, `file:scripts/iacode/gates/sandbox_tests.py`
- Test: `test:Gate3MandatoryGateTests`
- Negative test: _none_
- Documentation: _none_
- Validation: `command:cmd-0115`, `command:cmd-0111`, `checkpoint:REWORK-LOG.jsonl`
- Guardrail: _none_

### REQ-0003 - canonical:GATE-3#1.3

- Source reference: docs/GATE-3-CHECKLIST.md row 1.3
- Description: The test suite this Gate introduces is declared canonically, is counted by the count derivation and is resolvable as evidence.
- Implementation: `file:.iacode/policies/test-suites.json`
- Test: `test:Gate3TestSuiteRegistryTests`
- Negative test: _none_
- Documentation: _none_
- Validation: `command:cmd-0120`, `checkpoint:COUNTS.json`
- Guardrail: _none_

### REQ-0004 - canonical:GATE-3#1.4

- Source reference: docs/GATE-3-CHECKLIST.md row 1.4
- Description: The internal Red Team battery of this Gate is executable, scoped to the sandbox, runs its attacks against the real container engine and records a null-mutation control.
- Implementation: `file:scripts/development-ledger/gate3_red_team.py`
- Test: `test:Gate3RedTeamHarnessTests`
- Negative test: _none_
- Documentation: _none_
- Validation: `checkpoint:M1-INTERNAL-RED-TEAM.json`, `checkpoint:RED-TEAM-REPORT.md`, `command:cmd-0119`
- Guardrail: _none_

### REQ-0005 - canonical:GATE-3#1.5

- Source reference: docs/GATE-3-CHECKLIST.md row 1.5
- Description: The reservation of the sandbox directory is consumed by the Gate that owns it, and every reservation of a later Gate is still enforced.
- Implementation: `file:.iacode/policies/gate-scope.json`
- Test: `test:Gate3ScopeTests`
- Negative test: _none_
- Documentation: `file:services/sandbox/README.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0006 - canonical:GATE-3#1.6

- Source reference: docs/GATE-3-CHECKLIST.md row 1.6
- Description: One documented command verifies this Gate, adds the stages it introduces and keeps a targeted mode that does not restart the stack.
- Implementation: `file:scripts/iacode/verify.py`
- Test: `test:Gate3VerificationStageTests`
- Negative test: _none_
- Documentation: _none_
- Validation: `command:cmd-0105`, `checkpoint:VERIFICATION-REPORT.json`
- Guardrail: _none_

### REQ-0007 - canonical:GATE-3#2.1

- Source reference: docs/GATE-3-CHECKLIST.md row 2.1
- Description: The repository publishes to exactly one authorised remote, and a remote pointing anywhere else is refused rather than used.
- Implementation: `file:scripts/development-ledger/remote_sync.py`
- Test: `test:test_a_remote_other_than_the_authorised_one_fails`, `test:test_the_authorised_remote_is_the_one_the_policy_names`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0008 - canonical:GATE-3#2.2

- Source reference: docs/GATE-3-CHECKLIST.md row 2.2
- Description: The whole history was scanned for credentials before its first publication, and a finding names the commit, the file, the line and the kind but never the value.
- Implementation: `file:scripts/development-ledger/secret_scan.py`, `file:.iacode/policies/secret-scan-allowlist.json`
- Test: `test:SecretScanTests`, `test:test_a_finding_never_prints_the_value`
- Negative test: _none_
- Documentation: _none_
- Validation: `command:cmd-0005`
- Guardrail: _none_

### REQ-0009 - canonical:GATE-3#2.3

- Source reference: docs/GATE-3-CHECKLIST.md row 2.3
- Description: The published history carries no credential, and the check is repeatable against the history as it now stands.
- Implementation: `file:scripts/development-ledger/secret_scan.py`
- Test: `test:PublishedHistoryTests`, `test:test_the_published_history_carries_no_credential`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0010 - canonical:GATE-3#2.4

- Source reference: docs/GATE-3-CHECKLIST.md row 2.4
- Description: Every push is preceded by a scan of exactly the staged content, and an allowance matches a value's digest rather than a path.
- Implementation: `file:scripts/development-ledger/secret_scan.py`
- Test: `test:test_the_staged_scan_judges_only_the_staged_content`, `test:test_the_allowlist_matches_the_value_and_not_the_path`
- Negative test: _none_
- Documentation: _none_
- Validation: `command:cmd-0010`, `command:cmd-0058`
- Guardrail: _none_

### REQ-0011 - canonical:GATE-3#2.5

- Source reference: docs/GATE-3-CHECKLIST.md row 2.5
- Description: Whether the branch and the checkpoint tag are on the remote is asked of the remote, an unpushed commit or a missing tag fails, and an unreachable remote is never a pass.
- Implementation: `file:scripts/development-ledger/remote_sync.py`
- Test: `test:RemoteSyncTests`, `test:test_an_unreachable_remote_is_unavailable_and_never_a_pass`
- Negative test: _none_
- Documentation: _none_
- Validation: `command:cmd-0006`
- Guardrail: _none_

### REQ-0012 - canonical:GATE-3#2.6

- Source reference: docs/GATE-3-CHECKLIST.md row 2.6
- Description: The commit, push, tag and correction rules are stated in the development contract and recorded as a decision: atomic commits, green commits only, no rewriting of published history, no moving of a published tag, and no credential in a URL, a configuration or a versioned file.
- Implementation: _none_
- Test: `test:GitPolicyDocumentationTests`
- Negative test: _none_
- Documentation: `file:docs/DEVELOPMENT-CONTRACT.md`, `file:docs/adr/ADR-0024-public-remote-and-atomic-commits.md`, `file:.iacode/policies/secret-policy.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0013 - canonical:GATE-3#2.7

- Source reference: docs/GATE-3-CHECKLIST.md row 2.7
- Description: The history of this Gate's development is preserved as observable data — requirement, commits, tests, fixes, checkpoint — and nothing in it is marked as training-eligible.
- Implementation: _none_
- Test: `test:test_the_decision_is_recorded_as_an_adr`
- Negative test: _none_
- Documentation: `file:docs/adr/ADR-0024-public-remote-and-atomic-commits.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0014 - canonical:GATE-3#3.1

- Source reference: docs/GATE-3-CHECKLIST.md row 3.1
- Description: A command the ledger could not replay is refused before it executes, the refusal is itself recorded, and the recorder and the validator apply one shared replayability rule.
- Implementation: `file:scripts/development-ledger/ledger_common.py`, `file:scripts/development-ledger/record_command.py`, `file:scripts/development-ledger/validate_checkpoint.py`
- Test: `test:LedgerCommandReplayabilityTests`, `test:test_rejected_command_is_never_executed`, `test:test_recorder_and_validator_share_one_rule`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0015 - canonical:GATE-3#3.2

- Source reference: docs/GATE-3-CHECKLIST.md row 3.2
- Description: A guardrail entry that names a file or a path where a test is required is refused, and lesson validation and guardrail effectiveness resolve an entry through one function.
- Implementation: `file:scripts/development-ledger/lessons.py`
- Test: `test:GuardrailRegistryResolutionTests`, `test:test_validation_and_effectiveness_agree`, `test:test_one_function_resolves_a_guardrail_entry`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0016 - canonical:GATE-3#3.3

- Source reference: docs/GATE-3-CHECKLIST.md row 3.3
- Description: The committed lesson index is the render of the memory, and a memory changed without re-rendering it, or an index edited by hand, is refused under the memory policy that introduced the rule.
- Implementation: `file:scripts/development-ledger/lessons.py`, `file:.iacode/memory/POLICY.json`
- Test: `test:LessonIndexFreshnessTests`, `test:test_a_memory_changed_without_rerendering_is_refused`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0017 - canonical:GATE-3#3.4

- Source reference: docs/GATE-3-CHECKLIST.md row 3.4
- Description: The event stream of a run that is already terminal delivers every event after the cursor, however many pages that takes, before it closes.
- Implementation: `file:apps/api/src/iacode_api/routes/agent_runs.py`
- Test: `test:test_a_terminal_stream_drains_every_page_after_the_cursor`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0018 - canonical:GATE-3#3.5

- Source reference: docs/GATE-3-CHECKLIST.md row 3.5
- Description: A canonical ADR index exists, lists every record with its title and status, resolves every link, and its test asserts rather than skips.
- Implementation: _none_
- Test: `test:AdrIndexTests`, `test:test_the_index_lists_every_record_with_its_title_and_status`
- Negative test: _none_
- Documentation: `file:docs/adr/README.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0019 - canonical:GATE-3#4.1

- Source reference: docs/GATE-3-CHECKLIST.md row 4.1
- Description: The sandbox is its own service in the directory the scope registry reserved for it, with its own contracts, and the decision is recorded.
- Implementation: _none_
- Test: `test:SandboxBoundaryTests`
- Negative test: _none_
- Documentation: `file:docs/adr/ADR-0025-sandbox-isolation-boundary.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0020 - canonical:GATE-3#4.2

- Source reference: docs/GATE-3-CHECKLIST.md row 4.2
- Description: No sandbox logic lives in the API routes, the Agent Runtime or the Model Gateway: none of them imports the sandbox package or a container client.
- Implementation: _none_
- Test: `test:SandboxBoundaryTests`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0021 - canonical:GATE-3#4.3

- Source reference: docs/GATE-3-CHECKLIST.md row 4.3
- Description: The Agent Runtime and the workflow that drives it still execute nothing themselves; a tool reaches the sandbox only as an activity on the sandbox's own task queue.
- Implementation: _none_
- Test: `test:RepositoryToolExecutionBoundaryTests`, `test:ToolExecutionBoundaryTests`, `test:WorkflowSandboxDispatchTests`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0022 - canonical:GATE-3#4.4

- Source reference: docs/GATE-3-CHECKLIST.md row 4.4
- Description: Inside the sandbox service only the engine backend and the in-container helper start a process, and the controller never uses a shell.
- Implementation: `file:services/sandbox/src/iacode_sandbox/backend.py`, `file:services/sandbox/src/iacode_sandbox/helper.py`
- Test: `test:test_only_the_backend_and_the_helper_start_processes`, `test:test_no_module_of_the_controller_uses_a_shell`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0023 - canonical:GATE-3#4.5

- Source reference: docs/GATE-3-CHECKLIST.md row 4.5
- Description: The controller starts only the container client, with an argument vector, and never a command a request supplied.
- Implementation: `file:services/sandbox/src/iacode_sandbox/backend.py`
- Test: `test:test_the_backend_starts_only_the_container_client`, `test:test_the_image_decides_the_command_not_the_request`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0024 - canonical:GATE-3#4.6

- Source reference: docs/GATE-3-CHECKLIST.md row 4.6
- Description: The controller is the only service given the container engine, and it holds no capability, cannot gain one, and publishes no port.
- Implementation: `file:infra/compose/docker-compose.yml`
- Test: `test:test_only_the_sandbox_service_is_given_the_engine_socket`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0025 - canonical:GATE-3#5.1

- Source reference: docs/GATE-3-CHECKLIST.md row 5.1
- Description: Versioned contracts exist for the sandbox session, the policy, the workspace, the execution request, the execution result, the command execution, the file operation, the Git operation and the artifact reference.
- Implementation: `file:services/sandbox/src/iacode_sandbox/contracts.py`, `file:services/sandbox/src/iacode_sandbox/policy.py`, `file:packages/contracts/src/iacode_contracts/sandbox.py`
- Test: `test:SandboxContractTests`, `test:test_the_contract_is_versioned`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0026 - canonical:GATE-3#5.2

- Source reference: docs/GATE-3-CHECKLIST.md row 5.2
- Description: A contract of another version is refused rather than interpreted, and a request carrying a field the contract does not declare or missing one it requires is refused.
- Implementation: `file:services/sandbox/src/iacode_sandbox/contracts.py`
- Test: `test:test_another_version_is_refused_rather_than_interpreted`, `test:test_a_request_cannot_carry_a_field_the_contract_does_not_declare`, `test:test_a_missing_required_field_is_refused`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0027 - canonical:GATE-3#5.3

- Source reference: docs/GATE-3-CHECKLIST.md row 5.3
- Description: A command result carries the exit code, standard output, standard error, duration, whether it timed out, whether it was truncated and its artifact references, and no exit code is invented for a command that never started.
- Implementation: `file:services/sandbox/src/iacode_sandbox/contracts.py`
- Test: `test:test_no_exit_code_is_invented_for_a_command_that_never_started`, `test:test_the_result_round_trips_with_its_artifacts`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0028 - canonical:GATE-3#5.4

- Source reference: docs/GATE-3-CHECKLIST.md row 5.4
- Description: The execution status, session state, workspace and operation vocabularies are closed, and the database accepts exactly the declared ones.
- Implementation: `file:packages/contracts/src/iacode_contracts/sandbox.py`
- Test: `test:test_the_status_vocabulary_is_closed`, `test:test_the_session_workspace_and_operations_have_closed_vocabularies`, `test:test_the_session_state_vocabulary_the_database_accepts_is_the_declared_one`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0029 - canonical:GATE-3#5.5

- Source reference: docs/GATE-3-CHECKLIST.md row 5.5
- Description: The result an agent receives cannot present a cancellation, a denial or a timeout as a success.
- Implementation: `file:services/sandbox/src/iacode_sandbox/contracts.py`
- Test: `test:test_the_agent_sees_a_cancellation_as_a_failure_it_cannot_misread`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0030 - canonical:GATE-3#6.1

- Source reference: docs/GATE-3-CHECKLIST.md row 6.1
- Description: An explicit registry names every executable tool — list, read, write, patch and search of files, shell execution, and the local Git status, diff, log, show, add and commit — and only a registered name can execute.
- Implementation: `file:services/sandbox/src/iacode_sandbox/tools.py`
- Test: `test:ToolRegistryTests`, `test:test_the_registry_is_exactly_the_specified_set`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0031 - canonical:GATE-3#6.2

- Source reference: docs/GATE-3-CHECKLIST.md row 6.2
- Description: An unknown tool name is refused, and no name is ever mapped to a shell.
- Implementation: `file:services/sandbox/src/iacode_sandbox/tools.py`, `file:services/sandbox/src/iacode_sandbox/service.py`
- Test: `test:test_an_unknown_tool_is_refused_and_never_mapped_to_a_shell`, `test:test_an_unknown_tool_is_denied_and_nothing_is_started`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0032 - canonical:GATE-3#6.3

- Source reference: docs/GATE-3-CHECKLIST.md row 6.3
- Description: A canonical sandbox tool policy defines, per policy, the allowed tools, the resource profile, the network profile, the workspace permissions, the command timeout and the output limits.
- Implementation: `file:.iacode/policies/sandbox-policy.json`, `file:services/sandbox/src/iacode_sandbox/policy.py`
- Test: `test:SandboxPolicyTests`, `test:test_the_canonical_policy_loads`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0033 - canonical:GATE-3#6.4

- Source reference: docs/GATE-3-CHECKLIST.md row 6.4
- Description: A tool the run's policy does not allow is refused, a policy naming an unregistered tool is refused, and an unknown policy is refused.
- Implementation: `file:services/sandbox/src/iacode_sandbox/policy.py`, `file:services/sandbox/src/iacode_sandbox/service.py`
- Test: `test:test_a_tool_outside_the_policy_is_refused`, `test:test_a_policy_naming_an_unregistered_tool_is_refused`, `test:test_an_unknown_policy_is_denied`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0034 - canonical:GATE-3#6.5

- Source reference: docs/GATE-3-CHECKLIST.md row 6.5
- Description: Tool arguments are structured and typed: an undeclared argument is refused, and a wrong type, an absent value and a wrong value each carry their own reason.
- Implementation: `file:services/sandbox/src/iacode_sandbox/tools.py`
- Test: `test:test_an_argument_a_tool_does_not_declare_is_refused`, `test:test_a_wrong_type_is_refused_with_its_own_reason`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0035 - canonical:GATE-3#6.6

- Source reference: docs/GATE-3-CHECKLIST.md row 6.6
- Description: No request can change its policy, its limits, its network or its mounts; a request that tries is denied, and a request may lower a timeout but never raise it.
- Implementation: `file:services/sandbox/src/iacode_sandbox/service.py`, `file:services/sandbox/src/iacode_sandbox/tools.py`
- Test: `test:test_a_request_that_tries_to_set_a_limit_is_denied`, `test:test_no_request_can_change_the_network_the_limits_or_the_mounts`, `test:test_a_request_may_lower_a_timeout_and_never_raise_it`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0036 - canonical:GATE-3#6.7

- Source reference: docs/GATE-3-CHECKLIST.md row 6.7
- Description: The limits a tool runs under come from the policy, and every limit a policy applies is inside its declared bound.
- Implementation: `file:services/sandbox/src/iacode_sandbox/tools.py`, `file:services/sandbox/src/iacode_sandbox/policy.py`
- Test: `test:test_the_limits_come_from_the_policy`, `test:test_every_limit_the_policy_applies_is_inside_its_bound`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0037 - canonical:GATE-3#6.8

- Source reference: docs/GATE-3-CHECKLIST.md row 6.8
- Description: A policy document with an unknown key, or a read-only policy that allows a writing tool, is refused when it is loaded.
- Implementation: `file:services/sandbox/src/iacode_sandbox/policy.py`
- Test: `test:test_an_unknown_key_is_refused`, `test:test_a_read_only_policy_that_allows_a_writer_is_refused`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0038 - canonical:GATE-3#6.9

- Source reference: docs/GATE-3-CHECKLIST.md row 6.9
- Description: Tools the policy allows execute automatically, inside the sandbox, without a confirmation per call; nothing is executed on the host under any policy.
- Implementation: `file:services/orchestrator/src/iacode_orchestrator/workflows/agent_run.py`
- Test: `test:WorkflowSandboxDispatchTests`
- Negative test: _none_
- Documentation: `file:docs/adr/ADR-0027-tool-execution-policy.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0039 - canonical:GATE-3#7.1

- Source reference: docs/GATE-3-CHECKLIST.md row 7.1
- Description: Every run executes in its own disposable container with its own workspace; two runs never share either.
- Implementation: `file:services/sandbox/src/iacode_sandbox/service.py`, `file:services/sandbox/src/iacode_sandbox/backend.py`
- Test: `test:test_two_runs_have_two_containers_and_two_workspaces`, `test:test_one_run_gets_one_session_and_two_runs_get_two`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0040 - canonical:GATE-3#7.2

- Source reference: docs/GATE-3-CHECKLIST.md row 7.2
- Description: The sandbox runs unprivileged, as a non-root user, with every capability dropped and no way to gain privileges.
- Implementation: `file:services/sandbox/src/iacode_sandbox/backend.py`, `file:services/sandbox/images/iacode-dev/Dockerfile`
- Test: `test:test_the_sandbox_runs_unprivileged_with_no_capability`, `test:test_every_isolation_flag_is_emitted`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0041 - canonical:GATE-3#7.3

- Source reference: docs/GATE-3-CHECKLIST.md row 7.3
- Description: The root filesystem is read-only, and the only writable places are the workspace and a temporary directory, both in-memory filesystems with a size limit.
- Implementation: `file:services/sandbox/src/iacode_sandbox/backend.py`
- Test: `test:test_the_root_filesystem_is_read_only`, `test:test_the_writable_places_are_bounded_in_memory_filesystems`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0042 - canonical:GATE-3#7.4

- Source reference: docs/GATE-3-CHECKLIST.md row 7.4
- Description: The container engine's socket, and any other engine endpoint, is absent from a sandbox.
- Implementation: `file:services/sandbox/src/iacode_sandbox/backend.py`
- Test: `test:test_no_docker_socket_or_engine_endpoint_is_reachable`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0043 - canonical:GATE-3#7.5

- Source reference: docs/GATE-3-CHECKLIST.md row 7.5
- Description: No host path is mounted into a sandbox — no drive, no root, no home, no profile, no SSH directory, no credential store, no secret environment file — and no argument of a request can add one.
- Implementation: `file:services/sandbox/src/iacode_sandbox/backend.py`
- Test: `test:test_no_host_path_is_mounted`, `test:test_no_privilege_and_no_host_resource_can_be_granted`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0044 - canonical:GATE-3#7.6

- Source reference: docs/GATE-3-CHECKLIST.md row 7.6
- Description: Every sandbox container carries labels naming the service instance that owns it, the session, the run, the policy and its expiry, so ownership is read from the engine rather than from memory.
- Implementation: `file:services/sandbox/src/iacode_sandbox/backend.py`
- Test: `test:test_every_container_carries_the_ownership_labels`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0045 - canonical:GATE-3#8.1

- Source reference: docs/GATE-3-CHECKLIST.md row 8.1
- Description: CPU, memory, process count, workspace size, execution timeout and output size are mandatory, configurable limits, and a zero, negative, absurd or missing value is refused.
- Implementation: `file:.iacode/policies/sandbox-policy.json`, `file:services/sandbox/src/iacode_sandbox/policy.py`
- Test: `test:ResourceLimitValidationTests`, `test:test_zero_negative_and_absurd_values_are_refused`, `test:test_a_missing_limit_is_refused`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0046 - canonical:GATE-3#8.2

- Source reference: docs/GATE-3-CHECKLIST.md row 8.2
- Description: The memory limit holds the in-memory filesystems, so a full workspace cannot starve the processes of the limit they were promised.
- Implementation: `file:services/sandbox/src/iacode_sandbox/policy.py`
- Test: `test:test_memory_must_hold_the_in_memory_filesystems`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0047 - canonical:GATE-3#8.3

- Source reference: docs/GATE-3-CHECKLIST.md row 8.3
- Description: A process that multiplies without end is contained by the process limit, and the sandbox remains usable afterwards.
- Implementation: `file:services/sandbox/src/iacode_sandbox/backend.py`
- Test: `test:test_a_fork_bomb_is_contained_by_the_process_limit`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0048 - canonical:GATE-3#8.4

- Source reference: docs/GATE-3-CHECKLIST.md row 8.4
- Description: A process that exceeds the memory limit fails in a controlled way, and the host is unaffected.
- Implementation: `file:services/sandbox/src/iacode_sandbox/backend.py`
- Test: `test:test_a_process_that_exceeds_memory_fails_in_a_controlled_way`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0049 - canonical:GATE-3#8.5

- Source reference: docs/GATE-3-CHECKLIST.md row 8.5
- Description: The workspace cannot outgrow its limit.
- Implementation: `file:services/sandbox/src/iacode_sandbox/backend.py`
- Test: `test:test_the_workspace_cannot_outgrow_its_limit`, `test:test_the_workspace_is_bounded`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0050 - canonical:GATE-3#8.6

- Source reference: docs/GATE-3-CHECKLIST.md row 8.6
- Description: A command that exceeds its timeout is ended together with every process it started, including a process that left its session, and nothing is left running.
- Implementation: `file:services/sandbox/src/iacode_sandbox/helper.py`
- Test: `test:test_a_timeout_kills_the_whole_process_tree`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0051 - canonical:GATE-3#8.7

- Source reference: docs/GATE-3-CHECKLIST.md row 8.7
- Description: Standard output and standard error are bounded while they are read; what exceeds the bound is truncated explicitly and stored whole as an artifact, and memory is never unbounded.
- Implementation: `file:services/sandbox/src/iacode_sandbox/helper.py`, `file:services/sandbox/src/iacode_sandbox/artifacts.py`
- Test: `test:test_output_is_bounded_and_the_rest_is_an_artifact`, `test:test_truncated_output_goes_to_the_artifact_store`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0052 - canonical:GATE-3#9.1

- Source reference: docs/GATE-3-CHECKLIST.md row 9.1
- Description: A sandbox has no network by default: only loopback exists, and every policy the Gate ships denies the network.
- Implementation: `file:services/sandbox/src/iacode_sandbox/backend.py`, `file:.iacode/policies/sandbox-policy.json`
- Test: `test:test_the_default_network_has_only_loopback`, `test:test_every_policy_denies_network_by_default`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0053 - canonical:GATE-3#9.2

- Source reference: docs/GATE-3-CHECKLIST.md row 9.2
- Description: An attempt to reach an external address from a sandbox without network fails.
- Implementation: `file:services/sandbox/src/iacode_sandbox/backend.py`
- Test: `test:test_external_egress_fails`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0054 - canonical:GATE-3#9.3

- Source reference: docs/GATE-3-CHECKLIST.md row 9.3
- Description: The one other network profile is local services only, on an internal network with no route outside, and it is chosen by the policy, never by a request.
- Implementation: `file:services/sandbox/src/iacode_sandbox/backend.py`, `file:services/sandbox/src/iacode_sandbox/policy.py`
- Test: `test:test_a_local_services_network_is_internal`, `test:test_no_request_can_change_the_network_the_limits_or_the_mounts`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0055 - canonical:GATE-3#9.4

- Source reference: docs/GATE-3-CHECKLIST.md row 9.4
- Description: No package installation from the internet is offered; the image carries the toolchain the Gate's tests need.
- Implementation: `file:services/sandbox/images/iacode-dev/Dockerfile`
- Test: `test:SandboxImageProfileTests`
- Negative test: _none_
- Documentation: `file:docs/runbooks/SANDBOX.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0056 - canonical:GATE-3#10.1

- Source reference: docs/GATE-3-CHECKLIST.md row 10.1
- Description: A sandbox receives only the variables its policy explicitly allows, and no variable of the controller — provider key, repository token, agent socket, cloud credential or engine address — reaches it.
- Implementation: `file:services/sandbox/src/iacode_sandbox/backend.py`, `file:services/sandbox/src/iacode_sandbox/tools.py`
- Test: `test:test_no_variable_of_the_controller_reaches_a_sandbox`, `test:test_the_command_environment_is_an_allowlist`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0057 - canonical:GATE-3#10.2

- Source reference: docs/GATE-3-CHECKLIST.md row 10.2
- Description: A command's environment inside the sandbox is the allowlist and nothing else.
- Implementation: `file:services/sandbox/src/iacode_sandbox/helper.py`
- Test: `test:test_the_environment_is_the_allowlist_and_nothing_else`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0058 - canonical:GATE-3#10.3

- Source reference: docs/GATE-3-CHECKLIST.md row 10.3
- Description: A policy cannot allow a credential-shaped variable into a command's environment.
- Implementation: `file:services/sandbox/src/iacode_sandbox/policy.py`
- Test: `test:test_a_credential_cannot_be_allowed_into_a_command_environment`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0059 - canonical:GATE-3#10.4

- Source reference: docs/GATE-3-CHECKLIST.md row 10.4
- Description: No Git credential, credential helper, SSH key or agent socket exists in a sandbox.
- Implementation: `file:services/sandbox/images/iacode-dev/gitconfig`, `file:services/sandbox/src/iacode_sandbox/backend.py`
- Test: `test:test_no_git_or_ssh_credential_exists`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0060 - canonical:GATE-3#11.1

- Source reference: docs/GATE-3-CHECKLIST.md row 11.1
- Description: A workspace has an identity and an explicit lifecycle, belongs to exactly one run, and a run holds at most one active session.
- Implementation: `file:services/sandbox/src/iacode_sandbox/service.py`, `file:packages/persistence/src/iacode_persistence/models.py`
- Test: `test:test_one_run_gets_one_session_and_two_runs_get_two`, `test:SandboxMigrationTests`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0061 - canonical:GATE-3#11.2

- Source reference: docs/GATE-3-CHECKLIST.md row 11.2
- Description: A workspace is provisioned only from an authorised snapshot, named by its artifact identifier and never by a path, and becomes a repository the tools can work on.
- Implementation: `file:services/sandbox/src/iacode_sandbox/snapshots.py`, `file:services/agent-runtime/src/iacode_agent_runtime/service.py`
- Test: `test:test_a_snapshot_provisions_the_workspace_as_a_repository`, `test:test_a_coding_run_names_an_authorised_snapshot`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0062 - canonical:GATE-3#11.3

- Source reference: docs/GATE-3-CHECKLIST.md row 11.3
- Description: Anything but a workspace snapshot artifact is refused before the run exists, and a snapshot for a team that executes no tool is refused.
- Implementation: `file:services/agent-runtime/src/iacode_agent_runtime/service.py`
- Test: `test:test_anything_but_a_snapshot_artifact_is_refused`, `test:test_a_snapshot_for_a_team_without_tools_is_refused`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0063 - canonical:GATE-3#11.4

- Source reference: docs/GATE-3-CHECKLIST.md row 11.4
- Description: A snapshot whose digest differs from its record, or that carries a link or an escaping member, is refused, and no session survives the refusal.
- Implementation: `file:services/sandbox/src/iacode_sandbox/snapshots.py`
- Test: `test:test_a_snapshot_with_a_different_digest_is_refused`, `test:test_an_unsafe_snapshot_is_refused_and_no_session_survives`, `test:test_the_snapshot_builder_refuses_a_link`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0064 - canonical:GATE-3#11.5

- Source reference: docs/GATE-3-CHECKLIST.md row 11.5
- Description: One run cannot read or write another run's files, nor see its processes.
- Implementation: `file:services/sandbox/src/iacode_sandbox/backend.py`
- Test: `test:CrossSessionIsolationTests`, `test:test_one_run_cannot_see_another_runs_files`, `test:test_one_run_cannot_see_another_runs_processes`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0065 - canonical:GATE-3#11.6

- Source reference: docs/GATE-3-CHECKLIST.md row 11.6
- Description: The development working tree of this repository is never an agent's workspace.
- Implementation: `file:services/sandbox/src/iacode_sandbox/snapshots.py`
- Test: `test:SandboxScenarioTests`
- Negative test: _none_
- Documentation: `file:docs/adr/ADR-0026-workspace-lifecycle.md`
- Validation: `command:cmd-0071`
- Guardrail: _none_

### REQ-0066 - canonical:GATE-3#12.1

- Source reference: docs/GATE-3-CHECKLIST.md row 12.1
- Description: One canonical path resolver decides every path a tool touches; no other module re-implements path safety.
- Implementation: `file:services/sandbox/src/iacode_sandbox/paths.py`
- Test: `test:SinglePathResolverTests`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0067 - canonical:GATE-3#12.2

- Source reference: docs/GATE-3-CHECKLIST.md row 12.2
- Description: Traversal, absolute paths, drive letters, UNC paths, null bytes and normalisation tricks are refused, each with its own reason.
- Implementation: `file:services/sandbox/src/iacode_sandbox/paths.py`
- Test: `test:PathResolverTests`, `test:test_every_hostile_spelling_is_refused_with_its_own_code`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0068 - canonical:GATE-3#12.3

- Source reference: docs/GATE-3-CHECKLIST.md row 12.3
- Description: A link inside the workspace that points outside it cannot be read or written through, whether it names a file, a directory, the root or climbs out relatively; a link that stays inside is followed.
- Implementation: `file:services/sandbox/src/iacode_sandbox/paths.py`
- Test: `test:SymlinkContainmentTests`, `test:test_a_symlink_that_points_outside_cannot_be_read_or_written_through`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0069 - canonical:GATE-3#12.4

- Source reference: docs/GATE-3-CHECKLIST.md row 12.4
- Description: Listing, reading, writing, searching and patching work inside the workspace of a real sandbox.
- Implementation: `file:services/sandbox/src/iacode_sandbox/helper.py`
- Test: `test:test_write_read_list_search_and_patch`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0070 - canonical:GATE-3#12.5

- Source reference: docs/GATE-3-CHECKLIST.md row 12.5
- Description: A read and a write are bounded in size, an oversized one is refused, and binary content is refused as text rather than mangled.
- Implementation: `file:services/sandbox/src/iacode_sandbox/helper.py`
- Test: `test:test_oversized_reads_and_writes_are_refused`, `test:test_binary_content_is_refused_as_text`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0071 - canonical:GATE-3#12.6

- Source reference: docs/GATE-3-CHECKLIST.md row 12.6
- Description: A write validates its parent directory and replaces the file atomically.
- Implementation: `file:services/sandbox/src/iacode_sandbox/helper.py`
- Test: `test:FilesystemToolTests`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0072 - canonical:GATE-3#12.7

- Source reference: docs/GATE-3-CHECKLIST.md row 12.7
- Description: A patch applies only inside the workspace; a patch whose context does not match, or that has one bad file, changes nothing.
- Implementation: `file:services/sandbox/src/iacode_sandbox/patching.py`
- Test: `test:PatchApplyTests`, `test:test_a_failing_patch_changes_nothing`, `test:test_a_multi_file_patch_with_one_bad_file_writes_no_file`, `test:test_a_patch_cannot_reach_outside_the_workspace`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0073 - canonical:GATE-3#12.8

- Source reference: docs/GATE-3-CHECKLIST.md row 12.8
- Description: A search is confined to the workspace and bounded in results, output and duration.
- Implementation: `file:services/sandbox/src/iacode_sandbox/helper.py`, `file:services/sandbox/src/iacode_sandbox/tools.py`
- Test: `test:test_write_read_list_search_and_patch`, `test:test_the_limits_come_from_the_policy`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0074 - canonical:GATE-3#12.9

- Source reference: docs/GATE-3-CHECKLIST.md row 12.9
- Description: A path refused inside the sandbox reaches the agent as a denial, not as a failure of the sandbox.
- Implementation: `file:services/sandbox/src/iacode_sandbox/service.py`
- Test: `test:test_a_path_refusal_from_inside_the_sandbox_is_a_denial`, `test:test_traversal_and_absolute_escapes_are_denied`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0075 - canonical:GATE-3#13.1

- Source reference: docs/GATE-3-CHECKLIST.md row 13.1
- Description: Shell execution runs only inside the sandbox container, with the command, the working directory, the allowed environment and the timeout passed as structured arguments.
- Implementation: `file:services/sandbox/src/iacode_sandbox/tools.py`, `file:services/sandbox/src/iacode_sandbox/helper.py`
- Test: `test:ShellToolTests`, `test:test_a_hostile_path_is_refused_before_the_helper`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0076 - canonical:GATE-3#13.2

- Source reference: docs/GATE-3-CHECKLIST.md row 13.2
- Description: Standard output, standard error, a zero and a non-zero exit code, a missing executable and a child process are all reported faithfully.
- Implementation: `file:services/sandbox/src/iacode_sandbox/helper.py`
- Test: `test:test_echo_stdout_stderr_and_exit_codes`, `test:test_a_missing_executable_is_a_failure_with_its_exit_code`, `test:test_a_child_process_runs_and_reports`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0077 - canonical:GATE-3#13.3

- Source reference: docs/GATE-3-CHECKLIST.md row 13.3
- Description: The working directory resolves inside the workspace, and an escaping one is refused.
- Implementation: `file:services/sandbox/src/iacode_sandbox/paths.py`
- Test: `test:test_the_working_directory_is_resolved_inside_the_workspace`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0078 - canonical:GATE-3#13.4

- Source reference: docs/GATE-3-CHECKLIST.md row 13.4
- Description: A payload that tries to reach a host command affects only the sandbox, inside its policy, and the host is unchanged.
- Implementation: `file:services/sandbox/src/iacode_sandbox/helper.py`
- Test: `test:test_an_injected_host_command_only_reaches_the_sandbox`, `test:SandboxScenarioTests`
- Negative test: _none_
- Documentation: _none_
- Validation: `command:cmd-0071`
- Guardrail: _none_

### REQ-0079 - canonical:GATE-3#13.5

- Source reference: docs/GATE-3-CHECKLIST.md row 13.5
- Description: A command still running when its run is cancelled is stopped, with every process it started.
- Implementation: `file:services/sandbox/src/iacode_sandbox/service.py`, `file:services/sandbox/src/iacode_sandbox/helper.py`
- Test: `test:test_a_cancelled_run_stops_its_command_and_leaves_nothing_running`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0080 - canonical:GATE-3#14.1

- Source reference: docs/GATE-3-CHECKLIST.md row 14.1
- Description: Inside the workspace an agent can read the status, the working and the staged diff, the log and a commit, stage files and commit locally.
- Implementation: `file:services/sandbox/src/iacode_sandbox/tools.py`, `file:services/sandbox/src/iacode_sandbox/helper.py`
- Test: `test:GitToolTests`, `test:test_status_diff_add_commit_log_and_show`, `test:test_the_staged_diff_is_asked_for_explicitly`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0081 - canonical:GATE-3#14.2

- Source reference: docs/GATE-3-CHECKLIST.md row 14.2
- Description: Every Git tool builds a fixed argument vector, a revision that looks like an option is refused, and a commit skips hooks and carries its message as one argument.
- Implementation: `file:services/sandbox/src/iacode_sandbox/tools.py`
- Test: `test:GitOperationTests`, `test:test_every_git_tool_builds_a_fixed_argument_vector`, `test:test_a_revision_that_looks_like_an_option_is_refused`, `test:test_a_commit_skips_hooks_and_carries_the_message_as_one_argument`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0082 - canonical:GATE-3#14.3

- Source reference: docs/GATE-3-CHECKLIST.md row 14.3
- Description: No remote Git operation is offered or possible — no push, fetch, clone or remote — and no destructive operation — hard reset, clean, rebase, history filtering, forced push — is offered by default.
- Implementation: `file:services/sandbox/src/iacode_sandbox/tools.py`, `file:.iacode/policies/sandbox-policy.json`
- Test: `test:test_no_remote_or_destructive_git_verb_exists`, `test:test_no_remote_operation_is_offered_or_possible`, `test:test_no_policy_offers_a_remote_git_operation`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0083 - canonical:GATE-3#14.4

- Source reference: docs/GATE-3-CHECKLIST.md row 14.4
- Description: An agent's commits carry an explicit sandbox identity that is not a person, separate from the owner's development identity, and the difference is documented.
- Implementation: `file:services/sandbox/images/iacode-dev/gitconfig`
- Test: `test:test_the_sandbox_git_identity_is_not_a_person`, `test:Gate3DocumentationTests`
- Negative test: _none_
- Documentation: `file:docs/runbooks/SANDBOX.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0084 - canonical:GATE-3#14.5

- Source reference: docs/GATE-3-CHECKLIST.md row 14.5
- Description: Git output is bounded like any other output.
- Implementation: `file:services/sandbox/src/iacode_sandbox/helper.py`
- Test: `test:test_git_output_is_bounded`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0085 - canonical:GATE-3#15.1

- Source reference: docs/GATE-3-CHECKLIST.md row 15.1
- Description: A session moves through explicit states, is created ready for its run and is removed with it.
- Implementation: `file:services/sandbox/src/iacode_sandbox/service.py`, `file:packages/contracts/src/iacode_contracts/sandbox.py`
- Test: `test:SessionLifecycleTests`, `test:test_a_session_is_created_ready_and_removed_with_its_run`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0086 - canonical:GATE-3#15.2

- Source reference: docs/GATE-3-CHECKLIST.md row 15.2
- Description: A running tool holds its session in the running state, and inspecting a session reports the store and the engine side by side.
- Implementation: `file:services/sandbox/src/iacode_sandbox/service.py`
- Test: `test:test_a_running_tool_holds_the_session_in_running`, `test:test_inspect_reports_the_store_and_the_engine`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0087 - canonical:GATE-3#15.3

- Source reference: docs/GATE-3-CHECKLIST.md row 15.3
- Description: When a run ends or is cancelled its sandbox is removed, and no container or temporary volume is left behind.
- Implementation: `file:services/sandbox/src/iacode_sandbox/service.py`, `file:services/orchestrator/src/iacode_orchestrator/workflows/agent_run.py`
- Test: `test:test_releasing_a_run_removes_its_container`, `test:WorkflowSandboxDispatchTests`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0088 - canonical:GATE-3#15.4

- Source reference: docs/GATE-3-CHECKLIST.md row 15.4
- Description: A restarted service reconciles from the store and the engine rather than from memory: it keeps a live session, removes a container no session owns, and fails a session whose container vanished.
- Implementation: `file:services/sandbox/src/iacode_sandbox/service.py`
- Test: `test:RecoveryTests`, `test:SessionRecoveryTests`, `test:test_a_restarted_service_keeps_a_live_session_and_removes_an_orphan`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0089 - canonical:GATE-3#15.5

- Source reference: docs/GATE-3-CHECKLIST.md row 15.5
- Description: Reconciliation touches only containers this service instance owns, so another stack or a test on the same engine is never cleaned up by it.
- Implementation: `file:services/sandbox/src/iacode_sandbox/backend.py`, `file:services/sandbox/src/iacode_sandbox/service.py`
- Test: `test:test_a_restarted_service_keeps_a_live_session_and_removes_an_orphan`, `test:test_every_container_carries_the_ownership_labels`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0090 - canonical:GATE-3#15.6

- Source reference: docs/GATE-3-CHECKLIST.md row 15.6
- Description: An orphan sweeper expires only sessions that have expired and are not running, in bounded, deterministic batches, and never removes an active workspace.
- Implementation: `file:services/sandbox/src/iacode_sandbox/service.py`
- Test: `test:test_the_sweeper_expires_only_what_has_expired_and_is_not_running`, `test:test_the_sweeper_is_bounded`, `test:test_nothing_unexpired_is_swept`, `test:test_an_expired_session_is_swept_and_its_container_removed`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0091 - canonical:GATE-3#16.1

- Source reference: docs/GATE-3-CHECKLIST.md row 16.1
- Description: This Gate adds its schema through a new migration and edits no migration that has already been applied.
- Implementation: `file:apps/api/migrations/versions/0004_sandbox.py`
- Test: `test:test_applied_migrations_are_not_edited`, `test:SandboxMigrationTests`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0092 - canonical:GATE-3#16.2

- Source reference: docs/GATE-3-CHECKLIST.md row 16.2
- Description: The existing tool call, artifact and run entities are evolved rather than duplicated, and the one new table holds only what nothing else could: the sandbox session.
- Implementation: `file:packages/persistence/src/iacode_persistence/models.py`
- Test: `test:test_the_agent_runtime_created_no_parallel_entity`, `test:test_structural_tables_exist`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0093 - canonical:GATE-3#16.3

- Source reference: docs/GATE-3-CHECKLIST.md row 16.3
- Description: A database created from nothing reaches the head revision, and a database at the previous Gate's head upgrades without losing a row.
- Implementation: `file:apps/api/migrations/versions/0004_sandbox.py`
- Test: `test:test_fresh_database_reaches_the_sandbox_head`, `test:test_gate2_database_upgrades_to_gate3_head`, `test:test_the_sandbox_migration_is_reversible`
- Negative test: _none_
- Documentation: _none_
- Validation: `command:cmd-0105`, `checkpoint:VERIFICATION-REPORT.json`
- Guardrail: _none_

### REQ-0094 - canonical:GATE-3#16.4

- Source reference: docs/GATE-3-CHECKLIST.md row 16.4
- Description: Every execution is traceable from the task through the run, the agent run, the tool request, the sandbox session and the execution to the result, and none of it holds private reasoning.
- Implementation: `file:packages/persistence/src/iacode_persistence/models.py`
- Test: `test:test_relationships_cascade_deliberately`, `test:test_the_detail_shows_what_the_sandbox_executed_and_not_its_output`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0095 - canonical:GATE-3#16.5

- Source reference: docs/GATE-3-CHECKLIST.md row 16.5
- Description: A retried request never executes twice: the execution is keyed by the tool request it answers.
- Implementation: `file:services/sandbox/src/iacode_sandbox/store.py`, `file:services/sandbox/src/iacode_sandbox/service.py`
- Test: `test:test_an_execution_is_never_repeated_for_a_retried_request`, `test:SqlSandboxStoreTests`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0096 - canonical:GATE-3#16.6

- Source reference: docs/GATE-3-CHECKLIST.md row 16.6
- Description: The store the service runs against in the stack records sessions and executions in the real database with the same behaviour the suite asserts in memory.
- Implementation: `file:services/sandbox/src/iacode_sandbox/store.py`
- Test: `test:SqlSandboxStoreTests`
- Negative test: _none_
- Documentation: _none_
- Validation: `command:cmd-0105`, `command:cmd-0100`, `checkpoint:VERIFICATION-REPORT.json`
- Guardrail: _none_

### REQ-0097 - canonical:GATE-3#16.7

- Source reference: docs/GATE-3-CHECKLIST.md row 16.7
- Description: Nothing this Gate persists is training-eligible, and no table stores a credential.
- Implementation: `file:packages/persistence/src/iacode_persistence/models.py`
- Test: `test:test_rights_default_to_denial`, `test:test_no_table_stores_a_credential`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0098 - canonical:GATE-3#17.1

- Source reference: docs/GATE-3-CHECKLIST.md row 17.1
- Description: A pending tool request of a stage with a sandbox policy is checked against the policy, executed in the run's sandbox, its result persisted, and the workflow resumes.
- Implementation: `file:services/orchestrator/src/iacode_orchestrator/workflows/agent_run.py`, `file:services/orchestrator/src/iacode_orchestrator/agent_runtime/activities.py`
- Test: `test:WorkflowSandboxDispatchTests`
- Negative test: _none_
- Documentation: _none_
- Validation: `command:cmd-0071`
- Guardrail: _none_

### REQ-0099 - canonical:GATE-3#17.2

- Source reference: docs/GATE-3-CHECKLIST.md row 17.2
- Description: A stage without a sandbox policy keeps the previous Gate's behaviour: the request waits for a result delivered through the API.
- Implementation: `file:services/orchestrator/src/iacode_orchestrator/workflows/agent_run.py`
- Test: `test:WorkflowSandboxDispatchTests`, `test:test_tool_request_pauses_the_run`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0100 - canonical:GATE-3#17.3

- Source reference: docs/GATE-3-CHECKLIST.md row 17.3
- Description: The run plan names the sandbox policy of each stage and the workspace source, frozen when the run is created.
- Implementation: `file:services/agent-runtime/src/iacode_agent_runtime/contracts.py`
- Test: `test:SandboxPlanContractTests`, `test:test_the_sandbox_policy_and_the_workspace_round_trip`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0101 - canonical:GATE-3#17.4

- Source reference: docs/GATE-3-CHECKLIST.md row 17.4
- Description: A tool result returns to the agent as labelled data in its own channel and never as an instruction.
- Implementation: `file:services/agent-runtime/src/iacode_agent_runtime/context.py`
- Test: `test:InstructionHierarchyTests`, `test:test_each_source_lands_in_its_own_channel`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0102 - canonical:GATE-3#17.5

- Source reference: docs/GATE-3-CHECKLIST.md row 17.5
- Description: A large result reaches the model truncated inline with an artifact reference, within the size the runtime accepts for a tool result.
- Implementation: `file:services/sandbox/src/iacode_sandbox/contracts.py`
- Test: `test:test_truncated_output_goes_to_the_artifact_store`, `test:Gate3AgentToolPolicyTests`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0103 - canonical:GATE-3#17.6

- Source reference: docs/GATE-3-CHECKLIST.md row 17.6
- Description: A tool that times out returns a normalised error result the agent receives, and the run never stays waiting for a tool for ever.
- Implementation: `file:services/sandbox/src/iacode_sandbox/service.py`, `file:services/orchestrator/src/iacode_orchestrator/workflows/agent_run.py`
- Test: `test:test_a_timeout_kills_the_whole_process_tree`, `test:WorkflowSandboxDispatchTests`
- Negative test: _none_
- Documentation: _none_
- Validation: `command:cmd-0072`
- Guardrail: _none_

### REQ-0104 - canonical:GATE-3#17.7

- Source reference: docs/GATE-3-CHECKLIST.md row 17.7
- Description: Cancelling a run during a long command stops the command, records the cancellation, ends the run cancelled and leaves no process behind.
- Implementation: `file:scripts/iacode/scenarios/sandbox_coding_e2e.py`
- Test: `test:test_a_cancelled_run_stops_its_command_and_leaves_nothing_running`
- Negative test: _none_
- Documentation: _none_
- Validation: `command:cmd-0073`
- Guardrail: _none_

### REQ-0105 - canonical:GATE-3#17.8

- Source reference: docs/GATE-3-CHECKLIST.md row 17.8
- Description: A sandbox service restart while a run executes does not lose the run: the session is reconciled and the run completes.
- Implementation: `file:scripts/iacode/scenarios/sandbox_coding_e2e.py`
- Test: `test:RecoveryTests`
- Negative test: _none_
- Documentation: _none_
- Validation: `command:cmd-0074`
- Guardrail: _none_

### REQ-0106 - canonical:GATE-3#18.1

- Source reference: docs/GATE-3-CHECKLIST.md row 18.1
- Description: A profile that may request tools names the sandbox policy that governs them, and a profile with tools and no policy is refused.
- Implementation: `file:services/agent-runtime/src/iacode_agent_runtime/profiles.py`
- Test: `test:SandboxProfileTests`, `test:test_a_profile_with_tools_and_no_policy_is_refused`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0107 - canonical:GATE-3#18.2

- Source reference: docs/GATE-3-CHECKLIST.md row 18.2
- Description: No agent is given every tool: each profile's permitted actions are within its policy's tools.
- Implementation: `file:.iacode/policies/sandbox-policy.json`
- Test: `test:Gate3AgentToolPolicyTests`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0108 - canonical:GATE-3#18.3

- Source reference: docs/GATE-3-CHECKLIST.md row 18.3
- Description: A developer profile may read, search, write, patch, run tests and use the local Git tools its policy allows.
- Implementation: `file:agents/profiles/developer.json`
- Test: `test:test_the_developer_and_the_reviewer_name_their_policies`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0109 - canonical:GATE-3#18.4

- Source reference: docs/GATE-3-CHECKLIST.md row 18.4
- Description: The reviewer is read-only: read, search, diff and test results, and no writing tool.
- Implementation: `file:agents/profiles/code-reviewer.json`
- Test: `test:test_the_code_reviewer_is_given_no_writing_tool`, `test:test_the_reviewer_is_read_only`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0110 - canonical:GATE-3#18.5

- Source reference: docs/GATE-3-CHECKLIST.md row 18.5
- Description: The planner has no writing tool and works from context alone.
- Implementation: `file:agents/profiles/planner.json`
- Test: `test:Gate3AgentToolPolicyTests`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0111 - canonical:GATE-3#18.6

- Source reference: docs/GATE-3-CHECKLIST.md row 18.6
- Description: A minimal coding team — planner, developer, reviewer — proves the flow, and no larger team is built.
- Implementation: `file:agents/teams/coding.json`
- Test: `test:test_the_coding_team_is_planner_developer_reviewer`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0112 - canonical:GATE-3#19.1

- Source reference: docs/GATE-3-CHECKLIST.md row 19.1
- Description: Full output, large diffs and workspace snapshots are stored in the existing artifact infrastructure, recorded as artifacts, and no second store is created.
- Implementation: `file:services/sandbox/src/iacode_sandbox/artifacts.py`, `file:services/sandbox/src/iacode_sandbox/snapshots.py`
- Test: `test:test_truncated_output_goes_to_the_artifact_store`, `test:SandboxArtifactStoreTests`
- Negative test: _none_
- Documentation: _none_
- Validation: `checkpoint:VERIFICATION-REPORT.json`
- Guardrail: _none_

### REQ-0113 - canonical:GATE-3#19.2

- Source reference: docs/GATE-3-CHECKLIST.md row 19.2
- Description: A workspace snapshot is created from an explicit source directory by a documented command, and never from the development working tree implicitly.
- Implementation: `file:scripts/iacode/sandbox_snapshot.py`
- Test: `test:test_the_snapshot_builder_refuses_a_link`, `test:SandboxScenarioTests`
- Negative test: _none_
- Documentation: _none_
- Validation: `command:cmd-0071`
- Guardrail: _none_

### REQ-0114 - canonical:GATE-3#20.1

- Source reference: docs/GATE-3-CHECKLIST.md row 20.1
- Description: A registry of sandbox image profiles exists, the architecture accepts new profiles, and one functional profile for this project carries Git and Python.
- Implementation: `file:.iacode/policies/sandbox-policy.json`, `file:services/sandbox/images/iacode-dev/Dockerfile`
- Test: `test:SandboxImageProfileTests`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0115 - canonical:GATE-3#20.2

- Source reference: docs/GATE-3-CHECKLIST.md row 20.2
- Description: The image is built as part of the Gate from a base pinned by digest and packages pinned by version, and never from a moving tag.
- Implementation: `file:services/sandbox/images/iacode-dev/Dockerfile`
- Test: `test:SandboxImageProfileTests`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0116 - canonical:GATE-3#20.3

- Source reference: docs/GATE-3-CHECKLIST.md row 20.3
- Description: The image is addressed by a fingerprint of its inputs, and a missing or stale image is refused rather than substituted.
- Implementation: `file:services/sandbox/src/iacode_sandbox/image.py`, `file:scripts/iacode/sandbox_image.py`
- Test: `test:test_a_missing_or_stale_image_is_refused_rather_than_substituted`, `test:SandboxImageProfileTests`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0117 - canonical:GATE-3#20.4

- Source reference: docs/GATE-3-CHECKLIST.md row 20.4
- Description: The sandbox gate builds the service image and the sandbox image before it measures anything.
- Implementation: `file:scripts/iacode/gates/sandbox_tests.py`
- Test: `test:Gate3MandatoryGateTests`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0118 - canonical:GATE-3#20.5

- Source reference: docs/GATE-3-CHECKLIST.md row 20.5
- Description: The sandbox service installs the one dependency lock the dependency scan reads, so its Python dependencies are scanned with the rest; the sandbox image's system packages are pinned by version, and what the scan does not cover is documented rather than implied.
- Implementation: `file:services/sandbox/Dockerfile`, `file:scripts/iacode/dependency_scan.py`
- Test: `test:SandboxImageProfileTests`
- Negative test: _none_
- Documentation: `file:docs/runbooks/SANDBOX.md`
- Validation: `command:cmd-0105`, `checkpoint:VERIFICATION-REPORT.json`
- Guardrail: _none_

### REQ-0119 - canonical:GATE-3#21.1

- Source reference: docs/GATE-3-CHECKLIST.md row 21.1
- Description: An internal service contract creates a session, executes a tool, inspects a session and terminates it, and it is reached only as activities on the sandbox's task queue.
- Implementation: `file:services/sandbox/src/iacode_sandbox/service.py`, `file:services/sandbox/src/iacode_sandbox/worker.py`
- Test: `test:SandboxServiceDecisionTests`, `test:WorkflowSandboxDispatchTests`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0120 - canonical:GATE-3#21.2

- Source reference: docs/GATE-3-CHECKLIST.md row 21.2
- Description: A refusal is recorded as an execution with its reason, so a denied request is as traceable as an executed one.
- Implementation: `file:services/sandbox/src/iacode_sandbox/service.py`
- Test: `test:test_a_denial_is_recorded_as_an_execution`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0121 - canonical:GATE-3#21.3

- Source reference: docs/GATE-3-CHECKLIST.md row 21.3
- Description: The service's health is a poller on its queue and an engine that answers, not a process that exists.
- Implementation: `file:services/sandbox/src/iacode_sandbox/healthcheck.py`
- Test: `test:SandboxBoundaryTests`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0122 - canonical:GATE-3#22.1

- Source reference: docs/GATE-3-CHECKLIST.md row 22.1
- Description: The service publishes instruments for sessions created and active, tool executions, their duration, failures, timeouts and policy refusals.
- Implementation: `file:services/sandbox/src/iacode_sandbox/telemetry.py`
- Test: `test:SandboxMetricsTests`, `test:test_every_required_instrument_exists`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0123 - canonical:GATE-3#22.2

- Source reference: docs/GATE-3-CHECKLIST.md row 22.2
- Description: Every metric label is low cardinality, a command never becomes a label, and a refusal is counted by its reason.
- Implementation: `file:services/sandbox/src/iacode_sandbox/telemetry.py`
- Test: `test:test_no_instrument_declares_a_label_outside_the_permitted_set`, `test:test_a_command_never_becomes_a_label`, `test:test_a_refusal_is_counted_by_reason`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0124 - canonical:GATE-3#22.3

- Source reference: docs/GATE-3-CHECKLIST.md row 22.3
- Description: Logs carry the run, the agent, the sandbox, the tool, the status and the duration, and never a whole result, a secret or the host environment.
- Implementation: `file:services/sandbox/src/iacode_sandbox/telemetry.py`
- Test: `test:SandboxLogTests`, `test:test_an_execution_log_record_holds_no_command_or_output`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0125 - canonical:GATE-3#22.4

- Source reference: docs/GATE-3-CHECKLIST.md row 22.4
- Description: The observability stack scrapes the sandbox service.
- Implementation: `file:infra/prometheus/prometheus.yml`
- Test: `test:SandboxBoundaryTests`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0126 - canonical:GATE-3#23.1

- Source reference: docs/GATE-3-CHECKLIST.md row 23.1
- Description: The run page shows each tool the sandbox executed: the tool, its status, its duration, the abbreviated sandbox identifier and a summary.
- Implementation: `file:apps/web/src/app/agent-runtime/agent-runtime.html`, `file:apps/web/src/app/agent-runtime/agent-runtime.spec.ts`
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0127 - canonical:GATE-3#23.2

- Source reference: docs/GATE-3-CHECKLIST.md row 23.2
- Description: The page never receives a tool's output and offers no interactive shell.
- Implementation: `file:apps/web/src/app/agent-runtime/agent-runtime.html`, `file:packages/contracts/src/iacode_contracts/sandbox.py`
- Test: `test:test_the_page_offers_nothing_that_would_execute_a_tool`, `test:test_the_detail_shows_what_the_sandbox_executed_and_not_its_output`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0128 - canonical:GATE-3#23.3

- Source reference: docs/GATE-3-CHECKLIST.md row 23.3
- Description: The command line interface stays reserved for the Gate that owns it.
- Implementation: `file:.iacode/policies/gate-scope.json`
- Test: `test:Gate3ScopeTests`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0129 - canonical:GATE-3#24.1

- Source reference: docs/GATE-3-CHECKLIST.md row 24.1
- Description: A synthetic repository with a defective function and a failing test is provisioned as a snapshot, and a coding run over it reads the code, runs the failing test, patches the code, runs the passing test, reads the diff, commits locally, is reviewed and finishes.
- Implementation: `file:scripts/iacode/scenarios/sandbox_coding_e2e.py`
- Test: `test:SandboxScenarioTests`
- Negative test: _none_
- Documentation: _none_
- Validation: `command:cmd-0071`
- Guardrail: _none_

### REQ-0130 - canonical:GATE-3#24.2

- Source reference: docs/GATE-3-CHECKLIST.md row 24.2
- Description: The scenario drives the real workflow, the real activities, the real sandbox service and the real container engine, with only the model replaced by a deterministic script.
- Implementation: `file:scripts/iacode/scenarios/sandbox_coding_e2e.py`
- Test: `test:SandboxScenarioTests`
- Negative test: _none_
- Documentation: _none_
- Validation: `command:cmd-0071`, `command:cmd-0072`, `command:cmd-0073`, `command:cmd-0074`
- Guardrail: _none_

### REQ-0131 - canonical:GATE-3#24.3

- Source reference: docs/GATE-3-CHECKLIST.md row 24.3
- Description: An automatic proof shows a shell request did not execute on the host: a sentinel outside the sandbox is neither created nor modified.
- Implementation: `file:scripts/iacode/scenarios/sandbox_coding_e2e.py`
- Test: `test:SandboxScenarioTests`
- Negative test: _none_
- Documentation: _none_
- Validation: `command:cmd-0071`
- Guardrail: _none_

### REQ-0132 - canonical:GATE-3#24.4

- Source reference: docs/GATE-3-CHECKLIST.md row 24.4
- Description: The scenario asserts what the run recorded — its terminal state, its tool executions and the test that passed — rather than what the harness sent.
- Implementation: `file:scripts/iacode/scenarios/sandbox_coding_e2e.py`
- Test: `test:SandboxScenarioTests`
- Negative test: _none_
- Documentation: _none_
- Validation: `command:cmd-0071`
- Guardrail: _none_

### REQ-0133 - canonical:GATE-3#25.1

- Source reference: docs/GATE-3-CHECKLIST.md row 25.1
- Description: The repository's one verification command covers this Gate, in its targeted and its full mode.
- Implementation: `file:scripts/iacode/verify.py`
- Test: `test:Gate3VerificationStageTests`
- Negative test: _none_
- Documentation: _none_
- Validation: `command:cmd-0105`, `checkpoint:VERIFICATION-REPORT.json`
- Guardrail: _none_

### REQ-0134 - canonical:GATE-3#25.2

- Source reference: docs/GATE-3-CHECKLIST.md row 25.2
- Description: A runbook documents the lifecycle, the tool policy, the filesystem, the shell, Git, the network, resources, artifacts, cleanup, debugging and the security boundary.
- Implementation: _none_
- Test: `test:Gate3DocumentationTests`
- Negative test: _none_
- Documentation: `file:docs/runbooks/SANDBOX.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0135 - canonical:GATE-3#25.3

- Source reference: docs/GATE-3-CHECKLIST.md row 25.3
- Description: The architecture, development, version and entry documents describe what this Gate delivered rather than what was planned.
- Implementation: _none_
- Test: `test:Gate3DocumentationTests`
- Negative test: _none_
- Documentation: `file:docs/ARCHITECTURE.md`, `file:docs/DEVELOPMENT.md`, `file:docs/VERSIONS.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0136 - canonical:GATE-3#25.4

- Source reference: docs/GATE-3-CHECKLIST.md row 25.4
- Description: The structural decisions of this Gate are recorded as ADRs and listed in the index.
- Implementation: _none_
- Test: `test:Gate3AdrTests`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0137 - canonical:GATE-3#25.5

- Source reference: docs/GATE-3-CHECKLIST.md row 25.5
- Description: The Gate produces its retrospective from the canonical template, and its reusable lessons are recorded with the guardrail that protects the property rather than one file.
- Implementation: `file:.iacode/memory/lessons.jsonl`
- Test: _none_
- Negative test: _none_
- Documentation: `file:.iacode/memory/retrospectives/GATE-3-CP-0001.md`, `file:.iacode/templates/retrospective/TEMPLATE.md`
- Validation: `command:cmd-0088`
- Guardrail: _none_

### REQ-0138 - canonical:GATE-3#25.6

- Source reference: docs/GATE-3-CHECKLIST.md row 25.6
- Description: Every commit of the Gate and its checkpoint tag are on the authorised remote when the Gate closes.
- Implementation: `file:scripts/development-ledger/remote_sync.py`
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: `command:cmd-0121`
- Guardrail: _none_

### REQ-0139 - canonical:GATE-3#25.7

- Source reference: docs/GATE-3-CHECKLIST.md row 25.7
- Description: The Gate closes at the project's own internal verdict, leaves the milestone verdict to a fresh-session audit, and starts no part of the Gate that follows it.
- Implementation: `file:docs/checkpoints/GATE-3-CP-0001/STATE.json`
- Test: `test:Gate3ScopeTests`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0001 - lesson:LSN-0001

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0001
- Description: Verify checkpoint validation must succeed from a detached checkout of the checkpoint tag
- Implementation: _none_
- Test: `test:DetachedHeadValidationTests.test_detached_head_at_checkpoint_tag_validates`, `test:DetachedHeadValidationTests.test_detached_head_at_wrong_commit_fails`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0002 - lesson:LSN-0002

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0002
- Description: Verify a file inventory must be recomputed from the repository, never trusted as an assertion
- Implementation: _none_
- Test: `test:DeltaInventoryTests.test_removed_manifest_entry_fails`, `test:DeltaInventoryTests.test_silent_tracked_modification_fails`
- Negative test: _none_
- Documentation: _none_
- Validation: `checkpoint:FILES.json`
- Guardrail: _none_

### LESSON-REQ-0003 - lesson:LSN-0003

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0003
- Description: Verify every operation attempt must be auditable, including a refusal decided before execution
- Implementation: _none_
- Test: `test:FinalizationAttemptRecordingTests.test_detached_head_refusal_is_recorded`, `test:FinalizationAttemptRecordingTests.test_non_latest_checkpoint_refusal_is_recorded`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0004 - lesson:LSN-0004

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0004
- Description: Verify a checkpoint may never claim readiness while it also claims to be blocked
- Implementation: _none_
- Test: `test:StatusBlockerInvariantTests.test_ready_for_review_with_blocker_fails`, `test:ResealedBlockerFixtureTests.test_resealed_ready_for_review_with_blocker_is_rejected`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0005 - lesson:LSN-0005

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0005
- Description: Verify a PASS requires evidence that can be executed or resolved, not a statement
- Implementation: _none_
- Test: `test:QualityEvidenceTests.test_pass_without_evidence_fails`, `test:QualityEvidenceTests.test_pass_referencing_a_failed_command_fails`, `test:PromotionInvariantTests.test_every_positive_status_rejects_every_red_quality_dimension`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0006 - lesson:LSN-0006

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0006
- Description: Verify the repository must be self-contained; a specification may not live outside it
- Implementation: _none_
- Test: `test:SetupChecklistTests.test_checklist_exists_and_is_referenced`, `test:SetupChecklistTests.test_documentation_links_resolve`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0007 - lesson:LSN-0007

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0007
- Description: Verify independent validation cannot be declared by the run that did the work
- Implementation: _none_
- Test: `test:ExternalAttestationTests.test_an_implementer_checkpoint_cannot_declare_an_external_pass`, `test:ExternalAttestationTests.test_an_attestation_naming_the_subject_as_its_own_auditor_is_rejected`, `test:ExternalAttestationTests.test_second_tool_validation_alone_is_not_enough`, `test:SecondToolValidationTests.test_failed_cross_tool_validation_cannot_grant_gate_pass`, `test:DeliveryAssuranceGateTests.test_self_claimed_independent_review_blocks_review`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0008 - lesson:LSN-0008

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0008
- Description: Verify requirement completeness must be total and evidence-backed before handoff
- Implementation: _none_
- Test: `test:ExpectedRequirementSetTests.test_deleting_a_requirement_and_recomputing_the_counts_still_fails`, `test:ExpectedRequirementSetTests.test_an_unexpected_anchored_requirement_is_rejected`, `test:DeliveryCompletenessMatrixTests.test_one_requirement_short_of_total_fails`, `test:DeliveryAssuranceGateTests.test_completeness_validator_not_executed_blocks_review`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0009 - lesson:LSN-0009

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0009
- Description: Verify a red gate requires rework, never a waiver, and never a weakened check
- Implementation: _none_
- Test: `test:MandatoryGatePolicyTests.test_a_cycle_measured_against_no_gate_is_rejected`, `test:MandatoryGatePolicyTests.test_the_policy_declares_a_non_empty_closed_set`, `test:GreenKeeperToolTests.test_red_gate_is_reported_as_still_red`, `test:DeliveryAssuranceGateTests.test_green_keeper_pass_with_a_real_failure_is_rejected`, `test:DeliveryAssuranceGateTests.test_red_tests_block_review`
- Negative test: _none_
- Documentation: _none_
- Validation: `checkpoint:REWORK-LOG.jsonl`, `command:cmd-0107`
- Guardrail: _none_

### LESSON-REQ-0010 - lesson:LSN-0010

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0010
- Description: Verify a recorded command must carry runtime, working directory, commit and purpose to be replayable
- Implementation: _none_
- Test: `test:CommandInputBindingTests.test_a_record_without_a_digest_is_rejected`, `test:CommandInputBindingTests.test_a_clean_tree_claim_is_checked_against_the_declared_commit`, `test:CommandReproducibilityTests.test_bare_script_name_is_rejected`, `test:CommandReproducibilityTests.test_unresolvable_script_path_is_rejected`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0011 - lesson:LSN-0011

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0011
- Description: Verify a control over a checkpoint's own evidence must be scoped to the moment it matters
- Implementation: _none_
- Test: `test:DeliveryAssuranceGateTests.test_gate_consistency_is_provisional_while_work_is_in_progress`, `test:GateRunnerTests.test_every_runner_of_the_mandatory_gates_refreshes_the_declared_hashes`, `test:GateRunnerTests.test_the_refresh_has_one_definition`, `test:GateRunnerTests.test_no_other_module_executes_the_mandatory_gate_set`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0012 - lesson:LSN-0012

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0012
- Description: Verify sealed checkpoints and their tags are immutable, and tooling must keep validating them
- Implementation: _none_
- Test: `test:IntegrityAnchorTests.test_a_moved_historical_tag_is_detected`, `test:IntegrityAnchorTests.test_a_broken_link_between_anchors_is_detected`, `test:HistoricalCheckpointCompatibilityTests.test_first_sealed_checkpoint_still_validates`, `test:HistoricalCheckpointCompatibilityTests.test_fourth_sealed_checkpoint_still_validates`
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
- Documentation: `file:docs/TOOL-CAPABILITIES.md`
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0014 - lesson:LSN-0014

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0014
- Description: Verify evidence must be recorded as it happens, not reconstructed at the end of a run
- Implementation: _none_
- Test: `test:SealChronologyTests.test_a_record_after_the_end_of_the_run_is_rejected`, `test:SealChronologyTests.test_a_missing_post_commit_validation_is_rejected`, `test:SealChronologyTests.test_a_dirty_tree_validation_is_not_evidence_of_a_sealed_commit`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0015 - lesson:LSN-0015

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0015
- Description: Verify every positive terminal status needs one shared promotion invariant
- Implementation: _none_
- Test: `test:PromotionInvariantTests.test_every_positive_status_rejects_a_red_green_keeper`, `test:PromotionInvariantTests.test_every_positive_status_rejects_every_red_quality_dimension`, `test:PromotionInvariantTests.test_a_terminal_status_requires_an_independent_verdict`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0016 - lesson:LSN-0016

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0016
- Description: Verify a mandatory set must be closed by policy, never chosen by the caller
- Implementation: _none_
- Test: `test:MandatoryGatePolicyTests.test_a_cycle_missing_one_mandatory_gate_is_rejected`, `test:MandatoryGatePolicyTests.test_a_mandatory_gate_that_exited_nonzero_is_rejected`, `test:MandatoryGatePolicyTests.test_a_pass_measured_before_a_source_change_is_stale`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0017 - lesson:LSN-0017

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0017
- Description: Verify a completeness denominator must come from a source the delivery does not own
- Implementation: _none_
- Test: `test:ExpectedRequirementSetTests.test_the_expected_set_is_derived_from_the_canonical_sources`, `test:ExpectedRequirementSetTests.test_the_checklist_is_reparsed_rather_than_trusted`, `test:ExpectedRequirementSetTests.test_a_downgraded_matrix_cannot_escape_the_comparison`, `test:ExpectedRequirementSetTests.test_an_unexpected_anchored_requirement_is_rejected`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0018 - lesson:LSN-0018

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0018
- Description: Verify a structured reference must be resolved, not merely well typed
- Implementation: _none_
- Test: `test:LessonResolutionTests.test_a_test_control_must_exist_in_the_suite`, `test:LessonResolutionTests.test_an_invariant_control_must_be_defined_in_the_tooling`, `test:LessonResolutionTests.test_lesson_evidence_must_resolve`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0019 - lesson:LSN-0019

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0019
- Description: Verify a derived artifact must carry a fingerprint of the inputs that produced it
- Implementation: _none_
- Test: `test:PreflightFreshnessTests.test_a_changed_fingerprint_makes_the_preflight_stale`, `test:PreflightFreshnessTests.test_a_dropped_lesson_makes_the_preflight_stale`, `test:PreflightFreshnessTests.test_a_preflight_from_another_gate_is_refused`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0020 - lesson:LSN-0020

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0020
- Description: Verify evidence produced from a dirty tree needs immutable input identity
- Implementation: _none_
- Test: `test:CommandInputBindingTests.test_the_recorder_binds_inputs_automatically`, `test:CommandInputBindingTests.test_a_digest_that_omits_an_input_is_rejected`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0021 - lesson:LSN-0021

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0021
- Description: Verify sealed history needs an anchor outside the content it describes
- Implementation: _none_
- Test: `test:IntegrityAnchorTests.test_an_unexpected_tree_is_detected`, `test:IntegrityAnchorTests.test_a_sealed_checkpoint_without_an_anchor_is_detected`, `test:IntegrityAnchorTests.test_a_recomputed_anchor_hash_must_match_its_fields`, `test:IntegrityAnchorTests.test_a_broken_link_between_anchors_is_detected`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0022 - lesson:LSN-0022

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0022
- Description: Verify an authoritative count must be derived once, never maintained by hand twice
- Implementation: _none_
- Test: `test:DerivedCountTests.test_a_forged_count_is_rejected`, `test:DerivedCountTests.test_a_markdown_claim_that_contradicts_the_derivation_is_rejected`, `test:SourceCardinalityPolicyTests.test_no_comment_or_docstring_states_a_derived_count_claim`, `test:SourceCardinalityPolicyTests.test_no_comment_or_docstring_states_the_cardinality_of_a_derived_set`, `test:SourceCardinalityPolicyTests`
- Negative test: _none_
- Documentation: _none_
- Validation: `checkpoint:COUNTS.json`, `command:cmd-0120`
- Guardrail: _none_

### LESSON-REQ-0023 - lesson:LSN-0023

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0023
- Description: Verify a lesson must cite a source that actually records the finding it claims
- Implementation: _none_
- Test: `test:LessonProvenanceTests.test_a_finding_absent_from_the_cited_checkpoint_is_rejected`, `test:LessonProvenanceTests.test_a_nonexistent_checkpoint_is_rejected`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0024 - lesson:LSN-0024

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0024
- Description: Verify a control is finished only when its positive path has been executed, not only its refusals
- Implementation: _none_
- Test: `test:PositivePromotionTests.test_the_milestone_verdict_is_derived_as_passed`, `test:PositivePromotionTests.test_the_subject_is_not_rewritten_by_its_own_audit`, `test:SimulationExecutesProductionControlsTests.test_the_sealed_artifact_is_the_tools_own_output`, `test:SimulationExecutesProductionControlsTests.test_every_simulated_mirror_is_recorded_as_executed`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0025 - lesson:LSN-0025

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0025
- Description: Verify a generic guardrail derives repository state instead of naming today's checkpoint
- Implementation: _none_
- Test: `test:IntegrityAnchorTests.test_the_pending_exclusion_is_the_newest_sealed_checkpoint`, `test:SuccessorDurabilityTests.test_the_pending_exclusion_moves_with_the_chain`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0026 - lesson:LSN-0026

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0026
- Description: Verify an adversarial battery without a null-mutation control proves nothing
- Implementation: _none_
- Test: `test:InternalAssuranceTests.test_a_report_without_a_null_mutation_control_is_rejected`, `test:InternalAssuranceTests.test_a_failed_null_mutation_control_cannot_produce_a_pass`, `test:Gate3RedTeamHarnessTests`
- Negative test: _none_
- Documentation: _none_
- Validation: `checkpoint:M1-INTERNAL-RED-TEAM.json`
- Guardrail: _none_

### LESSON-REQ-0027 - lesson:LSN-0027

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0027
- Description: Verify a lesson's prose may record a residual limit but may never contradict its status
- Implementation: _none_
- Test: `test:MemoryPolicyDocumentTests.test_a_guarded_lesson_may_not_describe_itself_as_unguarded`, `test:MemoryPolicyDocumentTests.test_the_repository_memory_has_no_status_contradiction`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0028 - lesson:LSN-0028

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0028
- Description: Verify a configuration key that no code reads is a defect, not documentation
- Implementation: _none_
- Test: `test:MemoryPolicyDocumentTests.test_a_setting_no_code_reads_cannot_be_declared`, `test:MemoryPolicyDocumentTests.test_the_declared_policy_validates_against_its_schema`, `test:test_configuration.test_every_declared_key_is_read_somewhere`, `test:test_configuration.test_test_settings_ignore_the_ambient_environment`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0029 - lesson:LSN-0029

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0029
- Description: Verify a required protocol transition must never turn a mandatory gate red
- Implementation: _none_
- Test: `test:SuccessorDurabilityTests.test_every_state_of_the_chain_verifies`, `test:SuccessorDurabilityTests.test_a_missing_anchor_is_still_detected_after_the_chain_advances`, `test:GateTransitionSimulationTests.test_the_first_checkpoint_of_the_next_gate_reaches_review_readiness`, `test:GateTransitionSimulationTests.test_its_mirror_audit_passes_with_the_empty_dimensions_inapplicable`
- Negative test: _none_
- Documentation: _none_
- Validation: `command:cmd-0111`
- Guardrail: _none_

### LESSON-REQ-0030 - lesson:LSN-0031

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0030
- Description: Verify an empty applicable set is not a missing required set, and a control must tell them apart
- Implementation: _none_
- Test: `test:MirrorApplicabilitySemanticsTests.test_an_empty_applicable_set_is_not_applicable_and_the_mirror_passes`, `test:MirrorApplicabilitySemanticsTests.test_a_missing_required_set_fails_rather_than_being_inapplicable`, `test:MirrorApplicabilityValidationTests.test_a_registry_bound_dimension_cannot_be_declared_inapplicable`, `test:SimulationExecutesProductionControlsTests.test_the_sealed_artifact_is_the_tools_own_output`, `test:SimulationExecutesProductionControlsTests.test_every_simulated_mirror_is_recorded_as_executed`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0031 - lesson:LSN-0032

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0031
- Description: Verify a control written while one Gate was the only Gate stops being a control when the next one starts
- Implementation: _none_
- Test: `test:Gate1ScopeTests.test_no_future_gate_capability_is_implemented`, `test:MonorepoStructureTests.test_no_future_gate_capability_is_implemented`, `test:MonorepoStructureTests.test_the_scope_control_detects_an_implementation`, `test:MonorepoStructureTests.test_the_scope_control_ignores_a_gate_that_has_already_run`, `test:ExpectedRequirementSetTests.test_expected_set_names_the_gate_specification`, `test:AssuranceScopeTests.test_assurance_scope_covers_the_runtime_source`, `test:TestSuiteRegistryTests.test_declared_suites_are_discovered`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0032 - lesson:LSN-0033

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0032
- Description: Verify a value bound in middleware is absent in the handlers that run outside it
- Implementation: _none_
- Test: `test:test_errors_and_correlation.test_internal_error_still_carries_a_correlation_identifier`, `test:test_errors_and_correlation.test_internal_error_leaks_nothing`, `test:test_errors_and_correlation.test_a_missing_route_uses_the_error_contract`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0033 - lesson:LSN-0034

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0033
- Description: Verify re-deriving what the framework already computed diverges from the framework
- Implementation: _none_
- Test: `test:test_observability.test_metrics_endpoint_exposes_request_metrics`, `test:test_observability.test_metrics_label_routes_by_template_not_by_url`, `test:PrometheusConfigurationTests.test_the_api_instruments_reach_prometheus`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0034 - lesson:LSN-0035

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0034
- Description: Verify captured subprocess output decoded or re-emitted with the platform codepage crashes the tool, not the work
- Implementation: _none_
- Test: `test:SubprocessDecodingTests.test_no_capture_relies_on_the_platform_codepage`, `test:SubprocessDecodingTests.test_every_tool_that_re_emits_captured_output_configures_its_own_stream`, `test:SubprocessDecodingTests.test_the_rule_detects_a_capture_that_would_fail`, `test:SubprocessDecodingTests`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0035 - lesson:LSN-0036

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0035
- Description: Verify a gate that runs inside an image measures the image, not the source
- Implementation: _none_
- Test: `test:Gate1GuardrailTests.test_every_image_gate_builds_before_it_measures`, `test:Gate1GuardrailTests.test_the_image_gate_rule_detects_a_gate_that_would_skip_the_build`, `test:Gate3MandatoryGateTests.test_the_gate_builds_both_images_before_it_measures`, `test:SandboxScenarioTests.test_the_scenario_builds_what_it_measures_first`, `test:SandboxImageProfileTests.test_the_image_is_addressed_by_its_inputs`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0036 - lesson:LSN-0037

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0036
- Description: Verify a shared control that names an identifier the repository derives stops being a control when that identifier moves
- Implementation: _none_
- Test: `test:Gate1GuardrailTests.test_no_shared_control_is_bound_to_a_gate_literal`, `test:Gate1GuardrailTests.test_the_gate_literal_rule_detects_a_bound_control`, `test:Gate1GuardrailTests.test_the_gate_literal_rule_accepts_a_derived_gate_and_a_fixture_root`, `test:Gate1GuardrailTests.test_no_control_names_a_migration_revision_literally`, `test:Gate1GuardrailTests.test_the_revision_rule_detects_a_named_head`, `test:Gate1GuardrailTests.test_the_head_revision_has_one_derivation`, `test:Gate3ScopeTests`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0037 - lesson:LSN-0038

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0037
- Description: Verify two representations of one concept in one module disagree, and the safer one loses
- Implementation: _none_
- Test: `test:test_common_primitives.test_a_documented_placeholder_is_not_redacted`, `test:Gate1GuardrailTests.test_both_redactors_agree_on_every_value_the_example_file_carries`, `test:CredentialVocabularyTests.test_no_module_writes_its_own_credential_name_rule`, `test:CredentialVocabularyTests.test_the_rule_detects_a_second_opinion`, `test:CredentialVocabularyTests.test_the_two_questions_stay_different`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0038 - lesson:LSN-0039

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0038
- Description: Verify a test that writes to the operational database leaves production data behind
- Implementation: _none_
- Test: `test:test_gateway_persistence.test_the_operational_catalog_holds_only_providers_the_policy_declares`, `test:IntegrationResidueTests.test_nothing_this_suite_writes_is_left_behind`, `test:test_the_detail_shows_what_the_sandbox_executed_and_not_its_output`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0039 - lesson:LSN-0040

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0039
- Description: Verify a control that judges sealed history only runs once a successor anchors it
- Implementation: _none_
- Test: `test:RecordedInputTests.test_every_sealed_checkpoint_validates_from_its_own_tag`, `test:RecordedInputTests.test_the_recorder_never_declares_an_ignored_path_as_an_input`, `test:RecordedInputTests.test_an_ignored_input_is_bound_by_content_rather_than_by_presence`, `test:RecordedInputTests.test_an_input_the_repository_carries_is_still_required_to_exist`, `test:RecordedInputTests.test_an_ignored_input_without_a_bound_digest_is_still_refused`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0040 - lesson:LSN-0041

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0040
- Description: Verify an editing path that consumes a backslash escape leaves a control character, and the control it belonged to silently matches nothing
- Implementation: _none_
- Test: `test:SourceIntegrityTests.test_no_source_file_carries_a_stray_control_character`, `test:SourceIntegrityTests.test_the_scan_detects_one`, `test:FrontendSafetyTests.test_the_page_offers_nothing_that_would_execute_a_tool`, `test:RepositoryToolExecutionBoundaryTests.test_the_boundary_has_something_to_scan`, `test:SourceIntegrityTests`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0041 - lesson:LSN-0042

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0041
- Description: Verify a naming convention rewrites a CHECK constraint's name and leaves a UNIQUE constraint's alone
- Implementation: _none_
- Test: `test:Gate2MigrationTests.test_the_agent_runtime_migration_is_reversible`, `test:test_migrations.test_the_declared_model_matches_the_migrated_schema`, `test:MigrationConstraintNamingTests.test_a_check_constraint_is_created_and_dropped_by_its_bare_name`, `test:MigrationConstraintNamingTests.test_a_unique_constraint_keeps_exactly_the_name_it_was_given`, `test:SandboxMigrationTests`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0042 - lesson:LSN-0043

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0042
- Description: Verify a log line is not evidence that another process is ready
- Implementation: _none_
- Test: `test:ScenarioReadinessTests.test_readiness_is_asked_of_temporal`, `test:ScenarioReadinessTests.test_readiness_is_not_read_from_a_log_line`, `test:ScenarioReadinessTests.test_the_harness_asks_the_server_for_the_answer`, `test:SandboxBoundaryTests.test_the_health_is_a_poller_and_an_engine_not_a_process`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0043 - lesson:LSN-0044

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0043
- Description: Verify a boundary scan must read the code rather than the prose, and must be shown to fire on a mutated module
- Implementation: _none_
- Test: `test:ToolExecutionBoundaryTests.test_the_null_control_detects_a_mutation`, `test:test_boundary.test_the_provider_scan_would_catch_one`, `test:test_boundary.test_the_credential_scan_would_catch_one`, `test:RepositoryToolExecutionBoundaryTests.test_the_scan_detects_a_module_that_does_it`, `test:WorkflowDeterminismTests.test_the_determinism_scan_detects_a_module_that_breaks_it`, `test:SandboxBoundaryTests.test_the_scan_detects_a_module_that_does_it`, `test:SinglePathResolverTests.test_the_scans_detect_a_bypass`, `test:WorkflowSandboxDispatchTests.test_the_scan_detects_a_policy_taken_from_the_request`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0044 - lesson:LSN-0045

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0044
- Description: Verify a counted test suite must declare its cases statically, because the denominator is read from the source
- Implementation: _none_
- Test: `test:CountedSuiteExpansionTests.test_no_counted_pytest_case_expands_at_run_time`, `test:CountedSuiteExpansionTests.test_the_scan_detects_an_expansion`, `test:CountedSuiteExpansionTests`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0045 - lesson:LSN-0046

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0045
- Description: Verify a timeout that cancels the task it runs in leaves nothing able to record what happened
- Implementation: _none_
- Test: `test:DeadlineEnforcementTests.test_the_engine_is_not_wrapped_in_wait_for`, `test:DeadlineEnforcementTests.test_the_deadline_races_an_explicit_child_task`, `test:DeadlineEnforcementTests.test_the_wait_accepts_every_way_a_cancelled_activity_surfaces`, `test:DeadlineEnforcementTests.test_the_deadline_path_writes_the_failure_down`, `test:DeadlineEnforcementTests.test_the_scenario_asserts_the_run_ended_and_said_so`, `test:test_a_timeout_kills_the_whole_process_tree`, `test:WorkflowSandboxDispatchTests.test_a_sandbox_that_cannot_answer_is_a_failed_result_not_a_wait`
- Negative test: _none_
- Documentation: _none_
- Validation: `command:cmd-0072`
- Guardrail: _none_

### LESSON-REQ-0046 - lesson:LSN-0047

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0046
- Description: Verify a refusal that misnames the defect spends the only repair on the wrong correction
- Implementation: `file:services/agent-runtime/src/iacode_agent_runtime/protocol.py`, `file:services/agent-runtime/src/iacode_agent_runtime/context.py`
- Test: `test:test_content_of_the_wrong_type_is_refused_by_its_real_defect`, `test:test_the_runtime_instructions_state_that_content_is_one_string`, `test:test_invalid_envelope_is_not_accepted_silently`, `test:test_a_wrong_type_is_refused_with_its_own_reason`, `test:test_every_hostile_spelling_is_refused_with_its_own_code`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0047 - lesson:LSN-0048

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0047
- Description: Verify a state and the event that explains it, written in two commits, are written event first
- Implementation: `file:services/agent-runtime/src/iacode_agent_runtime/engine.py`, `file:services/orchestrator/src/iacode_orchestrator/workflows/agent_run.py`, `file:apps/api/src/iacode_api/routes/agent_runs.py`
- Test: `test:test_a_terminal_state_is_never_visible_before_its_terminal_event`, `test:DeadlineEnforcementTests.test_the_workflow_writes_the_terminal_event_before_the_terminal_state`, `test:test_a_workflow_that_cannot_start_fails_the_run_rather_than_leaving_it_created`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0048 - lesson:LSN-0049

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0048
- Description: Verify a metric read the instant after the call that moved it is read before the scrape that carries it
- Implementation: `file:scripts/iacode/gateway_smoke.py`, `file:scripts/iacode/smoke.py`
- Test: `test:LiveSmokeContractTests.test_the_observability_check_waits_for_a_scrape_and_asks_only_prometheus`, `test:LiveSmokeContractTests.test_live_smoke_is_bounded_and_minimal`, `test:ObserverCycleTests.test_every_script_that_reads_prometheus_waits_for_a_scrape`, `test:ObserverCycleTests.test_the_scan_fires_on_a_read_that_does_not_wait`, `test:ObserverCycleTests.test_the_foundation_smoke_waits_for_both_targets_and_asks_only_prometheus`, `test:ObserverCycleTests`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0049 - lesson:LSN-0050

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0049
- Description: Verify a checkpoint sealed without naming its own tag cannot be validated from that tag
- Implementation: `file:scripts/development-ledger/validate_checkpoint.py`, `file:scripts/development-ledger/seal_checkpoint.py`, `file:docs/adr/ADR-0023-sealed-checkpoint-binds-its-own-tag.md`
- Test: `test:DetachedHeadValidationTests.test_sealing_refuses_a_state_that_does_not_name_its_own_tag`, `test:DetachedHeadValidationTests.test_a_symbolic_head_validates_from_its_own_canonical_tag`, `test:DetachedHeadValidationTests.test_a_symbolic_head_away_from_its_canonical_tag_is_still_refused`, `test:RecordedInputTests.test_every_sealed_checkpoint_validates_from_its_own_tag`
- Negative test: _none_
- Documentation: `file:docs/CHECKPOINT-PROTOCOL.md`
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0050 - lesson:LSN-0051

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0050
- Description: Verify a payload one service bounds for another must be bounded as the receiver measures it
- Implementation: _none_
- Test: `test:Gate3AgentToolPolicyTests.test_the_runtime_accepts_every_result_the_sandbox_hands_over`, `test:AgentResultBoundTests`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0051 - lesson:LSN-0052

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0051
- Description: Verify two processes that meet on a queue must name what crosses it once, and a real run must exercise both
- Implementation: _none_
- Test: `test:WorkflowSandboxDispatchTests.test_both_sides_name_the_result_by_the_shared_key`, `test:WorkflowSandboxDispatchTests.test_the_key_scan_detects_a_literal`, `test:SandboxActivityTests`
- Negative test: _none_
- Documentation: _none_
- Validation: `command:cmd-0071`
- Guardrail: _none_

### LESSON-REQ-0052 - lesson:LSN-0053

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0052
- Description: Verify a process sweep that reads what a forking process holds waits on the processes it has to kill
- Implementation: _none_
- Test: `test:test_a_fork_bomb_that_detaches_leaves_a_sandbox_that_still_answers`
- Negative test: _none_
- Documentation: _none_
- Validation: `checkpoint:M1-INTERNAL-RED-TEAM.json`
- Guardrail: _none_

### LESSON-REQ-0053 - lesson:LSN-0054

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0053
- Description: Verify a pre-push check narrower than the change's reach lets a red gate reach the public remote
- Implementation: `file:docs/DEVELOPMENT-CONTRACT.md`
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: `command:cmd-0076`, `command:cmd-0064`, `command:cmd-0117`
- Guardrail: _none_
