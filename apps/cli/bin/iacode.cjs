#!/usr/bin/env node
"use strict";

const crypto = require("node:crypto");
const { setTimeout: delay } = require("node:timers/promises");

const [major, minor, patch] = process.versions.node.split(".").map(Number);
const supported =
  (major === 22 && (minor > 23 || (minor === 23 && patch >= 2))) ||
  (major === 24 && minor >= 19);
let protectedOutput = null;

function output(value, stream = process.stdout) {
  try {
    protectedOutput?.(value, process.env.IACODE_DESKTOP_TOKEN);
  } catch {
    stream.write(
      '{"code":"PROTECTED_OUTPUT_REFUSED","message":"protected or excessive data was not exported"}\n',
    );
    process.exitCode = 5;
    return;
  }
  const text = JSON.stringify(value);
  const configured = process.env.IACODE_DESKTOP_TOKEN || "";
  if (/^[0-9a-f]{64}$/.test(configured) && text.includes(configured)) {
    stream.write(
      '{"code":"CREDENTIAL_REFLECTION_REFUSED","message":"protected authentication material was not exported"}\n',
    );
    process.exitCode = 5;
    return;
  }
  stream.write(
    text.replace(
      /[\u007f-\uffff]/g,
      (char) => `\\u${char.charCodeAt(0).toString(16).padStart(4, "0")}`,
    ) + "\n",
  );
}

if (!supported) {
  output(
    {
      code: "RUNTIME_UNSUPPORTED",
      message:
        "Use Node 22.23.2+ or Node 24.19.0+ in those supported major lines",
    },
    process.stderr,
  );
  process.exitCode = 2;
} else {
  main()
    .then((code) => {
      if (!process.exitCode) process.exitCode = code;
    })
    .catch((error) => {
      const known = error?.name === "DesktopClientError";
      const code = known
        ? error.code
        : error?.code === "MODULE_NOT_FOUND"
          ? "INSTALLATION_INCOMPLETE"
          : "CLIENT_OPERATION_FAILED";
      output(
        {
          code,
          message: known
            ? error.message
            : "operation could not complete; verify the installed package and runtime configuration",
          uncertain: known ? error.uncertain : false,
          requestId: known ? error.requestId : undefined,
          idempotencyKey: known ? error.idempotencyKey : undefined,
          lastCursor: error.lastCursor,
          remoteCancellationRequested: false,
        },
        process.stderr,
      );
      const usage =
        /^(ARGUMENT_|COMMAND_|ENDPOINT_|CREDENTIAL_INVALID$|FIELD_|APPROVAL_|SNAPSHOT_|WORKSPACE_)/.test(
          code,
        );
      process.exitCode =
        code === "OBSERVATION_CANCELLED"
          ? 130
          : error.uncertain
            ? 4
            : usage || !known
              ? 2
              : 5;
    });
}

