from locust import HttpUser
from config import AuthConfig, CleanupConfig

import actions

class Cleanup(HttpUser):

    def on_start(self):
        # Log in as admin
        self.token = actions.login(self, AuthConfig.admin_username, AuthConfig.admin_password)
        
        # Delete generated items
        actions.deleteGeneratedAssetsAndPages(self)
        
        # Delete generated users
        if CleanupConfig.delete_users:
            actions.deleteGeneratedUsers(self)
        
        # Delete generated API Keys
        if CleanupConfig.revoke_api_keys:
            actions.deleteGeneratedApiKeys(self)
        
        # End session
        self.environment.runner.quit()