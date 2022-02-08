import dataclasses
import enum
import json
import logging
from typing import Optional, Iterable

import requests

from aiven_poke.models import TeamTopic
from aiven_poke.settings import Settings

LOG = logging.getLogger(__name__)
SESSION = requests.session()

DOC_LINK = "https://doc.nais.io/persistence/kafka/manage_topics/#permanently-deleting-topic-and-data"

# Messages
HEADING = "*Found topics on Aiven that are not defined in the cluster*"
MAIN_TEXT = f"""\
If this is not intentional, please rectify the situation by either:
* Create the missing Topic resource in the cluster if you wish to keep the topic, or
* Create a Topic resource in the cluster, then following the procedure for <{DOC_LINK}|permanently deleting data>
"""
FALLBACK = "Found topics on Aiven that are not defined in the cluster. " \
           "If this is not intentional, please rectify the situation."


class Color(str, enum.Enum):
    GOOD = "good"
    WARNING = "warning"
    DANGER = "danger"


@dataclasses.dataclass
class Field:
    title: str
    value: Optional[str] = None
    short: Optional[bool] = None


@dataclasses.dataclass
class Attachment:
    text: Optional[str] = None
    fallback: Optional[str] = None
    pretext: Optional[str] = None
    color: Optional[Color] = None
    fields: list[Field] = dataclasses.field(default_factory=list)


@dataclasses.dataclass
class Payload:
    channel: str
    text: Optional[str] = None
    attachments: list[Attachment] = dataclasses.field(default_factory=list)


def create_payload(team_topic):
    topics = ", ".join(team_topic.topics)
    return Payload(team_topic.slack_channel, attachments=[
        Attachment(fallback=FALLBACK, color=Color.WARNING, fields=[
            Field(HEADING, MAIN_TEXT),
            Field("Topics", topics)
        ])
    ])


def post_payload(settings, payload):
    data = dataclasses.asdict(payload)
    if settings.webhook_enabled and settings.webhook_url is not None:
        SESSION.post(settings.webhook_url, json=data)
    else:
        LOG.info("Would have sent payload: %s", json.dumps(data))
    return data


def poke(settings: Settings, missing: Iterable[TeamTopic]):
    """Poke the teams with topics missing in the cluster"""
    for team_topic in missing:
        payload = create_payload(team_topic)
        post_payload(settings, payload)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    settings = Settings()
    tt = TeamTopic("#pig-aiven", frozenset(("aura.test-topic", "aura.topic-test")))
    poke(settings, [tt])
