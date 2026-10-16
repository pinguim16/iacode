"use strict";

// Decision/transport tests against an owned real HTTP socket, not a live IACode runtime proof.
const test = require("node:test");
const assert = require("node:assert/strict");
const http = require("node:http");
const crypto = require("node:crypto");
const path = require("node:path");
const fs = require("node:fs/promises");
const os = require("node:os");
const { once } = require("node:events");
const corePath =
  process.env.IACODE_CLIENT_MODULE ||
  path.resolve(__dirname, "../src/client.cjs");
const {
  DesktopClient,
  protocol,
  protocolDigest,
  endpoint,
  validate,
  hash,
  mac,
} = require(corePath);
const { preview, inventoryDigest, safePath } = require(
  path.join(path.dirname(corePath), "snapshot.cjs"),
);
const credential = hash(
  "deterministic transport unit fixture, not an operational credential",
);

async function serverFixture(mode = "valid") {
  const state = { requests: 0, mutations: 0, requestIds: [], observed: [] };
  const server = http.createServer(async (req, res) => {
    const parts = [];
    for await (const part of req) parts.push(part);
    const body = Buffer.concat(parts);
    const requestId = req.headers[protocol.headers.requestId.toLowerCase()];
    const timestamp = req.headers[protocol.headers.timestamp.toLowerCase()];
    const expected = mac(
      credential,
      [
        protocol.version,
        requestId,
        timestamp,
        req.method,
        req.url,
        hash(body),
      ].join("\n"),
    );
    assert.equal(
      req.headers[protocol.headers.signature.toLowerCase()],
      expected,
    );
    assert.ok(!Object.values(req.headers).includes(credential));
    const value = JSON.parse(body);
    assert.equal(value.requestId, requestId);
    state.requests += 1;
    state.requestIds.push(requestId);
    state.observed.push(value);
    if (protocol.mutations.includes(value.operation)) state.mutations += 1;
    if (mode === "timeout" && value.operation === "start") return;
    const hello = {
      authenticated: true,
      protocolDigest,
      expiresAt: new Date(Date.now() + 3600000).toISOString(),
      operations: Object.keys(protocol.operations),
      runStates: ["QUEUED", "RUNNING", "SUCCEEDED", "CANCELLED"],
      terminalRunStates: ["SUCCEEDED", "CANCELLED"],
      qualityStates: ["QUEUED", "SUCCEEDED", "CANCELLED"],
      terminalQualityStates: ["SUCCEEDED", "CANCELLED"],
    };
    let data = hello;
    if (value.operation === "start")
      data = {
        runId: crypto.randomUUID(),
        state: mode === "bad-start" ? "INVENTED_SUCCESS" : "QUEUED",
      };
    if (value.operation === "read")
      data = {
        runId: value.arguments.runId,
        state: mode === "bad-state" ? "INVENTED_SUCCESS" : "RUNNING",
      };
    if (value.operation === "events")
      data = {
        events: [{ sequence: value.arguments.after + 1, type: "RUN_QUEUED" }],
        nextCursor: value.arguments.after + 1,
      };
    if (mode === "bad-cursor" && value.operation === "events")
      data.nextCursor += 100;
    let response = Buffer.from(
      JSON.stringify({
        version: protocol.version,
        requestId,
        operation: value.operation,
        data,
      }),
    );
    if (value.operation === "start" && mode === "deep-json")
      response = Buffer.from(
        '{"data":' + "[".repeat(20000) + "0" + "]".repeat(20000) + "}",
      );
    if (value.operation === "start" && mode === "reflected-key")
      response = Buffer.from(
        JSON.stringify({ data: Buffer.from(credential).toString("base64") }),
      );
    const status =
      mode === "redirect"
        ? 302
        : value.operation === "start" &&
            ["refused", "unknown-refusal"].includes(mode)
          ? 400
          : 200;
    if (
      value.operation === "start" &&
      ["refused", "unknown-refusal"].includes(mode)
    ) {
      response = Buffer.from(
        JSON.stringify({
          code:
            mode === "refused"
              ? "SNAPSHOT_NOT_AUTHORISED"
              : "UNDECLARED_REFUSAL",
        }),
      );
    }
    const signature = mac(
      credential,
      [protocol.version, requestId, String(status), hash(response)].join("\n"),
    );
    res.writeHead(status, {
      "Content-Type": "application/json",
      [protocol.headers.signature]:
        mode === "unsigned" ? "0".repeat(64) : signature,
      ...(mode === "redirect"
        ? { Location: "http://127.0.0.1:1/forbidden" }
        : {}),
    });
    if (mode === "tamper")
      response = Buffer.concat([response, Buffer.from(" ")]);
    res.end(response);
  });
  server.listen(0, "127.0.0.1");
  await once(server, "listening");
  const client = new DesktopClient(
    `http://127.0.0.1:${server.address().port}`,
    credential,
  );
  return {
    client,
    state,
    async close() {
      client.dispose();
      server.closeAllConnections();
      await new Promise((resolve, reject) =>
        server.close((error) => (error ? reject(error) : resolve())),
      );
    },
  };
}

