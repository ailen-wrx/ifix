"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.FailedTestInfoItem = exports.TestInfoProvider = void 0;
const vscode = require("vscode");
const path = require("path");
class TestInfoProvider {
    constructor(service) {
        this._onDidChangeTreeData = new vscode.EventEmitter();
        this.onDidChangeTreeData = this._onDidChangeTreeData.event;
        this._onDidChangeFileDecorations = new vscode.EventEmitter();
        this.onDidChangeFileDecorations = this._onDidChangeFileDecorations.event;
        this.service = service;
        this.service.onDidPatchesGenerated(() => this.refresh());
    }
    refresh() {
        this._onDidChangeTreeData.fire();
    }
    getTreeItem(element) {
        return element;
    }
    getChildren(element) {
        if (element) {
            if (element.tooltip === 'errorMsg') {
                return Promise.resolve([]);
            }
            return Promise.resolve(element.errorMsg.split('\n').map(line => new FailedTestInfoItem(0, "", line, "", 'errorMsg')));
        }
        else {
            const editor = vscode.window.activeTextEditor;
            if (!editor?.document) {
                return Promise.resolve([]);
            }
            const document = editor.document;
            const session = this.service.getSession(document);
            return Promise.resolve(session.data.failed_tests.map(test => new FailedTestInfoItem(test.line, test.module, test.id, test.error_msg, 'id')));
        }
    }
}
exports.TestInfoProvider = TestInfoProvider;
class FailedTestInfoItem extends vscode.TreeItem {
    constructor(line, module, id, errorMsg, show, command) {
        super(id, vscode.TreeItemCollapsibleState.Collapsed);
        this.line = line;
        this.module = module;
        this.id = id;
        this.errorMsg = errorMsg;
        this.show = show;
        this.command = command;
        this.label = this.id;
        this.tooltip = this.show;
        if (this.show === 'id') {
            this.collapsibleState = vscode.TreeItemCollapsibleState.Collapsed;
            this.iconPath = {
                light: path.join(__filename, '..', '..', 'resources', 'light', 'bug.svg'),
                dark: path.join(__filename, '..', '..', 'resources', 'dark', 'bug.svg')
            };
            this.contextValue = 'failedTest';
        }
        else {
            this.collapsibleState = vscode.TreeItemCollapsibleState.None;
            this.iconPath = {
                light: "",
                dark: ""
            };
            this.contextValue = 'errorMsg';
        }
    }
}
exports.FailedTestInfoItem = FailedTestInfoItem;
//# sourceMappingURL=TestInfoProvider.js.map