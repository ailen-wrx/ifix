from patch import PatchRanking, IPR
import json
from utils.utils import *

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
    with open(f'./result/CURE/{bug_id}/cluster_{stage}.json', 'w') as f:
        json.dump(output_data, f, indent=4)
    print(f'INFO: Clustered patches of {bug_id} have been dumped')

def output_ranked_patch(ranker_patch, bug_id, stage):
    with open(f'./result/CURE/{bug_id}/MCR_{stage}.java', 'w') as f:
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

def MCR_ranking_result(file_name, bug_id, buggy_line):
    ipr = IPR(file_name, bug_id, buggy_line)
    ranked_patch = ipr.patch_data[ipr.stage_id].get_ranked_patch()   
    cluster_data = ipr.patch_data[ipr.stage_id].get_cluster_data() 
    cur_stage = ipr.get_stage_id()
    output_cluster(cluster_data, bug_id, cur_stage)
    output_ranked_patch(ranked_patch, bug_id, cur_stage)

    cluster_id = 'cluster_1'
    cur_stage = ipr.get_stage_id()
    next_stage = cur_stage + '_' + cluster_id.split('_')[-1]
    ipr.set_patch_data(next_stage, cluster_data[cluster_id])
    ipr.set_stage_id(next_stage)
    ipr.set_cluster_dist()
    ranked_patch_new = ipr.patch_data[ipr.stage_id].get_ranked_patch()
    cluster_data_new = ipr.patch_data[ipr.stage_id].get_cluster_data()
    output_cluster(cluster_data_new, bug_id, next_stage)
    output_ranked_patch(ranked_patch_new, bug_id, next_stage)
    return


def MCR_test():
    with open('./data/bug_info.json', 'r') as f:
        bug_info = json.load(f)
        for bi in bug_info:
            MCR_ranking_result(bi['FILE_NAME'], bi['BUG_ID'], bi['BUGGY_LINE'])

if __name__ == '__main__':
    MCR_test()