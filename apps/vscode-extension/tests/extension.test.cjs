"use strict";

// Public VS Code API decision doubles, not extension-host, installation or live-runtime evidence.
// The production module has no test mode, approval hook, fake transport or environment bypass.
const test = require("node:test");
const assert = require("node:assert/strict");
const Module = require("node:module");
const fs = require("node:fs/promises");
const os = require("node:os");
const path = require("node:path");
const source =
  process.env.IACODE_EXTENSION_MODULE ||
  path.resolve(__dirname, "../src/extension.cjs");
const core = require(path.join(path.dirname(source), "core/client.cjs"));
const snapshots = require(path.join(path.dirname(source), "core/snapshot.cjs"));
const { inventoryDigest } = snapshots;
const fixtureKey = core.hash("explicit editor API decision fixture");
const runId = "11111111-1111-4111-8111-111111111111";
const snapshotId = "22222222-2222-4222-8222-222222222222";

async function fixture() {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), "iacode-editor-unit-"));
  await fs.writeFile(path.join(root, "main.py"), 'print("clean fixture")\n');
  const state = {
    calls: [],
    documents: [],
    picks: [],
    inputs: [],
    callbacks: [],
    closed: 0,
    saves: [],
    configured: new Map(),
    storage: {},
    connectFailure: false,
    candidates: [],
    showsAfterDispose: 0,
  };
  const commands = new Map();
  class Disposable {
    constructor(close = () => {}) {
      this.close = close;
    }
    dispose() {
      this.close();
    }
  }
  class EventEmitter extends Disposable {
    event() {
      return new Disposable();
    }
    fire() {}
  }
  const uri = {
    scheme: "file",
    fsPath: root,
    toString: () => `file://${root}`,
  };
  const vscode = {
    Uri: {
      parse: (value) => ({ scheme: "iacode-view", toString: () => value }),
    },
    languages: {
      async setTextDocumentLanguage(document, language) {
        document.language = language;
        return document;
      },
    },
    Disposable,
    EventEmitter,
    TreeItem: class {
      constructor(label) {
        this.label = label;
      }
    },
    StatusBarAlignment: { Left: 1 },
    commands: {
      registerCommand(name, handler) {
        commands.set(name, handler);
        return new Disposable(() => commands.delete(name));
      },
    },
    workspace: {
      isTrusted: true,
      workspaceFolders: [{ uri }],
      onDidChangeWorkspaceFolders(callback) {
        state.callbacks.push(callback);
        return new Disposable();
      },
      onDidGrantWorkspaceTrust(callback) {
        state.callbacks.push(callback);
        return new Disposable();
      },
      async openTextDocument(value) {
        const document = {
          language: "plaintext",
          uri: value,
          content: state.viewProvider.provideTextDocumentContent(value),
          isDirty: false,
        };
        state.documents.push(document);
        return document;
      },
      registerTextDocumentContentProvider(scheme, provider) {
        assert.equal(scheme, "iacode-view");
        state.viewProvider = provider;
        return new Disposable();
      },
    },
    window: {
      activeTextEditor: null,
      createStatusBarItem: () => {
        let disposed = false;
        return {
          show() {
            if (disposed) state.showsAfterDispose += 1;
          },
          dispose() {
            disposed = true;
          },
        };
      },
      registerTreeDataProvider: () => new Disposable(),
      async showTextDocument() {},
      async showQuickPick(items) {
        const item = state.picks.shift();
        return typeof item === "function" ? item(items) : items[item ?? 0];
      },
      async showInputBox() {
        return state.inputs.shift();
      },
      async showErrorMessage() {},
    },
  };
  class DecisionClient {
    constructor(address, key) {
      this.baseUrl = core.endpoint(address);
      if (key !== fixtureKey)
        throw new core.DesktopClientError(
          "CREDENTIAL_INVALID",
          "decision credential refused",
        );
      this.connected = false;
      state.candidates.push(this);
    }
    async connect() {
      if (state.connectHook) await state.connectHook();
      if (state.connectFailure)
        throw new core.DesktopClientError(
          "TRANSPORT_UNAVAILABLE",
          "decision offline",
        );
      this.connected = true;
    }
    intent(operation, args) {
      return core.hash(JSON.stringify({ operation, args }));
    }
    assertSafeData(value) {
      assert.ok(
        !JSON.stringify(value).includes(fixtureKey),
        "the production core separately tests protected data refusal",
      );
    }
    async execute(operation, args, options = {}) {
      state.calls.push({ operation, args, options });
      if (operation === "read" && state.readHook) await state.readHook();
      if (state.refusal && core.protocol.mutations.includes(operation)) {
        throw new core.DesktopClientError(
          "RESPONSE_CONTRACT_INVALID",
          "decision uncertain response",
          {
            uncertain: true,
            requestId: runId,
            idempotencyKey: args.idempotencyKey,
          },
        );
      }
      if (operation === "snapshot")
        return {
          snapshotId,
          snapshotDigest: core.hash("archive"),
          manifestDigest: args.manifestDigest,
        };
      if (operation === "teams")
        return [{ team: "coding", name: "Coding", enabled: true }];
      if (operation === "start") return { runId, state: "QUEUED" };
      if (operation === "lookup")
        return {
          found: state.found !== false,
          runId: state.lookupRunId || runId,
          state: "RUNNING",
        };
      if (operation === "list")
        return { runs: [{ runId, state: "RUNNING" }], total: 1 };
      if (operation === "quality-start")
        return { runId: "quality-fixture", state: "QUEUED" };
      if (operation === "quality-events")
        return {
          events: [{ sequence: args.after + 1, eventType: "CHECK" }],
          nextCursor: args.after + 1,
        };
      if (operation === "read")
        return {
          runId: args.runId,
          state: "RUNNING",
          result: "<script>untrusted</script>\u001b[31m",
        };
      if (operation === "events")
        return {
          events: [{ sequence: args.after + 1, type: "ACTUAL_EVENT" }],
          nextCursor: args.after + 1,
        };
      return { runId: args.runId, state: "CANCEL_REQUESTED" };
    }
    dispose() {
      this.connected = false;
      state.closed += 1;
    }
  }
  const context = {
    subscriptions: [],
    extension: {
      packageJSON: require(
        path.resolve(path.dirname(source), "../package.json"),
      ),
    },
    workspaceState: {
      get: () => ({}),
      async update(name, value) {
        state.saves.push(structuredClone(value));
        state.storage[name] = structuredClone(value);
      },
    },
    secrets: {
      async get(name) {
        return state.configured.get(name);
      },
      async store(name, value) {
        state.configured.set(name, value);
      },
      onDidChange: () => new Disposable(),
    },
  };
  const load = Module._load;
  delete require.cache[require.resolve(source)];
  try {
    Module._load = function (name, ...args) {
      if (name === "vscode") return vscode;
      if (name === "./core/client.cjs")
        return { ...core, DesktopClient: DecisionClient };
      if (name === "./core/snapshot.cjs")
        return {
          ...snapshots,
          preview: async (root) => {
            const result = await snapshots.preview(root);
            // Model a filesystem's canonical spelling differing from the editor-selected spelling.
            if (state.canonicalRootAlias)
              result.root = result.root.toUpperCase();
            return result;
          },
        };
      return load.call(this, name, ...args);
    };
    state.api = require(source).activate(context);
  } finally {
    Module._load = load;
  }
  await state.api.configureConnection("http://127.0.0.1:18080", fixtureKey);
  return {
    ...state,
    state,
    root,
    vscode,
    context,
    api: state.api,
    command: (name, ...args) => commands.get(`iacode.${name}`)(...args),
    async snapshot() {
      assert.equal((await commands.get("iacode.preview")()).ok, true);
      state.picks.push(1);
      return commands.get("iacode.snapshot")();
    },
    async close() {
      for (const disposable of context.subscriptions) disposable.dispose();
      await fs.rm(root, { recursive: true, force: true });
    },
  };
}

