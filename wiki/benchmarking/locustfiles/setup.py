from locust import HttpUser
from config import config

import common

class Setup(HttpUser): 

    def on_start(self):
        self.token = common.login(self, config.admin_username, config.admin_password)
        common.generateUsers(self, config.generate_users_count)
        common.applySettings(self)
        self.environment.runner.quit()