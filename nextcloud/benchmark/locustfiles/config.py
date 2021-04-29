from locust import between, constant


class StaticBenchmarkConfig:
    write_page_wait_seconds = constant(10)
    read_page_wait_seconds = constant(5)
    media_instances_per_content_category = 3


class UserSimulationBenchmarkConfig:
    media_instances_per_content_category = 5
    wait_time_between_tasks = between(5, 25)