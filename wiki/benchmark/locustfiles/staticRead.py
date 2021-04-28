from locust import HttpUser, task
from config import StaticBenchmarkConfig

import actions

class StaticBenchmarkWrite(HttpUser):
    wait_time = StaticBenchmarkConfig.read_page_wait_seconds

    def on_start(self):
        # Get all available pages
        self.pages = actions.getPageFullTree(self, 0)
        self.currentPage = 0


    @task
    def readPage(self):
        # Read page
        actions.loadPage(self, self.pages[self.currentPage]["path"])

        # Update next page index to read
        self.currentPage = (self.currentPage + 1) % len(self.pages)