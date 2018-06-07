import datetime
import json
import logging

from typing import Iterable, Mapping

from dateutil.parser import parse as dateutil_parse
import pykube.exceptions

import autoscaler.utils as utils

logger = logging.getLogger(__name__)


class KubePodStatus(object):
    RUNNING = 'Running'
    PENDING = 'Pending'
    CONTAINER_CREATING = 'ContainerCreating'
    SUCCEEDED = 'Succeeded'
    FAILED = 'Failed'

_CORDON_LABEL = 'synthai/cordoned-by-autoscaler'


class KubePod(object):
    _DRAIN_GRACE_PERIOD = datetime.timedelta(seconds=60*60)

    def __init__(self, pod):
        self.original = pod

        metadata = pod.obj['metadata']
        self.name = metadata['name']
        self.namespace = metadata['namespace']
        self.node_name = pod.obj['spec'].get('nodeName')
        self.status = pod.obj['status']['phase']
        self.uid = metadata['uid']
        self.selectors = pod.obj['spec'].get('nodeSelector', {})
        self.labels = metadata.get('labels', {})
        self.annotations = metadata.get('annotations', {})
        self.owner = self.labels.get('owner', None)
        self.creation_time = dateutil_parse(metadata['creationTimestamp'])
        self.start_time = dateutil_parse(pod.obj['status']['startTime']) if 'startTime' in pod.obj['status'] else None
        self.scheduled_time = None

        for condition in pod.obj['status'].get('conditions', []):
            if condition['type'] == 'PodScheduled' and condition['status'] == 'True':
                self.scheduled_time = dateutil_parse(condition['lastTransitionTime'])

        # TODO: refactor
        requests = [c.get('resources', {}).get('requests', {}) for c in pod.obj['spec']['containers']]
        resource_requests = {}
        for d in requests:
            for k, v in d.items():
                unitless_v = utils.parse_SI(v)
                resource_requests[k] = resource_requests.get(k, 0.0) + unitless_v
        self.resources = KubeResource(pods=1, **resource_requests)
        self.no_schedule_wildcard_toleration = False
        self.no_execute_wildcard_toleration = False
        self.no_schedule_existential_tolerations = set()
        self.no_execute_existential_tolerations = set()
        for toleration in pod.obj['spec'].get('tolerations', []):
            if toleration.get('operator', 'Equal') == 'Exists':
                effect = toleration.get('effect')
                if effect is None or effect == 'NoSchedule':
                    if 'key' not in toleration:
                        self.no_schedule_wildcard_toleration = True
                    else:
                        self.no_schedule_existential_tolerations.add(toleration['key'])
                if effect is None or effect == 'NoExecute':
                    if 'key' not in toleration:
                        self.no_execute_wildcard_toleration = True
                    else:
                        self.no_execute_existential_tolerations.add(toleration['key'])
            else:
                logger.warn("Equality tolerations not implemented. Pod {} has an equality toleration".format(pod))

        self.required_pod_anti_affinity_expressions = []
        anti_affinity_spec = pod.obj['spec'].get('affinity', {}).get('podAntiAffinity', {})
        required_anti_affinity_expressions = anti_affinity_spec.get('requiredDuringSchedulingIgnoredDuringExecution', []) +\
                                             anti_affinity_spec.get('requiredDuringSchedulingRequiredDuringExecution', [])
        for expression in required_anti_affinity_expressions:
            if expression.get('topologyKey') != 'kubernetes.io/hostname':
                logger.debug("Pod {} has non-hostname anti-affinity topology. Ignoring".format(pod))
                continue
            self.required_pod_anti_affinity_expressions.append(expression['labelSelector']['matchExpressions'])


    def is_mirrored(self):
        created_by = json.loads(self.annotations.get('kubernetes.io/created-by', '{}'))
        is_daemonset = created_by.get('reference', {}).get('kind') == 'DaemonSet'
        return is_daemonset or self.annotations.get('kubernetes.io/config.mirror')

    def is_replicated(self):
        created_by = json.loads(self.annotations.get('kubernetes.io/created-by', '{}'))
        return created_by

    def is_critical(self):
        return utils.parse_bool_label(self.labels.get('synthai/do-not-drain'))

    def is_in_drain_grace_period(self):
        """
        determines whether the pod is in a grace period for draining
        this prevents us from draining pods that are too new
        """
        return (self.scheduled_time and
                (datetime.datetime.now(self.scheduled_time.tzinfo) - self.scheduled_time) < self._DRAIN_GRACE_PERIOD)

    def is_drainable(self):
        """
        a pod is considered drainable if:
        - it's a daemon
        - it's a non-critical replicated pod that has exceeded grace period
        """
        return (self.is_mirrored() or
                (self.is_replicated() and not self.is_critical() and not self.is_in_drain_grace_period()))

    def delete(self):
        logger.info('Deleting Pod %s/%s', self.namespace, self.name)
        return self.original.delete()

    def __hash__(self):
        return hash(self.uid)

    def __eq__(self, other):
        return self.uid == other.uid

    def __str__(self):
        return 'KubePod({namespace}, {name})'.format(
            namespace=self.namespace, name=self.name)

    def __repr__(self):
        return str(self)


