import pytest

from aiven_poke.aiven import AivenKafka


class TestAiven:
    @pytest.fixture(scope="module")
    def aiven(self):
        return AivenKafka("void", "void", dry_run=True)

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
                    "topic_name": "team1.others.v1"
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
                    "topic_name": "team1.api_stream_-case.v1-state-store-changelog"
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
                    "topic_name": "team1.topic1"
                }
            ]
        }

    def test_parse_topics(self, topic_data, aiven):
        topics = aiven._parse_topics(topic_data)
        assert len(topics) == len(topic_data["topics"])
        assert all(topics[i].topic_name == topic_data["topics"][i]["topic_name"] for i in range(len(topics)))

    @pytest.fixture
    def user_data(self):
        return {
            "users": [
                {
                    "access_cert": "-----BEGIN CERTIFICATE-----\n-----END CERTIFICATE-----\n",
                    "access_cert_not_valid_after_time": "2026-05-12T08:58:15Z",
                    "access_key": "-----BEGIN PRIVATE KEY-----\n-----END PRIVATE KEY-----\n",
                    "password": "not-a-password",
                    "type": "normal",
                    "username": "team1_api_ef438220_MTP"
                },
                {
                    "access_cert": "-----BEGIN CERTIFICATE-----\n-----END CERTIFICATE-----\n",
                    "access_cert_not_valid_after_time": "2025-11-25T10:59:17Z",
                    "access_key": "-----BEGIN PRIVATE KEY-----\n-----END PRIVATE KEY-----\n",
                    "password": "not-a-password",
                    "type": "normal",
                    "username": "team1_filestore_778663d9_fAK"
                },
                {
                    "access_cert": "-----BEGIN CERTIFICATE-----\n-----END CERTIFICATE-----\n",
                    "access_cert_not_valid_after_time": "2026-06-02T08:03:40Z",
                    "access_key": "-----BEGIN PRIVATE KEY-----\n-----END PRIVATE KEY-----\n",
                    "password": "not-a-password",
                    "type": "normal",
                    "username": "team1_collection_95a74f92_FYa"
                },
                {
                    "access_cert": "-----BEGIN CERTIFICATE-----\n-----END CERTIFICATE-----\n",
                    "access_cert_not_valid_after_time": "2026-05-10T20:40:03Z",
                    "access_key": "-----BEGIN PRIVATE KEY-----\n-----END PRIVATE KEY-----\n",
                    "expiring_cert_not_valid_after_time": "2024-05-10T20:11:16Z",
                    "password": "not-a-password",
                    "type": "normal",
                    "username": "team2_cucumber-feature_7c5d8385_rgu"
                },
                {
                    "access_cert": "-----BEGIN CERTIFICATE-----\n-----END CERTIFICATE-----\n",
                    "access_cert_not_valid_after_time": "2026-05-10T20:40:04Z",
                    "access_key": "-----BEGIN PRIVATE KEY-----\n-----END PRIVATE KEY-----\n",
                    "expiring_cert_not_valid_after_time": "2024-05-10T20:12:25Z",
                    "password": "not-a-password",
                    "type": "normal",
                    "username": "team2_cucumber_9fc2370d_rgu"
                },
            ]
        }

    def test_parse_users(self, user_data, aiven):
        users = aiven._parse_users(user_data)
        assert len(users) == len(user_data["users"])
        assert all(users[i].username == user_data["users"][i]["username"] for i in range(len(users)))
        assert all(u.team in ("team1", "team2") for u in users)