test("DesktopSnapshotTests: canonical filesystem spelling is bound to the selected workspace identity", async () => {
  const f = await fixture();
  try {
    f.state.canonicalRootAlias = true;
    const result = await f.snapshot();
    assert.equal(result.ok, true, JSON.stringify(result));
    assert.equal(
      f.state.calls.filter((call) => call.operation === "snapshot").length,
      1,
    );
  } finally {
    await f.close();
  }
});

test("DesktopWorkspaceTrustTests: untrusted, multi-root and virtual mutations refuse before reads or network", async () => {
  const f = await fixture();
  try {
    f.vscode.workspace.isTrusted = false;
    assert.equal((await f.command("snapshot")).code, "WORKSPACE_UNTRUSTED");
    f.vscode.workspace.isTrusted = true;
    f.vscode.workspace.workspaceFolders.push(
      f.vscode.workspace.workspaceFolders[0],
    );
    assert.equal((await f.command("start")).code, "WORKSPACE_UNSUPPORTED");
    f.vscode.workspace.workspaceFolders.pop();
    f.vscode.workspace.workspaceFolders[0].uri.scheme = "virtual";
    assert.equal(
      (await f.command("qualityStart")).code,
      "WORKSPACE_UNSUPPORTED",
    );
    assert.equal(f.state.calls.length, 0);
  } finally {
    await f.close();
  }
});
test("DesktopApprovalTests: command arguments cannot approve; default Cancel has zero mutations", async () => {
  const f = await fixture();
  try {
    assert.equal((await f.command("preview")).ok, true);
    assert.equal(
      (await f.command("snapshot", { approve: true })).code,
      "APPROVAL_CANCELLED",
    );
    assert.equal(f.state.calls.length, 0);
    assert.equal(f.api.getState().lifecycle.pending, undefined);
  } finally {
    await f.close();
  }
});
test("DesktopApprovalTests: folder/trust invalidation after review cannot send a stale approval", async () => {
  const f = await fixture();
  try {
    await f.command("preview");
    f.state.picks.push((items) => {
      f.state.callbacks[0]();
      return items[1];
    });
    assert.equal((await f.command("snapshot")).code, "STALE_APPROVAL");
    assert.equal(f.state.calls.length, 0);
  } finally {
    await f.close();
  }
});
test("DesktopSnapshotTests: changed bytes require a new preview, and confirmed upload records only metadata", async () => {
  const f = await fixture();
  try {
    await f.command("preview");
    await fs.writeFile(path.join(f.root, "main.py"), "changed\n");
    assert.equal((await f.command("snapshot")).code, "WORKSPACE_CHANGED");
    assert.equal(f.state.calls.length, 0);
    const result = await f.snapshot();
    assert.equal(result.ok, true);
    assert.equal(f.state.calls[0].operation, "snapshot");
    assert.equal(
      f.state.calls[0].args.manifestDigest,
      inventoryDigest(f.state.calls[0].args.files),
    );
    const saved = JSON.stringify(f.state.saves);
    assert.ok(!saved.includes("changed\\n"));
    assert.ok(!saved.includes(fixtureKey));
  } finally {
    await f.close();
  }
});
test("DesktopRecoveryTests: uncertain create retains stable identity before IO and reconciles without mutation replay", async () => {
  const f = await fixture();
  try {
    await f.snapshot();
    f.state.inputs.push("Do the bounded task");
    f.state.picks.push(0, 1);
    f.state.refusal = true;
    const result = await f.command("start");
    assert.equal(result.ok, false);
    assert.equal(result.uncertain, true);
    const pending = f.api.getState().lifecycle.pending;
    assert.equal(pending.operation, "start");
    assert.equal(result.idempotencyKey, pending.idempotencyKey);
    assert.ok(!JSON.stringify(f.state.saves).includes("Do the bounded task"));
    f.state.found = false;
    assert.equal((await f.command("recover")).data.found, false);
    assert.deepEqual(f.api.getState().lifecycle.pending, pending);
    f.state.found = true;
    assert.equal((await f.command("recover")).data.found, true);
    assert.equal(f.api.getState().lifecycle.pending, null);
    assert.equal(
      f.state.calls.filter((call) => call.operation === "start").length,
      1,
    );
  } finally {
    await f.close();
  }
});
test("DesktopPresentationTests: runtime content stays plaintext; event pages resume and disconnect is not remote cancellation", async () => {
  const f = await fixture();
  try {
    await f.snapshot();
    f.state.inputs.push("bounded task");
    f.state.picks.push(0, 1);
    assert.equal((await f.command("start")).ok, true);
    await f.command("read");
    assert.ok(f.state.documents.every((doc) => doc.language === "plaintext"));
    assert.ok(
      f.state.documents.at(-1).content.includes("<script>untrusted</script>"),
    );
    assert.ok(!f.state.documents.at(-1).content.includes("\u001b"));
    assert.equal((await f.command("events")).data.nextCursor, 1);
    assert.equal((await f.command("events")).data.nextCursor, 2);
    assert.equal(
      f.state.calls.filter((call) => call.operation === "events")[1].args.after,
      1,
    );
    assert.equal(
      (await f.command("disconnect")).data.remoteCancellationRequested,
      false,
    );
    assert.equal(f.api.getState().stale, true);
    assert.equal(
      f.state.calls.filter((call) => call.operation === "cancel").length,
      0,
    );
  } finally {
    await f.close();
  }
});
test("DesktopCredentialTests: only explicit operator configuration uses SecretStorage, never workspace state", async () => {
  const f = await fixture();
  try {
    assert.equal(f.state.configured.size, 1);
    assert.ok([...f.state.configured.values()][0].includes(fixtureKey));
    assert.ok(!JSON.stringify(f.state.saves).includes(fixtureKey));
    const prior = f.api.getState().connected;
    f.state.connectFailure = true;
    await assert.rejects(
      f.api.configureConnection("http://127.0.0.1:18081", fixtureKey),
    );
    assert.equal(f.api.getState().connected, prior);
  } finally {
    await f.close();
  }
});