def reverse_bytes(value):
    assert len(value) % 2 == 0
    result = ""
    for i in range(len(value), 0, -2):
        result += value[i - 2: i]
    return result


# Returns True iff all expressions in and_expression match labels on pod
def match_anti_affinity_expression(and_expression: Iterable[Mapping], pod: KubePod):
    for expression in and_expression:
        label_value = pod.labels.get(expression['key'])
        if expression['operator'] == 'In' and label_value not in expression['values']:
            return False
        elif expression['operator'] == 'NotIn' and label_value in expression['values']:
            return False
        elif expression['operator'] == 'Exists' and label_value is None:
            return False
        elif expression['operator'] == 'DoesNotExist' and label_value is not None:
            return False
    return True


class KubeNode(object):
    _HEARTBEAT_GRACE_PERIOD = datetime.timedelta(seconds=60*60)

    def __init__(self, node):
        self.original = node
        self.pykube_node = node

        metadata = node.obj['metadata']
        self.name = metadata['name']
        self.instance_id, self.region, self.instance_type, self.provider = self._get_instance_data()
        self.pods = []

        self.capacity = KubeResource(**node.obj['status']['allocatable'])
        self.used_capacity = KubeResource()
        self.creation_time = dateutil_parse(metadata['creationTimestamp'])
        last_heartbeat_time = self.creation_time
        for condition in node.obj['status'].get('conditions', []):
            if condition.get('type') == 'Ready':
                last_heartbeat_time = dateutil_parse(condition['lastHeartbeatTime'])
        self.last_heartbeat_time = last_heartbeat_time
        self.no_schedule_taints = {}
        self.no_execute_taints = {}
        for taint in node.obj['spec'].get('taints', []):
            if taint['effect'] == 'NoSchedule':
                try:
                    self.no_schedule_taints[taint['key']] = taint['value']
                except:
                    self.no_schedule_taints[taint['key']] = ""
            if taint['effect'] == 'NoExecute':
                self.no_execute_taints[taint['key']] = taint['value']

    def _get_instance_data(self):
        """
        returns a tuple (instance id, region, instance type)
        """
        labels = self.original.obj['metadata'].get('labels', {})
        instance_type = labels.get('aws/type', labels.get('beta.kubernetes.io/instance-type'))

        provider = self.original.obj['spec'].get('providerID', '')
        if provider.startswith('aws://'):
            az, instance_id = tuple(provider.split('/')[-2:])
            if az and instance_id:
                return (instance_id, az[:-1], instance_type, 'aws')

        if labels.get('aws/id') and labels.get('aws/az'):
            instance_id = labels['aws/id']
            region = labels['aws/az'][:-1]
            return (instance_id, region, instance_type, 'aws')

        assert provider.startswith('azure:////'), provider
        # Id is in wrong order: https://azure.microsoft.com/en-us/blog/accessing-and-using-azure-vm-unique-id/
        big_endian_vm_id = provider.replace('azure:////', '')
        parts = big_endian_vm_id.split('-')
        instance_id = '-'.join([reverse_bytes(parts[0]),
                                reverse_bytes(parts[1]),
                                reverse_bytes(parts[2]),
                                parts[3],
                                parts[4]]).lower()
        instance_type = labels['azure/type']
        return (instance_id, 'placeholder', instance_type, 'azure')

    @property
    def selectors(self):
        return self.original.obj['metadata'].get('labels', {})

    @property
    def unschedulable(self):
        return self.original.obj['spec'].get('unschedulable', False)

    @property
    def can_uncordon(self):
        return utils.parse_bool_label(self.selectors.get(_CORDON_LABEL))

    def drain(self, pods, notifier=None):
        for pod in pods:
            if pod.is_drainable() and not pod.is_mirrored():
                pod.delete()

        logger.info("drained %s", self)
        if notifier:
            notifier.notify_drained_node(self, pods)

    def uncordon(self):
        if not utils.parse_bool_label(self.selectors.get(_CORDON_LABEL)):
            logger.debug('uncordon %s ignored', self)
            return False

        try:
            self.original.reload()
            self.original.obj['spec']['unschedulable'] = False
            self.original.update()
            logger.info("uncordoned %s", self)
            return True
        except pykube.exceptions.HTTPError as ex:
            logger.info("uncordon failed %s %s", self, ex)
            return False

    def cordon(self):
        try:
            self.original.reload()
            self.original.obj['spec']['unschedulable'] = True
            self.original.obj['metadata'].setdefault('labels', {})[_CORDON_LABEL] = 'true'
            self.original.update()
            logger.info("cordoned %s", self)
            return True
        except pykube.exceptions.HTTPError as ex:
            logger.info("cordon failed %s %s", self, ex)
            return False

    def delete(self):
        try:
            self.original.delete()
            logger.info("deleted %s", self)
            return True
        except pykube.exceptions.HTTPError as ex:
            logger.info("delete failed %s %s", self, ex)
            return False

    def count_pod(self, pod):
        assert isinstance(pod, KubePod)
        self.used_capacity += pod.resources
        self.pods.append(pod)

    def can_fit(self, resources):
        assert isinstance(resources, KubeResource)
        left = self.capacity - (self.used_capacity + resources)
        return left.possible

    def is_match(self, pod: KubePod):
        """
        whether this node matches all the selectors on the pod
        """
        for label, value in pod.selectors.items():
            if self.selectors.get(label) != value:
                return False
        for key in self.no_schedule_taints:
            if not (pod.no_schedule_wildcard_toleration or key in pod.no_schedule_existential_tolerations):
                return False
        for key in self.no_execute_taints:
            if not (pod.no_execute_wildcard_toleration or key in pod.no_execute_existential_tolerations):
                return False
        for expression in pod.required_pod_anti_affinity_expressions:
            for pod in self.pods:
                if match_anti_affinity_expression(expression, pod):
                    return False

        return True

    def is_managed(self):
        """
        an instance is managed if we know its instance ID in ec2.
        """
        return self.instance_id is not None

    def is_detached(self):
        return utils.parse_bool_label(self.selectors.get('synthai/detached'))

    def is_dead(self):
        return datetime.datetime.now(self.last_heartbeat_time.tzinfo) - self.last_heartbeat_time > self._HEARTBEAT_GRACE_PERIOD

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name

    def __str__(self):
        return "{}: {} ({})".format(self.name, self.instance_id,
                                    utils.selectors_to_hash(self.selectors))


