#!/usr/bin/python -S
"""
makedocs.py
"""

__author__ = 'Andy Chu'


import os
import shutil
import sys
import subprocess

if __name__ == '__main__':
  sys.path.insert(0, os.path.join(os.path.dirname(sys.argv[0]), '../..'))

from pan.core import json


def main(argv):

  argv = [
      './jsontemplate_test.py', '-l' 'documentation', '-d', 'test-cases']
  subprocess.call(argv)

  shutil.copy('test-cases/testTableExample-001.js.html', 'doc/')

  dictionary = json.dumps({
      'example1':
      open('test-cases/testTableExample-001.html').read(),
      })

  argv = [
      'python/expand.py',
      open('doc/Introducing-JSON-Template.html.jsont').read(),
      dictionary]
  p = subprocess.Popen(argv, stdout=subprocess.PIPE)
  body = p.stdout.read()
  p.wait()

  dictionary = json.dumps({
      # TODO: Could get this from the filename
      'title': 'Introducing JSON Template',
      'body': body,
      })

  argv = [
      'python/expand.py',
      open('doc/html.jsont').read(),
      dictionary]
  p = subprocess.Popen(argv, stdout=subprocess.PIPE)
  body = p.stdout.read()
  p.wait()

  open('doc/Introducing-JSON-Template.html', 'w').write(body)

  # Required epydoc to be installed
  # Don't show private variables, and don't assume the docstrings have epydoc
  # markup.
  argv = [
      'epydoc', 'python/jsontemplate.py', '--html', '-v',
      '--docformat=plaintext', '--no-private', '--include-log', '--no-frames',
      '--name', 'JSON Template',
      '-o', 'epydoc']
  subprocess.call(argv)

  print 'Docs generated in epydoc/ and test-cases/ -- now rsync it'


if __name__ == '__main__':
  sys.exit(main(sys.argv))
