from locust import HttpUser, task
from config import AuthConfig, Auth, StaticBenchmarkConfig

import actions

class StaticBenchmarkWrite(HttpUser):
    wait_time = StaticBenchmarkConfig.write_page_wait_seconds

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


    @task
    def writePage(self):
        actions.generatePage(self, StaticBenchmarkConfig.media_instances_per_content_category, False)