from locust.contrib.fasthttp import FastHttpUser

import actions, json


class Cleanup(FastHttpUser):
    def on_start(self):
        with open("inserted_assets.json", "r") as file:
            assets = json.load(file)

        files = assets["files"]
        for file in files:
            actions.delete_asset(self, file)

        folders = assets["folders"]
        for folder in folders:
            actions.delete_asset(self, folder)

        assets["files"] = []
        assets["folders"] = []
        with open("inserted_assets.json", "w") as file:
            json.dump(assets, file, indent=4, sort_keys=True)

        # End session
        self.environment.runner.quit()