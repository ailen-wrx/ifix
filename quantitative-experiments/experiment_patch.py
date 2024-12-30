import json
import copy
import javalang
import scipy.cluster.hierarchy as shc
from config import *
from new_utils import *

class PatchRanking(object):
    def __init__(self, _file_name, _bug_id, _buggy_line, pre_cluster_dist, patches=None):
        self.file_name = _file_name
        self.bug_id = _bug_id
        self.buggy_line = _buggy_line
        self.cluster_dist = 0
        self.origin_patch = []
        self.ranked_patch = []
        self.patch_cluster = {}
        # set origin_patch to plausible patches of the bug
        self.set_origin_patch(patches)

        # set cluster distance
        self.set_cluster_distance(pre_cluster_dist)

        # perform clustering and ranking
        self.set_cluster()

    def read_patch(self, file_name, bug_id):
        with open(f'./patches/{file_name}_{bug_id}.json', 'r') as f:
            data = json.load(f)
        return data
    
    def prepro_patch(self, patch_data, debug=False):
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
            print(f'Patches in {self.file_name}_{self.bug_id}: ')
            print(f'Total: {len(patch_data["patches"])}')
            print(f'Uncompileble / Timeout patches: {error_cnt}')
            print(f'Wrong patches: {len(wrong_patches)}')
            print(f'Plausible patches: {len(plausible_patches)}')
            print(f'Other type patches: {other_cnt}')
        
        assert len(patch_data["patches"]) == error_cnt + len(wrong_patches) + len(plausible_patches) + other_cnt

        return plausible_patches, wrong_patches

    def set_origin_patch(self, patches):
        if patches is not None:
            self.origin_patch = patches
        else:
            patch_list = self.read_patch(self.file_name, self.bug_id)
            plausible_patches, wrong_patches = self.prepro_patch(patch_list)
            self.origin_patch = plausible_patches

    def set_cluster_distance(self, pre_dist=None):
        res = 0
        patch_num = len(self.origin_patch)
        if patch_num > 250:
            res = 6
        elif patch_num > 100:
            res = 5
        elif patch_num > 20:
            res = 4
        else: 
            res = 3
        if pre_dist is not None and res == pre_dist:
            res -= 1
        self.cluster_dist = res

    def ranking(self, patch_list):
        parsed_buggy_line = list(javalang.tokenizer.tokenize(self.buggy_line))
        tmp_patch = copy.deepcopy(patch_list)
        for patch in tmp_patch:
            patch['rk_score'] = levenshtein_distance(patch['parsed_token'], parsed_buggy_line)
        tmp_patch.sort(key=lambda x: x['rk_score'])
        return tmp_patch

    def parse_patch(self, patch_list):
        patch_tokens_list = []

        for patch in patch_list:
            tokens = javalang.tokenizer.tokenize(patch['code'])
            try:
                patch_tokens_list.append(list(tokens))
            except TypeError:
                print(patch['code'])
                continue

        return patch_tokens_list

    def hierarchical_cluster(self, distance_mat, parsed_patches, distance=DISTANCE_THRES):
        Z = shc.linkage(distance_mat, method='single')
        # visualize_hie_cluster(Z)
        cluster = shc.fcluster(Z, t=self.cluster_dist, criterion='distance')
        cluster_data = {}

        for i in range(len(cluster)):
            key = f'cluster_{cluster[i]}'
            if key in cluster_data.keys():
                cluster_data[key].append({
                    'code': self.origin_patch[i]['code'],
                    'test_case': self.origin_patch[i]['test_case'],
                    # 'score': patches[i]['score'],
                    'parsed_token': list(parsed_patches[i])
                })
            else:
                cluster_data[key] = [{
                    'code': self.origin_patch[i]['code'],
                    'test_case': self.origin_patch[i]['test_case'],
                    # 'score': patches[i]['score'],
                    'parsed_token': list(parsed_patches[i])
                }]

        # print(cluster_data)
        return cluster, cluster_data

    def central_point(self, patches):
        if len(patches) == 0:
            print(f'ERROR: Empty cluster! {self.bug_id}, {self.file_name}')
            exit(-1)
        # only one patch in cluster, just choose it
        elif len(patches) == 1:
            return patches[0]

        min_distance = 1000000000
        min_distance_patch = None
        for i in range(len(patches)):
            sum_distance = 0
            for j in range(len(patches)):
                if i == j:
                    pass
                else:
                    dist = levenshtein_distance(patches[i]['parsed_token'], patches[j]['parsed_token'])
                    sum_distance += dist
            if sum_distance < min_distance:
                min_distance = sum_distance
                min_distance_patch = patches[i]
        return min_distance_patch
    
    def choose_representative_patch(self):
        res = []
        for k, v in self.patch_cluster.items():
            # central_patch = self.central_point(v)
            central_patch = self.ranking(v)[0]
            res.append({
                'cluster': k,
                'code': central_patch['code'],
                'test_case': central_patch['test_case'],
                'parsed_token': central_patch['parsed_token']
            })
        return res

    def set_cluster(self):
        if len(self.origin_patch) < 15:
            print(F'INFO: {self.file_name}_{self.bug_id}: There are only {len(self.origin_patch)} plausible patch(es), no need to sample')
            self.patch_cluster['cluster_1'] = self.origin_patch
            # todo: change the way of ranking
            for patch in self.origin_patch:
                patch['cluster'] = 'cluster_1'
                tokens = javalang.tokenizer.tokenize(patch['code'])
                try:
                    patch['parsed_token'] = list(tokens)
                except TypeError:
                    print(patch['code'])
                    continue
            self.ranked_patch = self.ranking(self.origin_patch)
            return 'skip'
        
        # todo: change the way of parsing code
        parsed_patches = self.parse_patch(self.origin_patch)

        # todo: change the way of calculating similarity
        plausible_patches_distance, plau_leven_info = similarity(parsed_patches)

        # todo: change the way of clustering
        cluster_info, self.patch_cluster = self.hierarchical_cluster(plausible_patches_distance, parsed_patches)

        if len(self.patch_cluster.keys()) == 1:
            print(len(self.patch_cluster['cluster_1']))
            print(len(self.origin_patch))
            print(self.patch_cluster.keys())
            assert len(self.patch_cluster['cluster_1']) == len(self.origin_patch)
            assert list(self.patch_cluster.keys())[0] == 'cluster_1'
            rank_single_cluster = self.ranking(self.patch_cluster['cluster_1'])
            for rsc_patch in rank_single_cluster:
                rsc_patch['cluster'] = 'cluster_1'
            self.ranked_patch = rank_single_cluster
        else:
            # todo: change the way of choosing representative patch and ranking
            representitve_patch = self.choose_representative_patch()
            self.ranked_patch = self.ranking(representitve_patch)

    def get_ranked_patch(self):
        return self.ranked_patch
    
    def get_cluster_data(self):
        return self.patch_cluster

    def get_cluster_dist(self):
        return self.cluster_dist

