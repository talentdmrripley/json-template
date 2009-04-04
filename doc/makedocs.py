#!/usr/bin/python -S
"""
makedocs.py
"""

__author__ = 'Andy Chu'


import glob
import os
import shutil
import sys
import subprocess

if __name__ == '__main__':
  sys.path.insert(0, os.path.join(os.path.dirname(sys.argv[0]), '..'))

from python import jsontemplate
from pan.core import json


# TDOO: don't hotlink it
_PRETTYPRINT_BASE = 'http://google-code-prettify.googlecode.com/svn/trunk/src/'


def BlogPosts(directory):
  assert directory.endswith('/')

  posts = []
  for filename in glob.glob(directory + '*.html.jsont'):
    title = filename[len(directory):-len('.html.jsont')].replace('-', ' ')
    outfilename = filename[:-len('.jsont')]

    dictionary = {}
    if 'Introducing' in title:
      dictionary['example1'] = open(
          'test-cases/testTableExample-01.html').read()

    body = jsontemplate.FromFile(open(filename)).expand(dictionary)

    pretty_print = 'Minimalism' in title

    posts.append(dict(
        filename=filename, title=title, body=body, outfilename=outfilename,
        pretty_print=pretty_print))
  return posts


def PythonExamples(directory):
  assert directory.endswith('/')

  examples = []
  for path in glob.glob(directory + '*.py'):
    filename = os.path.basename(path)
    title = filename
    outfilename = 'doc/' + filename + '.html'

    RAW_BASE = 'http://json-template.googlecode.com/svn/trunk/python/examples/'
    LIVE_BASE = 'http://www.chubot.org/json-template/cgi-bin/examples/'

    dictionary = {
        'code': open(path).read(),
        'live': LIVE_BASE + filename + '/',  # Important trailing slash!
        'raw': RAW_BASE + filename,
        }

    body = jsontemplate.FromFile(
        open('doc/python-examples.jsont')).expand(dictionary)

    examples.append(dict(
        filename=filename, title=title, body=body, outfilename=outfilename,
        pretty_print=True))
  return examples


def ExpandHtmlShell(title, body, pretty_print=False):
  dictionary = {
      'title': title,
      'body': body,
      }

  # Pretty print
  if pretty_print:
    dictionary['include-js'] = [_PRETTYPRINT_BASE + 'prettify.js']
    dictionary['include-css'] = [_PRETTYPRINT_BASE + 'prettify.css']
    dictionary['onload-js'] = 'prettyPrint();'

  return jsontemplate.FromFile(
      open('doc/html.jsont')).expand(dictionary)


def main(argv):

  # For now, leave off '-l' 'documentation', 
  argv = ['./jsontemplate_test.py', '-d', 'test-cases']
  subprocess.call(argv)

  shutil.copy('test-cases/testTableExample-01.js.html', 'doc/')

  for post in BlogPosts('doc/'):

    body = ExpandHtmlShell(
        post['title'], post['body'], pretty_print=post['pretty_print'])

    open(post['outfilename'], 'w').write(body)


  for example in PythonExamples('python/examples/'):

    body = ExpandHtmlShell(
        example['title'], example['body'], pretty_print=True)

    open(example['outfilename'], 'w').write(body)


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
