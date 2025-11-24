from bcr_api.bwproject import BWProject
from bcr_api.bwresources import BWQueries
import os

class BrandwatchClient:

    def __init__(self):
        project = BWProject(
            project=os.getenv("BRANDWATCH_PROJECT_ID"),
            username=os.getenv("BRANDWATCH_USERNAME"),
            password=os.getenv("BRANDWATCH_PASSWORD")
        )

        self.queries = BWQueries(project)
