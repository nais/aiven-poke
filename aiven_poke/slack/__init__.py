import dataclasses
import logging
from typing import Iterable, MutableMapping

import requests
from prometheus_client import Summary
from requests_toolbelt.utils import dump

from aiven_poke.aiven import User
from aiven_poke.models import TeamTopic
from aiven_poke.settings import Settings
from aiven_poke.slack.topics import create_topic_payload
from aiven_poke.slack.users import create_user_payload

LOG = logging.getLogger(__name__)
SESSION = requests.session()


class Poke:
    def __init__(self, settings: Settings, cluster_name):
        self._cluster_name = cluster_name
        self._settings = settings
        self._latency = Summary("slack_request_latency_seconds", "Slack requests latency")

    def topics(self, missing: Iterable[TeamTopic]):
        """Poke the teams with topics missing in the cluster"""
        for team_topic in missing:
            payload = create_topic_payload(team_topic, self._settings.main_project)
            self.post_payload(payload)
            channel = team_topic.slack_channel
            topics = ", ".join(team_topic.topics)
            LOG.info("Notified %s about topics: %s", channel, topics)

    def users(self, expiring_users: MutableMapping[str, list[User]], slack_channels: MutableMapping[str, str]):
        """Poke the teams with users with expiring credentials"""
        for team, users in expiring_users.items():
            channel = slack_channels[team]
            payload = create_user_payload(team, channel, users, self._settings.main_project, self._cluster_name)
            self.post_payload(payload)
            usernames = ", ".join(user.username for user in users)
            LOG.info("Notified %s about expiring users: %s", channel, usernames)

    def post_payload(self, payload):
        if self._settings.webhook_enabled and self._settings.webhook_url.get_secret_value() is not None:
            data = dataclasses.asdict(payload)
            with self._latency.time():
                resp = SESSION.post(self._settings.webhook_url.get_secret_value(), json=data)
            if LOG.isEnabledFor(logging.DEBUG):
                dumped = dump.dump_all(resp).decode('utf-8')
                LOG.debug(dumped)
            if not resp.ok:
                LOG.error("Failed sending data to webhook. The received message was:\n%s", resp.text)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    tt = TeamTopic("nais", "#jk-tullekanal",
                   frozenset(("nais.test-topic", "nais.topic-test", "nais.probably-a-test-too")))
    poke = Poke(Settings(), "test")
    poke.topics([tt])
