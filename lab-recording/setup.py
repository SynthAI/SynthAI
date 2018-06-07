from setuptools import setup, find_packages

setup(name='lab_recording',
      version='0.0.1',
      install_requires=['lab', 'boto3'],
      packages=find_packages(),
)
