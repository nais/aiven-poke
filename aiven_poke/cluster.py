from collections import defaultdict

from k8s.base import Model
from k8s.fields import Field
from k8s.models.common import ObjectMeta


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


def init_k8s_client():
    # TODO: Implement loading from KUBECONFIG for local development?
    from k8s import config
    try:
        config.use_in_cluster_config()
    except IOError:
        # Assume kubectl proxy is running
        config.api_server = "http://localhost:8001"


def get_cluster_topics():
    cluster_topics = Topic.list(namespace=None)
    namespaced_topics = defaultdict(set)
    for topic in cluster_topics:
        namespaced_topics[topic.metadata.namespace].add(f"{topic.metadata.namespace}.{topic.metadata.name}")
    return namespaced_topics
