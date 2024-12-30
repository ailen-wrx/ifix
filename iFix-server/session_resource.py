import dataclasses
from email import utils
from utils import *

import falcon


class SessionResource:

    def __init__(self, service):
        self.service = service

    def on_post(self, req, resp):
        media = req.get_media()
        project_name = media['project_name']
        file_path = media['file_path']
        if not project_name or not file_path:
            resp.status = falcon.HTTP_400
            return

        file_name = file_path.split('/')[-1]

        print(F'[Debug] file_name:{file_name}, project_name:{project_name}')

        session = self.service.create_session(file_name, project_name)

        if session is None:
            resp.status = falcon.HTTP_404
            return
        print(session.clusters)

        bug_oracle = get_oracle(project_name)
        resp.media = {
            'stage': 'start',
            'id': project_name,
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

        print(resp.media)
        resp.status = falcon.HTTP_200