async function main() {
  const {
    DesktopClient,
    DesktopClientError,
    protectData,
  } = require("../src/client.cjs");
  protectedOutput = protectData;
  const { preview } = require("../src/snapshot.cjs");
  const fail = (code, message) => {
    throw new DesktopClientError(code, message);
  };
  const argv = process.argv.slice(2);
  const command = argv.shift() || "help";
  const commands = {
    help: {},
    "new-id": {},
    doctor: {},
    agents: {},
    teams: {},
    preview: { root: "string" },
    snapshot: { root: "string", approve: "string" },
    start: {
      snapshot: "string",
      task: "string",
      team: "string",
      model: "string",
      "request-id": "string",
      approve: "boolean",
    },
    list: { limit: "integer" },
    read: { "run-id": "string" },
    lookup: { "request-id": "string" },
    "quality-lookup": { "request-id": "string" },
    "snapshot-lookup": { digest: "string" },
    events: { "run-id": "string", after: "integer", limit: "integer" },
    follow: { "run-id": "string", after: "integer", "wait-seconds": "integer" },
    cancel: { "run-id": "string", approve: "boolean" },
    "quality-start": {
      snapshot: "string",
      digest: "string",
      "request-id": "string",
      approve: "boolean",
    },
    "quality-read": { "run-id": "string" },
    "quality-events": {
      "run-id": "string",
      after: "integer",
      limit: "integer",
    },
    "quality-follow": {
      "run-id": "string",
      after: "integer",
      "wait-seconds": "integer",
    },
    "quality-cancel": { "run-id": "string", approve: "boolean" },
    "quality-reproduce": {
      "run-id": "string",
      "request-id": "string",
      approve: "boolean",
    },
  };
  if (!Object.hasOwn(commands, command))
    fail("COMMAND_UNKNOWN", "use help to list the closed command set");
  const allowed = { ...commands[command], endpoint: "string" };
  const options = {};
  while (argv.length) {
    const option = argv.shift();
    if (!option.startsWith("--") || !Object.hasOwn(allowed, option.slice(2)))
      fail("ARGUMENT_UNKNOWN", "unknown option; consult help");
    const name = option.slice(2);
    if (Object.hasOwn(options, name))
      fail("ARGUMENT_DUPLICATE", "an option was repeated");
    if (allowed[name] === "boolean") options[name] = true;
    else {
      if (!argv.length || argv[0].startsWith("--"))
        fail("ARGUMENT_MISSING", `a value is required for --${name}`);
      const value = argv.shift();
      if (allowed[name] === "integer") {
        if (
          !/^(0|[1-9][0-9]*)$/.test(value) ||
          !Number.isSafeInteger(Number(value))
        )
          fail(
            "ARGUMENT_VALUE_INVALID",
            `--${name} requires a bounded integer`,
          );
        options[name] = Number(value);
      } else options[name] = value;
    }
  }
  if (command === "help") {
    output({
      name: "IACode CLI",
      version: "0.1.0",
      commands,
      configuration:
        "Explicit --endpoint or IACODE_DESKTOP_ENDPOINT; credential only from IACODE_DESKTOP_TOKEN, never argv or workspace files",
      snapshotConsent:
        "preview --root PATH prints an inventory and digest without contents; snapshot --root PATH --approve DIGEST uploads only those exact bytes to the authenticated local runtime",
      mutationConsent:
        "start, cancel and quality mutations require --approve; creation/reproduction also require a stable UUID --request-id from new-id",
      observation:
        "follow emits JSON lines and resumes from --after; Ctrl+C stops only local observation, never the remote run",
      exitCodes: {
        success: 0,
        remoteFailure: 1,
        usageOrInstallation: 2,
        remoteCancelled: 3,
        uncertainMutation: 4,
        transportOrRefusal: 5,
        localInterrupted: 130,
      },
    });
    return 0;
  }
  if (command === "new-id") {
    output({ requestId: crypto.randomUUID() });
    return 0;
  }
  const requireOption = (name) => {
    if (!Object.hasOwn(options, name))
      fail("ARGUMENT_MISSING", `--${name} is required`);
    return options[name];
  };
  if (command === "preview") {
    const result = await preview(requireOption("root"));
    const { files, ...safe } = result;
    output(safe);
    return 0;
  }
  const controller = new AbortController();
  const interrupted = () => controller.abort();
  process.once("SIGINT", interrupted);
  let client;
  try {
    client = new DesktopClient(
      options.endpoint || process.env.IACODE_DESKTOP_ENDPOINT,
      process.env.IACODE_DESKTOP_TOKEN,
    );
    if (command === "doctor") {
      output(await client.connect({ signal: controller.signal }));
      return 0;
    }
    const operation = command;
    let args = {};
    if (command === "snapshot") {
      const approved = requireOption("approve");
      const result = await preview(requireOption("root"));
      if (
        !/^[0-9a-f]{64}$/.test(approved) ||
        result.manifestDigest !== approved
      )
        fail(
          "SNAPSHOT_CONSENT_MISMATCH",
          "run preview and approve the exact current inventory digest",
        );
      args = { manifestDigest: result.manifestDigest, files: result.files };
    } else if (command === "start") {
      args = {
        snapshotId: requireOption("snapshot"),
        task: requireOption("task"),
        team: options.team || "coding",
        idempotencyKey: requireOption("request-id"),
      };
      if (options.model) args.model = options.model;
    } else if (command === "list") {
      args = { limit: options.limit ?? 25 };
    } else if (["lookup", "quality-lookup"].includes(command)) {
      args = { idempotencyKey: requireOption("request-id") };
    } else if (command === "snapshot-lookup") {
      args = { manifestDigest: requireOption("digest") };
    } else if (command === "quality-start") {
      args = {
        snapshotId: requireOption("snapshot"),
        snapshotDigest: requireOption("digest"),
        idempotencyKey: requireOption("request-id"),
      };
    } else if (command === "quality-reproduce") {
      args = {
        runId: requireOption("run-id"),
        idempotencyKey: requireOption("request-id"),
      };
    } else if (!["agents", "teams"].includes(command)) {
      args = { runId: requireOption("run-id") };
      if (command.endsWith("events"))
        Object.assign(args, {
          after: options.after ?? 0,
          limit: options.limit ?? 200,
        });
    }
    if (["follow", "quality-follow"].includes(command)) {
      const quality = command === "quality-follow";
      const waitSeconds = options["wait-seconds"] ?? 600;
      if (waitSeconds < 1 || waitSeconds > 3600)
        fail(
          "ARGUMENT_VALUE_INVALID",
          "--wait-seconds must be between 1 and 3600",
        );
      const deadline = Date.now() + waitSeconds * 1000;
      let cursor = options.after ?? 0;
      while (Date.now() < deadline) {
        try {
          const page = await client.execute(
            quality ? "quality-events" : "events",
            { runId: args.runId, after: cursor, limit: 200 },
            { signal: controller.signal },
          );
          cursor = page.nextCursor;
          if (page.events.length)
            output({ type: "events", runId: args.runId, ...page });
          const detail = await client.execute(
            quality ? "quality-read" : "read",
            { runId: args.runId },
            { signal: controller.signal },
          );
          const state = quality ? detail.run.state : detail.state;
          const terminal = quality
            ? client.session.terminalQualityStates
            : client.session.terminalRunStates;
          if (terminal.includes(state) && page.events.length < 200) {
            // Read one final page after observing the terminal state; the last transition can
            // have committed between the previous events page and the state observation.
            const finalPage = await client.execute(
              quality ? "quality-events" : "events",
              { runId: args.runId, after: cursor, limit: 200 },
              { signal: controller.signal },
            );
            cursor = finalPage.nextCursor;
            if (finalPage.events.length) {
              output({ type: "events", runId: args.runId, ...finalPage });
              continue;
            }
            output({
              type: "terminal",
              lastCursor: cursor,
              remoteCancellationRequested: false,
              data: detail,
            });
            if (state === "CANCELLED") return 3;
            return state === "SUCCEEDED" &&
              (!quality || detail.verdict?.verdict === "PASS")
              ? 0
              : 1;
          }
          await delay(500, undefined, { signal: controller.signal });
        } catch (error) {
          if (controller.signal.aborted) {
            const stopped = new DesktopClientError(
              "OBSERVATION_CANCELLED",
              "local observation stopped; remote work was not cancelled",
            );
            stopped.lastCursor = cursor;
            throw stopped;
          }
          error.lastCursor = cursor;
          throw error;
        }
      }
      output({
        code: "OBSERVATION_DEADLINE",
        runId: args.runId,
        lastCursor: cursor,
        remoteCancellationRequested: false,
      });
      return 5;
    }
    const mutation = [
      "snapshot",
      "start",
      "cancel",
      "quality-start",
      "quality-cancel",
      "quality-reproduce",
    ].includes(operation);
    if (mutation && command !== "snapshot" && options.approve !== true)
      fail(
        "APPROVAL_REQUIRED",
        "the exact requested mutation requires --approve",
      );
    if (mutation) {
      await client.connect({ signal: controller.signal });
      output(
        await client.execute(operation, args, {
          approval: client.intent(operation, args),
          signal: controller.signal,
        }),
      );
    } else
      output(
        await client.execute(operation, args, { signal: controller.signal }),
      );
    return 0;
  } finally {
    client?.dispose();
    process.removeListener("SIGINT", interrupted);
  }
}
