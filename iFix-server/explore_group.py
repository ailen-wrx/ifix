import dataclasses

import falcon
from more_itertools import first_true
from utils import *


class ExploreGroupResource:

    def __init__(self, service):
        self.service = service

    def on_post(self, req, resp):
        media = req.get_media()
        print(media)
        session_id = media['session_id']
        group_id = media['group_id']
        if not session_id or not group_id:
            resp.status = falcon.HTTP_400
            return

        session = self.service.get_session(session_id)
        if session is None:
            print('404')
            print(self.service.sessions)
            resp.status = falcon.HTTP_404
            return

        group_index = group_id.split('_')[-1]
        mmr_result = MMR_patch(session.cluster_data, session.clusters, group_index)
        mmr_patch = output_mmr_patch(mmr_result, session.cluster_data, group_index)
        print(mmr_patch)

        bug_oracle = get_oracle(session_id)
        resp.media = {
            'stage': 'patch',
            "id": F'{session_id}_{group_id}',
            "line_number": bug_oracle["LINE_NUM"],
            "patch_groups": [],
            'failed_tests': bug_oracle["FAILED_TESTS"]
        }

        for i, p in enumerate(mmr_patch):
            resp.media['patch_groups'].append({
                'id': F'patch_{i}',
                'code': p['code'],
                'test_case': p['test_case']
            })

        resp.media['patch_groups'] = sorted(resp.media['patch_groups'], key=compare_test_case)

        resp.status = falcon.HTTP_200
