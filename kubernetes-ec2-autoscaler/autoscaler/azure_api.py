import logging
import json
import re

from azure.monitor import MonitorClient
from azure.monitor.models import EventData
from copy import deepcopy
from datetime import datetime, timedelta
from threading import RLock, Condition
from typing import List, Tuple, MutableMapping, Mapping

import pytz
from abc import ABC
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.compute.models import VirtualMachineScaleSet, Sku
from azure.mgmt.resource import ResourceManagementClient

from autoscaler.utils import Future

logger = logging.getLogger(__name__)


PRIORITY_TAG = 'priority'
# Value should be a json map of NoSchedule taint key-values
NO_SCHEDULE_TAINTS_TAG = 'no_schedule_taints'


class AzureScaleSet:
    def __init__(self, location: str, resource_group: str, name: str, instance_type: str, capacity: int,
                 provisioning_state: str, timeout_until: datetime = None, timeout_reason: str = None, priority: int = None,
                 no_schedule_taints: Mapping[str, str] = {}) -> None:
        self.name = name
        self.instance_type = instance_type
        self.capacity = capacity
        self.provisioning_state = provisioning_state
        self.resource_group = resource_group
        self.location = location
        self.timeout_until = timeout_until
        self.timeout_reason = timeout_reason
        self.priority = priority
        self.no_schedule_taints = no_schedule_taints

    def __str__(self):
        return 'AzureScaleSet({}, {}, {}, {})'.format(self.name, self.instance_type, self.capacity, self.provisioning_state)

    def __repr__(self):
        return str(self)

    def _key(self):
        return (self.name, self.instance_type, self.capacity, self.provisioning_state, self.resource_group, self.location,
                self.timeout_until, self.timeout_reason, self.priority, tuple(self.no_schedule_taints.items()))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, AzureScaleSet):
            return False
        return self._key() == other._key()

    def __hash__(self) -> int:
        return hash(self._key())


class AzureScaleSetInstance:
    def __init__(self, instance_id: str, vm_id: str, launch_time: datetime) -> None:
        self.instance_id = instance_id
        self.vm_id = vm_id
        self.launch_time = launch_time

    def __str__(self):
        return 'AzureScaleSetInstance({}, {}, {})'.format(self.instance_id, self.vm_id, self.launch_time)

    def __repr__(self):
        return str(self)

    def _key(self):
        return (self.instance_id, self.vm_id, self.launch_time)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, AzureScaleSetInstance):
            return False
        return self._key() == other._key()

    def __hash__(self) -> int:
        return hash(self._key())


class AzureApi(ABC):
    def list_scale_sets(self, resource_group_name: str) -> List[AzureScaleSet]:
        pass

    def list_scale_set_instances(self, scale_set: AzureScaleSet) -> List[AzureScaleSetInstance]:
        pass

    def update_scale_set(self, scale_set: AzureScaleSet, new_capacity: int) -> Future:
        pass

    def terminate_scale_set_instances(self, scale_set: AzureScaleSet, instances: List[AzureScaleSetInstance]) -> Future:
        pass

    def get_remaining_instances(self, resource_group_name: str, sku: str) -> int:
        pass


TIMEOUT_PERIOD = timedelta(minutes=15)


# Mangles a SKU name into the family name used for quotas
def _azure_sku_family(name: str) -> str:
    match = re.match('Standard_(?P<family>[A-Z]{1,2})[0-9]{1,2}_?(?P<version>v[0-9])?', name)
    if match is None:
        raise ValueError("SKU not from a recognized family: " + name)
    result = "standard" + match.group('family')
    if match.group('version') is not None:
        result += match.group('version')
    result += 'Family'
    return result


