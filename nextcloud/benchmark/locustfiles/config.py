from locust import between, constant


class StaticBenchmarkConfig:
    write_page_wait_seconds = constant(10)
    read_page_wait_seconds = constant(5)


class UserSimulationBenchmarkConfig:
    wait_time_between_tasks = between(10, 30)