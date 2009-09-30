JSON Template
=============

JSON Template is a simple declarative template language based on
JSON. It is designed to be easy to implement in multiple languages,
including client-side javascript. This release only contains the
official Python implementation of JSON Template.

For more about JSON Template, see:

http://json-template.googlecode.com

Testing
-------

To test JSON template, go to the trunk of the development version of
JSON template and do the following::

  $ python jsontemplate_test.py

Also run the Python tests::

  $ python jsontemplate_test.py --python

Also run the Python specific tests::

  $ cd python/jsontemplate
  $ python formatters_test.py
  $ python jsontemplate_unittest.py

**NOTE**: While there are some tests included in the Python release,
the tests won't run with just the release. You need the whole checkout
of the multi-language JSON Template in order to run the tests, not
just the Python parts.
