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

install_requires = ['numpy>=1.16',
                    'matplotlib>=2.1',
                    'scipy>=1.0',
                    'openturns>=1.14',
                    ]
extras_require = {'doc': ['jupyter', 'jupyter_client']}

with open("README.rst", "r") as fh:
    long_description = fh.read()

setup(
    name='retraites',
    keywords=("graphics"),
    version='1',
    packages=find_packages(exclude=['doc']),
    python_requires='>=3.4',
    install_requires=install_requires,
    extras_require=extras_require,
    description="retraites: Simulateur d'équilibre financier du système de retraites",
    long_description=long_description,
    classifiers=['Development Status :: 5 - Production/Stable',
                 'Environment :: Console',
                 'License :: OSI Approved',
                 'Intended Audience :: Science/Research',
                 'Intended Audience :: Developers',
                 'Natural Language :: English',
                 'Operating System :: Unix',
                 'Programming Language :: Python :: 3',
                 'Programming Language :: Python :: 3.4',
                 'Programming Language :: Python :: 3.5',
                 'Programming Language :: Python :: 3.6',
                 'Programming Language :: Python :: 3.7',
                 'Topic :: Documentation :: Sphinx',
                 'Topic :: Software Development',
                 'Topic :: Scientific/Engineering',
                 ],
    include_package_data=True,
    zip_safe=False,
    license="GPL",
    url="https://github.com/brunoscherrer/retraites",
)