test("DesktopLifecycleTests: disposal during connection cannot revive a candidate or render disposed UI", async () => {
  const f = await fixture();
  let release;
  try {
    f.state.connectHook = () =>
      new Promise((resolve) => {
        release = resolve;
      });
    const connecting = f.api.configureConnection(
      "http://127.0.0.1:18081",
      fixtureKey,
    );
    await new Promise((resolve) => setImmediate(resolve));
    await assert.rejects(
      f.api.configureConnection("http://127.0.0.1:18082", fixtureKey),
      { code: "CLIENT_BUSY" },
    );
    await f.close();
    release();
    await assert.rejects(connecting, { code: "STALE_CONNECTION" });
    assert.equal(f.api.getState().connected, false);
    assert.ok(f.state.candidates.every((candidate) => !candidate.connected));
    assert.equal(f.state.showsAfterDispose, 0);
  } finally {
    await f.close();
  }
});

test("DesktopPresentationTests: a late read cannot relabel an invalidated connection as fresh", async () => {
  const f = await fixture();
  let release;
  try {
    assert.equal((await f.command("select")).ok, true);
    f.state.readHook = () =>
      new Promise((resolve) => {
        release = resolve;
      });
    const reading = f.command("read");
    await new Promise((resolve) => setImmediate(resolve));
    f.state.callbacks[0]();
    release();
    assert.equal((await reading).code, "STALE_CONNECTION");
    assert.equal(f.api.getState().stale, true);
    assert.equal(f.api.getState().connected, false);
  } finally {
    await f.close();
  }
});

