"""
module to handle capacity of resources
"""
import json

from autoscaler.config import Config
from autoscaler.kube import KubeResource

# RESOURCE_SPEC should denote the amount of resouces that are available
# to workload pods on a new, clean node, i.e. resouces used by system pods
# have to be accounted for
with open(Config.CAPACITY_DATA, 'r') as f:
    data = json.loads(f.read())
    RESOURCE_SPEC = {}
    for instance_type, resource_spec in data.items():
        resource_spec['cpu'] -= Config.CAPACITY_CPU_RESERVE
        resource = KubeResource(**resource_spec)
        RESOURCE_SPEC[instance_type] = resource

DEFAULT_TYPE_SELECTOR_KEYS = ('aws/type', 'azure/type')
DEFAULT_CLASS_SELECTOR_KEYS = ('aws/class', 'azure/class')
COMPUTING_SELECTOR_KEY = 'synthai/computing'


def is_possible(pod):
    """
    returns whether the pod is possible under the maximum allowable capacity
    """
    max_pod_capacity = max_capacity_for_selectors(pod.selectors, pod.resources)
    if not max_pod_capacity:
        return False
    return (max_pod_capacity - pod.resources).possible


def max_capacity_for_selectors(selectors, resource_requests):
    """
    returns the maximum capacity that is possible for the given selectors
    """
    selector = ''
    for key in DEFAULT_TYPE_SELECTOR_KEYS:
        if key in selectors:
            selector = selectors[key]
            break
    class_ = ''
    for key in DEFAULT_CLASS_SELECTOR_KEYS:
        if key in selectors:
            class_ = selectors[key]
            break

    unit_caps = RESOURCE_SPEC

    # HACK: we modify our types with -modifier for special groups
    # e.g. c4.8xlarge-public
    # our selectors don't have dashes otherwise, so remove the modifier
    selector, _, _ = selector.partition('-')
    class_, _, _ = class_.partition('-')
    azure_class = 'Standard_{}'.format(class_)

    # if an instance type was specified
    if selector in unit_caps:
        return unit_caps[selector]

    max_capacity = None
    for type_, resource in unit_caps.items():
        if (not class_ or type_.startswith(class_) or
                type_.startswith(azure_class)):
            if not max_capacity or (resource - max_capacity).possible or (resource - resource_requests).possible:
                max_capacity = resource

    return max_capacity


def get_unit_capacity(group):
    """
    returns the KubeResource provided by one unit in the
    AutoScalingGroup or KubeNode
    """
    return RESOURCE_SPEC[group.instance_type]