class AzureWrapper(AzureApi):
    def __init__(self, compute_client: ComputeManagementClient, monitor_client: MonitorClient, resource_client: ResourceManagementClient) -> None:
        self._compute_client = compute_client
        self._monitor_client = monitor_client
        self._resource_client = resource_client

    def list_scale_sets(self, resource_group_name: str) -> List[AzureScaleSet]:
        fifteen_minutes_ago = datetime.now(pytz.utc) - TIMEOUT_PERIOD
        filter_clause = "eventTimestamp ge '{}' and resourceGroupName eq '{}'".format(fifteen_minutes_ago, resource_group_name)
        select_clause = "authorization,status,subStatus,properties,resourceId,eventTimestamp"

        failures_by_scale_set: MutableMapping[str, List[EventData]] = {}
        for log in self._monitor_client.activity_logs.list(filter=filter_clause, select=select_clause):
            if (log.status and log.status.value == 'Failed') or (log.properties and log.properties.get('statusCode') == 'Conflict'):
                if log.authorization and log.authorization.action and 'delete' in log.authorization.action:
                    continue
                failures_by_scale_set.setdefault(log.resource_id, []).append(log)

        result = []
        for scale_set in self._compute_client.virtual_machine_scale_sets.list(resource_group_name):
            failures = sorted(failures_by_scale_set.get(scale_set.id, []), key=lambda x: x.event_timestamp, reverse=True)
            timeout_until = None
            timeout_reason = None
            for failure in failures:
                status_message = json.loads(failure.properties.get('statusMessage', "{}")) if failure.properties else {}
                error_details = status_message.get('error', {})
                if 'message' in error_details:
                    timeout_until = failure.event_timestamp + TIMEOUT_PERIOD
                    timeout_reason = error_details['message']
                    # Stop if we found a message with details
                    break
                if timeout_until is None:
                    timeout_until = failure.event_timestamp + TIMEOUT_PERIOD
                    timeout_reason = failure.sub_status.localized_value

            priority = int(scale_set.tags[PRIORITY_TAG]) if PRIORITY_TAG in scale_set.tags else None
            no_schedule_taints = json.loads(scale_set.tags.get(NO_SCHEDULE_TAINTS_TAG, '{}'))

            result.append(AzureScaleSet(scale_set.location, resource_group_name, scale_set.name, scale_set.sku.name,
                                        scale_set.sku.capacity, scale_set.provisioning_state, timeout_until=timeout_until,
                                        timeout_reason=timeout_reason, priority=priority, no_schedule_taints=no_schedule_taints))
        return result

    def list_scale_set_instances(self, scale_set: AzureScaleSet) -> List[AzureScaleSetInstance]:
        result = []
        for instance in self._compute_client.virtual_machine_scale_set_vms.list(scale_set.resource_group, scale_set.name, expand="instanceView"):
            launch_time = datetime.now(pytz.utc)
            for status in instance.instance_view.statuses:
                if status.code == 'ProvisioningState/succeeded':
                    launch_time = status.time
                    break
            result.append(AzureScaleSetInstance(instance.instance_id, instance.vm_id, launch_time))
        return result

    def update_scale_set(self, scale_set: AzureScaleSet, new_capacity: int) -> Future:
        parameters = VirtualMachineScaleSet(scale_set.location, sku=Sku(name=scale_set.instance_type, capacity=new_capacity))
        azure_op = self._compute_client.virtual_machine_scale_sets.create_or_update(scale_set.resource_group, scale_set.name,
                                                                                    parameters=parameters)
        return AzureOperationPollerFutureAdapter(azure_op)

    def terminate_scale_set_instances(self, scale_set: AzureScaleSet, instances: List[AzureScaleSetInstance]) -> Future:
        future = self._compute_client.virtual_machine_scale_sets.delete_instances(scale_set.resource_group, scale_set.name, [instance.instance_id for instance in instances])
        return AzureOperationPollerFutureAdapter(future)

    def get_remaining_instances(self, resource_group_name: str, sku: str):
        resource_group = self._resource_client.resource_groups.get(resource_group_name)
        cores_per_instance = None
        for vm_size in self._compute_client.virtual_machine_sizes.list(location=resource_group.location):
            if vm_size.name == sku:
                cores_per_instance = vm_size.number_of_cores

        if cores_per_instance is None:
            logger.warn("No metadata found for sku: " + sku)
            return 0

        for usage in self._compute_client.usage.list(location=resource_group.location):
            if usage.name.value == _azure_sku_family(sku):
                return (usage.limit - usage.current_value) // cores_per_instance

        logger.warn("No quota found matching: " + sku)
        return 0


