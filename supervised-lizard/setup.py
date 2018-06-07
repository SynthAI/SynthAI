"""
Module configuration.
"""

from setuptools import setup

setup(
    name='supervised-lizard',
    version='0.0.1',
    description='Lizard for supervised meta-learning',
    long_description='Lizard for supervised meta-learning',
    url='https://github.com/synthai/supervised-lizard',
    author='Alex Nichol',
    author_email='alex@synthai.com',
    license='MIT',
    keywords='ai machine learning',
    packages=['supervised_lizard'],
    install_requires=[
        'numpy>=1.0.0,<2.0.0',
        'Pillow>=4.0.0,<5.0.0'
    ],
    extras_require={
        "tf": ["tensorflow>=1.0.0"],
        "tf_gpu": ["tensorflow-gpu>=1.0.0"],
    }
)
