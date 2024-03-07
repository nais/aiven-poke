from typing import Optional

from pydantic import HttpUrl, SecretStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    aiven_token: SecretStr
    main_project: str = "nav-integration-test"
    api_server: str = "http://localhost:8001"
    webhook_url: Optional[HttpUrl] = None
    webhook_enabled: bool = True
    push_gateway_address: Optional[str] = None
    expiring_users_enabled: bool = False
    topics_enabled: bool = True
