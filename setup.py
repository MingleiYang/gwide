#!/usr/bin/env python
""" Setup script for the gwide package."""

__author__ = 'Tomasz W. Turowski'

from setuptools import setup, find_packages


setup(
    name='gwide',
    version='0.3',
    # py_modules=['gwide'],
    packages=find_packages(),
    install_requires=[
        'pypeaks',
        'pandas',
        'ruffus',
        'PyYAML',
        'matplotlib',
        'numpy'
    ],
    entry_points='''
        [console_scripts]
        gwideHittable=gwide.gwideHittable:hittable
        gwidePlot=gwide.gwidePlot:plot
    ''',
    author="Tomasz W. Turowski",
    description='Set of tools to downstream analysis of pyCRAC data',
    long_description='',
    author_email="twturowski@gmail.com",
    classifiers=[
            'Development Status :: 2 - Pre-Alpha',
            'Intended Audience :: Science/Research',
            'License :: OSI Approved :: Apache',
            'Topic :: Scientific/Engineering :: Bio-Informatics']
)
