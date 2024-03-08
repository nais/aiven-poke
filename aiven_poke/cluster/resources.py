from typing import ClassVar

from lightkube.core import resource as res
from lightkube.models import meta_v1

from . import models


class Topic(res.NamespacedResourceG, models.Topic):
    _api_info = res.ApiInfo(
        resource=res.ResourceDef('kafka.nais.io', 'v1', 'Topic'),
        plural='topics',
        verbs=['delete', 'deletecollection', 'get', 'global_list', 'global_watch', 'list', 'patch', 'post', 'put',
               'watch'],
    )

    Status: ClassVar = meta_v1.Status
