from pydantic import BaseSettings


class Settings(BaseSettings):
    aiven_token: str
    main_project: str = "nav-integration-test"
    api_server: str = "http://localhost:8001"
