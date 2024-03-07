import logging
from collections import defaultdict
from datetime import datetime
from typing import Optional

import requests
from prometheus_client import Summary
from pydantic import BaseModel

LOG = logging.getLogger(__name__)


class Tag(BaseModel):
    key: str
    value: str


class Topic(BaseModel):
    cleanup_policy: str
    min_insync_replicas: int
    partitions: int
    replication: int
    retention_bytes: int
    retention_hours: int
    state: str
    tags: list[Tag]
    topic_name: str


class User(BaseModel):
    expiring_cert_not_valid_after_time: Optional[datetime] = None
    username: str

    @property
    def team(self):
        return self.username.split("_")[0]


class AivenAuth(requests.auth.AuthBase):
    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers["authorization"] = f"Bearer {self.token}"
        return r


class AivenKafka():
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
        self._latency = Summary("aiven_request_latency_seconds", "Aiven requests latency", ["action", "resource"])

    def get_users(self):
        with self._latency.labels("get", "service").time():
            resp = self.session.get(self.base_url)
        resp.raise_for_status()
        data = resp.json()
        return self._parse_users(data["service"])

    def _parse_users(self, data):
        return [User.model_validate(u) for u in data["users"]]

    def get_topics(self):
        with self._latency.labels("list", "topic").time():
            resp = self.session.get(f"{self.base_url}/topic")
        resp.raise_for_status()
        data = resp.json()
        return self._parse_topics(data)

    @staticmethod
    def _parse_topics(data):
        return [Topic.model_validate(t) for t in data["topics"]]

    def get_team_topics(self, gauge):
        aiven_topics = self.get_topics()
        team_topics = defaultdict(set)
        for topic in aiven_topics:
            if "_stream_" in topic.topic_name:
                continue
            if "." in topic.topic_name:
                team, _ = topic.topic_name.split(".", maxsplit=1)
                team_topics[team].add(topic.topic_name)
                gauge.inc()
        LOG.info("%d teams with topics found on Aiven", len(team_topics))
        return team_topics
