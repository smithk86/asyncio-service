#!/usr/bin/env python

import os.path

from setuptools import setup, find_packages


# get the version to include in setup()
dir_ = os.path.abspath(os.path.dirname(__file__))
with open(f'{dir_}/asyncio_service/__init__.py') as fh:
    for line in fh:
        if '__VERSION__' in line:
            exec(line)


setup(
    name='asyncio-service',
    version=__VERSION__,
    author='Kyle Smith',
    author_email='smithk86@gmail.com',
    description='Manage an Asyncio process in a similar way to a standard Thread',
    url='https://github.com/smithk86/asyncio-service',
    packages=['asyncio_service'],
    license='MIT',
    python_requires='>=3.7',
    install_requires=[
        'pytz'
    ],
    classifiers=(
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent",
        "Framework :: AsyncIO",
    )
)
