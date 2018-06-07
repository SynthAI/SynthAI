import collections
import datetime
import logging
import math
import time

import botocore
import boto3
import botocore.exceptions
import datadog
import pytz
import pykube

from enum import Enum

from azure.mgmt.compute import ComputeManagementClient
from azure.monitor import MonitorClient

from dateutil.parser import parse as dateutil_parse

from azure.mgmt.resource.resources import ResourceManagementClient
from azure.common.credentials import ServicePrincipalCredentials
from msrestazure.azure_exceptions import CloudError

import autoscaler.autoscaling_groups as autoscaling_groups
import autoscaler.azure as azure
from autoscaler.azure_api import AzureWriteThroughCachedApi, AzureWrapper
import autoscaler.capacity as capacity
from autoscaler.kube import KubePod, KubeNode, KubeResource, KubePodStatus
import autoscaler.utils as utils

# we are interested in all pods, incl. system ones
pykube.Pod.objects.namespace = None

logger = logging.getLogger(__name__)


class ClusterNodeState(Enum):
    DEAD = 'dead'
    INSTANCE_TERMINATED = 'instance-terminated'
    ASG_MIN_SIZE = 'asg-min-size'
    POD_PENDING = 'pod-pending'
    GRACE_PERIOD = 'grace-period'
    TYPE_GRACE_PERIOD = 'type-grace-period'
    IDLE_SCHEDULABLE = 'idle-schedulable'
    IDLE_UNSCHEDULABLE = 'idle-unschedulable'
    BUSY_UNSCHEDULABLE = 'busy-unschedulable'
    BUSY = 'busy'
    UNDER_UTILIZED_DRAINABLE = 'under-utilized-drainable'
    UNDER_UTILIZED_UNDRAINABLE = 'under-utilized-undrainable'
    LAUNCH_HR_GRACE_PERIOD = 'launch-hr-grace-period'
    DETACHED = 'detached'


