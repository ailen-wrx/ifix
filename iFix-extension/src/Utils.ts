import * as vscode from 'vscode';
import path = require('path');
import { TableContent } from './Models';


export function getShortFileName(document: vscode.TextDocument) {
    console.log(document.fileName);
    console.log(document.languageId);
    return document.fileName.substring(document.fileName.lastIndexOf(path.sep) + 1);
}

export function getRelativePath(document: vscode.TextDocument) {
    const rootPath = vscode.workspace.rootPath as string;
    return document.fileName.substring(rootPath.length + 1, document.fileName.length);
}

export function getProjectFolderName() {
    const rootPath = vscode.workspace.rootPath as string;
    return rootPath.substring(rootPath.lastIndexOf(path.sep) + 1);
}

export const mockupTables = [
    {
        title: 'MannWhitneyUTest.calculateAsymptoticPValue(double,int,int) ',
        lines: ['buggy #173', 'patch1 #174', 'patch2 #175', 'patch3 #176', 'patch4 #177', 'patch5 #178'],
        collapse: 0,
        variables: [
        {
            name: 'Umin', 
            identical: 0,
            values: ['1124250.000000', '1124250.000000', '1124250.000000', '1124250.000000', '1124250.000000', '1124250.000000']
        },
        {
            name: 'n1',
            identical: 0,
            values: ['1500', '1500', '1500', '1500', '1500', '1500'],
            position: {
                url: 'src/main/java/org/apache/commons/math3/stat/inference/MannWhitneyUTest.java',
                line: 169
            }
        },
        {
            name: 'n2',
            identical: 0,
            values: ['1500', '1500', '1500', '1500', '1500', '1500']
        },
        {
            name: 'n1n2prod',
            identical: 1,
            values: ['2250000', '2250000.000000', '2250750.000000', '2250000.000000', '6002', '2250000.000000']
        },
        {
            name: 'EU',
            identical: 1,
            values: ['1125000.000000', '1125000.000000', '1125375.000000', '1125000.000000', '3001.000000', '1125000.000000']
        },
        {
            name: 'VarU',
            identical: 1,
            values: ['-153140382.666667', '562687500.000000', '562875062.500000', '562687500.000000', '1501000.166667', '562687500.000000']
        },
        {
            name: 'z',
            identical: 1,
            values: ['NaN', '-0.031618', '-0.047418', '-0.031618', '915.190911', '-0.031618']
        },
        {
            name: '_return_',
            identical: 1,
            values: ['NaN', '0.974777', '0.962180', '0.974777', '2.000000', '0.974777']
        }
    ]},
    {
        title: 'MannWhitneyUTest.mannWhitneyUTest(double[],double[]) ',
        lines: ['buggy #173', 'patch1 #174', 'patch2 #175', 'patch3 #176', 'patch4 #177', 'patch5 #178'],        
        collapse: 1,
        variables: [
        {
            name: 'Umin',
            identical: 0,
            values: ['1124250.000000', '1124250.000000', '1124250.000000', '1124250.000000', '1124250.000000', '1124250.000000']
        },
        {
            name: 'x',
            identical: 0,
            values: ['double[1500]', 'double[1500]', 'double[1500]', 'double[1500]', 'double[1500]', 'double[1500]']
        },
        {
            name: 'y',
            identical: 0,
            values: ['double[1500]', 'double[1500]', 'double[1500]', 'double[1500]', 'double[1500]', 'double[1500]']
        },
        {
            name: '_return_',
            identical: 1,
            values: ['NaN', '0.974777', '0.962180', '0.974777', '2.000000', '0.974777']
        }
    ]},
    {
        title: 'MannWhitneyUTestTest.testBigDataSet() ',
        lines: ['buggy #173', 'patch1 #174', 'patch2 #175', 'patch3 #176', 'patch4 #177', 'patch5 #178'],        
        collapse: 1,
        variables: [
        {
            name: 'd1',
            identical: 0,
            values: ['double[1500]', 'double[1500]', 'double[1500]', 'double[1500]', 'double[1500]', 'double[1500]']
        },
        {
            name: 'd2',
            identical: 0,
            values: ['double[1500]', 'double[1500]', 'double[1500]', 'double[1500]', 'double[1500]', 'double[1500]']
        },
        {
            name: 'result',
            identical: 1,
            values: ['NaN', '0.974777', '0.962180', '0.974777', '2.000000', '0.974777']
        },
        {
            name: '_assert_',
            identical: 1,
            values: ['False', 'True', 'True', 'True', 'True', 'True']
        }
    ]}
];