test("DesktopRecoveryTests: changing endpoints cannot erase an uncertain identity", async () => {
  const f = await fixture();
  try {
    await f.snapshot();
    f.state.inputs.push("bounded task");
    f.state.picks.push(0, 1);
    f.state.refusal = true;
    assert.equal((await f.command("start")).uncertain, true);
    const before = f.api.getState().lifecycle;
    const created = f.state.candidates.length;
    await assert.rejects(
      f.api.configureConnection("http://127.0.0.1:18081", fixtureKey),
      { code: "RECOVERY_ENDPOINT_MISMATCH" },
    );
    assert.deepEqual(f.api.getState().lifecycle, before);
    assert.equal(f.state.candidates.length, created);
  } finally {
    await f.close();
  }
});

test("DesktopLifecycleTests: selecting and cancelling existing work needs no upload and preserves same-run cursors", async () => {
  const f = await fixture();
  try {
    assert.equal((await f.command("select")).ok, true);
    await f.command("events");
    await f.command("events");
    f.state.picks.push(1);
    assert.equal((await f.command("cancel")).ok, true);
    assert.equal(f.api.getState().lifecycle.runCursor, 2);
    assert.equal((await f.command("events")).data.nextCursor, 3);
    assert.equal(
      f.state.calls.filter((call) => call.operation === "snapshot").length,
      0,
    );
    assert.equal(f.api.getState().lifecycle.snapshot, undefined);
  } finally {
    await f.close();
  }
});

test("DesktopRecoveryTests: a recovered different task resets the old cursor but same quality cancellation does not", async () => {
  const f = await fixture();
  try {
    await f.snapshot();
    f.state.inputs.push("first task");
    f.state.picks.push(0, 1);
    assert.equal((await f.command("start")).ok, true);
    await f.command("events");
    await f.command("events");
    f.state.inputs.push("next task");
    f.state.picks.push(0, 1);
    f.state.refusal = true;
    assert.equal((await f.command("start")).uncertain, true);
    f.state.lookupRunId = "33333333-3333-4333-8333-333333333333";
    assert.equal((await f.command("recover")).ok, true);
    assert.equal(f.api.getState().lifecycle.runCursor, 0);
    assert.equal((await f.command("events")).data.nextCursor, 1);
    f.state.refusal = false;
    f.state.picks.push(1);
    assert.equal((await f.command("qualityStart")).ok, true);
    await f.command("qualityEvents");
    await f.command("qualityEvents");
    f.state.picks.push(1);
    assert.equal((await f.command("qualityCancel")).ok, true);
    assert.equal(f.api.getState().lifecycle.qualityCursor, 2);
    const uris = new Set(
      f.state.documents.map((document) => document.uri.toString()),
    );
    assert.ok(uris.size <= 3);
    assert.ok(
      f.state.documents.every(
        (document) =>
          !document.isDirty && document.uri.scheme === "iacode-view",
      ),
    );
  } finally {
    await f.close();
  }
});
