from dataclasses import dataclass

from lightkube.core.dataclasses_dict import DataclassDictMixIn
from lightkube.models import meta_v1


@dataclass
class TopicSpec(DataclassDictMixIn):
    # Incomplete definition
    pool: str = None


@dataclass
class Topic(DataclassDictMixIn):
    apiVersion: 'str' = None  # NOQA
    kind: 'str' = None
    metadata: meta_v1.ObjectMeta = None
    spec: TopicSpec = None
    status: meta_v1.Status = None
