// import * as vscode from 'vscode';
// import * as path from 'path';
// import { RepairService } from './RepairService';
// import { PatchNode } from './Models';

// export class BeamSearchTreeProvider implements vscode.TreeDataProvider<TreePatchNodeItem>, vscode.FileDecorationProvider {

//     private service: RepairService;

//     private _onDidChangeTreeData: vscode.EventEmitter<TreePatchNodeItem | undefined | null | void> = new vscode.EventEmitter<TreePatchNodeItem | undefined | null | void>();
//     readonly onDidChangeTreeData: vscode.Event<TreePatchNodeItem | undefined | null | void> = this._onDidChangeTreeData.event;

//     private _onDidChangeFileDecorations: vscode.EventEmitter<vscode.Uri | vscode.Uri[] | undefined> = new vscode.EventEmitter<vscode.Uri | vscode.Uri[] | undefined>();
//     readonly onDidChangeFileDecorations: vscode.Event<vscode.Uri | vscode.Uri[] | undefined> = this._onDidChangeFileDecorations.event;

//     refresh(): void {
//         this._onDidChangeTreeData.fire();
//     }

//     constructor(service: RepairService) {
//         this.service = service;
//         this.service.onDidPatchesGenerated(() => this.refresh());
//         vscode.window.registerFileDecorationProvider(this);
//     }

//     provideFileDecoration(uri: vscode.Uri, token: vscode.CancellationToken): vscode.ProviderResult<vscode.FileDecoration> {
//         if (uri.scheme === 'ipr-bst') {
//             const args = uri.path.split('/');
//             return {
//                 badge: args[0],
//                 color: new vscode.ThemeColor(args[1])
//             };
//         }
//     }

//     getTreeItem(element: TreePatchNodeItem): vscode.TreeItem {
//         return element;
//     }

//     getChildren(element?: TreePatchNodeItem): Thenable<TreePatchNodeItem[]> {
//         if (element) {
//             let items = element.patchNode.children.map(patch => new TreePatchNodeItem(patch, this.getLabel(patch)));
            
//             items.forEach(it => this.recursivelyUpdateItemCollapsibleState(it));
    
//             return Promise.resolve(items);
//         } else {
//             const editor = vscode.window.activeTextEditor;
//             if (!editor?.document) {
//                 return Promise.resolve([]);
//             }
//             const document = editor.document;

//             if (!this.service.hasSession(document)) {
//                 return Promise.resolve([]);
//             }
            
//             const session = this.service.getSession(document);
//             let items = session.data.root.children.map(patch => new TreePatchNodeItem(patch, this.getLabel(patch)));
    
//             items.forEach(it => this.recursivelyUpdateItemCollapsibleState(it));
//             return Promise.resolve(items);
//         }
//     }

//     getLabel(node: PatchNode): vscode.TreeItemLabel {
//         return { label: node.code };
//     }
    
//     recursivelyUpdateItemCollapsibleState(item: TreePatchNodeItem): boolean {
//         if (item.patchNode.children.length === 0) {
//             item.collapsibleState = vscode.TreeItemCollapsibleState.None;
//         } else {
//             item.collapsibleState = this.anyChildSampled(item.patchNode) ? vscode.TreeItemCollapsibleState.Expanded : vscode.TreeItemCollapsibleState.Collapsed;
//         }
//         return item.patchNode.sampled;
//     }

//     anyChildSampled(patchNode: PatchNode) {
//         if (patchNode.sampled) return true;
//         for (const child of patchNode.children) {
//             if (this.anyChildSampled(child)) return true;
//         }
//         return false;
//     }
// }

// class TreePatchNodeItem extends vscode.TreeItem {
//     constructor(
//         public readonly patchNode: PatchNode,
//         label: vscode.TreeItemLabel,
//     ) {
//         super(label, vscode.TreeItemCollapsibleState.Collapsed);
//         this.id = Math.random().toString(36).slice(2);
//         this.tooltip = `This is a tooltip`;
//         this.description = patchNode.sampling_prob + '';
        
//         let color;
//         let badge;
//         if (patchNode.pivot) {
//             color = 'charts.orange';
//             badge = 'P';
//         } else if (patchNode.sample_root) {
//             color = 'charts.blue';
//             badge = 'R';
//         } else if (patchNode.excluded) {
//             color = 'gitDecoration.deletedResourceForeground';
//             badge = '✘';
//         } else if (patchNode.sampled) {
//             color = 'gitDecoration.addedResourceForeground';
//             badge = '✔';
//         } else {
//             color = 'gitDecoration.ignoredResourceForeground';
//             badge = '';
//         }
//         this.resourceUri = vscode.Uri.parse('ipr-bst:' + badge + '/' + color, true);
//     }

//     iconPath = {
//         light: path.join(__filename, '..', '..', 'resources', 'light', 'dependency.svg'),
//         dark: path.join(__filename, '..', '..', 'resources', 'dark', 'dependency.svg')
//     };
// }