#!/usr/bin/env python
import logging
import os
import signal
import sys

from fiaas_logging import init_logging

from aiven_poke.aiven import get_aiven_topics
from aiven_poke.cluster import init_k8s_client, get_cluster_topics
from aiven_poke.endpoints import start_server
from aiven_poke.settings import Settings


class ExitOnSignal(Exception):
    pass


def signal_handler(signum, frame):
    raise ExitOnSignal()


def compare(aiven_topics, cluster_topics):
    missing = set()
    for team, topics in aiven_topics.items():
        in_cluster = cluster_topics[team]
        missing.update(topics - in_cluster)
    return missing


def poke(settings):
    aiven_topics = get_aiven_topics(settings)
    cluster_topics = get_cluster_topics()
    missing_in_cluster = compare(aiven_topics, cluster_topics)  # NOQA
    # TODO: Poke someone!
    return 0


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
    try:
        for sig in (signal.SIGTERM, signal.SIGINT):
            signal.signal(sig, signal_handler)
        try:
            exit_code = poke(settings)
        except ExitOnSignal:
            exit_code = 0
        except Exception as e:
            logging.exception(f"unwanted exception: {e}")
            exit_code = 113
    finally:
        server.shutdown()
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
