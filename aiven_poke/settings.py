from typing import Optional

from pydantic import HttpUrl
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    aiven_token: str
    main_project: str = "nav-integration-test"
    api_server: str = "http://localhost:8001"
    webhook_url: Optional[HttpUrl] = None
    webhook_enabled: bool = True
    push_gateway_address: Optional[str] = None
