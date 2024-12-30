import os
import json
import copy
from unittest.mock import patch
import javalang
from easydict import EasyDict
import scipy.cluster.hierarchy as shc
from matplotlib import pyplot as plt
import numpy as np

LOW_PRIORITY = ['uncompilable', 'timeout']
MEDIUM_PROORITY = ['wrong']
HIGH_PRIORITY = ['plausible']

CLUSTER_NUM = 3
DISTANCE_THRES = 4

FILE_NAME = ""
BUG_ID = ""
BUGGY_LINE = ""

RES_DIR = 'result'


def get_oracle(id):
    if id == "Lang_6":
        return {
            'LINE_NUM': 95,
            'FAILED_TESTS': [
    {
        'line': 95,
        'module': '',
        'id': 'org.apache.commons.lang3.StringUtilsTest:testEscapeSurrogatePairs',
        'error_msg': '''java.lang.StringIndexOutOfBoundsException: String index out of range: 2
 at java.lang.String.charAt(String.java:658)
 at java.lang.Character.codePointAt(Character.java:4884)
 at org.apache.commons.lang3.text.translate.CharSequenceTranslator.translate(CharSequenceTranslator.java:95)
 at org.apache.commons.lang3.text.translate.CharSequenceTranslator.translate(CharSequenceTranslator.java:59)
 at org.apache.commons.lang3.StringEscapeUtils.escapeCsv(StringEscapeUtils.java:556)
 at org.apache.commons.lang3.StringUtilsTest.testEscapeSurrogatePairs(StringUtilsTest.java:2187)'''
    }
],
            'STACK_TRACES': [
    {
        'id': 'CharSequenceTranslator.translate(CharSequence, Writer)',
        'file': '/src/main/java/org/apache/commons/lang3/text/translate/CharSequenceTranslator.java',
        'line': 95
    },
    {
        'id': 'CharSequenceTranslator.translate(CharSequence)',
        'file': '/src/main/java/org/apache/commons/lang3/text/translate/CharSequenceTranslator.java',
        'line': 59
    },
    {
        'id': 'StringEscapeUtils.escapeCsv(String)',
        'file': '/src/main/java/org/apache/commons/lang3/StringEscapeUtils.java',
        'line': 556
    },
    {
        'id': 'StringUtilsTest.testEscapeSurrogatePairs()',
        'file': '/src/test/java/org/apache/commons/lang3/StringUtilsTest.java',
        'line': 2187
    }
]
        }
    if id == "Math_30":
        return {
            'LINE_NUM': 173,
            'FAILED_TESTS': [{
                'line': 173,
                'module': '',
                'id': 'org.apache.commons.math3.stat.inference.MannWhitneyUTestTest:testBigDataSet',
                'error_msg': '''java.lang.AssertionError
at org.apache.commons.math3.stat.inference.MannWhitneyUTestTest.testBigDataSet(MannWhitneyUTestTest.java:113)'''
            }],
            'STACK_TRACES': [
            {
                'id': 'MannWhitneyUTest.calculateAsymptoticPValue(double,int,int)',
                'file': '/src/main/java/org/apache/commons/math3/stat/inference/MannWhitneyUTest.java',
                'line': 173
            },
            {
                'id': 'MannWhitneyUTest.mannWhitneyUTest(double[],double[])',
                'file': '/src/main/java/org/apache/commons/math3/stat/inference/MannWhitneyUTest.java',
                'line': 231
            },
            {
                'id': 'MannWhitneyUTestTest.testBigDataSet()',
                'file': '/src/test/java/org/apache/commons/math3/stat/inference/MannWhitneyUTestTest.java',
                'line': 112
            }
        ]
        }
    if id == "Chart_9":
        return {
            'LINE_NUM': 1071,
            'FAILED_TESTS': [
                {
                    'line': 1071,
                    'module': '',
                    'id': 'org.jfree.data.time.TimeSeriesTest:testBug1864222',
'error_msg': '''java.lang.IllegalArgumentException: Requires start [= end.
at org.jfree.chart/org.jfree.data.time.TimeSeries.createCopy(TimeSeries.java:1013)
at org.jfree.chart/org.jfree.data.time.TimeSeries.createCopy(TimeSeries.java:1076)
at org.jfree.chart/org.jfree.data.time.TimeSeriesTest.testBug1864222(TimeSeriesTest.java:864)
at java.base/java.util.ArrayList.forEach(ArrayList.java:1541)
at java.base/java.util.ArrayList.forEach(ArrayList.java:1541)'''
                }
            ],
            'STACK_TRACES': [
                {
                    'id': 'TimeSeries.createCopy(RegularTimePeriod, RegularTimePeriod)',
                    'file': '/src/main/java/org/jfree/data/time/TimeSeries.java',
                    'line': 1071
                },
                {
                    'id': 'TimeSeriesTest.testBug1864222()',
                    'file': '/src/test/java/org/jfree/data/time/TimeSeriesTest.java',
                    'line': 864
                }
            ]
        }
    if id == "Math_94":
            return {
                'LINE_NUM': 412,
                'FAILED_TESTS': [
                    {
                        'line': 412,
                        'module': '',
                        'id': 'org.apache.commons.math.util.MathUtilsTest:testGcd',
                        'error_msg': '''junit.framework.AssertionFailedError: 
expected:<98304> but was:<3440640>'''
                   }
                ],
                'STACK_TRACES': [
                    {
                        'id': 'MathUtils.gcd(int, int)',
                        'file': '/src/java/org/apache/commons/math/util/MathUtils.java',
                        'line': 412
                    },
                    {
                        'id': 'MathUtilsTest.testGcd()',
                        'file': '/src/test/org/apache/commons/math/util/MathUtilsTest.java',
                        'line': 274
                    }
                ]
            }

    return None



