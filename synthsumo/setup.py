import os
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join('..', path, filename))
    return paths

env_assets = package_files('synthsumo/envs/assets')
policy_assets = package_files('synthsumo/policy_zoo/assets')

setup(
    name='synthsumo',
    version='0.0.1.dev',
    packages=find_packages(),
    description='SynthSumo MuJoCo environments with Lab API.',
    long_description=read('README.md'),
    url='https://github.com/synthai/synthsumo',
    install_requires=[
        'click', 'lab', 'mujoco_py>=1.5', 'numpy', 'tensorflow>=1.1.0',
    ],
    package_data={
        'synthsumo': env_assets + policy_assets,
    },
)
