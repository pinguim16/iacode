"use strict";

// Developer/quality-sandbox runner. Never used by the production CLI. The whole suite is fixed;
// Jest's historical serial flag is translated to Node's equivalent, not used to select cases.
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const { spawnSync } = require("node:child_process");
if (process.argv.slice(2).some((arg) => arg !== "--runInBand"))
  throw new Error("unsupported test option");
const root = path.resolve(__dirname, "..");
const temporary = fs.mkdtempSync(path.join(os.tmpdir(), "iacode-cli-test-"));
try {
  fs.cpSync(path.join(root, "src"), path.join(temporary, "src"), {
    recursive: true,
  });
  fs.cpSync(path.join(root, "bin"), path.join(temporary, "bin"), {
    recursive: true,
  });
  const contract = path.join(temporary, "src/desktop_protocol.json");
  if (!fs.existsSync(contract))
    fs.copyFileSync(
      path.resolve(
        root,
        "../../packages/contracts/src/iacode_contracts/desktop_protocol.json",
      ),
      contract,
    );
  const tests = fs
    .readdirSync(path.join(root, "tests"))
    .filter((file) => file.endsWith(".test.cjs"))
    .sort();
  const result = spawnSync(
    process.execPath,
    [
      "--test",
      "--test-concurrency=1",
      ...tests.map((file) => path.join(root, "tests", file)),
    ],
    {
      stdio: "inherit",
      env: {
        ...process.env,
        IACODE_CLIENT_MODULE: path.join(temporary, "src/client.cjs"),
        IACODE_CLI_ENTRY: path.join(temporary, "bin/iacode.cjs"),
      },
    },
  );
  if (result.error) throw result.error;
  process.exitCode = result.status ?? 1;
} finally {
  fs.rmSync(temporary, { recursive: true, force: true });
}