def compare_test_case(patch):
    test_case = patch['test_case'].split('/')
    return test_case[0] + test_case[-1]


# Only need to be invoked one time
def transform_data(patch_file='./validate-update/validate_result.json'):
    with open(patch_file, 'r') as f:
        data = json.load(f)

    file_list = []
    for key in list(data.keys()):
        file_name = key.split('/')[-1].split('_')[0]
        bug_id = key.split('/')[0][:-1]
        file_list.append((file_name, bug_id))
        with open(f'./temp/{file_name}_{bug_id}.json', 'w') as f:
            json.dump(data[key], f, indent=4)
        print(f'INFO: Dumped {file_name}\'s patch data into ./temp/{file_name}_{bug_id}.json')

    return file_list


def read_patch(file_name=FILE_NAME, bug_id=BUG_ID):
    with open(f'./temp/{file_name}_{bug_id}.json', 'r') as f:
        data = json.load(f)
    return data


def prepro_patch(patch_data, debug=False):
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
                # 'score': patch['score'],
                'test_case': f'{patch["failed_triggering"]}/{patch["failed_non_triggering"]}'
            })
        elif patch["correctness"] in HIGH_PRIORITY:
            plausible_patches.append({
                'code': patch["patch"],
                # 'score': patch['score'],
                'test_case': f'{patch["failed_triggering"]}/{patch["failed_non_triggering"]}'
            })
        else:
            other_cnt += 1
            print(f'ERROR: New correctness level: {patch["correctness"]} was found, \
                please consider update your code! ')
    if debug:
        print(f'Patches in {FILE_NAME}_{BUG_ID}: ')

        print(f'Total: {len(patch_data["patches"])}')
        print(f'Uncompileble / Timeout patches: {error_cnt}')
        print(f'Wrong patches: {len(wrong_patches)}')
        print(f'Plausible patches: {len(plausible_patches)}')
        print(f'Other type patches: {other_cnt}')

    assert len(patch_data["patches"]) == error_cnt + len(wrong_patches) + len(plausible_patches) + other_cnt

    return plausible_patches, wrong_patches


def parse_patch(patches):
    patch_tokens_list = []

    for patch in patches:
        tokens = javalang.tokenizer.tokenize(patch['code'])
        try:
            patch_tokens_list.append(list(tokens))
        except TypeError:
            print(patch['code'])
            continue

    return patch_tokens_list


def levenshtein_ratio(len1, len2, leven_dist):
    return ((len1 + len2) - leven_dist) / (len1 + len2)


