#!/usr/bin/env python
import logging
import os
import signal
import sys

from fiaas_logging import init_logging
from prometheus_client import push_to_gateway, REGISTRY, generate_latest, Gauge

from aiven_poke.aiven import get_aiven_topics
from aiven_poke.cluster import init_k8s_client, get_cluster_topics, get_slack_channel
from aiven_poke.endpoints import start_server
from aiven_poke.models import TeamTopic
from aiven_poke.settings import Settings
from aiven_poke.slack import poke

LOG = logging.getLogger(__name__)


class ExitOnSignal(Exception):
    pass


def signal_handler(signum, frame):
    raise ExitOnSignal()


def compare(aiven_topics, cluster_topics):
    result = set()
    for team, topics in aiven_topics.items():
        in_cluster = cluster_topics[team]
        missing = topics - in_cluster
        if missing:
            team_topic = TeamTopic(team, get_slack_channel(team), missing)
            result.add(team_topic)
    LOG.info("%d teams with topics on Aiven missing in cluster", len(result))
    return result


def _init_logging():
    if os.getenv("NAIS_CLIENT_ID"):
        init_logging(format="json")
    else:
        init_logging(debug=True)
    logging.getLogger("werkzeug").setLevel(logging.WARN)


def main():
    _init_logging()
    settings = Settings()
    init_k8s_client(settings.api_server)
    server = start_server()
    exit_code = 0
    try:
        for sig in (signal.SIGTERM, signal.SIGINT):
            signal.signal(sig, signal_handler)
        try:
            LOG.info("Starting job")
            topic_gauge = Gauge("number_of_topics", "Number of topics found", ["source"])
            team_gauge = Gauge("number_of_teams", "Number of teams with topics", ["source"])

            aiven_topics = get_aiven_topics(settings, topic_gauge.labels("aiven"))
            team_gauge.labels("aiven").set(len(aiven_topics))

            cluster_topics = get_cluster_topics(settings, topic_gauge.labels("cluster"))
            team_gauge.labels("cluster").set(len(cluster_topics))

            missing_in_cluster = compare(aiven_topics, cluster_topics)
            team_gauge.labels("missing").set(len(missing_in_cluster))

            poke(settings, missing_in_cluster)
            LOG.info("Completed poking")
            if settings.push_gateway_address:
                push_to_gateway(settings.push_gateway_address, job='aiven-poke', registry=REGISTRY)
            else:
                LOG.info(generate_latest().decode("utf-8"))
        except ExitOnSignal:
            pass
        except Exception as e:
            logging.exception("unwanted exception: %s", e)
            exit_code = 113
    finally:
        server.shutdown()
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
