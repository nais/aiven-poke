import functools
import logging
from collections import defaultdict

from lightkube import Client, ApiError, ALL_NS
from lightkube.config.kubeconfig import KubeConfig
from lightkube.generic_resource import create_namespaced_resource
from lightkube.resources.core_v1 import Service, Namespace, Secret
from prometheus_client import Summary

from aiven_poke.cluster.resources import Topic
from aiven_poke.errors import KubernetesError
from aiven_poke.settings import Settings

SLACK_CHANNEL_KEY = "replicator.nais.io/slackAlertsChannel"

LOG = logging.getLogger(__name__)


def _create_k8s_client() -> Client:
    try:
        config = KubeConfig.from_env()
        client = Client(config.get())
        client.get(Service, "kubernetes", namespace="default")
        create_namespaced_resource("kafka.nais.io", "v1", "Topic", "topics")
    except Exception as e:
        raise KubernetesError(f"Unable to connect to kubernetes cluster") from e
    return client


class Cluster:
    def __init__(self, settings: Settings):
        self._client = _create_k8s_client()
        self._settings = settings
        self._latency = Summary("k8s_latency_seconds", "Kubernetes latency", ["action", "resource"])

    @functools.lru_cache
    def get_namespace(self, team):
        try:
            with self._latency.labels("get", "namespace").time():
                return self._client.get(Namespace, name=team)
        except ApiError as e:
            if e.status.code == 404:
                if not team.startswith("team"):
                    return self.get_namespace("team" + team)
                if not team.startswith("team-"):
                    return self.get_namespace("team-" + team[4:])
            raise

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
            cluster_topics = self._client.list(Topic, namespace=ALL_NS)
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
            secrets = self._client.list(Secret, namespace=namespace.metadata.name, labels={
                "type": "aivenator.aiven.nais.io"
            })
            for secret in secrets:
                service_user = secret.metadata.annotations.get("kafka.aiven.nais.io/serviceUser")
                if service_user:
                    aiven_secrets_by_name[service_user] = secret
        return aiven_secrets_by_name
