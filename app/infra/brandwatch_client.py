from bcr_api.bwproject import BWProject
from bcr_api.bwresources import BWQueries
import os

class BrandwatchClient:

    def __init__(self):
        project = BWProject(
            project=os.getenv("BW_PROJECT"),
            username=os.getenv("BW_EMAIL"),
            password=os.getenv("BW_PASSWORD")
        )

        self.queries = BWQueries(project)
