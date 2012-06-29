from setuptools import setup
import os

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


CHANGES = """
Changes
-------

0.87
~~~~

Applied patch that adds "provides" to setup.py.

0.86
~~~~

Trying again.

0.85b3
~~~~~~

Yet again adding CHANGES.txt.

0.85b2
~~~~~~

Again adding CHANGES.txt.

0.85
~~~~

JSON Template is usually released at:
http://code.google.com/p/json-template/downloads/list

This is the first PyPI release in 2+ years as I am not a PyPI user myself
(sorry).  Lots of changes since the last PyPI release:

- template styles
- section "pre-formatters"
- various tweaks and additions to the set of builtin formatters
- multiline comment
- whitespace options

doc/Design.txt has some skeletal notes.

(hg change set 434:d97224b19057, tag python-0.85)

0.5b2 (2009-05-27)
~~~~~~~~~~~~~~~~~~

* This release should actually be installable, as 'CHANGES.txt' is actually
  included.

0.5b1 (2009-05-14)
~~~~~~~~~~~~~~~~~~

* Initial public release on PyPI.
"""


long_description = (
    read('README.txt')
    + '\n' +
    CHANGES
    + '\n' +
    'Download\n'
    '--------\n'
    )

setup(
    name="jsontemplate",
    version="0.87",
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
    provides=['jsontemplate'],
    author='Andy Chu',
    author_email='json-template@googlegroups.com',
    url='http://json-template.googlecode.com',
    license='Apache Software License (v2)',
    packages=['jsontemplate'],
    )
