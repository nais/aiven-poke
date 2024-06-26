from typing import Optional

from pydantic import HttpUrl, SecretStr, Secret
from pydantic_settings import BaseSettings, SettingsConfigDict


class SecretUrlPath(Secret[HttpUrl]):
    def _display(self) -> str:
        value = self.get_secret_value()
        if value:
            path = "*" * len(value.path)
            return f"{value.scheme}://{value.host}/{path}"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

    aiven_token: SecretStr
    main_project: str
    webhook_url: Optional[SecretUrlPath] = None
    webhook_enabled: bool = True
    push_gateway_address: Optional[str] = None
    expiring_users_enabled: bool = False
    topics_enabled: bool = False
    override_slack_channel: Optional[str] = None
