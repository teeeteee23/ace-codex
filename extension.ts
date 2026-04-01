import * as vscode from "vscode";
import axios from "axios";

const SERVER_URL = "http://localhost:5005";

let statusBar: vscode.StatusBarItem;

export function activate(context: vscode.ExtensionContext) {
  console.log("ACE-Codex activated");

  // Status bar
  statusBar = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
  statusBar.text = "$(sparkle) ACE-Codex";
  statusBar.tooltip = "ACE-Codex: AI code completion active";
  statusBar.command = "ace-codex.selectModel";
  statusBar.show();
  context.subscriptions.push(statusBar);

  // Inline completion provider
  const provider = vscode.languages.registerInlineCompletionItemProvider(
    { pattern: "**" },
    {
      async provideInlineCompletionItems(document, position) {
        const prefix = document.getText(
          new vscode.Range(new vscode.Position(0, 0), position)
        );
        const suffix = document.getText(
          new vscode.Range(position, document.positionAt(document.getText().length))
        );

        try {
          const ragRes = await axios.post(`${SERVER_URL}/rag/query`, { text: prefix.slice(-200) });
          const context = ragRes.data.context || "";

          const res = await axios.post(`${SERVER_URL}/complete`, {
            prefix,
            suffix,
            language: document.languageId,
            context,
          });

          const completion = res.data.completion;
          if (!completion) return [];

          return [
            new vscode.InlineCompletionItem(
              completion,
              new vscode.Range(position, position)
            ),
          ];
        } catch {
          return [];
        }
      },
    }
  );
  context.subscriptions.push(provider);

  // Command: select model
  const selectModelCmd = vscode.commands.registerCommand("ace-codex.selectModel", async () => {
    try {
      const res = await axios.get(`${SERVER_URL}/models/list`);
      const models = res.data.local as string[];
      const picked = await vscode.window.showQuickPick(models, {
        placeHolder: "Select an Ollama model for completions",
      });
      if (picked) {
        await axios.post(`${SERVER_URL}/models/select`, { model: picked });
        statusBar.text = `$(sparkle) ACE: ${picked}`;
        vscode.window.showInformationMessage(`ACE-Codex: switched to ${picked}`);
      }
    } catch {
      vscode.window.showErrorMessage("ACE-Codex: could not connect to backend. Is it running?");
    }
  });
  context.subscriptions.push(selectModelCmd);

  // Command: index workspace for RAG
  const indexCmd = vscode.commands.registerCommand("ace-codex.indexWorkspace", async () => {
    const workspacePath = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
    if (!workspacePath) {
      vscode.window.showWarningMessage("ACE-Codex: No workspace folder open.");
      return;
    }
    vscode.window.showInformationMessage("ACE-Codex: Indexing workspace for RAG...");
    try {
      await axios.post(`${SERVER_URL}/rag/index`, { path: workspacePath });
      vscode.window.showInformationMessage("ACE-Codex: Workspace indexed successfully.");
    } catch {
      vscode.window.showErrorMessage("ACE-Codex: Indexing failed. Is backend running?");
    }
  });
  context.subscriptions.push(indexCmd);

  // Command: voice transcribe
  const voiceCmd = vscode.commands.registerCommand("ace-codex.voiceInput", async () => {
    vscode.window.showInformationMessage("ACE-Codex: Listening... (5 seconds)");
    try {
      const res = await axios.post(`${SERVER_URL}/voice/transcribe`, { audio_path: "" });
      const text = res.data.text;
      const editor = vscode.window.activeTextEditor;
      if (editor && text) {
        editor.edit((editBuilder) => {
          editBuilder.insert(editor.selection.active, text);
        });
      }
    } catch {
      vscode.window.showErrorMessage("ACE-Codex: Voice input failed.");
    }
  });
  context.subscriptions.push(voiceCmd);
}

export function deactivate() {
  statusBar?.dispose();
}
