import * as vscode from 'vscode';
import { TableContent } from './Models';
import { RepairService } from './RepairService';
import { mockupTables } from './Utils';

export class VariableProvider implements vscode.WebviewViewProvider {
    public static readonly viewType = 'iprVariables';

    private _view?: vscode.WebviewView;

    private service: RepairService;

    private _onDidChangeFileDecorations: vscode.EventEmitter<vscode.Uri | vscode.Uri[] | undefined> = new vscode.EventEmitter<vscode.Uri | vscode.Uri[] | undefined>();
    readonly onDidChangeFileDecorations: vscode.Event<vscode.Uri | vscode.Uri[] | undefined> = this._onDidChangeFileDecorations.event;

    constructor(service: RepairService, private readonly _extensionUri: vscode.Uri) {
        this.service = service;
        this.service.onDidPatchesGenerated(() => this.refresh());
    }

    public initTables(tables: any) {
        if (this._view) {
            console.log(tables);
            this._view.show();
			this._view.webview.postMessage({ 
                type: 'initTables',
                data: tables
            });
		}
    }

    refresh(): void {
    }

    public resolveWebviewView(
		webviewView: vscode.WebviewView,
		context: vscode.WebviewViewResolveContext,
		_token: vscode.CancellationToken,
	) {
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
                        vscode.window.showTextDocument(vscode.Uri.joinPath(
                            vscode.Uri.parse(vscode.workspace.rootPath as string), message.url as string)).then(_ => {
                                let activeEditor = vscode.window.activeTextEditor as vscode.TextEditor;
                                let range = activeEditor.document.lineAt(lineNumber).range;
                                activeEditor.selection =  new vscode.Selection(range.start, range.end);
                                activeEditor.revealRange(range);
                              });
						break;
					}
			}
		});


    }

    private _getHtmlForWebview(webview: vscode.Webview) {
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


function getNonce() {
	let text = '';
	const possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
	for (let i = 0; i < 32; i++) {
		text += possible.charAt(Math.floor(Math.random() * possible.length));
	}
	return text;
}