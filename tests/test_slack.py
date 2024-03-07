from unittest import mock

import pytest

from aiven_poke.settings import Settings
from aiven_poke.slack import Attachment, Color, Header, Payload, Poke, Text, TextType
from aiven_poke.slack.payload import Divider

WEBHOOK_URL = "https://example.com"


class TestSlack:
    @pytest.fixture
    def payload(self):
        return Payload("#channel", "text", attachments=[
            Attachment(Color.GOOD, "att_fallback", blocks=[
                Header(Text(TextType.PLAIN, "header")),
                Divider(),
            ])
        ])

    def test_post_payload(self, payload):
        with mock.patch("aiven_poke.slack.SESSION") as m:
            settings = Settings(aiven_token="fake_token", webhook_url=WEBHOOK_URL)
            poke = Poke(settings)
            poke.post_payload(payload)
            m.post.assert_called()