class Cluster(object):

    # the number of instances per type that is allowed to be idle
    # this is for keeping some spare capacity around for faster
    # pod scheduling, instead of keeping the cluster at capacity
    # and having to spin up nodes for every job submission
    TYPE_IDLE_COUNT = 5

    # since we pay for the full hour, don't prematurely kill instances
    # the number of minutes into the launch hour at which an instance
    # is fine to kill
    LAUNCH_HOUR_THRESHOLD = {
        'aws': 60 * 30,
        'azure': 60 * 5,  # Azure is billed by the minute
    }

    # HACK: before we're ready to favor bigger instances in all cases
    # just prioritize the ones that we're confident about
    _GROUP_DEFAULT_PRIORITY = 10
    _GROUP_PRIORITIES = {
        'g2.8xlarge': 2,
        'm4.xlarge': 0,
        'm4.2xlarge': 0,
        'm4.4xlarge': 0,
        'm4.10xlarge': 0
    }

    def __init__(self, aws_regions, aws_access_key, aws_secret_key,
                 azure_client_id, azure_client_secret, azure_subscription_id, azure_tenant_id,
                 azure_resource_group_names, azure_slow_scale_classes, kubeconfig,
                 idle_threshold, type_idle_threshold, pod_namespace,
                 instance_init_time, cluster_name, notifier,
                 use_aws_iam_role=False,
                 drain_utilization_below=0.0,
                 max_scale_in_fraction=0.1,
                 scale_up=True, maintainance=True,
                 datadog_api_key=None,
                 over_provision=5, dry_run=False):
        if kubeconfig:
            # for using locally
            logger.debug('Using kubeconfig %s', kubeconfig)
            self.api = pykube.HTTPClient(
                pykube.KubeConfig.from_file(kubeconfig))
        else:
            # for using on kube
            logger.debug('Using kube service account')
            self.api = pykube.HTTPClient(
                pykube.KubeConfig.from_service_account())
        if pod_namespace is None:
            self.pod_namespace = pykube.all
        else:
            self.pod_namespace = pod_namespace

        self.drain_utilization_below = drain_utilization_below
        self.max_scale_in_fraction = max_scale_in_fraction
        self._drained = {}
        self.session = None
        if aws_access_key and aws_secret_key:
            self.session = boto3.session.Session(
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key,
                region_name=aws_regions[0])  # provide a default region
        elif use_aws_iam_role is True:
            self.session = boto3.session.Session(region_name=aws_regions[0])  # provide a default region
        self.autoscaling_groups = autoscaling_groups.AutoScalingGroups(
            session=self.session, regions=aws_regions,
            cluster_name=cluster_name)
        self.autoscaling_timeouts = autoscaling_groups.AutoScalingTimeouts(
            self.session)

        azure_regions = []
        resource_groups = []
        self.azure_client = None
        if azure_client_id:
            azure_credentials = ServicePrincipalCredentials(
                client_id=azure_client_id,
                secret=azure_client_secret,
                tenant=azure_tenant_id
            )

            # Setup the Azure client
            resource_client = ResourceManagementClient(azure_credentials, azure_subscription_id)
            resource_client.providers.register('Microsoft.Compute')
            resource_client.providers.register('Microsoft.Network')
            resource_client.providers.register('Microsoft.Insights')

            region_map = {}
            for resource_group_name in azure_resource_group_names:
                resource_group = resource_client.resource_groups.get(resource_group_name)
                location = resource_group.location
                if location in region_map:
                    logger.fatal("{} and {} are both in {}. May only have one resource group per region".format(
                        resource_group_name, region_map[location], location
                    ))
                region_map[location] = resource_group_name
                azure_regions.append(location)
                resource_groups.append(resource_group)

            compute_client = ComputeManagementClient(azure_credentials, azure_subscription_id)
            compute_client.config.retry_policy.policy = azure.AzureBoundedRetry.from_retry(compute_client.config.retry_policy.policy)

            monitor_client = MonitorClient(azure_credentials, azure_subscription_id)
            monitor_client.config.retry_policy.policy = azure.AzureBoundedRetry.from_retry(monitor_client.config.retry_policy.policy)
            self.azure_client = AzureWriteThroughCachedApi(AzureWrapper(compute_client, monitor_client, resource_client))

        self.azure_groups = azure.AzureGroups(resource_groups, azure_slow_scale_classes, self.azure_client)

        # config
        self.azure_resource_group_names = azure_resource_group_names
        self.azure_regions = azure_regions
        self.aws_regions = aws_regions
        self.idle_threshold = idle_threshold
        self.instance_init_time = instance_init_time
        self.type_idle_threshold = type_idle_threshold
        self.over_provision = over_provision

        self.scale_up = scale_up
        self.maintainance = maintainance

        self.notifier = notifier

        if datadog_api_key:
            datadog.initialize(api_key=datadog_api_key)
            logger.info('Datadog initialized')
        self.stats = datadog.ThreadStats()
        self.stats.start()

        self.dry_run = dry_run

    def scale_loop(self):
        """
        runs one loop of scaling to current needs.
        returns True if successfully scaled.
        """
        logger.info("++++++++++++++ Running Scaling Loop ++++++++++++++++")
        try:
            start_time = time.time()

            kube_lookup_start_time = time.time()
            pykube_nodes = pykube.Node.objects(self.api)
            if not pykube_nodes:
                logger.warn('Failed to list nodes. Please check kube configuration. Terminating scale loop.')
                return False

            all_nodes = list(map(KubeNode, pykube_nodes))
            managed_nodes = [node for node in all_nodes if node.is_managed()]

            pods = list(map(KubePod, pykube.Pod.objects(self.api, namespace=self.pod_namespace)))

            running_or_pending_assigned_pods = [
                p for p in pods if (p.status == KubePodStatus.RUNNING or p.status == KubePodStatus.CONTAINER_CREATING) or (
                    p.status == KubePodStatus.PENDING and p.node_name
                )
            ]

            for node in all_nodes:
                for pod in running_or_pending_assigned_pods:
                    if pod.node_name == node.name:
                        node.count_pod(pod)
            self.stats.gauge('autoscaler.scaling_loop.kube_lookup_time', time.time() - kube_lookup_start_time)

            scaling_group_lookup_start_time = time.time()
            if self.azure_client is not None:
                for resource_group in self.azure_resource_group_names:
                    # Force a refresh of the cache to pick up any new Scale Sets that have been created
                    # or modified externally.
                    self.azure_client.list_scale_sets(resource_group, force_refresh=True)
                    # Force a refresh of the cache in case our quota was adjusted
                    self.azure_client.invalidate_quota_cache(resource_group)
            asgs = self.autoscaling_groups.get_all_groups(all_nodes)
            azure_groups = self.azure_groups.get_all_groups(all_nodes)
            scaling_groups = asgs + azure_groups
            self.stats.gauge('autoscaler.scaling_loop.scaling_group_lookup_time', time.time() - scaling_group_lookup_start_time)

            instance_lookup_start_time = time.time()
            running_insts_map = self.get_running_instances_map(managed_nodes, azure_groups)
            self.stats.gauge('autoscaler.scaling_loop.instance_lookup_time', time.time() - instance_lookup_start_time)

            pods_to_schedule_lookup_start_time = time.time()
            pods_to_schedule = self.get_pods_to_schedule(pods)
            self.stats.gauge(
                'autoscaler.scaling_loop.pods_to_schedule_lookup_time',
                time.time() - pods_to_schedule_lookup_start_time,
            )

            pods_by_node = {}
            for p in running_or_pending_assigned_pods:
                pods_by_node.setdefault(p.node_name, []).append(p)

            if self.scale_up:
                logger.info(
                    "++++++++++++++ Scaling Up Begins ++++++++++++++++")
                self.scale(
                    pods_to_schedule, all_nodes, scaling_groups,
                    running_insts_map)
                logger.info("++++++++++++++ Scaling Up Ends ++++++++++++++++")
            if self.maintainance:
                logger.info(
                    "++++++++++++++ Maintenance Begins ++++++++++++++++")
                self.maintain(
                    managed_nodes, running_insts_map,
                    pods_to_schedule, running_or_pending_assigned_pods,
                    scaling_groups)
                logger.info("++++++++++++++ Maintenance Ends ++++++++++++++++")

            self.stats.gauge('autoscaler.scaling_loop_time', time.time() - start_time)

            return True
        except botocore.exceptions.ClientError as e:
            logger.warn(e)
            return False

    def scale(self, pods_to_schedule, all_nodes, asgs, running_insts_map):
        """
        scale up logic
        """
        # TODO: generalize to azure
        self.autoscaling_timeouts.refresh_timeouts(
            [asg for asg in asgs if asg.provider == 'aws'],
            dry_run=self.dry_run)

        cached_live_nodes = []
        for node in all_nodes:
            # either we know the physical node behind it and know it's alive
            # or we don't know it and assume it's alive
            if (node.instance_id and node.instance_id in running_insts_map) \
                    or (not node.is_managed()):
                cached_live_nodes.append(node)

        # selectors -> pending KubePods
        pending_pods = {}

        # for each pending & unassigned job, try to fit them on current machines or count requested
        #   resources towards future machines
        for selectors_hash, pods in pods_to_schedule.items():
            for pod in pods:
                fitting = None
                for node in cached_live_nodes:
                    if node.unschedulable:
                        continue
                    if node.is_match(pod) and node.can_fit(pod.resources):
                        fitting = node
                        break
                if fitting is None:
                    # because a pod may be able to fit in multiple groups
                    # pick a group now
                    selectors = dict(pod.selectors)
                    pending_pods.setdefault(utils.selectors_to_hash(selectors), []).append(pod)
                    logger.info(
                        "{pod} is pending ({selectors_hash})".format(
                            pod=pod, selectors_hash=selectors_hash))
                else:
                    fitting.count_pod(pod)
                    logger.info("{pod} fits on {node}".format(pod=pod,
                                                              node=fitting))

        # scale each node type to reach the new capacity
        for selectors_hash in set(pending_pods.keys()):
            self.fulfill_pending(asgs,
                                 selectors_hash,
                                 pending_pods.get(selectors_hash, []))

        # TODO: make sure desired capacities of untouched groups are consistent

    def maintain(self, cached_managed_nodes, running_insts_map,
                 pods_to_schedule, running_or_pending_assigned_pods, asgs):
        """
        maintains running instances:
        - determines if idle nodes should be drained and terminated
        - determines if there are bad nodes in ASGs (did not spin up under
          `instance_init_time` seconds)
        """
        logger.info("++++++++++++++ Maintaining Nodes & Instances ++++++++++++++++")

        # for each type of instance, we keep one around for longer
        # in order to speed up job start up time
        idle_selector_hash = collections.Counter()

        pods_by_node = {}
        for p in running_or_pending_assigned_pods:
            pods_by_node.setdefault(p.node_name, []).append(p)

        stats_time = time.time()

        nodes_to_scale_in = {}
        nodes_to_delete = []
        state_counts = dict((state, 0) for state in ClusterNodeState)
        for node in cached_managed_nodes:
            asg = utils.get_group_for_node(asgs, node)
            state = self.get_node_state(
                node, asg, pods_by_node.get(node.name, []), pods_to_schedule,
                running_insts_map, idle_selector_hash)

            logger.info("node: %-*s state: %s" % (75, node, state))
            state_counts[state] += 1

            # state machine & why doesnt python have case?
            if state in (ClusterNodeState.POD_PENDING, ClusterNodeState.BUSY,
                         ClusterNodeState.GRACE_PERIOD,
                         ClusterNodeState.TYPE_GRACE_PERIOD,
                         ClusterNodeState.ASG_MIN_SIZE,
                         ClusterNodeState.LAUNCH_HR_GRACE_PERIOD,
                         ClusterNodeState.DETACHED):
                # do nothing
                pass
            elif state == ClusterNodeState.UNDER_UTILIZED_DRAINABLE:
                if not self.dry_run:
                    if not asg:
                        logger.warn('Cannot find ASG for node %s. Not cordoned.', node)
                    else:
                        node.cordon()
                        node.drain(pods_by_node.get(node.name, []), notifier=self.notifier)
                else:
                    logger.info('[Dry run] Would have drained and cordoned %s', node)
            elif state == ClusterNodeState.IDLE_SCHEDULABLE:
                if not self.dry_run:
                    if not asg:
                        logger.warn('Cannot find ASG for node %s. Not cordoned.', node)
                    else:
                        node.cordon()
                else:
                    logger.info('[Dry run] Would have cordoned %s', node)
            elif state == ClusterNodeState.BUSY_UNSCHEDULABLE:
                # this is duplicated in original scale logic
                if not self.dry_run:
                    node.uncordon()
                else:
                    logger.info('[Dry run] Would have uncordoned %s', node)
            elif state == ClusterNodeState.IDLE_UNSCHEDULABLE:
                # remove it from asg
                if not self.dry_run:
                    nodes_to_delete.append(node)
                    if not asg:
                        logger.warn('Cannot find ASG for node %s. Not terminated.', node)
                    else:
                        nodes_to_scale_in.setdefault(asg, []).append(node)
                else:
                    logger.info('[Dry run] Would have scaled in %s', node)
            elif state == ClusterNodeState.INSTANCE_TERMINATED:
                if not self.dry_run:
                    nodes_to_delete.append(node)
                else:
                    logger.info('[Dry run] Would have deleted %s', node)
            elif state == ClusterNodeState.DEAD:
                if not self.dry_run:
                    nodes_to_delete.append(node)
                    if asg:
                        nodes_to_scale_in.setdefault(asg, []).append(node)
                else:
                    logger.info('[Dry run] Would have reaped dead node %s', node)
            elif state == ClusterNodeState.UNDER_UTILIZED_UNDRAINABLE:
                # noop for now
                pass
            else:
                raise Exception("Unhandled state: {}".format(state))

        for state, count in state_counts.items():
            self.stats.gauge('kubernetes.custom.node.state.{}'.format(state.value.replace('-', '_')), count)

        # these are instances that have been running for a while but it's not properly managed
        #   i.e. not having registered to kube or not having proper meta data set
        managed_instance_ids = set(node.instance_id for node in cached_managed_nodes)
        instances_to_terminate = {}
        unmanaged_instance_count = 0
        for asg in asgs:
            unmanaged_instance_ids = (asg.instance_ids - managed_instance_ids)
            if len(unmanaged_instance_ids) > 0:
                if asg.provider == 'azure':
                    for inst_id in unmanaged_instance_ids:
                        inst = asg.instances[inst_id]
                        if (datetime.datetime.now(inst.launch_time.tzinfo)
                                - inst.launch_time).seconds >= self.instance_init_time:
                            if not self.dry_run:
                                logger.info("terminating unmanaged %s" % inst)
                                instances_to_terminate.setdefault(asg, []).append(inst_id)
                                unmanaged_instance_count += 1
                                # TODO: try to delete node from kube as well
                                # in the case where kubelet may have registered but node
                                # labels have not been applied yet, so it appears unmanaged
                            else:
                                logger.info('[Dry run] Would have terminated unmanaged %s', inst)
                else:
                    unmanaged_running_insts = self.get_running_instances_in_region(
                        asg.region, list(unmanaged_instance_ids))
                    for inst in unmanaged_running_insts:
                        if (datetime.datetime.now(inst.launch_time.tzinfo)
                                - inst.launch_time).seconds >= self.instance_init_time:
                            if not self.dry_run:
                                asg.client.terminate_instance_in_auto_scaling_group(
                                    InstanceId=inst.id, ShouldDecrementDesiredCapacity=False)
                                logger.info("terminating unmanaged %s" % inst)
                                unmanaged_instance_count += 1
                                # TODO: try to delete node from kube as well
                                # in the case where kubelet may have registered but node
                                # labels have not been applied yet, so it appears unmanaged
                            else:
                                logger.info(
                                    '[Dry run] Would have terminated unmanaged %s [%s]', inst, asg.region)
        self.stats.gauge('kubernetes.custom.node.state.unmanaged', unmanaged_instance_count)

        async_operations = []
        total_instances = max(sum(len(asg.instance_ids) for asg in asgs), len(cached_managed_nodes))
        max_allowed_scale_in = int(math.ceil(self.max_scale_in_fraction * total_instances))
        to_scale_in = sum(len(nodes) for nodes in nodes_to_scale_in.values()) + \
                      sum(len(instance_ids) for instance_ids in instances_to_terminate.values())
        to_scale_in = max(to_scale_in, len(nodes_to_delete))
        if to_scale_in > max_allowed_scale_in:
            logger.error("TOO MANY NODES TO SCALE IN: {}, max allowed is {}".format(to_scale_in, max_allowed_scale_in))
        elif not self.dry_run:
            for asg, nodes in nodes_to_scale_in.items():
                async_operations.append(asg.scale_nodes_in(nodes))

            for asg, instance_ids in instances_to_terminate.items():
                async_operations.append(asg.terminate_instances(instance_ids))

            for node in nodes_to_delete:
                node.delete()

        # Wait for all background scale-in operations to complete
        for operation in async_operations:
            try:
                operation.result()
            except CloudError as e:
                logger.warn("Error while deleting Azure node: {}".format(e.message))
            except TimeoutError:
                logger.warn("Timeout while deleting Azure node")

    def fulfill_pending(self, asgs, selectors_hash, pods):
        """
        selectors_hash - string repr of selectors
        pods - list of KubePods that are pending
        """
        logger.info(
            "========= Scaling for %s ========", selectors_hash)
        logger.debug("pending: %s", pods[:5])

        accounted_pods = dict((p, False) for p in pods)
        num_unaccounted = len(pods)

        groups = utils.get_groups_for_hash(asgs, selectors_hash)

        groups = self._prioritize_groups(groups)

        async_operations = []
        for group in groups:
            logger.debug("group: %s", group)
            if (self.autoscaling_timeouts.is_timed_out(group) or group.is_timed_out() or group.max_size == group.desired_capacity) \
                    and not group.unschedulable_nodes:
                continue

            unit_capacity = capacity.get_unit_capacity(group)
            new_instance_resources = []
            assigned_pods = []
            for pod, acc in accounted_pods.items():
                if acc or not (unit_capacity - pod.resources).possible or not group.is_taints_tolerated(pod):
                    continue

                found_fit = False
                for i, instance in enumerate(new_instance_resources):
                    if (instance - pod.resources).possible:
                        new_instance_resources[i] = instance - pod.resources
                        assigned_pods[i].append(pod)
                        found_fit = True
                        break
                if not found_fit:
                    new_instance_resources.append(
                        unit_capacity - pod.resources)
                    assigned_pods.append([pod])

            # new desired # machines = # running nodes + # machines required to fit jobs that don't
            # fit on running nodes. This scaling is conservative but won't
            # create starving
            units_needed = len(new_instance_resources)
            # The pods may not fit because of resource requests or taints. Don't scale in that case
            if units_needed == 0:
                continue
            units_needed += self.over_provision

            if self.autoscaling_timeouts.is_timed_out(group) or group.is_timed_out():
                # if a machine is timed out, it cannot be scaled further
                # just account for its current capacity (it may have more
                # being launched, but we're being conservative)
                unavailable_units = max(
                    0, units_needed - (group.desired_capacity - group.actual_capacity))
            else:
                unavailable_units = max(
                    0, units_needed - (group.max_size - group.actual_capacity))
            units_requested = units_needed - unavailable_units

            logger.debug("units_needed: %s", units_needed)
            logger.debug("units_requested: %s", units_requested)

            new_capacity = group.actual_capacity + units_requested
            if not self.dry_run:
                async_operation = group.scale(new_capacity)
                async_operations.append(async_operation)

                def notify_if_scaled(future):
                    if future.result():
                        flat_assigned_pods = []
                        for instance_pods in assigned_pods:
                            flat_assigned_pods.extend(instance_pods)
                        self.notifier.notify_scale(group, units_requested, flat_assigned_pods)

                async_operation.add_done_callback(notify_if_scaled)
            else:
                logger.info(
                    '[Dry run] Would have scaled up (%s) to %s', group, new_capacity)

            for i in range(min(len(assigned_pods), units_requested)):
                for pod in assigned_pods[i]:
                    accounted_pods[pod] = True
                    num_unaccounted -= 1

            logger.debug("remining pending: %s", num_unaccounted)

            if not num_unaccounted:
                break

        if num_unaccounted:
            logger.warn('Failed to scale sufficiently.')
            self.notifier.notify_failed_to_scale(selectors_hash, pods)

        for operation in async_operations:
            try:
                operation.result()
            except CloudError as e:
                logger.warn("Error while scaling Scale Set: {}".format(e.message))
            except TimeoutError:
                logger.warn("Timeout while scaling Scale Set")

    def get_running_instances_in_region(self, region, instance_ids):
        """
        a generator for getting ec2.Instance objects given a list of
        instance IDs.
        """
        if not region:
            logger.warn('Instance IDs without region: %s', instance_ids)
            return

        yielded_ids = set()
        try:
            running_insts = (self.session
                             .resource('ec2', region_name=region)
                             .instances
                             .filter(
                                 InstanceIds=instance_ids,
                                 Filters=[{
                                     'Name': "instance-state-name",
                                     'Values': ["running"]}]
                             ))
            # we have to go through each instance to make sure
            # they actually exist and handle errors otherwise
            # boto collections do not always call DescribeInstance
            # when returning from filter, so it could error during
            # iteration
            for inst in running_insts:
                yield inst
                yielded_ids.add(inst.id)
        except botocore.exceptions.ClientError as e:
            logger.debug('Caught %s', e)
            if str(e).find("InvalidInstanceID.NotFound") == -1:
                raise e
            elif len(instance_ids) == 1:
                return
            else:
                # this should hopefully happen rarely so we resort to slow methods to
                # handle this case
                for instance_id in instance_ids:
                    if instance_id in yielded_ids:
                        continue
                    for inst in self.get_running_instances_in_region(region, [instance_id]):
                        yield inst

    def get_running_instances_map(self, nodes, azure_groups):
        """
        given a list of KubeNode's, return a map of
        instance_id -> ec2.Instance object
        """
        instance_map = {}

        # first get azure instances
        for group in azure_groups:
            if isinstance(group, azure.AzureVirtualScaleSet):
                for instance in group.get_azure_instances():
                    instance_map[instance.id] = instance

        # now get aws instances
        instance_id_by_region = {}
        for node in nodes:
            if node.provider == 'aws':
                instance_id_by_region.setdefault(node.region, []).append(node.instance_id)

        for region, instance_ids in instance_id_by_region.items():
            # note that this assumes that all instances have a valid region
            # the regions referenced by the nodes may also be outside of the
            # list of regions provided by the user
            # this should be ok because they will just end up being nodes
            # unmanaged by autoscaling groups we know about
            region_instances = self.get_running_instances_in_region(
                region, instance_ids)
            instance_map.update((inst.id, inst) for inst in region_instances)

        return instance_map

    def _get_required_capacity(self, requested, group):
        """
        returns the number of nodes within an autoscaling group that should
        be provisioned to fit the requested amount of KubeResource.

        TODO: bin packing would probably be better?

        requested - KubeResource
        group - AutoScalingGroup
        """
        unit_capacity = capacity.get_unit_capacity(group)
        return max(
            # (peter) should 0.8 be configurable?
            int(math.ceil(requested.get(field, 0.0) / unit_capacity.get(field, 1.0)))
            for field in ('cpu', 'memory', 'pods')
        )

    def _prioritize_groups(self, groups):
        """
        returns the groups sorted in order of where we should try to schedule
        things first. we currently try to prioritize in the following order:
        - region
        - single-AZ groups over multi-AZ groups (for faster/cheaper network)
        - whether or not the group launches spot instances (prefer spot)
        - manually set _GROUP_PRIORITIES
        - group name
        """
        def sort_key(group):
            region = self._GROUP_DEFAULT_PRIORITY
            try:
                region = (self.azure_regions + self.aws_regions).index(group.region)
            except ValueError:
                pass
            # Some ASGs are pinned to be in a single AZ. Sort them in front of
            # multi-ASG groups that won't have this tag set.
            pinned_to_az = group.selectors.get('aws/az', 'z')
            priority = self._GROUP_PRIORITIES.get(
                group.selectors.get('aws/type'), self._GROUP_DEFAULT_PRIORITY)
            return (group.global_priority, region, pinned_to_az, not group.is_spot, priority, group.name)
        return sorted(groups, key=sort_key)

    def get_node_state(self, node, asg, node_pods, pods_to_schedule,
                       running_insts_map, idle_selector_hash):
        """
        returns the ClusterNodeState for the given node

        params:
        node - KubeNode object
        asg - AutoScalingGroup object that this node belongs in. can be None.
        node_pods - list of KubePods assigned to this node
        pods_to_schedule - list of all pending pods
        running_inst_map - map of all (instance_id -> ec2.Instance object)
        idle_selector_hash - current map of idle nodes by type. may be modified
        """
        pending_list = []
        for pods in pods_to_schedule.values():
            for pod in pods:
                # a pod is considered schedulable onto this node if all the
                # node selectors match
                # AND it doesn't use pod affinity (which we don't support yet)
                if (node.is_match(pod) and
                        'scheduler.alpha.kubernetes.io/affinity' not in pod.annotations):
                    pending_list.append(pod)
        # we consider a node to be busy if it's running any non-DaemonSet pods
        # TODO: we can be a bit more aggressive in killing pods that are
        # replicated
        busy_list = [p for p in node_pods if not p.is_mirrored()]
        undrainable_list = [p for p in node_pods if not p.is_drainable()]
        utilization = sum((p.resources for p in busy_list), KubeResource())
        under_utilized = (self.drain_utilization_below *
                          node.capacity - utilization).possible
        drainable = not undrainable_list

        maybe_inst = running_insts_map.get(node.instance_id)
        if maybe_inst:
            age = (datetime.datetime.now(maybe_inst.launch_time.tzinfo)
                   - maybe_inst.launch_time).seconds
            launch_hour_offset = age % 3600
        else:
            age = None

        instance_type = utils.selectors_to_hash(
            asg.selectors) if asg else node.instance_type

        type_spare_capacity = (instance_type and self.type_idle_threshold and
                               idle_selector_hash[instance_type] < self.TYPE_IDLE_COUNT)

        if maybe_inst is None:
            return ClusterNodeState.INSTANCE_TERMINATED

        if node.is_detached():
            return ClusterNodeState.DETACHED

        if node.is_dead():
            return ClusterNodeState.DEAD

        if asg and len(asg.nodes) <= asg.min_size:
            return ClusterNodeState.ASG_MIN_SIZE

        if busy_list and not under_utilized:
            if node.unschedulable:
                return ClusterNodeState.BUSY_UNSCHEDULABLE
            return ClusterNodeState.BUSY

        if pending_list and not node.unschedulable:
            # logger.warn('PENDING: %s', pending_list)
            return ClusterNodeState.POD_PENDING

        if launch_hour_offset < self.LAUNCH_HOUR_THRESHOLD[node.provider] and not node.unschedulable:
            return ClusterNodeState.LAUNCH_HR_GRACE_PERIOD

        # elif node.provider == 'azure':
            # disabling scale down in azure for now while we ramp up
            # TODO: remove once azure is bootstrapped
            # state = ClusterNodeState.GRACE_PERIOD

        if (not type_spare_capacity and age <= self.idle_threshold) and not node.unschedulable:
            # there is already an instance of this type sitting idle
            # so we use the regular idle threshold for the grace period
            return ClusterNodeState.GRACE_PERIOD

        if (type_spare_capacity and age <= self.type_idle_threshold) and not node.unschedulable:
            # we don't have an instance of this type yet!
            # use the type idle threshold for the grace period
            # and mark the type as seen
            idle_selector_hash[instance_type] += 1
            return ClusterNodeState.TYPE_GRACE_PERIOD

        if under_utilized and (busy_list or not node.unschedulable):
            # nodes that are under utilized (but not completely idle)
            # have their own states to tell if we should drain them
            # for better binpacking or not
            if drainable:
                return ClusterNodeState.UNDER_UTILIZED_DRAINABLE
            return ClusterNodeState.UNDER_UTILIZED_UNDRAINABLE

        if node.unschedulable:
            return ClusterNodeState.IDLE_UNSCHEDULABLE
        return ClusterNodeState.IDLE_SCHEDULABLE

    def get_pods_to_schedule(self, pods):
        """
        given a list of KubePod objects,
        return a map of (selectors hash -> pods) to be scheduled
        """
        pending_unassigned_pods = [
            p for p in pods
            if p.status == KubePodStatus.PENDING and (not p.node_name)
        ]

        # we only consider a pod to be schedulable if it's pending and
        # unassigned and feasible
        pods_to_schedule = {}
        now = datetime.datetime.now(pytz.utc)
        for pod in pending_unassigned_pods:
            age = (now - pod.creation_time).total_seconds()
            self.stats.histogram('autoscaler.scaling_loop.pending_pod_age', age)

            if capacity.is_possible(pod):
                pods_to_schedule.setdefault(
                    utils.selectors_to_hash(pod.selectors), []).append(pod)
            else:
                recommended_capacity = capacity.max_capacity_for_selectors(
                    pod.selectors, pod.resources)
                logger.warn(
                    "Pending pod %s cannot fit %s. "
                    "Please check that requested resource amount is "
                    "consistent with node selectors (recommended max: %s). "
                    "Scheduling skipped." % (pod.name, pod.selectors, recommended_capacity))
                self.notifier.notify_invalid_pod_capacity(
                    pod, recommended_capacity)
        return pods_to_schedule
