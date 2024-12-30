"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.RepairService = void 0;
/* eslint-disable @typescript-eslint/naming-convention */
const vscode = require("vscode");
const vscode_1 = require("vscode");
const Utils_1 = require("./Utils");
const md5 = require("blueimp-md5");
const axios = require('axios').default;
axios.defaults.baseURL = 'http://localhost:8000';
class RepairService {
    constructor() {
        this._onPatchesGenerated = new vscode.EventEmitter();
        this.onDidPatchesGenerated = this._onPatchesGenerated.event;
        this._onInstrumentDataGenerated = new vscode.EventEmitter();
        this.onDidInstrumentDataGenerated = this._onInstrumentDataGenerated.event;
        this.sessions = new Map();
        this.currentSession = '';
    }
    async startRepair(document) {
        await this.createSession(document);
    }
    async restartRepair(document) {
        if (!this.sessions.has(md5((0, Utils_1.getRelativePath)(document)))) {
            vscode_1.window.showErrorMessage("Repair mode has not started for this file!");
            return;
        }
        vscode_1.window.showInformationMessage("Restarting repair...");
        await this.createSession(document);
    }
    hasSession(document) {
        return this.sessions.has(md5((0, Utils_1.getRelativePath)(document)));
    }
    getSession(document) {
        return this.sessions.get(md5((0, Utils_1.getRelativePath)(document)));
    }
    getSessionFromIndex(index) {
        return this.sessions.get(index);
    }
    async createSession(document) {
        const filePath = (0, Utils_1.getRelativePath)(document);
        const projectName = (0, Utils_1.getProjectFolderName)();
        const index = md5(filePath);
        console.log('filePath');
        console.log(filePath);
        console.log(index);
        let originalDocumentText = document.getText();
        if (this.hasSession(document)) {
            originalDocumentText = this.getSession(document).originalDocumentText;
        }
        try {
            const res = await axios.post('/session', {
                project_name: projectName,
                file_path: filePath
            });
            const data = res.data;
            console.log(data);
            const session = {
                id: data.id,
                lineNumber: data.line_number,
                document: document,
                originalDocumentText: originalDocumentText,
                data: data
            };
            console.log('Session created:');
            console.log(session);
            this.sessions.set(index, session);
        }
        catch (error) {
            console.log(error);
            console.log((0, Utils_1.getShortFileName)(document) + ' does not have repair data or service is not online');
            return;
        }
        this.currentSession = index;
        vscode_1.window.showInformationMessage("Repair mode is active. The file is now read-only.");
        console.log('Patches generated. Firing event...');
        this._onPatchesGenerated.fire(document);
    }
    async exploreGroup(document, patchGroup) {
        const filePath = (0, Utils_1.getRelativePath)(document);
        const index = md5(filePath);
        console.log(filePath);
        if (!this.sessions.has(index)) {
            vscode_1.window.showErrorMessage("Repair mode has not started for this file!");
            return;
        }
        console.log('Exploring patch group: ' + patchGroup.code);
        let session = this.sessions.get(index);
        console.log(session.id);
        const res = await axios.post('/explore_group', {
            'session_id': session.id,
            'group_id': patchGroup.id
        });
        session.data = res.data;
        console.log('Session updated:');
        console.log(session);
        this.sessions.set(index, session);
        console.log('Patches generated');
        this._onPatchesGenerated.fire(document);
    }
    async excludeGroup(document, patchGroup) {
        const filePath = (0, Utils_1.getRelativePath)(document);
        const index = md5(filePath);
        console.log(filePath);
        if (!this.sessions.has(index)) {
            vscode_1.window.showErrorMessage("Repair mode has not started for this file!");
            return;
        }
        console.log('Excluding patch group: ' + patchGroup.code);
        let session = this.sessions.get(index);
        const res = await axios.post('/exclude_group', {
            'session_id': session.id,
            'group_id': patchGroup.id
        });
        session.data = res.data;
        console.log('Session updated:');
        console.log(session);
        this.sessions.set(index, session);
        console.log('Patches generated');
        this._onPatchesGenerated.fire(document);
    }
    async instrument(node) {
        const editor = vscode.window.activeTextEditor;
        if (!editor?.document) {
            return Promise.resolve([]);
        }
        const document = editor.document;
        const filePath = (0, Utils_1.getRelativePath)(document);
        const index = md5(filePath);
        if (!this.sessions.has(index)) {
            vscode_1.window.showErrorMessage("Repair mode has not started for this file!");
            return;
        }
        let session = this.sessions.get(index);
        console.log('Instrument begins:');
        console.log(document);
        console.log(session);
        const rootPath = vscode.workspace.rootPath;
        var groups = session.data.patch_groups;
        var groups_code = [];
        groups.forEach(group => {
            groups_code.push(group.code);
        });
        var groups_code_to_string = groups_code.join("##");
        let outputChannel = vscode_1.window.createOutputChannel("IPR Instrument");
        outputChannel.show(true);
        const lineNumber = node.line;
        const testId = node.id;
        const testModule = node.module;
        const testClass = testId.split(':')[0];
        const shortTestClass = testClass.substring(testClass.lastIndexOf('.') + 1);
        const testMethod = testId.split(':')[1];
        const pwd = __dirname;
        const instrumentToolLocation = pwd.substring(0, pwd.lastIndexOf('/')) + "/runtime-comp/target";
        vscode.window.showInformationMessage('Re-running test with patches...');
        var spawn = require('child_process').spawn;
        var task = spawn('mvn', ['-version']);
        var task = spawn('java', ['-jar', 'instrument.jar',
            rootPath,
            document.fileName,
            lineNumber,
            groups_code_to_string,
            testClass,
            rootPath,
            "",
            testMethod,
            rootPath + "/.ifix/ifix-trace",
            rootPath + "/.ifix/ifix-types",
            rootPath + "/.ifix/ifix-script.sh"
        ], { cwd: instrumentToolLocation });
        task.stdout.on('data', function (data) {
            outputChannel.appendLine(data.toString());
        });
        task.stderr.on('data', function (data) {
            outputChannel.appendLine(data.toString());
        });
        task.on('exit', async function (code) {
            outputChannel.appendLine('child process exited with code ' + code.toString());
            // console.log(code);
            if (code === 0) {
                const res = await axios.post('/mock_instrument', {
                    'session_id': session.id
                });
                session.variables = res.data.result;
                outputChannel.appendLine('Get table data from backend');
                console.log(session.variables);
                vscode_1.commands.executeCommand('ipr.initTables', session.variables);
            }
        });
    }
    async acceptPatch(document, patchGroup) {
        const filePath = (0, Utils_1.getRelativePath)(document);
        const index = md5(filePath);
        console.log(filePath);
        if (!this.sessions.has(index)) {
            vscode_1.window.showErrorMessage("Repair mode has not started for this file!");
            return;
        }
        console.log('Accepting Patch: ' + patchGroup.code);
        let session = this.sessions.get(index);
        session.data.stage = 'accept';
        session.data.patch_groups = [patchGroup];
        console.log('Patches generated');
        this._onPatchesGenerated.fire(document);
    }
}
exports.RepairService = RepairService;
//# sourceMappingURL=RepairService.js.map