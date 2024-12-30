import json
import javalang
import copy
from utils.ranking import *
from experiment_patch import PatchRanking, IPR


def get_parsed_code(code):
    tokens = javalang.tokenizer.tokenize(code)
    try:
        parsed_code = list(tokens)
        return parsed_code
    except TypeError:
        print(code)
        return []

def rr_get_patch_list(bug_id, parsed=True):
    f = open(f'./RewardRepairPatches/plausible-{bug_id}.json', 'r')
    patch_data = json.load(f)
    plausible_patches = []
    for patch in patch_data:
        if patch["correctness"] == 'plausible':
            if parsed: 
                parsed_patch = get_parsed_code(patch["patch"])
                plausible_patches.append({
                    'code': patch["patch"],
                    'parsed_token': parsed_patch,
                })
            else:
                plausible_patches.append({
                    'code': patch["patch"],
                    'test_case': '0/0'
                })
    return plausible_patches

def rr_get_buggy_line(buggy_line, parsed=True):
    if parsed:
        parsed_buggy_line = get_parsed_code(buggy_line)
        return {
            'code': buggy_line,
            'parsed_token': parsed_buggy_line
        }
    else:
        return {
            'code': buggy_line
        }

def rr_output_ranked_patch(bug_id, ranked_patch, prompt, format='normal'):
    with open(f'./result/RewardRepair/{bug_id}/{prompt}_rank.java', 'w') as f:
        if format == 'normal':
            for patch in ranked_patch:
                f.write(f"{patch['code']}\n")
        elif format == 's3_kv':
            for key, value in ranked_patch.items():
                f.write(f"{value}: {key}\n")

def rr_simple_ranking_result(bug_id, buggy_line):
    # parsed_buggy_line = list(javalang.tokenizer.tokenize(buggy_line))
    plausible_patches = rr_get_patch_list(bug_id)
    parsed_buggy_line = rr_get_buggy_line(buggy_line)
    tmp_patch = copy.deepcopy(plausible_patches)
    for patch in tmp_patch:
        patch['rk_score'] = levenshtein_distance(patch['parsed_token'], parsed_buggy_line['parsed_token'])
    tmp_patch.sort(key=lambda x: x['rk_score'])
    rr_output_ranked_patch(bug_id, tmp_patch, 'SIMPLE_RANK')
    return tmp_patch

def RewardRepair_ranking_result(bug_id):
    plausible_patches = rr_get_patch_list(bug_id, False)
    rr_output_ranked_patch(bug_id, plausible_patches, 'RewardRepair')


def output_cluster(cluster_data, bug_id, stage):
    output_data = {}
    for key, value in cluster_data.items():
        tmp = []
        for patch in value:
            tmp.append({
                'code': patch['code'],
                'test_case': patch['test_case']
            })
        output_data[key] = tmp
    with open(f'./result/RewardRepair/{bug_id}/cluster_{stage}.json', 'w') as f:
        json.dump(output_data, f, indent=4)
    print(f'INFO: Clustered patches of {bug_id} have been dumped')

def output_ranked_patch(ranker_patch, bug_id, stage):
    with open(f'./result/RewardRepair/{bug_id}/MCR_{stage}.java', 'w') as f:
        for patch in ranker_patch:
            f.write(f"{patch['cluster']}: {patch['code']}\n")


    # cluster_id = 'cluster_4'
    # cur_stage = ipr.get_stage_id()
    # next_stage = cur_stage + '_' + cluster_id.split('_')[-1]
    # ipr.set_patch_data(next_stage, cluster_data[cluster_id])
    # ipr.set_stage_id(next_stage)
    # ipr.set_cluster_dist()
    # ranked_patch_new = ipr.patch_data[ipr.stage_id].get_ranked_patch()
    # cluster_data_new = ipr.patch_data[ipr.stage_id].get_cluster_data()
    # output_cluster(cluster_data_new, next_stage)
    # output_ranked_patch(ranked_patch_new, next_stage)


def RewardRepair_MCR_ranking_result(file_name, bug_id, buggy_line):
    plausible_patches = rr_get_patch_list(bug_id, False)
    ipr = IPR(file_name, bug_id, buggy_line, plausible_patches)
    ranked_patch = ipr.patch_data[ipr.stage_id].get_ranked_patch()   
    cluster_data = ipr.patch_data[ipr.stage_id].get_cluster_data()   
    cur_stage = ipr.get_stage_id()
    output_cluster(cluster_data, bug_id, cur_stage)
    output_ranked_patch(ranked_patch, bug_id, cur_stage)


def RewardRepair_test():
    with open('./data/RR_bug_info.json', 'r') as f:
        bug_info = json.load(f)
        for bi in bug_info:
            if bi['BUG_ID'] in []:
                continue
            RewardRepair_MCR_ranking_result(bi['FILE_NAME'], bi['BUG_ID'], bi['BUGGY_LINE'])
            # RewardRepair_ranking_result(bi['BUG_ID'])
            # rr_simple_ranking_result(bi['BUG_ID'], bi['BUGGY_LINE'])