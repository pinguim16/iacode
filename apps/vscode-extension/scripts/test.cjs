"use strict";

// Complete Node decision suite inside an owned capsule, not a native-editor substitute.
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const { spawnSync } = require("node:child_process");
if (process.argv.slice(2).some((arg) => arg !== "--runInBand"))
  throw new Error("unsupported test option");
const root = path.resolve(__dirname, "..");
const temporary = fs.mkdtempSync(path.join(os.tmpdir(), "iacode-editor-test-"));
try {
  const source = path.join(temporary, "src");
  fs.mkdirSync(path.join(source, "core"), { recursive: true });
  fs.copyFileSync(
    path.join(root, "src/extension.cjs"),
    path.join(source, "extension.cjs"),
  );
  fs.copyFileSync(
    path.join(root, "package.json"),
    path.join(temporary, "package.json"),
  );
  for (const name of ["client.cjs", "snapshot.cjs"])
    fs.copyFileSync(
      path.resolve(root, "../cli/src", name),
      path.join(source, "core", name),
    );
  fs.copyFileSync(
    path.resolve(
      root,
      "../../packages/contracts/src/iacode_contracts/desktop_protocol.json",
    ),
    path.join(source, "core/desktop_protocol.json"),
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
        IACODE_EXTENSION_MODULE: path.join(source, "extension.cjs"),
      },
    },
  );
  if (result.error) throw result.error;
  process.exitCode = result.status ?? 1;
} finally {
  fs.rmSync(temporary, { recursive: true, force: true });
}
