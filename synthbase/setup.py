from setuptools import setup, find_packages
import sys

if sys.version_info.major != 3:
    print('This Python is only compatible with Python 3, but you are running '
          'Python {}. The installation will likely fail.'.format(sys.version_info.major))


setup(name='synthbase',
      packages=[package for package in find_packages()
                if package.startswith('synthbase')],
      install_requires=[
          'lab[mujoco,atari,classic_control,robotics]',
          'scipy',
          'tqdm',
          'joblib',
          'zmq',
          'dill',
          'progressbar2',
          'mpi4py',
          'cloudpickle',
          'tensorflow>=1.4.0',
          'click',
          'opencv-python'
      ],
      description='SynthAI synthbase: high quality implementations of reinforcement learning algorithms',
      author='SynthAI',
      url='https://github.com/synthai/synthbase',
      author_email='lab@synthai.com',
      version='0.1.5')
