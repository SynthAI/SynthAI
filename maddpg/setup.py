from setuptools import setup, find_packages

setup(name='maddpg',
      version='0.0.1',
      description='Multi-Agent Deep Deterministic Policy Gradient',
      url='https://github.com/synthai/maddpg',
      author='Igor Mordatch',
      author_email='mordatch@synthai.com',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=['lab', 'numpy-stl']
)
