import os
import yaml

from institute.runtimes.registration import register_runtime

with open(os.path.join(os.path.dirname(__file__), '../runtimes.yml')) as f:
    spec = yaml.load(f)

# If you have a local repo, do something like
# export SYNTHAI_DOCKER_REPO=docker.synthai.com  (this one only for synthai folks)
docker_repo = os.environ.get('SYNTHAI_DOCKER_REPO', 'quay.io/synthai')

register_runtime(
    id='lab-core',
    kind='docker',
    image=docker_repo + '/institute.lab-core:{}'.format(spec['lab-core']['tag']),
)

register_runtime(
    id='flashgames',
    kind='docker',
    image=docker_repo + '/institute.flashgames:{}'.format(spec['flashgames']['tag']),
    host_config={
        'privileged': True,
        'cap_add': ['SYS_ADMIN'],
        'ipc_mode': 'host',
    },
    default_params={'cpu': 3.9, 'livestream_url': None},
    server_registry_file=os.path.join(os.path.dirname(__file__), 'flashgames.json'),
)

register_runtime(
    id='world-of-bits',
    kind='docker',
    image=docker_repo + '/institute.world-of-bits:{}'.format(spec['world-of-bits']['tag']),
    host_config={
        'privileged': True,
        'cap_add': ['SYS_ADMIN'],
        'ipc_mode': 'host'
    })

register_runtime(
    id='vnc-windows',
    kind='windows',
)

del spec
