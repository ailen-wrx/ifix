import json
import copy
import subprocess
import os
import numpy as np
from utils.utils import *

CONSTANT_TYPE = [
    'Integer', 'DecimalInteger', 'OctalInteger', 'BinaryInteger', 'HexInteger',
    'FloatingPoint', 'DecimalFloatingPoint', 'HexFloatingPoint',
    'Boolean',
    'Character', 'String'
    ]

VARIABLE_TYPE = ['Identifier']

def get_variables(parsed_code):
    variables = []
    for token in parsed_code:
        if token.__class__.__name__ in VARIABLE_TYPE + CONSTANT_TYPE:
            variables.append(token.value)
    return variables

def nodetype_occurrence(parsed_code):
    nodetype_occurrence = {}
    for token in parsed_code:
        if token.__class__.__name__ in nodetype_occurrence.keys():
            nodetype_occurrence[token.__class__.__name__] += 1
        else:
            nodetype_occurrence[token.__class__.__name__] = 1
    return nodetype_occurrence

def read_context(bug_id, file_name):
    with open(f'./context/{bug_id}/{file_name}', 'r') as f:
        context = f.readlines()
    return context

def execute_gumtree(file_path1, file_path2, output_path):
    command = f'gumtree-3.0.0/bin/gumtree textdiff {file_path1} {file_path2} -o {output_path} -f JSON'
    res = subprocess.run(command, shell=True, capture_output=True)
    output = res.stdout.decode()

def write_patched_context(patched_path, context, line_number, patch):
    # replace buggy line with patch
    patched_context = context
    patched_context[line_number - 1] = patch + '\n'

    parent_dir = os.path.dirname(patched_path)
    if not os.path.exists(parent_dir):
        os.makedirs(parent_dir)
    with open(f'{patched_path}', 'w') as f:
        f.writelines(patched_context)

def S3_ASTDist(bug_id, file_name, line_number, p_buggy_line, p_patch_list):
    context = read_context(bug_id, file_name)
    # check buggy line number
    try:
        if context[line_number - 1].strip() != p_buggy_line['code'].strip():
            print(bug_id)
            return
    except IndexError:
        print(f'{bug_id}: IndexError: list index out of range')
        return
    
    score_res = {}
    # get current path
    current_path = os.getcwd()

    for patch in p_patch_list:
        patch_hash = hash(patch['code'])
        buggy_patch = f'{current_path}/context/{bug_id}/{file_name}'
        patched_patch = f"{current_path}/patched_context/{bug_id}/{patch_hash}.java"
        output_path = f"{current_path}/patched_context/{bug_id}/{patch_hash}.json"
        write_patched_context(patched_patch, context, line_number, patch['code'])
        # execute gumtree
        execute_gumtree(buggy_patch, patched_patch, output_path)

        #todo: read files
        with open(f'{output_path}') as f:
            ast_difference = json.load(f)
            # get number of actions
            actions = ast_difference['actions']
            score_res[patch['code']] = len(actions)
    
    # sort by number of actions
    rank_res = dict(sorted(score_res.items(), key=lambda item: item[1]))

    # output result
    output_ranked_patch(bug_id, rank_res, 'S3_ASTDist', 's3_kv')

    return score_res