test("DesktopTransportTests: only explicit canonical loopback endpoints are accepted", () => {
  assert.equal(endpoint("http://127.0.0.1:18080"), "http://127.0.0.1:18080");
  for (const value of [
    "http://localhost:18080",
    "http://2130706433:18080",
    "http://0x7f000001:18080",
    "http://127.0.0.1:18080/api",
    "http://user:password@127.0.0.1:18080",
    "https://127.0.0.1:18080",
    "http://example.com:18080",
    "http://127.0.0.1:18080?target=x",
    "http://127.0.0.1:18080#x",
  ]) {
    assert.throws(
      () => endpoint(value),
      (error) => error.code.startsWith("ENDPOINT_"),
    );
  }
});

test("DesktopContractTests: wrong type, missing value and invalid value stay distinct", () => {
  const schema = protocol.operations.events;
  for (const [value, code] of [
    [{}, "FIELD_MISSING"],
    [{ runId: 1, after: 0 }, "FIELD_TYPE_INVALID"],
    [{ runId: "bad", after: 0 }, "FIELD_VALUE_INVALID"],
    [{ runId: crypto.randomUUID(), after: true }, "FIELD_TYPE_INVALID"],
  ]) {
    assert.throws(
      () => validate(value, schema),
      (error) => error.code === code,
    );
  }
  assert.throws(() =>
    validate({ runId: `${crypto.randomUUID()}\n`, after: 0 }, schema),
  );
});

test("DesktopContractTests: callers cannot mutate the canonical limits or operation schemas", () => {
  assert.throws(() => {
    protocol.maxResponseBytes = Number.MAX_SAFE_INTEGER;
  }, TypeError);
  assert.throws(() => {
    protocol.operations.events.properties.after.maximum =
      Number.MAX_SAFE_INTEGER;
  }, TypeError);
});

test("DesktopTransportTests: real request and response authentication preserve exact bytes", async () => {
  const fixture = await serverFixture();
  try {
    const hello = await fixture.client.connect();
    assert.equal(hello.protocolDigest, protocolDigest);
    assert.equal(fixture.client.connected, true);
    const id = crypto.randomUUID();
    const result = await fixture.client.execute("read", { runId: id });
    assert.equal(result.runId, id);
    assert.equal(result.state, "RUNNING");
    assert.equal(fixture.state.requests, 2);
    assert.notEqual(fixture.state.requestIds[0], fixture.state.requestIds[1]);
  } finally {
    await fixture.close();
  }
});

test("DesktopTransportTests: altered or unsigned responses cannot create a session", async () => {
  for (const mode of ["unsigned", "tamper"]) {
    const fixture = await serverFixture(mode);
    try {
      await assert.rejects(
        fixture.client.connect(),
        (error) => error.code === "RESPONSE_AUTHENTICATION_INVALID",
      );
      assert.equal(fixture.client.connected, false);
      assert.equal(fixture.state.mutations, 0);
    } finally {
      await fixture.close();
    }
  }
});

test("DesktopTransportTests: redirects are never followed", async () => {
  const fixture = await serverFixture("redirect");
  try {
    await assert.rejects(
      fixture.client.connect(),
      (error) => error.code === "REMOTE_ERROR",
    );
    assert.equal(fixture.state.requests, 1);
  } finally {
    await fixture.close();
  }
});

test("DesktopApprovalTests: approval binds exact target and current connection", async () => {
  const fixture = await serverFixture();
  try {
    await fixture.client.connect();
    const args = {
      snapshotId: crypto.randomUUID(),
      task: "A bounded approved unit task",
      team: "coding",
      idempotencyKey: crypto.randomUUID(),
    };
    await assert.rejects(
      fixture.client.execute("start", args),
      (error) => error.code === "APPROVAL_REQUIRED",
    );
    const approved = fixture.client.intent("start", args);
    await assert.rejects(
      fixture.client.execute(
        "start",
        { ...args, task: "Changed target" },
        { approval: approved },
      ),
      (error) => error.code === "APPROVAL_REQUIRED",
    );
    assert.equal(fixture.state.mutations, 0);
    const result = await fixture.client.execute("start", args, {
      approval: approved,
    });
    assert.equal(result.state, "QUEUED");
    await fixture.client.connect();
    await assert.rejects(
      fixture.client.execute("start", args, { approval: approved }),
      (error) => error.code === "APPROVAL_REQUIRED",
    );
    assert.equal(fixture.state.mutations, 1);
  } finally {
    await fixture.close();
  }
});

