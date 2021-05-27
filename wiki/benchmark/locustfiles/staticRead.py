from locust import HttpUser, task
from config import StaticBenchmarkConfig

import random
import actions


class StaticBenchmarkRead(HttpUser):
    wait_time = StaticBenchmarkConfig.read_page_wait_seconds

    @task
    def readPage(self):
        # Read random page
        page = actions.getSinglePage(self)

        if (page is not None):
            actions.loadPage(self, page["path"])
        else:
            pages = actions.getPageFullTree(self, 0)
            actions.loadPage(self, random.choice(pages)["path"])