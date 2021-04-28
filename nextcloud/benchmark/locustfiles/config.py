from locust import between, constant


class SetupConfig:
    generate_users_count = 50


class StaticBenchmarkConfig:
    write_page_wait_seconds = constant(10)
    read_page_wait_seconds = constant(5)
    media_instances_per_content_category = 3


class SimulateUser:
    media_instances_per_content_category = 5
    wait_time_between_tasks = between(5, 25)