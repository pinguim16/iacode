"use strict";

// A consent preview reads bounded regular UTF-8 source files only. It executes no workspace
// program and uploads nothing. The authenticated API owns the canonical secret/persistence gate.
const fs = require("node:fs");
const path = require("node:path");
const { DesktopClientError, protocol, hash } = require("./client.cjs");
const { createHash } = require("node:crypto");

function reject(code, message) {
  throw new DesktopClientError(code, message);
}
function excluded(name) {
  const lower = name.toLowerCase();
  return (
    protocol.excludedDirectories.includes(lower) ||
    protocol.excludedNames.includes(lower) ||
    lower.startsWith(".env") ||
    protocol.excludedSuffixes.some((suffix) => lower.endsWith(suffix))
  );
}

function safePath(name) {
  if (
    !name ||
    Buffer.byteLength(name) > 240 ||
    name !== name.normalize("NFC") ||
    path.posix.isAbsolute(name) ||
    /[\\:<>"|?*\p{Cc}\p{Cf}\p{Cs}]/u.test(name)
  )
    return false;
  const parts = name.split("/");
  return parts.every(
    (part) =>
      part &&
      ![".", ".."].includes(part) &&
      !/[. ]$/.test(part) &&
      !excluded(part) &&
      !/^(con|prn|aux|nul|com[1-9]|lpt[1-9])(?:\.|$)/i.test(part),
  );
}

function inventoryDigest(files) {
  const digest = createHash("sha256");
  for (const file of [...files].sort((a, b) =>
    Buffer.compare(Buffer.from(a.path), Buffer.from(b.path)),
  )) {
    const content = Buffer.from(file.content, "utf8");
    digest.update(`${file.path}\0${content.length}:${hash(content)}\n`, "utf8");
  }
  return digest.digest("hex");
}

async function preview(root) {
  if (typeof root !== "string" || root.length === 0)
    reject("WORKSPACE_REQUIRED", "select one explicit local workspace root");
  const selected = path.resolve(root);
  let rootInfo;
  try {
    rootInfo = await fs.promises.lstat(selected);
  } catch {
    reject("WORKSPACE_UNAVAILABLE", "selected workspace root cannot be read");
  }
  if (!rootInfo.isDirectory() || rootInfo.isSymbolicLink())
    reject(
      "WORKSPACE_UNSAFE",
      "workspace root must be a regular directory, not a link",
    );
  const canonicalRoot = await fs.promises.realpath(selected);
  const files = [];
  const names = new Set();
  let total = 0;
  let excludedCount = 0;
  let visited = 0;
  const inside = (candidate) => {
    const relative = path.relative(canonicalRoot, candidate);
    return (
      relative !== ".." &&
      !relative.startsWith(`..${path.sep}`) &&
      !path.isAbsolute(relative)
    );
  };

  async function visit(directory, relativeDirectory) {
    const entries = [];
    const stream = await fs.promises.opendir(directory);
    for await (const entry of stream) {
      visited += 1;
      if (visited > protocol.maxLocalEntries)
        reject(
          "SNAPSHOT_TOO_LARGE",
          "workspace traversal exceeds its entry bound",
        );
      entries.push(entry);
    }
    entries.sort((a, b) =>
      Buffer.compare(Buffer.from(a.name), Buffer.from(b.name)),
    );
    for (const entry of entries) {
      if (excluded(entry.name)) {
        excludedCount += 1;
        continue;
      }
      const relative = relativeDirectory
        ? `${relativeDirectory}/${entry.name}`
        : entry.name;
      if (!safePath(relative))
        reject(
          "SNAPSHOT_PATH_REFUSED",
          "workspace contains an unsafe or nonportable source path",
        );
      const absolute = path.join(directory, entry.name);
      const before = await fs.promises.lstat(absolute);
      if (before.isSymbolicLink())
        reject("SNAPSHOT_LINK_REFUSED", "workspace links are not uploaded");
      const resolved = await fs.promises.realpath(absolute);
      if (!inside(resolved))
        reject(
          "SNAPSHOT_PATH_REFUSED",
          "source path escaped the selected workspace",
        );
      if (before.isDirectory()) {
        await visit(absolute, relative);
        continue;
      }
      if (!before.isFile() || before.nlink !== 1)
        reject(
          "SNAPSHOT_SPECIAL_FILE_REFUSED",
          "only singly linked regular source files are supported",
        );
      if (
        files.length >= protocol.maxFiles ||
        before.size > protocol.maxFileBytes
      )
        reject(
          "SNAPSHOT_TOO_LARGE",
          "workspace exceeds the bounded file inventory",
        );
      const folded = relative.toLowerCase();
      if (names.has(folded))
        reject("SNAPSHOT_PATH_REFUSED", "workspace has case-ambiguous paths");
      names.add(folded);
      const handle = await fs.promises.open(
        absolute,
        fs.constants.O_RDONLY | (fs.constants.O_NOFOLLOW || 0),
      );
      let content;
      try {
        const opened = await handle.stat();
        if (
          !opened.isFile() ||
          opened.nlink !== 1 ||
          opened.ino !== before.ino ||
          opened.dev !== before.dev
        )
          reject("WORKSPACE_CHANGED", "source identity changed during preview");
        const buffer = Buffer.alloc(protocol.maxFileBytes + 1);
        let read = 0;
        while (read < buffer.length) {
          const item = await handle.read(
            buffer,
            read,
            buffer.length - read,
            read,
          );
          if (item.bytesRead === 0) break;
          read += item.bytesRead;
        }
        if (read > protocol.maxFileBytes)
          reject("SNAPSHOT_TOO_LARGE", "source grew beyond its byte bound");
        const after = await handle.stat();
        const current = await fs.promises.lstat(absolute);
        const resolvedAfter = await fs.promises.realpath(absolute);
        if (
          after.ino !== opened.ino ||
          after.dev !== opened.dev ||
          after.size !== read ||
          after.mtimeMs !== opened.mtimeMs ||
          current.isSymbolicLink() ||
          current.ino !== opened.ino ||
          current.dev !== opened.dev ||
          !inside(resolvedAfter) ||
          resolvedAfter !== resolved
        )
          reject(
            "WORKSPACE_CHANGED",
            "source changed during preview; inspect again",
          );
        try {
          content = new TextDecoder("utf-8", {
            fatal: true,
            ignoreBOM: true,
          }).decode(buffer.subarray(0, read));
        } catch {
          reject(
            "SNAPSHOT_BINARY_REFUSED",
            "desktop snapshots support UTF-8 source files only",
          );
        }
        total += Buffer.byteLength(content, "utf8");
        if (total > protocol.maxSnapshotBytes)
          reject(
            "SNAPSHOT_TOO_LARGE",
            "workspace exceeds its decoded byte bound",
          );
      } finally {
        await handle.close();
      }
      files.push({ path: relative, content });
    }
  }

  try {
    await visit(canonicalRoot, "");
  } catch (error) {
    if (error instanceof DesktopClientError) throw error;
    reject(
      "WORKSPACE_READ_FAILED",
      "source could not be read consistently; inspect the workspace again",
    );
  }
  const rootAfter = await fs.promises.lstat(selected);
  if (
    rootAfter.isSymbolicLink() ||
    rootAfter.ino !== rootInfo.ino ||
    rootAfter.dev !== rootInfo.dev ||
    (await fs.promises.realpath(selected)) !== canonicalRoot
  )
    reject("WORKSPACE_CHANGED", "workspace root changed during preview");
  if (!files.length)
    reject("SNAPSHOT_EMPTY", "workspace has no eligible source files");
  return {
    root: canonicalRoot,
    files,
    manifestDigest: inventoryDigest(files),
    inventory: files.map((file) => ({
      path: file.path,
      sizeBytes: Buffer.byteLength(file.content),
      sha256: hash(Buffer.from(file.content)),
    })),
    totalBytes: total,
    excludedCount,
  };
}

module.exports = { preview, inventoryDigest, safePath, excluded };
