from typing import Optional

from pydantic import HttpUrl, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

    aiven_token: SecretStr
    main_project: str = "nav-integration-test"
    webhook_url: Optional[HttpUrl] = None
    webhook_enabled: bool = True
    push_gateway_address: Optional[str] = None
    expiring_users_enabled: bool = False
    topics_enabled: bool = False
    override_slack_channel: Optional[str] = None

