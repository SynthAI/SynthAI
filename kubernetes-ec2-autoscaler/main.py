import logging
import sys
import time

import click

from autoscaler.cluster import Cluster
from autoscaler.notification import Notifier

logger = logging.getLogger('autoscaler')

DEBUG_LOGGING_MAP = {
    0: logging.CRITICAL,
    1: logging.WARNING,
    2: logging.INFO,
    3: logging.DEBUG
}


@click.command()
@click.option("--cluster-name")
@click.option("--aws-regions", default="us-west-1")
@click.option("--sleep", default=60)
@click.option("--kubeconfig", default=None,
              help='Full path to kubeconfig file. If not provided, '
                   'we assume that we\'re running on kubernetes.')
@click.option("--pod-namespace", default=None,
              help='The namespace to look for out-of-resource pods in. By '
                   'default, this will look in all namespaces.')
@click.option("--idle-threshold", default=3300)
@click.option("--type-idle-threshold", default=3600*24*7)
@click.option("--over-provision", default=5)
@click.option("--max-scale-in-fraction", default=0.1)
@click.option("--drain-utilization", default=0.0)
@click.option("--azure-slow-scale-classes", default="")
@click.option("--azure-resource-groups")
@click.option("--azure-client-id", default=None, envvar='AZURE_CLIENT_ID')
@click.option("--azure-client-secret", default=None, envvar='AZURE_CLIENT_SECRET')
@click.option("--azure-subscription-id", default=None, envvar='AZURE_SUBSCRIPTION_ID')
@click.option("--azure-tenant-id", default=None, envvar='AZURE_TENANT_ID')
@click.option("--aws-access-key", default=None, envvar='AWS_ACCESS_KEY_ID')
@click.option("--aws-secret-key", default=None, envvar='AWS_SECRET_ACCESS_KEY')
@click.option("--use-aws-iam-role", is_flag=True)
@click.option("--datadog-api-key", default=None, envvar='DATADOG_API_KEY')
@click.option("--instance-init-time", default=25 * 60)
@click.option("--no-scale", is_flag=True)
@click.option("--no-maintenance", is_flag=True)
@click.option("--slack-hook", default=None, envvar='SLACK_HOOK',
              help='Slack webhook URL. If provided, post scaling messages '
                   'to Slack.')
@click.option("--slack-bot-token", default=None, envvar='SLACK_BOT_TOKEN',
              help='Slack bot token. If provided, post scaling messages '
                   'to Slack users directly.')
@click.option("--dry-run", is_flag=True)
@click.option('--verbose', '-v',
              help="Sets the debug noise level, specify multiple times "
                   "for more verbosity.",
              type=click.IntRange(0, 3, clamp=True),
              count=True)
def main(cluster_name, aws_regions, azure_resource_groups, azure_slow_scale_classes, sleep, kubeconfig,
         azure_client_id, azure_client_secret, azure_subscription_id, azure_tenant_id,
         aws_access_key, aws_secret_key, use_aws_iam_role, pod_namespace, datadog_api_key,
         idle_threshold, type_idle_threshold, max_scale_in_fraction, drain_utilization,
         over_provision, instance_init_time, no_scale, no_maintenance,
         slack_hook, slack_bot_token, dry_run, verbose):
    logger_handler = logging.StreamHandler(sys.stderr)
    logger_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%dT%H:%M:%S%z'))
    logger.addHandler(logger_handler)
    logger.setLevel(DEBUG_LOGGING_MAP.get(verbose, logging.CRITICAL))

    aws_regions_list = aws_regions.split(',') if aws_regions else []
    if not ((aws_secret_key and aws_access_key) or use_aws_iam_role) and aws_regions_list:
        logger.error("Missing AWS credentials. Please provide aws-access-key and aws-secret-key.")
        sys.exit(1)

    notifier = Notifier(slack_hook, slack_bot_token)
    cluster = Cluster(aws_access_key=aws_access_key,
                      aws_secret_key=aws_secret_key,
                      use_aws_iam_role=use_aws_iam_role,
                      aws_regions=aws_regions_list,
                      azure_client_id=azure_client_id,
                      azure_client_secret=azure_client_secret,
                      azure_subscription_id=azure_subscription_id,
                      azure_tenant_id=azure_tenant_id,
                      azure_resource_group_names=azure_resource_groups.split(',') if azure_resource_groups else [],
                      azure_slow_scale_classes=azure_slow_scale_classes.split(',') if azure_slow_scale_classes else [],
                      kubeconfig=kubeconfig,
                      pod_namespace=pod_namespace,
                      idle_threshold=idle_threshold,
                      instance_init_time=instance_init_time,
                      type_idle_threshold=type_idle_threshold,
                      cluster_name=cluster_name,
                      max_scale_in_fraction=max_scale_in_fraction,
                      drain_utilization_below=drain_utilization,
                      scale_up=not no_scale,
                      maintainance=not no_maintenance,
                      over_provision=over_provision,
                      datadog_api_key=datadog_api_key,
                      notifier=notifier,
                      dry_run=dry_run,
                      )
    backoff = sleep
    while True:
        scaled = cluster.scale_loop()
        if scaled:
            time.sleep(sleep)
            backoff = sleep
        else:
            logger.warn("backoff: %s" % backoff)
            backoff *= 2
            time.sleep(backoff)


if __name__ == "__main__":
    main()
