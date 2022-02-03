from collections import defaultdict
from dataclasses import dataclass

import requests


@dataclass
class Tag:
    key: str
    value: str


@dataclass
class Topic:
    cleanup_policy: str
    min_insync_replicas: int
    partitions: int
    replication: int
    retention_bytes: int
    retention_hours: int
    state: str
    tags: list[Tag]
    topic_name: str


class AivenAuth(requests.auth.AuthBase):
    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers["authorization"] = f"Bearer {self.token}"
        return r


class AivenKafka(object):
    base = "https://api.aiven.io/v1/project"

    def __init__(self, token, project, service=None, dry_run=False):
        self.project = project
        if service is None:
            service = project + "-kafka"
        self.service = service
        self.dry_run = dry_run
        self.session = requests.Session()
        self.session.auth = AivenAuth(token)
        self.base_url = f"{self.base}/{self.project}/service/{self.service}"

    def get_topics(self):
        resp = self.session.get(f"{self.base_url}/topic")
        resp.raise_for_status()
        data = resp.json()
        topics = []
        for t in data["topics"]:
            topic = Topic(**t)
            topic.tags = [Tag(**tag) for tag in t["tags"]]
            topics.append(topic)
        return topics


def get_aiven_topics(settings):
    aiven = AivenKafka(settings.aiven_token, settings.main_project)
    aiven_topics = aiven.get_topics()
    team_topics = defaultdict(set)
    for topic in aiven_topics:
        if "." in topic.topic_name:
            team, _ = topic.topic_name.split(".", maxsplit=1)
            team_topics[team].add(topic.topic_name)
    return team_topics
