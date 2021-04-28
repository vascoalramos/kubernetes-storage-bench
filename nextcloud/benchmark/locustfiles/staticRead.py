from locust import HttpUser, task
from config import StaticBenchmarkConfig


class StaticBenchmarkWrite(HttpUser):
    wait_time = StaticBenchmarkConfig.read_page_wait_seconds

    @task
    def readPage(self):
        """
        self.client.get(
            "http://cloud74:30000/remote.php/dav/files/admin/Documents/report2.pdf",
            auth=("admin", "admin"),
        )

        self.client.request(
            "MKCOL",
            "http://cloud74:30000/remote.php/dav/files/admin/Documents/newfolder",
            auth=("admin", "admin"),
        )

        self.client.request(
            "COPY",
            "http://cloud74:30000/remote.php/dav/files/admin/Documents/newfolder2",
            auth=("admin", "admin"),
            headers={
                "Destination": "http://cloud74:30000/remote.php/dav/files/admin/Documents/newfolder"
            },
        )"""
