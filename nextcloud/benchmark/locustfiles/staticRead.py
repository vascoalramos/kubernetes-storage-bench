from locust import HttpUser, task
from config import StaticBenchmarkConfig
from actions import get_file, get_content_list


class StaticBenchmarRead(HttpUser):
    wait_time = StaticBenchmarkConfig.read_page_wait_seconds

    @task
    def readPage(self):
        get_file(self, "Nextcloud.png")