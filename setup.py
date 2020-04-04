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
from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='retraites',
    keywords=("graphics"),
    version='0.1.1',
    packages=find_packages(),
    install_requires=['numpy',
                      'matplotlib',
                      'scipy',
                      'openturns',
                      ],
    description="Simulateur financier du système de retraites",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=['Development Status :: 5 - Production/Stable',
                 'Environment :: Console',
                 'License :: OSI Approved :: GNU General Public License (GPL)',
                 'Intended Audience :: Science/Research',
                 'Intended Audience :: Developers',
                 'Natural Language :: French',
                 'Programming Language :: Python :: 3',
                 'Topic :: Software Development',
                 'Topic :: Scientific/Engineering',
                 ],
    license="GPL",
    url="https://github.com/brunoscherrer/retraites",
    include_package_data=True,
    maintainer = "Michaël Baudin",
    maintainer_email = "michael.baudin@gmail.com",
    author = "Bruno Scherrer and Michaël Baudin", 
    author_email = "michael.baudin@gmail.com"
)
