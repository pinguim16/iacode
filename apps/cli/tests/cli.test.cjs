"use strict";

const test = require("node:test");
const assert = require("node:assert/strict");
const { spawnSync } = require("node:child_process");
const path = require("node:path");
const fs = require("node:fs");
const os = require("node:os");
const crypto = require("node:crypto");
const entry =
  process.env.IACODE_CLI_ENTRY || path.resolve(__dirname, "../bin/iacode.cjs");
function cli(args, environment = {}) {
  return spawnSync(process.execPath, [entry, ...args], {
    encoding: "utf8",
    timeout: 10000,
    env: {
      ...process.env,
      IACODE_DESKTOP_ENDPOINT: "",
      IACODE_DESKTOP_TOKEN: "",
      ...environment,
    },
  });
}
test("DesktopCliTests: discoverable help and stable identifiers need no configured runtime", () => {
  const help = cli(["help"]);
  assert.equal(help.status, 0, help.stderr);
  assert.ok(JSON.parse(help.stdout).commands["quality-reproduce"]);
  const one = JSON.parse(cli(["new-id"]).stdout).requestId;
  const two = JSON.parse(cli(["new-id"]).stdout).requestId;
  assert.match(one, /^[a-f0-9-]{36}$/);
  assert.notEqual(one, two);
});
test("DesktopCliTests: usage, duplicate, missing, credential argv and insecure endpoint refuse locally", () => {
  for (const args of [
    ["invented"],
    ["list", "--limit", "-1"],
    ["read", "--run-id"],
    ["list", "--limit", "1", "--limit", "2"],
    ["doctor", "--token", "never-on-argv"],
    ["doctor", "--endpoint", "http://example.com:8000"],
  ]) {
    const result = cli(args);
    assert.equal(result.status, 2, result.stderr);
    assert.equal(JSON.parse(result.stderr).uncertain, false);
  }
});
test("DesktopCliTests: no approval causes no attempted domain mutation", () => {
  const result = cli(
    [
      "cancel",
      "--endpoint",
      "http://127.0.0.1:1",
      "--run-id",
      "00000000-0000-0000-0000-000000000000",
    ],
    { IACODE_DESKTOP_TOKEN: "1".repeat(64) },
  );
  assert.equal(result.status, 2);
  assert.equal(JSON.parse(result.stderr).code, "APPROVAL_REQUIRED");
  assert.ok(!result.stderr.includes("1".repeat(64)));
});
test("DesktopCliTests: connection failure is bounded, typed and never prints its credential", () => {
  const result = cli(["doctor", "--endpoint", "http://127.0.0.1:1"], {
    IACODE_DESKTOP_TOKEN: "2".repeat(64),
  });
  assert.equal(result.status, 5);
  assert.equal(JSON.parse(result.stderr).code, "TRANSPORT_UNAVAILABLE");
  assert.ok(!result.stderr.includes("2".repeat(64)));
});

test("DesktopCliTests: offline previews refuse known capability data in inventory names", () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "iacode-cli-preview-"));
  const key = crypto
    .createHash("sha256")
    .update("explicit preview boundary fixture")
    .digest("hex");
  const encoded = Buffer.from(key).toString("hex");
  try {
    fs.writeFileSync(path.join(root, encoded + ".txt"), "clean source");
    const result = cli(["preview", "--root", root], {
      IACODE_DESKTOP_TOKEN: key,
    });
    assert.equal(result.status, 5);
    assert.equal(JSON.parse(result.stdout).code, "PROTECTED_OUTPUT_REFUSED");
    assert.ok(!result.stdout.includes(key) && !result.stdout.includes(encoded));
  } finally {
    fs.rmSync(root, { recursive: true, force: true });
  }
});
