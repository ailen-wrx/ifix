"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.RepairDocumentRenderer = exports.RenderPhase = void 0;
const vscode = require("vscode");
const Utils_1 = require("./Utils");
var RenderPhase;
(function (RenderPhase) {
    RenderPhase[RenderPhase["init"] = 0] = "init";
    RenderPhase[RenderPhase["appended"] = 1] = "appended";
    RenderPhase[RenderPhase["decorated"] = 2] = "decorated";
})(RenderPhase = exports.RenderPhase || (exports.RenderPhase = {}));
class RepairDocumentRenderer {
    constructor(service) {
        this._onDidChangeCodeLenses = new vscode.EventEmitter();
        this.onDidChangeCodeLenses = this._onDidChangeCodeLenses.event;
        this.lastDocumentChangeTime = new Date();
        this.service = service;
        this.states = new Map();
        console.log(vscode.workspace.getConfiguration("ipr").get("enabled"));
        if (vscode.workspace.getConfiguration("ipr").get("enabled") === true) {
            vscode.workspace.onDidChangeConfiguration((_) => {
                this._onDidChangeCodeLenses.fire();
            });
            vscode.workspace.onDidChangeTextDocument((change) => {
                const document = change.document;
                console.log(change.contentChanges);
                if (change.contentChanges.length > 0 && this.service.hasSession(document)) {
                    // Revert and don't pass the event to downstream if the change is marked as our own
                    const isOwnChange = change.contentChanges.length >= 1
                        && change.contentChanges.some(it => it.text === RepairDocumentRenderer.changeFlag);
                    if (isOwnChange) {
                        console.log('Is own change. Ignoring');
                        var editor = vscode.window.activeTextEditor;
                        if (editor?.document !== document) {
                            return;
                        }
                        editor.edit(editBuilder => {
                            editBuilder.delete(new vscode.Range(new vscode.Position(0, 0), new vscode.Position(0, RepairDocumentRenderer.changeFlag.length)));
                        });
                        console.log('RenderState');
                        console.log(this.getState(document).phase);
                        if (this.getState(document).phase === RenderPhase.appended) {
                            this.decoratePatches(document);
                        }
                        return;
                    }
                    // Ignore if the change is our deletion change above
                    const isOwnDeletion = change.contentChanges.length >= 1
                        && change.contentChanges.some(it => it.rangeOffset === 0 && it.rangeLength === RepairDocumentRenderer.changeFlag.length);
                    if (isOwnDeletion) {
                        console.log('Is own deletion. Ignoring');
                        return;
                    }
                    // Reset changes and re-render
                    this.render(document);
                    console.log('Reverting changes');
                    vscode.window.showErrorMessage("You may not edit the file in repair mode.");
                }
            });
            this.service.onDidPatchesGenerated((document) => this.render(document));
        }
    }
    getSession(document) {
        return this.service.getSession(document);
    }
    getState(document) {
        return this.states.get((0, Utils_1.getShortFileName)(document));
    }
    render(document) {
        if (!this.states.has((0, Utils_1.getShortFileName)(document))) {
            this.states.set((0, Utils_1.getShortFileName)(document), { phase: RenderPhase.init, currentDecorationTypes: [] });
        }
        console.log('Render started');
        const session = this.getSession(document);
        const state = this.getState(document);
        state.phase = RenderPhase.init;
        var editor = vscode.window.activeTextEditor;
        state.currentDecorationTypes.forEach(type => {
            editor?.setDecorations(type, []);
        });
        vscode.window.activeTextEditor?.edit(editBuilder => {
            this.markChangeAsOwn(editBuilder);
            editBuilder.replace(new vscode.Range(document.lineAt(0).range.start, document.lineAt(document.lineCount - 1).range.end), session.originalDocumentText);
            if (vscode.workspace.getConfiguration("ipr").get("enabled") === true && document.languageId !== "Log") {
                const token = this.lastDocumentChangeTime = new Date();
                setTimeout(() => {
                    if (this.lastDocumentChangeTime !== token) {
                        return;
                    }
                    this.appendPatches(document);
                }, 2000);
            }
        }, {
            undoStopBefore: false,
            undoStopAfter: false
        });
    }
    appendPatches(document) {
        console.log('Appending patches');
        var editor = vscode.window.activeTextEditor;
        if (!editor) {
            return;
        }
        const session = this.getSession(document);
        const state = this.getState(document);
        console.log('Session is:');
        console.log(session);
        editor.edit(editBuilder => {
            this.markChangeAsOwn(editBuilder);
            console.log('Editing');
            try {
                const buggyLine = document.lineAt(session.lineNumber - 1);
                var indent = buggyLine.text.substring(0, buggyLine.firstNonWhitespaceCharacterIndex);
                if (this.getSession(document).data.stage === 'accept') {
                    editBuilder.insert(new vscode.Position(buggyLine.range.start.line, buggyLine.range.start.character + indent.length), '// ');
                }
                else {
                    indent += "// ";
                }
                editBuilder.insert(buggyLine.range.end, ' '.repeat(Math.max(0, indent.length + this.getLineLength(session.data) - buggyLine.text.length))
                    + '\n'
                    + this.formatPatches(indent, session.data));
                console.log('Edited');
                state.phase = RenderPhase.appended;
            }
            catch (ex) {
                console.log(ex);
            }
        });
    }
    getLineLength(data) {
        const longestPatchLength = data.patch_groups.reduce((a, b) => a.code.length > b.code.length ? a : b).code.length;
        const lineLength = longestPatchLength + 8;
        return lineLength;
    }
    formatPatches(indent, data) {
        let content = '';
        for (var patchGroup of data.patch_groups) {
            content += indent + patchGroup.code.padEnd(this.getLineLength(data), ' ');
            content += '\n';
        }
        content = content.substring(0, content.length - 1);
        console.log(content);
        return content;
    }
    decoratePatches(document) {
        console.log('Formatting patches');
        var editor = vscode.window.activeTextEditor;
        if (!editor) {
            return;
        }
        ;
        const session = this.getSession(document);
        const state = this.getState(document);
        state.phase = RenderPhase.decorated;
        let lineNumber = session.lineNumber;
        let failedTriggeringTestCases = -1;
        // Clear current decorations
        if (editor) {
            for (let decorationType of state.currentDecorationTypes) {
                editor.setDecorations(decorationType, []);
            }
        }
        state.currentDecorationTypes = [];
        if (vscode.workspace.getConfiguration("ipr").get("enabled") === true && document.languageId !== "Log") {
            for (let patchGroup of session.data.patch_groups) {
                patchGroup.startLineNumber = lineNumber;
                const index = 0;
                const makeAfter = (group) => {
                    const v = group.test_case;
                    {
                        return {
                            contentText: v.split('/')[1] + ' TEST PASSED',
                            color: new vscode.ThemeColor('textLink.activeForeground'),
                            fontWeight: 'bold'
                        };
                    }
                };
                const subDecorationType = vscode.window.createTextEditorDecorationType({
                    isWholeLine: true,
                    backgroundColor: new vscode.ThemeColor('list.dropBackground'),
                    // after: makeAfter(patchGroup)
                });
                state.currentDecorationTypes.push(subDecorationType);
                console.log(document.fileName);
                editor?.setDecorations(subDecorationType, [new vscode.Range(document.lineAt(lineNumber + index).range.start, document.lineAt(lineNumber + index).range.end)]);
                lineNumber += 0 + 1;
            }
            if (failedTriggeringTestCases >= 0) {
                const subDecorationType = vscode.window.createTextEditorDecorationType({
                    isWholeLine: true,
                    backgroundColor: new vscode.ThemeColor('inputValidation.errorBackground'),
                });
                state.currentDecorationTypes.push(subDecorationType);
                console.log(document.fileName);
                editor?.setDecorations(subDecorationType, [new vscode.Range(document.lineAt(session.lineNumber - 1).range.start, document.lineAt(session.lineNumber - 1).range.end)]);
            }
        }
    }
    markChangeAsOwn(editBuilder) {
        // This is such a dumb workaround.
        editBuilder.insert(new vscode.Position(0, 0), RepairDocumentRenderer.changeFlag);
    }
    provideCodeLenses(document, token) {
        console.log('Providing code lenses');
        console.log((0, Utils_1.getShortFileName)(document));
        console.log(vscode.workspace.getConfiguration("ipr").get("enabled"));
        if (vscode.workspace.getConfiguration("ipr").get("enabled") === true && document.languageId !== "Log") {
            console.log("Provide code lenses");
            const codeLenses = [];
            // TODO: Don't auto-activate, or at least don't activate the service here?
            console.log(this.service.sessions);
            if (!this.service.hasSession(document)) {
                this.service.startRepair(document);
            }
            else {
                const session = this.getSession(document);
                const state = this.getState(document);
                const line = document.lineAt(session.lineNumber - 1);
                codeLenses.push(new vscode.CodeLens(line.range, {
                    title: "$(debug-restart) Restart Repair",
                    tooltip: "Restart repair from the beginning.",
                    command: "ipr.restart-repair",
                    arguments: [document]
                }));
                console.log(line);
                // TODO: How to make this async in the future?
                if (state.phase === RenderPhase.decorated && (session.data.stage === 'cluster' || session.data.stage === 'start')) {
                    for (var patchGroup of session.data.patch_groups) {
                        codeLenses.push(new vscode.CodeLens(document.lineAt(patchGroup.startLineNumber).range, {
                            title: "$(getting-started-beginner) Explore " + patchGroup.n_similar.toString() + " similar patche(s)",
                            tooltip: "Explore similar patches.",
                            command: "ipr.explore-group",
                            arguments: [document, patchGroup]
                        }));
                        codeLenses.push(new vscode.CodeLens(document.lineAt(patchGroup.startLineNumber).range, {
                            title: "$(terminal-kill) Exclude similar patches",
                            tooltip: "Exclude similar patches.",
                            command: "ipr.exclude-group",
                            arguments: [document, patchGroup]
                        }));
                        codeLenses.push(new vscode.CodeLens(document.lineAt(patchGroup.startLineNumber).range, {
                            title: "$(check-all) Accept patch",
                            tooltip: "Accept patch.",
                            command: "ipr.accept-patch",
                            arguments: [document, patchGroup]
                        }));
                    }
                }
                else if (state.phase === RenderPhase.decorated && session.data.stage === 'patch') {
                    for (var patchGroup of session.data.patch_groups) {
                        codeLenses.push(new vscode.CodeLens(document.lineAt(patchGroup.startLineNumber).range, {
                            title: "$(check) Accept patch",
                            tooltip: "Accept patch.",
                            command: "ipr.accept-patch",
                            arguments: [document, patchGroup]
                        }));
                    }
                }
            }
            if (this.getState(document).phase === RenderPhase.appended || this.getState(document).phase === RenderPhase.decorated) {
                this.decoratePatches(document);
            }
            return codeLenses;
        }
        console.log('Do not provide code lenses');
        var state = this.getState(document);
        var editor = vscode.window.activeTextEditor;
        state.currentDecorationTypes.forEach(type => {
            editor?.setDecorations(type, []);
        });
        return [];
    }
    resolveCodeLens(codeLens, token) {
        if ((vscode.workspace.getConfiguration("ipr").get("enabled") === true)) {
            return codeLens;
        }
        return null;
    }
}
exports.RepairDocumentRenderer = RepairDocumentRenderer;
RepairDocumentRenderer.changeFlag = '########### This file is being changed by IPR. If you see this message, a bug has occurred! ###########';
//# sourceMappingURL=RepairDocumentRenderer.js.map