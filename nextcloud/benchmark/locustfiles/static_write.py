from locust import task
from locust.contrib.fasthttp import FastHttpUser
from config import StaticBenchmarkConfig


class StaticBenchmarkWrite(FastHttpUser):
    wait_time = StaticBenchmarkConfig.write_page_wait_seconds

    @task
    def writePage(self):
        with open("./assets/files/pa02.pdf", "rb") as file:
            self.client.request(
                "MKCOL",
                "http://cloud74:30000/remote.php/dav/files/admin/MyDocuments",
                auth=("admin", "admin"),
            )
            self.client.put(
                "http://cloud74:30000/remote.php/dav/files/admin/MyDocuments/report3.pdf",
                data=file,
                auth=("admin", "admin"),
            )
