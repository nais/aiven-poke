from aiven_poke.settings import Settings
from aiven_poke.slack import Payload, post_payload


class TestSlack():
    def test_post_payload(self):
        payload = Payload("#channel", "text", [])
        settings = Settings(aiven_token="fake_token")
        actual = post_payload(settings, payload)
        assert actual["channel"] == "#channel"
        assert actual["text"] == "text"
