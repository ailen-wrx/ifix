// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
import { ExtensionContext, languages, commands, Disposable, workspace, window, TextDocument, EventEmitter, Uri } from 'vscode';
import { RepairDocumentRenderer } from './RepairDocumentRenderer';
import { RepairService } from './RepairService';
import { PatchGroup, TableContent } from './Models';
import { TestInfoProvider, FailedTestInfoItem } from './TestInfoProvider';
import { VariableProvider } from './VariableProvider';
import { mockupTables } from './Utils';

// this method is called when your extension is activated
// your extension is activated the very first time the command is executed

let disposables: Disposable[] = [];

export function activate(context: ExtensionContext) {
    const service = new RepairService();
    const documentRenderer = new RepairDocumentRenderer(service);
    const testInfoProvider = new TestInfoProvider(service);
    const variableProvider = new VariableProvider(service, context.extensionUri);
    // const exprProvider = new ExprProvider(service, context.extensionUri);

    languages.registerCodeLensProvider("*", documentRenderer);

    window.registerTreeDataProvider('iprFailedTests', testInfoProvider);
    window.registerWebviewViewProvider('iprVariables', variableProvider);
    // window.registerWebviewViewProvider('iprSubExpr', exprProvider);


    commands.registerCommand("ipr.enable", () => {
        workspace.getConfiguration("ipr").update("enabled", true, false);
    });

    commands.registerCommand("ipr.disable", () => {
        workspace.getConfiguration("ipr").update("enabled", false, false);
    });

    commands.registerCommand("ipr.restart-repair", (document: TextDocument) => {
        service.restartRepair(document);
    });

    commands.registerCommand("ipr.explore-group", (document: TextDocument, patchGroup: PatchGroup) => {
        service.exploreGroup(document, patchGroup);
    });

    commands.registerCommand("ipr.exclude-group", (document: TextDocument, patchGroup: PatchGroup) => {
        service.excludeGroup(document, patchGroup);
    });

    commands.registerCommand("ipr.accept-patch", (document: TextDocument, patchGroup: PatchGroup) => {
        service.acceptPatch(document, patchGroup);
    });

	commands.registerCommand('iprFailedTests.addEntry', () => window.showInformationMessage(`Successfully called add entry.`));
	commands.registerCommand('iprFailedTests.rerunEntry', (node: FailedTestInfoItem) => { 
        service.instrument(node);
    });
	commands.registerCommand('iprFailedTests.deleteEntry', (node: FailedTestInfoItem) => window.showInformationMessage(`Successfully called delete entry on ${node.label}.`));

    commands.registerCommand('ipr.initTables', (tableData: any) => {
        // console.log(tableData);
        // console.log(mockupTables);
        variableProvider.initTables(tableData);
	});

}

// this method is called when your extension is deactivated
export function deactivate() {
    if (disposables) {
        disposables.forEach(item => item.dispose());
    }
    disposables = [];
}