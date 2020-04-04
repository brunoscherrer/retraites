# coding: utf8
"""
Setup script for retraites
==========================

This script allows to install retraites within the Python environment.

Usage
-----
::

    python setup.py install

"""
from setuptools import (setup, find_packages)

install_requires = ['numpy',
                    'matplotlib',
                    'scipy',
                    'openturns',
                    ]
extras_require = {'doc': ['jupyter', 'jupyter_client']}

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='retraites',
    keywords=("graphics"),
    version='0.0.1',
    packages=find_packages(exclude=['doc']),
    install_requires=install_requires,
    extras_require=extras_require,
    description="retraites: Simulateur d'équilibre financier du système de retraites",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=['Development Status :: 5 - Production/Stable',
                 'Environment :: Console',
                 'License :: OSI Approved',
                 'Intended Audience :: Science/Research',
                 'Intended Audience :: Developers',
                 'Natural Language :: English',
                 'Operating System :: Unix',
                 'Programming Language :: Python :: 3',
                 'Topic :: Documentation :: Sphinx',
                 'Topic :: Software Development',
                 'Topic :: Scientific/Engineering',
                 ],
    include_package_data=True,
    zip_safe=False,
    license="GPL",
    url="https://github.com/brunoscherrer/retraites",
)
