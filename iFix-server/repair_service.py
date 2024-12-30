from dataclasses import dataclass
from utils import *

@dataclass
class RepairSession:
    cluster_data: dict
    clusters: dict

class RepairService:

    def __init__(self):
        self.sessions = {}

    def create_session(self, file_name, project_name):
        print('Creating session for file %s' % file_name)

        cluster_data = sample_patches(file_name, project_name)
        self.sessions[project_name] = RepairSession(cluster_data=cluster_data, clusters=show_patch_from_cluster_by_sim(cluster_data))

        return self.sessions[project_name]

    def get_session(self, id):
        if id not in self.sessions:
            return None
        return self.sessions[id]
