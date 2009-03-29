#!/usr/bin/python -S
"""
makedocs.py
"""

__author__ = 'Andy Chu'


import os
import sys
import subprocess

if __name__ == '__main__':
  sys.path.insert(0, os.path.join(os.path.dirname(sys.argv[0]), '../..'))

from pan.core import json


def main(argv):
  """Returns an exit code."""

  dictionary = json.dumps({
    'example1': 
    open('generated_docs/testSearchResultsExample-001.html').read(),
    })

  argv = [
      'python/expand.py', 
      open('doc/Introducing-JSON-Template.html.jsont').read(),
      dictionary]
  subprocess.call(argv)


if __name__ == '__main__':
  sys.exit(main(sys.argv))
