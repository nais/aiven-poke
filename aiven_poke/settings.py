from pydantic import BaseSettings


class Settings(BaseSettings):
    aiven_token: str
    main_project: str = "nav-integration-test"
