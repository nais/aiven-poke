import dataclasses
import enum
import logging
from typing import Optional, Iterable, Union

import requests
from requests_toolbelt.utils import dump

from aiven_poke.models import TeamTopic
from aiven_poke.settings import Settings

LOG = logging.getLogger(__name__)
SESSION = requests.session()

DOC_LINK = "https://doc.nais.io/persistence/kafka/manage_topics/#permanently-deleting-topic-and-data"

# TODO: Mention which cluster (nav-dev vs nav-prod)
# Messages
HEADER = "Your team has topics on Aiven which are not found in a nais cluster"
MAIN_TEXT = f"""\
Topics on Aiven should be defined by a Topic resource in a nais cluster.
Topics not defined by such a resource are inaccessible by applications on nais, which indicates that this topic may be forgotten.

Please rectify the situation by either:
* Create the missing Topic resource in the cluster if you wish to keep the topic, or
* Create a Topic resource in the cluster, then following the procedure for <{DOC_LINK}|permanently deleting data>

If you need help, reach out in <#C73B9LC86|kafka> or <#C5KUST8N6|nais>
"""
FALLBACK = "Your team has topics on Aiven which are not found in a nais cluster. " \
           "If this is not intentional, please rectify the situation."


class Color(str, enum.Enum):
    GOOD = "339900"
    WARNING = "ffcc00"
    DANGER = "cc3300"


class BlockType(str, enum.Enum):
    HEADER = "header"
    SECTION = "section"
    DIVIDER = "divider"


class TextType(str, enum.Enum):
    PLAIN = "plain_text"
    MARKDOWN = "mrkdwn"


@dataclasses.dataclass
class Text:
    type: TextType
    text: Optional[str] = None


@dataclasses.dataclass
class Header:
    text: Optional[Text] = None
    type: BlockType = BlockType.HEADER


@dataclasses.dataclass
class TextSection:
    text: Optional[Text] = None
    type: BlockType = BlockType.SECTION


@dataclasses.dataclass
class FieldsSection:
    fields: list[Text] = dataclasses.field(default_factory=list)
    type: BlockType = BlockType.SECTION


@dataclasses.dataclass
class Divider:
    type: BlockType = BlockType.DIVIDER


@dataclasses.dataclass
class Attachment:
    color: Optional[Color] = None
    fallback: Optional[str] = None
    blocks: list[Union[Header, TextSection, Divider]] = dataclasses.field(default_factory=list)


@dataclasses.dataclass
class Payload:
    channel: str
    text: Optional[str] = None
    blocks: list[Union[Header, TextSection, Divider]] = dataclasses.field(default_factory=list)
    attachments: list[Attachment] = dataclasses.field(default_factory=list)


def create_payload(team_topic):
    topics = [Text(TextType.PLAIN, topic) for topic in team_topic.topics]
    return Payload(team_topic.slack_channel, attachments=[
        Attachment(Color.WARNING, FALLBACK, blocks=[
            Header(Text(TextType.PLAIN, HEADER)),
            TextSection(Text(TextType.MARKDOWN, MAIN_TEXT)),
            Divider(),
            Header(Text(TextType.PLAIN, "Topics found")),
            FieldsSection(topics)
        ])
    ])


def post_payload(settings, payload):
    if settings.webhook_enabled and settings.webhook_url is not None:
        data = dataclasses.asdict(payload)
        resp = SESSION.post(settings.webhook_url, json=data)
        if LOG.isEnabledFor(logging.DEBUG):
            dumped = dump.dump_all(resp).decode('utf-8')
            LOG.debug(dumped)
        if not resp.ok:
            LOG.error("Failed sending data to webhook. The received message was:\n%s", resp.text)
    else:
        channel = payload.channel
        try:
            topics = payload.attachments[-1].fields[-1].value
        except KeyError:
            topics = "<unable to take topics from payload>"
        LOG.info("Would have notified %s about topics: %s", channel, topics)


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
