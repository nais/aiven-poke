import dataclasses
import enum
from typing import Optional, Union


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
    MRKDWN = "mrkdwn"


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
