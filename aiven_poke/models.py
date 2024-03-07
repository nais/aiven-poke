from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class TeamTopic:
    team: str
    slack_channel: str
    topics: frozenset[str]

    def __post_init__(self):
        object.__setattr__(self, "topics", frozenset(self.topics))


@dataclass
class ExpiringUser:
    team: str
    username: str
    is_protected: bool
    expiring_cert_not_valid_after_time: datetime