def similarity(patches):
    patch_num = len(patches)

    leven_dist = []
    pdist = np.zeros((patch_num * (patch_num - 1) // 2), dtype=np.int8)
    k = 0

    for i in range(patch_num - 1):
        for j in range(i + 1, patch_num):
            levensh = levenshtein_distance(patches[i], patches[j])
            # print(patches[i])
            leven_dist.append({
                'len1': len(patches[i]),
                'len2': len(patches[j]),
                'leven': levensh
            })
            # pdist[k] = levenshtein_ratio(len(patches[i].parse_token), len(patches[j].parse_token), levensh)
            pdist[k] = levensh
            k += 1

    return pdist, leven_dist


def same_token(token1, token2):
    if token1.value == token2.value and type(token1) == type(token2):
        return True
    return False


def levenshtein_distance(patch1, patch2):
    # Implement calculating levenshtein distanse by dynamic planning
    # todo: the costs of add and delete are both 1
    # todo: but here we set the cost of substitute as 2
    len_patch1 = len(patch1) + 1
    len_patch2 = len(patch2) + 1

    matrix = [0 for n in range(len_patch1 * len_patch2)]

    # first row
    for i in range(len_patch1):
        matrix[i] = i
    # first column
    for j in range(0, len(matrix), len_patch1):
        if j % len_patch1 == 0:
            matrix[j] = j // len_patch1

    for i in range(1, len_patch1):
        for j in range(1, len_patch2):
            if same_token(patch1[i - 1], patch2[j - 1]):
                cost = 0
            else:
                # the cost of substitute
                cost = 2
            matrix[j * len_patch1 + i] = min(
                matrix[(j - 1) * len_patch1 + i] + 1,
                matrix[j * len_patch1 + (i - 1)] + 1,
                matrix[(j - 1) * len_patch1 + (i - 1)] + cost
            )
    return matrix[-1]


# def visualize_hie_cluster(Z):
# fig = plt.figure(figsize=(25, 10))
# dn = shc.dendrogram(Z)
# plt.savefig(f'./{RES_DIR}/{BUG_ID}/cluster_{BUG_ID}_{FILE_NAME}.png')

def hierarchical_cluster(distance_mat, patches, parsed_patches, distance=DISTANCE_THRES, cluster_num=CLUSTER_NUM,
                         debug=True):
    Z = shc.linkage(distance_mat, method='single')
    # visualize_hie_cluster(Z)
    cluster = shc.fcluster(Z, t=distance, criterion='distance')
    cluster_data = {}

    for i in range(len(cluster)):
        key = f'cluster_{cluster[i]}'
        if key in cluster_data.keys():
            cluster_data[key].append({
                'code': patches[i]['code'],
                'test_case': patches[i]['test_case'],
                # 'score': patches[i]['score'],
                'parsed_token': list(parsed_patches[i])
            })
        else:
            cluster_data[key] = [{
                'code': patches[i]['code'],
                'test_case': patches[i]['test_case'],
                # 'score': patches[i]['score'],
                'parsed_token': list(parsed_patches[i])
            }]

    # print(cluster_data)
    return cluster, cluster_data


def output_cluster(cluster_data):
    output_data = {}

    for key, value in cluster_data.items():
        tmp = []
        for patch in value:
            tmp.append({
                'code': patch['code'],
                'test_case': patch['test_case']
            })

        output_data[key] = tmp

    # with open(f'./{RES_DIR}/{BUG_ID}/cluster_{BUG_ID}_{FILE_NAME}.json', 'w') as f:
    #     json.dump(output_data, f, indent=4)
    # print(f'INFO: Clustered patches of {FILE_NAME} have been dumped into ./{RES_DIR}/{BUG_ID}/cluster_{BUG_ID}_{FILE_NAME}.json')


def cluster_similarity(cluster1, cluster2):
    result = 0
    for patch1 in cluster1:
        patch_sim = 0
        for patch2 in cluster2:
            patch_distance = levenshtein_distance(patch1['parsed_token'], patch2['parsed_token'])
            sim = levenshtein_ratio(len(patch1['parsed_token']), len(patch2['parsed_token']), patch_distance)
            if sim > patch_sim:
                patch_sim = sim
        if patch_sim > result:
            result = patch_sim
    return result


def rank_cluster(cluster_data):
    cluster_score = {}

    for [key, cluster] in cluster_data.items():
        score = 0
        for patch in cluster:
            score += patch['score']
        average_score = score / len(cluster)
        cluster_score[key] = average_score

    sorted_cluster = sorted(cluster_score.items(), key=lambda item: item[1], reverse=True)

    # print(sorted_cluster[0])

    return sorted_cluster[0][0]


def MMR_cluster(cluster_data):
    # find the most promising cluster
    first_cluster = rank_cluster(cluster_data)

    # todo:
    lambda_constant = 0.7
    TOPK = 3

    result = []
    R = list(cluster_data.keys())
    R.remove(first_cluster)

    while len(R) > 0:
        score = 0
        selected_cluster = ''
        # i = 'cluster_x'
        for i in R:
            sim1 = cluster_similarity(cluster_data[first_cluster], cluster_data[i])
            sim2 = 0

            for j in result:
                cluster_sim = cluster_similarity(cluster_data[i], cluster_data[j[0]])

                if cluster_sim > sim2:
                    sim2 = cluster_sim

            equation_score = lambda_constant * (sim1) - (1 - lambda_constant) * sim2
            if equation_score > score:
                score = equation_score
                selected_cluster = i

        if selected_cluster == '':
            selected_cluster = i

        R.remove(selected_cluster)
        result.append((selected_cluster, score))

    result.insert(0, (first_cluster, 1))

    return (result, result[:TOPK + 1])[TOPK + 1 < len(result)]


def output_mmr_cluster(mmr_result, cluster_data):
    res = {}

    for mmr in mmr_result:
        res[mmr[0]] = [{'code': patch['code'], 'score': patch['score']} for patch in cluster_data[mmr[0]]]

    with open(f'./{RES_DIR}/{BUG_ID}/mmr_{BUG_ID}_{FILE_NAME}.json', 'w') as f:
        json.dump(res, f, indent=4)

    sorted_res = {}
    for cluster, patches in res.items():
        if len(patches) <= 2:
            sorted_res[cluster] = patches
            continue
        sorted_res[cluster] = []
        selected = []
        for time in range(2):
            score = 0
            select_item = -1
            for i in range(len(patches)):
                if (patches[i]['score'] > score) and (i not in selected):
                    score = patches[i]['score']
                    select_item = i
                    # print(time, i)
            sorted_res[cluster].append(patches[select_item])
            selected.append(select_item)
            # print(selected)

    # with open(f'./{RES_DIR}/{BUG_ID}/mmr_sort_{BUG_ID}_{FILE_NAME}.json', 'w') as f:
    #     json.dump(sorted_res, f, indent=4)


def show_patch_from_cluster(cluster_data):
    showed_patch = {}
    for cluster, patches in cluster_data.items():
        if len(patches) < 2:
            showed_patch[cluster] = {
                'code': patches[0]['code'],
                'test_case': patches[0]['test_case']
            }
            continue
        length = 999
        select_item = -1
        for i in range(len(patches)):

            if len(patches[i]['parsed_token']) < length:
                length = len(patches[i]['parsed_token'])
                select_item = i
            # if patches[i]['score'] > score:
            #     score = patches[i]['score']
            #     select_item = i
        showed_patch[cluster] = {
            'code': patches[select_item]['code'],
            'test_case': patches[select_item]['test_case']
        }

    # with open(f'./{RES_DIR}/{BUG_ID}/select_{BUG_ID}_{FILE_NAME}.json', 'w') as f:
    #     json.dump(showed_patch, f, indent=4)
    #
    # print(f'INFO: Selected patches of {FILE_NAME} have been dumped into ./{RES_DIR}/{BUG_ID}/select_{FILE_NAME}.json')

    return showed_patch


def show_patch_from_cluster_by_sim(cluster_data, buggy_line=BUGGY_LINE):
    showed_patch = {}
    for cluster, patches in cluster_data.items():
        if len(patches) < 2:
            showed_patch[cluster] = {
                'code': patches[0]['code'],
                'test_case': patches[0]['test_case']
            }
            continue
        length = 999
        select_item = -1
        for i in range(len(patches)):
            parsed_buggy_line = list(javalang.tokenizer.tokenize(buggy_line))
            sim_to_buggy_line = levenshtein_distance(patches[i]['parsed_token'], parsed_buggy_line)
            if sim_to_buggy_line < length:
                length = sim_to_buggy_line
                select_item = i
            # if patches[i]['score'] > score:
            #     score = patches[i]['score']
            #     select_item = i
        showed_patch[cluster] = {
            'code': patches[select_item]['code'],
            'test_case': patches[select_item]['test_case']
        }

    # with open(f'./{RES_DIR}/{BUG_ID}/select_{BUG_ID}_{FILE_NAME}.json', 'w') as f:
    #     json.dump(showed_patch, f, indent=4)
    #
    # print(f'INFO: Selected patches of {FILE_NAME} have been dumped into ./{RES_DIR}/{BUG_ID}/select_{FILE_NAME}.json')

    return showed_patch


def get_index(cluster_data, selected_cluster, Q):
    for i in range(len(cluster_data[f'cluster_{selected_cluster}'])):
        if cluster_data[f'cluster_{selected_cluster}'][i]['code'] == Q['code']:
            Q_idx = i
            return Q_idx

    print('ERROR: Somthing went wrong in MMR re-ranking')
    return False


def MMR_patch(cluster_data, show_patch, selected_cluster):
    # todo:
    lambda_constant = 0.7
    TOPK = 4

    result = []

    patches = cluster_data[f'cluster_{selected_cluster}']

    R = [i for i in range(len(patches))]
    Q = show_patch[f'cluster_{selected_cluster}']
    Q_idx = get_index(cluster_data, selected_cluster, Q)
    R.remove(Q_idx)
    Q = cluster_data[f'cluster_{selected_cluster}'][Q_idx]

    while len(R) > 0:
        # print(R)
        score = 0
        selected_cluster = ''
        # i = 'cluster_x'
        for i in R:
            distance1 = levenshtein_distance(Q['parsed_token'], patches[i]['parsed_token'])
            sim1 = levenshtein_ratio(len(Q['parsed_token']), len(patches[i]['parsed_token']), distance1)
            sim2 = 0
            for j in result:
                distance2 = levenshtein_distance(patches[j[0]]['parsed_token'], patches[i]['parsed_token'])
                cluster_sim = levenshtein_ratio(len(patches[i]['parsed_token']), len(patches[j[0]]['parsed_token']),
                                                distance2)

                if cluster_sim > sim2:
                    sim2 = cluster_sim

            equation_score = lambda_constant * (sim1) - (1 - lambda_constant) * sim2
            if equation_score > score:
                score = equation_score
                selected_cluster = i

        if selected_cluster == '':
            selected_cluster = i

        R.remove(selected_cluster)
        result.append((selected_cluster, score))

    result.insert(0, (Q_idx, 1))

    # print(result)

    # print(len(result))

    return (result, result[:TOPK + 1])[TOPK + 1 < len(result)]


def output_mmr_patch(mmr_result, cluster_data, selected_cluster):
    mmr_patch = []

    cluster = cluster_data[f'cluster_{selected_cluster}']

    for idx in mmr_result:
        mmr_patch.append({
            'code': cluster[idx[0]]['code'],
            'test_case': cluster[idx[0]]['test_case']
        })

    # with open(f'./{RES_DIR}/{BUG_ID}/mmr_result_{BUG_ID}_{FILE_NAME}.json', 'w') as f:
    #     json.dump(mmr_patch, f, indent=4)

    return mmr_patch


def cluster_patches(patches, output=False):
    # parse the patch to get its grammar structure
    parsed_patches = parse_patch(patches)

    # calculate the similarity matrix of patches
    plausible_patches_distance, plau_leven_info = similarity(parsed_patches)

    # hierarchical clustering
    cluster, cluster_data = hierarchical_cluster(plausible_patches_distance, patches, parsed_patches)

    # output the cluster result into a json file
    if output == True:
        output_cluster(cluster_data)

    # showed_patch = show_patch_from_cluster(cluster_data)
    showed_patch = show_patch_from_cluster_by_sim(cluster_data, buggy_line=BUGGY_LINE)

    return cluster_data, showed_patch


def get_patch_list_from_cluster(cluster_data, selected_cluster):
    patch_list = []

    for patch in cluster_data[f'cluster_{selected_cluster}']:
        patch_list.append(patch['code'])

    return patch_list


def sample_patches(file_name, bug_id):
    # todo: Now we get patch data from a temporary file
    # todo: After getting the new format data we should change this function
    patch_data = read_patch(file_name, bug_id)

    # patch data preprocessing
    # todo: here we only focus on the patches which is plausible
    # todo: wrong patches will also be taken into consideration in the future
    plausible_patches, wrong_patches = prepro_patch(patch_data)

    if not os.path.exists(f'./{RES_DIR}/{bug_id}'):
        os.makedirs(f'./{RES_DIR}/{bug_id}')
    
    with open(f'./{RES_DIR}/{bug_id}/plausible_patch.java', 'w') as f:
        for patch in plausible_patches:
            f.write(f'{patch["code"]}\n')
    if len(plausible_patches) < 2:
        print(
            F'INFO: {bug_id}_{file_name}: There are only {len(plausible_patches)} plausible patch(es), no need to sample')
        return None

    # cluster the patches
    cluster_data, showed_patch = cluster_patches(plausible_patches, output=True)

    # using Maximal Marginal Relevance to re-rank results
    # mmr_res = MMR_patch(cluster_data, showed_patch, 1)

    # output_mmr_patch(mmr_res, cluster_data, 1)

    return cluster_data

# file_list = transform_data()
# sample_patches(FILE_NAME, BUG_ID)