test("DesktopPresentationTests: unknown success states invalidate the view", async () => {
  const fixture = await serverFixture("bad-state");
  try {
    await fixture.client.connect();
    await assert.rejects(
      fixture.client.execute("read", { runId: crypto.randomUUID() }),
      (error) => error.code === "RESPONSE_CONTRACT_INVALID",
    );
    assert.equal(fixture.client.connected, false);
  } finally {
    await fixture.close();
  }
});

test("DesktopRecoveryTests: a signed malformed mutation result retains uncertain outcome and retry identity", async () => {
  const fixture = await serverFixture("bad-start");
  try {
    await fixture.client.connect();
    const args = {
      snapshotId: crypto.randomUUID(),
      task: "Mutation result validation fixture",
      team: "coding",
      idempotencyKey: crypto.randomUUID(),
    };
    await assert.rejects(
      fixture.client.execute("start", args, {
        approval: fixture.client.intent("start", args),
      }),
      (error) =>
        error.code === "RESPONSE_CONTRACT_INVALID" &&
        error.uncertain === true &&
        error.idempotencyKey === args.idempotencyKey,
    );
    assert.equal(fixture.state.mutations, 1);
    assert.equal(fixture.client.connected, false);
  } finally {
    await fixture.close();
  }
});

test("DesktopRecoveryTests: only authenticated declared pre-effect refusals clear mutation uncertainty", async () => {
  for (const [mode, uncertain] of [
    ["refused", false],
    ["unknown-refusal", true],
  ]) {
    const fixture = await serverFixture(mode);
    try {
      await fixture.client.connect();
      const args = {
        snapshotId: crypto.randomUUID(),
        task: "fixture",
        team: "coding",
        idempotencyKey: crypto.randomUUID(),
      };
      await assert.rejects(
        fixture.client.execute("start", args, {
          approval: fixture.client.intent("start", args),
        }),
        (error) =>
          error.uncertain === uncertain &&
          error.idempotencyKey === args.idempotencyKey,
      );
      assert.equal(fixture.state.mutations, 1);
    } finally {
      await fixture.close();
    }
  }
});

test("DesktopEventTests: cursor must equal the last ordered actual event", async () => {
  const clean = await serverFixture();
  try {
    const page = await clean.client.execute("events", {
      runId: crypto.randomUUID(),
      after: 6,
    });
    assert.equal(page.nextCursor, 7);
    assert.equal(page.events[0].sequence, 7);
  } finally {
    await clean.close();
  }
  const adverse = await serverFixture("bad-cursor");
  try {
    await assert.rejects(
      adverse.client.execute("events", {
        runId: crypto.randomUUID(),
        after: 6,
      }),
      (error) => error.code === "RESPONSE_CONTRACT_INVALID",
    );
  } finally {
    await adverse.close();
  }
});

test("DesktopRecoveryTests: a real deadline reports uncertainty without retry or remote cancellation", async () => {
  const fixture = await serverFixture("timeout");
  try {
    await fixture.client.connect();
    const args = {
      snapshotId: crypto.randomUUID(),
      task: "Intentional timeout decision fixture",
      team: "coding",
      idempotencyKey: crypto.randomUUID(),
    };
    await assert.rejects(
      fixture.client.execute("start", args, {
        approval: fixture.client.intent("start", args),
      }),
      (error) =>
        error.code === "TRANSPORT_TIMEOUT" &&
        error.uncertain === true &&
        error.idempotencyKey === args.idempotencyKey,
    );
    assert.equal(fixture.state.mutations, 1);
    assert.equal(fixture.state.requests, 2);
    assert.equal(fixture.client.connected, false);
  } finally {
    await fixture.close();
  }
});

