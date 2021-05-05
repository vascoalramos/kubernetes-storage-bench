from locust import HttpUser, task
from config import StaticBenchmarkConfig

import random
import actions

class StaticBenchmarkWrite(HttpUser):
    wait_time = StaticBenchmarkConfig.read_page_wait_seconds

    def on_start(self):
        # Get all available pages
        self.pages = actions.getPageFullTree(self, 0)


    @task
    def readPage(self):
        # Read random page
        actions.loadPage(self, random.choice(self.pages)["path"])