class IPR(object):
    def __init__(self, _project_name, _bug_id, _buggy_line, _patch_list=None):
        self.buggy_line = _buggy_line
        self.bug_id = _bug_id
        self.project_name = _project_name
        self.patch_data = {}
        self.stage_id = ''
        self.cluster_dist = None
        self.set_patch_data(stage_id='1', patches=_patch_list)
        self.set_stage_id()
        self.set_cluster_dist()

    def get_previous_stage(self, stage_id):
        if stage_id == '1':
            return stage_id
        else:
            tmp_id_list = stage_id.split('_')
            prev_id = '_'.join(tmp_id_list[:-1])
            return prev_id
    
    def set_patch_data(self, stage_id='1', patches=None):
        # print('patches: ', patches)
        if stage_id not in self.patch_data.keys():
            patch_rk = PatchRanking(self.project_name, self.bug_id, self.buggy_line, self.cluster_dist, patches)
            self.patch_data[stage_id] = patch_rk
            self.cluster_dist = patch_rk.get_cluster_dist()

    def set_stage_id(self, stage_id='1'):
        self.stage_id = stage_id
    
    def set_cluster_dist(self):
        self.cluster_dist = self.patch_data[self.stage_id].cluster_dist

    def get_stage_id(self):
        return self.stage_id
    
    def get_cluster_dist(self):
        return self.cluster_dist
