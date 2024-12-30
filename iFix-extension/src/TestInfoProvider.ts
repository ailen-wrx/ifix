import * as vscode from 'vscode';
import * as path from 'path';
import { RepairService } from './RepairService';

export class TestInfoProvider implements vscode.TreeDataProvider<FailedTestInfoItem> {

    private service: RepairService;

    private _onDidChangeTreeData: vscode.EventEmitter<FailedTestInfoItem | undefined | null | void> = new vscode.EventEmitter<FailedTestInfoItem | undefined | null | void>();
    readonly onDidChangeTreeData: vscode.Event<FailedTestInfoItem | undefined | null | void> = this._onDidChangeTreeData.event;

    private _onDidChangeFileDecorations: vscode.EventEmitter<vscode.Uri | vscode.Uri[] | undefined> = new vscode.EventEmitter<vscode.Uri | vscode.Uri[] | undefined>();
    readonly onDidChangeFileDecorations: vscode.Event<vscode.Uri | vscode.Uri[] | undefined> = this._onDidChangeFileDecorations.event;

    constructor(service: RepairService) {
        this.service = service;
        this.service.onDidPatchesGenerated(() => this.refresh());
    }

    refresh(): void {
        this._onDidChangeTreeData.fire();
    }

    getTreeItem(element: FailedTestInfoItem): vscode.TreeItem {
        return element;
    }

    getChildren(element?: FailedTestInfoItem): Thenable<FailedTestInfoItem[]> {
        if (element) {
            if (element.tooltip === 'errorMsg') {
                return Promise.resolve([]);
            }
            return Promise.resolve(element.errorMsg.split('\n').map(line => new FailedTestInfoItem(0, "", line, "", 'errorMsg')));
        } else {
            const editor = vscode.window.activeTextEditor;
            if (!editor?.document) {
                return Promise.resolve([]);
            }
            const document = editor.document;
            const session = this.service.getSession(document);
            return Promise.resolve(session.data.failed_tests.map(test =>  new FailedTestInfoItem(test.line, test.module, test.id, test.error_msg, 'id')));
        }
    }
}

export class FailedTestInfoItem extends vscode.TreeItem {
    constructor(
        public readonly line: number,
        public readonly module: string,
        public readonly id: string,
        public readonly errorMsg: string,
        public readonly show: string,
        public readonly command?: vscode.Command,
    ) {
        super(id, vscode.TreeItemCollapsibleState.Collapsed);
        this.label = this.id;
        this.tooltip = this.show;
        if (this.show === 'id') {
            this.collapsibleState = vscode.TreeItemCollapsibleState.Collapsed;
            this.iconPath = {
                light: path.join(__filename, '..', '..', 'resources', 'light', 'bug.svg'),
                dark: path.join(__filename, '..', '..', 'resources', 'dark', 'bug.svg')
            };
            this.contextValue = 'failedTest';
        } else {
            this.collapsibleState = vscode.TreeItemCollapsibleState.None;
            this.iconPath = {
                light: "",
                dark: ""
            };
            this.contextValue = 'errorMsg';
        }
        
    }

    
}