from enum import Enum
from locust import between, constant

class Auth(Enum):
    API_KEY = 1
    USERNNAME_PASSWORD = 2


class AuthConfig:
    auth = Auth.API_KEY
    admin_username = "admin@example.com"
    admin_password = "admin1234"
    
class SetupConfig:
    generate_users_count = 50

class StaticBenchmarkConfig:
    write_page_wait_seconds = constant(15)
    read_page_wait_seconds = constant(10)
    media_instances_per_content_category = 4

class SimulateUser:
    media_instances_per_content_category = 4
    wait_time_between_tasks = between(10, 25)

class CleanupConfig:
    revoke_api_keys = False
    delete_users = False