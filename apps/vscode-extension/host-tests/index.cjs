"use strict";

// Actual VS Code Extension Host acceptance. No API replacement, mocked approval or test mode.
const vscode = require("vscode");
const assert = require("node:assert/strict");
const fs = require("node:fs/promises");
const path = require("node:path");
const crypto = require("node:crypto");
const { setTimeout: delay } = require("node:timers/promises");
const digest = (value) =>
  crypto.createHash("sha256").update(value).digest("hex");

async function run() {
  const report = {
    kind: "ACTUAL_ISOLATED_VSCODE_EXTENSION_HOST",
    result: "FAIL",
    mode: process.env.IACODE_EDITOR_MODE,
    editorVersion: vscode.version,
    nodeVersion: process.version,
    processId: process.pid,
    steps: [],
  };
  const record = (name, facts = {}) =>
    report.steps.push({ name, result: "PASS", ...facts });
  try {
    const extension = vscode.extensions.getExtension("iacode.iacode");
    assert.ok(extension, "fresh installed VSIX must be present");
    const installedRoot = path.resolve(process.env.IACODE_EDITOR_EXTENSIONS);
    const relative = path.relative(installedRoot, extension.extensionPath);
    assert.ok(
      relative && !relative.startsWith("..") && !path.isAbsolute(relative),
      "must load the installed VSIX, not development source",
    );
    const api = await extension.activate();
    const commands = await vscode.commands.getCommands(true);
    assert.ok(
      extension.packageJSON.contributes.commands.every((item) =>
        commands.includes(item.command),
      ),
    );
    assert.equal(
      digest(
        await fs.readFile(
          path.join(extension.extensionPath, "out/core/desktop_protocol.json"),
        ),
      ),
      process.env.IACODE_EDITOR_PROTOCOL_DIGEST,
    );
    record("fresh-installed-extension-active", {
      commands: extension.packageJSON.contributes.commands.length,
      extensionPath: extension.extensionPath,
    });
    const invoke = (name) => vscode.commands.executeCommand(`iacode.${name}`);
    if (report.mode === "untrusted") {
      assert.equal(
        vscode.workspace.isTrusted,
        false,
        "fresh profile must actually be untrusted",
      );
      for (const name of [
        "preview",
        "snapshot",
        "start",
        "cancel",
        "qualityStart",
        "qualityCancel",
        "qualityReproduce",
      ]) {
        const result = await invoke(name);
        assert.equal(result.code, "WORKSPACE_UNTRUSTED");
      }
      assert.equal(api.getState().lifecycle.pending, undefined);
      record(
        "actual-untrusted-workspace-refuses-every-mutation-before-connection",
      );
    } else {
      assert.equal(
        vscode.workspace.isTrusted,
        true,
        "explicit trusted test profile",
      );
      if (report.mode === "package") {
        assert.equal((await invoke("snapshot")).code, "CONNECTION_REQUIRED");
        assert.equal(api.getState().connected, false);
        record("configuration-not-inherited-from-workspace-or-environment");
      } else {
        const accept = "workbench.action.acceptSelectedQuickOpenItem";
        const next = "workbench.action.quickOpenSelectNext";
        assert.ok(
          commands.includes(accept) && commands.includes(next),
          "native QuickInput actions must exist",
        );
        async function waitUI(kind) {
          const end = Date.now() + 10000;
          while (Date.now() < end && api.getState().awaiting !== kind) {
            const state = api.getState();
            if (!state.busy && state.lastError)
              assert.fail(
                `native action refused before ${kind}: ${JSON.stringify(state.lastError)}`,
              );
            await delay(25);
          }
          assert.equal(
            api.getState().awaiting,
            kind,
            `actual native ${kind} must be shown`,
          );
          // Let the workbench render the QuickInput requested across the extension-host RPC.
          await delay(100);
        }
        async function pick(kind, approve = false) {
          await waitUI(kind);
          if (approve) await vscode.commands.executeCommand(next);
          await vscode.commands.executeCommand(accept);
        }
        async function approve(name) {
          const action = invoke(name);
          await pick("approval", true);
          const result = await action;
          assert.equal(
            result.ok,
            true,
            `native ${name}: ${JSON.stringify(result)}`,
          );
          return result.data;
        }
        if (report.mode === "start") {
          await api.configureConnection(
            process.env.IACODE_DESKTOP_ENDPOINT,
            process.env.IACODE_DESKTOP_TOKEN,
          );
          assert.equal(api.getState().connected, true);
          assert.equal((await invoke("teams")).ok, true);
          assert.equal((await invoke("agents")).ok, true);
          const inventory = await invoke("preview");
          assert.equal(inventory.ok, true);
          assert.ok(
            inventory.data.inventory.length > 0 && !inventory.data.files,
          );
          const cancelled = invoke("snapshot");
          await pick("approval");
          assert.equal((await cancelled).code, "APPROVAL_CANCELLED");
          assert.equal(api.getState().lifecycle.snapshot, undefined);
          record("native-default-cancel-sends-no-upload");
          const snapshot = await approve("snapshot");
          record("native-exact-snapshot-approved", {
            snapshotId: snapshot.snapshotId,
            snapshotDigest: snapshot.snapshotDigest,
          });
          const document = await vscode.workspace.openTextDocument({
            language: "plaintext",
            content: process.env.IACODE_EDITOR_TASK,
          });
          const editor = await vscode.window.showTextDocument(document);
          editor.selection = new vscode.Selection(
            document.positionAt(0),
            document.positionAt(document.getText().length),
          );
          const action = invoke("start");
          await pick("task");
          await pick("team"); // Canonical registry sorts coding before the other teams.
          await pick("approval", true);
          const started = await action;
          assert.equal(
            started.ok,
            false,
            "the owned transport proxy must interrupt the first accepted create response",
          );
          assert.equal(started.uncertain, true);
          const pending = api.getState().lifecycle.pending;
          assert.equal(pending.operation, "start");
          assert.equal(pending.idempotencyKey, started.idempotencyKey);
          report.pending = pending;
          record(
            "actual-uncertain-create-retains-stable-identity-without-retry",
            { code: started.code, idempotencyKey: pending.idempotencyKey },
          );
        } else if (report.mode === "resume") {
          // New host process, same isolated profile: read the actual persisted credential/state.
          assert.ok(
            api.getState().lifecycle.pending,
            "pending identity must survive host exit",
          );
          assert.equal(
            (await invoke("connect")).ok,
            true,
            "real SecretStorage must survive host restart",
          );
          const recovered = await invoke("recover");
          assert.equal(recovered.ok, true);
          assert.equal(recovered.data.found, true);
          assert.equal(api.getState().lifecycle.pending, null);
          const runId = api.getState().lifecycle.runId;
          assert.ok(runId);
          record("new-host-read-only-recovery", { runId });
          let detail;
          const end = Date.now() + 900000;
          while (Date.now() < end) {
            const refreshed = await invoke("refresh");
            assert.equal(refreshed.ok, true);
            if (
              ["SUCCEEDED", "FAILED", "CANCELLED"].includes(
                refreshed.data.taskState,
              )
            ) {
              detail = (await invoke("read")).data;
              break;
            }
            await delay(500);
          }
          assert.ok(detail, "actual provider workflow must become terminal");
          report.taskObservation = {
            runId,
            state: detail.state,
            errorType: detail.errorType,
            modelCalls: detail.budget?.modelCallsUsed,
            sandboxExecutions: detail.toolExecutions?.length,
          };
          assert.equal(
            detail.state,
            "SUCCEEDED",
            `actual task failed: ${detail.errorType}`,
          );
          assert.ok(detail.budget.modelCallsUsed > 0);
          assert.ok(
            detail.toolExecutions.length > 0,
            "provider task must execute real sandbox tools",
          );
          const testRequest = detail.toolRequests.find(
            (request) =>
              request.name === "shell.exec" &&
              typeof request.arguments.command === "string" &&
              /^python(?:3(?:\.\d+)?)?\s+-m\s+unittest(?:\s+[A-Za-z0-9_./*?=-]+)*$/.test(
                request.arguments.command.trim(),
              ) &&
              detail.toolExecutions.some(
                (execution) =>
                  execution.toolRequestId === request.toolRequestId &&
                  execution.status === "SUCCEEDED" &&
                  execution.exitCode === 0 &&
                  execution.sandboxSession,
              ),
          );
          assert.ok(
            testRequest,
            "the real sandbox must successfully execute the requested unittest command, not merely read a file",
          );
          assert.equal(detail.trainingAllowed, false);
          const first = (await invoke("events")).data;
          const second = (await invoke("events")).data;
          assert.ok(first.events.length > 0);
          assert.ok(
            second.events.every((event) => event.sequence > first.nextCursor),
          );
          report.runId = runId;
          record("actual-provider-task-sandbox-result-and-ordered-events", {
            runId,
            modelCalls: detail.budget.modelCallsUsed,
            sandboxExecutions: detail.toolExecutions.length,
            successfulUnittestExecution: true,
            lastCursor: second.nextCursor,
          });
          const quality = await approve("qualityStart");
          let qualityDetail;
          const qualityEnd = Date.now() + 600000;
          while (Date.now() < qualityEnd) {
            const result = await invoke("qualityRead");
            assert.equal(result.ok, true);
            if (
              [
                "SUCCEEDED",
                "FAILED",
                "CANCELLED",
                "TIMED_OUT",
                "INVALID",
              ].includes(result.data.run.state)
            ) {
              qualityDetail = result.data;
              break;
            }
            await delay(500);
          }
          assert.ok(qualityDetail);
          assert.equal(qualityDetail.run.state, "SUCCEEDED");
          assert.equal(qualityDetail.verdict.verdict, "PASS");
          assert.ok(
            qualityDetail.results.length && qualityDetail.evidence.length,
          );
          assert.ok(
            qualityDetail.checks
              .filter((check) => check.applicable)
              .every((check) =>
                qualityDetail.results.some(
                  (result) =>
                    result.checkId === check.checkId &&
                    result.status === "PASSED",
                ),
              ),
          );
          report.qualityRunId = quality.runId;
          record("native-derived-quality-results-and-evidence", {
            qualityRunId: quality.runId,
            verdict: qualityDetail.verdict.verdict,
            checks: qualityDetail.checks.length,
            evidence: qualityDetail.evidence.length,
          });
          assert.equal(
            (await invoke("disconnect")).data.remoteCancellationRequested,
            false,
          );
          assert.equal(api.getState().stale, true);
          record("native-disconnect-stale-without-remote-cancel");
        } else throw new Error("unsupported native acceptance mode");
      }
    }
    report.result = "PASS";
  } catch (error) {
    report.failure = {
      name: error.name,
      message: error.message.slice(0, 1200),
    };
    throw error;
  } finally {
    await fs.writeFile(
      process.env.IACODE_EDITOR_REPORT,
      JSON.stringify(report, null, 2) + "\n",
      "utf8",
    );
  }
}

module.exports = { run };
