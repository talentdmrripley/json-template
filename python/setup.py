from setuptools import setup
import os

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('README.txt')
    + '\n' +
    read('CHANGES.txt')
    + '\n' +
    'Download\n'
    '--------\n'
    )

setup(
    name="jsontemplate",
    version="0.5b2dev",
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
