"use strict";

const vscode = require("vscode");
const crypto = require("node:crypto");
const {
  DesktopClient,
  DesktopClientError,
  endpoint,
  hash,
  protectData,
} = require("./core/client.cjs");
const { preview } = require("./core/snapshot.cjs");
const CONFIG = "iacode.connection.v1";
const STATE = "iacode.lifecycle.v1";
const plain = (value) =>
  JSON.stringify(value, null, 2).replace(
    /[\u007f-\uffff]/g,
    (char) => `\\u${char.charCodeAt(0).toString(16).padStart(4, "0")}`,
  );
const fail = (code, message) => {
  throw new DesktopClientError(code, message);
};

function activate(context) {
  let client = null;
  let generation = 0;
  let disposed = false;
  let busy = false;
  let awaiting = null;
  let inventory = null;
  let inventoryIdentity = null;
  let lastError = null;
  let stale = true;
  let taskState = "NOT_OBSERVED";
  let qualityState = "NOT_OBSERVED";
  let lifecycle = context.workspaceState.get(STATE, {});
  let configurationDigest = null;
  const observers = new Set();
  const candidates = new Set();
  const changed = new vscode.EventEmitter();
  const viewChanged = new vscode.EventEmitter();
  const views = new Map();
  const viewProvider = {
    onDidChange: viewChanged.event,
    provideTextDocumentContent: (uri) => views.get(uri.toString()) || "",
  };
  const status = vscode.window.createStatusBarItem(
    vscode.StatusBarAlignment.Left,
    30,
  );
  const provider = {
    onDidChangeTreeData: changed.event,
    getTreeItem: (item) => item,
    getChildren: () => [
      new vscode.TreeItem(
        `Connection: ${client?.connected ? "authenticated" : "disconnected"}${stale ? " (STALE)" : ""}`,
      ),
      new vscode.TreeItem(`Task: ${taskState} · ${lifecycle.runId || "none"}`),
      new vscode.TreeItem(
        `Quality: ${qualityState} · ${lifecycle.qualityRunId || "none"}`,
      ),
      new vscode.TreeItem(
        `Pending reconciliation: ${lifecycle.pending?.operation || "none"}`,
      ),
      new vscode.TreeItem(`Last refusal: ${lastError?.code || "none"}`),
    ],
  };
  function render() {
    if (disposed) return;
    status.text = `IACode: ${stale ? "STALE" : "connected"} · ${taskState}`;
    status.tooltip =
      "Refresh reads runtime truth; disconnect never cancels remote work.";
    status.command = "iacode.refresh";
    status.show();
    changed.fire();
  }
  async function save(next) {
    await context.workspaceState.update(STATE, next);
    lifecycle = next;
    render();
  }
  function invalidate() {
    generation += 1;
    inventory = null;
    inventoryIdentity = null;
    stale = true;
    for (const observer of observers) observer.abort();
    observers.clear();
    for (const candidate of candidates) candidate.dispose();
    candidates.clear();
    client?.dispose();
    client = null;
    render();
  }
  function workspace() {
    if (!vscode.workspace.isTrusted)
      fail(
        "WORKSPACE_UNTRUSTED",
        "Trust this workspace before any mutation. No request was sent.",
      );
    const folders = vscode.workspace.workspaceFolders || [];
    if (folders.length !== 1 || folders[0].uri.scheme !== "file")
      fail("WORKSPACE_UNSUPPORTED", "Select exactly one local file workspace.");
    return { root: folders[0].uri.fsPath, identity: folders[0].uri.toString() };
  }
  function ticket() {
    return { ...workspace(), generation, client };
  }
  function check(before) {
    if (
      disposed ||
      before.generation !== generation ||
      before.client !== client ||
      before.identity !== workspace().identity
    )
      fail(
        "STALE_APPROVAL",
        "Connection, trust or workspace changed; inspect and approve again.",
      );
  }
  function connectionCheck(epoch) {
    if (disposed || epoch !== generation)
      fail(
        "STALE_CONNECTION",
        "Connection context changed; connect again explicitly.",
      );
  }
  async function authenticatedCandidate(address, key, epoch) {
    const candidate = new DesktopClient(address, key);
    candidates.add(candidate);
    try {
      await candidate.connect();
      connectionCheck(epoch);
      return candidate;
    } catch (error) {
      candidates.delete(candidate);
      candidate.dispose();
      throw error;
    }
  }
  async function configure(address, key) {
    const epoch = generation;
    connectionCheck(epoch);
    const canonical = endpoint(address);
    if (lifecycle.pending && lifecycle.endpointHash !== hash(canonical))
      fail(
        "RECOVERY_ENDPOINT_MISMATCH",
        "Reconcile pending work at the original runtime before changing endpoints.",
      );
    const candidate = await authenticatedCandidate(canonical, key, epoch);
    try {
      const serialized = JSON.stringify({
        version: 1,
        endpoint: canonical,
        key,
      });
      configurationDigest = hash(serialized);
      await context.secrets.store(CONFIG, serialized);
      connectionCheck(epoch);
      candidates.delete(candidate);
      invalidate();
      client = candidate;
      const connectedEpoch = generation;
      // Completed identities belong to one runtime; uncertain identities were refused above.
      if (lifecycle.endpointHash !== hash(canonical))
        await save({ endpointHash: hash(canonical) });
      connectionCheck(connectedEpoch);
      stale = false;
      render();
      return { connected: true, endpoint: canonical };
    } catch (error) {
      candidates.delete(candidate);
      candidate.dispose();
      throw error;
    }
  }
  async function configureConnection(address, key) {
    if (disposed || busy)
      fail(
        "CLIENT_BUSY",
        "Finish the current command before changing connection.",
      );
    busy = true;
    try {
      return await configure(address, key);
    } finally {
      busy = false;
    }
  }
  async function connect() {
    if (disposed) fail("CLIENT_DISPOSED", "Extension has been disposed.");
    if (client?.connected) return client;
    const epoch = generation;
    const value = await context.secrets.get(CONFIG);
    connectionCheck(epoch);
    let config;
    try {
      config = JSON.parse(value);
    } catch {
      fail("CONNECTION_REQUIRED", "Use IACode: Configure Local Runtime.");
    }
    if (config?.version !== 1)
      fail(
        "CONNECTION_REQUIRED",
        "Configure the runtime credential in SecretStorage.",
      );
    if (
      lifecycle.endpointHash &&
      lifecycle.endpointHash !== hash(endpoint(config.endpoint))
    )
      fail(
        "RECOVERY_ENDPOINT_MISMATCH",
        "Use explicit configuration for a different runtime; pending identities are retained.",
      );
    const candidate = await authenticatedCandidate(
      config.endpoint,
      config.key,
      epoch,
    );
    candidates.delete(candidate);
    client?.dispose();
    client = candidate;
    configurationDigest = hash(value);
    generation += 1;
    stale = false;
    render();
    return client;
  }
  async function show(title, value) {
    if (disposed) fail("CLIENT_DISPOSED", "Extension has been disposed.");
    client?.assertSafeData(value);
    if (!client) {
      const stored = await context.secrets.get(CONFIG);
      let configured;
      try {
        configured = stored ? JSON.parse(stored) : null;
      } catch {
        fail(
          "CONNECTION_REQUIRED",
          "Configure valid protected connection state before displaying data.",
        );
      }
      protectData(value, configured?.key);
      if (disposed) fail("CLIENT_DISPOSED", "Extension has been disposed.");
    }
    // Three owned read-only buffers, not unbounded dirty untitled documents or filesystem writes.
    const slot = title.startsWith("Review exact")
      ? "approval"
      : title.startsWith("Local inventory")
        ? "inventory"
        : "runtime";
    const uri = vscode.Uri.parse(`iacode-view:/${slot}.txt`);
    views.set(uri.toString(), plain({ title, data: value }));
    viewChanged.fire(uri);
    const document = await vscode.workspace.openTextDocument(uri);
    await vscode.languages.setTextDocumentLanguage(document, "plaintext");
    if (disposed) fail("CLIENT_DISPOSED", "Extension has been disposed.");
    await vscode.window.showTextDocument(document, {
      preview: true,
      preserveFocus: false,
    });
  }
  async function observed(operation, args) {
    const epoch = generation;
    const observer = client;
    if (!observer?.connected)
      fail("CONNECTION_REQUIRED", "Connect before reading runtime state.");
    const result = await observer.execute(operation, args);
    connectionCheck(epoch);
    if (observer !== client)
      fail("STALE_CONNECTION", "Runtime changed during observation.");
    return result;
  }
  async function choose(kind, items, options) {
    awaiting = kind;
    try {
      return await vscode.window.showQuickPick(items, {
        ...options,
        ignoreFocusOut: false,
      });
    } finally {
      awaiting = null;
    }
  }
  async function input(kind, options) {
    awaiting = kind;
    try {
      return await vscode.window.showInputBox({
        ...options,
        ignoreFocusOut: false,
      });
    } finally {
      awaiting = null;
    }
  }
  async function approve(operation, args, before) {
    const intent = client.intent(operation, args);
    await show(
      "Review exact local runtime operation — no code is applied locally",
      {
        endpoint: client.baseUrl,
        workspace: before.root,
        operation,
        arguments:
          operation === "snapshot"
            ? {
                manifestDigest: args.manifestDigest,
                inventory: inventory.inventory,
                totalBytes: inventory.totalBytes,
                excludedCount: inventory.excludedCount,
              }
            : args,
      },
    );
    check(before);
    const selected = await choose(
      "approval",
      [
        { label: "Cancel", approved: false },
        { label: "Approve exact operation", approved: true },
      ],
      {
        title: `IACode approval: ${operation}`,
        placeHolder:
          "Review the plaintext inventory/action. Cancel is the default.",
      },
    );
    if (!selected?.approved)
      fail(
        "APPROVAL_CANCELLED",
        "Approval dismissed; no domain request was sent.",
      );
    check(before);
    return intent;
  }
  async function mutation(operation, args, before) {
    if (lifecycle.pending)
      fail(
        "RECONCILIATION_REQUIRED",
        "Read the pending outcome before creating another mutation.",
      );
    const approval = await approve(operation, args, before);
    const identity = Object.fromEntries(
      Object.entries(args).filter(([key]) =>
        ["idempotencyKey", "runId", "manifestDigest"].includes(key),
      ),
    );
    await save({
      ...lifecycle,
      rootIdentity: before.identity,
      endpointHash: hash(client.baseUrl),
      pending: { operation, ...identity },
    });
    let result;
    try {
      check(before);
      result = await client.execute(operation, args, { approval });
    } catch (error) {
      if (error instanceof DesktopClientError && !error.uncertain)
        await save({ ...lifecycle, pending: null });
      throw error;
    }
    try {
      check(before);
    } catch {
      throw new DesktopClientError(
        "CONTEXT_CHANGED_OUTCOME_UNCERTAIN",
        "Remote action returned after the local context changed; reconcile before continuing.",
        { uncertain: true, idempotencyKey: args.idempotencyKey },
      );
    }
    const next = { ...lifecycle, pending: null };
    if (operation === "snapshot") next.snapshot = result;
    else if (["start", "cancel"].includes(operation)) {
      if (next.runId !== result.runId) next.runCursor = 0;
      next.runId = result.runId;
      taskState = result.state;
    } else {
      if (next.qualityRunId !== result.runId) next.qualityCursor = 0;
      next.qualityRunId = result.runId;
      qualityState = result.state;
    }
    await save(next);
    await show(
      "Authenticated runtime result — requested is not completed",
      result,
    );
    return result;
  }
  async function recover() {
    await connect();
    const pending = lifecycle.pending;
    if (!pending) return { pending: false };
    if (lifecycle.endpointHash !== hash(client.baseUrl))
      fail(
        "RECOVERY_ENDPOINT_MISMATCH",
        "Use the original runtime for reconciliation.",
      );
    let result;
    if (pending.operation === "snapshot")
      result = await observed("snapshot-lookup", {
        manifestDigest: pending.manifestDigest,
      });
    else if (pending.idempotencyKey)
      result = await observed(
        pending.operation === "start" ? "lookup" : "quality-lookup",
        { idempotencyKey: pending.idempotencyKey },
      );
    else
      result = await observed(
        pending.operation === "cancel" ? "read" : "quality-read",
        { runId: pending.runId },
      );
    if (result.found === false) {
      // An in-flight request can commit later. Not found is not evidence of no side effect.
      await show(
        "Outcome still uncertain — original identity retained; no request replayed",
        result,
      );
      return result;
    }
    const next = { ...lifecycle, pending: null };
    if (pending.operation === "snapshot") next.snapshot = result;
    else if (pending.operation === "start") {
      if (next.runId !== result.runId) next.runCursor = 0;
      next.runId = result.runId;
    } else if (pending.operation.startsWith("quality-")) {
      const recoveredId = result.runId || result.run?.runId;
      if (next.qualityRunId !== recoveredId) next.qualityCursor = 0;
      next.qualityRunId = recoveredId;
    }
    await save(next);
    await show("Read-only reconciliation — no mutation replayed", result);
    return result;
  }
  async function handler(name) {
    if (name === "configure") {
      const address = await input("endpoint", {
        title: "IACode numeric-loopback endpoint",
        prompt: "Explicit local runtime, not a workspace setting",
      });
      if (!address) return { cancelled: true };
      const key = await input("credential", {
        title: "IACode expiring desktop credential",
        password: true,
        prompt: "Stored only in VS Code SecretStorage",
      });
      if (!key) return { cancelled: true };
      // The public configuration API and native command use the same implementation.
      return configure(address, key);
    }
    if (name === "disconnect") {
      invalidate();
      return { disconnected: true, remoteCancellationRequested: false };
    }
    if (name === "connect") {
      invalidate();
      await connect();
      return { connected: true };
    }
    if (name === "recover") return recover();
    if (name === "preview") {
      const root = workspace();
      const before = { ...root, generation, client };
      inventory = await preview(root.root);
      check(before);
      inventoryIdentity = before.identity;
      const { files, ...safe } = inventory;
      await show(
        "Local inventory only — nothing uploaded; API scans exact content before persistence",
        safe,
      );
      return safe;
    }
    const mutations = [
      "snapshot",
      "start",
      "cancel",
      "qualityStart",
      "qualityCancel",
      "qualityReproduce",
    ];
    if (mutations.includes(name)) workspace(); // Before any network call or local file read.
    await connect();
    if (mutations.includes(name)) {
      const before = ticket();
      if (name === "snapshot") {
        if (!inventory || inventoryIdentity !== before.identity)
          fail(
            "SNAPSHOT_PREVIEW_REQUIRED",
            "Preview the current workspace inventory first.",
          );
        const current = await preview(before.root);
        check(before);
        if (
          current.root !== inventory.root ||
          current.manifestDigest !== inventory.manifestDigest
        )
          fail(
            "WORKSPACE_CHANGED",
            "Workspace changed since preview; inspect again.",
          );
        return mutation(
          "snapshot",
          { manifestDigest: current.manifestDigest, files: current.files },
          before,
        );
      }
      if (
        ["start", "qualityStart"].includes(name) &&
        (lifecycle.rootIdentity !== before.identity || !lifecycle.snapshot)
      )
        fail(
          "SNAPSHOT_REQUIRED",
          "Approve a snapshot for this exact workspace and runtime first.",
        );
      if (name === "start") {
        const selection = vscode.window.activeTextEditor;
        const initial = selection
          ? selection.document.getText(selection.selection).slice(0, 8192)
          : "";
        const task = await input("task", {
          title: "IACode task for the immutable snapshot",
          value: initial,
          validateInput: (text) =>
            !text.trim() || Array.from(text).length > 8192
              ? "Enter 1–8192 characters."
              : undefined,
        });
        if (!task)
          fail("APPROVAL_CANCELLED", "Task input dismissed; nothing started.");
        check(before);
        const teams = await observed("teams");
        check(before);
        const team = await choose(
          "team",
          teams
            .filter((item) => item.enabled)
            .map((item) => ({ label: item.team, team: item.team })),
          {
            title: "IACode declared team",
            placeHolder: "Choose the governed runtime team",
          },
        );
        if (!team)
          fail(
            "APPROVAL_CANCELLED",
            "Team selection dismissed; nothing started.",
          );
        check(before);
        return mutation(
          "start",
          {
            snapshotId: lifecycle.snapshot.snapshotId,
            task,
            team: team.team,
            idempotencyKey: crypto.randomUUID(),
          },
          before,
        );
      }
      if (name === "qualityStart")
        return mutation(
          "quality-start",
          {
            snapshotId: lifecycle.snapshot.snapshotId,
            snapshotDigest: lifecycle.snapshot.snapshotDigest,
            idempotencyKey: crypto.randomUUID(),
          },
          before,
        );
      const quality = name.startsWith("quality");
      const runId = quality ? lifecycle.qualityRunId : lifecycle.runId;
      if (!runId) fail("RUN_REQUIRED", "Select a real runtime run first.");
      const operation =
        name === "qualityReproduce"
          ? "quality-reproduce"
          : quality
            ? "quality-cancel"
            : "cancel";
      const args = { runId };
      if (name === "qualityReproduce")
        args.idempotencyKey = crypto.randomUUID();
      return mutation(operation, args, before);
    }
    if (["agents", "teams"].includes(name)) {
      const data = await observed(name);
      await show(name, data);
      return data;
    }
    if (name === "select") {
      const data = await observed("list", { limit: 100 });
      const epoch = generation;
      const selected = await choose(
        "run",
        data.runs.map((run) => ({
          label: run.runId,
          description: run.state,
          runId: run.runId,
        })),
        { title: "IACode existing task" },
      );
      if (!selected) return { cancelled: true };
      connectionCheck(epoch);
      await save({ ...lifecycle, runId: selected.runId, runCursor: 0 });
      name = "read";
    }
    const quality = name.startsWith("quality");
    if (name === "refresh") {
      if (lifecycle.pending) await recover();
      if (lifecycle.runId) {
        const data = await observed("read", { runId: lifecycle.runId });
        taskState = data.state;
      }
      if (lifecycle.qualityRunId) {
        const data = await observed("quality-read", {
          runId: lifecycle.qualityRunId,
        });
        qualityState = data.run.state;
      }
      stale = false;
      render();
      return { taskState, qualityState, pending: Boolean(lifecycle.pending) };
    }
    const runId = quality ? lifecycle.qualityRunId : lifecycle.runId;
    if (!runId) fail("RUN_REQUIRED", "Select a real runtime run first.");
    if (name.endsWith("Events") || name === "events") {
      const cursorKey = quality ? "qualityCursor" : "runCursor";
      const page = await observed(quality ? "quality-events" : "events", {
        runId,
        after: lifecycle[cursorKey] || 0,
        limit: 200,
      });
      await show(
        "Ordered event page — resume cursor is persisted only after display",
        page,
      );
      await save({ ...lifecycle, [cursorKey]: page.nextCursor });
      return page;
    }
    const data = await observed(quality ? "quality-read" : "read", {
      runId,
    });
    if (quality) qualityState = data.run.state;
    else taskState = data.state;
    stale = false;
    render();
    await show(
      quality
        ? "Derived quality verdict, checks, findings and immutable evidence"
        : "Actual task, stages, budget, result and failure",
      data,
    );
    return data;
  }
  const commands = context.extension.packageJSON.contributes.commands;
  for (const { command } of commands)
    context.subscriptions.push(
      vscode.commands.registerCommand(command, async () => {
        if (busy) return { ok: false, code: "CLIENT_BUSY" };
        busy = true;
        lastError = null;
        try {
          return {
            ok: true,
            data: await handler(command.slice("iacode.".length)),
          };
        } catch (error) {
          lastError = {
            code:
              error instanceof DesktopClientError
                ? error.code
                : "CLIENT_OPERATION_FAILED",
            uncertain: Boolean(error.uncertain),
            requestId: error.requestId,
            idempotencyKey: error.idempotencyKey,
          };
          if (error.uncertain || !client?.connected) stale = true;
          render();
          void vscode.window.showErrorMessage(
            `IACode: ${lastError.code}. ${lastError.uncertain ? "Outcome uncertain; use read-only reconciliation." : "No automatic retry was performed."}`,
          );
          return { ok: false, ...lastError };
        } finally {
          busy = false;
        }
      }),
    );
  context.subscriptions.push(
    status,
    changed,
    viewChanged,
    vscode.workspace.registerTextDocumentContentProvider(
      "iacode-view",
      viewProvider,
    ),
    vscode.window.registerTreeDataProvider("iacode.status", provider),
    vscode.workspace.onDidChangeWorkspaceFolders(invalidate),
    vscode.workspace.onDidGrantWorkspaceTrust(invalidate),
    context.secrets.onDidChange((event) => {
      if (event.key !== CONFIG) return;
      void context.secrets
        .get(CONFIG)
        .then((value) => {
          if (!value || hash(value) !== configurationDigest) invalidate();
        })
        .catch(() => {
          lastError = { code: "CREDENTIAL_STATE_UNAVAILABLE" };
          invalidate();
        });
    }),
    new vscode.Disposable(() => {
      disposed = true;
      views.clear();
      invalidate();
    }),
  );
  render();
  return Object.freeze({
    // Explicit operator configuration only. Never reads workspace settings/environment and never
    // approves, uploads or starts work. External integration must invoke the native commands.
    configureConnection,
    getState: () =>
      structuredClone({
        connected: Boolean(client?.connected),
        stale,
        busy,
        awaiting,
        taskState,
        qualityState,
        lifecycle,
        lastError,
        trusted: vscode.workspace.isTrusted,
      }),
  });
}

module.exports = { activate };
