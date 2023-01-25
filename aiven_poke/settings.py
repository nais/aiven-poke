from pydantic import BaseSettings, HttpUrl, AnyUrl


class Settings(BaseSettings):
    aiven_token: str
    main_project: str = "nav-integration-test"
    api_server: str = "http://localhost:8001"
    webhook_url: HttpUrl = None
    webhook_enabled: bool = True
    push_gateway_address: str = None
