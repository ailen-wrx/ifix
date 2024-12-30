"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.deactivate = exports.activate = void 0;
// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
const vscode_1 = require("vscode");
const RepairDocumentRenderer_1 = require("./RepairDocumentRenderer");
const RepairService_1 = require("./RepairService");
const TestInfoProvider_1 = require("./TestInfoProvider");
const VariableProvider_1 = require("./VariableProvider");
// this method is called when your extension is activated
// your extension is activated the very first time the command is executed
let disposables = [];
function activate(context) {
    const service = new RepairService_1.RepairService();
    const documentRenderer = new RepairDocumentRenderer_1.RepairDocumentRenderer(service);
    const testInfoProvider = new TestInfoProvider_1.TestInfoProvider(service);
    const variableProvider = new VariableProvider_1.VariableProvider(service, context.extensionUri);
    // const exprProvider = new ExprProvider(service, context.extensionUri);
    vscode_1.languages.registerCodeLensProvider("*", documentRenderer);
    vscode_1.window.registerTreeDataProvider('iprFailedTests', testInfoProvider);
    vscode_1.window.registerWebviewViewProvider('iprVariables', variableProvider);
    // window.registerWebviewViewProvider('iprSubExpr', exprProvider);
    vscode_1.commands.registerCommand("ipr.enable", () => {
        vscode_1.workspace.getConfiguration("ipr").update("enabled", true, false);
    });
    vscode_1.commands.registerCommand("ipr.disable", () => {
        vscode_1.workspace.getConfiguration("ipr").update("enabled", false, false);
    });
    vscode_1.commands.registerCommand("ipr.restart-repair", (document) => {
        service.restartRepair(document);
    });
    vscode_1.commands.registerCommand("ipr.explore-group", (document, patchGroup) => {
        service.exploreGroup(document, patchGroup);
    });
    vscode_1.commands.registerCommand("ipr.exclude-group", (document, patchGroup) => {
        service.excludeGroup(document, patchGroup);
    });
    vscode_1.commands.registerCommand("ipr.accept-patch", (document, patchGroup) => {
        service.acceptPatch(document, patchGroup);
    });
    vscode_1.commands.registerCommand('iprFailedTests.addEntry', () => vscode_1.window.showInformationMessage(`Successfully called add entry.`));
    vscode_1.commands.registerCommand('iprFailedTests.rerunEntry', (node) => {
        service.instrument(node);
    });
    vscode_1.commands.registerCommand('iprFailedTests.deleteEntry', (node) => vscode_1.window.showInformationMessage(`Successfully called delete entry on ${node.label}.`));
    vscode_1.commands.registerCommand('ipr.initTables', (tableData) => {
        // console.log(tableData);
        // console.log(mockupTables);
        variableProvider.initTables(tableData);
    });
}
exports.activate = activate;
// this method is called when your extension is deactivated
function deactivate() {
    if (disposables) {
        disposables.forEach(item => item.dispose());
    }
    disposables = [];
}
exports.deactivate = deactivate;
//# sourceMappingURL=extension.js.map