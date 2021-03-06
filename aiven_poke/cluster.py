import functools
import logging
from collections import defaultdict

from k8s.base import Model
from k8s.fields import Field
from k8s.models.common import ObjectMeta
from k8s.models.namespace import Namespace

SLACK_CHANNEL = "slack-channel"
PLATFORM_ALERTS_CHANNEL = "platform-alerts-channel"

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


@functools.lru_cache
def get_slack_channel(team):
    ns = Namespace.get(team)
    an = ns.metadata.annotations
    slack_channel = an.get(PLATFORM_ALERTS_CHANNEL, an.get(SLACK_CHANNEL))
    if not slack_channel.startswith("#"):
        return f"#{slack_channel}"
    return slack_channel


def get_cluster_topics(settings):
    cluster_topics = Topic.list(namespace=None)
    namespaced_topics = defaultdict(set)
    for topic in cluster_topics:
        if topic.spec.pool == settings.main_project:
            namespaced_topics[topic.metadata.namespace].add(f"{topic.metadata.namespace}.{topic.metadata.name}")
    LOG.info("%d namespaces with topics found in cluster", len(namespaced_topics))
    return namespaced_topics
