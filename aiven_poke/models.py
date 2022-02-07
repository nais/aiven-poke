from dataclasses import dataclass


@dataclass(frozen=True)
class TeamTopic:
    slack_channel: str
    topics: frozenset[str]

    def __post_init__(self):
        object.__setattr__(self, "topics", frozenset(self.topics))