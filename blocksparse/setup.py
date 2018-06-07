#!/usr/bin/env python

import setuptools

setuptools.setup(
    name='blocksparse',
    version='1.0.0',
    description='Tensorflow ops for blocksparse matmul, convolution and related operations.',
    author='SynthAI',
    maintainer='Scott Gray',
    maintainer_email='scott@synthai.com',
    install_requires=[
        'numpy',
        'scipy',
        # We don't depend on `tensorflow` or `tensorflow-gpu` here, since one or the other is sufficient.
    ],
    packages=['blocksparse'],
    package_data={ 'blocksparse': ['blocksparse_ops.so'] },
    url='https://github.com/synthai/blocksparse',
    license='MIT')