class AzureWriteThroughCachedApi(AzureApi):
    def __init__(self, delegate: AzureApi) -> None:
        self._delegate = delegate
        self._lock = RLock()
        self._instance_cache: MutableMapping[Tuple[str, str], List[AzureScaleSetInstance]] = {}
        self._scale_set_cache: MutableMapping[str, List[AzureScaleSet]] = {}
        self._remaining_instances_cache: MutableMapping[str, MutableMapping[str, int]] = {}

    def invalidate_quota_cache(self, resource_group_name: str) -> None:
        with self._lock:
            if resource_group_name in self._remaining_instances_cache:
                del self._remaining_instances_cache[resource_group_name]

    def list_scale_sets(self, resource_group_name: str, force_refresh=False) -> List[AzureScaleSet]:
        if not force_refresh:
            with self._lock:
                if resource_group_name in self._scale_set_cache:
                    return deepcopy(self._scale_set_cache[resource_group_name])

        scale_sets = self._delegate.list_scale_sets(resource_group_name)
        with self._lock:
            old_scale_sets = dict((x.name, x) for x in self._scale_set_cache.get(resource_group_name, []))
            for scale_set in scale_sets:
                old_scale_set = old_scale_sets.get(scale_set.name)
                if not old_scale_set:
                    continue

                # Check if Scale Set was changed externally
                if old_scale_set.capacity != scale_set.capacity:
                    if (resource_group_name, scale_set.name) in self._instance_cache:
                        del self._instance_cache[(resource_group_name, scale_set.name)]

            self._scale_set_cache[resource_group_name] = scale_sets
        return deepcopy(scale_sets)

    def list_scale_set_instances(self, scale_set: AzureScaleSet) -> List[AzureScaleSetInstance]:
        key = (scale_set.resource_group, scale_set.name)
        with self._lock:
            if key in self._instance_cache:
                return deepcopy(self._instance_cache[key])

        instances = self._delegate.list_scale_set_instances(scale_set)
        # Make sure we don't poison the cache, if our delegate is eventually consistent
        if len(instances) == scale_set.capacity:
            with self._lock:
                self._instance_cache[key] = instances
        return deepcopy(instances)

    def update_scale_set(self, scale_set: AzureScaleSet, new_capacity: int) -> Future:
        future = self._delegate.update_scale_set(scale_set, new_capacity)
        future.add_done_callback(lambda _: self._invalidate(scale_set.resource_group, scale_set.name))
        return future

    def terminate_scale_set_instances(self, scale_set: AzureScaleSet, instances: List[AzureScaleSetInstance]) -> Future:
        future = self._delegate.terminate_scale_set_instances(scale_set, instances)
        future.add_done_callback(lambda _: self._invalidate(scale_set.resource_group, scale_set.name))
        return future

    def get_remaining_instances(self, resource_group_name: str, sku: str):
        with self._lock:
            if resource_group_name in self._remaining_instances_cache:
                cached = self._remaining_instances_cache[resource_group_name]
                if sku in cached:
                    return cached[sku]
        remaining = self._delegate.get_remaining_instances(resource_group_name, sku)
        with self._lock:
            self._remaining_instances_cache.setdefault(resource_group_name, {})[sku] = remaining
        return remaining

    def _invalidate(self, resource_group_name: str, scale_set_name: str) -> None:
        with self._lock:
            if (resource_group_name, scale_set_name) in self._instance_cache:
                del self._instance_cache[(resource_group_name, scale_set_name)]

            if resource_group_name in self._scale_set_cache:
                del self._scale_set_cache[resource_group_name]

            if resource_group_name in self._remaining_instances_cache:
                del self._remaining_instances_cache[resource_group_name]


_AZURE_API_MAX_WAIT = 10*60


# Adapts an Azure async operation to behave like a Future
class AzureOperationPollerFutureAdapter(Future):
    def __init__(self, azure_operation):
        self._done = False
        self._result = None
        self._exception = None
        # NOTE: All this complexity with a Condition is here because AzureOperationPoller is not reentrant,
        # so a callback added with add_done_callback() could not call result(), if we delegated everything
        self._condition = Condition()
        self._callbacks = []
        self.azure_operation = azure_operation
        azure_operation.add_done_callback(self._handle_completion)

    def _handle_completion(self, result):
        with self._condition:
            self._done = True
            if self.azure_operation._exception is None:
                self._result = result
            else:
                self._exception = self.azure_operation._exception
            self._condition.notifyAll()
            callbacks = self._callbacks
            self._callbacks.clear()

        for callback in callbacks:
            callback(self)

    def result(self):
        callbacks = []
        try:
            with self._condition:
                if not self._done:
                    self._condition.wait(_AZURE_API_MAX_WAIT)
                    if not self._done:
                        # We reached the timeout
                        self._exception = TimeoutError()
                        self._done = True
                        callbacks = self._callbacks
                        self._callbacks.clear()
                if self._exception:
                    raise self._exception
                return self._result
        finally:
            for callback in callbacks:
                callback(self)

    def add_done_callback(self, fn):
        with self._condition:
            if self._done:
                fn(self)
            else:
                self._callbacks.append(fn)
