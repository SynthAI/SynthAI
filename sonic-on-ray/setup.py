from setuptools import setup, find_packages

setup(name='sonic_on_ray',
      packages=[package for package in find_packages()
                if package.startswith('sonic_on_ray')],
      description='Running lab retro on Ray',
      author='Philipp Moritz',
      url='https://github.com/synthai/sonic-on-ray',
      author_email='pcmoritz@gmail.com',
      version='0.0.1')
