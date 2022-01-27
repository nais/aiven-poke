#!/usr/bin/env python
import logging
import os
import signal
import sys

from fiaas_logging import init_logging

from aiven_poke.endpoints import start_server


class ExitOnSignal(Exception):
    pass


def signal_handler(signum, frame):
    raise ExitOnSignal()


def poke():
    return 0


def main():
    _init_logging()
    server = start_server()
    try:
        for sig in (signal.SIGTERM, signal.SIGINT):
            signal.signal(sig, signal_handler)
        try:
            exit_code = poke()
        except ExitOnSignal:
            exit_code = 0
        except Exception as e:
            logging.exception(f"unwanted exception: {e}")
            exit_code = 113
    finally:
        server.shutdown()
    sys.exit(exit_code)


def _init_logging():
    if os.getenv("NAIS_CLIENT_ID"):
        init_logging(format="json")
    else:
        init_logging(debug=True)
    logging.getLogger("werkzeug").setLevel(logging.WARN)
