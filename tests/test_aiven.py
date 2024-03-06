import pytest

from aiven_poke.aiven import AivenKafka
import pytest

from aiven_poke.aiven import AivenKafka


class TestAiven:
    @pytest.fixture
    def topic_data(self):
        return {
            "topics": [
                {
                    "cleanup_policy": "compact,delete",
                    "min_insync_replicas": 2,
                    "partitions": 12,
                    "replication": 3,
                    "retention_bytes": -1,
                    "retention_hours": 168,
                    "state": "ACTIVE",
                    "tags": [
                        {
                            "key": "created-by",
                            "value": "Kafkarator"
                        },
                        {
                            "key": "touched-at",
                            "value": "2022-10-20T08:10:15Z"
                        }
                    ],
                    "topic_name": "aap.andre-folketrygdytelser.v1"
                },
                {
                    "cleanup_policy": "compact",
                    "min_insync_replicas": 1,
                    "partitions": 12,
                    "replication": 3,
                    "retention_bytes": -1,
                    "retention_hours": 168,
                    "state": "ACTIVE",
                    "tags": [],
                    "topic_name": "aap.api_stream_-aap.vedtak.v1-state-store-changelog"
                },
                {
                    "cleanup_policy": "delete",
                    "min_insync_replicas": 1,
                    "partitions": 1,
                    "replication": 3,
                    "retention_bytes": -1,
                    "retention_hours": 336,
                    "state": "ACTIVE",
                    "tags": [
                        {
                            "key": "created-by",
                            "value": "Kafkarator"
                        },
                        {
                            "key": "touched-at",
                            "value": "2022-10-20T07:50:00Z"
                        }
                    ],
                    "topic_name": "yrkesskade.privat-yrkesskade-skademeldinginnsendt"
                }
            ]
        }

    def test_parse_topics(self, topic_data):
        aiven = AivenKafka("void", "void", dry_run=True)
        topics = aiven._parse_topics(topic_data)
        assert len(topics) == len(topic_data["topics"])
        assert all(topics[i].topic_name == topic_data["topics"][i]["topic_name"] for i in range(len(topics)))
