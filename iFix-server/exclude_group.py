import dataclasses

import falcon
from more_itertools import first_true
from utils import *


class ExcludeGroupResource:

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

        del session.clusters[group_id]
        print(session.clusters)

        bug_oracle = get_oracle(session_id)
        resp.media = {
            'stage': 'cluster',
            'id': session_id,
            "line_number": bug_oracle["LINE_NUM"],
            "patch_groups": [],
            'failed_tests': bug_oracle["FAILED_TESTS"]
        }

        for key in session.clusters:
            group_index = key.split('_')[-1]
            mmr_result = MMR_patch(session.cluster_data, session.clusters, group_index)
            mmr_patch = output_mmr_patch(mmr_result, session.cluster_data, group_index)
            resp.media['patch_groups'].append(
                {
                    'id': key,
                    'code': session.clusters[key]['code'],
                    'test_case': session.clusters[key]['test_case'],
                    'n_similar': len(mmr_patch)
                }
            )

        resp.media['patch_groups'] = sorted(resp.media['patch_groups'], key=compare_test_case)

        resp.status = falcon.HTTP_200