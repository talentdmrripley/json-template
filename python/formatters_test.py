#!/usr/bin/python -S
"""
formatters_test.py: Tests for formatters.py
"""

__author__ = 'Andy Chu'


import os
import sys
import unittest

if __name__ == '__main__':
  sys.path.insert(0, os.path.join(os.path.dirname(sys.argv[0]), '..'))

from python import formatters  # module under test
from python import jsontemplate

from pan.test import testy


class FormattersTest(testy.Test):

  def setUpOnce(self):
    self.printf_template = '{a|printf %.2f}'
    self.include_template = '{profile|template include-test.jsont}'

  def testBasic(self):
    t = jsontemplate.Template('{a}')
    self.verify.Equal(t.expand(a=1), '1')

  def testPythonPercentFormat(self):
    t = jsontemplate.Template(
        self.printf_template, more_formatters=formatters.PythonPercentFormat)
    self.verify.Equal(t.expand(a=1.0/3), '0.33')

  def testTemplateInclude(self):
    t = jsontemplate.Template(
        self.include_template,
        more_formatters=formatters.TemplateFileInclude('testdata/'))

    d = {'profile': {'name': 'Bob', 'age': 13}}

    self.verify.Equal(t.expand(d), 'Bob is 13\n')

  def testLookupChain(self):
    chained = formatters.LookupChain([
        formatters.PythonPercentFormat,
        formatters.TemplateFileInclude('testdata/'),
        ])

    # Test that the cases from testPythonPercentFormat and testTemplateInclude
    # both work here.

    t = jsontemplate.Template(
        self.printf_template, more_formatters=chained)

    self.verify.Equal(t.expand(a=1.0/3), '0.33')

    t = jsontemplate.Template(
        self.include_template, more_formatters=chained)

    d = {'profile': {'name': 'Bob', 'age': 13}}

    self.verify.Equal(t.expand(d), 'Bob is 13\n')


if __name__ == '__main__':
  testy.RunThisModule()
