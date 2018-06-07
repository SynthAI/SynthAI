import json
import unittest
import mock
from datetime import datetime

import pytz
from azure.mgmt.compute.models import VirtualMachineScaleSet, Sku
from azure.monitor.models import EventData, LocalizableString

from autoscaler.azure_api import AzureApi, AzureScaleSet, AzureWriteThroughCachedApi, \
    AzureScaleSetInstance, AzureWrapper, TIMEOUT_PERIOD, PRIORITY_TAG, NO_SCHEDULE_TAINTS_TAG
from autoscaler.utils import CompletedFuture


class TestingFuture:
    def __init__(self):
        self.callbacks = []

    def add_done_callback(self, fn):
        self.callbacks.append(fn)

    def complete(self):
        for callback in self.callbacks:
            callback(self)


class TestWriteThroughCache(unittest.TestCase):
    def test_caching(self):
        scale_set = AzureScaleSet('eastus', 'test_rg', 'test', 'Standard_H16', 1, 'Succeeded')
        instance = AzureScaleSetInstance('fake_id', 'fake_vm', datetime.now())

        mock_api = mock.Mock(AzureApi)
        mock_api.list_scale_sets = mock.Mock(return_value=[scale_set])
        mock_api.list_scale_set_instances = mock.Mock(return_value=[instance])

        cached_api = AzureWriteThroughCachedApi(mock_api)

        self.assertEqual(cached_api.list_scale_sets('test_rg'), [scale_set])
        self.assertEqual(cached_api.list_scale_sets('test_rg'), [scale_set])

        self.assertEqual(cached_api.list_scale_set_instances(scale_set), [instance])
        self.assertEqual(cached_api.list_scale_set_instances(scale_set), [instance])

        mock_api.list_scale_sets.assert_called_once_with('test_rg')
        mock_api.list_scale_set_instances.assert_called_once_with(scale_set)

    def test_copied(self):
        scale_set = AzureScaleSet('eastus', 'test_rg', 'test', 'Standard_H16', 1, 'Succeeded')
        instance = AzureScaleSetInstance('fake_id', 'fake_vm', datetime.now())

        mock_api = mock.Mock(AzureApi)
        mock_api.list_scale_sets = mock.Mock(return_value=[scale_set])
        mock_api.list_scale_set_instances = mock.Mock(return_value=[instance])

        cached_api = AzureWriteThroughCachedApi(mock_api)

        returned_scale_set = cached_api.list_scale_sets('test_rg')[0]
        self.assertEqual(returned_scale_set.capacity, 1)
        returned_scale_set.capacity = 0
        self.assertEqual(cached_api.list_scale_sets('test_rg')[0].capacity, 1)

        returned_instance = cached_api.list_scale_set_instances(scale_set)[0]
        self.assertEqual(returned_instance.vm_id, 'fake_vm')
        returned_instance.vm_id = 'modified'
        self.assertEqual(cached_api.list_scale_set_instances(scale_set)[0].vm_id, 'fake_vm')

    def test_refresh(self):
        scale_set = AzureScaleSet('eastus', 'test_rg', 'test', 'Standard_H16', 1, 'Succeeded')
        updated_scale_set = AzureScaleSet('eastus', 'test_rg', 'test', 'Standard_H16', 0, 'Succeeded')
        scale_set2 = AzureScaleSet('eastus', 'test_rg', 'test2', 'Standard_H16', 0, 'Succeeded')
        instance = AzureScaleSetInstance('fake_id', 'fake_vm', datetime.now())

        mock_api = mock.Mock(AzureApi)
        mock_api.list_scale_sets = mock.Mock(return_value=[scale_set])
        mock_api.list_scale_set_instances = mock.Mock(return_value=[instance])

        cached_api = AzureWriteThroughCachedApi(mock_api)

        self.assertEqual(cached_api.list_scale_sets('test_rg'), [scale_set])
        self.assertEqual(cached_api.list_scale_set_instances(scale_set), [instance])
        mock_api.list_scale_sets.assert_called_once_with('test_rg')
        mock_api.list_scale_set_instances.assert_called_once_with(scale_set)

        mock_api.list_scale_sets = mock.Mock(return_value=[updated_scale_set, scale_set2])
        mock_api.list_scale_set_instances = mock.Mock(return_value=[])
        self.assertEqual(set(cached_api.list_scale_sets('test_rg', force_refresh=True)), {updated_scale_set, scale_set2})
        self.assertEqual(cached_api.list_scale_set_instances(updated_scale_set), [])
        mock_api.list_scale_sets.assert_called_once_with('test_rg')
        mock_api.list_scale_set_instances.assert_called_once_with(updated_scale_set)

    def test_update(self):
        scale_set = AzureScaleSet('eastus', 'test_rg', 'test', 'Standard_H16', 1, 'Succeeded')
        updated_scale_set = AzureScaleSet('eastus', 'test_rg', 'test', 'Standard_H16', 0, 'Succeeded')
        instance = AzureScaleSetInstance('fake_id', 'fake_vm', datetime.now())
        future = CompletedFuture(None)

        mock_api = mock.Mock(AzureApi)
        mock_api.list_scale_sets = mock.Mock(return_value=[scale_set])
        mock_api.list_scale_set_instances = mock.Mock(return_value=[instance])
        mock_api.update_scale_set = mock.Mock(return_value=future)

        cached_api = AzureWriteThroughCachedApi(mock_api)

        self.assertEqual(cached_api.list_scale_sets('test_rg'), [scale_set])
        self.assertEqual(cached_api.list_scale_set_instances(scale_set), [instance])
        cached_api.update_scale_set(scale_set, 0).result()
        mock_api.list_scale_sets.assert_called_once_with('test_rg')
        mock_api.list_scale_set_instances.assert_called_once_with(scale_set)
        mock_api.update_scale_set.assert_called_once_with(scale_set, 0)

        mock_api.list_scale_sets = mock.Mock(return_value=[updated_scale_set])
        mock_api.list_scale_set_instances = mock.Mock(return_value=[])
        self.assertEqual(cached_api.list_scale_sets('test_rg'), [updated_scale_set])
        self.assertEqual(cached_api.list_scale_set_instances(updated_scale_set), [])
        mock_api.list_scale_sets.assert_called_once_with('test_rg')
        mock_api.list_scale_set_instances.assert_called_once_with(updated_scale_set)

    def test_inconsistent_delegate(self):
        scale_set = AzureScaleSet('eastus', 'test_rg', 'test', 'Standard_H16', 0, 'Succeeded')
        updated_scale_set = AzureScaleSet('eastus', 'test_rg', 'test', 'Standard_H16', 1, 'Succeeded')
        instance = AzureScaleSetInstance('fake_id', 'fake_vm', datetime.now())
        future = CompletedFuture(None)

        mock_api = mock.Mock(AzureApi)
        mock_api.list_scale_sets = mock.Mock(return_value=[scale_set])
        mock_api.list_scale_set_instances = mock.Mock(return_value=[])
        mock_api.update_scale_set = mock.Mock(return_value=future)

        cached_api = AzureWriteThroughCachedApi(mock_api)

        self.assertEqual(cached_api.list_scale_sets('test_rg'), [scale_set])
        self.assertEqual(cached_api.list_scale_set_instances(scale_set), [])
        mock_api.list_scale_sets.assert_called_once_with('test_rg')
        mock_api.list_scale_set_instances.assert_called_once_with(scale_set)
        cached_api.update_scale_set(scale_set, 1).result()
        mock_api.update_scale_set.assert_called_once_with(scale_set, 1)

        mock_api.list_scale_sets = mock.Mock(return_value=[updated_scale_set])
        mock_api.list_scale_set_instances = mock.Mock(return_value=[])
        self.assertEqual(cached_api.list_scale_sets('test_rg'), [updated_scale_set])
        self.assertEqual(cached_api.list_scale_set_instances(updated_scale_set), [])
        mock_api.list_scale_sets.assert_called_once_with('test_rg')
        mock_api.list_scale_set_instances.assert_called_once_with(updated_scale_set)

        # Test that even if there is inconsistency between the list_scale_sets and list_scale_set_instances, the
        # cache doesn't end up with bad data
        mock_api.list_scale_set_instances = mock.Mock(return_value=[instance])
        self.assertEqual(cached_api.list_scale_set_instances(updated_scale_set), [instance])
        mock_api.list_scale_set_instances.assert_called_once_with(updated_scale_set)

    def test_terminate(self):
        scale_set = AzureScaleSet('eastus', 'test_rg', 'test', 'Standard_H16', 1, 'Succeeded')
        updated_scale_set = AzureScaleSet('eastus', 'test_rg', 'test', 'Standard_H16', 0, 'Succeeded')
        instance = AzureScaleSetInstance('fake_id', 'fake_vm', datetime.now())
        future = CompletedFuture(None)

        mock_api = mock.Mock(AzureApi)
        mock_api.list_scale_sets = mock.Mock(return_value=[scale_set])
        mock_api.list_scale_set_instances = mock.Mock(return_value=[instance])
        mock_api.terminate_scale_set_instances = mock.Mock(return_value=future)

        cached_api = AzureWriteThroughCachedApi(mock_api)

        self.assertEqual(cached_api.list_scale_sets('test_rg'), [scale_set])
        self.assertEqual(cached_api.list_scale_set_instances(scale_set), [instance])
        cached_api.terminate_scale_set_instances(scale_set, [instance]).result()
        mock_api.list_scale_sets.assert_called_once_with('test_rg')
        mock_api.list_scale_set_instances.assert_called_once_with(scale_set)
        mock_api.terminate_scale_set_instances.assert_called_once_with(scale_set, [instance])

        mock_api.list_scale_sets = mock.Mock(return_value=[updated_scale_set])
        mock_api.list_scale_set_instances = mock.Mock(return_value=[])
        self.assertEqual(cached_api.list_scale_sets('test_rg'), [updated_scale_set])
        self.assertEqual(cached_api.list_scale_set_instances(updated_scale_set), [])
        mock_api.list_scale_sets.assert_called_once_with('test_rg')
        mock_api.list_scale_set_instances.assert_called_once_with(updated_scale_set)

    def test_terminate_with_concurrent_read(self):
        scale_set = AzureScaleSet('eastus', 'test_rg', 'test', 'Standard_H16', 1, 'Succeeded')
        updated_scale_set = AzureScaleSet('eastus', 'test_rg', 'test', 'Standard_H16', 0, 'Succeeded')
        instance = AzureScaleSetInstance('fake_id', 'fake_vm', datetime.now())
        future = TestingFuture()

        mock_api = mock.Mock(AzureApi)
        mock_api.list_scale_sets = mock.Mock(return_value=[scale_set])
        mock_api.list_scale_set_instances = mock.Mock(return_value=[instance])
        mock_api.terminate_scale_set_instances = mock.Mock(return_value=future)

        cached_api = AzureWriteThroughCachedApi(mock_api)

        self.assertEqual(cached_api.list_scale_sets('test_rg'), [scale_set])
        self.assertEqual(cached_api.list_scale_set_instances(scale_set), [instance])
        cached_api.terminate_scale_set_instances(scale_set, [instance])
        mock_api.list_scale_sets.assert_called_once_with('test_rg')
        mock_api.list_scale_set_instances.assert_called_once_with(scale_set)
        mock_api.terminate_scale_set_instances.assert_called_once_with(scale_set, [instance])

        # Call list again concurrently with the delete, and make sure it's still served from the cache
        self.assertEqual(cached_api.list_scale_sets('test_rg'), [scale_set])
        self.assertEqual(cached_api.list_scale_set_instances(scale_set), [instance])
        mock_api.list_scale_sets.assert_called_once_with('test_rg')
        mock_api.list_scale_set_instances.assert_called_once_with(scale_set)

        future.complete()
        mock_api.list_scale_sets = mock.Mock(return_value=[updated_scale_set])
        mock_api.list_scale_set_instances = mock.Mock(return_value=[])
        self.assertEqual(cached_api.list_scale_sets('test_rg'), [updated_scale_set])
        self.assertEqual(cached_api.list_scale_set_instances(updated_scale_set), [])
        mock_api.list_scale_sets.assert_called_once_with('test_rg')
        mock_api.list_scale_set_instances.assert_called_once_with(updated_scale_set)


