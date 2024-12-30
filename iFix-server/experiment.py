from patch import PatchRanking, IPR
import json

def read_benchmark_file(file_name):
    res = []
    with open(file_name, 'r') as f:
        line = f.readline()
        while line:
            if line.startswith('buggy line'):
                buggy_line = line.split(' ')[-1].strip()
            elif line.startswith('file name'):
                file_name = line.split(' ')[-1].strip()
            elif line.startswith('bug id'):
                bug_id = line.split(' ')[-1].strip()
            elif line.startswith('--------'):
                res.append({
                    'buggy_line': buggy_line,
                    'file_name': file_name,
                    'bug_id': bug_id
                })
            line = f.readline()
    return res

FILE_NAME = 'EigenDecompositionImpl.java'
BUG_ID = 'Math_80'
BUGGY_LINE = "int j = 4 * n - 1;"

def output_cluster(cluster_data, stage):
    output_data = {}
    for key, value in cluster_data.items():
        tmp = []
        for patch in value:
            tmp.append({
                'code': patch['code'],
                'test_case': patch['test_case']
            })
        output_data[key] = tmp
    with open(f'./new_result/{BUG_ID}/cluster_{BUG_ID}_{FILE_NAME}_{stage}.json', 'w') as f:
        json.dump(output_data, f, indent=4)
    print(f'INFO: Clustered patches of {FILE_NAME} have been dumped into .new_result/{BUG_ID}/cluster_{BUG_ID}_{FILE_NAME}_{stage}.json')

def output_ranked_patch(ranker_patch, stage):
    with open(f'./new_result/{BUG_ID}/ranking_{BUG_ID}_{FILE_NAME}_{stage}.txt', 'w') as f:
        for patch in ranker_patch:
            f.write(f"{patch['cluster']}: {patch['code']}\n")

def get_ranking_result(meta_data=None, cluster_id=None, explore=False):
    if meta_data is not None:
        file_name = meta_data['file_name']
        bug_id = meta_data['bug_id']
        buggy_line = meta_data['buggy_line']
    else:
        file_name = FILE_NAME
        bug_id = BUG_ID
        buggy_line = BUGGY_LINE
    ipr = IPR(file_name, bug_id, buggy_line)
    ranked_patch = ipr.patch_data[ipr.stage_id].get_ranked_patch()   # 这是要展示的
    cluster_data = ipr.patch_data[ipr.stage_id].get_cluster_data()   # 这是存个底
    cur_stage = ipr.get_stage_id()
    output_cluster(cluster_data, cur_stage)
    output_ranked_patch(ranked_patch, cur_stage)


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


get_ranking_result()
# read_benchmark_file('./data/bugs.log')