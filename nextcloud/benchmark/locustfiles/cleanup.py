from locust.contrib.fasthttp import FastHttpUser
from config import AuthConfig

import actions


class Cleanup(FastHttpUser):
    def on_start(self):
        # Log in as admin
        self.token = actions.login(
            self, AuthConfig.admin_username, AuthConfig.admin_password
        )

        # Delete generated items
        actions.deleteGeneratedAssetsAndPages(self)
        actions.deleteGeneratedUsers(self)
        actions.deleteGeneratedApiKeys(self)

        # End session
        self.environment.runner.quit()