"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.VariableProvider = void 0;
const vscode = require("vscode");
class VariableProvider {
    constructor(service, _extensionUri) {
        this._extensionUri = _extensionUri;
        this._onDidChangeFileDecorations = new vscode.EventEmitter();
        this.onDidChangeFileDecorations = this._onDidChangeFileDecorations.event;
        this.service = service;
        this.service.onDidPatchesGenerated(() => this.refresh());
    }
    initTables(tables) {
        if (this._view) {
            console.log(tables);
            this._view.show();
            this._view.webview.postMessage({
                type: 'initTables',
                data: tables
            });
        }
    }
    refresh() {
    }
    resolveWebviewView(webviewView, context, _token) {
        this._view = webviewView;
        webviewView.webview.options = {
            // Allow scripts in the webview
            enableScripts: true,
            localResourceRoots: [
                this._extensionUri
            ]
        };
        webviewView.webview.html = this._getHtmlForWebview(webviewView.webview);
        webviewView.webview.onDidReceiveMessage(message => {
            switch (message.command) {
                case 'jumpto':
                    {
                        console.log(this.service);
                        const service = this.service.getSessionFromIndex(this.service.currentSession);
                        console.log('jumpto');
                        console.log(service);
                        console.log(message.url);
                        var lineNumber = message.line - 1;
                        console.log(lineNumber);
                        vscode.window.showTextDocument(vscode.Uri.joinPath(vscode.Uri.parse(vscode.workspace.rootPath), message.url)).then(_ => {
                            let activeEditor = vscode.window.activeTextEditor;
                            let range = activeEditor.document.lineAt(lineNumber).range;
                            activeEditor.selection = new vscode.Selection(range.start, range.end);
                            activeEditor.revealRange(range);
                        });
                        break;
                    }
            }
        });
    }
    _getHtmlForWebview(webview) {
        const scriptUri = webview.asWebviewUri(vscode.Uri.joinPath(this._extensionUri, 'media', 'main.js'));
        const styleResetUri = webview.asWebviewUri(vscode.Uri.joinPath(this._extensionUri, 'media', 'reset.css'));
        const styleVSCodeUri = webview.asWebviewUri(vscode.Uri.joinPath(this._extensionUri, 'media', 'vscode.css'));
        const styleMainUri = webview.asWebviewUri(vscode.Uri.joinPath(this._extensionUri, 'media', 'main.css'));
        const nonce = getNonce();
        let html = `
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <!--
            Use a content security policy to only allow loading images from https or from our extension directory,
            and only allow scripts that have a specific nonce.
            -->
            <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src ${webview.cspSource}; script-src 'nonce-${nonce}';">

            <meta name="viewport" content="width=device-width, initial-scale=1.0">


            <link href="${styleResetUri}" rel="stylesheet">
            <link href="${styleVSCodeUri}" rel="stylesheet">
            <link href="${styleMainUri}" rel="stylesheet">
            <title>Variables</title>
        </head>
        <body>
            <ul class='table-list'>
            </ul>
            <script nonce="${nonce}" src="${scriptUri}"></script>`;
        html += `
			</body>
			</html>`;
        return html;
    }
}
exports.VariableProvider = VariableProvider;
VariableProvider.viewType = 'iprVariables';
function getNonce() {
    let text = '';
    const possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    for (let i = 0; i < 32; i++) {
        text += possible.charAt(Math.floor(Math.random() * possible.length));
    }
    return text;
}
//# sourceMappingURL=VariableProvider.js.map