def S3_ASTCosDist(bug_id, p_buggy_line, p_patch_list):
    score_res = {}
    buggy_line_nto = nodetype_occurrence(p_buggy_line['parsed_token'])
    for patch in p_patch_list:
        patch_nto = nodetype_occurrence(patch['parsed_token'])
        # deep copy
        tmp_bl_nto = copy.deepcopy(buggy_line_nto)
        tmp_p_nto = copy.deepcopy(patch_nto)

        # align
        for key in tmp_bl_nto.keys():
            if key not in tmp_p_nto.keys():
                tmp_p_nto[key] = 0
        for key in tmp_p_nto.keys():
            if key not in tmp_bl_nto.keys():
                tmp_bl_nto[key] = 0
        
        # sort by key
        tmp_bl_nto = dict(sorted(tmp_bl_nto.items(), key=lambda item: item[0]))
        tmp_p_nto = dict(sorted(tmp_p_nto.items(), key=lambda item: item[0]))

        # vectorize
        bl_vec = []
        p_vec = []
        for key in tmp_bl_nto.keys():
            bl_vec.append(tmp_bl_nto[key])
            p_vec.append(tmp_p_nto[key])
        
        # transform to numpy array
        bl_vec = np.array(bl_vec)
        p_vec = np.array(p_vec)

        # calculate cosine distance
        sim = (np.dot(bl_vec, p_vec) / (np.linalg.norm(bl_vec) * np.linalg.norm(p_vec)))
        dist = 1 - sim
        score_res[patch['code']] = dist
    
    # sort by distance
    rank_res = dict(sorted(score_res.items(), key=lambda item: item[1]))
    
    # output result
    output_ranked_patch(bug_id, rank_res, 'S3_ASTCosDist', 's3_kv')

    return score_res

def S3_VariableDist(bug_id, p_buggy_line, p_patch_list):
    score_res = {}
    buggy_line_var = get_variables(p_buggy_line['parsed_token'])
    for patch in p_patch_list:
        patch_var = get_variables(patch['parsed_token'])

        # deep copy
        tmp_bl_var = copy.deepcopy(buggy_line_var)
        tmp_p_var = copy.deepcopy(patch_var)

        # padding
        if len(tmp_bl_var) > len(tmp_p_var):
            tmp_p_var += ['xx--^^4321'] * (len(tmp_bl_var) - len(tmp_p_var))
        elif len(tmp_bl_var) < len(tmp_p_var):
            tmp_bl_var += ['xx--^^4321'] * (len(tmp_p_var) - len(tmp_bl_var))
        
        # calculate hamming distance
        dist = 0
        for i in range(len(tmp_bl_var)):
            if tmp_bl_var[i] != tmp_p_var[i]:
                dist += 1
    
        score_res[patch['code']] = dist
    
    # sort by distance
    rank_res = dict(sorted(score_res.items(), key=lambda item: item[1]))

    # output result
    output_ranked_patch(bug_id, rank_res, 'S3_VariableDist', 's3_kv')

    # note that this return value is for the whole rank of S3
    return score_res

def S3_Dist(bug_id, ASTDist_res, ASTCosDist_res, VariableDist_res): 
    s3_res = {}
    for key in ASTDist_res.keys():
        assert ASTDist_res.keys() == ASTCosDist_res.keys() == VariableDist_res.keys()
        s3_res[key] = ASTDist_res[key] + ASTCosDist_res[key] + VariableDist_res[key]
    # sort by distance
    rank_res = dict(sorted(s3_res.items(), key=lambda item: item[1]))

    # output result
    output_ranked_patch(bug_id, rank_res, 'S3', 's3_kv')

    # note that this return value is for the whole rank of S3
    return s3_res

def S3_test():
    with open('./data/bug_info.json', 'r') as f:
        bug_info = json.load(f)
        for bi in bug_info:
            print(f"Running {bi['BUG_ID']}.")
            plausible_patches = get_patch_list(bi['FILE_NAME'], bi['BUG_ID'])
            parsed_buggy_line = get_buggy_line(bi['BUGGY_LINE'])
            ASTDist_res = S3_ASTDist(bi['BUG_ID'], bi['FILE_NAME'], bi['LINE_NUMBER'], parsed_buggy_line, plausible_patches)
            ASTCosDist_res = S3_ASTCosDist(bi['BUG_ID'], parsed_buggy_line, plausible_patches)
            VariableDist_res = S3_VariableDist(bi['BUG_ID'], parsed_buggy_line, plausible_patches)
            S3_res = S3_Dist(bi['BUG_ID'], ASTDist_res, ASTCosDist_res, VariableDist_res)
            print(f"{bi['BUG_ID']} complete.")
