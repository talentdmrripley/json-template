from distutils.core import setup

import os

long_description = """
JSON Template is a simple declarative templating language.

This is a release of the official Python implementation of JSON
Template.

For more about JSON Template, see:

http://json-template.googlecode.com
"""

setup(
    name="jsontemplate",
    version="0.5dev",
    description="A declarative templating language based on JSON",
    long_description=long_description,
    classifiers=[
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Markup :: HTML",
        ],
    keywords='json template templating jsontemplate',
    author='Andy Chu',
    author_email='json-template@googlegroups.com',
    url='http://json-template.googlecode.com',
    license='Apache Software License (v2)',
    packages=['jsontemplate'],
    )