class KubeResource(object):

    def __init__(self, **kwargs):
        self.raw = dict((k, utils.parse_resource(v))
                        for (k, v) in kwargs.items())

    def __add__(self, other):
        keys = set(self.raw.keys()) | set(other.raw.keys())
        raw_diff = dict((k, self.raw.get(k, 0) + other.raw.get(k, 0))
                        for k in keys)
        return KubeResource(**raw_diff)

    def __sub__(self, other):
        keys = set(self.raw.keys()) | set(other.raw.keys())
        raw_diff = dict((k, self.raw.get(k, 0) - other.raw.get(k, 0))
                        for k in keys)
        return KubeResource(**raw_diff)

    def __mul__(self, multiplier):
        new_raw = dict((k, v * multiplier) for k, v in self.raw.items())
        return KubeResource(**new_raw)

    def __rmul__(self, multiplier):
        return self.__mul__(multiplier)

    def __cmp__(self, other):
        """
        should return a negative integer if self < other,
        zero if self == other, a positive integer if self > other.

        we consider self to be greater than other if it exceeds
        the resource amount in other in more resource types.
        e.g. if self = {cpu: 4, memory: 1K, gpu: 1},
        other = {cpu: 2, memory: 2K}, then self exceeds the resource
        amount in other in both cpu and gpu, while other exceeds
        the resource amount in self in only memory, so self > other.
        """
        resource_diff = (self - other).raw
        num_resource_types = len(resource_diff)
        num_eq = sum(1 for v in resource_diff.values() if v == 0)
        num_less = sum(1 for v in resource_diff.values() if v < 0)
        num_more = num_resource_types - num_eq - num_less
        return num_more - num_less

    def __str__(self):
        return str(self.raw)

    def get(self, key, default=None):
        return self.raw.get(key, default)

    @property
    def possible(self):
        return all([x >= 0 for x in self.raw.values()])
