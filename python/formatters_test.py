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

  def testBasic(self):
    t = jsontemplate.Template('{a}')
    self.verify.Equal(t.expand(a=1), '1')

  def testPythonPercentFormat(self):
    t = jsontemplate.Template(
        '{a|printf %.2f}', more_formatters=formatters.PythonPercentFormat)
    self.verify.Equal(t.expand(a=1.0/3), '0.33')

  def testTemplateInclude(self):
    t = jsontemplate.Template(
        '{profile|template include-test.jsont}',
        more_formatters=formatters.TemplateFileInclude('testdata/'))

    d = {'profile': {'name': 'Bob', 'age': 13}}

    self.verify.Equal(t.expand(d), 'Bob is 13\n')


if __name__ == '__main__':
  testy.RunThisModule()
