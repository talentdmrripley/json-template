#!/usr/bin/python -S
"""
datadict_test.py: Tests for datadict.py
"""

__author__ = 'Andy Chu'


import os
import sys

if __name__ == '__main__':
  # for jsontemplate and pan, respectively
  sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
  sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from jsontemplate import datadict  # module under test
from pan.test import testy


class DataDictTest(testy.Test):

  def testAddIndex(self):
    d = [ {'foo': 1},
          {'spam': 'eggs'},
        ]
    datadict.AddIndex(d),
    self.verify.Equal(
        d,
        [ {'foo': 1, 'index': 0},
          {'spam': 'eggs', 'index': 1},
        ])

    d = { 'bar': [
          {'foo': 1},
          {'spam': 'eggs'},
          ]
        }

    datadict.AddIndex(d)
    self.verify.Equal(
        d,
        { 'bar': [
          {'foo': 1, 'index': 0},
          {'spam': 'eggs', 'index': 1},
          ]
        })

    # Two levels of lists
    d = { 'bar': [
          {'foo': 1},
          {'spam': [1, 2, 3]},
          {'spam': [{'zero': None}, {'one': None}]},
          ]
        }
    datadict.AddIndex(d)
    self.verify.Equal(
        d,
        { 'bar': [
          {'foo': 1, 'index': 0},
          {'spam': [1, 2, 3], 'index': 1},
          { 'spam': [{'zero': None, 'index': 0}, {'one': None, 'index': 1}],
            'index': 2},
          ]
        })


if __name__ == '__main__':
  testy.RunThisModule()
