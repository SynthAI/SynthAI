from setuptools import setup, find_packages

setup(name='multiagent',
      version='0.0.1',
      description='Multi-Agent Goal-Driven Communication Environment',
      url='https://github.com/synthai/multiagent-public',
      author='Igor Mordatch',
      author_email='mordatch@synthai.com',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=['lab', 'numpy-stl']
)
