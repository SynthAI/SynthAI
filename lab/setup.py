from setuptools import setup, find_packages
import sys, os.path

# Don't import lab module here, since deps may not be installed
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lab'))
from version import VERSION

# Environment-specific dependencies.
extras = {
  'atari': ['atari_py>=0.1.1', 'Pillow', 'PyOpenGL'],
  'box2d': ['Box2D-kengz'],
  'classic_control': ['PyOpenGL'],
  'mujoco': ['mujoco_py>=1.50', 'imageio'],
  'robotics': ['mujoco_py>=1.50', 'imageio'],
}

# Meta dependency groups.
all_deps = []
for group_name in extras:
    all_deps += extras[group_name]
extras['all'] = all_deps

setup(name='lab',
      version=VERSION,
      description='The SynthAI Lab: A toolkit for developing and comparing your reinforcement learning agents.',
      url='https://github.com/synthai/lab',
      author='SynthAI',
      author_email='lab@synthai.com',
      license='',
      packages=[package for package in find_packages()
                if package.startswith('lab')],
      zip_safe=False,
      install_requires=[
          'numpy>=1.10.4', 'requests>=2.0', 'six', 'pyglet>=1.2.0',
      ],
      extras_require=extras,
      package_data={'lab': [
        'envs/mujoco/assets/*.xml',
        'envs/classic_control/assets/*.png',
        'envs/robotics/assets/LICENSE.md',
        'envs/robotics/assets/fetch/*.xml',
        'envs/robotics/assets/hand/*.xml',
        'envs/robotics/assets/stls/fetch/*.stl',
        'envs/robotics/assets/stls/hand/*.stl',
        'envs/robotics/assets/textures/*.png']
      },
      tests_require=['pytest', 'mock'],
)
