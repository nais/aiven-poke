from unittest import mock

import pytest
from prometheus_client import Summary

from aiven_poke.models import TeamTopic
from aiven_poke.settings import Settings
from aiven_poke.slack import Attachment, Color, Divider, Header, Payload, post_payload, Text, TextType

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
            team_topic = TeamTopic("aura", "#channel", {"aura.test-topic", "aura.topic-test"})
            summary = Summary("slack_request_latency_seconds", "Slack requests latency")
            post_payload(settings, payload, team_topic, summary)
            m.post.assert_called()
