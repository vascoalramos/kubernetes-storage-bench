from locust import HttpUser
from config import AuthConfig, Auth, SetupConfig

import actions

class Setup(HttpUser): 

    def on_start(self):
        # Log in as admin
        self.token = actions.login(self, AuthConfig.admin_username, AuthConfig.admin_password)
        
        # Client authentication by API keys
        if (AuthConfig.auth == Auth.API_KEY):
            actions.manageApiAccessState(self, True)
            actions.generateApiKeys(self, SetupConfig.generate_users_count)
        
        # Client authentication by username and password
        else:
            actions.generateUsers(self, SetupConfig.generate_users_count)

        # Apply desired settings
        actions.applySettings(self)

        # End session
        self.environment.runner.quit()