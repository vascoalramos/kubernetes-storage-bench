from locust import HttpUser
from config import config

import common

class Cleanup(HttpUser): 

    def on_start(self):
        self.token = common.login(self, config.admin_username, config.admin_password)
        common.deleteGeneratedAssetsAndPages(self)
        common.deleteGeneratedUsers(self)
        self.environment.runner.quit()