from locust import HttpUser, task
from config import AuthConfig, Auth, SimulateUser

import actions, random
import actions.loadAssets as dataset

class SimulateUserBenchmark(HttpUser):
    wait_time = SimulateUser.wait_time_between_tasks

    def on_start(self):
        # Locust user ID
        greenlet_id = self._greenlet.getcurrent().minimal_ident
        
        # Authenticate via API key
        if AuthConfig.auth == Auth.API_KEY:
            self.token = actions.getApiKey(greenlet_id)

        # Authenticate via username and password
        else:
            user, password = actions.getCredentials(greenlet_id)
            self.token = actions.login(self, user, password)


    @task(1)
    def writePage(self):
        actions.generatePage(self, dataset.data, SimulateUser.media_instances_per_content_category, False)

    @task(5)
    def readPage(self):
        pages = actions.getPageFullTree(self, 0)
        actions.loadPage(self, random.choice(pages)["path"])