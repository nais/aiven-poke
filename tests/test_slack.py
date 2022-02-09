from unittest import mock

import pytest

from aiven_poke.settings import Settings
from aiven_poke.slack import Attachment, Color, Field, Payload, post_payload

WEBHOOK_URL = "https://example.com"


class TestSlack:
    @pytest.fixture
    def payload(self):
        return Payload("#channel", "text", [
            Attachment("att_text", "att_fallback", "att_pretext", Color.GOOD, [
                Field("title", "value"),
            ])
        ])

    def test_post_payload(self, payload):
        with mock.patch("aiven_poke.slack.SESSION") as m:
            settings = Settings(aiven_token="fake_token", webhook_url=WEBHOOK_URL)
            post_payload(settings, payload)
            m.post.assert_called()
