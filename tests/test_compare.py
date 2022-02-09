from unittest import mock

import pytest

from aiven_poke.main import compare
from aiven_poke.models import TeamTopic


class TestCompare:
    @pytest.fixture
    def aiven_topics(self):
        return {
            "team1": {"team1.topic1", "team1.topic2", "team1.topic3"},
            "team2": {"team2.topic1", "team2.topic2", "team2.topic3"},
            "team3": {"team3.topic1", "team3.topic2", "team3.topic3"},
            "team4": {"team4.topic1", "team4.topic2", "team4.topic3"},
        }

    @pytest.fixture
    def cluster_topics(self):
        return {
            "team1": {"team1.topic2", "team1.topic3"},
            "team2": {"team2.topic1", "team2.topic3"},
            "team3": {"team3.topic1", "team3.topic2"},
            "team4": {"team4.topic1", "team4.topic2", "team4.topic3"},
        }

    @pytest.fixture
    def expected(self):
        return {
            TeamTopic("#team1", {"team1.topic1"}),
            TeamTopic("#team2", {"team2.topic2"}),
            TeamTopic("#team3", {"team3.topic3"}),
        }

    def test_compare(self, aiven_topics, cluster_topics, expected):
        with mock.patch("aiven_poke.main.get_slack_channel") as m:
            m.side_effect = lambda t: f"#{t}"
            actual = compare(aiven_topics, cluster_topics)
            assert actual == expected
