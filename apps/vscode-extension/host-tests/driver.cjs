"use strict";

// Owned acceptance driver, never part of the production VSIX. Run in a real development
// host without --extensionTestsPath: that flag deliberately replaces persistent VS Code storage.
const vscode = require("vscode");

async function activate() {
  try {
    await require("./test.cjs").run();
  } catch (error) {
    // test.cjs already writes the bounded FAIL report. Never log payloads or credentials here.
    console.error(`IACode native acceptance failed: ${error.name}`);
  } finally {
    // Every window/profile/document in this driver is owned by the acceptance invocation.
    // Discard only its untitled test/result documents, never a source file or user window.
    for (const document of [...vscode.workspace.textDocuments]) {
      if (document.uri.scheme !== "untitled" || document.isClosed) continue;
      await vscode.window.showTextDocument(document, { preserveFocus: false });
      await vscode.commands.executeCommand(
        "workbench.action.revertAndCloseActiveEditor",
      );
    }
    await vscode.commands.executeCommand("workbench.action.quit");
  }
}

module.exports = { activate };
