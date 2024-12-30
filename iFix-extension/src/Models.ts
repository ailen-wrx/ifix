import * as vscode from 'vscode';

/* eslint-disable @typescript-eslint/naming-convention */
export interface PatchNode {
    code: string
    validations: PatchValidation[]

    sampling_prob: number
    sampled: boolean

    excluded: boolean
    sample_root: boolean
    pivot: boolean
}

export interface PatchValidation {
    result: ValidationResult
    failed_triggering_test_cases_before: number
    failed_triggering_test_cases_after: number
    failed_non_triggering_test_cases: number
}

export enum ValidationResult {
    Plausible = 1,
    Wrong = 2,
    Uncompilable = 3,
    Timeout = 4
}

export interface PatchGroup {
    id: number
    code: string
    test_case: string
    n_similar: number

    startLineNumber?: number
}

export interface FailedTest {
    line: number
    module: string
    id: string
    error_msg: string
}

export interface Variable {
    stage: string
    type: string
    name: string
    value: string
}

export interface RepairSession {
    id: number,
    lineNumber: number

    data: RepairSessionData
    document: vscode.TextDocument
    originalDocumentText: string
    variables?: Variable[]
}

export interface RepairSessionData {
    stage: string
    line_number: number
    patch_groups: PatchGroup[]
    failed_tests: FailedTest[]
}

export interface TableContent {
    title: string
    lines: string[]
    collapse: boolean
    variables: any[]
}