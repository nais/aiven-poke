import dataclasses
import enum
import logging
import textwrap
from typing import Optional, Iterable, Union

import requests
from requests_toolbelt.utils import dump

from aiven_poke.models import TeamTopic
from aiven_poke.settings import Settings

LOG = logging.getLogger(__name__)
SESSION = requests.session()

CREATE_DOC = "https://doc.nais.io/persistence/kafka/manage_topics/#creating-topics-and-defining-access"
PERMA_DELETE_DOC = "https://doc.nais.io/persistence/kafka/manage_topics/#permanently-deleting-topic-and-data"

# Messages
MAIN_HEADER = "Your team has topics on Aiven which are not found in a nais cluster"
WHAT_IS_THIS = " ".join(textwrap.dedent("""
    Topics on Aiven should be defined by a Topic resource in a nais cluster.
    Topics not defined by such a resource are inaccessible by applications on nais,
    which indicates that this topic may be forgotten.
""").splitlines())

TOPIC_HEADER = "*Forgotten topics found in the {main_project} pool*"

SOLUTION_HEADER = "*Solution*"
SOLUTION1 = " ".join(textwrap.dedent(f"""\
    To rectify the situation, start by <{CREATE_DOC}|re-creating the topic>.
    If the intention was to delete the topic, follow the procedure for <{PERMA_DELETE_DOC}|permanently deleting data>.
""").splitlines())
SOLUTION2 = " ".join(textwrap.dedent("""\
    If you need help, reach out in <#C73B9LC86|kafka> or <#C5KUST8N6|nais>
""").splitlines())

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


def create_payload(team_topic, main_project):
    topics = [Text(TextType.PLAIN, topic) for topic in team_topic.topics]
    return Payload(team_topic.slack_channel, attachments=[
        Attachment(Color.WARNING, FALLBACK, blocks=[
            Header(Text(TextType.PLAIN, MAIN_HEADER)),
            TextSection(Text(TextType.MARKDOWN, WHAT_IS_THIS)),
            TextSection(Text(TextType.MARKDOWN, TOPIC_HEADER.format(main_project=main_project))),
            FieldsSection(topics),
            TextSection(Text(TextType.MARKDOWN, SOLUTION_HEADER)),
            TextSection(Text(TextType.MARKDOWN, SOLUTION1)),
            TextSection(Text(TextType.MARKDOWN, SOLUTION2)),
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
        payload = create_payload(team_topic, settings.main_project)
        post_payload(settings, payload)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    settings = Settings()
    tt = TeamTopic("#pig-aiven", frozenset(("aura.test-topic", "aura.topic-test", "aura.probably-a-test-too")))
    poke(settings, [tt])
