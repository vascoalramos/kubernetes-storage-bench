import random
from locust import HttpUser, task, between

import actions
import blocks


class ReadFromWiki(HttpUser):

    def on_start(self):
        self.token = actions.login(self, "admin", "passwd")
        self.available_pages = blocks.getPageFullTree(self, 0)

    @task
    def requestAllPages(self):
        import time
        time.sleep(1)