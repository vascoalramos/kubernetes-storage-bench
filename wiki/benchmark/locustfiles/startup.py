from locust import HttpUser
from config import AuthConfig
from time import sleep

import actions

class Setup(HttpUser): 

    def on_start(self):
        # Start wiki instance by inserting admin settings
        actions.initWikiInstance(self)
        sleep(5)

        # Log in as admin
        self.token = actions.login(self, AuthConfig.admin_username, AuthConfig.admin_password)
        
        # Create homepage
        actions.createPage(self, "home", "Homepage", "This is my homepage!")

        # End session
        self.environment.runner.quit()