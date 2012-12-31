#!/usr/bin/python -S
"""
makedocs.py
"""

__author__ = 'Andy Chu'


import glob
import os
import re
import shutil
import sys
import subprocess
try:
  import json
except ImportError:
  import simplejson as json

if __name__ == '__main__':
  sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'python'))

import jsontemplate



TEST_CASE_INDEX_HTML_TEMPLATE = """
{.repeated section @}
  {@|plain-url}<br>
{.end}
"""

def BlogPosts(directory):
  assert directory.endswith('/')

  posts = []
  for filename in glob.glob(directory + '*.html.jsont'):
    title = filename[len(directory):-len('.html.jsont')].replace('-', ' ')
    outfilename = filename[:-len('.jsont')]

    blog_template = open(filename).read()

    dictionary = {}
    try:
      body = jsontemplate.FromString(blog_template).expand(dictionary)
    except jsontemplate.EvaluationError, e:
      print >>sys.stderr, 'Error expanding %s' % filename
      raise

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

  return jsontemplate.FromFile(
      open('doc/html.jsont')).expand(dictionary)


def MakeIndexHtml(directory):
  files = os.listdir(directory)
  files.sort()
  html = jsontemplate.expand(TEST_CASE_INDEX_HTML_TEMPLATE, files)
  open(directory + 'index.html', 'w').write(html)


# TODO: Make this into a Makefile 
def main(argv):

  # For now, leave off '-l' 'documentation', 
  argv = ['python', 'jsontemplate_test.py', '-d', 'test-cases']
  subprocess.call(argv)

  argv = ['python', 'jsontemplate_test.py', '-b', 'browser-tests']
  subprocess.call(argv)

  MakeIndexHtml('test-cases/')

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
      'epydoc', 'python/jsontemplate/_jsontemplate.py', '--html', '-v',
      '--docformat=plaintext', '--no-private', '--include-log', '--no-frames',
      '--name', 'JSON Template',
      '-o', 'epydoc']
  subprocess.call(argv)

  print 'Docs generated in epydoc/ and test-cases/ -- now rsync it'


if __name__ == '__main__':
  sys.exit(main(sys.argv))
