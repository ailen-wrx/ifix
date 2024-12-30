import copy

from utils.ranking import *
from utils.utils import *

def simple_ranking_result(file_name, bug_id, buggy_line):
    # parsed_buggy_line = list(javalang.tokenizer.tokenize(buggy_line))
    plausible_patches = get_patch_list(file_name, bug_id)
    parsed_buggy_line = get_buggy_line(buggy_line)
    tmp_patch = copy.deepcopy(plausible_patches)
    for patch in tmp_patch:
        # parsed_patch = list(javalang.tokenizer.tokenize(patch['code']))
        patch['rk_score'] = levenshtein_distance(patch['parsed_token'], parsed_buggy_line['parsed_token'])
    tmp_patch.sort(key=lambda x: x['rk_score'])
    # output_ranked_patch(tmp_patch, bug_id, file_name)
    output_ranked_patch(bug_id, tmp_patch, 'SIMPLE_RANK')
    return tmp_patch


def SIMPLERANK_test():
    with open('./data/bug_info.json', 'r') as f:
        bug_info = json.load(f)
        for bi in bug_info:
            simple_ranking_result(bi['FILE_NAME'], bi['BUG_ID'], bi['BUGGY_LINE'])