test("DesktopSnapshotTests: preview preserves UTF-8/BOM bytes, excludes private files and uploads nothing", async () => {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), "iacode-preview-"));
  try {
    const bytes = Buffer.from("\ufeffolá\r\n", "utf8");
    await fs.writeFile(path.join(root, "source.txt"), bytes);
    await fs.writeFile(path.join(root, ".env"), "excluded local fixture");
    const result = await preview(root);
    assert.equal(result.files.length, 1);
    assert.equal(result.excludedCount, 1);
    assert.deepEqual(Buffer.from(result.files[0].content), bytes);
    assert.equal(result.manifestDigest, inventoryDigest(result.files));
    assert.equal(result.inventory[0].sha256, hash(bytes));
  } finally {
    await fs.rm(root, { recursive: true, force: true });
  }
});

test("DesktopSnapshotTests: links and nonportable paths are refused", async () => {
  for (const name of [
    ".",
    "..",
    "a//b",
    "/absolute",
    "C:/file",
    "a/NUL.txt",
    "a/file.pem",
    "a/\u202eb",
  ])
    assert.equal(safePath(name), false);
  const root = await fs.mkdtemp(path.join(os.tmpdir(), "iacode-preview-"));
  const outside = await fs.mkdtemp(path.join(os.tmpdir(), "iacode-outside-"));
  try {
    await fs.writeFile(path.join(outside, "source.txt"), "outside fixture");
    await fs.symlink(
      path.join(outside, "source.txt"),
      path.join(root, "source.txt"),
    );
    await assert.rejects(
      preview(root),
      (error) => error.code === "SNAPSHOT_LINK_REFUSED",
    );
  } finally {
    await fs.rm(root, { recursive: true, force: true });
    await fs.rm(outside, { recursive: true, force: true });
  }
});

test("DesktopSnapshotTests: decoded file bytes and even excluded traversal entries remain bounded", async () => {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), "iacode-preview-"));
  try {
    await fs.writeFile(
      path.join(root, "large.txt"),
      Buffer.alloc(protocol.maxFileBytes + 1),
    );
    await assert.rejects(
      preview(root),
      (error) => error.code === "SNAPSHOT_TOO_LARGE",
    );
    await fs.unlink(path.join(root, "large.txt"));
    for (let index = 0; index <= protocol.maxLocalEntries; index += 1) {
      await fs.writeFile(path.join(root, `.env.${index}`), "excluded");
    }
    await assert.rejects(
      preview(root),
      (error) => error.code === "SNAPSHOT_TOO_LARGE",
    );
  } finally {
    await fs.rm(root, { recursive: true, force: true });
  }
});

test("DesktopRecoveryTests: signed deep JSON and protected-data refusals keep one effect and stable uncertainty", async () => {
  for (const mode of ["deep-json", "reflected-key"]) {
    const f = await serverFixture(mode);
    const client = f.client;
    try {
      await client.connect();
      const args = {
        snapshotId: crypto.randomUUID(),
        task: "bounded task",
        team: "coding",
        idempotencyKey: crypto.randomUUID(),
      };
      await assert.rejects(
        client.execute("start", args, {
          approval: client.intent("start", args),
        }),
        (error) =>
          error.code ===
            (mode === "deep-json"
              ? "JSON_COMPLEXITY_REFUSED"
              : "CREDENTIAL_REFLECTION_REFUSED") &&
          error.uncertain &&
          error.idempotencyKey === args.idempotencyKey &&
          !error.message.includes(credential),
      );
      assert.equal(f.state.mutations, 1);
      assert.equal(client.connected, false);
    } finally {
      client.dispose();
      await f.close();
    }
  }
});

test("DesktopCredentialTests: capability values and bounded encoded forms never become operation data", async () => {
  const f = await serverFixture();
  const client = f.client;
  try {
    await client.connect();
    const forms = [
      credential,
      credential.toUpperCase(),
      Buffer.from(credential).toString("base64"),
      Buffer.from(credential).toString("hex"),
      [...Buffer.from(credential)]
        .map((value) => `%${value.toString(16)}`)
        .join(""),
    ];
    for (const task of forms) {
      assert.throws(
        () =>
          client.intent("start", {
            snapshotId: crypto.randomUUID(),
            task,
            team: "coding",
            idempotencyKey: crypto.randomUUID(),
          }),
        { code: "CREDENTIAL_REFLECTION_REFUSED" },
      );
    }
    assert.doesNotThrow(() =>
      client.assertSafeData({ clean: Array(10).fill("bounded") }),
    );
    assert.throws(
      () => client.assertSafeData(Array(protocol.maxJsonNodes + 1).fill(0)),
      { code: "JSON_COMPLEXITY_REFUSED" },
    );
    assert.equal(f.state.requests, 1);
    assert.equal(f.state.mutations, 0);
  } finally {
    client.dispose();
    await f.close();
  }
});
