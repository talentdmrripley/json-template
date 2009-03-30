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

  argv = [
      './jsontemplate_test.py', '-l' 'documentation', '-d', 'generated_docs']
  subprocess.call(argv)

  dictionary = json.dumps({
    'example1': 
    open('generated_docs/testSearchResultsExample-001.html').read(),
    })

  argv = [
      'python/expand.py', 
      open('doc/Introducing-JSON-Template.html.jsont').read(),
      dictionary]
  p = subprocess.Popen(argv, stdout=subprocess.PIPE)
  contents = p.stdout.read()
  p.wait()

  open('doc/Introducing-JSON-Template.html', 'w').write(contents)


if __name__ == '__main__':
  sys.exit(main(sys.argv))
