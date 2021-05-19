from locust import HttpUser, task
from config import UserSimulationBenchmarkConfig
from datetime import datetime

import actions, random, os, json, load_dataset


class UserSimulationBenchmark(HttpUser):
    wait_time = UserSimulationBenchmarkConfig.wait_time_between_tasks
    assets = []
    inserted_files = []
    inserted_folders = [""]
    files = []

    def on_start(self):
        with open("content.json", "r") as file:
            self.files = json.load(file)["files"]

    def on_stop(self):
        inserted_assets = {
            "files": self.inserted_files,
            "folders": self.inserted_folders[1:],
        }
        with open("inserted_assets.json", "w") as file:
            json.dump(inserted_assets, file, indent=4, sort_keys=True)

    @task(30)
    def readPage(self):
        actions.get_file(self, random.choice(self.files))

    @task(20)
    def upload_file(self):
        i = random.randint(0, len(load_dataset.assets) - 1)
        filename = load_dataset.assets[i]
        folder = random.choice(self.inserted_folders)
        _, ext = os.path.splitext(filename)

        if folder == "":
            new_filename = f"{folder}_generated{datetime.now().timestamp()}{ext}"
        else:
            new_filename = f"{folder}/_generated{datetime.now().timestamp()}{ext}"

        response = actions.upload_file(self, load_dataset.files[i], new_filename)

        if str(response.status_code)[0] != "2":
            print(response.content)

        self.inserted_files.append(new_filename)

    @task(1)
    def create_folder(self):
        new_foldername = f"_generated_folder{datetime.now().timestamp()}"
        response = actions.create_folder(self, new_foldername)
        if str(response.status_code)[0] == "2":
            self.inserted_folders.append(new_foldername)