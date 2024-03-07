import functools
import logging
from collections import defaultdict

from k8s.base import Model, Equality
from k8s.client import NotFound
from k8s.fields import Field
from k8s.models.common import ObjectMeta
from k8s.models.namespace import Namespace
from k8s.models.secret import Secret
from prometheus_client import Summary

from aiven_poke.settings import Settings

SLACK_CHANNEL_KEY = "replicator.nais.io/slackAlertsChannel"

LOG = logging.getLogger(__name__)


class TopicSpec(Model):
    # Incomplete definition
    pool = Field(str)


class Topic(Model):
    class Meta:
        list_url = "/apis/kafka.nais.io/v1/topics"
        url_template = "/apis/kafka.nais.io/v1/namespaces/{namespace}/topics/{name}"

    apiVersion = Field(str, "kafka.nais.io/v1")  # NOQA
    kind = Field(str, "Topic")

    metadata = Field(ObjectMeta)
    spec = Field(TopicSpec)


def init_k8s_client(api_server):
    # TODO: Implement loading from KUBECONFIG for local development?
    from k8s import config
    try:
        config.use_in_cluster_config()
    except IOError:
        # Assume kubectl proxy is running without auth at given URL
        config.api_server = api_server


class Cluster:
    def __init__(self, settings: Settings):
        init_k8s_client(settings.api_server)
        self._settings = settings
        self._latency = Summary("k8s_latency_seconds", "Kubernetes latency", ["action", "resource"])

    @functools.lru_cache
    def get_namespace(self, team):
        try:
            with self._latency.labels("get", "namespace").time():
                return Namespace.get(team)
        except NotFound:
            if not team.startswith("team"):
                return self.get_namespace("team" + team)
            if not team.startswith("team-"):
                return self.get_namespace("team-" + team[4:])

    @functools.lru_cache
    def get_slack_channel(self, team):
        if self._settings.override_slack_channel is not None:
            return self._settings.override_slack_channel
        namespace = self.get_namespace(team)
        annotations = namespace.metadata.annotations
        slack_channel = annotations.get(SLACK_CHANNEL_KEY)
        if not slack_channel:
            LOG.error("Team %s has no slack channel set, directing poke to #nais-alerts-info", team)
            return "#nais-alerts-info"
        if not slack_channel.startswith("#"):
            return f"#{slack_channel}"
        return slack_channel

    def get_cluster_topics(self, gauge):
        with self._latency.labels("list", "topic").time():
            cluster_topics = Topic.list(namespace=None)
        namespaced_topics = defaultdict(set)
        for topic in cluster_topics:
            if topic.spec.pool == self._settings.main_project:
                namespaced_topics[topic.metadata.namespace].add(f"{topic.metadata.namespace}.{topic.metadata.name}")
                gauge.inc()
        LOG.info("%d namespaces with topics found in cluster", len(namespaced_topics))
        return namespaced_topics

    @functools.lru_cache
    def get_aiven_secrets_by_name(self, team):
        namespace = self.get_namespace(team)
        aiven_secrets_by_name = {}
        with self._latency.labels("list", "secret").time():
            secrets = Secret.find(namespace=namespace.metadata.name, labels={
                "type": Equality("aivenator.aiven.nais.io")
            })
            for secret in secrets:
                service_user = secret.metadata.annotations.get("kafka.aiven.nais.io/serviceUser")
                if service_user:
                    aiven_secrets_by_name[service_user] = secret
        return aiven_secrets_by_name
