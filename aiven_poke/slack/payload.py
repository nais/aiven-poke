import dataclasses
import enum


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
    text: str | None = None


@dataclasses.dataclass
class Header:
    text: Text | None = None
    type: BlockType = BlockType.HEADER


@dataclasses.dataclass
class TextSection:
    text: Text | None = None
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
    color: Color | None = None
    fallback: str | None = None
    blocks: list[Header | TextSection | Divider] = dataclasses.field(default_factory=list)


@dataclasses.dataclass
class Payload:
    channel: str
    text: str | None = None
    blocks: list[Header | TextSection | Divider] = dataclasses.field(default_factory=list)
    attachments: list[Attachment] = dataclasses.field(default_factory=list)