class TestWrapper(unittest.TestCase):
    def test_basic(self):
        scale_set = VirtualMachineScaleSet('eastus', {PRIORITY_TAG: '1', NO_SCHEDULE_TAINTS_TAG: json.dumps({'gpu': 'yes'})},
                                           sku=Sku('Standard_H16', capacity=1))
        scale_set.name = 'test'
        scale_set.provisioning_state = 'Succeeded'
        scale_set.id = 'fake_id'

        compute_client = mock.Mock()
        compute_client.virtual_machine_scale_sets = mock.Mock()
        compute_client.virtual_machine_scale_sets.list = mock.Mock(return_value=[scale_set])

        monitor_client = mock.Mock()
        monitor_client.activity_logs = mock.Mock()
        monitor_client.activity_logs.list = mock.Mock(return_value=[])

        api = AzureWrapper(compute_client, monitor_client, None)
        resource_group = 'test_rg'
        expected = AzureScaleSet(scale_set.location, resource_group, scale_set.name, scale_set.sku.name, scale_set.sku.capacity,
                                 scale_set.provisioning_state, priority=1, no_schedule_taints={'gpu': 'yes'})
        self.assertEqual([expected], api.list_scale_sets(resource_group))

        compute_client.virtual_machine_scale_sets.list.assert_called_once_with(resource_group)
        monitor_client.activity_logs.list.assert_called_once()

    def test_out_of_quota(self):
        scale_set = VirtualMachineScaleSet('eastus', {}, sku=Sku('Standard_H16', capacity=1))
        scale_set.name = 'test'
        scale_set.provisioning_state = 'Succeeded'
        scale_set.id = 'fake_id'

        compute_client = mock.Mock()
        compute_client.virtual_machine_scale_sets = mock.Mock()
        compute_client.virtual_machine_scale_sets.list = mock.Mock(return_value=[scale_set])

        reason = "Operation results in exceeding quota limits of Core. Maximum allowed: 800, Current in use: 784, Additional requested: 320."
        message = "{\"error\":{\"code\":\"OperationNotAllowed\",\"message\":\"" + reason + "\"}}"
        monitor_client = mock.Mock()
        monitor_client.activity_logs = mock.Mock()
        now = datetime.now(pytz.utc)
        monitor_client.activity_logs.list = mock.Mock(return_value=[EventData('Error',
                                                                              now,
                                                                              now,
                                                                              resource_id=scale_set.id,
                                                                              status=LocalizableString('Failed'),
                                                                              properties={'statusCode': 'Conflict',
                                                                                          'statusMessage': message})])

        api = AzureWrapper(compute_client, monitor_client, None)
        resource_group = 'test_rg'
        expected = AzureScaleSet(scale_set.location, resource_group, scale_set.name, scale_set.sku.name, scale_set.sku.capacity,
                                 scale_set.provisioning_state, now + TIMEOUT_PERIOD, reason)
        acutal = api.list_scale_sets(resource_group)
        self.assertEqual([expected], acutal)

        compute_client.virtual_machine_scale_sets.list.assert_called_once_with(resource_group)
        monitor_client.activity_logs.list.assert_called_once()
