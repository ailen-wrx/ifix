from patch import PatchRanking, IPR
from config import *
from new_utils import *
import json
import copy
import javalang

def read_benchmark_file(file):
    res = []
    with open(file, 'r') as f:
        line = f.readline()
        while line:
            if line.startswith('buggy line'):
                buggy_line = line.split(' ')[-1].strip()
            elif line.startswith('file_name'):
                file_name = line.split(' ')[-1].strip()
            elif line.startswith('bug id'):
                bug_id = line.split(' ')[-1].strip()
            elif line.startswith('correct patch'):
                correct_patch = line.split(' ')[-1].strip()
            elif line.startswith('--------'):
                res.append({
                    'buggy_line': buggy_line,
                    'file_name': file_name,
                    'bug_id': bug_id,
                    'correct_patch': correct_patch
                })
            line = f.readline()
    return res

def output_ranked_patch(ranker_patch, bug_id, file_name):
    with open(f'./new_result/{bug_id}/baseline_rank.log', 'w') as f:
        for patch in ranker_patch:
            f.write(f"{patch['code']}\n")

def read_patch(file_name, bug_id):
    with open(f'./temp/{file_name}_{bug_id}.json', 'r') as f:
        data = json.load(f)
    return data

def prepro_patch(patch_data):
    wrong_patches = []
    plausible_patches = []

    error_cnt = 0
    other_cnt = 0

    for patch in patch_data['patches']:
        if patch["correctness"] in LOW_PRIORITY:
            error_cnt += 1
        elif patch["correctness"] in MEDIUM_PROORITY:
            wrong_patches.append({
                'code': patch["patch"],
                'score': patch['score'],
                'test_case': f'{patch["failed_triggering"]}/{patch["failed_non_triggering"]}'
            })
        elif patch["correctness"] in HIGH_PRIORITY:
            plausible_patches.append({
                'code': patch["patch"],
                'score': patch['score'],
                'test_case': f'{patch["failed_triggering"]}/{patch["failed_non_triggering"]}'
            })
        else:
            other_cnt += 1
            print(f'ERROR: New correctness level: {patch["correctness"]} was found, \
                please consider update your code! ')
    return plausible_patches, wrong_patches

def our_ranking_result(file_name, bug_id, plausible_patches, buggy_line):
    parsed_buggy_line = list(javalang.tokenizer.tokenize(buggy_line))
    tmp_patch = copy.deepcopy(plausible_patches)
    for patch in tmp_patch:
        parsed_patch = list(javalang.tokenizer.tokenize(patch['code']))
        patch['rk_score'] = levenshtein_distance(parsed_patch, parsed_buggy_line)
    tmp_patch.sort(key=lambda x: x['rk_score'])
    output_ranked_patch(tmp_patch, bug_id, file_name)
    return tmp_patch


def cure_ranking_result(file_name, bug_id, plausible_patches):
    tmp_patch = copy.deepcopy(plausible_patches)
    print(tmp_patch[0])
    tmp_patch.sort(key=lambda x: x['score'], reverse=True)
    output_ranked_patch(tmp_patch, bug_id, file_name)
    return tmp_patch

def main():
    res = read_benchmark_file('./data/bugs_2.log')
    for bug in res:
        print(bug['bug_id'])
        patch_data = read_patch(bug['file_name'], bug['bug_id'])
        plausible_patches, wrong_patches = prepro_patch(patch_data)
        # cure_ranking_result(bug['file_name'], bug['bug_id'], plausible_patches)
        our_ranking_result(bug['file_name'], bug['bug_id'], plausible_patches, bug['buggy_line'])

if __name__ == "__main__":
    main()
