#!/usr/bin/env python
import logging
import os
import signal
import sys
from collections import defaultdict

from fiaas_logging import init_logging
from prometheus_client import push_to_gateway, REGISTRY, generate_latest, Gauge

from aiven_poke.aiven import AivenKafka
from aiven_poke.cluster import init_k8s_client, get_cluster_topics, get_slack_channel
from aiven_poke.endpoints import start_server
from aiven_poke.models import TeamTopic
from aiven_poke.settings import Settings
from aiven_poke.slack import Poke

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
            LOG.info("Starting job with config %s", settings)
            topic_gauge = Gauge("number_of_topics", "Number of topics found", ["source"])
            team_gauge = Gauge("number_of_teams", "Number of teams with topics", ["source"])
            expiring_users_gauge = Gauge("number_of_expiring_users",
                                         "Number of service users with expiring credentials")

            aiven = AivenKafka(settings.aiven_token.get_secret_value(), settings.main_project)
            poke = Poke(settings)
            if settings.topics_enabled:
                handle_topics(aiven, poke, settings, team_gauge, topic_gauge)
            if settings.expiring_users_enabled:
                handle_expiring_users(aiven, poke, expiring_users_gauge)

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


def handle_expiring_users(aiven, poke, expiring_users_gauge):
    users = aiven.get_users()
    expiring_users_per_team = defaultdict(list)
    count = 0
    for user in users:
        if user.expiring_cert_not_valid_after_time is None:
            continue
        expiring_users_per_team[user.team].append(user)
        count += 1
    expiring_users_gauge.set(count)

    slack_channels_per_team = {team: get_slack_channel(team) for team in expiring_users_per_team.keys()}

    poke.users(expiring_users_per_team, slack_channels_per_team)
    LOG.info("Completed poking about expiring users")


def handle_topics(aiven, poke, settings, team_gauge, topic_gauge):
    aiven_topics = aiven.get_team_topics(topic_gauge.labels("aiven"))
    team_gauge.labels("aiven").set(len(aiven_topics))
    cluster_topics = get_cluster_topics(settings, topic_gauge.labels("cluster"))
    team_gauge.labels("cluster").set(len(cluster_topics))
    missing_in_cluster = compare(aiven_topics, cluster_topics)
    team_gauge.labels("missing").set(len(missing_in_cluster))
    poke.topics(missing_in_cluster)
    LOG.info("Completed poking about topics")


if __name__ == '__main__':
    main()
