from locust import task
from locust.contrib.fasthttp import FastHttpUser
from config import StaticBenchmarkConfig

import actions
import json
import random


class StaticBenchmarRead(FastHttpUser):
    wait_time = StaticBenchmarkConfig.read_page_wait_seconds
    files = []

    def on_start(self):
        with open("content.json", "r") as file:
            self.files = json.load(file)["files"]

    @task
    def readPage(self):
        actions.get_file(self, random.choice(self.files))
