#!/usr/bin/env python
# -*- coding: utf-8 -*-
import multiprocessing
import os
import subprocess
import sys

from setuptools import find_packages, Extension
from distutils.core import setup
from distutils.command.build import build as DistutilsBuild

def read(file_path):
    with open(file_path) as fp:
        return fp.read()

with open(os.path.join(os.path.dirname(__file__), 'src/fastzbarlight/package_data.txt')) as f:
    package_data = [line.rstrip() for line in f.readlines()]

# For parsing a 100x100 QR code, the default libzbar on Ubuntu is
# about 3x slower than when it's compiled with -O3. Thus we vendor and
# compile our own.
class Build(DistutilsBuild):
    def run(self):
        zbar = os.path.join(os.path.dirname(__file__), 'src/fastzbarlight/vendor/zbar-0.10')

        cores_to_use = max(1, multiprocessing.cpu_count() - 1)
        # Need -D_FORTIFY_SOURCE=0 since otherwise the build fails in
        # system header files.
        cmd = ['./configure', '--disable-dependency-tracking', '--without-python', '--without-qt', '--disable-video', '--without-gtk', '--without-imagemagick', '--with-x=no', 'CFLAGS=-Wall -Wno-parentheses -D_FORTIFY_SOURCE=0 -O3 -fPIC']
        try:
            subprocess.check_call(cmd, cwd=zbar)
        except subprocess.CalledProcessError as e:
            sys.stderr.write("Could not build fastzbarlight: %s.\n" % e)
            raise

        cmd = ['make', '-j', str(cores_to_use)]
        try:
            subprocess.check_call(cmd, cwd=zbar)
        except subprocess.CalledProcessError as e:
            sys.stderr.write("Could not build fastzbarlight: %s.\n" % e)
            raise
        except OSError as e:
            sys.stderr.write("Unable to execute '{}'. HINT: are you sure `make` is installed?\n".format(' '.join(cmd)))
            raise
        DistutilsBuild.run(self)

# HACK: it'd be better to build zbar without iconv, but this is
# easier for now
proc = subprocess.Popen(['ld', '-liconv'], stderr=subprocess.PIPE)
_, stderr = proc.communicate()
if b'-liconv' in stderr:
    libraries = []
else:
    libraries = ['iconv']

setup(
    name='fastzbarlight',
    version='0.0.14',
    description="A fork of zbarlight, which includes a vendored copy of zbar compiled with optimization flags",
    long_description=read('README.rst'),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: C',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Scientific/Engineering :: Image Recognition',
    ],
    keywords=['zbar', 'QR code reader'],
    license='BSD',
    packages=find_packages(where='src', exclude=['docs', 'tests']),
    package_dir={'': str('src')},
    ext_modules=[
        Extension(
            name=str('fastzbarlight._zbarlight'),
            sources=[str('src/fastzbarlight/_zbarlight.c')],
            extra_compile_args=['-std=c99', '-fPIC'],
            include_dirs=[os.path.join(os.path.dirname(__file__), 'src/fastzbarlight/vendor/zbar-0.10/include')],
            optional=os.environ.get('READTHEDOCS', False),  # Do not build on Read the Docs
            extra_link_args=[os.path.join(os.path.dirname(__file__), 'src/fastzbarlight/vendor/zbar-0.10/zbar/.libs/libzbar.a')],
            libraries=libraries,
        ),
    ],
    package_data={'fastzbarlight': package_data},
    zip_safe=False,
    setup_requires=[
        'setuptools',
    ],
    install_requires=[
        'Pillow',
    ],
    cmdclass={'build': Build},
)
