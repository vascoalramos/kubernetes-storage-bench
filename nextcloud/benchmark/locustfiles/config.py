from locust import between, constant


class StaticBenchmarkConfig:
    write_page_wait_seconds = constant(7.5)
    read_page_wait_seconds = constant(2.5)


class UserSimulationBenchmarkConfig:
    wait_time_between_tasks = between(5, 10)