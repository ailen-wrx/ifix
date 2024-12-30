import json
from utils.utils import *

def cure_ranking_result(file_name, bug_id):
    plausible_patches = get_patch_list(file_name, bug_id, False)
    output_ranked_patch(bug_id, plausible_patches, 'CURE', 'CURE')


def CURE_test():
    with open('./data/bug_info.json', 'r') as f:
        bug_info = json.load(f)
        for bi in bug_info:
            cure_ranking_result(bi['FILE_NAME'], bi['BUG_ID'])