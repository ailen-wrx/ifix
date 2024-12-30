/* eslint-disable @typescript-eslint/naming-convention */
import * as vscode from 'vscode';
import { commands, window } from 'vscode';
import { PatchGroup, RepairSession } from './Models';
import { TestInfoProvider, FailedTestInfoItem } from './TestInfoProvider';
import { getShortFileName, getRelativePath, getProjectFolderName } from './Utils';
import md5 = require('blueimp-md5');
const axios = require('axios').default;
axios.defaults.baseURL = 'http://localhost:8000';

export class RepairService {

    sessions: Map<string, RepairSession>;
    currentSession: string;

    private _onPatchesGenerated: vscode.EventEmitter<vscode.TextDocument> = new vscode.EventEmitter<vscode.TextDocument>();
    public readonly onDidPatchesGenerated: vscode.Event<vscode.TextDocument> = this._onPatchesGenerated.event;
    private _onInstrumentDataGenerated: vscode.EventEmitter<vscode.Terminal> = new vscode.EventEmitter<vscode.Terminal>();
    public readonly onDidInstrumentDataGenerated: vscode.Event<vscode.Terminal> = this._onInstrumentDataGenerated.event;
    constructor() {
        this.sessions = new Map<string, RepairSession>();
        this.currentSession = '';
    }

    public async startRepair(document: vscode.TextDocument) {
        await this.createSession(document);
    }

    public async restartRepair(document: vscode.TextDocument) {
        if (!this.sessions.has(md5(getRelativePath(document)))) {
            window.showErrorMessage("Repair mode has not started for this file!");
            return;
        }

        window.showInformationMessage("Restarting repair...");
        await this.createSession(document);
    }

    public hasSession(document: vscode.TextDocument) {
        return this.sessions.has(md5(getRelativePath(document)));
    }

    public getSession(document: vscode.TextDocument) {
        return this.sessions.get(md5(getRelativePath(document)))!;
    }

    public getSessionFromIndex(index: string) {
        return this.sessions.get(index)!;
    }

    public async createSession(document: vscode.TextDocument) {
        const filePath = getRelativePath(document);
        const projectName = getProjectFolderName();
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
        } catch (error) {
            console.log(error);
            console.log(getShortFileName(document) + ' does not have repair data or service is not online');
            return;
        }
        this.currentSession = index;

        window.showInformationMessage("Repair mode is active. The file is now read-only.");
        console.log('Patches generated. Firing event...');
        this._onPatchesGenerated.fire(document);
    }

    public async exploreGroup(document: vscode.TextDocument, patchGroup: PatchGroup) {
        const filePath = getRelativePath(document);
        const index = md5(filePath);
        console.log(filePath);
        if (!this.sessions.has(index)) {
            window.showErrorMessage("Repair mode has not started for this file!");
            return;
        }

        console.log('Exploring patch group: ' + patchGroup.code);
        let session = this.sessions.get(index)!;
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

    public async excludeGroup(document: vscode.TextDocument, patchGroup: PatchGroup) {
        const filePath = getRelativePath(document);
        const index = md5(filePath);
        console.log(filePath);
        if (!this.sessions.has(index)) {
            window.showErrorMessage("Repair mode has not started for this file!");
            return;
        }

        console.log('Excluding patch group: ' + patchGroup.code);

        let session = this.sessions.get(index)!;
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

    public async instrument(node: FailedTestInfoItem) {
        const editor = vscode.window.activeTextEditor;
        if (!editor?.document) {
            return Promise.resolve([]);
        }
        const document = editor.document;

        const filePath = getRelativePath(document);
        const index = md5(filePath);

        if (!this.sessions.has(index)) {
            window.showErrorMessage("Repair mode has not started for this file!");
            return;
        }

        let session = this.sessions.get(index)!;
        console.log('Instrument begins:');
        console.log(document);
        console.log(session);

        const rootPath = vscode.workspace.rootPath as string;
        var groups = session.data.patch_groups;
        
        var groups_code: string[] = [];
        groups.forEach(group => {
            groups_code.push(group.code);
        });
        var groups_code_to_string = groups_code.join("##");

        let outputChannel = window.createOutputChannel("IPR Instrument");
        outputChannel.show(true);

        const lineNumber = node.line as number;
        const testId = node.id as String;
        const testModule = node.module as String;

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
            ], 
            { cwd: instrumentToolLocation });
        
        task.stdout.on('data', function (data: any) {
            outputChannel.appendLine(data.toString());
        });
        task.stderr.on('data', function (data: any) {
            outputChannel.appendLine(data.toString());
        });
        task.on('exit', async function (code: any) {
            outputChannel.appendLine('child process exited with code ' + code.toString());
            // console.log(code);
            if (code === 0) 
            {
                const res = await axios.post('/mock_instrument', {
                    'session_id': session.id
                });
                session.variables = res.data.result;
                outputChannel.appendLine('Get table data from backend');
                console.log(session.variables);
                commands.executeCommand('ipr.initTables', session.variables);
            }
        });

    }
    

    public async acceptPatch(document: vscode.TextDocument, patchGroup: PatchGroup) {
        const filePath = getRelativePath(document);
        const index = md5(filePath);
        console.log(filePath);
        if (!this.sessions.has(index)) {
            window.showErrorMessage("Repair mode has not started for this file!");
            return;
        }

        console.log('Accepting Patch: ' + patchGroup.code);
        let session = this.sessions.get(index)!;
        session.data.stage = 'accept';
        session.data.patch_groups = [patchGroup];

        console.log('Patches generated');
        this._onPatchesGenerated.fire(document);
    }


}